#!/usr/bin/python2.6

import os
import sys
import time
import datetime
import MySQLdb
from multiprocessing import Process, JoinableQueue, Queue
from subprocess import *

basedir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(basedir)

import lock

lockfile = __file__+'.lock'
N_THREAD = 10

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

def get_queued():
    conn = get_conn()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT id, command FROM action_queue where status='W' and action_type='push'")
    cmds = []
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        cmds.append((row[0], row[1]))
    ids = map(lambda x: str(x[0]), cmds)
    if len(ids) > 0:
        cursor.execute("update action_queue set status='Q' where id in (%s)"%(','.join(ids)))
        conn.commit()
    cursor.close()
    conn.close()
    return cmds

def dequeue_worker(i, q):
    idle = False
    while True:
        try:
            (id, cmd) = q.get()
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
        cursor.close()
        conn.close()
        q.task_done()
    sys.exit(0)

def get_conn():
    try:
        conn = MySQLdb.connect(host="dbopensvc",
                               user="opensvc",
                               passwd="opensvc",
                               db="opensvc")
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        return None
    return conn

ps = []

def start_workers(q):
    for i in range(0, N_THREAD):
        p = Process(target=dequeue_worker, args=(i, q), name='[worker%d]'%i)
        p.start()
        ps.append(p)

def stop_workers():
    """ TODO: need to wait for worker idling before stop """
    for p in ps:
        p.terminate()
    for p in ps:
        p.join()

def dequeue():
    idle = False
    q = JoinableQueue()
    start_workers(q)
    while True:
        bunch = get_queued()
        if len(bunch) == 0:
            if not idle:
                print "[Queue manager] idle"
                idle = True
            time.sleep(1)
            continue
        idle = False
        for id, cmd in bunch:
            q.put((id, cmd), block=True)
    #stop_workers()

try:
    lockfd = actiond_lock(lockfile)
    fork(dequeue)
    actiond_unlock(lockfd)
except lock.lockError:
    sys.exit(0)
except:
    sys.exit(1)
