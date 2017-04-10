def refresh_b_action_errors():
    sql = """truncate b_action_errors"""
    db.executesql(sql)
    db.commit()
    sql = """insert into b_action_errors
               select NULL, m.svc_id, m.node_id, count(a.id)
               from svcmon m
                 left join svcactions a
                 on m.svc_id=a.svc_id and m.node_id=a.node_id
               where
                 a.status='err'
                 and (a.ack=0 or isnull(a.ack))
                 and a.end is not NULL
               group by m.svc_id, m.node_id
          """
    db.executesql(sql)
    db.commit()

def cron_scrub():
    cron_scrub_svcstatus()
    cron_scrub_resstatus()

def cron_scrub_svcstatus():
    """ Mark undef the services with 0 instance updating their status
    """
    q = db.v_outdated_services.uptodate == 0
    svc_ids = [r.svc_id for r in db(q).select(db.v_outdated_services.svc_id)]
    q = db.services.svc_id.belongs(svc_ids)
    if len(svc_ids) > 0:
        q &= (db.services.svc_status != 'undef') | (db.services.svc_availstatus != 'undef')
        svc_ids_new = [r.svc_id for r in db(q).select(db.services.svc_id)]
        db(q).update(svc_status="undef", svc_availstatus="undef")
        for svc_id in svc_ids_new:
            _log("service.status",
                 "service '%(svc)s' has zero live instance. Status flagged 'undef'",
                 dict(svc=get_svcname(svc_id)),
                 user="scheduler",
                 svc_id=svc_id,
                 level="error")
    for svc_id in svc_ids:
        svc_log_update(svc_id, "undef")

def cron_scrub_resstatus():
    limit = datetime.datetime.now() - datetime.timedelta(minutes=15)
    q = db.resmon.updated < limit
    rows = db(q).select(db.resmon.node_id, db.resmon.svc_id, db.resmon.rid)
    for row in rows:
        resmon_log_update(row.node_id, row.svc_id, row.rid, "undef")

def cron_scrub_checks():
    thres = now - datetime.timedelta(days=2)
    q = db.checks_live.chk_updated < thres
    return db(q).delete()


def cron_purge_node_hba():
    sql = """delete from node_hba where updated < date_sub(now(), interval 1 week)"""
    db.executesql(sql)
    db.commit()

def _cron_table_purge(table, date_col, orderby=None):
    days = 365
    try:
        config = local_import('config', reload=True)
        try:
            days = config.stats_retention_days
        except:
            pass
        if table in config.retentions:
            days = config.retentions[table]
    except Exception as e:
        print e, "defaulting to", days
    day = now - datetime.timedelta(days=days)

    # sanity purge (entries dated in the future)
    sql = """delete from %(table)s where
               %(date_col)s > now()
          """ % dict(table=table,date_col=date_col)
    n = db.executesql(sql)

    if orderby is None:
        orderby = date_col

    if table == "dashboard_events":
        where = " and not dash_end is NULL"
    else:
        where = ""

    sql = """select %(date_col)s from %(table)s where
               %(date_col)s is not null and
               %(date_col)s > 0
               %(where)s
             order by %(orderby)s limit 1
          """ % dict(table=table,date_col=date_col,orderby=orderby,where=where)
    try:
        oldest = db.executesql(sql)[0][0]
    except:
        print "no data in table %s" % table
        return

    if type(oldest) == datetime.date:
        oldest = datetime.datetime.combine(oldest, datetime.datetime.min.time())

    if oldest > day:
        print "oldest entry is dated %s, threshold is set to %s ... skip table %s purge"%(str(oldest), str(day), table)
        return
    delta = day - oldest
    print "%d days to purge in table %s" % (delta.days, table)
    import time
    for i in range(delta.days):
        _day = oldest + datetime.timedelta(days=i)
        count = 0
        while True:
            print " purge table %s till %s (%d)" % (table, str(_day), count)
            sql = """delete from %(table)s where
                           %(date_col)s is not null and
                       %(date_col)s > 0 and
                       %(date_col)s < "%(threshold)s"
                       %(where)s
                       limit 1000
                  """ % dict(
                    table=table,
                    where=where,
                    date_col=date_col,
                    threshold=str(_day)
                  )
            db.executesql(sql)
            sql = """select row_count()"""
            rows = db.executesql(sql)
            db.commit()
            count += rows[0][0]
            if rows[0][0] == 0:
                break
            time.sleep(0.1)
    db.commit()

def cron_purge_expiry():
    tables = [('saves', 'save_date', None),
              ('log', 'log_date', None),
              ('stats_cpu', 'date', None),
              ('stats_fs_u', 'date', None),
              ('stats_swap', 'date', None),
              ('stats_netdev', 'date', None),
              ('stats_blockdev', 'date', None),
              ('stats_block', 'date', None),
              ('stats_mem_u', 'date', None),
              ('stats_netdev_err', 'date', None),
              ('stats_proc', 'date', None),
              ('stats_svc', 'date', None),
              ('stats_cpu_hour', 'date', None),
              ('stats_fs_u_hour', 'date', None),
              ('stats_swap_hour', 'date', None),
              ('stats_netdev_hour', 'date', None),
              ('stats_blockdev_hour', 'date', None),
              ('stats_block_hour', 'date', None),
              ('stats_mem_u_hour', 'date', None),
              ('stats_netdev_err_hour', 'date', None),
              ('stats_proc_hour', 'date', None),
              ('stats_svc_hour', 'date', None),
              ('stats_cpu_day', 'date', None),
              ('stats_fs_u_day', 'date', None),
              ('stats_swap_day', 'date', None),
              ('stats_netdev_day', 'date', None),
              ('stats_blockdev_day', 'date', None),
              ('stats_block_day', 'date', None),
              ('stats_mem_u_day', 'date', None),
              ('stats_netdev_err_day', 'date', None),
              ('stats_proc_day', 'date', None),
              ('stats_svc_day', 'date', None),
              ('stat_day_disk_array', 'day', None),
              ('stat_day_disk_array_dg', 'day', None),
              ('stat_day_disk_app', 'day', None),
              ('stat_day_disk_app_dg', 'day', None),
              ('metrics_log', 'date', None),
              ('switches', 'sw_updated', None),
              ('comp_log', 'run_date', None),
              ('comp_log_daily', 'run_date', None),
              ('svcmon_log', 'mon_end', None),
              ('services_log', 'svc_end', None),
              ('resmon_log', 'res_end', None),
              ('resinfo_log', 'updated', None),
              ('svcactions', 'begin', 'id'),
              ('dashboard_events', 'dash_end', None),
              ('packages', 'pkg_updated', None),
              ('patches', 'patch_updated', None),
              ('node_ip', 'updated', None),
              ('node_users', 'updated', None),
              ('node_groups', 'updated', None),
              ('links','link_last_consultation_date',None)]
    for table, date_col, orderby in tables:
        try:
            _cron_table_purge(table, date_col, orderby=orderby)
        except Exception as e:
            print e

def cron_stats():
    # refresh db tables
    try:
        cron_purge_expiry()
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
    except Exception as e:
        print(e)
        pass
    db.commit()

def cron_stat_day_disk():
    cron_stat_day_disk_app()
    cron_stat_day_disk_app_dg()
    cron_stat_day_disk_array()
    cron_stat_day_disk_array_dg()
    db.commit()

def cron_stat_day_disk_app():
    sql = """insert ignore into stat_day_disk_app
             select
               NULL,
               NOW(),
               app,
               sum(quota_used) as quota_used,
               sum(quota) as quota
             from v_disk_quota
             group by app
          """
    rows = db.executesql(sql)
    db.commit()
    print "cron_stat_day_disk_app", str(rows)

def cron_stat_day_disk_app_dg():
    sql = """insert ignore into stat_day_disk_app_dg
             select
               NULL,
               NOW(),
               dg.id,
               ap.app,
               sd.disk_used,
               dgq.quota
             from diskinfo di
             join svcdisks sd on di.disk_id=sd.disk_id
             join apps ap on ap.id=sd.app_id
             join stor_array ar on ar.array_name=di.disk_arrayid
             join stor_array_dg dg on ar.id=dg.array_id and dg.dg_name=di.disk_group
             left join stor_array_dg_quota dgq on ap.id=dgq.app_id and dg.id=dgq.dg_id
          """
    rows = db.executesql(sql)
    db.commit()
    print "cron_stat_day_disk_app_dg", str(rows)

def cron_stat_day_disk_array():
    sql = """insert ignore into stat_day_disk_array
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
    db.commit()
    print "cron_stat_day_disk_array", str(rows)

def cron_stat_day_disk_array_dg():
    sql = """insert ignore into stat_day_disk_array_dg
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
    db.commit()
    print "cron_stat_day_disk_array_dg", str(rows)

def cron_stat_day():
    # global stats

    #when = datetime.datetime.now()-datetime.timedelta(days=14)
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    _cron_stat_day_billing(end)

    # per filterset stats
    q = db.gen_filtersets.id > 0
    q &= db.gen_filtersets.fset_stats == True
    rows = db(q).select(db.gen_filtersets.id)
    for row in rows:
        _cron_stat_day_billing(end, row.id)

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

def cron_stat_day_svc():
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)
    day_s = begin.strftime("%Y-%m-%d")

    sql = """insert ignore into stat_day_svc (svc_id, day, nb_action_err) select a.svc_id, "%(day)s", count(a.id) from svcactions a where a.begin>'%(begin)s' and a.begin<'%(end)s' and a.status='err' group by a.svc_id on duplicate key update nb_action_err=values(nb_action_err)""" % dict(day=day_s, begin=str(begin), end=str(end))
    print sql
    db.executesql(sql)
    db.commit()

    sql = """insert ignore into stat_day_svc (svc_id, day, nb_action_warn) select a.svc_id, "%(day)s", count(a.id) from svcactions a where a.begin>'%(begin)s' and a.begin<'%(end)s' and a.status='warn' group by a.svc_id on duplicate key update nb_action_warn=values(nb_action_warn)""" % dict(day=day_s, begin=str(begin), end=str(end))
    print sql
    db.executesql(sql)
    db.commit()

    sql = """insert ignore into stat_day_svc (svc_id, day, nb_action_ok) select a.svc_id, "%(day)s", count(a.id) from svcactions a where a.begin>'%(begin)s' and a.begin<'%(end)s' and a.status='ok' group by a.svc_id on duplicate key update nb_action_ok=values(nb_action_ok)""" % dict(day=day_s, begin=str(begin), end=str(end))
    print sql
    db.executesql(sql)
    db.commit()

    sql = """insert ignore into stat_day_svc (svc_id, day, nb_action) select a.svc_id, "%(day)s", count(a.id) from svcactions a where a.begin>'%(begin)s' and a.begin<'%(end)s' group by a.svc_id on duplicate key update nb_action=values(nb_action)""" % dict(day=day_s, begin=str(begin), end=str(end))
    print sql
    db.executesql(sql)
    db.commit()

    sql = """insert ignore into stat_day_svc (svc_id, day, disk_size) select d.svc_id, "%(day)s", if(sum(d.disk_size) is NULL, 0, sum(d.disk_size)) from svcdisks d where d.disk_local='F' group by d.svc_id on duplicate key update disk_size=values(disk_size)""" % dict(day=day_s)
    print sql
    db.executesql(sql)
    db.commit()

    sql = """insert ignore into stat_day_svc (svc_id, day, local_disk_size) select d.svc_id, "%(day)s", if(sum(d.disk_size) is NULL, 0, sum(d.disk_size)) from svcdisks d where d.disk_local='T' group by d.svc_id on duplicate key update local_disk_size=values(local_disk_size)""" % dict(day=day_s)
    print sql
    db.executesql(sql)
    db.commit()



#
# Misc
#
#######
def cron_unfinished_actions():
    return task_unfinished_actions()

#
# Alerts and purges
#
####################

def alert_wrong_netmask():
    sql = """select
               node_id,
               node_env,
               addr,
               mask,
               net_netmask,
               net_name
             from v_nodenetworks
             where
               mask<net_netmask and
               mask!="" and
               addr_updated>date_sub(now(), interval 2 day)
          """
    rows = db.executesql(sql, as_dict=True)

    for row in rows:
        if row.get('node_env') == 'PRD':
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="netmask misconfigured",
                   svc_id="",
                   node_id="%(node_id)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(addr)s configured with mask %%(mask)s instead of %%(net_netmask)s",
                   dash_dict='{"addr": "%(addr)s", "mask": "%(mask)s", "net_netmask": "%(net_netmask)s"}',
                   dash_created=now(),
                   dash_env="%(env)s",
                   dash_updated=now()
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(addr)s configured with mask %%(mask)s instead of %%(net_netmask)s",
                   dash_dict='{"addr": "%(addr)s", "mask": "%(mask)s", "net_netmask": "%(net_netmask)s"}',
                   dash_updated=now()
              """%dict(
                       node_id=row.get('node_id', ''),
                       mask=str(row.get('mask', '')),
                       net_netmask=str(row.get('net_netmask', '')),
                       sev=sev,
                       env=row.get('node_env', ''),
                       addr=row.get('addr', ''))
        db.executesql(sql)
        db.commit()

    sql = """delete from dashboard
             where
               dash_type="netmask misconfigured" and
               dash_updated < date_sub(now(), interval 1 minute)
          """
    db.executesql(sql)
    db.commit()

def alerts_apps_without_responsible():
    q = db.apps.id > 0
    q = db.apps_responsibles.group_id == None
    l = db.apps_responsibles.on(db.apps.id==db.apps_responsibles.app_id)
    rows = db(q).select(db.apps.app, left=l)
    apps = [r.app for r in rows]

    if len(apps) == 0:
        return

    _log("app",
         "applications with no declared responsibles %(app)s",
         dict(app=', '.join(apps)),
         user="scheduler",
         level="warning"
    )

def alerts_services_not_updated():
    """ Alert if service is not updated for 48h
    """
    age = 2
    sql = """insert ignore
             into log
               select NULL,
                      "service.config",
                      "scheduler",
                      "service config not updated for more than %(age)d days (%%(date)s)",
                      concat('{"date": "', updated, '"}'),
                      now(),
                      svc_id,
                      0,
                      0,
                      md5(concat("service.config.notupdated",svcname,updated)),
                      "warning",
                      NULL
               from services
               where updated<date_sub(now(), interval %(age)d day)"""%dict(age=age)
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
                      "scheduler",
                      "service status not updated for more than %(age)dh (%%(date)s)",
                      concat('{"date": "', mon_updated, '"}'),
                      now(),
                      svc_id,
                      0,
                      0,
                      md5(concat("service.status.notupdated",node_id,svc_id,mon_updated)),
                      "warning",
                      node_id
               from svcmon
               where mon_updated<date_sub(now(), interval %(age)d hour)"""%dict(age=age)
    n = db.executesql(sql)
    db.commit()
    return n

def refresh_dash_action_errors():
    sql = """delete from dashboard
             where
               dash_type like "%action err%" and
               (svc_id, node_id) not in (
                 select svc_id, node_id
                 from b_action_errors
               )"""
    db.executesql(sql)
    db.commit()

def update_dash_action_errors():
    sql = """select
               e.err,
               s.svc_env,
               e.svc_id,
               e.node_id
             from
               b_action_errors e
             join services s on e.svc_id=s.svc_id
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
                   svc_id="%(svc_id)s",
                   node_id="%(node_id)s",
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
              """%dict(svc_id=row[2],
                       node_id=row[3],
                       sev=sev,
                       env=row[1],
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
    sql = """select id, svc_id, node_id from svcactions where
                 status="err" and
                 (ack=0 or ack is NULL) and
                 begin<date_sub(now(), interval %(age)d day)"""%dict(age=age)
    rows = db.executesql(sql)
    ids = map(lambda x: str(x[0]), rows)

    if len(ids) == 0:
        return

    sql = """insert ignore
             into log
               select NULL,
                      "service.action.notacked",
                      "scheduler",
                      "unacknowledged failed action '%%(action)s' at '%%(begin)s'",
                      concat('{"action": "', action, '", "begin": "', begin, '"}'),
                      now(),
                      svc_id,
                      0,
                      0,
                      md5(concat("service.action.notacked",node_id,svc_id,begin)),
                      "warning",
                      node_id
               from svcactions
               where
                 id in (%(ids)s)"""%dict(ids=','.join(ids))
    db.executesql(sql)
    db.commit()

    import datetime
    now = datetime.datetime.now()

    """ Ack all actions we sent an alert for
    """
    sql = """update svcactions set
               ack=1,
               acked_date="%(date)s",
               acked_comment="Automatically acknowledged",
               acked_by="admin@opensvc.com"
             where id in (%(ids)s)"""%dict(ids=','.join(ids), date=now)
    db.executesql(sql)
    db.commit()

    """ Update dashboard
    """
    update_dash_action_errors()

    return ids

def purge_sessions():
    from sessions2trash import single_loop
    single_loop(auth.settings.expiration, force=True, verbose=True)

def purge_svcdisks():
    sql = """delete from svcdisks where disk_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def purge_diskinfo():
    sql = """delete from diskinfo where disk_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def purge_stor_array():
    sql = """delete from stor_array where array_model like "vdisk%" and array_updated < DATE_SUB(NOW(), INTERVAL 2 day)"""
    db.executesql(sql)
    db.commit()

def update_dg_quota():
    sql = """insert ignore into stor_array_dg_quota
             select NULL, dg.id, sd.app_id, NULL
             from
               svcdisks sd
               join diskinfo di on sd.disk_id=di.disk_id
               join stor_array ar on (di.disk_arrayid=ar.array_name)
               join stor_array_dg dg on (di.disk_group=dg.dg_name and dg.array_id=ar.id)
          """
    db.executesql(sql)
    db.commit()

def purge_comp_rulesets_services():
    sql = """delete from comp_rulesets_services
             where
               svc_id not in (
                 select distinct svc_id from svcmon
               )
          """
    db.executesql(sql)
    db.commit()

def purge_comp_rulesets_nodes():
    sql = """delete from comp_rulesets_nodes
             where
               node_id not in (
                select node_id from nodes
               )
          """
    db.executesql(sql)
    db.commit()

def purge_comp_modulesets_services():
    sql = """delete from comp_modulesets_services
             where
               svc_id not in (
                 select distinct svc_id from svcmon
               )
          """
    db.executesql(sql)
    db.commit()

def purge_comp_modulesets_nodes():
    sql = """delete from comp_node_moduleset
             where
               node_id not in (
                select node_id from nodes
               )
          """
    db.executesql(sql)
    db.commit()

def purge_comp_status():
    #
    # purge entries older than 30 days
    #
    sql = """delete from comp_status
             where
               run_date<date_sub(now(), interval 31 day)
    """
    db.executesql(sql)
    db.commit()

    #
    # purge svc compliance status for deleted services
    #
    sql = """delete from comp_status
             where
               svc_id != "" and
               svc_id not in (
                 select distinct svc_id from svcmon
               )
           """
    db.executesql(sql)
    db.commit()

    #
    # purge node compliance status for deleted nodes
    #
    sql = """delete from comp_status
             where
               node_id not in (
                 select distinct node_id from nodes
               )
    """
    db.executesql(sql)
    db.commit()

    #
    # purge compliance status older than 7 days
    # for modules in no moduleset, ie not schedulable
    #
    sql = """delete from comp_status
             where
               run_date<date_sub(now(), interval 7 day) and
               run_module not in (
                 select modset_mod_name from comp_moduleset_modules
               )
    """
    db.executesql(sql)
    db.commit()

    #
    # purge node compliance status older than 7 days
    # for unattached modules
    #
    sql = """delete from comp_status
             where
               run_date<date_sub(now(), interval 7 day) and
               svc_id="" and
               run_module not in (
                 select modset_mod_name
                 from comp_moduleset_modules
                 where modset_id in (
                   select modset_id
                   from comp_node_moduleset
                 )
               )
    """
    db.executesql(sql)
    db.commit()

    #
    # purge svc compliance status older than 7 days
    # for unattached modules
    #
    sql = """delete from comp_status
             where
               run_date<date_sub(now(), interval 7 day) and
               svc_id != "" and
               run_module not in (
                 select modset_mod_name
                 from comp_moduleset_modules
                 where modset_id in (
                   select modset_id
                   from comp_modulesets_services
                 )
               )
    """
    db.executesql(sql)
    db.commit()


def purge_alerts_on_nodes_without_asset():
    l = db.nodes.on(db.dashboard.node_id==db.nodes.node_id)
    q = db.dashboard.node_id != ""
    q &= db.nodes.node_id == None
    ids = map(lambda x: x.id, db(q).select(db.dashboard.id, left=l))
    if len(ids) > 0:
        q = db.dashboard.id.belongs(ids)
        db(q).delete()
        db.commit()

    l = db.services.on(db.dashboard.svc_id==db.services.svc_id)
    q = db.dashboard.svc_id != ""
    q &= db.services.svc_id == None
    ids = map(lambda x: x.id, db(q).select(db.dashboard.id, left=l))
    if len(ids) > 0:
        q = db.dashboard.id.belongs(ids)
        db(q).delete()
        db.commit()

def cron_purge_packages():
    threshold = now - datetime.timedelta(days=100)
    q = db.packages.pkg_updated < threshold
    db(q).delete()
    db.commit()

def purge_alerts_comp_diff():
    sql = """select distinct(svc_id) from dashboard where
             dash_type="compliance differences in cluster"
    """
    rows = db.executesql(sql)
    svc_ids = [row[0] for row in rows]
    update_dash_compdiff_svc(svc_ids)

def cron_alerts_daily():
    print "alerts_apps_without_responsible"
    alerts_apps_without_responsible()
    print "alerts_services_not_updated"
    alerts_services_not_updated()
    print "alerts_failed_actions_not_acked"
    alerts_failed_actions_not_acked()
    print "refresh_b_action_errors"
    refresh_b_action_errors()
    print "refresh_dash_action_errors"
    refresh_dash_action_errors()
    print "purge_svcdisks"
    purge_svcdisks()
    print "purge_diskinfo"
    purge_diskinfo()
    print "purge_stor_array"
    purge_stor_array()
    print "update_dg_quota"
    update_dg_quota()
    print "purge_alerts_on_nodes_without_asset"
    purge_alerts_on_nodes_without_asset()
    print "cron_resmon_purge"
    cron_resmon_purge()
    print "cron_purge_node_hba"
    cron_purge_node_hba()
    print "cron_purge_packages"
    cron_purge_packages()
    print "cron_mac_dup"
    cron_mac_dup()
    print "purge_comp_status"
    purge_comp_status()
    print "purge_comp_modulesets_nodes"
    purge_comp_modulesets_nodes()
    print "purge_comp_rulesets_nodes"
    purge_comp_rulesets_nodes()
    print "purge_comp_modulesets_services"
    purge_comp_modulesets_services()
    print "purge_comp_rulesets_services"
    purge_comp_rulesets_services()
    print "purge_alerts_comp_diff"
    purge_alerts_comp_diff()
    print "purge_sessions"
    purge_sessions()

def cron_alerts_hourly():
    rets = []
    alert_wrong_netmask()
    rets.append(alerts_svcmon_not_updated())
    return rets

def cron_resmon_purge():
    sql = """delete from resmon where
              updated < date_sub(now(), interval 1 day)"""
    db.executesql(sql)
    db.commit()

def cron_mac_dup():
    sql = """select * from (
              select
               count(t.mac) as n,
               group_concat(t.node_id order by t.node_id),
               t.mac
              from (
               select node_ip.node_id,node_ip.mac from node_ip
               join nodes on nodes.node_id=node_ip.node_id
               where
                node_ip.intf not like "%:%" and
                node_ip.intf not like "usbecm%" and
                node_ip.intf not like "docker%" and
                node_ip.mac!="00:00:00:00:00:00" and
                node_ip.mac!="0:0:0:0:0:0" and
                node_ip.mac!="0" and
                node_ip.updated > date_sub(now(), interval 1 day)
               group by mac, node_id
              ) t
              group by t.mac) v
              where v.n>1"""

    rows = db.executesql(sql)

    if len(rows) == 0:
        # clean all
        sql = """delete from dashboard
                 where
                   dash_type = "mac duplicate"
              """
        db.executesql(sql)
        db.commit()
        return

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    for row in rows:
        for node_id in row[1].split(','):
            q = db.nodes.node_id == node_id
            node_entry = db(q).select(db.nodes.node_env).first()
            if node_entry is None:
                return
            environment = node_entry.node_env
            severity = 3
            if environment == "PRD":
                severity += 1
            sql = """insert into dashboard
                     set
                       dash_type="mac duplicate",
                       dash_severity=%(severity)d,
                       node_id="%(node_id)s",
                       svc_id="",
                       dash_fmt="mac %%(mac)s reported by nodes %%(nodes)s",
                       dash_dict='{"mac": "%(mac)s", "nodes": "%(nodes)s"}',
                       dash_created="%(now)s",
                       dash_env="%(environment)s",
                       dash_updated="%(now)s"
                     on duplicate key update
                       dash_fmt="mac %%(mac)s reported by nodes %%(nodes)s",
                       dash_dict='{"mac": "%(mac)s", "nodes": "%(nodes)s"}',
                       dash_env="%(environment)s",
                       dash_updated="%(now)s"
                  """%dict(severity=severity,
                           environment=environment,
                           node_id=node_id,
                           nodes=', '.join(map(lambda x: get_nodename(x), row[1].split(","))),
                           mac=row[2],
                           now=str(now))
            db.executesql(sql)
    db.commit()

    # clean old
    sql = """delete from dashboard
             where
               dash_type = "mac duplicate" and
               dash_updated < "%(now)s" """%dict(now=str(now))
    db.executesql(sql)
    db.commit()

def cron_feed_monitor():
    task_feed_monitor()

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
       m.node_id=n.node_id and
       m.mon_vmname=n2.nodename and
       m.mon_vmtype in ('ldom', 'hpvm', 'kvm', 'xen', 'vbox', 'ovm', 'esx', 'zone', 'lxc', 'jail', 'vz', 'srp') and
       m.mon_containerstatus in ("up", "stdby up", "warn")
    """
    db.executesql(sql)


def replay_perf_week():
    replay_perf(7)

def replay_perf_month():
    replay_perf(30)

all_stats = ['cpu', 'fs_u', 'proc', 'block', 'blockdev', 'netdev',
'netdev_err', 'mem_u', 'swap', 'svc']

def replay_perf(days):
    begin = now - datetime.timedelta(days=1,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
    end = begin + datetime.timedelta(days=1)

    for i in range(days):
        begin = begin - datetime.timedelta(days=1)
        end = end - datetime.timedelta(days=1)
        _perf_ageing(begin, end, "hour")
        _perf_ageing(begin, end, "day")

def cron_perf():
    now = datetime.datetime.now()
    begin = now - datetime.timedelta(days=1,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
    end = begin + datetime.timedelta(days=1)
    _perf_ageing(begin, end, "hour")
    _perf_ageing(begin, end, "day")

def _perf_ageing(begin, end, period, stats=None):
    if stats is None:
        stats = all_stats
    for stat in stats:
        print "insert %s %s stats (%s)"%(period, stat, str(begin))
        globals()["_perf_"+stat](begin, end, period)
        db.commit()

def prev_period(period):
    periods = ['', 'hour', 'day']
    i = periods.index(period)
    p = periods[i-1]
    if len(p) > 0:
        return '_'+p
    return p

def _perf_proc(begin, end, period):
    sql = """insert ignore into stats_proc_%(period)s
             select
               %(period_sql)s as d,
               runq_sz,
               plist_sz,
               ldavg_1,
               ldavg_5,
               ldavg_15,
               node_id
             from stats_proc%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    rows = db.executesql(sql)

def _perf_fs_u(begin, end, period):
    sql = """insert ignore into stats_fs_u_%(period)s
             select
               %(period_sql)s as d,
               mntpt,
               avg(size),
               avg(used),
               node_id
             from stats_fs_u%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, mntpt, d""" % dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_cpu(begin, end, period):
    sql = """insert ignore into stats_cpu_%(period)s
             select
               %(period_sql)s as d,
               cpu,
               avg(usr),
               avg(nice),
               avg(sys),
               avg(iowait),
               avg(steal),
               avg(irq),
               avg(soft),
               avg(guest),
               avg(gnice),
               avg(idle),
               node_id
             from stats_cpu%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s' and
               cpu='ALL'
             group by
               node_id, d""" % dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_block(begin, end, period):
    sql = """insert ignore into stats_block_%(period)s
             select 
                    %(period_sql)s as d,
                    avg(tps),
                    avg(rtps),
                    avg(wtps),
                    avg(rbps),
                    avg(wbps),
                    node_id
             from stats_block%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_mem_u(begin, end, period):
    sql = """insert ignore into stats_mem_u_%(period)s
             select
               avg(kbmemfree),
               avg(kbmemused),
               avg(pct_memused),
               avg(kbbuffers),
               avg(kbcached),
               avg(kbcommit),
               avg(pct_commit),
               %(period_sql)s as d,
               avg(kbmemsys),
               avg(kbactive),
               avg(kbinact),
               avg(kbdirty),
               node_id
             from stats_mem_u%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_blockdev(begin, end, period):
    sql = """insert ignore into stats_blockdev_%(period)s
             select
               %(period_sql)s as d,
               dev,
               avg(tps),
               avg(rsecps),
               avg(wsecps),
               avg(avgrq_sz),
               avg(avgqu_sz),
               avg(await),
               avg(svctm),
               avg(pct_util),
               node_id
             from stats_blockdev%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, dev, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_netdev(begin, end, period):
    sql = """insert ignore into stats_netdev_%(period)s
             select
               %(period_sql)s as d,
               dev,
               avg(rxkBps),
               avg(txkBps),
               avg(rxpckps),
               avg(txpckps),
               node_id
             from stats_netdev%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, dev, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_netdev_err(begin, end, period):
    sql = """insert ignore into stats_netdev_err_%(period)s
             select
               %(period_sql)s as d,
               avg(rxerrps),
               avg(txerrps),
               avg(collps),
               avg(rxdropps),
               avg(txdropps),
               dev,
               node_id
             from stats_netdev_err%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, dev, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_swap(begin, end, period):
    sql = """insert ignore into stats_swap_%(period)s
             select
               %(period_sql)s as d,
               avg(kbswpfree),
               avg(kbswpused),
               avg(pct_swpused),
               avg(kbswpcad),
               avg(pct_swpcad),
               node_id
             from stats_swap%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def _perf_svc(begin, end, period):
    sql = """insert ignore into stats_svc_%(period)s
             select
               %(period_sql)s as d,
               svc_id,
               avg(swap),
               avg(rss),
               avg(cap),
               avg(at),
               avg(avgat),
               avg(pg),
               avg(avgpg),
               avg(nproc),
               avg(mem),
               avg(cpu),
               avg(cap_cpu),
               node_id
             from stats_svc%(prev_period)s
             where
               date>='%(begin)s' and
               date<='%(end)s'
             group by
               node_id, svc_id, d"""%dict(
      prev_period=prev_period(period),
      period_sql=period_sql(period),
      period=period,
      begin=begin,
      end=end,
    )
    db.executesql(sql)

def test_task_metrics():
    task_metrics(verbose=True)
