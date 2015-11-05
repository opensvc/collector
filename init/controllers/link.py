@auth.requires_login()
def link():
    options = dict()
    for v in request.vars:
        options[v] = request.vars[v]

    link_id = request.vars.link_id;

    if request.vars['js'] == 'true':
        link_div = DIV(
            SCRIPT("""osvc_get_link("link", "%(link_id)s");""" % dict(link_id=link_id)),
          _id="link",
          _style="text-align:left",
            )
        return dict(table=link_div)
    else:
        link_div = DIV(
            SCRIPT(_src="/init/static/js/jquery.min.js"),
            SCRIPT(_src="/init/static/js/osvc/osvc-common.js"),
            SCRIPT("""link("link", %s) """ % str(options)),
          _id="link",
            )
        return link_div