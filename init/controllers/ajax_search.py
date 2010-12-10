max_search_result = 10

@auth.requires_login()
def ajax_search():
    word = request.vars.search
    if word is None or len(word) == 0:
        return ''
    pattern = '%'+word+'%'

    svc = format_svc(pattern)
    node = format_node(pattern)
    user = format_user(pattern)
    app = format_app(pattern)

    if len(svc)+len(node)+len(user)+len(app) == 0:
        return ''

    return DIV(
             svc,
             node,
             user,
             app,
           )

def format_app(pattern):
    o = db.apps.app
    q = o.like(pattern)
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row):
        d = TABLE(
              TR(
                TD(
                  IMG(_src=URL(r=request, c='static', f='svc.png')),
                ),
                TD(
                  P(
                    row.app
                  ),
                  A(
                    T('status'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_svc_app': row.app})
                  ),
                  A(
                    T('availability'),
                    _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                              vars={'svcmon_log_f_svc_app': row.app})
                  ),
                  A(
                    T('application'),
                    _href=URL(r=request, c='apps', f='apps',
                              vars={'apps_f_app': row.app})
                  ),
                ),
              ),
            )
        return d
    d = [H3(T('Applications'), ' (', n, ')')]
    for row in rows:
        d.append(format_row(row))
    return DIV(*d)

def format_svc(pattern):
    o = db.svcmon.mon_svcname
    q = o.like(pattern)
    q = _where(q, 'svcmon', domain_perms(), 'mon_svcname')
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row):
        d = TABLE(
              TR(
                TD(
                  IMG(_src=URL(r=request, c='static', f='svc.png')),
                ),
                TD(
                  P(
                    row.mon_svcname
                  ),
                  A(
                    T('status'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_svc_name': row.mon_svcname})
                  ),
                  A(
                    T('actions'),
                    _href=URL(r=request, c='svcactions', f='svcactions',
                              vars={'actions_f_svcname': row.mon_svcname})
                  ),
                  A(
                    T('availability'),
                    _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                              vars={'svcmon_log_f_mon_svcname': row.mon_svcname})
                  ),
                  A(
                    T('checks'),
                    _href=URL(r=request, c='checks', f='checks',
                              vars={'checks_f_chk_svcname': row.mon_svcname})
                  ),
                ),
              ),
            )
        return d
    d = [H3(T('Services'), ' (', n, ')')]
    for row in rows:
        d.append(format_row(row))
    return DIV(*d)

def format_node(pattern):
    o = db.nodes.nodename
    q = o.like(pattern)
    q = _where(q, 'nodes', domain_perms(), 'nodename')
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row):
        d = TABLE(
              TR(
                TD(
                  IMG(_src=URL(r=request, c='static', f='node16.png')),
                ),
                TD(
                  P(row.nodename),
                  A(
                    T('asset'),
                    _href=URL(r=request, c='nodes', f='nodes',
                              vars={'nodes_f_nodename': row.nodename})
                  ),
                  A(
                    T('actions'),
                    _href=URL(r=request, c='svcactions', f='svcactions',
                              vars={'actions_f_hostname': row.nodename})
                  ),
                  A(
                    T('services'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_mon_nodname': row.nodename})
                  ),
                  A(
                    T('checks'),
                    _href=URL(r=request, c='checks', f='checks',
                              vars={'checks_f_chk_nodename': row.nodename})
                  ),
                  A(
                    T('compliance status'),
                    _href=URL(r=request, c='compliance', f='comp_status',
                              vars={'0_f_run_nodename': row.nodename})
                  ),
                  A(
                    T('compliance log'),
                    _href=URL(r=request, c='compliance', f='comp_log',
                              vars={'ajax_comp_log_f_run_nodename': row.nodename})
                  ),
                ),
              ),
            )
        return d
    d = [H3(T('Nodes'), ' (', n, ')')]
    for row in rows:
        d.append(format_row(row))
    return DIV(*d)

def format_user(pattern):
    o = db.v_users.fullname
    q = o.like(pattern)
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row):
        d = TABLE(
              TR(
                TD(
                  IMG(_src=URL(r=request, c='static', f='guy16.png')),
                ),
                TD(
                  P(row.fullname),
                  A(
                    T('user'),
                    _href=URL(r=request, c='users', f='users',
                              vars={'users_f_fullname': row.fullname})
                  ),
                  A(
                    T('logs'),
                    _href=URL(r=request, c='log', f='log',
                              vars={'log_f_log_user': row.fullname})
                  ),
                  A(
                    T('apps'),
                    _href=URL(r=request, c='apps', f='apps',
                              vars={'apps_f_responsibles': '%'+row.fullname+'%'})
                  ),
                ),
              ),
            )
        return d
    d = [H3(T('Users'), ' (', n, ')')]
    for row in rows:
        d.append(format_row(row))
    return DIV(*d)


