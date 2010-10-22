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


