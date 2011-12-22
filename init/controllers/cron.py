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
    db.commit()
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
    db.commit()

def refresh_b_action_errors():
    sql = """truncate b_action_errors;"""
    db.executesql(sql)
    db.commit()
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
    db.commit()

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
    db.commit()

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
    # global stats

    #when = datetime.datetime.now()-datetime.timedelta(days=14)
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    _cron_stat_day(end)

    # per filterset stats
    rows = db(db.gen_filtersets.id>0).select(db.gen_filtersets.id)
    for row in rows:
        _cron_stat_day(end, row.id)

def stat_nb_nodes(fset_id):
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id)
    n = db(q).count()
    print "stat_nb_nodes():", str(n)
    return n

def stat_nb_nodes_prd(fset_id):
    q = db.nodes.environnement.like("%pr%")
    q = apply_filters(q, db.nodes.nodename, None, fset_id)
    n = db(q).count()
    print "stat_nb_nodes_prd():", str(n)
    return n

def stat_nb_svc(fset_id):
    q = db.services.id < 0
    q = or_apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_nb_svc():", str(n)
    return n

def stat_nb_svc_cluster(fset_id):
    q = db.services.svc_nodes.like("% %")
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_nb_svc_cluster():", str(n)
    return n

def stat_nb_svc_prd(fset_id):
    q = db.services.svc_type == "PRD"
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_nb_svc_prd():", str(n)
    return n

def stat_nb_vcpu(fset_id):
    q = db.services.id < 0
    q = or_apply_filters(q, None, db.services.svc_name, fset_id)
    rows = db(q).select(db.services.svc_vcpus)
    n = 0
    for row in rows:
        n += row.svc_vcpus
    print "stat_nb_vcpu():", str(n)
    return n

def stat_nb_vmem(fset_id):
    q = db.services.id < 0
    q = or_apply_filters(q, None, db.services.svc_name, fset_id)
    rows = db(q).select(db.services.svc_vmem)
    n = 0
    for row in rows:
        n += row.svc_vmem
    print "stat_nb_vmem():", str(n)
    return n

def stat_nb_core(fset_id):
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id)
    rows = db(q).select(db.nodes.cpu_cores)
    n = 0
    for row in rows:
        n += row.cpu_cores
    print "stat_nb_cores():", str(n)
    return n

def stat_nb_mem(fset_id):
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id)
    rows = db(q).select(db.nodes.mem_bytes)
    n = 0
    for row in rows:
        n += row.mem_bytes
    # convert to GB
    n = n / 1024
    print "stat_nb_mem():", str(n)
    return n

def stat_nb_svc_with_drp(fset_id):
    q = db.services.svc_drpnodes != None
    q &= db.services.svc_drpnodes != ""
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_nb_svc_with_drp():", str(n)
    return n

now = datetime.datetime.now()
today = now - datetime.timedelta(hours=now.hour,
                                 minutes=now.minute,
                                 seconds=now.second,
                                 microseconds=now.microsecond)
yesterday = today - datetime.timedelta(days=1)

def stat_nb_action(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q = apply_filters(q, db.SVCactions.hostname, db.SVCactions.svcname, fset_id)
    n = db(q).count()
    print "stat_nb_action():", str(n)
    return n

def stat_nb_action_err(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "err"
    q = apply_filters(q, db.SVCactions.hostname, db.SVCactions.svcname, fset_id)
    n = db(q).count()
    print "stat_nb_action_err():", str(n)
    return n

def stat_nb_action_warn(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "warn"
    q = apply_filters(q, db.SVCactions.hostname, db.SVCactions.svcname, fset_id)
    n = db(q).count()
    print "stat_nb_action_warn():", str(n)
    return n

def stat_nb_action_ok(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "ok"
    q = apply_filters(q, db.SVCactions.hostname, db.SVCactions.svcname, fset_id)
    n = db(q).count()
    print "stat_nb_action_ok():", str(n)
    return n

def stat_nb_apps(fset_id):
    q = db.apps.app == db.services.svc_app
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = len(db(q).select(groupby=db.apps.app))
    print "stat_nb_apps():", str(n)
    return n

def stat_nb_accounts(fset_id):
    q = db.auth_user.id > 0
    n = len(db(q).select())
    print "stat_nb_accounts():", str(n)
    return n

def stat_nb_resp_accounts(fset_id):
    q = db.auth_user.id == db.auth_membership.user_id
    q &= db.auth_group.id == db.auth_membership.group_id
    q &= db.services.svc_app == db.apps.app
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    uids = set([row.id for row in db(q).select(db.auth_user.id, groupby=db.auth_user.id)])

    q = db.auth_user.id == db.auth_membership.user_id
    q &= db.auth_group.id == db.auth_membership.group_id
    q &= db.auth_group.role == db.nodes.team_responsible
    q = apply_filters(q, db.nodes.nodename, None, fset_id)
    uids |= set([row.id for row in db(q).select(db.auth_user.id, groupby=db.auth_user.id)])

    n = len(uids)
    print "stat_nb_resp_accounts():", str(n)
    return n

def stat_disk_size(fset_id):
    q = db.svcdisks.id > 0
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname, fset_id)
    rows = db(q).select(groupby=db.svcdisks.id)
    s = 0
    for row in rows:
        if row.disk_size is None:
            continue
        s += row.disk_size
    print "stat_disk_size():", str(s)
    return s

def _cron_stat_day(end, fset_id=None):
    q = db.stat_day.day == end
    if fset_id is None:
        q &= db.stat_day.fset_id == 0
    else:
        q &= db.stat_day.fset_id == fset_id
    print "stat_day:", end, "fset_id:", fset_id if fset_id is not None else 0
    if db(q).count() == 0:
        db.stat_day.insert(
          day=end,
          fset_id=fset_id if fset_id is not None else 0,
          nb_svc=stat_nb_svc(fset_id),
          nb_action=stat_nb_action(fset_id),
          nb_action_err=stat_nb_action_err(fset_id),
          nb_action_warn=stat_nb_action_warn(fset_id),
          nb_action_ok=stat_nb_action_ok(fset_id),
          nb_apps=stat_nb_apps(fset_id),
          nb_accounts=stat_nb_accounts(fset_id),
          nb_resp_accounts=stat_nb_resp_accounts(fset_id),
          nb_svc_with_drp=stat_nb_svc_with_drp(fset_id),
          nb_svc_prd=stat_nb_svc_prd(fset_id),
          nb_vcpu=stat_nb_vcpu(fset_id),
          nb_vmem=stat_nb_vmem(fset_id),
          nb_svc_cluster=stat_nb_svc_cluster(fset_id),
          nb_nodes=stat_nb_nodes(fset_id),
          nb_nodes_prd=stat_nb_nodes_prd(fset_id),
          disk_size=stat_disk_size(fset_id),
          nb_cpu_core=stat_nb_core(fset_id),
          ram_size=stat_nb_mem(fset_id),
        )
    else:
        db(q).update(
          day=end,
          fset_id=fset_id if fset_id is not None else 0,
          nb_svc=stat_nb_svc(fset_id),
          nb_action=stat_nb_action(fset_id),
          nb_action_err=stat_nb_action_err(fset_id),
          nb_action_warn=stat_nb_action_warn(fset_id),
          nb_action_ok=stat_nb_action_ok(fset_id),
          nb_apps=stat_nb_apps(fset_id),
          nb_accounts=stat_nb_accounts(fset_id),
          nb_resp_accounts=stat_nb_resp_accounts(fset_id),
          nb_svc_with_drp=stat_nb_svc_with_drp(fset_id),
          nb_svc_prd=stat_nb_svc_prd(fset_id),
          nb_vcpu=stat_nb_vcpu(fset_id),
          nb_vmem=stat_nb_vmem(fset_id),
          nb_svc_cluster=stat_nb_svc_cluster(fset_id),
          nb_nodes=stat_nb_nodes(fset_id),
          nb_nodes_prd=stat_nb_nodes_prd(fset_id),
          disk_size=stat_disk_size(fset_id),
          nb_cpu_core=stat_nb_core(fset_id),
          ram_size=stat_nb_mem(fset_id),
        )
    db.commit()

    # os lifecycle
    print "os lifecycle: %s, fset_id: %d"%(end, fset_id if fset_id is not None else 0)
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id)
    nodes = ','.join([repr(r.nodename) for r in db(q).select()])
    if len(nodes) >0:
        where_nodes = "where nodename in (%s)"%nodes
    else:
        where_nodes = ""

    sql2 = """replace into lifecycle_os
              (fset_id, lc_os_concat, lc_count, lc_date, lc_os_name, lc_os_vendor)
              select %d,
                     concat_ws(' ', os_name, os_vendor, os_release, os_arch) c,
                     count(nodename),CURDATE(), os_name, os_vendor
              from nodes %s group by c;"""%(fset_id if fset_id is not None else 0, where_nodes)
    db.executesql(sql2)
    db.commit()

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
    db.commit()
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
                      md5(concat("service.config.notupdated",svc_name,updated)),
                      "warning"
               from services
               where updated<date_sub(now(), interval %(age)d day);"""%dict(age=age)
    return db.executesql(sql)
    db.commit()

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
    db.commit()

def refresh_dash_action_errors():
    sql = """delete from dashboard
             where
               dash_type like "%action err%" and
               (dash_svcname, dash_nodename) not in (
                 select nodename, svcname
                 from b_action_errors
               )"""
    db.executesql(sql)
    db.commit()

def update_dash_action_errors(svc_name, nodename):
    svc_name = svc_name.strip("'")
    nodename = nodename.strip("'")
    sql = """select e.err, s.svc_type from b_action_errors e
             join services s on e.svcname=s.svc_name
             where
               svcname="%(svcname)s" and
               nodename="%(nodename)s"
          """%dict(svcname=svc_name, nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1:
        if rows[0][1] == 'PRD':
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created=now()
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created=now()
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                       err=rows[0][0])
    else:
        sql = """delete from dashboard
                 where
                   dash_type="action errors" and
                   dash_svcname="%(svcname)s" and
                   dash_nodename="%(nodename)s"
              """%dict(svcname=svc_name,
                       nodename=nodename)
    db.executesql(sql)
    db.commit()

def alerts_failed_actions_not_acked():
    """ Actions not ackowleged : Alert responsibles & Acknowledge
        This function is meant to be scheduled daily, at night,
        and alerts generated should be sent as soon as possible.
    """
    age = 1
    sql = """select id, svcname, hostname from SVCactions where
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
    db.commit()

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
    db.commit()

    """ Update dashboard
    """
    for row in rows:
        update_dash_action_errors(row[1], row[2])

    return ids

def cron_alerts_daily():
    alerts_apps_without_responsible()
    alerts_services_not_updated()
    alerts_failed_actions_not_acked()
    refresh_b_action_errors()
    refresh_dash_action_errors()

def cron_alerts_hourly():
    rets = []
    rets.append(alerts_svcmon_not_updated())
    return rets

