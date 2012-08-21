@auth.requires_login()
def svc_pkgdiff():
    svcname = request.args[0]
    rows = db(db.svcmon.mon_svcname==svcname).select(db.svcmon.mon_nodname)
    nodes = [row.mon_nodname for row in rows]
    return _ajax_pkgdiff(nodes)

@auth.requires_login()
def ajax_pkgdiff():
    nodes = set(request.vars.node.split(','))
    nodes -= set([""])
    return _ajax_pkgdiff(nodes)

def _ajax_pkgdiff(nodes):
    n = len(nodes)

    if n == 0:
         return DIV(T("No nodes selected"))

    if list(nodes)[0][0] in "0123456789":
        # received node ids
        nodes = [r.nodename for r in db(db.nodes.id.belongs(nodes)).select(db.nodes.nodename)]

    sql = """select * from (
               select group_concat(pkg_nodename order by pkg_nodename),
                      pkg_name,
                      pkg_version,
                      pkg_arch,
                      count(pkg_nodename) as c
               from packages
               where pkg_nodename in (%(nodes)s)
               group by pkg_name,pkg_version,pkg_arch
               order by pkg_name,pkg_version,pkg_arch
             ) as t
             where t.c!=%(n)s;
          """%dict(n=n, nodes=','.join(map(repr, nodes)))
    rows = db.executesql(sql)

    def fmt_header():
        return TR(
                 TH(T("Node")),
                 TH(T("Package")),
                 TH(T("Version")),
                 TH(T("Arch")),
               )

    def fmt_line(row):
        return TR(
                 TD(row[0]),
                 TD(row[1]),
                 TD(row[2]),
                 TD(row[3]),
               )

    def fmt_table(rows):
        return TABLE(
                 fmt_header(),
                 map(fmt_line, rows),
               )

    return DIV(fmt_table(rows))


