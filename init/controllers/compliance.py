#
# custom column formatting
#
class col_run_log(HtmlTableColumn):
    def html(self, o):
        return PRE(self.get(o))

class col_run_ruleset(HtmlTableColumn):
    def html(self, o):
        return self.get(o).replace(',',', ')

class col_mod_nodes(HtmlTableColumn):
    def html(self, o):
        return self.get(o).replace(',',', ')

class col_run_status(HtmlTableColumn):
    img_h = {0: 'check16.png',
             1: 'nok.png'}
    def html(self, o):
        val = self.get(o)
        if val in self.img_h:
            r = IMG(
                  _src=URL(r=request,c='static',f=self.img_h[val]),
                  _title=val,
                )
        else:
            r = val
        return r

v_nodes_cols = [
     'loc_country',
     'loc_zip',
     'loc_city',
     'loc_addr',
     'loc_building',
     'loc_floor',
     'loc_room',
     'loc_rack',
     'os_name',
     'os_release',
     'os_vendor',
     'os_arch',
     'os_kernel',
     'cpu_dies',
     'cpu_cores',
     'cpu_model',
     'cpu_freq',
     'mem_banks',
     'mem_slots',
     'mem_bytes',
     'team_responsible',
     'serial',
     'model',
     'role',
     'environnement',
     'warranty_end',
     'status',
     'type',
     'power_supply_nb',
     'power_cabinet1',
     'power_cabinet2',
     'power_protect',
     'power_protect_breaker',
     'power_breaker1',
     'power_breaker2'
]

v_nodes_colprops = {
            'loc_country': HtmlTableColumn(
                     title = 'Country',
                     field='loc_country',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_zip': HtmlTableColumn(
                     title = 'ZIP',
                     field='loc_zip',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_city': HtmlTableColumn(
                     title = 'City',
                     field='loc_city',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_addr': HtmlTableColumn(
                     title = 'Address',
                     field='loc_addr',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_building': HtmlTableColumn(
                     title = 'Building',
                     field='loc_building',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),

            'loc_floor': HtmlTableColumn(
                     title = 'Floor',
                     field='loc_floor',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_room': HtmlTableColumn(
                     title = 'Room',
                     field='loc_room',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'loc_rack': HtmlTableColumn(
                     title = 'Rack',
                     field='loc_rack',
                     display = False,
                     img = 'loc',
                     table = 'v_nodes',
                    ),
            'os_name': HtmlTableColumn(
                     title = 'OS name',
                     field='os_name',
                     display = False,
                     img = 'os16',
                     table = 'v_nodes',
                    ),
            'os_release': HtmlTableColumn(
                     title = 'OS release',
                     field='os_release',
                     display = False,
                     img = 'os16',
                     table = 'v_nodes',
                    ),
            'os_vendor': HtmlTableColumn(
                     title = 'OS vendor',
                     field='os_vendor',
                     display = False,
                     img = 'os16',
                     table = 'v_nodes',
                    ),
            'os_arch': HtmlTableColumn(
                     title = 'OS arch',
                     field='os_arch',
                     display = False,
                     img = 'os16',
                     table = 'v_nodes',
                    ),
            'os_kernel': HtmlTableColumn(
                     title = 'OS kernel',
                     field='os_kernel',
                     display = False,
                     img = 'os16',
                     table = 'v_nodes',
                    ),
            'cpu_dies': HtmlTableColumn(
                     title = 'CPU dies',
                     field='cpu_dies',
                     display = False,
                     img = 'cpu16',
                     table = 'v_nodes',
                    ),
            'cpu_cores': HtmlTableColumn(
                     title = 'CPU cores',
                     field='cpu_cores',
                     display = False,
                     img = 'cpu16',
                     table = 'v_nodes',
                    ),
            'cpu_model': HtmlTableColumn(
                     title = 'CPU model',
                     field='cpu_model',
                     display = False,
                     img = 'cpu16',
                     table = 'v_nodes',
                    ),
            'cpu_freq': HtmlTableColumn(
                     title = 'CPU freq',
                     field='cpu_freq',
                     display = False,
                     img = 'cpu16',
                     table = 'v_nodes',
                    ),
            'mem_banks': HtmlTableColumn(
                     title = 'Memory banks',
                     field='mem_banks',
                     display = False,
                     img = 'mem16',
                     table = 'v_nodes',
                    ),
            'mem_slots': HtmlTableColumn(
                     title = 'Memory slots',
                     field='mem_slots',
                     display = False,
                     img = 'mem16',
                     table = 'v_nodes',
                    ),
            'mem_bytes': HtmlTableColumn(
                     title = 'Memory',
                     field='mem_bytes',
                     display = False,
                     img = 'mem16',
                     table = 'v_nodes',
                    ),
            'serial': HtmlTableColumn(
                     title = 'Serial',
                     field='serial',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'model': HtmlTableColumn(
                     title = 'Model',
                     field='model',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'team_responsible': HtmlTableColumn(
                     title = 'Team responsible',
                     field='team_responsible',
                     display = False,
                     img = 'guy16',
                     table = 'v_nodes',
                    ),
            'role': HtmlTableColumn(
                     title = 'Role',
                     field='role',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'environnement': HtmlTableColumn(
                     title = 'Env',
                     field='environnement',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'warranty_end': HtmlTableColumn(
                     title = 'Warranty end',
                     field='warranty_end',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'status': HtmlTableColumn(
                     title = 'Status',
                     field='status',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'type': HtmlTableColumn(
                     title = 'Type',
                     field='type',
                     display = False,
                     img = 'node16',
                     table = 'v_nodes',
                    ),
            'power_supply_nb': HtmlTableColumn(
                     title = 'Power supply number',
                     field='power_supply_nb',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_cabinet1': HtmlTableColumn(
                     title = 'Power cabinet #1',
                     field='power_cabinet1',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_cabinet2': HtmlTableColumn(
                     title = 'Power cabinet #2',
                     field='power_cabinet2',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_protect': HtmlTableColumn(
                     title = 'Power protector',
                     field='power_protect',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_protect_breaker': HtmlTableColumn(
                     title = 'Power protector breaker',
                     field='power_protect_breaker',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_breaker1': HtmlTableColumn(
                     title = 'Power breaker #1',
                     field='power_breaker1',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
            'power_breaker2': HtmlTableColumn(
                     title = 'Power breaker #2',
                     field='power_breaker2',
                     display = False,
                     img = 'pwr',
                     table = 'v_nodes',
                    ),
}

class table_comp_mod_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mod_name', 'mod_total', 'mod_ok', 'mod_percent',
                     'mod_nodes']
        self.colprops = {
            'mod_name': HtmlTableColumn(
                     title='Module',
                     field='mod_name',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                    ),
            'mod_total': HtmlTableColumn(
                     title='Total',
                     field='mod_total',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_ok': HtmlTableColumn(
                     title='Ok',
                     field='mod_ok',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_percent': HtmlTableColumn(
                     title='Percent',
                     field='mod_percent',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_nodes': col_mod_nodes(
                     title='Nodes',
                     field='mod_nodes',
                     #table='comp_mod_status',
                     display=True,
                     img='node16',
                    ),
        }

@auth.requires_login()
def ajax_comp_mod_status():
    t = table_comp_mod_status('ajax_comp_mod_status', 'ajax_comp_mod_status')
    t.upc_table = 'comp_mod_status'

    o = ~db.v_comp_mod_status.mod_percent
    q = db.v_comp_mod_status.id > 0
    for f in t.cols:
        q &= _where(None, 'v_comp_mod_status', t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def comp_mod_status():
    return dict(table=DIV(ajax_comp_mod_status(), _id='ajax_comp_mod_status'))

class table_comp_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['run_date',
                     'run_nodename',
                     'run_module',
                     'run_status',
                     'run_ruleset']
        self.cols += v_nodes_cols
        self.colprops = {
            'run_date': HtmlTableColumn(
                     title='Run date',
                     field='run_date',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_nodename': HtmlTableColumn(
                     title='Node name',
                     field='run_nodename',
                     table='comp_status',
                     img='node16',
                     display=True,
                    ),
            'run_module': HtmlTableColumn(
                     title='Module',
                     field='run_module',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_status': col_run_status(
                     title='Status',
                     field='run_status',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_log': col_run_log(
                     title='Log',
                     field='run_log',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_ruleset': col_run_ruleset(
                     title='Rule set',
                     field='run_ruleset',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
        }
        self.colprops.update(v_nodes_colprops)


@auth.requires_login()
def ajax_comp_log_col_values():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    col = request.args[0]
    o = db.comp_log[col]
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q &= _where(None, t.colprops[f].table, t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    t = table_comp_status('ajax_comp_status', 'ajax_comp_status')
    col = request.args[0]
    o = db.comp_status[col]
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q &= _where(None, t.colprops[f].table, t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('ajax_comp_status', 'ajax_comp_status')
    t.upc_table = 'comp_status'

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q &= _where(None, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()


@auth.requires_login()
def comp_status():
    return dict(table=DIV(ajax_comp_status(), _id='ajax_comp_status'))

class table_comp_log(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table_comp_status.__init__(self, id, 'ajax_comp_log', innerhtml)
        self.cols = ['run_date', 'run_nodename', 'run_module', 'run_status',
                     'run_log', 'run_ruleset']
        self.cols += v_nodes_cols
        for c in self.colprops:
            if 'run_' in c:
                self.colprops[c].table = 'comp_log'

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    t.upc_table = 'comp_log'

    o = ~db.comp_log.run_date
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q &= _where(None, 'comp_log', t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()


@auth.requires_login()
def comp_log():
    return dict(table=DIV(ajax_comp_log(), _id='ajax_comp_log'))

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.xmlrpc
def comp_get_moduleset_modules(moduleset):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.moduleset.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.moduleset == moduleset
    else:
        return []
    rows = db(q).select(db.comp_moduleset.module,
                        groupby=db.comp_moduleset.module)
    return [r.module for r in rows]

def comp_moduleset_exists(moduleset):
    q = db.comp_moduleset.moduleset == moduleset
    if len(db(q).select(db.comp_moduleset.id)) == 0:
        return False
    return True

def comp_moduleset_attached(nodename, moduleset):
    q = db.comp_node_moduleset.moduleset_node == nodename
    q &= db.comp_node_moduleset.moduleset_name == moduleset
    if len(db(q).select(db.comp_node_moduleset.id)) == 0:
        return False
    return True

def comp_ruleset_exists(ruleset):
    q = db.comp_rules.rule_table == 'comp_node_ruleset'
    q &= db.comp_rules.rule_field == 'ruleset_name'
    q &= db.comp_rules.rule_value == ruleset
    if len(db(q).select(db.comp_rules.id)) == 0:
        return False
    return True

def comp_ruleset_attached(nodename, ruleset):
    q = db.comp_node_ruleset.ruleset_node == nodename
    q &= db.comp_node_ruleset.ruleset_name == ruleset
    if len(db(q).select(db.comp_node_ruleset.id)) == 0:
        return False
    return True

@service.xmlrpc
def comp_add_moduleset(nodename, moduleset):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    if not comp_moduleset_exists(moduleset):
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    if comp_moduleset_attached(nodename, moduleset):
        return dict(status=True,
                    msg="moduleset %s is already attached to this node"%moduleset)
    n = db.comp_node_moduleset.insert(moduleset_node=nodename,
                                    moduleset_name=moduleset)
    if n == 0:
        return dict(status=False, msg="failed to attach moduleset %s"%moduleset)
    return dict(status=True, msg="moduleset %s attached"%moduleset)

@service.xmlrpc
def comp_del_moduleset(nodename, moduleset):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    if not comp_moduleset_attached(nodename, moduleset):
        return dict(status=True,
                    msg="moduleset %s is not attached to this node"%moduleset)
    q = db.comp_node_moduleset.moduleset_node == nodename
    q &= db.comp_node_moduleset.moduleset_name == moduleset
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the moduleset")
    return dict(status=True, msg="moduleset %s detached"%moduleset)

@service.xmlrpc
def comp_add_ruleset(nodename, ruleset):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    if not comp_ruleset_exists(ruleset):
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if comp_ruleset_attached(nodename, ruleset):
        return dict(status=True,
                    msg="ruleset %s is already attached to this node"%ruleset)
    n = db.comp_node_ruleset.insert(ruleset_node=nodename,
                                    ruleset_name=ruleset)
    if n == 0:
        return dict(status=False, msg="failed to attach ruleset %s"%ruleset)
    return dict(status=True, msg="ruleset %s attached"%ruleset)

@service.xmlrpc
def comp_del_ruleset(nodename, ruleset):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    if not comp_ruleset_attached(nodename, ruleset):
        return dict(status=True,
                    msg="ruleset %s is not attached to this node"%ruleset)
    q = db.comp_node_ruleset.ruleset_node == nodename
    q &= db.comp_node_ruleset.ruleset_name == ruleset
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the ruleset")
    return dict(status=True, msg="ruleset %s detached"%ruleset)

@service.xmlrpc
def comp_get_moduleset(nodename):
    moduleset = []
    q = db.comp_node_moduleset.moduleset_node == nodename
    rows = db(q).select(db.comp_node_moduleset.moduleset_name,
                        groupby=db.comp_node_moduleset.moduleset_name)
    return [r.moduleset_name for r in rows]

@service.xmlrpc
def comp_log_action(vars, vals):
    generic_insert('comp_log', vars, vals)
    generic_insert('comp_status', vars, vals)

def comp_query(q, rule):
    if rule.rule_op == '=':
        qry = db[rule.rule_table][rule.rule_field] == rule.rule_value
    elif rule.rule_op == 'LIKE':
        qry = db[rule.rule_table][rule.rule_field].like(rule.rule_value)
    elif rule.rule_op == '>=':
        qry = db[rule.rule_table][rule.rule_field] >= rule.rule_value
    elif rule.rule_op == '>':
        qry = db[rule.rule_table][rule.rule_field] > rule.rule_value
    elif rule.rule_op == '<=':
        qry = db[rule.rule_table][rule.rule_field] <= rule.rule_value
    elif rule.rule_op == '<':
        qry = db[rule.rule_table][rule.rule_field] < rule.rule_value
    else:
        return q
    if rule.rule_log_op == 'AND':
        q &= qry
    elif rule.rule_log_op == 'OR':
        q |= qry
    return q

def comp_format_filter(q):
    s = str(q)
    if 'comp_node_ruleset' in s:
        return ''
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.replace('nodes.id>0 AND ','')
    return s

def comp_get_node_ruleset(nodename):
    q = db.v_nodes.nodename == nodename
    rows = db(q).select()
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_node', 
               'filter': str(q),
               'vars': []}
    for f in db.nodes.fields:
        ruleset['vars'].append(('nodes.'+f, rows[0][f]))
    return {'osvc_node':ruleset}

@service.xmlrpc
def comp_get_ruleset(nodename):
    ruleset = comp_get_node_ruleset(nodename)
    q = db.nodes.nodename == nodename
    rows = db(db.comp_rules.id>0).select(orderby=db.comp_rules.rule_name)
    last_index = len(rows)-1
    qr = db.nodes.id > 0

    for i, rule in enumerate(rows):
        if rule.rule_table == 'comp_node_ruleset':
            qr = db.comp_node_ruleset.ruleset_node == db.nodes.nodename
        if i == last_index:
            end_seq = True
        elif rows[i].rule_name != rows[i+1].rule_name:
            end_seq = True
        else:
            end_seq = False
        qr = comp_query(qr, rule)
        if end_seq:
            match = db(q&qr).select(db.nodes.id)
            if len(match) == 1:
                rulevars = db(db.comp_rules_vars.rule_name==rule.rule_name).select()
                ruleset[rule.rule_name] = dict(name=rule.rule_name,
                                                  filter=comp_format_filter(qr),
                                                  vars=[])
                for rulevar in rulevars:
                    ruleset[rule.rule_name]['vars'].append((rulevar.rule_var_name,
                                                            rulevar.rule_var_value))
            qr = db.nodes.id > 0
    return ruleset


