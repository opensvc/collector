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

    nodes = list(set(nodes) - set(['']))
    nodes.sort()

    sql = """select * from (
               select group_concat(pkg_nodename order by pkg_nodename),
                      pkg_name,
                      pkg_version,
                      pkg_arch,
                      count(pkg_nodename) as c
               from packages
               where pkg_nodename in (%(nodes)s)
               group by pkg_name,pkg_version,pkg_arch,pkg_type
               order by pkg_name,pkg_version,pkg_arch,pkg_type
             ) as t
             where t.c!=%(n)s
          """%dict(n=n, nodes=','.join(map(repr, nodes)))
    rows = db.executesql(sql)

    def fmt_header1():
        return TR(
                 TH("", _colspan=3),
                 TH(T("Nodes"), _colspan=n, _style="text-align:center"),
               )
    def fmt_header2():
        h = [TH(T("Package")),
             TH(T("Version")),
             TH(T("Arch"))]
        for node in nodes:
            h.append(TH(
              node.split('.')[0],
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(row, bg):
        h = [TD(row[1]),
             TD(row[2]),
             TD(row[3])]
        l = row[0].split(',')
        for node in nodes:
            if node in l:
                h.append(TD(
                  IMG(_src=URL(r=request,c='static',f='check16.png')),
                  _style="text-align:center",
                ))
            else:
                h.append(TD(""))
                #h.append(TD(IMG( _src=URL(r=request,c='static',f='na.png'))))
        return TR(h, _class=bg)

    def fmt_table(rows):
        last = ""
        bgl = {'cell1': 'cell3', 'cell3': 'cell1'}
        bg = "cell1"
        lines = [fmt_header1(),
                 fmt_header2()]
        for row in rows:
            if last != row[1]:
                bg = bgl[bg]
                last = row[1]
            lines.append(fmt_line(row, bg))
        return TABLE(lines)

    return DIV(fmt_table(rows))


