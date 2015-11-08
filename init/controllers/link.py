@auth.requires_login()
def link():
    link_id = request.vars.link_id;

    link_div = DIV(
      SCRIPT("""osvc_get_link("link", "%(link_id)s");""" % dict(link_id=link_id)),
      _id="link",
      _style="text-align:left",
    )

    return dict(table=link_div)
