@auth.requires_login()
def link():
    options = dict()
    for v in request.vars:
        options[v] = request.vars[v]

    link_id = request.vars.link_id;

    if request.vars['js'] == 'true':
        function = request.vars.fn;
        link_div = DIV(
            SCRIPT("""%(fn)s("link", %(opt)s) """ % dict(fn=link_id,opt=str(options))),
          _id="link",
          _style="text-align:left",
            )
        return dict(table=link_div)
    else:
        link_div = DIV(
            SCRIPT("""link("link", %s) """ % str(options)),
          _id="link",
            )
        return dict(table=link_div)