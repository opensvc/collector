#!/usr/bin/python2.6

import os
import sys
import time
import datetime
import MySQLdb
import json
import smtplib
import xmpp
from multiprocessing import Process, JoinableQueue, Queue
from subprocess import Popen

basedir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(basedir)

import lock

lockfile = __file__+'.lock'
N_THREAD = 10
sender = 'opensvc@'+os.uname()[1]

import xmpp
import sys
import config

def alertd_lock(lockfile):
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
        print("another alertd is currently running (pid=%s)"%e.pid)
        raise lock.lockError
    except:
        print("unexpected locking error")
        import traceback
        traceback.print_exc()
        raise lock.lockError
    return lockfd

def alertd_unlock(lockfd):
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

class SendError(Exception):
    pass

class im_job(object):
    def __init__(self, row):
        self.addr = row[3]
        self.lines = []
        self += row

    def __iadd__(self, row):
        fmt = row[1]
        try:
            dic = json.loads(row[2])
            l = (row[0], row[5], row[6], fmt%dic)
        except:
            print "skip on json error:", fmt, row[2]
            return self
        self.lines.append(l)
        return self

    def __str__(self):
        s = ""
        for l in self.lines:
            s += "%s | %20s | %20s | %s\n"%(str(l[0]), l[1], l[2], l[3])
        return s

    def __call__(self):
        message = str(self)
        try:
            c = xmpp.Client("gmail.com", debug=[])
            c.connect(("talk.google.com", 5223))
            c.auth(config.gtalk_username, config.gtalk_password)
            c.send(xmpp.Message(self.addr.strip("'"), message))
        except:
            raise SendError()

class email_job(object):
    def __init__(self, row):
        self.addr = row[3]
        self.lines = []
        self += row

    def __iadd__(self, row):
        fmt = row[1]
        try:
            dic = json.loads(row[2])
            l = (row[0], row[5], row[6], fmt%dic)
        except:
            print "skip on json error:", fmt, row[2]
            return self
        self.lines.append(l)
        return self

    def __str__(self):
        s = ""
        for l in self.lines:
            s += "%s | %20s | %20s | %s\n"%(str(l[0]), l[1], l[2], l[3])
        return s

    def __call__(self):
        receivers = [self.addr]
        message = """From: OpenSVC Collector <%(sender)s>
To: %(rcpt)s
Subject: OpenSVC events

%(body)s
"""%dict(sender=sender, rcpt=self.addr, body=str(self))

        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
        except smtplib.SMTPException:
            raise SendError()

def get_im_queued_node(q):
    max_entries_per_msg = 10
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.im_username,
               l.id,
               l.log_nodename,
               ""
             from log l
               join nodes n on l.log_nodename=n.nodename
               join auth_group g on n.team_responsible=g.role
               join auth_membership am on am.group_id=g.id
               join auth_user u on am.user_id=u.id
             where
               u.im_notifications = 'T' and
               l.log_svcname is NULL and
               l.log_nodename is not NULL and
               l.log_gtalk_sent=0
             order by u.im_username, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = im_job(row)
        if row[3] == addr and len(j.lines) <= max_entries_per_msg:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def get_im_queued_manager(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               t.im_username,
               l.id,
               "",
               ""
             from log l,
               (select im_username from auth_user u
                 join auth_membership am on u.id=am.user_id
                 join auth_group g on am.group_id=g.id
                where
                  g.role="Manager" and
                  u.im_notifications = 'T') t
             where
               l.log_svcname is NULL and
               l.log_nodename is NULL and
               l.log_im_sent=0
             order by t.im_username, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = im_job(row)
        if row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def get_im_queued_svc(q):
    max_entries_per_msg = 10
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.im_username,
               l.id,
               l.log_nodename,
               l.log_svcname
             from log l
               join services s on l.log_svcname=s.svc_name
               join apps a on s.svc_app=a.app
               join apps_responsibles ar on a.id=ar.app_id
               join auth_membership am on ar.group_id=am.group_id
               join auth_user u on am.user_id=u.id
             where
               u.im_notifications = 'T' and
               l.log_svcname is not NULL and
               l.log_gtalk_sent=0
             order by u.im_username, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = im_job(row)
        if row[3] == addr and len(j.lines) <= max_entries_per_msg:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def im_done(ids):
    if len(ids) == 0:
        return
    conn = get_conn()
    if conn is None:
        return []
    sql = """update log set log_gtalk_sent=1 where id in (%s)"""%(','.join(map(str, ids)))
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def email_done(ids):
    if len(ids) == 0:
        return
    conn = get_conn()
    if conn is None:
        return []
    sql = """update log set log_email_sent=1 where id in (%s)"""%(','.join(map(str, ids)))
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def get_email_queued_node(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.email,
               l.id,
               l.log_nodename,
               ""
             from log l
               join nodes n on l.log_nodename=n.nodename
               join auth_group g on n.team_responsible=g.role
               join auth_membership am on am.group_id=g.id
               join auth_user u on am.user_id=u.id
             where
               u.email_notifications = 'T' and
               l.log_svcname is NULL and
               l.log_nodename is not NULL and
               l.log_email_sent=0
             order by u.email, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = email_job(row)
        if row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def get_email_queued_manager(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               t.email,
               l.id,
               "",
               ""
             from log l,
               (select email from auth_user u
                 join auth_membership am on u.id=am.user_id
                 join auth_group g on am.group_id=g.id
                where
                  g.role="Manager" and
                  u.email_notifications = 'T') t
             where
               l.log_svcname is NULL and
               l.log_nodename is NULL and
               l.log_email_sent=0
             order by t.email, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = email_job(row)
        if row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def get_email_queued_svc(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.email,
               l.id,
               l.log_nodename,
               l.log_svcname
             from log l
               join services s on l.log_svcname=s.svc_name
               join apps a on s.svc_app=a.app
               join apps_responsibles ar on a.id=ar.app_id
               join auth_membership am on ar.group_id=am.group_id
               join auth_user u on am.user_id=u.id
             where
               u.email_notifications = 'T' and
               l.log_svcname is not NULL and
               l.log_email_sent=0
             order by u.email, l.id
             limit 1000
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    addr = None
    n_job = 0
    n_entry = 0
    ids = set([])
    while (1):
        row = cursor.fetchone()
        if row is None:
            if addr is not None:
                q.put(j, block=True)
                n_job += 1
            break
        n_entry +=1
        if addr is None:
            addr = row[3]
            j = email_job(row)
        if row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            j += row
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return {'n_job': n_job, 'n_entry': n_entry, 'ids': ids}

def dequeue_worker_int(i, q):
    try:
        dequeue_worker(i, q)
    except KeyboardInterrupt:
        print "[%d] keyboard interrupt"%(i)
        pass

def dequeue_worker(i, q):
    print "[%d] start"%(i)
    while True:
        job = q.get()
        if job is None:
            print "[%d] stop on poison pill"%(i)
            break
        print '[%d] %s'%(i, str(job))
        try:
            job()
        except SendError:
            print '[%d] error sending message to %s'%(i, job.addr)
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
for i in range(0, N_THREAD):
    ps.append(None)

def start_workers(q):
    for i in range(0, N_THREAD):
        p = Process(target=dequeue_worker_int, args=(i, q), name='[worker%d]'%i)
        p.start()
        ps[i] = p

def stop_workers(q):
    """ TODO: need to wait for worker idling before stop """
    for p in ps:
        q.put(None)
    for p in ps:
        p.join()

def dequeue(q):
    while True:
        n_entry = 0
        n_job = 0
        ids = []

        d = get_email_queued_svc(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        d = get_email_queued_node(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        d = get_email_queued_manager(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        if n_job > 0:
            start_workers(q)
            print "[Queue manager] queued %d log entries in %d emails"%(n_entry, n_job)
            stop_workers(q)
            email_done(ids)

        if not config.gtalk:
            time.sleep(1)
            continue

        n_entry = 0
        n_job = 0
        ids = []

        d = get_im_queued_svc(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        d = get_im_queued_node(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        d = get_im_queued_manager(q)
        n_entry += d['n_entry']
        n_job += d['n_job']
        ids += d['ids']

        if n_job > 0:
            start_workers(q)
            print "[Queue manager] queued %d log entries in %d instant messages"%(d['n_entry'], d['n_job'])
            stop_workers(q)
            im_done(ids)

        time.sleep(1)
        continue
    #stop_workers()

def dequeue_int():
    q = JoinableQueue()
    try:
        dequeue(q)
    except KeyboardInterrupt:
        print "[Queue manager] keyboard interrupt"
        stop_workers(q)
        pass

dequeue_int()
"""
try:
    lockfd = alertd_lock(lockfile)
    fork(dequeue)
    alertd_unlock(lockfd)
except lock.lockError:
    sys.exit(0)
except:
    sys.exit(1)
"""
