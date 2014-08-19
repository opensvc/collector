def update_dash_compdiff(nodename):
    nodename = nodename.strip("'")
    q = db.svcmon.mon_nodname == nodename
    q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
    rows = db(q).select(db.svcmon.mon_svcname, db.svcmon.mon_svctype)
    svcnames = map(lambda x: x.mon_svcname, rows)
    update_dash_compdiff_svc(svcnames)
    dashboard_events()

def update_dash_compdiff_svc(svcnames):
    if type(svcnames) != list:
        svcnames = [svcnames]

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    for svcname in svcnames:
        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=1440)
        rows = db(q).select(db.svcmon.mon_nodname,
                            db.svcmon.mon_svctype,
                            orderby=db.svcmon.mon_nodname)
        nodes = map(lambda x: x.mon_nodname, rows)
        n = len(nodes)

        if n < 2:
            continue

        row = rows[0]

        sql = """select count(t.id) from (
                   select
                     cs.id,
                     count(cs.run_nodename) as c
                   from
                     comp_status cs,
                     svcmon m
                   where
                     (cs.run_svcname is NULL or cs.run_svcname="") and
                     m.mon_svcname="%(svcname)s" and
                     m.mon_nodname=cs.run_nodename
                   group by
                     cs.run_svcname,
                     cs.run_module,
                     cs.run_status
                  ) as t
                  where
                    t.c!=%(n)s
              """%dict(svcname=svcname, n=n)

        rows = db.executesql(sql)

        if rows[0][0] == 0:
            continue

        if row.mon_svctype == 'PRD':
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
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(n)s compliance differences in cluster %%(nodes)s",
                   dash_dict='{"n": %(n)d, "nodes": "%(nodes)s"}',
                   dash_dict_md5=md5('{"n": %(n)d, "nodes": "%(nodes)s"}'),
                   dash_created="%(now)s",
                   dash_updated="%(now)s",
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_updated="%(now)s"
              """%dict(svcname=svcname,
                       sev=sev,
                       now=str(now),
                       env=row.mon_svctype,
                       n=rows[0][0],
                       nodes=nodes_s)

        rows = db.executesql(sql)
        db.commit()

    if len(svcnames) > 0:
        q = db.dashboard.dash_svcname.belongs(svcnames)
        q &= db.dashboard.dash_type == "compliance differences in cluster"
        q &= (db.dashboard.dash_updated < now) | (db.dashboard.dash_updated == None)
        db(q).delete()
        db.commit()


def update_dash_moddiff_node(nodename):
    q = db.svcmon.mon_nodname == nodename
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=2)
    svcnames = [r.mon_svcname for r in db(q).select(db.svcmon.mon_svcname)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_moddiff(svcname))

    dashboard_events()
    return str(r)

def update_dash_moddiff(svcname):

    def cleanup(svcname, now):
        sql = """delete from dashboard
                 where
                   dash_type="compliance moduleset attachment differences in cluster" and
                   dash_svcname="%(svcname)s" and
                   dash_updated < "%(now)s"
              """%dict(svcname=svcname, now=str(now))
        db.executesql(sql)
        db.commit()

    rows = db(db.svcmon.mon_svcname==svcname).select(orderby=db.svcmon.mon_nodname)
    nodes = [r.mon_nodname for r in rows]
    n = len(nodes)

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    if n < 2:
        cleanup(svcname, now)
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
               count(nm.modset_node) as n,
               group_concat(nm.modset_node) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               svcmon m,
               comp_moduleset ms
             where
               m.mon_svcname="%(svcname)s" and
               m.mon_nodname=nm.modset_node and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n)
    _rows = db.executesql(sql)

    if _rows[0][0] == 0:
        cleanup(svcname, now)
        return

    sql = """
           insert into dashboard set
             dash_type="compliance moduleset attachment differences in cluster",
             dash_svcname="%(svcname)s",
             dash_nodename="",
             dash_severity=%(sev)d,
             dash_fmt="%%(n)d differences in cluster %%(nodes)s",
             dash_dict='{"n": %(ndiff)d, "nodes": "%(nodes)s"}',
             dash_created="%(now)s",
             dash_updated="%(now)s",
             dash_dict_md5=md5('{"n": %(ndiff)d, "nodes": "%(nodes)s"}'),
             dash_env="%(env)s"
           on duplicate key update
             dash_updated="%(now)s"
    """%dict(now=str(now), svcname=svcname, nodes=nodes_s, ndiff=_rows[0][0], sev=sev, env=rows.first().mon_svctype)
    db.executesql(sql)
    db.commit()

    cleanup(svcname, now)
    return svcname, _rows[0][0]

def update_dash_rsetdiff_node(nodename):
    q = db.svcmon.mon_nodname == nodename
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=2)
    svcnames = [r.mon_svcname for r in db(q).select(db.svcmon.mon_svcname)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_rsetdiff(svcname))

    dashboard_events()
    return str(r)

def update_dash_rsetdiff(svcname):
    rows = db(db.svcmon.mon_svcname==svcname).select(orderby=db.svcmon.mon_nodname)
    nodes = [r.mon_nodname for r in rows]
    n = len(nodes)

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    def cleanup(svcname, now):
        sql = """delete from dashboard
                 where
                   dash_type="compliance ruleset attachment differences in cluster" and
                   dash_svcname="%(svcname)s" and
                   dash_updated < "%(now)s"
              """%dict(svcname=svcname, now=str(now))
        db.executesql(sql)
        db.commit()

    if n < 2:
        cleanup(svcname, now)
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
               count(rn.nodename) as n,
               group_concat(rn.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               svcmon m,
               comp_rulesets rs
             where
               m.mon_svcname="%(svcname)s" and
               m.mon_nodname=rn.nodename and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n)
    _rows = db.executesql(sql)

    if _rows[0][0] == 0:
        cleanup(svcname, now)
        return

    sql = """
           insert into dashboard set
             dash_type="compliance ruleset attachment differences in cluster",
             dash_svcname="%(svcname)s",
             dash_nodename="",
             dash_severity=%(sev)d,
             dash_fmt="%%(n)d differences in cluster %%(nodes)s",
             dash_dict='{"n": %(ndiff)d, "nodes": "%(nodes)s"}',
             dash_created="%(now)s",
             dash_updated="%(now)s",
             dash_dict_md5=md5('{"n": %(ndiff)d, "nodes": "%(nodes)s"}'),
             dash_env="%(env)s"
           on duplicate key update
             dash_updated="%(now)s"
    """%dict(now=str(now), svcname=svcname, nodes=nodes_s, ndiff=_rows[0][0], sev=sev, env=rows.first().mon_svctype)
    db.executesql(sql)
    db.commit()

    return svcname, _rows[0][0]

