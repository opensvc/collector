@auth.requires_login()
def link():
    link_id = request.vars.link_id;

    link_div = DIV(
      SCRIPT("""$.when(osvc.app_started).then(function(){ osvc_get_link("link", "%(link_id)s")})""" % dict(link_id=link_id)),
      _id="link",
    )

    return dict(table=link_div)
