class table_comp_mod_status(table):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table.__init__(self, id, func, innerhtml)
        self.cols = ['mod_name', 'mod_total', 'mod_ok', 'mod_percent',
                     'mod_nodes']
        self.colprops = {
            'mod_name': dict(
                     size=12, title='module', _class='',
                     get=lambda x: x['mod_name'],
                     str=lambda x: x['mod_name'],
                     img='check16',
                    ),
            'mod_total': dict(
                     size=3, title='total', _class='',
                     get=lambda x: x['mod_total'],
                     str=lambda x: x['mod_total'],
                     img='check16',
                    ),
            'mod_ok': dict(
                     size=3, title='ok', _class='',
                     get=lambda x: x['mod_ok'],
                     str=lambda x: x['mod_ok'],
                     img='check16',
                    ),
            'mod_percent': dict(
                     size=3, title='percent', _class='',
                     get=lambda x: x['mod_percent'],
                     str=lambda x: x['mod_percent'],
                     img='check16',
                    ),
            'mod_nodes': dict(
                     size=10, title='mod_nodes', _class='',
                     get=lambda x: x['mod_nodes'],
                     str=lambda x: x['mod_nodes'].replace(',',', '),
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

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.table()

@auth.requires_login()
def comp_mod_status():
    return dict(table=DIV(ajax_comp_mod_status(), _id='ajax_comp_mod_status'))

class table_comp_status(table):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table.__init__(self, id, func, innerhtml)
        self.cols = ['run_date', 'run_nodename', 'run_module', 'run_status',
                     'run_ruleset']
        self.colprops = {
            'run_date': dict(
                     size=12, title='date', _class='',
                     get=lambda x: x['run_date'],
                     str=lambda x: x['run_date'],
                     img='check16',
                    ),
            'run_nodename': dict(
                     size=10, title='nodename', _class='',
                     get=lambda x: x['run_nodename'],
                     str=lambda x: x['run_nodename'],
                     img='node16',
                    ),
            'run_module': dict(
                     size=6, title='module', _class='',
                     get=lambda x: x['run_module'],
                     str=lambda x: x['run_module'],
                     img='check16',
                    ),
            'run_status': dict(
                     size=1, title='status', _class='',
                     get=lambda x: x['run_status'],
                     str=lambda x: self.format_run_status(x),
                     img='check16',
                    ),
            'run_log': dict(
                     size=16, title='log', _class='',
                     get=lambda x: x['run_log'],
                     str=lambda x: PRE(x['run_log']),
                     img='check16',
                    ),
            'run_ruleset': dict(
                     size=6, title='ruleset', _class='',
                     get=lambda x: x['run_ruleset'],
                     str=lambda x: x['run_ruleset'].replace(',',', '),
                     img='check16',
                    ),
        }
        self.img_h = {0: 'check16.png',
                      1: 'nok.png'}

    def format_run_status(self, x):
        val = x['run_status']
        if val in self.img_h:
            r = IMG(
                  _src=URL(r=request,c='static',f=self.img_h[val]),
                  _title=val,
                )
        else:
            r = val
        return r

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('ajax_comp_status', 'ajax_comp_status')
    t.upc_table = 'comp_status'

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    for f in t.cols:
        q &= _where(None, 'comp_status', t.filter_parse(f), f)

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.table()


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

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    t.upc_table = 'comp_log'

    o = ~db.comp_log.run_date
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    for f in t.cols:
        q &= _where(None, 'comp_log', t.filter_parse(f), f)

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.table()


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


