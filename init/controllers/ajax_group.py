@auth.requires_login()
def ajax_group():
    session.forget(response)
    t = group_tabs(role=request.vars.groupname)
    return t

