@auth.requires_login()
def tabs():
    if request.vars.otype:
        otype = request.vars.otype
        oid = request.vars.oid
    elif len(request.args) > 1:
        otype = request.args[0]
        oid = request.args[1]
    else:
        return dict(table=DIV())
    area = DIV(
      SCRIPT("""$.when(osvc.app_started).then(function(){ osvc_show_tabs("area", "%(otype)s", "%(oid)s")})""" % dict(
          otype=otype,
          oid=oid,
      )),
      _id="area",
    )

    return dict(table=area)
