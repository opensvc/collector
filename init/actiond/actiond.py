#!/usr/bin/python2.6

import os
import sys
import datetime
import MySQLdb
from multiprocessing import Process, Queue
from subprocess import Popen

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
    cursor.execute("SELECT id, command FROM action_queue where status='W'")
    cmds = []
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        cmds.append((row[0], row[1]))
    cursor.close()
    return cmds

def dequeue_worker(i, q):
    conn = get_conn()
    if conn is None:
        return
    cursor = conn.cursor()
    while (not q.empty()):
        (id, cmd) = q.get()
        cursor.execute("update action_queue set status='R' where id=%d"%id)
        conn.commit()
        print '[%d] %d: %s'%(i, id, cmd)
        cmd = cmd.split()
        process = Popen(cmd, stdin=None)
        process.communicate()
        now = str(datetime.datetime.now())
        cursor.execute("update action_queue set status='T', date_dequeued='%s' where id=%d"%(now, id))
    cursor.close()

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

def dequeue():
    ps = []
    q = Queue()
    for id, cmd in get_queued():
        q.put((id, cmd))
    for i in range(0, N_THREAD):
        p = Process(target=dequeue_worker, args=(i, q))
        p.start()
        ps.append(p)
    for p in ps:
        p.join()

try:
    lockfd = actiond_lock(lockfile)
    fork(dequeue)
    actiond_unlock(lockfd)
except lock.lockError:
    sys.exit(0)
except:
    sys.exit(1)
