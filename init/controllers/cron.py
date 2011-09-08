def rotate_stats():
    """ lower data resolution with ageing
    """
    thres1 = now - datetime.timedelta(days=30)
    thres2 = now - datetime.timedelta(days=180)

    sql = """
     delete from stats_fs_u
     where date<"%(thres1)s" and date>="%(thres2)s" and
     id not in (
       select id from (
         select MAX(id) as id,
         CONCAT(YEAR(date),'-',MONTH(date),'-',DAY(date),' ',HOUR(date)) as d,
         nodename
         from stats_fs_u
         where date<"%(thres1)s" and date>"%(thres2)s"
         group by d,nodename,mntpt
       ) tmp1
     )
    """%dict(thres1=thres1, thres2=thres2)
    db.executesql(sql)
    sql = """
     delete from stats_fs_u
     where date<"%(thres2)s" and
     id not in (
       select id from (
         select MAX(id) as id,
         CONCAT(YEAR(date),'-',MONTH(date),'-',DAY(date)) as d,
         nodename
         from stats_fs_u
         where date<"%(thres2)s"
         group by d,nodename,mntpt
       ) tmp1
     )
    """%dict(thres1=thres1, thres2=thres2)
    db.executesql(sql)

def refresh_b_action_errors():
    sql = """truncate b_action_errors;"""
    db.executesql(sql)
    sql = """insert into b_action_errors
               select NULL, m.mon_svcname, m.mon_nodname, count(a.id)
               from svcmon m
                 left join SVCactions a
                 on m.mon_svcname=a.svcname and m.mon_nodname=a.hostname
               where a.status='err'
                 and (a.ack=0 or isnull(a.ack))
               group by m.mon_svcname, m.mon_nodname;
          """
    db.executesql(sql)

def refresh_b_apps():
    try:
        sql = "drop table if exists b_apps_new"
        db.executesql(sql)
        sql = "create table b_apps_new like b_apps"
        db.executesql(sql)
        sql = "insert into b_apps_new select * from v_apps"
        db.executesql(sql)
        sql = "drop table if exists b_apps_old"
        db.executesql(sql)
        sql = "rename table b_apps to b_apps_old, b_apps_new to b_apps"
        db.executesql(sql)
    except:
        sql = "drop table if exists b_apps"
        db.executesql(sql)
        sql = """CREATE TABLE `b_apps` (
  `id` int(11) NOT NULL DEFAULT '0',
  `app` varchar(20) CHARACTER SET latin1 NOT NULL,
  `roles` varchar(342) DEFAULT NULL,
  `responsibles` varchar(342) DEFAULT NULL,
  `mailto` varchar(342) DEFAULT NULL,
  KEY `i_app` (`app`)
)
"""
        db.executesql(sql)
        sql = "insert into b_apps select * from v_apps"
        db.executesql(sql)

def svc_log_update(svcname, astatus):
    q = db.services_log.svc_name == svcname
    o = ~db.services_log.id
    rows = db(q).select(orderby=o, limitby=(0,1))
    end = datetime.datetime.now()
    if len(rows) == 1:
        prev = rows[0]
        if prev.svc_availstatus == astatus:
            id = prev.id
            q = db.services_log.id == id
            db(q).update(svc_end=end)
        else:
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=prev.svc_end,
                                   svc_end=end,
                                   svc_availstatus=astatus)
    else:
        db.services_log.insert(svc_name=svcname,
                               svc_begin=end,
                               svc_end=end,
                               svc_availstatus=astatus)

def cron_scrub_svcstatus():
    """ Mark undef the services with 0 instance updating their status
    """
    q = db.v_outdated_services.uptodate == 0
    svcs = [r.svcname for r in db(q).select(db.v_outdated_services.svcname)]
    q = db.services.svc_name.belongs(svcs)
    if len(svcs) > 0:
        q &= (db.services.svc_status != 'undef') | (db.services.svc_availstatus != 'undef')
        svcs_new = [r.svc_name for r in db(q).select(db.services.svc_name)]
        db(q).update(svc_status="undef", svc_availstatus="undef")
        for svcname in svcs_new:
            _log("service.status",
                 "service '%(svc)s' has zero live instance. Status flagged 'undef'",
                 dict(svc=svcname),
                 svcname=svcname,
                 level="error")
    for svcname in svcs:
        svc_log_update(svcname, "undef")

def cron_stats():
    # refresh db tables
    cron_stat_day()
    cron_stat_day_svc()

def cron_stat_day():
    #when = datetime.datetime.now()-datetime.timedelta(days=14)
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    pairs = ["nb_svc=(select count(distinct svc_name) from services)"]
    pairs += ["nb_action=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s')"%(begin, end)]
    pairs += ["nb_action_err=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='err')"%(begin, end)]
    pairs += ["nb_action_warn=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='warn')"%(begin, end)]
    pairs += ["nb_action_ok=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='ok')"%(begin, end)]
    pairs += ["nb_apps=(select count(distinct svc_app) from services)"]
    pairs += ["nb_accounts=(select count(distinct id) from auth_user)"]
    pairs += ["nb_svc_with_drp=(select count(distinct svc_name) from services where svc_drpnode is not NULL and svc_drpnode!='')"]
    pairs += ["nb_svc_prd=(select count(distinct svc_name) from services where svc_type='PRD')"]
    pairs += ["nb_svc_cluster=(select sum(length(svc_nodes)-length(replace(svc_nodes,' ',''))+1>1) from services)"]
    pairs += ["nb_nodes=(select count(distinct mon_nodname) from svcmon)"]
    pairs += ["nb_nodes_prd=(select count(distinct mon_nodname) from v_svcmon where environnement='PRD')"]
    pairs += ["disk_size=(select ifnull((select sum(t.disk_size) from (select distinct s.disk_id, s.disk_size from svcdisks s) t), 0))"]
    sql = "insert into stat_day set day='%(end)s', %(pairs)s on duplicate key update %(pairs)s"%dict(end=end, pairs=','.join(pairs))
    #raise Exception(sql)
    db.executesql(sql)

    # os lifecycle
    sql2 = """replace into lifecycle_os
              (lc_os_concat, lc_count, lc_date, lc_os_name, lc_os_vendor)
              select concat_ws(' ', os_name, os_vendor, os_release, os_arch) c,
                     count(nodename),CURDATE(), os_name, os_vendor
              from nodes group by c;"""
    db.executesql(sql2)

    return dict(sql=sql, sql2=sql2)

def cron_stat_day_svc():
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    rows = db(db.services.id>0).select(db.services.svc_name, groupby=db.services.svc_name)

    for row in rows:
        svc = row.svc_name
        pairs = ["nb_action=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_err=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='err' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_warn=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='warn' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_ok=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='ok' and hostname='%s')"%(begin, end, svc)]
        pairs += ["disk_size=(select sum(t.disk_size) from (select distinct s.disk_id, s.disk_size from svcdisks s where s.disk_svcname='%s') t)"%svc]
        sql = "insert into stat_day_svc set day='%(end)s', svcname='%(svc)s', %(pairs)s on duplicate key update %(pairs)s"%dict(end=end, svc=svc, pairs=','.join(pairs))
        #raise Exception(sql)
        db.executesql(sql)
    return dict(sql=sql)


#
# Misc
#
#######
def cron_unfinished_actions():
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=120)
    q = (db.SVCactions.begin < tmo)
    q &= (db.SVCactions.end==None)
    rows = db(q).select(orderby=db.SVCactions.id)
    db(q).update(status="err", end='1000-01-01 00:00:00')
    for r in rows:
        _log('action.timeout', "action ids %(ids)s closed on timeout",
              dict(ids=r.id),
              user='collector',
              svcname=r.svcname,
              nodename=r.hostname,
              level="warning")
    return "%d actions marked timed out"%len(rows)

def cron_scrub_checks():
    thres = now - datetime.timedelta(days=2)
    q = db.checks_live.chk_updated < thres
    return db(q).delete()

#
# Alerts and purges
#
####################

def alerts_apps_without_responsible():
    q = db.v_apps.mailto == None
    rows = db(q).select()
    apps = [r.v_apps.app for r in rows]

    if len(apps) == 0:
        return

    _log("app",
         "applications with no declared responsibles '%(app)s'",
         dict(app=', '.join(apps)),level="warning")

def alerts_services_not_updated():
    """ Alert if service is not updated for 48h
    """
    age = 2
    sql = """insert ignore
             into log
               select NULL,
                      "service.config",
                      "feed",
                      "service config not updated for more than %(age)d days (%%(date)s)",
                      concat('{"date": "', updated, '"}'),
                      now(),
                      svc_name,
                      NULL,
                      0,
                      0,
                      md5(concat("service.config.notupdated",svc_name,updated))
               from services
               where updated<date_sub(now(), interval %(age)d day);"""%dict(age=age)
    return db.executesql(sql)

def alerts_svcmon_not_updated():
    """ Alert if svcmon is not updated for 2h
    """
    age = 2
    sql = """insert ignore
             into log
               select NULL,
                      "service.status",
                      "feed",
                      "service status not updated for more than %(age)dh (%%(date)s)",
                      concat('{"date": "', mon_updated, '"}'),
                      now(),
                      mon_svcname,
                      mon_nodname,
                      0,
                      0,
                      md5(concat("service.status.notupdated",mon_nodname,mon_svcname,mon_updated))
               from v_svcmon
               where mon_updated<date_sub(now(), interval %(age)d hour);"""%dict(age=age)
    return db.executesql(sql)

def alerts_failed_actions_not_acked():
    """ Actions not ackowleged : Alert responsibles & Acknowledge
        This function is meant to be scheduled daily, at night,
        and alerts generated should be sent as soon as possible.
    """
    age = 1
    sql = """select id from SVCactions where
                 status="err" and
                 (ack=0 or ack is NULL) and
                 begin>date_sub(now(), interval 7 day) and
                 begin<date_sub(now(), interval %(age)d day);"""%dict(age=age)
    rows = db.executesql(sql)
    ids = map(lambda x: str(x[0]), rows)

    if len(ids) == 0:
        return

    sql = """insert ignore
             into log
               select NULL,
                      "service.action.notacked",
                      "feed",
                      "unacknowledged failed action '%%(action)s' at '%%(begin)s'",
                      concat('{"action": "', action, '", "begin": "', begin, '"}'),
                      now(),
                      svcname,
                      hostname,
                      0,
                      0,
                      md5(concat("service.action.notacked",hostname,svcname,begin)),
                      "warning"
               from SVCactions
               where
                 id in (%(ids)s);"""%dict(ids=','.join(ids))
    db.executesql(sql)

    import datetime
    now = datetime.datetime.now()

    """ Ack all actions we sent an alert for
    """
    sql = """update SVCactions set
               ack=1,
               acked_date="%(date)s",
               acked_comment="Automatically acknowledged",
               acked_by="admin@opensvc.com"
             where id in (%(ids)s);"""%dict(ids=','.join(ids), date=now)
    db.executesql(sql)
    refresh_b_action_errors()

def cron_alerts_daily():
    alerts_apps_without_responsible()
    alerts_services_not_updated()
    alerts_failed_actions_not_acked()

def cron_alerts_hourly():
    rets = []
    rets.append(alerts_svcmon_not_updated())
    return rets

