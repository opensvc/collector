def svc_log_update(svc_id, astatus):
    sql = """select id, svc_availstatus, svc_end from services_log
             where svc_id="%s"
             order by id desc limit 1 """ % svc_id
    rows = db.executesql(sql)
    end = datetime.datetime.now()
    change = False
    changed = False
    if len(rows) == 1:
        prev = rows[0]
        sql = """update services_log set svc_end="%s" where id=%d""" % (end, prev[0])
        db.executesql(sql)
        db.commit()
        if prev[1] != astatus:
            change = True
        changed = True
    if len(rows) == 0 or change:
        db.services_log.insert(svc_id=svc_id,
                               svc_begin=end,
                               svc_end=end,
                               svc_availstatus=astatus)
        db.commit()
        changed = True
    if changed:
        table_modified("services_log")

def resmon_log_update(node_id, svc_id, rid, astatus):
    rid = rid.strip("'")
    astatus = astatus.strip("'")
    sql = """select id, res_status, res_end from resmon_log
             where node_id="%s" and svc_id="%s" and rid="%s"
             order by id desc limit 1 """ % (node_id, svc_id, rid)
    rows = db.executesql(sql)
    end = datetime.datetime.now()
    change = False
    if len(rows) == 1:
        prev = rows[0]
        sql = """update resmon_log set res_end="%s" where id=%d""" % (end, prev[0])
        db.executesql(sql)
        db.commit()
        if prev[1] == astatus:
            change = True
        changed = True
    if len(rows) == 0 or change:
        db.resmon_log.insert(svc_id=svc_id,
                             node_id=node_id,
                             rid=rid,
                             res_begin=end,
                             res_end=end,
                             res_status=astatus)
        changed = True
    if changed:
        table_modified("resmon_log")

def update_dash_svcmon_not_updated(svc_id, node_id):
    sql = """delete from dashboard
               where
                 svc_id = "%(svc_id)s" and
                 node_id = "%(node_id)s" and
                 dash_type = "service status not updated"
          """%dict(svc_id=svc_id, node_id=node_id)
    rows = db.executesql(sql)
    db.commit()
    # dashboard_events() called from __svcmon_update

def update_dash_service_available_but_degraded(svc_id, svc_type, svc_availstatus, svc_status):
    if svc_type == 'PRD':
        sev = 3
    else:
        sev = 2
    if svc_availstatus == "up" and svc_status != "up":
        sql = """insert into dashboard
                 set
                   dash_type="service available but degraded",
                   svc_id="%(svc_id)s",
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
              """%dict(svc_id=svc_id,
                       sev=sev,
                       env=svc_type,
                       status=svc_status)
        db.executesql(sql)
        db.commit()
    else:
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   svc_id="%s"
              """%svc_id
        db.executesql(sql)
        db.commit()
    # dashboard_events() called from __svcmon_update

def update_dash_service_unavailable(svc_id, svc_type, svc_availstatus):
    if svc_type == 'PRD':
        sev = 4
    else:
        sev = 3
    if svc_availstatus in ["up", "n/a"]:
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   svc_id="%s"
              """%svc_id
        db.executesql(sql)
        db.commit()
    else:
        sql = """select count(id) from svcmon_log_ack
                 where
                   svc_id="%s" and
                   mon_begin <= now() and
                   mon_end >= now()
              """%(svc_id)
        n = db.executesql(sql)[0][0]
        if n > 0:
            sql = """delete from dashboard
                     where
                       dash_type="service unavailable" and
                       svc_id="%s"
                  """%(svc_id)
            db.executesql(sql)
            db.commit()
            return

        sql = """insert into dashboard
                 set
                   dash_type="service unavailable",
                   svc_id="%(svc_id)s",
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svc_id=svc_id,
                       sev=sev,
                       env=svc_type,
                       status=svc_availstatus)
        db.executesql(sql)
        db.commit()
    # dashboard_events() called from __svcmon_update

def svc_status_update(svc_id):
    """ avail and overall status can be:
        up, down, stdby up, stdby down, warn, undef
    """
    sql = """select mon_overallstatus, mon_availstatus, mon_updated, mon_svctype from svcmon where svc_id="%s" """ % svc_id
    rows = db.executesql(sql, as_dict=True)

    tlim = datetime.datetime.now() - datetime.timedelta(minutes=15)
    ostatus_l = [r["mon_overallstatus"] for r in rows if r["mon_updated"] is not None and r["mon_updated"] > tlim]
    astatus_l = [r["mon_availstatus"] for r in rows if r["mon_updated"] is not None and r["mon_updated"] > tlim]
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
        svc_log_update(svc_id, astatus)
    except NameError:
        pass
    try:
        svctype = rows[0]["mon_svctype"]
    except:
        svctype = 'TST'

    sql = """update services set
                svc_status="%(svc_status)s",
                svc_availstatus="%(svc_availstatus)s",
                svc_status_updated=NOW()
             where svc_id="%(svc_id)s" """% dict(
      svc_id=svc_id,
      svc_status=ostatus,
      svc_availstatus=astatus,
    )
    db.executesql(sql)
    db.commit()

    update_dash_service_unavailable(svc_id, svctype, astatus)
    update_dash_service_available_but_degraded(svc_id, svctype, astatus, ostatus)



