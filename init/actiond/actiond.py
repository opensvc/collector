#!/usr/bin/python

import os
import sys
import time
import datetime
import MySQLdb
from multiprocessing import Process, JoinableQueue, Queue
from subprocess import *
from socket import *
import json

basedir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(basedir)
sys.path.append(basedir+"/../../..")
sys.path.append(basedir+"/../modules")
sys.path.append(basedir+"/../models")

import lock
import config
from comet import event_msg, _websocket_send

def msg(conn):
    sql = """select
              (select count(id) from action_queue where status in ('Q', 'N', 'W', 'R')) as queued,
              (select count(id) from action_queue where ret!=0) as ko,
              (select count(id) from action_queue where ret=0 and status='T') as ok
          """
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    s = {
      'event': 'action_q_change',
      'data': {
        'queued': row[0],
        'ko': row[1],
        'ok': row[2],
      },
    }
    cursor.close()
    return s

try:
    dbopensvc = config.dbopensvc_host
except:
    dbopensvc = "127.0.0.1"

try:
    dbopensvc_password = config.dbopensvc_password
except:
    dbopensvc_password = "opensvc"

try:
    actiond_workers = config.actiond_workers
except:
    actiond_workers = 10

try:
    notification_timeout = config.notification_timeout
except:
    notification_timeout = 5

lockfile = __file__+'.lock'

def actiond_lock(lockfile):
    try:
        lockfd = lock.lock(timeout=0, delay=0, lockfile=lockfile)
    except lock.lockTimeout:
        print("timed out waiting for lock")
        raise lock.lockError
    except lock.lockNoLockFile:
        print("lock_nowait: set the 'lockfile' param")
        raise lock.lockError
    except lock.lockCreateError:
        print("can not create lock file %s"%lockfile)
        raise lock.lockError
    except lock.lockAcquire as e:
        print("another actiond is currently running (pid=%s)"%e.pid)
        raise lock.lockError
    except:
        print("unexpected locking error")
        import traceback
        traceback.print_exc()
        raise lock.lockError
    return lockfd

def actiond_unlock(lockfd):
    lock.unlock(lockfd)

def fork(fn, kwargs={}):
    try:
        if os.fork() > 0:
            """ return to parent execution
            """
            return
    except:
        """ no dblogging will be done. too bad.
        """
        return

    """ separate the son from the father
    """
    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except:
        os._exit(1)

    fn(**kwargs)
    os._exit(0)

def notify_node(nodename, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((nodename, port))
    sock.send("dequeue_actions")
    sock.close()

def get_queued():
    conn = get_conn()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT a.id, a.command, a.action_type, a.connect_to, n.fqdn, n.listener_port, a.form_id FROM action_queue a join nodes n on a.node_id=n.node_id where a.status='W'")
    cmds = []
    ids = []
    nids = []
    invalid_ids = []
    unreachable_ids = []

    while (1):
        row = cursor.fetchone()
        if row is None:
            break

        dq_time = time.time()
        nodename = row[3]

        if 'opensvc@localhost' in row[1] or \
           'opensvc@localhost.localdomain' in row[1]:
            invalid_ids.append(str(row[0]))
            continue

        if row[2] == "pull":
            port = row[5]
            notified = False
            while time.time() - dq_time < notification_timeout:
                try:
                    notify_node(nodename, port)
                    nids.append(str(row[0]))
                    notified = True
                    break
                except Exception as exc:
                    print("notify", nodename, port, "error:", exc)
                    time.sleep(1)
            if not notified:
                unreachable_ids.append(str(row[0]))
        else:
            cmds.append((row[0], row[1], row[6]))
            ids.append(str(row[0]))

    if len(unreachable_ids) > 0:
        now = str(datetime.datetime.now())
        sql = """update action_queue set
                   status='T',
                   date_dequeued='%s',
                   ret=1,
                   stdout="",
                   stderr="unreachable"
                 where id in (%s)
              """%(now, ','.join(unreachable_ids))
        cursor.execute(sql)
        conn.commit()

    if len(invalid_ids) > 0:
        now = str(datetime.datetime.now())
        sql = """update action_queue set
                   status='T',
                   date_dequeued='%s',
                   ret=1,
                   stdout="",
                   stderr="invalid"
                 where id in (%s)
              """%(now, ','.join(invalid_ids))
        cursor.execute(sql)
        conn.commit()

    if len(nids) > 0:
        cursor.execute("update action_queue set status='N' where id in (%s)"%(','.join(nids)))
        conn.commit()

    if len(ids) > 0:
        cursor.execute("update action_queue set status='Q' where id in (%s)"%(','.join(ids)))
        conn.commit()

    if len(ids)+len(nids)+len(invalid_ids) + len(unreachable_ids) > 0:
        _websocket_send(event_msg(msg(conn)))

    cursor.close()
    conn.close()
    return cmds

def dequeue_worker(i, recv, send):
    idle = False
    while True:
        try:
            (id, cmd, form_id) = recv.get()
        except KeyboardInterrupt:
            return
        except Queue.Empty:
            if not idle:
                print '[%d] idle'%(i)
                idle = True
            time.sleep(1)
            continue
        idle = False
        conn = get_conn()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("update action_queue set status='R' where id=%d"%id)
        conn.commit()
        _websocket_send(event_msg(msg(conn)))
        print '[%d] %d: %s'%(i, id, cmd)
        cmd = cmd.split()
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=None)
        out, err = process.communicate()
        now = str(datetime.datetime.now())
        cursor = conn.cursor()
        sql = """update action_queue set
                   status='T',
                   date_dequeued='%s',
                   ret=%d,
                   stdout=%s,
                   stderr=%s
                 where id=%d
              """%(now, process.returncode, repr(out), repr(err), id)
        cursor.execute(sql)
        conn.commit()
        _websocket_send(event_msg(msg(conn)))

        if form_id is not None:
            send.put(dict(
                       id=id,
                       form_id=form_id,
                       cmd=cmd,
                       ret=process.returncode,
                       out=out,
                       err=err
            ))
        cursor.close()
        conn.close()
        recv.task_done()
    sys.exit(0)

def get_form_scripts(conn, cursor, form_id):
    script_data = None
    sql = """select form_scripts from forms_store where id=%s"""%form_id
    cursor.execute(sql)
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        scripts_data = row[0]
    return scripts_data

def update_form_id(data):
    id = data['id']
    form_id = data['form_id']
    out = data['out']
    err = data['err']
    ret = data['ret']
    cmd = data['cmd']

    conn = get_conn()
    if conn is None:
        return
    cursor = conn.cursor()

    for i in range(5):
        script_data = get_form_scripts(conn, cursor, form_id)
        if script_data is None:
            print "form %s not found. wait."%str(form_id)
            time.sleep(1)
        break

    if script_data is None:
        print "form %s not found. abort."%str(form_id)
        return

    script_data = script_data.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    try:
        script_data = json.loads(script_data)
    except Exception as e:
        print e
        script_data = {'returncode': 0}

    script_data[str(id)] = {
      'path': " ".join(cmd),
      'stdout': out,
      'stderr': err,
      'returncode': ret,
    }
    if ret != 0:
        script_data['returncode'] = 1

    print "updating form_id", form_id, "with script data", script_data
    sql = """update forms_store set form_scripts='%s' where id=%s""" % (json.dumps(script_data), str(form_id))
    cursor.execute(sql)
    conn.commit()

    sql = """select id from action_queue where form_id=%s"""%str(form_id)
    cursor.execute(sql)
    conn.commit()
    todo = []
    done = []
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        todo.append(row[0])
    for key in script_data.keys():
        try:
            done.append(int(key))
        except:
            pass
    print "todo", todo, "done", done
    if set(todo) == set(done):
        close_workflow(form_id, conn, cursor)

    cursor.close()
    conn.close()

def close_workflow(form_id, conn, cursor):
    print "close workflow %s is the tail form of"%str(form_id)
    sql = """update workflows set status="closed" where last_form_id=%s"""%str(form_id)
    cursor.execute(sql)
    sql = """update forms_store set form_next_id=0 where id=%s"""%str(form_id)
    cursor.execute(sql)
    conn.commit()

def get_conn():
    try:
        conn = MySQLdb.connect(host=dbopensvc,
                               user="opensvc",
                               passwd=dbopensvc_password,
                               db="opensvc")
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        return None
    return conn

ps = []

def start_workers(send, recv):
    for i in range(0, actiond_workers):
        p = Process(target=dequeue_worker, args=(i, send, recv), name='[worker%d]'%i)
        p.start()
        ps.append(p)

def stop_workers():
    """ TODO: need to wait for worker idling before stop """
    for p in ps:
        p.terminate()
    for p in ps:
        p.join()

def dequeue():
    try:
        _dequeue()
    except KeyboardInterrupt:
        pass

def _dequeue():
    idle = False
    send = JoinableQueue()
    recv = JoinableQueue()
    start_workers(send, recv)
    while True:
        bunch = get_queued()
        while not recv.empty():
            data = recv.get()
            print "scheduler recv data:", data
            try:
                update_form_id(data)
            except Exception as e:
                print e
            recv.task_done()
        if len(bunch) == 0:
            if not idle:
                print "[Queue manager] idle"
                idle = True
            time.sleep(1)
            continue
        idle = False
        for id, cmd, form_id in bunch:
            send.put((id, cmd, form_id), block=True)
    #stop_workers()

#dequeue()
#sys.exit()

try:
    lockfd = actiond_lock(lockfile)
    fork(dequeue)
    actiond_unlock(lockfd)
except lock.lockError:
    sys.exit(0)
except:
    sys.exit(1)
