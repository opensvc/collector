@auth.requires_login()
def sysrep():
    d = DIV(
      _sysrep(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

def _sysrep():
    nodes = request.vars.nodes
    path = request.vars.path if request.vars.path else ""
    begin = request.vars.begin if request.vars.begin else ""
    end = request.vars.end if request.vars.end else ""
    cid = request.vars.cid if request.vars.cid else ""
    d = DIV(
      SCRIPT("""sysrep("sysreport_simple", "%(nodes)s", "%(path)s", "%(begin)s", "%(end)s", "%(cid)s") """ %
                dict(nodes=nodes, path=path, begin=begin, end=end, cid=cid)),
      _id="sysreport_simple",
    )
    return d

@auth.requires_login()
def sysrepdiff():
    d = DIV(
      _sysrepdiff(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

def _sysrepdiff():
    nodes = request.vars.nodes
    path = request.vars.path if request.vars.path else ""
    ignore_blanks = request.vars.ignore_blanks if request.vars.ignore_blanks else ""
    d = DIV(
      SCRIPT("""sysrepdiff("sysreport_simple", "%(nodes)s", "%(path)s", "%(ignore_blanks)s") """ %
                dict(nodes=nodes, path=path, ignore_blanks=ignore_blanks)),
      _id="sysreport_simple",
    )
    return d

