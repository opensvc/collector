def lib_packages_diff(nodenames=[], svcnames=[], encap=False):
    if len(svcnames) > 0:
        if encap:
            q = db.svcmon.mon_svcname.belongs(svcnames)
            q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
            rows = db(q).select(db.svcmon.mon_vmname,
                                groupby=db.svcmon.mon_vmname)
            nodenames = [row.mon_vmname for row in rows if row.mon_vmname != "" and row.mon_vmname is not None]
        else:
            q = db.svcmon.mon_svcname.belongs(svcnames)
            q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
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
        q &= _where(None, 'nodes', domain_perms(), 'nodename')
        rows = db(q).select(db.nodes.nodename)
        nodenames = [r.nodename for r in rows]
    else:
        # apply domain filtering
        q = db.nodes.nodename.belongs(nodenames)
        q &= _where(None, 'nodes', domain_perms(), 'nodename')
        rows = db(q).select(db.nodes.nodename)
        nodenames = [r.nodename for r in rows]

    nodenames = list(set(nodenames) - set(['']))
    n = len(nodenames)
    if n < 2:
        raise Exception(T("At least two nodes should be selected"))

    sql = """select pkg_nodename, pkg_name, pkg_version, pkg_arch, pkg_type from (
               select
                      pkg_nodename,
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
          """%dict(n=n, nodes=','.join(map(repr, nodenames)))
    rows = db.executesql(sql, as_dict=True)

    return rows


