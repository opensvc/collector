def svc_log_update(svc_id, astatus, deferred=False):
    change = False
    changed = set()
    sql = """select id, svc_availstatus, svc_end, svc_begin from services_log_last
             where svc_id="%s"
          """ % svc_id
    rows = db.executesql(sql)
    end = datetime.datetime.now()
    if len(rows) == 1:
        prev = rows[0]
        if prev[1] == astatus:
            sql = """update services_log_last set svc_end="%s" where id=%d""" % (end, prev[0])
            db.executesql(sql)
        else:
            db.services_log.insert(svc_id=svc_id,
                                   svc_begin=prev[3],
                                   svc_end=end,
                                   svc_availstatus=prev[1])
            change = True
        changed.add("services_log")
    if len(rows) == 0 or change:
        db.services_log_last.update_or_insert({"svc_id": svc_id},
                                              svc_id=svc_id,
                                              svc_begin=end,
                                              svc_end=end,
                                              svc_availstatus=astatus)
        changed.add("services_log")
    if not deferred and "services_log" in changed:
        db.commit()
        table_modified("services_log")
    return changed

def svcmon_log_update(node_id, svc_id, idata, deferred=False):
    change = False
    changed = set()
    sql = """select * from svcmon_log_last
             where node_id="%s" and svc_id="%s"
          """ % (node_id, svc_id)
    rows = db.executesql(sql, as_dict=True)
    end = datetime.datetime.now()
    if len(rows) == 1:
        prev = rows[0]
        if prev["mon_availstatus"] == idata["avail"] and \
           prev["mon_overallstatus"] == idata["overall"] and \
           prev["mon_syncstatus"] == idata["sync"] and \
           prev["mon_ipstatus"] == idata["ip"] and \
           prev["mon_fsstatus"] == idata["fs"] and \
           prev["mon_diskstatus"] == idata["disk"] and \
           prev["mon_sharestatus"] == idata["share"] and \
           prev["mon_containerstatus"] == idata["container"] and \
           prev["mon_appstatus"] == idata["app"]:
            sql = """update svcmon_log_last set mon_end="%s" where id=%d""" % (end, prev["id"])
            db.executesql(sql)
        else:
            db.svcmon_log.insert(
                svc_id=svc_id,
                node_id=node_id,
                mon_availstatus=prev["mon_availstatus"],
                mon_overallstatus=prev["mon_overallstatus"],
                mon_syncstatus=prev["mon_syncstatus"],
                mon_ipstatus=prev["mon_ipstatus"],
                mon_fsstatus=prev["mon_fsstatus"],
                mon_diskstatus=prev["mon_diskstatus"],
                mon_sharestatus=prev["mon_sharestatus"],
                mon_containerstatus=prev["mon_containerstatus"],
                mon_appstatus=prev["mon_appstatus"],
                mon_begin=prev["mon_begin"],
                mon_end=end,
            )
            change = True
        changed.add("svcmon_log")
    if len(rows) == 0 or change:
        db.svcmon_log_last.update_or_insert({
                "svc_id": svc_id,
                "node_id": node_id,
            },
            svc_id=svc_id,
            node_id=node_id,
            mon_availstatus=idata["avail"],
            mon_overallstatus=idata["overall"],
            mon_syncstatus=idata["sync"],
            mon_ipstatus=idata["ip"],
            mon_fsstatus=idata["fs"],
            mon_diskstatus=idata["disk"],
            mon_sharestatus=idata["share"],
            mon_containerstatus=idata["container"],
            mon_appstatus=idata["app"],
            mon_begin=end,
            mon_end=end,
        )
        changed.add("svcmon_log")
    if not deferred and "svcmon_log" in changed:
        db.commit()
        table_modified("svcmon_log")
    return changed

def resmon_log_update(node_id, svc_id, rid, astatus, deferred=False):
    change = False
    changed = set()
    rid = rid.strip("'")
    astatus = astatus.strip("'")
    sql = """select id, res_status, res_end, res_begin from resmon_log_last
             where node_id="%s" and svc_id="%s" and rid="%s"
          """ % (node_id, svc_id, rid)
    rows = db.executesql(sql)
    end = datetime.datetime.now()
    if len(rows) == 1:
        prev = rows[0]
        if prev[1] == astatus:
            sql = """update resmon_log_last set res_end="%s" where id=%d""" % (end, prev[0])
            db.executesql(sql)
        else:
            db.resmon_log.insert(svc_id=svc_id,
                                 node_id=node_id,
                                 rid=rid,
                                 res_begin=prev[3],
                                 res_end=end,
                                 res_status=prev[1])
            change = True
        changed.add("resmon_log")
    if len(rows) == 0 or change:
        db.resmon_log_last.update_or_insert({"svc_id": svc_id,
                                             "node_id": node_id,
                                             "rid": rid},
                                            svc_id=svc_id,
                                            node_id=node_id,
                                            rid=rid,
                                            res_begin=end,
                                            res_end=end,
                                            res_status=astatus)
        changed.add("resmon_log")
    if not deferred and "resmon_log" in changed:
        db.commit()
        table_modified("resmon_log")
    return changed

def update_dash_svcmon_not_updated(svc_id, node_id):
    sql = """delete from dashboard
               where
                 svc_id = "%(svc_id)s" and
                 node_id = "%(node_id)s" and
                 dash_type = "service status not updated"
          """%dict(svc_id=svc_id, node_id=node_id)
    ret = db.executesql(sql)
    db.commit()
    if ret:
        return set(["dashboard"])
    return set()
    # dashboard_events() called from __svcmon_update

def update_dash_service_available_but_degraded(svc_id, env, svc_availstatus, svc_status):
    if env == 'PRD':
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
                       env=env,
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

def update_dash_service_unavailable(svc_id, env, svc_availstatus):
    changed = set()
    if env == 'PRD':
        sev = 4
    else:
        sev = 3
    if svc_availstatus in ["up", "n/a"]:
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   svc_id="%s"
              """%svc_id
        data = db.executesql(sql)
        if data:
            changed.add("dashboard")
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
            changed.add("dashboard")
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
                       env=env,
                       status=svc_availstatus)
        db.executesql(sql)
        db.commit()
        changed.add("dashboard")
    # dashboard_events() called from __svcmon_update
    return changed

def svc_status_update(svc_id):
    """ avail and overall status can be:
        up, down, stdby up, stdby down, warn, undef
    """
    changed = set()
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
        changed = svc_log_update(svc_id, astatus, deferred=True)
    except NameError:
        pass
    try:
        svc_env = rows[0]["mon_svctype"]
    except:
        svc_env = 'TST'

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
    if "services_log" in changed:
        table_modified("services_log")

    update_dash_service_unavailable(svc_id, svc_env, astatus)
    update_dash_service_available_but_degraded(svc_id, svc_env, astatus, ostatus)



