@auth.requires_login()
def sysrep():
    d = DIV(
      _sysrep(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

def _sysrep():
    options = dict(
      nodes = request.vars.nodes,
      path = request.vars.path if request.vars.path else "",
      begin = request.vars.begin if request.vars.begin else "",
      end = request.vars.end if request.vars.end else "",
      cid = request.vars.cid if request.vars.cid else "",
    )
    d = DIV(
      SCRIPT("""sysrep("sysreport_simple", %s) """ % str(options)),
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
    options = dict(
      nodes = request.vars.nodes,
      path = request.vars.path if request.vars.path else "",
      ignore_blanks = request.vars.ignore_blanks if request.vars.ignore_blanks else "",
    )
    d = DIV(
      SCRIPT("""sysrepdiff("sysreport_simple", %s) """ % str(options)),
      _id="sysreport_simple",
    )
    return d

