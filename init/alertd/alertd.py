#!/usr/bin/python

import os
import sys
import time
import optparse
import datetime
import MySQLdb
import json
import smtplib
from multiprocessing import Process, JoinableQueue, Queue
from subprocess import Popen
import logging
import logging.handlers
import xmpp
import requests

basedir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(basedir)
sys.path.append(os.path.join(basedir,"..","modules"))

import lock
import config

SEVERITIES = {
    "notice": 0,
    "warning": 1,
    "error": 2,
    "critical": 3,
    "alert": 4,
}
SEVERITY_NAMES = {
    0: "notice",
    1: "warning",
    2: "error",
    3: "critical",
    4: "alert",
}
COLORS = {
    4: "#292b2c",
    3: "#990000",
    2: "#dd0000",
    1: "#ffa500",
    0: "#009900",
}
WEEKDAYS = {
    0: "mon",
    1: "tue",
    2: "wed",
    3: "thu",
    4: "fri",
    5: "sat",
    6: "sun",
}

DEFAULTS = {
    "dbopensvc_host": "127.0.0.1",
    "dbopensvc_user": "opensvc",
    "dbopensvc_password": "opensvc",
    "xmpp": False,
    "xmpp_port": 5222,
    "xmpp_host": "talk.google.com",
    "http_host": "collector",
    "title": "collector",
    "slack": False,
    "email": False,
    "email_from": "collector",
    "email_ssl": False,
    "email_tls": False,
}

OPTIONS = {}

def config_get(param):
    try:
        val = OPTIONS[param]
        if val is not None:
            return val
    except Exception:
        pass
    try:
        return os.environ[param.upper().replace("-", "_")]
    except Exception:
        pass
    try:
        return getattr(config, param)
    except Exception:
        pass
    return DEFAULTS.get(param)

def fmt_desc(data):
    try:
        fmt = data["fmt"]
        dic = json.loads(data["dict"])
        desc = fmt % dic
    except:
        desc = ""
    return desc

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

    fn(kwargs)
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

def get_conn():
    try:
        conn = MySQLdb.connect(host=config_get("dbopensvc_host"),
                               user=config_get("dbopensvc_user"),
                               passwd=config_get("dbopensvc_password"),
                               db="opensvc")
    except MySQLdb.Error, e:
        return None
    return conn

def mark_done(proto, user_id, alert_ids):
    conn = get_conn()
    if conn is None:
        return []
    for alert_id in alert_ids:
        sql = """insert into alerts_sent
                 (user_id, alert_id, msg_type) values
                 (%d, %d, "%s")""" % (user_id, alert_id, proto)
        cursor = conn.cursor()
        cursor.execute(sql)
    sql = "commit"
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.close()

def sql_list(l):
    return ",".join([repr(s) for s in l])

def dequeue_worker_int(i, q):
    log = logging.getLogger("WORKER.%d"%i)
    log.info("worker %d started" % i)
    try:
        dequeue_worker(i, q)
    except KeyboardInterrupt:
        log.info("keyboard interrupt")
        pass

def dequeue_worker(i, q):
    log = logging.getLogger("WORKER.%d"%i)
    while True:
        job = q.get()
        if job is None:
            break
        log.info("%s for %s\n"%(job.name, job.addr))
        try:
            job()
        except SendError as exc:
            log.error('error sending message to %s: %s'%(job.addr, str(exc)))
        q.task_done()
    sys.exit(0)

##############################################################################
#
# Exceptions
#
##############################################################################
class JobFull(Exception):
    pass

class SendError(Exception):
    pass

##############################################################################
#
# Protocol drivers
#
##############################################################################
class GenericJob(object):
    def digest(self, data):
        dig = {
            "severity": SEVERITY_NAMES[data["severity"]],
            "created": data["created"].strftime("%Y-%m-%d %H:%M:%S"),
            "id": data["id"],
            "desc": fmt_desc(data),
            "type": data["type"],
            "color": COLORS[data["severity"]],
            "nodename": "",
            "node_link": "",
            "svcname": "",
            "svc_link": "",
            "env": "",
            "app": "",
            "app_link": "",
        }
        if data["node_id"] != "":
            dig["nodename"] = data["nodename"]
            dig["node_link"] = "https://%s/init/show/tabs/node/%s" % (config_get("http_host"), data["node_id"])
            if data["svc_id"] == "":
                dig["app_link"] = "https://%s/init/show/tabs/app/%s" % (config_get("http_host"), data["node_app"])
                dig["app"] = data["node_app"]
                dig["env"] = data["node_env"]
        if data["svc_id"] != "":
            dig["svc_link"] = "https://%s/init/show/tabs/svc/%s" % (config_get("http_host"), data["svc_id"])
            dig["svcname"] = data["svcname"]
            dig["app_link"] = "https://%s/init/show/tabs/app/%s" % (config_get("http_host"), data["svc_app"])
            dig["app"] = data["svc_app"]
            dig["env"] = data["svc_env"]
        return dig

class XmppJob(GenericJob):
    max_alerts = 10

    def __init__(self, user, data=None):
        self.name = "Xmpp messaging job"
        self.user = user
        self.addr = user["im_username"].strip("'")
        self.alerts = []
        self.alert_ids = []
        if data:
            self += data

    def __iadd__(self, data):
        if len(self.alerts) > self.max_alerts:
            raise JobFull
        self.alerts.append(self.digest(data))
        self.alert_ids.append(data["id"])
        return self

    def __str__(self):
        s = ""
        for data in self.alerts:
            s += self.format_alert(data)
        return s

    def format_alert(self, data):
        if "svcname" in data:
            return "%(created)s %(severity)s %(type)s %(desc)s app=%(app)s env=%(env)s svcname=%(svcname)s nodename=%(nodename)s\n" % data
        else:
            return "%(created)s %(severity)s %(type)s %(desc)s app=%(app)s env=%(env)s nodename=%(nodename)s\n" % data

    def __call__(self):
        message = str(self)
        try:
            jid = xmpp.protocol.JID(config_get("xmpp_username"))
            if not jid:
                raise Exception("xmpp_username not set")
            if "@" not in self.addr:
                self.addr = self.addr+"@"+jid.getDomain()
            c = xmpp.Client(jid.getDomain(), debug=[])
            c.connect((config_get("xmpp_host"), config_get("xmpp_port")))
            c.auth(jid.getNode(), config_get("xmpp_password"))
            c.send(xmpp.protocol.Message(self.addr, message, typ='chat'))
            mark_done("xmpp", self.user["id"], self.alert_ids)
        except Exception as exc:
            raise SendError(str(exc))

class SlackJob(GenericJob):
    max_attachments = 10

    def __init__(self, user, data=None):
        self.name = "Slack messaging job"
        self.user = user
        self.addr = user["im_username"]
        self.attachments = []
        self.alert_ids = []
        if data:
            self += data

    def __iadd__(self, data):
        if len(self.attachments) > self.max_attachments:
            raise JobFull
        self.alert_ids.append(data["id"])
        data = self.digest(data)

        l = {
            "fallback": ": ".join((data["type"], data["desc"])),
            "title": data["type"],
            "text": data["desc"],
            #"pretext": "",
            "color": data["color"],
            "fields": [],
        }
        def fmt_field(k, v):
            l["fields"].append({
                "title": k,
                "value": v,
                "short": True,
            })
        l["fields"].append(fmt_field("severity", data["severity"]))
        l["fields"].append(fmt_field("created", data["created"]))
        if data["svc_link"] != "":
            v = "<%s|%s>" % (data["svc_link"], data["svcname"])
            l["fields"].append(fmt_field("service", v))
        if data["node_link"] != "":
            v = "<%s|%s>" % (data["node_link"], data["nodename"])
            l["fields"].append(fmt_field("node", v))
        if data["app_link"] != "":
            v = "<%s|%s>" % (data["app_link"], data["app"])
            l["fields"].append(fmt_field("app", v))
        if data["env"] != "":
            l["fields"].append(fmt_field("env", data["env"]))
        self.attachments.append(l)
        return self

    def __str__(self):
        return "%s to %s: %s" % (self.name, self.user["im_username"], str(self.attachments))

    def __call__(self):
        try:
            self.slacksend()
            mark_done("slack", self.user["id"], self.alert_ids)
        except Exception as exc:
            raise SendError(str(exc))

    def slacksend(self):
        payload = {
            'channel': "@"+self.addr,
            'username': config_get("title"),
            'attachments': self.attachments,
            'parse': 'none',
            'icon_url': ('http://www.opensvc.com/init/static/images/opensvc-logo-64.png'),
        }
        data = json.dumps(payload)
        try:
            response = requests.post(config_get("slack_webhook_url"), data=data)
            return response
        except Exception as exc:
            log = logging.getLogger("JOB.SLACK")
            log.warning('submit to Slack: %s' % str(exc))

class EmailJob(GenericJob):
    max_alerts = 100

    def __init__(self, user, data=None):
        self.name = "Email job"
        self.user = user
        self.addr = user["email"]
        self.alerts = []
        self.alert_ids = []
        if data:
            self += data

    def __iadd__(self, data):
        if len(self.alerts) > self.max_alerts:
            raise JobFull
        self.alerts.append(self.digest(data))
        self.alert_ids.append(data["id"])
        return self

    def __str__(self):
        #return self.text()
        return self.html()

    def text(self):
        s = ""
        for d in self.alerts:
            s += self.format_alert_text(d)
        return s

    def format_alert_text(self, data):
        if "svcname" in data:
            return "%(created)s %(severity)s %(type)s %(desc)s app=%(app)s env=%(env)s svcname=%(svcname)s nodename=%(nodename)s\n" % data
        else:
            return "%(created)s %(severity)s %(type)s %(desc)s app=%(app)s env=%(env)s nodename=%(nodename)s\n" % data

    def html(self):
        header = "<html><table>" \
                  "<tr style='text-align:left'>" \
                  "<th>Created</th>" \
                  "<th>Severity</th>" \
                  "<th>Type</th>" \
                  "<th>Description</th>" \
                  "<th>App</th>" \
                  "<th>Env</th>" \
                  "<th>Service</th>" \
                  "<th>Node</th>" \
                  "</tr>"
        footer = "</table></html>"
        body = ""
        for d in self.alerts:
            body += self.format_alert_html(d)
        return header + body + footer

    def format_alert_html(self, data):
        s = "<tr>" \
            "<td>%(created)s</td>" \
            "<td style='color:%(color)s'>%(severity)s</td>" \
            "<td>%(type)s</td>" \
            "<td>%(desc)s</td>" \
            "<td><a href='%(app_link)s'>%(app)s</a></td>" \
            "<td>%(env)s</td>" \
            "<td><a href='%(svc_link)s'>%(svcname)s</a></td>" \
            "<td><a href='%(node_link)s'>%(nodename)s</a></td>" \
            "</tr>\n" % data
        return s

    def __call__(self):
        receivers = [self.addr]
        ts = time.time()
        sender = config_get("email_from")
        ses = sender.index("@")
        sender = sender[:ses] + "+" + str(ts) + sender[ses:]
        message = "From: %(sender_name)s <%(sender)s>\n" \
                  "To: %(rcpt)s\n" \
                  "Subject: %(n)d OpenSVC alerts\n" \
                  "Content-Type: text/html; charset=UTF-8\n" \
                  "%(body)s\n" % dict(
            n=len(self.alerts),
            sender_name=config_get("title", "OpenSVC Collector"),
            sender=sender,
            rcpt=self.addr,
            body=str(self)
        )

        try:
            if config_get("email_ssl"):
                server = smtplib.SMTP_SSL(config_get("email_host"))
            else:
                server = smtplib.SMTP(config_get("email_host"))
            if config_get("email_tls") and not config_get("email_ssl"):
                hostname = None
                server.ehlo(hostname)
                server.starttls()
                server.ehlo(hostname)
            login = config_get("email_login")
            if login:
                server.login(*login.split(':', 1))
            server.sendmail(config_get("email_from"), receivers, message)
            server.quit()
            mark_done("email", self.user["id"], self.alert_ids)
        except Exception as exc:
            raise SendError(str(exc))

PROTOCOLS = {
    "email": {
        "job": EmailJob,
        "min_sev": "email_log_level",
        "notifications_delay": "email_notifications_delay",
    },
    "xmpp": {
        "job": XmppJob,
        "min_sev": "im_log_level",
        "notifications_delay": "im_notifications_delay",
    },
    "slack": {
        "job": SlackJob,
        "min_sev": "im_log_level",
        "notifications_delay": "im_notifications_delay",
    },
}

##############################################################################
#
# Alert daemon
#
##############################################################################

class Alertd(object):
    n_threads = 10
    users = None
    lockfd = None
    processes = []
    max_entries_per_msg = 10
    loop_interval = 5
    janitor_interval = 20
    janitor_loops = janitor_interval // loop_interval + 1

    def __init__(self):
        self.setup_log()
        self.lockfile = __file__+'.lock'
        self.queue = JoinableQueue()

        for i in range(0, self.n_threads):
            self.processes.append(None)

        try:
            with open(basedir+"/../static/mail.css", "r") as f:
                self.style = f.read()
        except:
            self.style = ""

    def setup_log(self):
        self.log = logging.getLogger()
        fileformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #logfile = os.path.join(basedir, 'alertd.log')
        #filehandler = logging.handlers.RotatingFileHandler(logfile,
        #                                                   maxBytes=5242880,
        #                                                   backupCount=5)
        #filehandler.setFormatter(fileformatter)
        #self.log.addHandler(filehandler)
        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(fileformatter)
        self.log.addHandler(streamhandler)
        self.log.setLevel(logging.INFO)

    def alertd_lock(self):
        try:
            self.lockfd = lock.lock(timeout=0, delay=0, lockfile=self.lockfile)
        except lock.lockTimeout:
            self.log.info("timed out waiting for lock")
            raise lock.lockError
        except lock.lockNoLockFile:
            self.log.info("lock_nowait: set the 'lockfile' param")
            raise lock.lockError
        except lock.lockCreateError:
            self.log.info("can not create lock file %s"%lockfile)
            raise lock.lockError
        except lock.lockAcquire as e:
            self.log.info("another alertd is currently running (pid=%s)"%e.pid)
            raise lock.lockError
        except:
            self.log.error("unexpected locking error")
            import traceback
            traceback.print_exc()
            raise lock.lockError

    def alertd_unlock(self):
        if self.lockfd is None:
            return
        lock.unlock(self.lockfd)
        self.lockfd = None

    def enqueue_user(self, user, proto):
        Job = PROTOCOLS[proto]["job"]
        min_sev = user[PROTOCOLS[proto]["min_sev"]]
        delay = user[PROTOCOLS[proto]["notifications_delay"]]
        conn = get_conn()
        if conn is None:
            return []
        sql = """select
                   a.id,
                   a.dash_created,
                   a.dash_severity,
                   a.dash_type,
                   a.dash_fmt,
                   a.dash_dict,
                   a.node_id,
                   a.svc_id,
                   n.nodename,
                   s.svcname,
                   n.app,
                   n.node_env,
                   s.svc_app,
                   s.svc_env
                 from dashboard a
                   left join services s on a.svc_id=s.svc_id
                   left join nodes n on a.node_id=n.node_id
                 where
                   a.dash_created <= DATE_SUB(NOW(), INTERVAL %(delay)d MINUTE) and
                   a.dash_severity >= %(min_sev)d and
                   (s.svc_notifications="T" or s.svc_notifications is NULL) and
                   s.svc_snooze_till is NULL and
                   (n.notifications="T" or n.notifications is NULL) and
                   n.snooze_till is NULL and
                   not a.id in (select alert_id from alerts_sent where user_id=%(user_id)d and msg_type="%(proto)s")
                   %(where)s
                 limit 1000
        """ % dict(
            user_id=user["id"],
            where=user["where"],
            proto=proto,
            min_sev=min_sev,
            delay=delay,
        )

        cursor = conn.cursor()
        cursor.execute(sql)
        addr = None
        ids = set([])
        j = None
        while (1):
            row = cursor.fetchone()
            if row is None:
                break
            if j is None:
                j = Job(user)
            data = {
                "id": int(row[0]),
                "created": row[1],
                "severity": int(row[2]),
                "type": row[3],
                "fmt": row[4],
                "dict": row[5],
                "node_id": row[6],
                "svc_id": row[7],
                "nodename": row[8],
                "svcname": row[9],
                "node_app": row[10],
                "node_env": row[11],
                "svc_app": row[12],
                "svc_env": row[13],
            }
            try:
                j += data
            except JobFull:
                self.queue.put(j, block=True)
                j = Job(user, data)
            ids |= set([row[0]])
        if j is not None:
            self.queue.put(j, block=True)
        cursor.close()
        conn.close()

    def start_workers(self):
        for i in range(0, self.n_threads):
            p = Process(target=dequeue_worker_int, args=(i, self.queue), name='[worker%d]'%i)
            p.start()
            self.processes[i] = p

    def stop_workers(self):
        """ TODO: need to wait for worker idling before stop """
        for p in self.processes:
            self.queue.put(None)
        for p in self.processes:
            if p is None:
                continue
            p.join()

    def get_user_nodes(self, user, conn):
        sql = """select n.node_id from
                   auth_membership am,
                   apps_responsibles ar,
                   apps a,
                   nodes n
                 where
                   am.user_id=%d and
                   am.group_id=ar.group_id and
                   ar.app_id=a.id and
                   a.app=n.app
            """%user["id"]
        cursor = conn.cursor()
        cursor.execute(sql)
        data = []
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            data.append(row[0])
        return data

    def get_user_services(self, user, conn):
        sql = """select s.svc_id from
                   auth_membership am,
                   apps_responsibles ar,
                   apps a,
                   services s
                 where
                   am.user_id=%d and
                   am.group_id=ar.group_id and
                   ar.app_id=a.id and
                   a.app=s.svc_app
            """%user["id"]
        cursor = conn.cursor()
        cursor.execute(sql)
        data = []
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            data.append(row[0])
        return data

    def get_users(self):
        self.users = {}
        conn = get_conn()
        if conn is None:
            return
        sql = """select
                   u.id,
                   u.email_notifications,
                   u.email_notifications_delay,
                   u.email,
                   u.email_log_level,
                   u.im_notifications,
                   u.im_notifications_delay,
                   u.im_username,
                   u.im_log_level,
                   u.im_type,
                   p.prefs
                 from auth_user u left join user_prefs p
                 on u.id=p.user_id
                 where
                   (not u.email is NULL and u.email_notifications='T') or
                   (not u.im_username is NULL and u.im_notifications='T')
        """
        cursor = conn.cursor()
        cursor.execute(sql)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            user = {
                "id": int(row[0]),
                "email_notifications": True if row[1]=="T" else False,
                "email_notifications_delay": row[2],
                "email": row[3],
                "email_log_level": SEVERITIES.get(row[4], 3),
                "im_notifications": True if row[5]=="T" else False,
                "im_notifications_delay": int(row[6]),
                "im_username": row[7],
                "im_log_level": SEVERITIES.get(row[8], 3),
                "im_type": row[9],
                "notifications_periods": None,
            }
            try:
                prefs = json.loads(row[10])
                user["notifications_periods"] = prefs["notifications_periods"]
            except (ValueError, TypeError, KeyError):
                user["notifications_periods"] = None
            nodes = self.get_user_nodes(user, conn)
            services = self.get_user_services(user, conn)
            where = []
            if services:
                where.append("a.svc_id in (%s)" % sql_list(services))
            if nodes:
                where.append("a.node_id in (%s)" % sql_list(nodes))
            user["where"] = " or ".join(where)
            if user["where"]:
                user["where"] = "and (%s)" % user["where"]

            self.users[row[0]] = user
        conn.close()

    def in_period(self, user):
        if user["notifications_periods"] is None:
            return True
        now = datetime.datetime.now()
        day = WEEKDAYS[now.weekday()]
        period = user["notifications_periods"][day]
        if period is None or period["period"] == "always":
            return True
        if period["period"] == "never":
            return False
        val = "%02d:%02d" % (now.hour, now.minute)
        if val >= period["begin"] and val <= period["end"]:
            return True
        return False

    def enqueue_user_messages(self, user):
        if not self.in_period(user):
            self.log.info("user %d not in notification period", user["id"])
            return
        if user["email_notifications"] and config_get("email"):
            self.enqueue_user(user, "email")
        if user["im_notifications"]:
            if user["im_type"] == "xmpp" and config_get("xmpp"):
                self.enqueue_user(user, "xmpp")
            elif user["im_type"] == "slack" and config_get("slack"):
                self.enqueue_user(user, "slack")

    def purge_alerts_sent(self):
        conn = get_conn()
        if conn is None:
            return
        sql = """delete from alerts_sent where alert_id not in (select id from dashboard)"""
        cursor = conn.cursor()
        cursor.execute(sql)
        sql = "commit"
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.close()

    def janitor_snooze(self):
        conn = get_conn()
        if conn is None:
            return
        sql = """update nodes set snooze_till=NULL where snooze_till<NOW()"""
        cursor = conn.cursor()
        cursor.execute(sql)
        sql = """update services set svc_snooze_till=NULL where svc_snooze_till<NOW()"""
        cursor = conn.cursor()
        cursor.execute(sql)
        sql = "commit"
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.close()

    def run_forever(self):
        while True:
            try:
                self._run_forever()
            except KeyboardInterrupt:
                # propagate
                raise
            except Exception as exc:
                self.log.exception(exc)
                time.sleep(5)

    def _run_forever(self):
        iterations = 0
        while True:
            iterations += 1
            if iterations > self.janitor_loops or self.users is None:
                self.get_users()
                self.janitor_snooze()
                self.purge_alerts_sent()
                iterations = 0
            for user in self.users.values():
                self.enqueue_user_messages(user)
            time.sleep(self.loop_interval)

    def main(self):
        try:
            self.start_workers()
            self.run_forever()
        except KeyboardInterrupt:
            self.log.info("keyboard interrupt")
            pass
        finally:
            self.stop_workers()
            self.alertd_unlock()

def main(foreground=True):
    daemon = Alertd()
    try:
        daemon.alertd_lock()
        if foreground:
            daemon.main()
        else:
            fork(daemon.main)
    except lock.lockError:
        return 0
    except Exception as exc:
        import traceback
        traceback.print_exc(exc)
        return 1

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", default=False, action="store_true",
                      dest="foreground", help="Run in forground")
    parser.add_option("--email", action="store_true",
                      dest="email", help="Activate email alarming")
    parser.add_option("--email-from",
                      dest="email_from", help="The email sender address")
    parser.add_option("--email-host",
                      dest="email_host", help="The email server address or name")
    parser.add_option("--email-port",
                      dest="email_port", help="The email server port")
    parser.add_option("--email-ssl", action="store_true",
                      dest="email_ssl", help="Use SSL to communicate with the email server")
    parser.add_option("--email-tls", action="store_true",
                      dest="email_tls", help="Use TLS to communicate with the email server")
    parser.add_option("--slack", action="store_true",
                      dest="slack", help="Activate Slack alarming")
    parser.add_option("--slack-webhook-url",
                      dest="slack_webhook_url", help="The url to post Slack messages to")
    parser.add_option("--xmpp", action="store_true",
                      dest="xmpp", help="Activate XMPP alarming")
    parser.add_option("--xmpp-port", default="5222",
                      dest="xmpp_port", help="XMPP server port")
    parser.add_option("--xmpp-host",
                      dest="xmpp_host", help="XMPP server dns name")
    parser.add_option("--xmpp-username",
                      dest="xmpp_username", help="user to log in the XMPP server")
    parser.add_option("--xmpp-password",
                      dest="xmpp_password", help="user password to log in the XMPP server")
    parser.add_option("--http-host",
                      dest="http_host", help="The collector url to format links with")
    parser.add_option("--title",
                      dest="title", help="The bot name to display in Slack messages")
    options, _ = parser.parse_args()
    OPTIONS.update(vars(options))
    sys.exit(main(foreground=OPTIONS["foreground"]))
