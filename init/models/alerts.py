def update_dash_compdiff(node_id):
    q = db.svcmon.node_id == node_id
    q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
    rows = db(q).select(db.svcmon.svc_id, db.svcmon.mon_svctype)
    svc_ids = map(lambda x: x.svc_id, rows)
    update_dash_compdiff_svc(svc_ids)
    dashboard_events()

def update_dash_compdiff_svc(svc_ids):
    if type(svc_ids) != list:
        svc_ids = [svc_ids]

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    for svc_id in svc_ids:
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.nodes.node_id
        q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=1440)
        rows = db(q).select(db.nodes.nodename,
                            orderby=db.nodes.nodename)
        nodes = map(lambda x: x.nodename, rows)
        n = len(nodes)

        if n < 2:
            continue

        sql = """
                   select
                     cs.id,
                     count(cs.node_id) as c,
                     cs.run_module,
                     cs.run_status
                   from
                     comp_status cs,
                     svcmon m
                   where
                     (cs.svc_id is NULL or cs.svc_id="") and
                     m.svc_id="%(svc_id)s" and
                     m.node_id=cs.node_id
                   group by
                     cs.svc_id,
                     cs.run_module,
                     cs.run_status
              """%dict(svc_id=svc_id, n=n)

        rows = db.executesql(sql)

        h = {}
        for row in rows:
            if row[2] not in h:
                h[row[2]] = {}
            h[row[2]][row[3]] = row[1]

        pb = 0
        for mod, d in h.items():
            if len(d) == 1:
                # all ok or all err is not a pb
                continue
            if len(d) == 2 and 2 in d:
                # n/a + ok or nok is not a pb
                continue
            pb += 1

        if pb == 0:
            continue

        q = db.services.svc_id == svc_id
        svc = db(q).select(db.services.svc_env).first()
        if svc and svc.svc_env == 'PRD':
            sev = 1
        else:
            sev = 0

        skip = 0
        trail = ""
        while True:
            nodes_s = ','.join(nodes).replace("'", "")+trail
            if len(nodes_s) < 50:
                break
            skip += 1
            nodes = nodes[:-1]
            trail = ", ... (+%d)"%skip

        sql = """insert into dashboard
                 set
                   dash_type="compliance differences in cluster",
                   svc_id="%(svc_id)s",
                   node_id="",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(n)s compliance differences in cluster %%(nodes)s",
                   dash_dict='{"n": %(n)d, "nodes": "%(nodes)s"}',
                   dash_dict_md5=md5('{"n": %(n)d, "nodes": "%(nodes)s"}'),
                   dash_created="%(now)s",
                   dash_updated="%(now)s",
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_updated="%(now)s"
              """%dict(svc_id=svc_id,
                       sev=sev,
                       now=str(now),
                       env=svc.svc_env,
                       n=pb,
                       nodes=nodes_s)

        rows = db.executesql(sql)
        db.commit()
        ws_send("dashboard_change")

    if len(svc_ids) > 0:
        q = db.dashboard.svc_id.belongs(svc_ids)
        q &= db.dashboard.dash_type == "compliance differences in cluster"
        q &= (db.dashboard.dash_updated < now) | (db.dashboard.dash_updated == None)
        n = db(q).delete()
        db.commit()
        if n > 0:
            ws_send("dashboard_change")


def update_dash_moddiff_node(node_id):
    q = db.svcmon.node_id == node_id
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=2)
    svc_ids = [r.svc_id for r in db(q).select(db.svcmon.svc_id)]

    r = []
    for svc_id in svc_ids:
        r.append(update_dash_moddiff(svc_id))

    dashboard_events()
    return str(r)

def update_dash_moddiff(svc_id):

    def cleanup(svc_id, now):
        sql = """delete from dashboard
                 where
                   dash_type="compliance moduleset attachment differences in cluster" and
                   svc_id="%(svc_id)s" and
                   dash_updated < "%(now)s"
              """%dict(svc_id=svc_id, now=str(now))
        db.executesql(sql)
        db.commit()

    rows = db(db.svcmon.svc_id==svc_id).select(orderby=db.svcmon.node_id)
    nodes = [r.node_id for r in rows]
    n = len(nodes)

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    if n < 2:
        cleanup(svc_id, now)
        return

    if rows.first().mon_svctype == 'PRD':
        sev = 1
    else:
        sev = 0

    skip = 0
    trail = ""
    while True:
        nodes_s = ','.join(nodes).replace("'", "")+trail
        if len(nodes_s) < 50:
            break
        skip += 1
        nodes = nodes[:-1]
        trail = ", ... (+%d)"%skip

    sql = """
            select count(t.n) from
            (
             select
               count(nm.node_id) as n,
               group_concat(nm.node_id) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               svcmon m,
               comp_moduleset ms
             where
               m.svc_id="%(svc_id)s" and
               m.node_id=nm.node_id and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svc_id=svc_id, n=n)
    _rows = db.executesql(sql)

    if _rows[0][0] == 0:
        cleanup(svc_id, now)
        return

    sql = """
           insert into dashboard set
             dash_type="compliance moduleset attachment differences in cluster",
             svc_id="%(svc_id)s",
             node_id="",
             dash_severity=%(sev)d,
             dash_fmt="%%(n)d differences in cluster %%(nodes)s",
             dash_dict='{"n": %(ndiff)d, "nodes": "%(nodes)s"}',
             dash_created="%(now)s",
             dash_updated="%(now)s",
             dash_dict_md5=md5('{"n": %(ndiff)d, "nodes": "%(nodes)s"}'),
             dash_env="%(env)s"
           on duplicate key update
             dash_updated="%(now)s"
    """%dict(now=str(now), svc_id=svc_id, nodes=nodes_s, ndiff=_rows[0][0], sev=sev, env=rows.first().mon_svctype)
    db.executesql(sql)
    db.commit()

    cleanup(svc_id, now)
    return svc_id, _rows[0][0]

def update_dash_rsetdiff_node(node_id):
    q = db.svcmon.node_id == node_id
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=2)
    svc_ids = [r.svc_id for r in db(q).select(db.svcmon.svc_id)]

    r = []
    for svc_id in svc_ids:
        r.append(update_dash_rsetdiff(svc_id))

    dashboard_events()
    return str(r)

def update_dash_rsetdiff(svc_id):
    q = db.svcmon.svc_id == svc_id
    q &= db.svcmon.node_id == db.nodes.node_id
    rows = db(q).select(orderby=db.svcmon.node_id)
    nodes = [r.nodes.nodename for r in rows]
    n = len(nodes)

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    def cleanup(svc_id, now):
        sql = """delete from dashboard
                 where
                   dash_type="compliance ruleset attachment differences in cluster" and
                   svc_id="%(svc_id)s" and
                   dash_updated < "%(now)s"
              """%dict(svc_id=svc_id, now=str(now))
        db.executesql(sql)
        db.commit()

    if n < 2:
        cleanup(svc_id, now)
        return

    if rows.first().svcmon.mon_svctype == 'PRD':
        sev = 1
    else:
        sev = 0

    skip = 0
    trail = ""
    while True:
        nodes_s = ','.join(nodes)+trail
        if len(nodes_s) < 50:
            break
        skip += 1
        nodes = nodes[:-1]
        trail = ", ... (+%d)"%skip

    sql = """
            select count(t.n) from
            (
             select
               count(rn.node_id) as n,
               group_concat(rn.node_id) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               svcmon m,
               comp_rulesets rs
             where
               m.svc_id="%(svc_id)s" and
               m.node_id=rn.node_id and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svc_id=svc_id, n=n)
    _rows = db.executesql(sql)

    if _rows[0][0] == 0:
        cleanup(svc_id, now)
        return

    sql = """
           insert into dashboard set
             dash_type="compliance ruleset attachment differences in cluster",
             svc_id="%(svc_id)s",
             node_id="",
             dash_severity=%(sev)d,
             dash_fmt="%%(n)d differences in cluster %%(nodes)s",
             dash_dict='{"n": %(ndiff)d, "nodes": "%(nodes)s"}',
             dash_created="%(now)s",
             dash_updated="%(now)s",
             dash_dict_md5=md5('{"n": %(ndiff)d, "nodes": "%(nodes)s"}'),
             dash_env="%(env)s"
           on duplicate key update
             dash_updated="%(now)s"
    """%dict(now=str(now), svc_id=svc_id, nodes=nodes_s, ndiff=_rows[0][0], sev=sev, env=rows.first().svcmon.mon_svctype)
    db.executesql(sql)
    db.commit()

    return svc_id, _rows[0][0]

