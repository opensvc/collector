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
def actions():
    return dict()

@auth.requires_login()
def stats():
    return dict()

@auth.requires_login()
def log():
    return dict()

@auth.requires_login()
def node():
    return dict(nodename=request.args[0])

@auth.requires_login()
def svc():
    return dict(svcname=request.args[0])

@auth.requires_login()
def show_action():
    return dict(action_id=request.args[0])

@service.json
def json_node(nodename):
    q = db.nodes.nodename == nodename
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    row = db(q).select(
            db.nodes.warranty_end,
            db.nodes.status,
            db.nodes.role,
            db.nodes.environnement,
            db.nodes.host_mode,
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

@auth.requires_login()
def nodes():
    return dict()

@service.json
def json_node_services(nodename):
    q = db.svcmon.mon_nodname == nodename
    q &= _where(None, 'svcmon', domain_perms(), 'mon_svcname')
    rows = db(q).select(db.svcmon.mon_svcname)
    l = map(lambda x: x.mon_svcname, rows)
    return l

@service.json
def json_nodes(start, end, s):
    start = int(start)
    end = int(end)
    q = db.nodes.id > 0
    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= db.nodes.nodename.like(s)
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    q = apply_filters(q, None, db.nodes.nodename)
    rows = db(q).select(db.nodes.nodename, limitby=(start, end))
    l = map(lambda x: x.nodename, rows)
    return l

@service.json
def json_services(start, end, s):
    start = int(start)
    end = int(end)
    q = db.services.id > 0
    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= db.services.svc_name.like(s)
    q &= _where(None, 'services', domain_perms(), 'svc_name')
    q = apply_filters(q, None, db.services.svc_name)
    rows = db(q).select(db.services.svc_name, limitby=(start, end))
    l = map(lambda x: x.svc_name, rows)
    return l

@service.json
def json_alerts(start, end, s):
    return get_alerts(start, end, s)

@service.json
def json_node_alerts(nodename):
    return get_alerts(nodename=nodename)

@service.json
def json_service_alerts(svcname):
    return get_alerts(svcname=svcname)

def get_alerts(start=None, end=None, s="", svcname=None, nodename=None):
    if start is None:
        start = 0
    else:
        start = int(start)

    if end is None:
        end = 50
    else:
        end = int(end)

    o = ~db.dashboard.dash_severity
    q = db.dashboard.id > 0

    if svcname is not None:
        q &= db.dashboard.dash_svcname == svcname

    if nodename is not None:
        q &= db.dashboard.dash_nodename == nodename

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
def json_compliance(start, end, s):
    return get_compliance(start, end, s)

@service.json
def json_node_compliance(nodename):
    return get_compliance(nodename=nodename)

@service.json
def json_service_compliance(svcname):
    return get_compliance(svcname=svcname)

def get_compliance(start=None, end=None, s="", svcname=None, nodename=None):
    if start is None:
        start = 0
    else:
        start = int(start)

    if end is None:
        end = 50
    else:
        end = int(end)

    o = db.comp_status.run_nodename|db.comp_status.run_svcname|db.comp_status.run_module
    q = db.comp_status.id > 0

    if svcname is not None:
        q &= db.comp_status.run_svcname == svcname

    if nodename is not None:
        q &= db.comp_status.run_nodename == nodename

    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= (db.comp_status.run_svcname.like(s) | \
              db.comp_status.run_nodename.like(s) | \
              db.comp_status.run_log.like(s) | \
              db.comp_status.run_module.like(s))

    q &= _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q = apply_filters(q, db.comp_status.run_nodename, None)

    rows = db(q).select(orderby=o,
                        limitby=(start, end))
    return rows

@service.json
def json_actions(start, end, s):
    return get_actions(start, end, s)

@service.json
def json_node_actions(nodename):
    return get_actions(nodename=nodename)

@service.json
def json_service_actions(svcname):
    return get_actions(svcname=svcname)

def get_actions(start=None, end=None, s="", svcname=None, nodename=None):
    if start is None:
        start = 0
    else:
        start = int(start)

    if end is None:
        end = 50
    else:
        end = int(end)

    o = ~db.SVCactions.id
    q = db.SVCactions.status_log == None

    if svcname is not None:
        q &= db.SVCactions.svcname == svcname

    if nodename is not None:
        q &= db.SVCactions.hostname == nodename

    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= (db.SVCactions.svcname.like(s) | \
              db.SVCactions.hostname.like(s) | \
              db.SVCactions.action.like(s) | \
              db.SVCactions.status.like(s))

    q &= _where(None, 'SVCactions', domain_perms(), 'svcname')
    q = apply_filters(q, db.SVCactions.hostname, None)

    rows = db(q).select(orderby=o,
                        limitby=(start, end))
    return rows

@service.json
def json_logs(start, end, s):
    return get_logs(start, end, s)

@service.json
def json_node_logs(nodename):
    return get_logs(nodename=nodename)

@service.json
def json_service_logs(svcname):
    return get_logs(svcname=svcname)

def get_logs(start=None, end=None, s="", svcname=None, nodename=None):
    if start is None:
        start = 0
    else:
        start = int(start)

    if end is None:
        end = 50
    else:
        end = int(end)

    o = ~db.log.id
    q = db.log.id > 0

    if svcname is not None:
        q &= db.log.log_svcname == svcname

    if nodename is not None:
        q &= db.log.log_nodename == nodename

    if len(s) > 0 and s != "null":
        s = "%"+s+"%"
        q &= (db.log.log_svcname.like(s) | \
              db.log.log_nodename.like(s) | \
              db.log.log_action.like(s) | \
              db.log.log_dict.like(s))

    q &= _where(None, 'log', domain_perms(), 'log_nodename')
    q = apply_filters(q, db.log.log_nodename, None)

    rows = db(q).select(orderby=o,
                        limitby=(start, end))
    l = []
    for row in rows:
        if len(row.log_dict) > 0 and len(row.log_fmt) > 0:
            try:
                d = json.loads(row.log_dict)
                body = row.log_fmt % d
            except:
                body = "log body corrupted"
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
def json_show_action(action_id):
    q = db.SVCactions.id == action_id
    action = db(q).select().first()
    if action.pid is None:
        return []

    o = db.SVCactions.id
    q = db.SVCactions.pid.belongs(map(lambda x: int(x), action.pid.split(',')))
    q &= db.SVCactions.hostname == action.hostname
    q &= db.SVCactions.svcname == action.svcname
    q &= db.SVCactions.begin >= action.begin
    if action.end is not None:
        q &= db.SVCactions.end <= action.end
    else:
        q &= db.SVCactions.end <= action.begin + datetime.timedelta(days=1)
    q &= _where(None, 'SVCactions', domain_perms(), 'svcname')

    rows = db(q).select(orderby=o)
    return rows

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

