def lib_packages_diff(nodenames=[], svcnames=[], encap=False):
    if len(svcnames) > 0:
        if encap:
            q = db.svcmon.mon_svcname.belongs(svcnames)
            q = q_filter(q, svc_field=db.svcmon.mon_svcname)
            rows = db(q).select(db.svcmon.mon_vmname,
                                groupby=db.svcmon.mon_vmname)
            nodenames = [row.mon_vmname for row in rows if row.mon_vmname != "" and row.mon_vmname is not None]
        else:
            q = db.svcmon.mon_svcname.belongs(svcnames)
            q = q_filter(q, svc_field=db.svcmon.mon_svcname)
            rows = db(q).select(db.svcmon.mon_nodname)
            nodenames += [r.mon_nodname for r in rows]

    nodenames = list(set(nodenames) - set(['']))
    n = len(nodenames)
    if n < 2:
        if not encap:
            raise Exception(T("At least two nodes should be selected"))
        else:
            return []

    if list(nodenames)[0][0] in "0123456789":
        # received node ids
        q = db.nodes.id.belongs(nodenames)
        q = q_filter(q, app_field=db.nodes.app)
        rows = db(q).select(db.nodes.nodename)
        nodenames = [r.nodename for r in rows]
    else:
        # apply domain filtering
        q = db.nodes.nodename.belongs(nodenames)
        q = q_filter(q, app_field=db.nodes.app)
        rows = db(q).select(db.nodes.nodename)
        nodenames = [r.nodename for r in rows]

    nodenames = list(set(nodenames) - set(['']))
    n = len(nodenames)
    if n < 2:
        raise Exception(T("At least two nodes should be selected"))

    sql = """
           select p.pkg_nodename, p.pkg_name, p.pkg_version, p.pkg_arch, p.pkg_type from packages p, (
             select pkg_name, pkg_version, pkg_arch, pkg_type from (
               select
                      pkg_name,
                      pkg_version,
                      pkg_arch,
                      pkg_type,
                      count(pkg_nodename) as c
               from packages
               where pkg_nodename in (%(nodes)s)
               group by pkg_name,pkg_version,pkg_arch,pkg_type
               order by pkg_name,pkg_version,pkg_arch,pkg_type
             ) as t
             where t.c!=%(n)s
           ) u
           where
             p.pkg_name=u.pkg_name and p.pkg_version=u.pkg_version and p.pkg_arch=u.pkg_arch and p.pkg_type=u.pkg_type and
             p.pkg_nodename in (%(nodes)s)
          """%dict(n=n, nodes=','.join(map(repr, nodenames)))
    rows = db.executesql(sql, as_dict=True)

    return rows


