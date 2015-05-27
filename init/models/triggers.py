def update_dash_service_available_but_degraded(svc_name, svc_type, svc_availstatus, svc_status):
    if svc_type == 'PRD':
        sev = 3
    else:
        sev = 2
    if svc_availstatus == "up" and svc_status != "up":
        sql = """insert into dashboard
                 set
                   dash_type="service available but degraded",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current overall status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current overall status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       env=svc_type,
                       status=svc_status)
        db.executesql(sql)
        db.commit()
    else:
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
        db.commit()
    # dashboard_events() called from __svcmon_update

def update_dash_service_unavailable(svc_name, svc_type, svc_availstatus):
    if svc_type == 'PRD':
        sev = 4
    else:
        sev = 3
    if svc_availstatus in ["up", "n/a"]:
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
        db.commit()
    else:
        sql = """select count(id) from svcmon_log_ack
                 where
                   mon_svcname="%s" and
                   mon_begin <= now() and
                   mon_end >= now()
              """%(svc_name)
        n = db.executesql(sql)[0][0]
        if n > 0:
            sql = """delete from dashboard
                     where
                       dash_type="service unavailable" and
                       dash_svcname="%s"
                  """%(svc_name)
            db.executesql(sql)
            db.commit()
            return

        sql = """insert into dashboard
                 set
                   dash_type="service unavailable",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s", "svcname": "%(svcname)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s", "svcname": "%(svcname)s"}',
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       env=svc_type,
                       status=svc_availstatus)
        db.executesql(sql)
        db.commit()
    # dashboard_events() called from __svcmon_update

def svc_status_update(svcname):
    """ avail and overall status can be:
        up, down, stdby up, stdby down, warn, undef
    """
    q = db.svcmon.mon_svcname == svcname
    rows = db(q).select(db.svcmon.mon_overallstatus,
                        db.svcmon.mon_availstatus,
                        db.svcmon.mon_updated,
                        db.svcmon.mon_svctype,
                        db.svcmon.mon_frozen)

    tlim = datetime.datetime.now() - datetime.timedelta(minutes=15)
    ostatus_l = [r.mon_overallstatus for r in rows if r.mon_updated is not None and r.mon_updated > tlim]
    astatus_l = [r.mon_availstatus for r in rows if r.mon_updated is not None and r.mon_updated > tlim]
    n_trusted_nodes = len(ostatus_l)
    n_nodes = len(rows)
    ostatus_l = set(ostatus_l)
    astatus_l = set(astatus_l)

    ostatus = 'undef'
    astatus = 'undef'

    if 'up' in astatus_l:
        astatus = 'up'
    elif n_trusted_nodes == 0:
        astatus = 'undef'
    else:
        if astatus_l == set(['n/a']):
            astatus = 'n/a'
        elif 'warn' in astatus_l:
            astatus = 'warn'
        else:
            astatus = 'down'

    if n_trusted_nodes < n_nodes:
        ostatus = 'warn'
    elif n_trusted_nodes == 0:
        ostatus = 'undef'
    elif 'warn' in ostatus_l or \
         'stdby down' in ostatus_l or \
         'undef' in ostatus_l:
        ostatus = 'warn'
    elif set(['up']) == ostatus_l or \
         set(['up', 'down']) == ostatus_l or \
         set(['up', 'stdby up']) == ostatus_l or \
         set(['up', 'down', 'stdby up']) == ostatus_l or \
         set(['up', 'down', 'stdby up', 'n/a']) == ostatus_l:
        ostatus = 'up'
    elif set(['down']) == ostatus_l or \
         set(['down', 'stdby up']) == ostatus_l or \
         set(['down', 'stdby up', 'n/a']) == ostatus_l:
        ostatus = 'down'
    else:
        ostatus = 'undef'

    try:
        svc_log_update(svcname, astatus)
    except NameError:
        pass
    try:
        svctype = rows[0].mon_svctype
    except:
        svctype = 'TST'

    db(db.services.svc_name==svcname).update(
      svc_status=ostatus,
      svc_availstatus=astatus,
      svc_status_updated=datetime.datetime.now(),
    )
    db.commit()

    update_dash_service_unavailable(svcname, svctype, astatus)
    update_dash_service_available_but_degraded(svcname, svctype, astatus, ostatus)


