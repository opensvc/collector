#!/opt/opensvc/bin/python

import os
import sys
import time
import datetime
import MySQLdb
import json
import smtplib
from multiprocessing import Process, JoinableQueue, Queue
from subprocess import Popen
import logging
import logging.handlers

basedir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(basedir)

import lock

lockfile = __file__+'.lock'
N_THREAD = 10
max_entries_per_msg = 10

import xmpp
import sys
import config

def setup_log():
    logfile = os.path.join(basedir, 'alertd.log')
    log = logging.getLogger()
    fileformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    filehandler = logging.handlers.RotatingFileHandler(logfile,
                                                       maxBytes=5242880,
                                                       backupCount=5)
    filehandler.setFormatter(fileformatter)
    log.addHandler(filehandler)
    log.setLevel(logging.INFO)

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

def prettydate(dt, T=lambda x: x):
    if dt.days < 0:
        suffix = ' later'
        dt = -dt
    else:
        suffix = ' before'
    if dt.days >= 2 * 365:
        return T('%d years' + suffix) % int(dt.days / 365)
    elif dt.days >= 365:
        return T('1 year' + suffix)
    elif dt.days >= 60:
        return T('%d months' + suffix) % int(dt.days / 30)
    elif dt.days > 21:
        return T('1 month' + suffix)
    elif dt.days >= 14:
        return T('%d weeks' + suffix) % int(dt.days / 7)
    elif dt.days >= 7:
        return T('1 week' + suffix)
    elif dt.days > 1:
        return T('%d days' + suffix) % dt.days
    elif dt.days == 1:
        return T('1 day' + suffix)
    elif dt.seconds >= 2 * 60 * 60:
        return T('%d hours' + suffix) % int(dt.seconds / 3600)
    elif dt.seconds >= 60 * 60:
        return T('1 hour' + suffix)
    elif dt.seconds >= 2 * 60:
        return T('%d minutes' + suffix) % int(dt.seconds / 60)
    elif dt.seconds >= 60:
        return T('1 minute' + suffix)
    elif dt.seconds > 1:
        return T('%d seconds' + suffix) % dt.seconds
    elif dt.seconds == 1:
        return T('1 second' + suffix)
    else:
        return T('meanwhile')

class SendError(Exception):
    pass

class counters(object):
    def __init__(self, n_job=0, n_entry=0, ids=set([])):
        self.n_job = n_job
        self.n_entry = n_entry
        self.ids = ids

    def __str__(self):
        return "jobs: %d, entries %d, ids: %s"%(
          self.n_job, self.n_entry, ','.join(map(lambda x: str(x), self.ids)))

    def __iadd__(self, o):
        self.n_job += o.n_job
        self.n_entry += o.n_entry
        self.ids |= o.ids
        return self

    def reset(self):
        self.__init__()

class im_job(object):
    def __init__(self, row):
        self.addr = row[3]
        self.lines = []
        self += row
        self.name = "Instant messaging job"

    def __iadd__(self, row):
        fmt = row[1]
        try:
            dic = json.loads(row[2])
            l = (row[0], row[7], row[5], row[6], fmt%dic)
        except:
            jlog.warning("skip on json error: %s, %s" % (fmt, row[2]))
            return self
        self.lines.append(l)
        return self

    def __str__(self):
        s = ""
        for l in self.lines:
            s += "%s | %8s | %20s | %20s | %s\n"%(str(l[0]), l[1], l[2], l[3], l[4])
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

try:
    with open(basedir+"/../static/mail.css", "r") as f:
        style = f.read()
except:
    style = ""

class email_job(object):
    def __init__(self, row):
        self.addr = row[3]
        self.lines = []
        self += row
        self.name = "Email job"

    def __iadd__(self, row):
        fmt = row[1]
        try:
            dic = json.loads(row[2])
            l = (row[0], row[7], row[5], row[6], fmt%dic)
        except:
            jlog.warning("skip on json error: %s, %s" % (fmt, row[2]))
            return self
        self.lines.append(l)
        return self

    def __str__(self):
        return self.html()

    def text(self):
        s = ""
        for l in self.lines:
            s += "%s | %8s | %20s | %20s | %s\n"%(str(l[0]), l[1], l[2], l[3], l[4])
        return s

    def html(self):
        header = """<html><head><style _type="text/css">"""+style+"""</style></head><table>"""
        header += """<tr><th>Date</th><th>Severity</th><th>Node</th><th>Service</th><th>Message</th></tr>"""
        footer = """</table></html>"""
        body = ""
        for i, l in enumerate(self.lines):
            if i == 0:
                refdate = l[0]
                _date = str(refdate)
            else:
                _date = prettydate(refdate-l[0])
            body += """<tr><td>%s</td><td class="%s">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (_date, l[1], l[1], l[2], l[3], l[4])
        return header+body+footer

    def __call__(self):
        receivers = [self.addr]
        message = """From: OpenSVC Collector <%(sender)s>
To: %(rcpt)s
Subject: %(n)d OpenSVC events
Content-Type: text/html; charset=UTF-8

%(body)s
"""%dict(n=len(self.lines), sender=config.email_from, rcpt=self.addr, body=str(self))

        try:
            smtpObj = smtplib.SMTP(config.email_server)
            smtpObj.sendmail(config.email_from, receivers, message)
        except:
            raise SendError()

def get_im_queued_node(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.im_username,
               l.id,
               n.nodename,
               "",
               l.log_level
             from log l
               join nodes n on l.node_id=n.node_id
               join auth_group g on n.team_responsible=g.role
               join auth_membership am on am.group_id=g.id
               join auth_user u on am.user_id=u.id
             where
               u.im_notifications = 'T' and
               u.im_username is not NULL and
               u.im_log_level+0 <= l.log_level+0 and
               l.svc_id = "" and
               l.node_id != "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_gtalk_sent=0
             group by l.id, u.id
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
            ids |= set([row[4]])
        elif row[3] == addr and len(j.lines) <= max_entries_per_msg:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

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
               "",
               l.log_level
             from log l,
               (select im_username, im_log_level from auth_user u
                 join auth_membership am on u.id=am.user_id
                 join auth_group g on am.group_id=g.id
                where
                  g.role="Manager" and
                  u.im_username is not NULL and
                  u.im_notifications = 'T') t
             where
               t.im_log_level+0 <= l.log_level+0 and
               l.svc_id = "" and
               l.node_id = "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_gtalk_sent=0
             group by l.id, t.im_username
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
            ids |= set([row[4]])
        elif row[3] == addr and len(j.lines) <= max_entries_per_msg:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

def get_im_queued_svc(q):
    conn = get_conn()
    if conn is None:
        return []
    sql = """select
               l.log_date,
               l.log_fmt,
               l.log_dict,
               u.im_username,
               l.id,
               n.nodename,
               s.svcname,
               l.log_level
             from log l
               join services s on l.svc_id=s.svc_id
               join apps a on s.svc_app=a.app
               join apps_responsibles ar on a.id=ar.app_id
               join auth_membership am on ar.group_id=am.group_id
               join auth_user u on am.user_id=u.id
               left join nodes n on l.node_id=n.node_id
             where
               u.im_log_level+0 <= l.log_level+0 and
               u.im_notifications = 'T' and
               u.im_username is not NULL and
               l.svc_id != "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_gtalk_sent=0
             group by l.id, u.id
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
            ids |= set([row[4]])
        elif row[3] == addr and len(j.lines) <= max_entries_per_msg:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = im_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

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
    conn.commit()
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
               n.nodename,
               "",
               l.log_level
             from log l
               join nodes n on l.node_id=n.node_id
               join auth_group g on n.team_responsible=g.role
               join auth_membership am on am.group_id=g.id
               join auth_user u on am.user_id=u.id
             where
               u.email_log_level+0 <= l.log_level+0 and
               u.email_notifications = 'T' and
               u.email is not NULL and
               l.svc_id = "" and
               l.node_id != "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_email_sent=0
             group by l.id, u.id
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
            ids |= set([row[4]])
        elif row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

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
               "",
               l.log_level
             from log l,
               (select email, email_log_level from auth_user u
                 join auth_membership am on u.id=am.user_id
                 join auth_group g on am.group_id=g.id
                where
                  g.role="Manager" and
                  u.email is not NULL and
                  u.email_notifications = 'T') t
             where
               t.email_log_level+0 <= l.log_level+0 and
               l.svc_id = "" and
               l.node_id = "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_email_sent=0
             group by l.id, t.email
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
            ids |= set([row[4]])
        elif row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

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
               n.nodename,
               s.svcname,
               l.log_level
             from log l
               join services s on l.svc_id=s.svc_id
               join apps a on s.svc_app=a.app
               join apps_responsibles ar on a.id=ar.app_id
               join auth_membership am on ar.group_id=am.group_id
               join auth_user u on am.user_id=u.id
               left join nodes n on l.node_id=n.node_id
             where
               u.email_log_level+0 <= l.log_level+0 and
               u.email_notifications = 'T' and
               u.email is not NULL and
               l.svc_id != "" and
               l.log_date > date_sub(now(), interval 1 day) and
               l.log_email_sent=0
             group by l.id, u.id
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
            ids |= set([row[4]])
        elif row[3] == addr:
            j += row
            ids |= set([row[4]])
        else:
            q.put(j, block=True)
            n_job += 1
            addr = row[3]
            j = email_job(row)
            ids |= set([row[4]])
    cursor.close()
    conn.close()
    return counters(n_job=n_job, n_entry=n_entry, ids=ids)

def dequeue_worker_int(i, q):
    log = logging.getLogger("WORKER.%d"%i)
    try:
        dequeue_worker(i, q)
    except KeyboardInterrupt:
        log.info("keyboard interrupt")
        pass

def dequeue_worker(i, q):
    log = logging.getLogger("WORKER.%d"%i)
    log.debug("start worker")
    while True:
        job = q.get()
        if job is None:
            log.debug("stop on poison pill")
            break
        log.info("%s for %s\n%s"%(job.name, job.addr, str(job)))
        try:
            job()
        except SendError:
            log.error('error sending message to %s'%job.addr)
        q.task_done()
    sys.exit(0)

def get_conn():
    try:
        conn = MySQLdb.connect(host="dbopensvc",
                               user="opensvc",
                               passwd="opensvc",
                               db="opensvc")
    except MySQLdb.Error, e:
        qlog.error("Error %d: %s" % (e.args[0], e.args[1]))
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
    qlog.info("email enabled:%s, im enabled:%s"%(str(config.email), str(config.gtalk)))
    c = counters()
    while True:
        if config.email:
            c.reset()
            c += get_email_queued_svc(q)
            c += get_email_queued_node(q)
            c += get_email_queued_manager(q)

            if c.n_job > 0:
                start_workers(q)
                qlog.info("queued %d log entries in %d emails"%(c.n_entry, c.n_job))
                stop_workers(q)
                email_done(c.ids)

        if config.gtalk:
            c.reset()
            c += get_im_queued_svc(q)
            c += get_im_queued_node(q)
            c += get_im_queued_manager(q)

            if c.n_job > 0:
                start_workers(q)
                qlog.info("queued %d log entries in %d instant messages"%(c.n_entry, c.n_job))
                stop_workers(q)
                im_done(c.ids)

        time.sleep(10)

def dequeue_int():
    q = JoinableQueue()
    try:
        dequeue(q)
    except KeyboardInterrupt:
        qlog.info("keyboard interrupt")
        stop_workers(q)
        pass

setup_log()
qlog = logging.getLogger("QUEUE.MANAGER")
jlog = logging.getLogger("JOB")
#dequeue_int()
try:
    lockfd = alertd_lock(lockfile)
    fork(dequeue_int)
    alertd_unlock(lockfd)
except lock.lockError:
    sys.exit(0)
except:
    sys.exit(1)
