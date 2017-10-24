@auth.requires_login()
def link():
    link_id = request.vars.link_id;

    link_div = DIV(
      SCRIPT("""$.when(osvc.app_started).then(function(){ osvc_get_link("link", "%(link_id)s")})""" % dict(link_id=link_id)),
      _id="link",
    )

    context = dict(table=link_div)
    if request.vars["pdf"]:
        return _pdf()
    return context

def _pdf():
    import uuid
    import os
    import json
    from subprocess import *
    import gluon.contenttype

    fid = str(uuid.uuid4())
    response.headers['Content-Type']=gluon.contenttype.contenttype('.pdf')
#    response.headers['Content-disposition'] = 'attachment; filename=%s.pdf' % fid
    con_d = os.path.dirname(__file__)
    fpath = con_d+"/../static/"+fid+".pdf"
    new_vars = request.vars
    del new_vars["pdf"]
    cookie = {
        "name": response.session_id_name,
        "value": response.cookies[response.session_id_name].value,
    }
    url = "https://127.0.0.1"+str(URL(f="link", args=request.args, vars=new_vars))
    cmd = ["xvfb-run", "phantomjs", "--ignore-ssl-errors=true",  "--web-security=false", con_d+"/../scripts/pdf.js", url, fpath]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = proc.communicate(input=json.dumps(cookie))
    return response.stream(open(fpath,'rb'), chunk_size=10**6)

