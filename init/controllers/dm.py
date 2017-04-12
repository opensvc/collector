@auth.requires_login()
def index():
    fn = request.args[0]
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){%s("layout")})""" % fn,
        )
    return dict(table=t)

def index_load():
    return index()["table"]

