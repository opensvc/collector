def refresh_b_action_errors():
    sql = """truncate b_action_errors;"""
    db.executesql(sql)
    db.commit()
    sql = """insert into b_action_errors
               select NULL, m.mon_svcname, m.mon_nodname, count(a.id)
               from svcmon m
                 left join SVCactions a
                 on m.mon_svcname=a.svcname and m.mon_nodname=a.hostname
               where
                 a.status='err'
                 and (a.ack=0 or isnull(a.ack))
                 and a.end is not NULL
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
  `app` varchar(64),
  `roles` varchar(342) DEFAULT NULL,
  `responsibles` varchar(342) DEFAULT NULL,
  `mailto` varchar(342) DEFAULT NULL,
  KEY `i_app` (`app`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
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

def _cron_stats_purge(table, day):
    sql = """select date from stats_%(table)s order by date limit 1""" % dict(table=table)
    oldest = db.executesql(sql)[0][0]
    if oldest > day:
        print "oldest entry is dated %s, threshold is set to %s ... skip table %s purge"%(str(oldest), str(day), table)
        return
    delta = day - oldest
    print "%d days to purge in table %s" % (delta.days, table)
    for i in range(delta.days):
        _day = oldest + datetime.timedelta(days=i)
        print " purge table %s till %s" % (table, str(_day))
        sql = """delete from stats_%s where date < "%s" """%(table, str(_day))
        db.executesql(sql)
    db.commit()

def cron_stats_purge():
    try:
        config = local_import('config', reload=True)
        days = config.stats_retention_days
    except:
        days = 365
    day = now - datetime.timedelta(days=days)

    tables = ['cpu',
              'swap',
              'netdev',
              'blockdev',
              'block',
              'mem_u',
              'netdev_err',
              'proc',
              'svc']
    for table in tables:
        try:
            _cron_stats_purge(table, day)
        except Exception as e:
            print e

def cron_stats():
    # refresh db tables
    try:
        cron_stats_purge()
    except:
        pass
    try:
        cron_stat_day()
    except:
        pass
    try:
        cron_stat_day_svc()
    except:
        pass
    try:
        cron_stat_day_disk()
    except:
        pass

def cron_stat_day_disk():
    cron_stat_day_disk_app()
    cron_stat_day_disk_app_dg()
    cron_stat_day_disk_array()
    cron_stat_day_disk_array_dg()

def cron_stat_day_disk_app():
    sql = """insert into stat_day_disk_app
             select
               NULL,
               NOW(),
               app,
               sum(quota_used) as quota_used,
               sum(quota) as quota
             from v_disk_quota
             group by app;
          """
    rows = db.executesql(sql)
    print "cron_stat_day_disk_app", str(rows)

def cron_stat_day_disk_app_dg():
    sql = """insert into stat_day_disk_app_dg
             select
               NULL,
               NOW(),
               dg.id,
               t.app,
               t.disk_used,
               dgq.quota
             from v_disks_app t
             join apps ap on ap.app=t.app
             join stor_array ar on ar.array_name=t.disk_arrayid
             join stor_array_dg dg on ar.id=dg.array_id and dg.dg_name=t.disk_group
             left join stor_array_dg_quota dgq on ap.id=dgq.app_id and dg.id=dgq.dg_id
          """
    rows = db.executesql(sql)
    print "cron_stat_day_disk_app_dg", str(rows)

def cron_stat_day_disk_array():
    sql = """insert into stat_day_disk_array
             select
               NULL,
               NOW(),
               t.array_name,
               sum(t.dg_used),
               sum(t.dg_size),
               sum(t.dg_reserved),
               sum(t.dg_reservable)
             from (
               select
                 array_name,
                 dg_used,
                 dg_size,
                 dg_reserved,
                 dg_reservable
               from
                 v_disk_quota
               group by
                 array_name, dg_name
             ) t
             group by
               t.array_name
          """
    rows = db.executesql(sql)
    print "cron_stat_day_disk_array", str(rows)

def cron_stat_day_disk_array_dg():
    sql = """insert into stat_day_disk_array_dg
             select
               NULL,
               NOW(),
               array_name,
               dg_name,
               dg_used,
               dg_size,
               dg_reserved,
               dg_reservable
             from
               v_disk_quota
             group by
               array_name, dg_name
           """
    rows = db.executesql(sql)
    print "cron_stat_day_disk_array_dg", str(rows)

def cron_stat_day():
    # global stats

    #when = datetime.datetime.now()-datetime.timedelta(days=14)
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    _cron_stat_day(end)
    _cron_stat_day_billing(end)

    # per filterset stats
    rows = db(db.gen_filtersets.id>0).select(db.gen_filtersets.id)
    for row in rows:
        _cron_stat_day(end, row.id)
        _cron_stat_day_billing(end, row.id)

def stat_nb_nodes(fset_id):
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id)
    n = db(q).count()
    print "stat_nb_nodes():", str(n)
    return n

def stat_nb_nodes_prd(fset_id):
    q = db.nodes.host_mode.like("%pr%")
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
    q = db.svcmon.id < 0
    q = or_apply_filters(q, None, db.svcmon.mon_svcname, fset_id)
    rows = db(q).select(db.svcmon.mon_vcpus, groupby=db.svcmon.mon_vmname)
    n = 0
    for row in rows:
        n += row.mon_vcpus
    print "stat_nb_vcpu():", str(n)
    return n

def stat_nb_vmem(fset_id):
    q = db.svcmon.id < 0
    q = or_apply_filters(q, None, db.svcmon.mon_svcname, fset_id)
    rows = db(q).select(db.svcmon.mon_vmem, groupby=db.svcmon.mon_vmname)
    n = 0
    for row in rows:
        n += row.mon_vmem
    print "stat_nb_vmem():", str(n)
    return n

def stat_nb_core(fset_id):
    q = ~db.nodes.nodename.belongs(db(db.services.id > 0).select(db.services.svc_name))
    q &= ~db.nodes.model.like("%virtuel%")
    q &= ~db.nodes.model.like("%VMware%")
    q &= ~db.nodes.model.like("%KVM%")
    q &= ~db.nodes.model.like("%QEMU%")
    q = apply_filters(q, db.nodes.nodename, None, fset_id)
    rows = db(q).select(db.nodes.cpu_cores)
    n = 0
    for row in rows:
        n += row.cpu_cores
    print "stat_nb_cores():", str(n)
    return n

def stat_nb_mem(fset_id):
    q = ~db.nodes.nodename.belongs(db(db.services.id > 0).select(db.services.svc_name))
    q &= ~db.nodes.model.like("%virtuel%")
    q &= ~db.nodes.model.like("%VMware%")
    q &= ~db.nodes.model.like("%KVM%")
    q &= ~db.nodes.model.like("%QEMU%")
    q = apply_filters(q, db.nodes.nodename, None, fset_id)
    rows = db(q).select(db.nodes.mem_bytes)
    n = 0
    for row in rows:
        n += row.mem_bytes
    # convert to GB
    n = n / 1024
    print "stat_nb_mem():", str(n)
    return n

def stat_nb_virt_nodes(fset_id):
    q = db.nodes.nodename.belongs(db(db.services.id > 0).select(db.services.svc_name))
    q |= db.nodes.model.like("%virtuel%")
    q |= db.nodes.model.like("%VMware%")
    q |= db.nodes.model.like("%KVM%")
    q |= db.nodes.model.like("%QEMU%")
    q = apply_filters(q, db.nodes.nodename, None, fset_id)
    n = db(q).count()
    print "stat_nb_virt_nodes():", str(n)
    return n

def stat_nb_svc_with_drp(fset_id):
    q = db.services.svc_drpnodes != None
    q &= db.services.svc_drpnodes != ""
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_nb_svc_with_drp():", str(n)
    return n

def stat_billing_nb_svc_prd(fset_id, os):
    q = db.services.svc_type == "PRD"
    q &= db.services.svc_name == db.svcmon.mon_svcname
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    q &= db.nodes.os_name == os
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_billing_nb_svc_prd():", str(n)
    return n

def stat_billing_nb_svc_nonprd(fset_id, os):
    q = db.services.svc_type != "PRD"
    q &= db.services.svc_name == db.svcmon.mon_svcname
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    q &= db.nodes.os_name == os
    q = apply_filters(q, None, db.services.svc_name, fset_id)
    n = db(q).count()
    print "stat_billing_nb_svc_nonprd():", str(n)
    return n

def stat_billing_nb_agents_without_svc_prd(fset_id, os):
    n = 0
    print "stat_billing_nb_agents_without_svc_prd():", str(n)
    return n

def stat_billing_nb_agents_without_svc_nonprd(fset_id, os):
    n = 0
    print "stat_billing_nb_agents_without_svc_nonprd():", str(n)
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
    q = apply_filters(q, db.SVCactions.hostname, None, fset_id)
    n = db(q).count()
    print "stat_nb_action():", str(n)
    return n

def stat_nb_action_err(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "err"
    q = apply_filters(q, db.SVCactions.hostname, None, fset_id)
    n = db(q).count()
    print "stat_nb_action_err():", str(n)
    return n

def stat_nb_action_warn(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "warn"
    q = apply_filters(q, db.SVCactions.hostname, None, fset_id)
    n = db(q).count()
    print "stat_nb_action_warn():", str(n)
    return n

def stat_nb_action_ok(fset_id):
    q = db.SVCactions.begin > yesterday
    q &= db.SVCactions.end < today
    q &= db.SVCactions.status == "ok"
    q = apply_filters(q, db.SVCactions.hostname, None, fset_id)
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
    q = db.svcdisks.disk_local == False
    q = apply_filters(q, db.svcdisks.disk_nodename, None, fset_id)
    rows = db(q).select(groupby=db.svcdisks.disk_id)
    s = 0
    for row in rows:
        if row.disk_size is None:
            continue
        s += row.disk_size
    print "stat_disk_size():", str(s)
    return s

def stat_local_disk_size(fset_id):
    q = db.svcdisks.disk_local == True
    q = apply_filters(q, db.svcdisks.disk_nodename, None, fset_id)
    rows = db(q).select(groupby=db.svcdisks.disk_id)
    s = 0
    for row in rows:
        if row.disk_size is None:
            continue
        s += row.disk_size
    print "stat_local_disk_size():", str(s)
    return s

def _cron_stat_day(end, fset_id=0):
    q = db.stat_day.day == end
    q &= db.stat_day.fset_id == fset_id
    print "stat_day:", end, "fset_id:", fset_id
    if db(q).count() == 0:
        db.stat_day.insert(
          day=end,
          fset_id=fset_id,
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
          nb_virt_nodes=stat_nb_virt_nodes(fset_id),
          nb_nodes_prd=stat_nb_nodes_prd(fset_id),
          disk_size=stat_disk_size(fset_id),
          nb_cpu_core=stat_nb_core(fset_id),
          ram_size=stat_nb_mem(fset_id),
          local_disk_size=stat_local_disk_size(fset_id),
        )
    else:
        db(q).update(
          day=end,
          fset_id=fset_id,
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
          nb_virt_nodes=stat_nb_virt_nodes(fset_id),
          nb_nodes=stat_nb_nodes(fset_id),
          nb_nodes_prd=stat_nb_nodes_prd(fset_id),
          disk_size=stat_disk_size(fset_id),
          nb_cpu_core=stat_nb_core(fset_id),
          ram_size=stat_nb_mem(fset_id),
          local_disk_size=stat_local_disk_size(fset_id),
        )
    db.commit()

    # os lifecycle
    print "os lifecycle: %s, fset_id: %d"%(end, fset_id)
    q = db.nodes.id < 0
    q = or_apply_filters(q, db.nodes.nodename, None, fset_id if fset_id != 0 else None)
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
              from nodes %s group by c;"""%(fset_id, where_nodes)
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
        pairs += ["disk_size=(select if(sum(t.disk_size) is NULL, 0, sum(t.disk_size)) from (select distinct s.disk_id, s.disk_size from svcdisks s where s.disk_svcname='%s' and s.disk_local='F') t)"%svc]
        pairs += ["local_disk_size=(select if(sum(t.disk_size) is NULL, 0, sum(t.disk_size)) from (select distinct s.disk_id, s.disk_size from svcdisks s where s.disk_svcname='%s' and s.disk_local='T') t)"%svc]
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
    apps = [r.app for r in rows]

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
                      md5(concat("service.status.notupdated",mon_nodname,mon_svcname,mon_updated)),
                      "warning"
               from svcmon
               where mon_updated<date_sub(now(), interval %(age)d hour);"""%dict(age=age)
    n = db.executesql(sql)
    db.commit()
    return n

def refresh_dash_action_errors():
    sql = """delete from dashboard
             where
               dash_type like "%action err%" and
               (dash_svcname, dash_nodename) not in (
                 select svcname, nodename
                 from b_action_errors
               )"""
    db.executesql(sql)
    db.commit()

def update_dash_action_errors():
    sql = """select
               e.err,
               s.svc_type,
               e.svcname,
               e.nodename,
               s.svc_type
             from
               b_action_errors e
             join services s on e.svcname=s.svc_name
          """
    rows = db.executesql(sql)

    for row in rows:
        if row[1] == 'PRD':
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
                   dash_created=now(),
                   dash_env="%(env)s",
                   dash_updated=now()
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_updated=now()
              """%dict(svcname=row[2],
                       nodename=row[3],
                       sev=sev,
                       env=row[4],
                       err=row[0])
        db.executesql(sql)
        db.commit()

    refresh_dash_action_errors()

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
    update_dash_action_errors()

    return ids

def purge_svcdisks():
    sql = """delete from svcdisks where disk_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def purge_diskinfo():
    sql = """delete from diskinfo where disk_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def purge_stor_array():
    sql = """delete from stor_array where array_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def update_dg_quota():
    sql = """insert ignore into stor_array_dg_quota
             select NULL, dg.id, ap.id, NULL
             from
               v_disks_app v
               join stor_array ar on (v.disk_arrayid=ar.array_name)
               join stor_array_dg dg on (v.disk_group=dg.dg_name and dg.array_id=ar.id)
               join apps ap on v.app=ap.app
          """
    db.executesql(sql)
    db.commit()

def purge_alerts_on_nodes_without_asset():
    l = db.nodes.on(db.dashboard.dash_nodename==db.nodes.nodename)
    q = db.dashboard.dash_type == "node information not updated"
    q &= db.nodes.nodename == None
    ids = map(lambda x: x.id, db(q).select(db.dashboard.id, left=l))
    if len(ids) > 0:
        q = db.dashboard.id.belongs(ids)
        db(q).delete()
        db.commit()

    l = db.svcmon.on(db.dashboard.dash_nodename==db.svcmon.mon_nodname)
    q = db.dashboard.dash_type == "node without asset information"
    q &= db.svcmon.mon_nodname == None
    ids = map(lambda x: x.id, db(q).select(db.dashboard.id, left=l))
    if len(ids) > 0:
        q = db.dashboard.id.belongs(ids)
        db(q).delete()
        db.commit()

def cron_alerts_daily():
    alerts_apps_without_responsible()
    alerts_services_not_updated()
    alerts_failed_actions_not_acked()
    refresh_b_action_errors()
    refresh_dash_action_errors()
    purge_svcdisks()
    purge_diskinfo()
    purge_stor_array()
    update_dg_quota()
    purge_alerts_on_nodes_without_asset()
    cron_resmon_purge()

def cron_alerts_hourly():
    rets = []
    rets.append(alerts_svcmon_not_updated())
    return rets

def cron_resmon_purge():
    sql = """delete from resmon where
              updated < date_sub(now(), interval 1 day)"""
    db.executesql(sql)
    db.commit()

def cron_feed_monitor():
    e = db(db.feed_queue.id>0).select(limitby=(0,1)).first()
    if e is None:
        # clean all
        sql = """delete from dashboard
                 where
                   dash_type = "feed queue"
              """
        db.executesql(sql)
        db.commit()
        return

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    limit = now - datetime.timedelta(minutes=5)
    if e.created < limit:
        n = db(db.feed_queue.created<limit).count()
        sql = """insert into dashboard
                 set
                   dash_type="feed queue",
                   dash_severity=4,
                   dash_fmt="%%(n)s entries stalled in feed queue",
                   dash_dict='{"n": "%(n)d"}',
                   dash_created="%(now)s",
                   dash_env="PRD",
                   dash_updated="%(now)s"
                 on duplicate key update
                   dash_fmt="%%(n)s entries stalled in feed queue",
                   dash_dict='{"n": "%(n)d"}',
                   dash_updated="%(now)s"
              """%dict(n=n, now=str(now))
        db.executesql(sql)
    db.commit()

    # clean old
    sql = """delete from dashboard
             where
               dash_type = "feed queue" and
               dash_updated < "%(now)s" """%dict(now=str(now))
    db.executesql(sql)


def _cron_stat_day_billing(end, fset_id=0):
    q = db.stat_day_billing.day == end
    q &= db.stat_day_billing.fset_id == fset_id
    print "stat_day_billing:", end, "fset_id:", fset_id
    for os in [r.os_name for r in db(db.nodes.id>0).select(db.nodes.os_name, groupby=db.nodes.os_name)]:
        if len(os) == 0:
            continue
        qq = q & (db.stat_day_billing.os_name == os)
        if db(qq).count() == 0:
            db.stat_day_billing.insert(
              day=end,
              fset_id=fset_id,
              os_name=os,
              nb_svc_prd=stat_billing_nb_svc_prd(fset_id, os),
              nb_svc_nonprd=stat_billing_nb_svc_nonprd(fset_id, os),
              nb_agents_without_svc_prd=stat_billing_nb_agents_without_svc_prd(fset_id, os),
              nb_agents_without_svc_nonprd=stat_billing_nb_agents_without_svc_nonprd(fset_id, os),
            )
        else:
            db(qq).update(
              day=end,
              fset_id=fset_id,
              os_name=os,
              nb_svc_prd=stat_billing_nb_svc_prd(fset_id, os),
              nb_svc_nonprd=stat_billing_nb_svc_nonprd(fset_id, os),
              nb_agents_without_svc_prd=stat_billing_nb_agents_without_svc_prd(fset_id, os),
              nb_agents_without_svc_nonprd=stat_billing_nb_agents_without_svc_nonprd(fset_id, os),
            )
    db.commit()

def cron_update_virtual_asset():
    fields = ['loc_addr', 'loc_city', 'loc_zip', 'loc_room', 'loc_building',
              'loc_floor', 'loc_rack', 'power_cabinet1', 'power_cabinet2',
              'power_supply_nb', 'power_protect', 'power_protect_breaker',
              'power_breaker1', 'power_breaker2', 'loc_country', 'enclosure']
    sql = """
      update svcmon m, nodes n, nodes n2
      set
       n2.loc_addr=n.loc_addr,
       n2.loc_city=n.loc_city,
       n2.loc_zip=n.loc_zip,
       n2.loc_room=n.loc_room,
       n2.loc_building=n.loc_building,
       n2.loc_floor=n.loc_floor,
       n2.loc_rack=n.loc_rack,
       n2.loc_country=n.loc_country,
       n2.power_cabinet1=n.power_cabinet1,
       n2.power_cabinet2=n.power_cabinet2,
       n2.power_supply_nb=n.power_supply_nb,
       n2.power_protect=n.power_protect,
       n2.power_protect_breaker=n.power_protect_breaker,
       n2.power_breaker1=n.power_breaker1,
       n2.power_breaker2=n.power_breaker2,
       n2.enclosure=n.enclosure
      where
       m.mon_nodname=n.nodename and
       m.mon_vmname=n2.nodename and
       m.mon_vmtype in ('ldom', 'hpvm', 'kvm', 'xen', 'vbox', 'ovm', 'esx', 'zone', 'lxc', 'jail', 'vz', 'srp') and
       m.mon_containerstatus in ("up", "stdby up", "warn")
    """
    db.executesql(sql)

