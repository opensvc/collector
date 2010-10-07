def user_roles(uid):
    q = db.auth_membership.user_id == uid
    q &= db.auth_membership.group_id == db.auth_group.id
    rows = db(q).select(db.auth_group.role)
    return [r.role for r in rows]

def user_apps(uid):
    q = db.auth_user.id == uid
    q &= db.auth_user.id == db.auth_membership.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.id == db.apps_responsibles.group_id
    q &= db.apps_responsibles.app_id == db.apps.id
    rows = db(q).select(db.apps.app, groupby=db.apps.id)
    return [r.app for r in rows]

def alerts_apps_without_responsible(user):
    import datetime
    now = datetime.datetime.now()
    delay = datetime.timedelta(hours=24)

    if 'Manager' not in user_roles(user.id):
        return

    q = db.v_apps.mailto==None
    q &= db.v_apps.app==db.apps.app
    q &= db.apps.updated<now-delay
    rows = db(q).select()
    apps = [r.v_apps.app for r in rows]
    if len(apps) == 0:
        return

    h = {}
    h['subject'] = "applications with no declared responsibles"
    h['body'] = ', '.join(apps)
    h['mailto'] = user.email

    send_alert(h)
    db.alerts.insert(subject=h['subject'],
                     body=['body'],
                     sent_at=now,
                     sent_to=h['mailto'])

    return dict(alerts=apps)

def alerts_services_not_updated(user):
    """ Alert if service is not updated for 48h
    """
    h = {}
    import datetime
    now = datetime.datetime.now()
    two_days_ago = now - datetime.timedelta(days=2)
    three_days_ago = now - datetime.timedelta(days=3)

    def format_subject(row):
        return T("[%(app)s][%(svcname)s] service configuration not updated since %(last)s", dict(
                 last=row.updated,
                 app=row.svc_app,
                 svcname=row.svc_name
                )
               )

    q = db.v_services.updated<two_days_ago
    if 'Manager' not in user_roles(user.id):
        q &= db.v_services.svc_app.belongs(user_apps(user.id))

    cancelled = []
    body = []
    rows = db(q).select()
    for row in rows:
        msg = DIV(
                "Last status update occured on %s."%str(row.updated),
                BR(),
                "This service will be purged on %s"%str(row.updated + datetime.timedelta(days=3)),
              )
        body.append(alert_format_body(msg, svcname=row.svc_name, app=row.svc_app, svctype=row.svc_type))

    if len(rows) > 0:
        h['body'] = SPAN(body)
        h['subject'] = "service configurations not updated"
        h['mailto'] = user.email
        send_alert(h)
        db.alerts.insert(subject=h['subject'],
                         body=h['body'],
                         sent_at=now,
                         domain=domainname(row.svc_name),
                         sent_to=h['mailto'])

    return dict(alerts=[r.svc_name for r in rows])

def purge_services_not_updated():
    import datetime
    now = datetime.datetime.now()
    three_days_ago = now - datetime.timedelta(days=3)
    """ Remove the service after 3 days
    """
    rows = db(db.v_services.updated<three_days_ago).select()
    for row in rows:
        db(db.svcmon.mon_svcname==row.svc_name).delete()
        db(db.services.svc_name==row.svc_name).delete()

    return dict(deleted=rows)

def alerts_svcmon_not_updated(user):
    """ Alert if svcmon is not updated for 2h
    """
    import datetime
    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)

    def format_subject(row):
        return "[%(app)s][%(svcname)s] service status not updated for more than 2h (%(date)s)"%dict(app=row.svc_app, svcname=row.mon_svcname, date=str(row.mon_updated))

    q = db.v_svcmon.mon_updated<two_hours_ago
    if 'Manager' not in user_roles(user.id):
        q &= db.v_svcmon.svc_app.belongs(user_apps(user.id))
    rows = db(q).select()

    dup = []
    alert = []
    for row in rows:
        h = {}
        h['subject'] = format_subject(row)
        q = db.alerts.subject==h['subject']
        q &= db.alerts.sent_to==user.email
        dups = db(q).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            dup.append(row.mon_svcname)
            continue

        alert.append(row.mon_svcname)
        h['mailto'] = user.email
        h['body'] = alert_format_body(
          "Service will be purged from database on %s"%str(row.mon_updated+datetime.timedelta(days=1)),
          svcname=row.mon_svcname,
          app=row.svc_app,
          node=row.mon_nodname,
          svctype=row.svc_type
        )
        send_alert(h)
        db.alerts.insert(subject=h['subject'],
                         body=['body'],
                         sent_at=now,
                         domain=domainname(row.mon_svcname),
                         sent_to=h['mailto'])
    return dict(cancelled=dup, alerts=alert)

def purge_svcmon_not_updated():
    """ Remove the service after 24h
    """
    import datetime
    now = datetime.datetime.now()
    one_day_ago = now - datetime.timedelta(days=1)

    rows = db(db.v_svcmon.mon_updated<one_day_ago).select()
    for row in rows:
        db(db.svcmon.mon_svcname==row.mon_svcname).delete()
        db(db.services.svc_name==row.mon_svcname).delete()

    return dict(deleted=[r.mon_svcname for r in rows])

def alerts_failed_actions_not_acked(user):
    """ Actions not ackowleged : Alert responsibles & Acknowledge
        This function is meant to be scheduled daily, at night,
        and alerts generated should be sent as soon as possible.
    """
    def format_body(p):
        b = []

        for pid in p:
            err = p[pid]
            b.append(alert_format_body(
                       map(P, err['log']),
                       node=err['node'],
                       svcname=err['svcname'],
                       app=err['app'],
                       pid=pid,
                       action=err['action'],
                       begin=err['begin'],
                       end=err['end']))
        return DIV(map(DIV, b))

    def log_alert(h):
        db.alerts.insert(subject=h['subject'],
                         body=h['body'],
                         sent_at=now,
                         domain=h['domain'],
                         sent_to=user.email)

    import datetime

    subject = "unacknowledged failed actions"
    now = datetime.datetime.now()
    delay = datetime.timedelta(hours=24)
    rids = set([])

    """ group all alerts for a user in a single mail
    """
    rows = []
    apps = user_apps(user.id)
    if len(apps) > 0:
        q = db.v_svcactions.app.belongs(apps)
        q &= db.v_svcactions.end<now-delay
        q &= db.v_svcactions.status=='err'
        q &= ((db.v_svcactions.ack!=1)|(db.v_svcactions.ack==None))
        rows = db(q).select(orderby=db.v_svcactions.end|db.v_svcactions.pid)

    if len(rows) ==  0:
       return dict(alert=[])

    h = {}
    p = {}
    for row in rows:
        """ print only one header for logs of actions with same pid
        """
        pid = row.pid
        if pid not in h:
            p[pid] = {}
            p[pid]['log'] = []
            p[pid]['rid'] = []
            p[pid]['node'] = row.hostname
            p[pid]['svcname'] = row.svcname
            p[pid]['app'] = row.app
            p[pid]['action'] = row.action
            p[pid]['begin'] = row.begin

        p[pid]['log'] += str(row.status_log).split('\\n')
        p[pid]['end'] = row.end
        rids |= set([row.id])

    h['mailto'] = user.email
    h['subject'] = subject
    h['body'] = format_body(p)
    h['domain'] = domainname(row.svcname)

    send_alert(h)
    log_alert(h)

    return dict(alert=rids)

def purge_failed_actions_not_acked(rids):
    """ Ack all actions we sent an alert for
    """
    if len(rids) == 0:
        return dict(count=0)

    import datetime
    now = datetime.datetime.now()

    ack_comment = "Automatically acknowledged upon ticket generation.  Alert sent to responsibles."
    q = db.SVCactions.id.belongs(rids)
    count = db(q).update(ack=1,
                         acked_comment=ack_comment,
                         acked_date=now,
                         acked_by="admin@opensvc.com")
    return dict(acked=count)

def cron_alerts_daily():
    q = db.auth_user.email_notifications==True
    users = db(q).select(db.auth_user.id,
                         db.auth_user.email)
    h = {}
    rids = set()
    for user in users:
        h[user.email] = {}
        h[user.email]['svc_not_updated'] = alerts_services_not_updated(user)
        h[user.email]['apps_wo_resp'] = alerts_apps_without_responsible(user)
        h[user.email]['failed_actions_not_acked'] = alerts_failed_actions_not_acked(user)
        rids |= set(h[user.email]['failed_actions_not_acked']['alert'])

    purge_failed_actions_not_acked(rids)
    purge_services_not_updated()
    purge_svcmon_not_updated()

    return dict(done=h)

def cron_alerts_hourly():
    q = db.auth_user.email_notifications==True
    users = db(q).select(db.auth_user.id,
                         db.auth_user.email)
    h = {}
    for user in users:
        h[user.email] = {}
        h[user.email]['svcmon_not_updated'] = alerts_svcmon_not_updated(user)

    return dict(done=h)

def send_alert(h):
    """ Send mail alert
    """
    import smtplib
    import datetime

    now = datetime.datetime.now()
    server = smtplib.SMTP('localhost')
    botaddr = 'admin@opensvc.com'
    msg = "To: %s\r\nFrom: %s\r\nSubject: %s\r\nContent-type: text/html;charset=utf-8\r\n\r\n%s"%(h['mailto'], botaddr, h['subject'], h['body'])
    server.sendmail(botaddr, h['mailto'].split(", "), msg)
    server.quit()

    return dict(alert_sent=h)


