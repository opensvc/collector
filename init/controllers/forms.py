import re
import os
import yaml

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

class table_workflows(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['form_head_id',
                     'form_name',
                     'last_form_id',
                     'last_form_name',
                     'form_folder',
                     'status',
                     'steps',
                     'creator',
                     'last_assignee',
                     'create_date',
                     'last_update',
                     'form_yaml',
                    ]
        self.colprops = {
            'form_head_id': HtmlTableColumn(
                field = 'form_head_id',
                table = 'workflows',
            ),
            'last_form_id': HtmlTableColumn(
                field = 'last_form_id',
                table = 'workflows',
            ),
            'status': HtmlTableColumn(
                field = 'status',
                table = 'workflows',
            ),
            'steps': HtmlTableColumn(
                field = 'steps',
                table = 'workflows',
            ),
            'creator': HtmlTableColumn(
                field = 'creator',
                table = 'workflows',
            ),
            'last_assignee': HtmlTableColumn(
                field = 'last_assignee',
                table = 'workflows',
            ),
            'create_date': HtmlTableColumn(
                field = 'create_date',
                table = 'workflows',
            ),
            'last_update': HtmlTableColumn(
                field = 'last_update',
                table = 'workflows',
            ),
            'form_name': HtmlTableColumn(
                field = 'form_name',
                table = 'forms_revisions',
            ),
            'last_form_name': HtmlTableColumn(
                field = 'last_form_name',
                table = 'workflows',
            ),
            'form_folder': HtmlTableColumn(
                field = 'form_folder',
                table = 'forms_revisions',
            ),
            'form_yaml': HtmlTableColumn(
                field = 'form_yaml',
                table = 'forms_revisions',
            ),
        }
        self.ajax_col_values = 'ajax_workflows_col_values'

@auth.requires_login()
def ajax_workflows_col_values():
    table_id = request.vars.table_id
    t = table_workflows(table_id, 'ajax_workflows')

    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.workflows.id > 0
    q &= db.workflows.form_md5 == db.forms_revisions.form_md5
    for f in t.cols:
        q = _where(q, 'workflows', t.filter_parse(f), f)
    t.object_list = db(q).select(
        o,
        db.workflows.id.count(),
        orderby=~db.workflows.id.count(),
        groupby=o,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_workflows():
    table_id = request.vars.table_id
    t = table_workflows(table_id, 'ajax_workflows')

    o = t.get_orderby(default=~db.workflows.id)
    q = db.workflows.id > 0
    q &= db.workflows.form_md5 == db.forms_revisions.form_md5
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=True)

@auth.requires_login()
def workflows():
    t = SCRIPT(
          """table_workflows("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def workflows_load():
    return workflows()["table"]


class table_forms(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'form_name',
                     'form_type',
                     'form_folder',
                     'form_team_responsible',
                     'form_team_publication',
                     'form_yaml',
                     'form_created',
                     'form_author']
        self.colprops = {
            'id': HtmlTableColumn(
                field = 'id',
                table = 'v_forms',
            ),
            'form_name': HtmlTableColumn(
                field = 'form_name',
                table = 'v_forms',
            ),
            'form_team_publication': HtmlTableColumn(
                field = 'form_team_publication',
                table = 'v_forms',
            ),
            'form_team_responsible': HtmlTableColumn(
                field = 'form_team_responsible',
                table = 'v_forms',
            ),
            'form_type': HtmlTableColumn(
                field = 'form_type',
                table = 'v_forms',
            ),
            'form_folder': HtmlTableColumn(
                field = 'form_folder',
                table = 'v_forms',
            ),
            'form_yaml': HtmlTableColumn(
                field = 'form_yaml',
                table = 'v_forms',
            ),
            'form_created': HtmlTableColumn(
                field = 'form_created',
                table = 'v_forms',
            ),
            'form_author': HtmlTableColumn(
                field = 'form_author',
                table = 'v_forms',
            ),
        }
        self.ajax_col_values = 'ajax_forms_admin_col_values'

@auth.requires_login()
def ajax_forms_admin_col_values():
    table_id = request.vars.table_id
    t = table_forms(table_id, 'ajax_forms_admin')

    col = request.args[0]
    o = db.v_forms[col]
    q = db.v_forms.id > 0
    for f in t.cols:
        q = _where(q, 'v_forms', t.filter_parse(f), f)
    t.object_list = db(q).select(
        o,
        db.v_forms.id.count(),
        orderby=~db.v_forms.id.count(),
        groupby=o,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_forms_admin():
    table_id = request.vars.table_id
    t = table_forms(table_id, 'ajax_forms_admin')
    o = t.get_orderby(default=db.v_forms.form_name)
    q = db.v_forms.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def forms_admin():
    t = SCRIPT(
          """table_forms("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def forms_admin_load():
    return forms_admin()["table"]

@auth.requires_login()
def forms():
    o = {}
    if "form_name" in request.vars:
        o["form_name"] = request.vars.form_name
    if "form_folder" in request.vars:
        o["form_folder"] = request.vars.form_folder
    d = SCRIPT(
          """$.when(osvc.app_started).then(function(){requests("layout", %s)})""" % json.dumps(o)
    )
    return dict(table=d)

def forms_load():
    return forms()["table"]

@auth.requires_login()
def workflows_assigned_to_me():
    d = SCRIPT(
          """table_workflows_assigned_to_me("layout", %s)""" % request_vars_to_table_options(),
    )
    return dict(table=d)

def workflows_assigned_to_me_load():
    return workflows_assigned_to_me()["table"]

@auth.requires_login()
def workflows_pending_tiers_action():
    d = SCRIPT(
          """table_workflows_assigned_to_tiers("layout", %s)""" % request_vars_to_table_options(),
    )
    return dict(table=d)

def workflows_pending_tiers_action_load():
    return workflows_pending_tiers_action()["table"]

#
# deprecated in favor of the rest api
#
@auth.requires_login()
def _get_node_portnames(node_id):
    q = db.nodes.team_responsible.belongs(user_groups())
    q &= db.node_hba.node_id == node_id
    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)
    return [r.hba_id for r in rows]

@service.json
def json_node_portnames(node_id):
    return _get_node_portnames(node_id)

@auth.requires_login()
def _get_service_portnames(svc_id, node_id=None, loc_city=None):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.svc_id == db.services.svc_id
    q &= db.services.svc_id == svc_id
    q &= db.node_hba.node_id == db.svcmon.node_id

    if node_id is not None:
        q &= db.node_hba.node_id == node_id

    if loc_city is not None:
        q &= db.svcmon.node_id == db.nodes.node_id
        q &= db.nodes.loc_city == loc_city

    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)

    return [r.hba_id for r in rows]

@service.json
def json_service_portnames(svc_id, node_id=None, loc_city=None):
    return _get_service_portnames(svc_id, node_id, loc_city)

@auth.requires_login()
def _get_service_nodes(svc_id, loc_city=None):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.svc_id == db.services.svc_id
    q &= db.svcmon.svc_id == svc_id

    if loc_city is not None:
        q &= db.svcmon.node_id == db.nodes.node_id
        q &= db.nodes.loc_city == loc_city

    rows = db(q).select(db.svcmon.node_id,
                        orderby=db.svcmon.node_id,
                        groupby=db.svcmon.node_id)
    return [r.node_id for r in rows]

@service.json
def json_service_nodes(svc_id, loc_city=None):
    return _get_service_nodes(svc_id, loc_city)

@auth.requires_login()
def _get_service_loc_city(svc_id):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.svc_id == db.services.svc_id
    q &= db.svcmon.svc_id == svc_id
    q &= db.svcmon.node_id == db.nodes.node_id
    rows = db(q).select(db.nodes.loc_city,
                        orderby=db.nodes.loc_city,
                        groupby=db.nodes.loc_city)
    return [r.loc_city for r in rows]

@service.json
def json_service_loc_city(svc_id):
    return _get_service_loc_city(svc_id)

@auth.requires_login()
def _get_node_generic(node_id, col):
    q = db.nodes.team_responsible.belongs(user_groups())
    q &= db.nodes.node_id == node_id
    node = db(q).select().first()
    if node is not None:
        if node[col] is None:
            return ""
        else:
            return node[col]
    q = db.nodes.team_responsible.belongs(user_groups())
    q &= db.nodes.node_id == node_id
    node = db(q).select().first()
    if node is not None:
        if node[col] is None:
            return ""
        else:
            return node[col]
    return T("node not found")

@service.json
def json_node_sec_zone(node_id):
    val = _get_node_generic(node_id, "sec_zone")
    if val is None:
        val = ""
    return val

@service.json
def json_node_asset_env(node_id):
    return _get_node_generic(node_id, "asset_env")

@service.json
def json_node_os_concat(node_id):
    return _get_node_generic(node_id, "os_concat")

@service.json
def json_node_loc_city(node_id):
    return _get_node_generic(node_id, "loc_city")

@service.json
def json_node_team_responsible(node_id):
    return _get_node_generic(node_id, "team_responsible")

@service.json
def json_node_macs(node_id):
    q = db.nodes.node_id == node_id
    q &= db.node_ip.node_id == db.nodes.node_id
    q &= ~db.node_ip.intf.belongs(["lo", "lo0"])
    q &= ~db.node_ip.intf.like("veth%")
    q &= ~db.node_ip.intf.like("docker%")
    q &= ~db.node_ip.intf.like("br%")
    q &= ~db.node_ip.intf.like("lxc%")
    q &= ~db.node_ip.intf.like("xenbr%")
    rows = db(q).select(db.node_ip.mac, db.node_ip.intf,
                        groupby=db.node_ip.mac,
                        orderby=db.node_ip.mac)
    return ["%s (%s)"%(r.mac, r.intf) for r in rows]

@service.json
def json_mac_ipv4(mac):
    q = db.node_ip.node_id == db.nodes.node_id
    q &= db.node_ip.mac == mac
    q &= db.node_ip.type == "ipv4"
    row = db(q).select(db.node_ip.addr,
                       groupby=db.node_ip.addr,
                       orderby=db.node_ip.addr).first()
    if row is None:
        return T("mac not found")
    return row.addr

def ip_to_int(ip):
    v = ip.split(".")
    if len(v) != 4:
        return 0
    n = 0
    n += int(v[0]) << 24
    n += int(v[1]) << 16
    n += int(v[2]) << 8
    n += int(v[3])
    return n

def cidr_to_netmask(cidr):
    s = ""
    for i in range(cidr):
        s += "1"
    for i in range(32-cidr):
        s += "0"
    return int_to_ip(int(s, 2))

def int_to_ip(ip):
    l = []
    l.append(str(ip >> 24))
    ip = ip & 0x00ffffff
    l.append(str(ip >> 16))
    ip = ip & 0x0000ffff
    l.append(str(ip >> 8))
    ip = ip & 0x000000ff
    l.append(str(ip))
    return ".".join(l)

@service.json
def json_ip_netmask(ip):
    ip = ip_to_int(ip)
    sql = """select netmask from networks where
              %(ip)d >= inet_aton(begin) and
              %(ip)d <= inet_aton(end)""" % dict(ip=ip)
    rows = db.executesql(sql)
    if len(rows) == 0:
        return "not found"
    return cidr_to_netmask(rows[0][0])

@service.json
def json_ip_gateway(ip):
    ip = ip_to_int(ip)
    sql = """select gateway from networks where
              %(ip)d >= inet_aton(begin) and
              %(ip)d <= inet_aton(end)""" % dict(ip=ip)
    rows = db.executesql(sql)
    if len(rows) == 0:
        return "not found"
    return rows[0][0]

@service.json
def json_amazon_subnets_in_vpc(vpc):
    if not vpc.startswith("vpc"):
        return "malformated vpc name"
    elif not vpc.startswith("vpc-"):
        vpc = "vpc-"+vpc.replace("vpc", "")
    sql = """select name, concat(name, ", ", network, "/", netmask) from networks where
              comment = "%(vpc)s"
              order by name
          """ % dict(vpc=vpc)
    rows = db.executesql(sql)
    if len(rows) == 0:
        return "not found"
    return [(r[0], r[1]) for r in rows]

@service.json
def json_amazon_sizes(provider, access_key_id):
    from applications.init.modules import amazon
    cloud = amazon.get_cloud(provider, access_key_id)
    return cloud.list_sizes_value_label()

