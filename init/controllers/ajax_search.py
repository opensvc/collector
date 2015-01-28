max_search_result = 10

@auth.requires_login()
def ajax_search():
    word = request.vars.search
    if word is None or len(word) == 0:
        return ''
    chars = "%&|,()"
    is_filter = False
    for char in chars:
        if char in word:
            is_filter = True
            break
    if not is_filter:
        pattern = '%'+word+'%'
    else:
        pattern = word

    svc = format_svc(pattern)
    node = format_node(pattern)
    vm = format_vm(pattern)
    user = format_user(pattern)
    group = format_group(pattern)
    app = format_app(pattern)
    disk = format_disk(pattern)

    if len(svc)+len(node)+len(user)+len(group)+len(app)+len(vm)+len(disk) == 0:
        return ''

    return DIV(
             svc,
             node,
             vm,
             user,
             group,
             app,
             disk,
           )

def format_disk(pattern):
    o = db.b_disk_app.disk_id
    q = _where(None, 'b_disk_app', pattern, 'disk_id')
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_gen_filters(q, ["b_disk_app"])
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        d = TABLE(
              TR(
                TD(
                  _class="s_disk48",
                ),
                TD(
                  P(
                    row['disk_id'],
                    _class=_class,
                  ),
                  A(
                    T('disk info'),
                    _href=URL(r=request, c='disks', f='disks',
                              vars={'disks_f_disk_id': row['disk_id'],
                                    'clear_filters': 'true'}),
                    _class="hd16",
                  ),
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'disk_id': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Disks'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d

def format_app(pattern):
    o = db.v_svcmon.svc_app
    q = _where(None, 'v_svcmon', pattern, 'svc_app')
    q = _where(q, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_gen_filters(q, ["v_svcmon"])
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if row.get("svc_app") is None:
            return SPAN()
        d = TABLE(
              TR(
                TD(
                  _class="s_svc48",
                ),
                TD(
                  P(
                    row['svc_app'].upper(),
                    _class=_class,
                  ),
                  A(
                    T('nodes'),
                    _href=URL(r=request, c='nodes', f='nodes',
                              vars={'nodes_f_project': row['svc_app'],
                                    'clear_filters': 'true'}),
                    _class="hw16",
                  ),
                  A(
                    T('status'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_svc_app': row['svc_app'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('disk info'),
                    _href=URL(r=request, c='disks', f='disks',
                              vars={'disks_f_app': row['svc_app'],
                                    'clear_filters': 'true'}),
                    _class="hd16",
                  ),
                  A(
                    T('availability'),
                    _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                              vars={'svcmon_log_f_svc_app': row['svc_app'],
                                    'clear_filters': 'true'}),
                    _class="avail16",
                  ),
                  A(
                    T('application'),
                    _href=URL(r=request, c='apps', f='apps',
                              vars={'apps_f_app': row['svc_app'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'svc_app': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Applications'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d

def format_svc(pattern):
    o = db.services.svc_name
    q = _where(None, 'services', pattern, 'svc_name')
    q = _where(q, 'services', domain_perms(), 'svc_name')
    services = filterset_encap_query(user_fset_id())[1]
    q &= db.services.svc_name.belongs(services)
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if _class == "":
            _class="meta_svcname clickable"

        d = TABLE(
              TR(
                TD(
                  _class="s_svc48",
                ),
                TD(
                  P(
                    row['svc_name'].lower(),
                    _class=_class,
                  ),
                  A(
                    T('dashboard'),
                    _href=URL(r=request, c='dashboard', f='index',
                              vars={'dashboard_f_dash_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="alert16",
                  ),
                  A(
                    T('status'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_mon_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('resources'),
                    _href=URL(r=request, c='resmon', f='resmon',
                              vars={'resmon_f_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('appinfo'),
                    _href=URL(r=request, c='appinfo', f='appinfo',
                              vars={'appinfo_f_app_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('actions'),
                    _href=URL(r=request, c='svcactions', f='svcactions',
                              vars={'actions_f_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="action16",
                  ),
                  A(
                    T('checks'),
                    _href=URL(r=request, c='checks', f='checks',
                              vars={'checks_f_chk_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="check16",
                  ),
                  A(
                    T('disks'),
                    _href=URL(r=request, c='disks', f='disks',
                              vars={'disks_f_disk_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="hd16",
                  ),
                  A(
                    T('saves'),
                    _href=URL(r=request, c='saves', f='saves',
                              vars={'saves_f_save_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="cd16",
                  ),
                  A(
                    T('compliance status'),
                    _href=URL(r=request, c='compliance', f='comp_status',
                              vars={'cs0_f_run_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="comp16",
                  ),
                  A(
                    T('compliance log'),
                    _href=URL(r=request, c='compliance', f='comp_log',
                              vars={'comp_log_f_run_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="log16",
                  ),
                  A(
                    T('availability'),
                    _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                              vars={'svcmon_log_f_svc_name': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="avail16",
                  ),
                  A(
                    T('log'),
                    _href=URL(r=request, c='log', f='log',
                              vars={'log_f_log_svcname': row['svc_name'],
                                    'clear_filters': 'true'}),
                    _class="log16",
                  ),
                ),
              ),
              TR(
                TD(
                  _name="extra",
                  _colspan=2,
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'svc_name': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Services'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d

def format_vm(pattern):
    o = db.v_svcmon.mon_vmname
    q = _where(None, 'v_svcmon', pattern, 'mon_vmname')
    q = _where(q, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_gen_filters(q, ["v_svcmon"])
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if _class == "":
            _class="meta_nodename clickable"
        d = TABLE(
              TR(
                TD(
                  _class="s_svc48",
                ),
                TD(
                  P(
                    row['mon_vmname'].lower(),
                    _class=_class,
                  ),
                  A(
                    T('status'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_mon_vmname': row['mon_vmname'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('availability'),
                    _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                              vars={'svcmon_log_f_mon_vmname': row['mon_vmname'],
                                    'clear_filters': 'true'}),
                    _class="avail16",
                  ),
                ),
              ),
              TR(
                TD(
                  _name="extra",
                  _colspan=2,
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'mon_vmname': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Virtual Machines'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d

def format_node(pattern):
    o = db.v_nodes.nodename
    q = _where(None, 'v_nodes', pattern, 'nodename')
    q = _where(q, 'v_nodes', domain_perms(), 'nodename')
    q = apply_gen_filters(q, ["v_nodes"])
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if _class == "":
            _class="meta_nodename clickable"

        d = TABLE(
              TR(
                TD(
                  _class="s_node48",
                ),
                TD(
                  P(row['nodename'].lower(), _class=_class),
                  A(
                    T('nodes'),
                    _href=URL(r=request, c='nodes', f='nodes',
                              vars={'nodes_f_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="hw16",
                  ),
                  A(
                    T('dashboard'),
                    _href=URL(r=request, c='dashboard', f='index',
                              vars={'dashboard_f_dash_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="alert16",
                  ),
                  A(
                    T('services'),
                    _href=URL(r=request, c='default', f='svcmon',
                              vars={'svcmon_f_mon_nodname': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('resources'),
                    _href=URL(r=request, c='resmon', f='resmon',
                              vars={'resmon_f_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('appinfo'),
                    _href=URL(r=request, c='appinfo', f='appinfo',
                              vars={'appinfo_f_app_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('actions'),
                    _href=URL(r=request, c='svcactions', f='svcactions',
                              vars={'actions_f_hostname': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="action16",
                  ),
                  A(
                    T('checks'),
                    _href=URL(r=request, c='checks', f='checks',
                              vars={'checks_f_chk_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="check16",
                  ),
                  A(
                    T('packages'),
                    _href=URL(r=request, c='packages', f='packages',
                              vars={'packages_f_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="pkg16",
                  ),
                  A(
                    T('network'),
                    _href=URL(r=request, c='nodenetworks', f='nodenetworks',
                              vars={'nodenetworks_f_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="net16",
                  ),
                  A(
                    T('san'),
                    _href=URL(r=request, c='nodesan', f='nodesan',
                              vars={'nodesan_f_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="net16",
                  ),
                  A(
                    T('disks'),
                    _href=URL(r=request, c='disks', f='disks',
                              vars={'disks_f_disk_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="hd16",
                  ),
                  A(
                    T('saves'),
                    _href=URL(r=request, c='saves', f='saves',
                              vars={'saves_f_save_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="cd16",
                  ),
                  A(
                    T('compliance status'),
                    _href=URL(r=request, c='compliance', f='comp_status',
                              vars={'cs0_f_run_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="comp16",
                  ),
                  A(
                    T('compliance log'),
                    _href=URL(r=request, c='compliance', f='comp_log',
                              vars={'comp_log_f_run_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="log16",
                  ),
                  A(
                    T('log'),
                    _href=URL(r=request, c='log', f='log',
                              vars={'log_f_log_nodename': row['nodename'],
                                    'clear_filters': 'true'}),
                    _class="log16",
                  ),
                ),
              ),
              TR(
                TD(
                  _name="extra",
                  _colspan=2,
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'nodename': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Nodes'), ' (', n, ')',
          SPAN(l),
          _class="menu_section"
        )
    return d

def format_user(pattern):
    o = db.v_users.fullname
    q = _where(None, 'v_users', pattern, 'fullname')
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if _class == "":
            _class="meta_username clickable"

        d = TABLE(
              TR(
                TD(
                  _class="s_guy48",
                ),
                TD(
                  P(row['fullname'], _class=_class),
                  A(
                    T('user'),
                    _href=URL(r=request, c='users', f='users',
                              vars={'users_f_fullname': row['fullname'],
                                    'clear_filters': 'true'}),
                    _class="guy16",
                  ),
                  A(
                    T('logs'),
                    _href=URL(r=request, c='log', f='log',
                              vars={'log_f_log_user': row['fullname'],
                                    'clear_filters': 'true'}),
                    _class="log16",
                  ),
                  A(
                    T('apps'),
                    _href=URL(r=request, c='apps', f='apps',
                              vars={'apps_f_responsibles': '%'+row['fullname']+'%',
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                ),
              ),
              TR(
                TD(
                  _name="extra",
                  _colspan=2,
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'fullname': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Users'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d

def format_group(pattern):
    o = db.auth_group.role
    q = _where(None, 'auth_group', pattern, 'role')
    rows = db(q).select(o, orderby=o, groupby=o, limitby=(0,max_search_result))
    n = len(db(q).select(o, groupby=o))

    if len(rows) == 0:
        return ''

    def format_row(row, _class=""):
        if _class == "":
            _class="meta_groupname clickable"

        d = TABLE(
              TR(
                TD(
                  _class="s_guys48",
                ),
                TD(
                  P(row['role'], _class=_class),
                  A(
                    T('nodes'),
                    _href=URL(r=request, c='nodes', f='nodes',
                              vars={'nodes_f_team_responsible': row['role'],
                                    'clear_filters': 'true'}),
                    _class="hw16",
                  ),
                  A(
                    T('apps'),
                    _href=URL(r=request, c='apps', f='apps',
                              vars={'apps_f_roles': '%'+row['role']+'%',
                                    'clear_filters': 'true'}),
                    _class="svc",
                  ),
                  A(
                    T('checks'),
                    _href=URL(r=request, c='checks', f='checks',
                              vars={'checks_f_team_responsible': row['role'],
                                    'clear_filters': 'true'}),
                    _class="check16",
                  ),
                  A(
                    T('compliance status'),
                    _href=URL(r=request, c='compliance', f='comp_status',
                              vars={'cs0_f_team_responsible': row['role'],
                                    'clear_filters': 'true'}),
                    _class="comp16",
                  ),
                ),
              ),
              TR(
                TD(
                  _name="extra",
                  _colspan=2,
                ),
              ),
            )
        return d
    l = []
    if n > 1:
        l.append(format_row({'role': pattern}, "highlight_light"))
    for row in rows:
        l.append(format_row(row))
    d = DIV(
          T('Groups'), ' (', n, ')',
          SPAN(l),
          _class="menu_section",
        )
    return d


