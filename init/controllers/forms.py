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
        self.keys = ['form_head_id']
        self.span = ['form_head_id']
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
                title = 'Head form id',
                field = 'form_head_id',
                display = True,
                table = 'workflows',
                img = 'wf16',
                _class = 'form_id',
            ),
            'last_form_id': HtmlTableColumn(
                title = 'Last form id',
                field = 'last_form_id',
                display = True,
                table = 'workflows',
                img = 'wf16',
                _class = 'form_id',
            ),
            'status': HtmlTableColumn(
                title = 'Status',
                field = 'status',
                display = True,
                table = 'workflows',
                img = 'wf16'
            ),
            'steps': HtmlTableColumn(
                title = 'Steps',
                field = 'steps',
                display = True,
                table = 'workflows',
                img = 'wf16'
            ),
            'creator': HtmlTableColumn(
                title = 'Creator',
                field = 'creator',
                display = True,
                table = 'workflows',
                img = 'guy16'
            ),
            'last_assignee': HtmlTableColumn(
                title = 'Last assignee',
                field = 'last_assignee',
                display = True,
                table = 'workflows',
                img = 'guy16'
            ),
            'create_date': HtmlTableColumn(
                title = 'Created on',
                field = 'create_date',
                display = True,
                table = 'workflows',
                img = 'time16',
                _class="datetime_no_age",
            ),
            'last_update': HtmlTableColumn(
                title = 'Last updated',
                field = 'last_update',
                display = True,
                table = 'workflows',
                img = 'time16',
                _class="datetime_no_age",
            ),
            'form_name': HtmlTableColumn(
                title = 'Name',
                field = 'form_name',
                display = True,
                table = 'forms_revisions',
                img = 'wf16'
            ),
            'last_form_name': HtmlTableColumn(
                title = 'Last form name',
                field = 'last_form_name',
                display = True,
                table = 'workflows',
                img = 'wf16'
            ),
            'form_folder': HtmlTableColumn(
                title = 'Folder',
                field = 'form_folder',
                display = True,
                table = 'forms_revisions',
                img = 'hd16'
            ),
            'form_yaml': HtmlTableColumn(
                title = 'Definition',
                field = 'form_yaml',
                display = False,
                table = 'forms_revisions',
                img = 'action16',
                _class = 'yaml'
            ),
        }
        for col in self.cols:
            self.colprops[col].t = self
        self.ajax_col_values = 'ajax_workflows_col_values'
        self.dbfilterable = False
        self.dataable = True
        self.wsable = True
        self.checkboxes = False

    def extra_line_key(self, o):
        return o.workflows.id

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
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_workflows():
    table_id = request.vars.table_id
    t = table_workflows(table_id, 'ajax_workflows')

    o = ~db.workflows.id
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
          """$.when(osvc.app_started).then(function(){ table_workflows("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def workflows_load():
    return workflows()["table"]


class table_forms(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.events = ["forms_change"]
        self.keys = ['id']
        self.force_cols = ['id']
        self.span = ['id']
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
                title = 'Id',
                field = 'id',
                display = False,
                table = 'v_forms',
                img = 'key'
            ),
            'form_name': HtmlTableColumn(
                title = 'Name',
                field = 'form_name',
                display = True,
                table = 'v_forms',
                img = 'prov',
                _class="form_name"
            ),
            'form_team_publication': HtmlTableColumn(
                title = 'Team publication',
                field = 'form_team_publication',
                display = True,
                table = 'v_forms',
                img = 'guys16',
                _class='groups'
            ),
            'form_team_responsible': HtmlTableColumn(
                title = 'Team responsible',
                field = 'form_team_responsible',
                display = True,
                table = 'v_forms',
                img = 'guys16',
                _class='groups'
            ),
            'form_type': HtmlTableColumn(
                title = 'Type',
                field = 'form_type',
                display = True,
                table = 'v_forms',
                img = 'edit16'
            ),
            'form_folder': HtmlTableColumn(
                title = 'Folder',
                field = 'form_folder',
                display = True,
                table = 'v_forms',
                img = 'hd16',
            ),
            'form_yaml': HtmlTableColumn(
                title = 'Definition',
                field = 'form_yaml',
                display = True,
                table = 'v_forms',
                img = 'action16',
                _class = 'yaml'
            ),
            'form_created': HtmlTableColumn(
                title = 'Created on',
                field = 'form_created',
                display = False,
                table = 'v_forms',
                img = 'time16',
                _class="datetime_no_age",
            ),
            'form_author': HtmlTableColumn(
                title = 'Author',
                field = 'form_author',
                display = False,
                table = 'v_forms',
                img = 'guy16'
            ),
        }
        self.ajax_col_values = 'ajax_forms_admin_col_values'
        self.dbfilterable = False
        self.dataable = True
        self.wsable = True
        self.checkboxes = True
        self.force_cols = ["id", "form_type"]

@auth.requires_login()
def ajax_forms_admin_col_values():
    table_id = request.vars.table_id
    t = table_forms(table_id, 'ajax_forms_admin')

    col = request.args[0]
    o = db.v_forms[col]
    q = db.v_forms.id > 0
    for f in t.cols:
        q = _where(q, 'v_forms', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_forms_admin():
    table_id = request.vars.table_id
    t = table_forms(table_id, 'ajax_forms_admin')
    o = db.v_forms.form_name
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
          """$.when(osvc.app_started).then(function(){ table_forms("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def forms_admin_load():
    return forms_admin()["table"]

@auth.requires_login()
def forms():
    o = {}
    if "form_name" in request.vars:
        o["form_name"] = request.vars.form_name
    d = SCRIPT(
          """$.when(osvc.app_started).then(function(){ requests("layout", %s) })""" % json.dumps(o)
    )
    return dict(table=d)

def forms_load():
    return forms()["table"]

@auth.requires_login()
def workflows_assigned_to_me():
    d = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_workflows_assigned_to_me("layout", {}) })""" 
    )
    return dict(table=d)

def workflows_assigned_to_me_load():
    return workflows_assigned_to_me()["table"]

@auth.requires_login()
def workflows_pending_tiers_action():
    d = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_workflows_assigned_to_tiers("layout", {}) })""" 
    )
    return dict(table=d)

def workflows_pending_tiers_action_load():
    return workflows_pending_tiers_action()["table"]

#
# deprecated in favor of the rest api
#
@auth.requires_login()
def _get_node_portnames(nodename):
    q = db.nodes.team_responsible.belongs(user_groups())
    q &= db.node_hba.nodename == db.nodes.nodename
    q &= db.node_hba.nodename == nodename
    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)
    return [r.hba_id for r in rows]

@service.json
def json_node_portnames(nodename):
    return _get_node_portnames(nodename)

@auth.requires_login()
def _get_service_portnames(svcname, nodename=None, loc_city=None):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.services.svc_name == svcname
    q &= db.node_hba.nodename == db.svcmon.mon_nodname

    if nodename is not None:
        q &= db.node_hba.nodename == nodename

    if loc_city is not None:
        q &= db.svcmon.mon_nodname == db.nodes.nodename
        q &= db.nodes.loc_city == loc_city

    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)

    return [r.hba_id for r in rows]

@service.json
def json_service_portnames(svcname, nodename=None, loc_city=None):
    return _get_service_portnames(svcname, nodename, loc_city)

@auth.requires_login()
def _get_service_nodes(svcname, loc_city=None):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.svcmon.mon_svcname == svcname

    if loc_city is not None:
        q &= db.svcmon.mon_nodname == db.nodes.nodename
        q &= db.nodes.loc_city == loc_city

    rows = db(q).select(db.svcmon.mon_nodname,
                        orderby=db.svcmon.mon_nodname,
                        groupby=db.svcmon.mon_nodname)
    return [r.mon_nodname for r in rows]

@service.json
def json_service_nodes(svcname, loc_city=None):
    return _get_service_nodes(svcname, loc_city)

@auth.requires_login()
def _get_service_loc_city(svcname):
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    rows = db(q).select(db.nodes.loc_city,
                        orderby=db.nodes.loc_city,
                        groupby=db.nodes.loc_city)
    return [r.loc_city for r in rows]

@service.json
def json_service_loc_city(svcname):
    return _get_service_loc_city(svcname)

@auth.requires_login()
def _get_node_generic(nodename, col):
    q = db.v_nodes.team_responsible.belongs(user_groups())
    q &= db.v_nodes.nodename == nodename
    node = db(q).select().first()
    if node is not None:
        if node[col] is None:
            return ""
        else:
            return node[col]
    q = db.v_nodes.team_responsible.belongs(user_groups())
    q &= db.v_nodes.nodename == nodename.split('.')[0]
    node = db(q).select().first()
    if node is not None:
        if node[col] is None:
            return ""
        else:
            return node[col]
    return T("node not found")

@service.json
def json_node_sec_zone(nodename):
    val = _get_node_generic(nodename, "sec_zone")
    if val is None:
        val = ""
    return val

@service.json
def json_node_environnement(nodename):
    return _get_node_generic(nodename, "environnement")

@service.json
def json_node_os_concat(nodename):
    return _get_node_generic(nodename, "os_concat")

@service.json
def json_node_loc_city(nodename):
    return _get_node_generic(nodename, "loc_city")

@service.json
def json_node_team_responsible(nodename):
    return _get_node_generic(nodename, "team_responsible")

@service.json
def json_node_macs(nodename):
    q = db.nodes.nodename.belongs((nodename, nodename.split('.')[0]))
    q &= db.node_ip.nodename == db.nodes.nodename
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
    q = db.node_ip.nodename == db.nodes.nodename
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
