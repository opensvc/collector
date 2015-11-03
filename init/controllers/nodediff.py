@auth.requires_login()
def ajax_svcdiff():
    svcs = set(request.vars.node.split(','))
    svcs -= set([""])
    l = []
    l.append(link("/init/nodediff/svc_diff", request.vars.node))
    l.append(H2(T("Service differences")))
    l.append(SPAN(svcdiff(svcs)))
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
                            f='images/'+colprops[key].img+'.png'),
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
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
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
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
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
            _id=divid
          ),
          SCRIPT("""pkgdiff('%(div)s', %(options)s);"""%dict(
              div=divid,
              options=str({"nodenames": request.vars.node}),
            ),
          ),
        )
    return d

def svc_diff():
    return dict(table=ajax_svcdiff())

def node_diff():
    return dict(table=ajax_nodediff())
