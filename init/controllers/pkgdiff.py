@auth.requires_login()
def ajax_pkgdiff():
    nodes = set(request.vars.node.split(','))
    nodes -= set([""])
    n = len(nodes)

    if n == 0:
         return DIV(T("No nodes selected"))

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


