#!/usr/bin/python

from __future__ import print_function

import os
import sys
import time
import datetime
import optparse
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


def purge():
    conn = get_conn()
    if conn is None:
        return
    sql = """delete from action_queue where date_dequeued<date_sub(now(), interval 1 day) and status in ('T', 'C')
          """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()


def msg(conn):
    sql = """select
              (select count(id) from action_queue where status in ('Q', 'N', 'W', 'R', 'S')) as queued,
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


def conf(envkey, cnfkey, default):
    v = os.environ.get(envkey)
    if v is not None:
        return v, "env"
    try:
        return getattr(config, cnfkey), "configfile"
    except AttributeError:
        return default, "default"


print("init parameters:")

dbopensvc_host, src = conf("DBOPENSVC_HOST", "dbopensvc_host", "127.0.0.1")
print(" dbopensvc_host =", dbopensvc_host, "<", src)

dbopensvc_password, src = conf("DBOPENSVC_PASSWORD", "dbopensvc_password", "opensvc")
print(" dbopensvc_password =", "xxxx", "<", src)

actiond_workers, src = conf("ACTIOND_WORKERS", "actiond_workers", 10)
print(" actiond_workers =", actiond_workers, "<", src)

notification_timeout, src = conf("NOTIFICATION_TIMEOUT", "notification_timeout", 5)
notification_timeout = int(notification_timeout)
print(" notification_timeout =", notification_timeout, "<", src)

purge_timeout, src = conf("PURGE_TIMEOUT", "purge_timeout", 24*3600)
purge_timeout = int(purge_timeout)
print(" purge_timeout =", purge_timeout, "<", src)

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
        print("can not create lock file %s" % lockfile)
        raise lock.lockError
    except lock.lockAcquire as e:
        print("another actiond is currently running (pid=%s)" % e.pid)
        raise lock.lockError
    except Exception:
        print("unexpected locking error")
        import traceback
        traceback.print_exc()
        raise lock.lockError
    return lockfd


def actiond_unlock(lockfd):
    lock.unlock(lockfd)


def fork(fn, kwargs=None):
    kwargs = kwargs or {}

    try:
        if os.fork() > 0:
            """ return to parent execution
            """
            return
    except Exception:
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
    except Exception:
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
    """
    for action fetched from action_queue db where status is "W"
        if command is invalid
            => status changed from "W" -> "T" stderr: "invalid"
        else if action type is pull
            notify node that it has action to dequeue
                ok => status changed from "W" -> "N"
                else  status changed from "W" -> "T", stderr: "unreachable"
        else
            status changed from "W" -> "Q"
        update db action_queue with current changes on every max_inflight actions

    update db action_queue with not yet updated changes

    return queued actions (status: "Q") [(id, command, form_id), ...]
    """
    conn = get_conn()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT a.id, a.command, a.action_type, a.connect_to, n.fqdn, n.listener_port, a.form_id FROM action_queue a join nodes n on a.node_id=n.node_id where a.status='W'")
    max_inflight = 10
    cmds = []
    data = {
        "ids": [],
        "nids": [],
        "invalid_ids": [],
        "unreachable_ids": [],
    }
    count = 0

    def update_action_queue_db():
        if len(data["unreachable_ids"]) > 0:
            now = str(datetime.datetime.now())
            sql = """update action_queue set
                       status='T',
                       date_dequeued='%s',
                       ret=1,
                       stdout="",
                       stderr="unreachable"
                     where id in (%s)
                  """ % (now, ','.join(data["unreachable_ids"]))
            cursor.execute(sql)
            conn.commit()

        if len(data["invalid_ids"]) > 0:
            now = str(datetime.datetime.now())
            sql = """update action_queue set
                       status='T',
                       date_dequeued='%s',
                       ret=1,
                       stdout="",
                       stderr="invalid"
                     where id in (%s)
                  """ % (now, ','.join(data["invalid_ids"]))
            cursor.execute(sql)
            conn.commit()

        if len(data["nids"]) > 0:
            cursor.execute("update action_queue set status='N' where id in (%s) and status='W'" % (','.join(data["nids"])))
            conn.commit()

        if len(data["ids"]) > 0:
            cursor.execute("update action_queue set status='Q' where id in (%s) and status='W'" % (','.join(data["ids"])))
            conn.commit()

        if len(data["ids"])+len(data["nids"])+len(data["invalid_ids"]) + len(data["unreachable_ids"]) > 0:
            _websocket_send(event_msg(msg(conn)))

        data["ids"] = []
        data["nids"] = []
        data["invalid_ids"] = []
        data["unreachable_ids"] = []

    while True:
        row = cursor.fetchone()
        if row is None:
            break

        count += 1
        if count > max_inflight:
            update_action_queue_db()
            count = 0

        dq_time = time.time()
        action_id = str(row[0])
        command = row[1]
        action_type = row[2]
        nodename = row[3]
        form_id = row[6]

        if 'opensvc@localhost' in command or \
           'opensvc@localhost.localdomain' in command:
            data["invalid_ids"].append(action_id)
            continue

        if action_type == "pull":
            port = row[5]
            notified = False
            while time.time() - dq_time < notification_timeout:
                try:
                    notify_node(nodename, port)
                    data["nids"].append(action_id)
                    notified = True
                    break
                except Exception as exc:
                    print("notify", nodename, port, "error:", exc)
                    time.sleep(1)
            if not notified:
                data["unreachable_ids"].append(action_id)
        else:
            cmds.append((action_id, command, form_id))
            data["ids"].append(action_id)

    update_action_queue_db()
    cursor.close()
    conn.close()
    return cmds


def dequeue_worker(worker_id, recv, send):
    """
    dequeue_worker will loop on recv queue until no db connexion or KeyboardInterrupt
    become idle for 1s when recv queue is empty

    each loop will:
        update db action_queue with status 'R'
        process job
        update db action_queue with status 'T' and updated ret, stdout, stderr
        if job has form_id 'send' queue is updated with job results

    """
    idle = False
    while True:
        try:
            (id, cmd, form_id) = recv.get()
        except KeyboardInterrupt:
            return
        except Queue.Empty:
            if not idle:
                print('[%d] idle' % worker_id)
                idle = True
            time.sleep(1)
            continue
        idle = False
        conn = get_conn()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("update action_queue set status='R' where id=%d" % id)
        conn.commit()
        _websocket_send(event_msg(msg(conn)))
        print('[%d] %d: %s' % (worker_id, id, cmd))
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
              """ % (now, process.returncode, repr(out), repr(err), id)
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


def get_form_scripts(cursor, form_id):
    scripts_data = None
    sql = """select form_scripts from forms_store where id=%s""" % form_id
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
        script_data = get_form_scripts(cursor, form_id)
        if script_data is None:
            print("form %s not found. wait." % str(form_id))
            time.sleep(1)
        break

    if script_data is None:
        print("form %s not found. abort." % str(form_id))
        return

    script_data = script_data.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    try:
        script_data = json.loads(script_data)
    except Exception as e:
        print(e)
        script_data = {'returncode': 0}

    script_data[str(id)] = {
      'path': " ".join(cmd),
      'stdout': out,
      'stderr': err,
      'returncode': ret,
    }
    if ret != 0:
        script_data['returncode'] = 1

    print("updating form_id", form_id, "with script data", script_data)
    sql = """update forms_store set form_scripts='%s' where id=%s""" % (json.dumps(script_data), str(form_id))
    cursor.execute(sql)
    conn.commit()

    sql = """select id from action_queue where form_id=%s""" % str(form_id)
    cursor.execute(sql)
    conn.commit()
    todo = []
    done = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        todo.append(row[0])
    for key in script_data.keys():
        try:
            done.append(int(key))
        except Exception:
            pass
    print("todo", todo, "done", done)
    if set(todo) == set(done):
        close_workflow(form_id, conn, cursor)

    cursor.close()
    conn.close()


def close_workflow(form_id, conn, cursor):
    print("close workflow %s is the tail form of" % str(form_id))
    sql = """update workflows set status="closed" where last_form_id=%s""" % str(form_id)
    cursor.execute(sql)
    sql = """update forms_store set form_next_id=0 where id=%s""" % str(form_id)
    cursor.execute(sql)
    conn.commit()


def get_conn():
    try:
        conn = MySQLdb.connect(host=dbopensvc_host,
                               user="opensvc",
                               passwd=dbopensvc_password,
                               db="opensvc")
    except MySQLdb.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return None
    return conn


ps = []


def start_workers(send, recv):
    for i in range(0, actiond_workers):
        p = Process(target=dequeue_worker, args=(i, send, recv), name='[worker%d]' % i)
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
    """
    manager for action queue process
    It is responsible of creation of 'send' and 'recv' queues
    start dequeue workers
    loop
        jobs_for_dequeue_workers = get_queued() <- [(id, command, form_id), ....]

        receive results of dequeue_workers jobs (from 'recv' queue) to update theirs associated form_id

        if no jobs_for_dequeue_workers
            if not purged since purge_timeout delay
                take time to purge()
            delay next loop for 1s
        else
            send jobs to dequeue_workers (using 'send' queue)
    """
    idle = False
    send = JoinableQueue()
    recv = JoinableQueue()
    start_workers(send, recv)
    last_purge = 0
    while True:
        jobs_for_dequeue_workers = get_queued()
        while not recv.empty():
            data = recv.get()
            print("scheduler recv data:", data)
            try:
                update_form_id(data)
            except Exception as e:
                print(e)
            recv.task_done()
        if len(jobs_for_dequeue_workers) == 0:
            if not idle:
                print("[Queue manager] idle")
                idle = True
            if time.time() - last_purge > purge_timeout:
                print("purge")
                purge()
                last_purge = time.time()
            time.sleep(1)
            continue
        idle = False
        for id, cmd, form_id in jobs_for_dequeue_workers:
            send.put((id, cmd, form_id), block=True)


def main(**options):
    try:
        lockfd = actiond_lock(lockfile)
        if options.get("foreground"):
            dequeue()
        else:
            fork(dequeue)
        actiond_unlock(lockfd)
    except lock.lockError:
        return 0
    except Exception as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", default=False, action="store_true",
                      dest="foreground", help="Run in forground")
    options, _ = parser.parse_args()
    options = vars(options)
    sys.exit(main(**options))
