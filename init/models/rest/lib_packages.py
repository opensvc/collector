def lib_packages_diff(node_ids=[], svc_ids=[], encap=False):
    if len(svc_ids) > 0:
        if encap:
            q = db.svcmon.svc_id.belongs(svc_ids)
            q &= db.svcmon.mon_vmname == db.nodes.nodename
            q &= db.svcmon.mon_vmname != ""
            q &= db.svcmon.mon_vmname != None
            q = q_filter(q, svc_field=db.svcmon.svc_id)
            rows = db(q).select(db.nodes.node_id,
                                groupby=db.nodes.node_id)
            node_ids += [r.node_id for r in rows]
        else:
            q = db.svcmon.svc_id.belongs(svc_ids)
            q = q_filter(q, svc_field=db.svcmon.svc_id)
            rows = db(q).select(db.svcmon.node_id, groupby=db.svcmon.node_id)
            node_ids += [r.node_id for r in rows]

    n = len(node_ids)
    if n < 2:
        if not encap:
            raise HTTP(400, T("At least two nodes should be selected"))
        else:
            return []

    sql = """
           select p.node_id, p.pkg_name, p.pkg_version, p.pkg_arch, p.pkg_type from packages p, (
             select pkg_name, pkg_version, pkg_arch, pkg_type from (
               select
                      pkg_name,
                      pkg_version,
                      pkg_arch,
                      pkg_type,
                      count(node_id) as c
               from packages
               where node_id in (%(nodes)s)
               group by pkg_name,pkg_version,pkg_arch,pkg_type
               order by pkg_name,pkg_version,pkg_arch,pkg_type
             ) as t
             where t.c!=%(n)s
           ) u
           where
             p.pkg_name=u.pkg_name and p.pkg_version=u.pkg_version and p.pkg_arch=u.pkg_arch and p.pkg_type=u.pkg_type and
             p.node_id in (%(nodes)s)
          """%dict(n=n, nodes=','.join(map(repr, node_ids)))
    rows = db.executesql(sql, as_dict=True)

    return rows


