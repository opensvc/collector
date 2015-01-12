@auth.requires_login()
def ajax_svcdiff():
    svcs = set(request.vars.node.split(','))
    svcs -= set([""])
    l = []
    l.append(link("/init/nodediff/svc_diff", request.vars.node))
    l.append(H2(T("Service differences")))
    l.append(SPAN(svcdiff(svcs)))
    #l.append(H2(T("Package differences")))
    #l.append(SPAN(ajax_pkgdiff()))
    l.append(H2(T("Compliance differences")))
    l.append(SPAN(ajax_services_compdiff()))

    return SPAN(l)

def link(url, name):
    link = DIV(
      DIV(
        _class="hidden",
      ),
      _onclick="""
        url = $(location).attr("origin")
        url += "%(url)s?node=%(name)s"
        $(this).children().html(url)
        $(this).children().show()
      """ % dict(url=url, name=name),
      _style="float:right",
      _class="link16 clickable",
    )
    return link

@auth.requires_login()
def ajax_nodediff():
    nodes = set(request.vars.node.split(','))
    nodes -= set([""])
    l = []
    l.append(link("/init/nodediff/node_diff", request.vars.node))
    l.append(H2(T("Asset differences")))
    l.append(SPAN(nodediff(nodes)))
    l.append(H2(T("Package differences")))
    l.append(SPAN(ajax_pkgdiff()))
    l.append(H2(T("Compliance differences")))
    l.append(SPAN(ajax_compdiff()))

    return SPAN(l)

def compare(nodes, rows, cols, colprops, objtype):
    def _label(key, colprops):
        return DIV(
                 IMG(
                   _src=URL(r=request, c='static',
                            f=colprops[key].img+'.png'),
                   _style='vertical-align:top;margin-right:10px',
                 ),
                 colprops[key].title,
               )

    def fmt_header1(n):
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2(nodes):
        h = [TH(T("Field"))]
        for node in nodes:
            h.append(TH(
              node.split('.')[0],
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(nodes, col, colprops, rows, bg):
        h = [TD(_label(col, colprops))]
        ref = None
        diff = False
        for i, node in enumerate(nodes):
            row = rows[i]
            val = row[col]
            if ref is None:
                ref = val
            elif ref != val:
                diff = True
            h.append(TD(row[col]))
        if not diff:
            return
        return TR(h, _class=bg)

    last = ""
    bgl = {'cell1': 'cell3', 'cell3': 'cell1'}
    bg = "cell1"
    lines = [fmt_header1(len(nodes)),
             fmt_header2(nodes)]
    for col in cols:
        line = fmt_line(nodes, col, colprops, rows, bg)
        if line is not None:
            bg = bgl[bg]
            lines.append(line)
    return TABLE(lines)

def svcdiff(svcs):
    q = db.v_services.svc_name.belongs(svcs)
    rows = db(q).select()
    svcs = [r.svc_name for r in rows]
    cols = v_services_cols
    cols.remove('svc_updated')
    return compare(svcs, rows, v_services_cols, v_services_colprops, "Services")

def nodediff(nodes):
    q = db.v_nodes.nodename.belongs(nodes)
    rows = db(q).select()
    nodes = [ r.nodename for r in rows]
    return compare(nodes, rows, v_nodes_cols, v_nodes_colprops, "Nodes")

def ajax_services_compdiff():
    divid = "svcdiff_compdiff"
    d = DIV(
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id=divid
          ),
          SCRIPT("""sync_ajax('%(url)s?node=%(nodes)s', [], '%(div)s', function(){});"""%dict(
              url=URL(r=request,c='compliance',f='ajax_compliance_svcdiff'),
              div=divid,
              nodes=request.vars.node,
            ),
          ),
        )
    return d

def ajax_compdiff():
    divid = "nodediff_compdiff"
    d = DIV(
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id=divid
          ),
          SCRIPT("""sync_ajax('%(url)s?node=%(nodes)s', [], '%(div)s', function(){});"""%dict(
              url=URL(r=request,c='compliance',f='ajax_compliance_nodediff'),
              div=divid,
              nodes=request.vars.node,
            ),
          ),
        )
    return d

def ajax_pkgdiff():
    divid = "nodediff_pkgdiff"
    d = DIV(
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id=divid
          ),
          SCRIPT("""sync_ajax('%(url)s?node=%(nodes)s', [], '%(div)s', function(){});"""%dict(
              url=URL(r=request,c='pkgdiff',f='ajax_pkgdiff'),
              div=divid,
              nodes=request.vars.node,
            ),
          ),
        )
    return d

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
    if len(rows) == 0:
        return

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

def svc_diff():
    return dict(table=ajax_svcdiff())

def node_diff():
    return dict(table=ajax_nodediff())
