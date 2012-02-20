def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def index():
    redirect(URL(r=request, f='alerts'))

@auth.requires_login()
def nav():
    return dict()

@auth.requires_login()
def alerts():
    return dict()

@auth.requires_login()
def node():
    return dict(nodename=request.args[0])

@auth.requires_login()
def svc():
    return dict(svcname=request.args[0])

@service.json
def json_node(nodename):
    q = db.nodes.nodename == nodename
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    row = db(q).select(
            db.nodes.warranty_end,
            db.nodes.status,
            db.nodes.role,
            db.nodes.environnement,
            db.nodes.mem_bytes,
            db.nodes.mem_banks,
            db.nodes.mem_slots,
            db.nodes.os_vendor,
            db.nodes.os_name,
            db.nodes.os_kernel,
            db.nodes.os_release,
            db.nodes.os_arch,
            db.nodes.cpu_freq,
            db.nodes.cpu_dies,
            db.nodes.cpu_cores,
            db.nodes.cpu_model,
            db.nodes.cpu_vendor,
            db.nodes.type,
            db.nodes.nodename,
            db.nodes.team_responsible,
            db.nodes.team_integ,
            db.nodes.team_support,
            db.nodes.project,
            db.nodes.serial,
            db.nodes.model,
            db.nodes.loc_addr,
            db.nodes.loc_city,
            db.nodes.loc_zip,
            db.nodes.loc_rack,
            db.nodes.loc_floor,
            db.nodes.loc_country,
            db.nodes.loc_building,
            db.nodes.loc_room,
            db.nodes.power_supply_nb,
            db.nodes.power_cabinet1,
            db.nodes.power_cabinet2,
            db.nodes.power_protect,
            db.nodes.power_protect_breaker,
            db.nodes.power_breaker1,
            db.nodes.power_breaker2,
            db.nodes.updated,
          ).first()
    return row

@service.json
def json_service(svcname):
    q = db.services.svc_name == svcname
    q &= _where(None, 'services', domain_perms(), 'svc_name')
    row = db(q).select(
            db.services.svc_availstatus,
            db.services.svc_status,
            db.services.svc_type,
            db.services.svc_app,
            db.services.svc_created,
            db.services.svc_comment,
            db.services.svc_containertype,
            db.services.svc_envfile,
            db.services.svc_vmname,
            db.services.updated,
            db.services.svc_vcpus,
            db.services.svc_vmem,
            db.services.svc_guestos,
            db.services.svc_cluster_type,
            db.services.svc_flex_min_nodes,
            db.services.svc_flex_max_nodes,
            db.services.svc_flex_cpu_low_threshold,
            db.services.svc_flex_cpu_high_threshold,
            db.services.svc_ha,
          ).first()
    return row

@service.json
def json_service_resstatus(svcname):
    o = db.svcmon.mon_nodname
    q = db.svcmon.mon_svcname == svcname
    q &= _where(None, 'svcmon', domain_perms(), 'mon_svcname')
    rows = db(q).select(o, orderby=o)
    h = {}
    for row in rows:
        q = db.resmon.nodename == row.mon_nodname
        q &= db.resmon.svcname == svcname
        res = db(q).select()
        h[row.mon_nodname] = res
    return h

@auth.requires_login()
def services():
    return dict()

@service.json
def json_services():
    start = 0
    end = 20
    q = db.services.id > 0
    q &= _where(None, 'services', domain_perms(), 'svc_name')
    q = apply_filters(q, None, db.services.svc_name)
    rows = db(q).select(db.services.svc_name, limitby=(start, end))
    l = map(lambda x: x.svc_name, rows)
    return l

@service.json
def json_alerts(start, end, s):
    start = int(start)
    end = int(end)
    o = ~db.dashboard.dash_severity
    q = db.dashboard.id > 0
    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= (db.dashboard.dash_dict.like(s) | \
              db.dashboard.dash_fmt.like(s) | \
              db.dashboard.dash_svcname.like(s) | \
              db.dashboard.dash_nodename.like(s) | \
              db.dashboard.dash_type.like(s))
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)

    rows = db(q).select(orderby=o,
                        limitby=(start, end))

    l = []
    for row in rows:
        if len(row.dash_dict) > 0 and len(row.dash_fmt) > 0:
            try:
                d = json.loads(row.dash_dict)
                body = row.dash_fmt % d
            except:
                body = "alert body corrupted"
        else:
            body = ""
        h = {'body': body}
        for field in row:
            if field in ('update_record', 'delete_record'):
                continue
            h[field] = row[field]
        l.append(h)
    return l

@service.json
def json_filters():
    o = db.gen_filtersets.fset_name
    q = db.gen_filtersets.id > 0
    rows = db(q).select(orderby=o)

    q = db.auth_user.id == auth.user_id
    q &= db.gen_filterset_user.user_id == db.auth_user.id
    row = db(q).select(db.gen_filterset_user.fset_id).first()
    if row is None:
        fset_id = None
    else:
        fset_id = row.fset_id
    return fset_id, rows

@service.json
def json_set_filter(fset_id):
    q = db.gen_filterset_user.user_id == auth.user_id
    if fset_id == "0":
        db(q).delete()
    else:
        n = db(q).count()
        if n > 1:
            db(q).delete()
            n = 0
        if n == 1:
            db(q).update(fset_id=fset_id)
        elif n == 0:
            db.gen_filterset_user.insert(user_id=auth.user_id, fset_id=fset_id)
    return 0

