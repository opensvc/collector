def call():
    session.forget()
    return service()

@service.xmlrpc
@auth.requires_membership('ReplicationManager')
def relay_rest_request(user_id, action, path, data):
    auth.impersonate(user_id=user_id)
    handler = get_handler(action, path)
    args, vars = data
    return handler.handle(*args, **vars)

class rest_get_api(rest_get_handler):
    def __init__(self):
        desc = [
          "List the api available handlers."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api"
        ]

        rest_get_handler.__init__(
          self,
          path="/",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        data = {}
        for a in ("GET", "POST", "DELETE", "PUT"):
            data[a] = []
            for handler in get_handlers(a):
                handler.update_parameters()
                handler.update_data()
                if type(handler.data) == dict:
                    hdata = handler.data
                else:
                    hdata = {}
                data[a].append({
                  "path": handler.path,
                  "pattern": handler.get_pattern(),
                  "data": hdata,
                  "params": handler.params,
                  "examples": handler.examples,
                  "desc": handler.desc,
                })
        return dict(data=data)

def rest_router(action, args, vars):
    # the default restful wrapper suppress the trailing .xxx
    # we need it for fqdn nodenames and svcname though.
    request.raw_args = request.raw_args.replace("(percent)", "%")
    args = request.raw_args.split('/')
    for i, arg in enumerate(args):
        args[i] = arg.replace("(slash)", "/")
    if args[0] == "":
        return rest_get_api().handle(*args, **vars)
    try:
        candidate_handlers = get_handlers(action, args[0])
    except KeyError:
        return dict(error="Unsupported api url: %s /%s" % (action, str(request.raw_args)))

    try:
        for handler in candidate_handlers:
            if handler.match("/"+request.raw_args):
                return handler.handle(*args, **vars)
    except CompInfo as exc:
        return dict(info=str(exc))
    except CompError as exc:
        return dict(error=str(exc))
    except HTTP as exc:
        response.status = exc.status
        return dict(ret=exc.status, error=exc.body)
    except:
        import sys
        import traceback
        e = sys.exc_info()
        if e[0] in (Exception, KeyError):
            err = str(e[1])
        else:
            err = traceback.format_exc()
        response.status = 500
        return dict(error=err)
    response.status = 404
    return dict(error="Unsupported api url: %s /%s" % (action, str(request.raw_args)))


@request.restful()
@auth.requires_login()
def api():
    def GET(*args, **vars):
        return rest_router("GET", args, vars)
    def POST(*args, **vars):
        return rest_router("POST", args, vars)
    def PUT(*args, **vars):
        return rest_router("PUT", args, vars)
    def DELETE(*args, **vars):
        return rest_router("DELETE", args, vars)
    return locals()

def doc():
    # the default restful wrapper suppress the trailing .xxx
    # we need it for fqdn nodenames and svcname though.
    args = request.raw_args.split('/')

    d = DIV(
          SCRIPT("""
            $.when(osvc.app_started).then(function(){
              api_doc("api_doc", {args: %(args)s})
            })
          """ % dict(args=str(args))),
          _id="api_doc",
        )
    return dict(doc=d)

def doc_load():
    return doc()["doc"]

def task_rq_async():
    task_rq("osvc:q:async", None)

def task_rq_form_submit():
    task_rq("osvc:q:form_submit", lambda q: _form_submit)

