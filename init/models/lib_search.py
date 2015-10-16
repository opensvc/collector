max_search_result = 10

def lib_search_fset(pattern):
    o = db.gen_filtersets.fset_name
    q = _where(None, 'gen_filtersets', pattern, 'fset_name')
    return db(q).select(db.gen_filtersets.id,
                        o,
                        orderby=o,
                        limitby=(0,max_search_result)
    ).as_list()

def lib_search_disk(pattern):
    o = db.b_disk_app.disk_id
    q = _where(None, 'b_disk_app', pattern, 'disk_id')
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_gen_filters(q, ["b_disk_app"])
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result)
    ).as_list()

def lib_search_app(pattern):
    o = db.nodes.project
    q = _where(None, 'nodes', pattern, 'project')
    q = _where(q, 'nodes', domain_perms(), 'nodename')
    rows = db(q).select(o, groupby=o, limitby=(0,max_search_result))
    apps = set([r.project for r in rows])

    o = db.services.svc_app
    q = _where(None, 'services', pattern, 'svc_app')
    q = _where(q, 'services', domain_perms(), 'svc_name')
    rows = db(q).select(o, groupby=o, limitby=(0,max_search_result))
    apps |= set([r.svc_app for r in rows])

    apps = sorted(list(apps))[:max_search_result]
    data = [ {"app": app} for app in apps ]
    return data

def lib_search_service(pattern):
    o = db.services.svc_name
    q = _where(None, 'services', pattern, 'svc_name')
    q = _where(q, 'services', domain_perms(), 'svc_name')
    services = filterset_encap_query(user_fset_id())[1]
    q &= db.services.svc_name.belongs(services)
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

def lib_search_vm(pattern):
    o = db.v_svcmon.mon_vmname
    q = _where(None, 'v_svcmon', pattern, 'mon_vmname')
    q = _where(q, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_gen_filters(q, ["v_svcmon"])
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

def lib_search_ip(pattern):
    o = db.node_ip.addr
    q = _where(None, 'node_ip', pattern, 'addr')
    q = _where(q, 'node_ip', domain_perms(), 'nodename')
    q &= db.node_ip.nodename.belongs(current_fset_nodenames())
    return db(q).select(o,
                        db.node_ip.nodename,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()


def lib_search_node(pattern):
    o = db.v_nodes.nodename
    q = _where(None, 'v_nodes', pattern, 'nodename')
    q = _where(q, 'v_nodes', domain_perms(), 'nodename')
    q = apply_gen_filters(q, ["v_nodes"])
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

def lib_search_user(pattern):
    o = db.v_users.fullname
    q = _where(None, 'v_users', pattern, 'fullname')
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

def lib_search_group(pattern):
    o = db.auth_group.role
    q = db.auth_group.privilege == 'F'
    q &= ~db.auth_group.role.like("user_%")
    q = _where(q, 'auth_group', pattern, 'role')
    return db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

def lib_search_safe_file(pattern):
    o = db.safe.uuid
    q = db.safe.uuid.like(pattern) | db.safe.name.like(pattern)
    q &= db.safe.id == db.safe_team_publication.file_id
    q &= db.safe_team_publication.group_id.belongs(user_group_ids()) | \
         (db.safe.uploader == auth.user_id)
    return db(q).select(o,
                        db.safe.name,
                        orderby=o,
                        groupby=o,
                        limitby=(0,max_search_result),
    ).as_list()

