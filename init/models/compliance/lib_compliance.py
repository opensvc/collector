import copy

def ruleset_responsible(id):
    ug = user_groups()
    q = db.comp_rulesets.id == id
    if 'Manager' not in ug:
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    v = rows.first()
    if v is None:
        return False
    return True

def ruleset_publication(id):
    if ruleset_has_everybody_publication(id):
        return True
    ug = user_groups()
    q = db.comp_rulesets.id == id
    if 'Manager' not in ug:
        q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
        q &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    v = rows.first()
    if v is None:
        return False
    return True

def moduleset_responsible(id):
    ug = user_groups()
    q = db.comp_moduleset.id == id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    v = rows.first()
    if v is None:
        return False
    return True

def moduleset_publication(id):
    if moduleset_has_everybody_publication(id):
        return True
    ug = user_groups()
    q = db.comp_moduleset.id == id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
        q &= db.comp_moduleset_team_publication.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    v = rows.first()
    if v is None:
        return False
    return True

def fset_get_ancestors():
    q = db.gen_filtersets_filters.f_id == 0
    rows = db(q).select()
    ancestors = {}
    for row in rows:
        if row.encap_fset_id not in ancestors:
            ancestors[row.encap_fset_id] = []
        ancestors[row.encap_fset_id].append(row.fset_id)
    return ancestors

def fset_loop(fset_id, parent_fset_id):
    if fset_id == parent_fset_id:
        return True
    fset_id = int(fset_id)
    parent_fset_id = int(parent_fset_id)
    ancestors = fset_get_ancestors()
    tested = []
    def recurse_rel(fset_id, parent_fset_id):
        if parent_fset_id not in ancestors:
            return False
        for _parent_fset_id in ancestors[parent_fset_id]:
            tested.append("%d-%d"%(fset_id,_parent_fset_id))
            if fset_id == _parent_fset_id:
                return True
            if recurse_rel(fset_id, _parent_fset_id):
                return True
        return False

    return recurse_rel(fset_id, parent_fset_id)

def rset_loop(rset_id, parent_rset_id):
    rset_id = int(rset_id)
    parent_rset_id = int(parent_rset_id)
    q = db.comp_rulesets_rulesets.id > 0
    rows = db(q).select()
    ancestors = {}
    for row in rows:
        if row.child_rset_id not in ancestors:
            ancestors[row.child_rset_id] = []
        ancestors[row.child_rset_id].append(row.parent_rset_id)

    tested = []
    def recurse_rel(rset_id, parent_rset_id):
        if parent_rset_id not in ancestors:
            return False
        for _parent_rset_id in ancestors[parent_rset_id]:
            tested.append("%d-%d"%(rset_id,_parent_rset_id))
            if rset_id == _parent_rset_id:
                return True
            if recurse_rel(rset_id, _parent_rset_id):
                return True
        return False

    return recurse_rel(rset_id, parent_rset_id)

def comp_rulesets_chains():
    # populate rset names cache
    rset_names = get_rset_names()

    # populate rset relations cache
    rset_relations = _get_rset_relations()

    def recurse_rel(rset_id, chains, rset_id_chain):
        rset_id_chain += [rset_id]
        if rset_id_chain in chains:
            return chains
        if len(rset_id_chain) > 1:
            chains.append(rset_id_chain)
        if rset_id not in rset_relations:
            return chains
        for child_rset_id in rset_relations[rset_id]:
            chains = recurse_rel(child_rset_id, chains, copy.copy(rset_id_chain))
        return chains

    chains = []
    for ruleset_id in rset_names:
        chains += [[ruleset_id, ruleset_id]]
        chains += recurse_rel(ruleset_id, chains=[], rset_id_chain=[])

    vars = ['head_rset_id', 'tail_rset_id', 'chain_len', 'chain']
    vals = []
    for chain in chains:
        val = [str(chain[0]), str(chain[-1])]
        if chain[0] != chain[-1] or len(chain) != 2:
            _chain_len = str(len(chain))
            _chain = map(lambda x: rset_names[x], chain)
            _chain = ' > '.join(_chain)
        else:
            _chain_len = '1'
            _chain = ''
        val.append(_chain_len)
        val.append(_chain)
        vals.append(val)

    db.executesql("truncate comp_rulesets_chains")
    generic_insert('comp_rulesets_chains', vars, vals)
    db.commit()

def ruleset_has_everybody_publication(ruleset_id):
    q = db.auth_group.role == "Everybody"
    q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
    q &= db.comp_ruleset_team_publication.ruleset_id == ruleset_id
    if db(q).count() == 0:
        return False
    return True

def moduleset_has_everybody_publication(modset_id):
    q = db.auth_group.role == "Everybody"
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= db.comp_moduleset_team_publication.modset_id == modset_id
    if db(q).count() == 0:
        return False
    return True

def comp_moduleset_svc_attachable(svc_id, modset_id):
    if moduleset_has_everybody_publication(modset_id):
        return True
    q = db.services.svc_id == svc_id
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) == 0:
        return False
    return True

def comp_ruleset_svc_attachable(svc_id, rset_id):
    if ruleset_has_everybody_publication(rset_id):
        return True
    q = db.services.svc_id == svc_id
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
    q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == rset_id
    q &= db.comp_rulesets.ruleset_public == True
    q &= db.comp_rulesets.ruleset_type == "explicit"
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) == 0:
        return False
    return True

def comp_moduleset_attachable(node_id, modset_id):
    if moduleset_has_everybody_publication(modset_id):
        return True
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    q &= db.nodes.node_id == node_id
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) != 1:
        return False
    return True

def comp_ruleset_attachable(node_id, ruleset_id):
    if ruleset_has_everybody_publication(ruleset_id):
        return True
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
    q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == ruleset_id
    q &= db.comp_rulesets.ruleset_public == True
    q &= db.comp_rulesets.ruleset_type == "explicit"
    q &= db.nodes.node_id == node_id
    rows = db(q).select(cacheable=True)
    if len(rows) != 1:
        return False
    return True

def comp_slave(svc_id, node_id):
    q = db.svcmon.mon_vmname == db.nodes.nodename
    q &= db.nodes.node_id == node_id
    q &= db.svcmon.svc_id == svc_id
    row = db(q).select(cacheable=True).first()
    if row is None:
        return False
    return True

def comp_moduleset_attached(node_id, modset_id):
    q = db.comp_node_moduleset.node_id == node_id
    q &= db.comp_node_moduleset.modset_id == modset_id
    if len(db(q).select(db.comp_node_moduleset.id, cacheable=True)) == 0:
        return False
    return True

def comp_ruleset_svc_attached(svc_id, rset_id, slave):
    q = db.comp_rulesets_services.svc_id == svc_id
    q &= db.comp_rulesets_services.ruleset_id == rset_id
    q &= db.comp_rulesets_services.slave == slave
    if len(db(q).select(db.comp_rulesets_services.id, cacheable=True)) == 0:
        return False
    return True

def comp_moduleset_svc_attached(svc_id, modset_id, slave):
    q = db.comp_modulesets_services.svc_id == svc_id
    q &= db.comp_modulesets_services.modset_id == modset_id
    q &= db.comp_modulesets_services.slave == slave
    if len(db(q).select(db.comp_modulesets_services.id, cacheable=True)) == 0:
        return False
    return True

def comp_ruleset_exists(ruleset):
    q = db.v_comp_explicit_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.v_comp_explicit_rulesets.id, cacheable=True)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_ruleset_attached(node_id, ruleset_id):
    q = db.comp_rulesets_nodes.node_id == node_id
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if len(db(q).select(db.comp_rulesets_nodes.id, cacheable=True)) == 0:
        return False
    return True

def comp_attached_ruleset_id(node_id):
    q = db.comp_rulesets_nodes.node_id == node_id
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id, cacheable=True)
    return [r.ruleset_id for r in rows]

def comp_attached_svc_moduleset_id(svc_id):
    q = db.comp_modulesets_services.svc_id == svc_id
    rows = db(q).select(db.comp_modulesets_services.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

def comp_attached_moduleset_id(node_id):
    q = db.comp_node_moduleset.node_id == node_id
    rows = db(q).select(db.comp_node_moduleset.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

def comp_ruleset_variable_id(ruleset_id, var_name):
    q = db.comp_rulesets_variables.ruleset_id == ruleset_id
    q &= db.comp_rulesets_variables.var_name == var_name
    rows = db(q).select(db.comp_rulesets_variables.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_module_id(modset_id, mod_name):
    q = db.comp_moduleset_modules.modset_id == modset_id
    q &= db.comp_moduleset_modules.modset_mod_name == mod_name
    rows = db(q).select(db.comp_moduleset_modules.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_ruleset_id(ruleset):
    q = db.comp_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_ruleset_name(ruleset_id):
    q = db.comp_rulesets.id == ruleset_id
    rows = db(q).select(db.comp_rulesets.ruleset_name, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].ruleset_name

def comp_moduleset_name(modset_id):
    q = db.comp_moduleset.id == modset_id
    rows = db(q).select(db.comp_moduleset.modset_name, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].modset_name

def comp_moduleset_id(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_exists(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_attached_svc_ruleset_id(svc_id, slave):
    q = db.comp_rulesets_services.svc_id == svc_id
    q &= db.comp_rulesets_services.slave == slave
    rows = db(q).select(db.comp_rulesets_services.ruleset_id, cacheable=True)
    return [r.ruleset_id for r in rows]


#
@auth.requires_membership('CompManager')
def attach_moduleset_to_moduleset(child_modset_id, parent_modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == parent_modset_id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("parent moduleset not found or not owned by you")

    q = db.comp_moduleset.id == child_modset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("child moduleset not found")

    q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
    q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
    if db(q).count() > 0:
        raise CompInfo("already attached")

    db.comp_moduleset_moduleset.update_or_insert(parent_modset_id=parent_modset_id,
                                                 child_modset_id=child_modset_id)
    table_modified("comp_moduleset_moduleset")
    fmt = 'attached moduleset %(child_modset_name)s to moduleset %(parent_modset_name)s'
    fmt_data = dict(child_modset_name=w.modset_name, parent_modset_name=v.modset_name)
    _log('compliance.moduleset.moduleset.attach', fmt, fmt_data)


#
# moduleset attachments
#
def lib_comp_moduleset_attach_node(node_id, modset_id):
    moduleset = comp_moduleset_name(modset_id)
    if moduleset is None:
        return dict(error="moduleset %s does not exist"%moduleset)
    if comp_moduleset_attached(node_id, modset_id):
        return dict(info="moduleset %s is already attached to this node"%moduleset)
    if not comp_moduleset_attachable(node_id, modset_id):
        return dict(error="moduleset %s is not attachable"%moduleset)

    n = db.comp_node_moduleset.insert(node_id=node_id,
                                      modset_id=modset_id)
    table_modified("comp_node_moduleset")
    update_dash_moddiff_node(node_id)

    if n == 0:
        return dict(error="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.node.attach',
         '%(moduleset)s attached to node %(node)s',
         dict(node=get_nodename(node_id), moduleset=moduleset),
         node_id=node_id,
    )
    ws_send('comp_node_moduleset_change', {'node_id': node_id, 'modset_id': modset_id})
    return dict(info="moduleset %s attached"%moduleset)


def lib_comp_moduleset_detach_node(node_id, modset_id):
    if type(modset_id) == list:
        moduleset = "all"
        if len(modset_id) == 0:
            return dict(info="this node has no moduleset attached")
    else:
        moduleset = comp_moduleset_name(modset_id)
        if moduleset is None:
            return dict(error="moduleset %s does not exist"%moduleset)
        if not comp_moduleset_attached(node_id, modset_id):
            return dict(info="moduleset %s is not attached to this node"%moduleset)
    q = db.comp_node_moduleset.node_id == node_id
    if isinstance(modset_id, list):
        q &= db.comp_node_moduleset.modset_id.belongs(modset_id)
    else:
        q &= db.comp_node_moduleset.modset_id == modset_id
    n = db(q).delete()
    table_modified("comp_node_moduleset")
    if n == 0:
        return dict(error="failed to detach the moduleset")
    update_dash_moddiff_node(node_id)

    _log('compliance.moduleset.node.detach',
         '%(moduleset)s detached from node %(node)s',
         dict(node=get_nodename(node_id), moduleset=moduleset),
         node_id=node_id,
    )
    ws_send('comp_node_moduleset_change', {'modset_id': modset_id})
    return dict(info="moduleset %s detached"%moduleset)


def lib_comp_moduleset_detach_service(svc_id, modset_id, slave=False):
    if type(modset_id) == list:
        moduleset = "all"
        if len(modset_id) == 0:
            return dict(info="this service has no moduleset attached")
    else:
        moduleset = comp_moduleset_name(modset_id)
        if moduleset is None:
            return dict(error="moduleset %s does not exist"%moduleset)
        if not comp_moduleset_svc_attached(svc_id, modset_id, slave):
            return dict(info="moduleset %s is not attached to this service"%moduleset)
    q = db.comp_modulesets_services.svc_id == svc_id
    q &= db.comp_modulesets_services.slave == slave
    if isinstance(modset_id, list):
        q &= db.comp_modulesets_services.modset_id.belongs(modset_id)
    else:
        q &= db.comp_modulesets_services.modset_id == modset_id
    n = db(q).delete()
    table_modified("comp_modulesets_services")
    if n == 0:
        return dict(error="failed to detach the moduleset")
    _log('compliance.moduleset.service.detach',
         '%(moduleset)s detached from service',
         dict(moduleset=moduleset),
         svc_id=svc_id,
    )
    ws_send('comp_modulesets_services_change', {'modset_id': modset_id})
    return dict(info="moduleset %s detached"%moduleset)


def lib_comp_moduleset_attach_service(svc_id, modset_id, slave):
    moduleset = comp_moduleset_name(modset_id)
    if moduleset is None:
        return dict(error="moduleset %s does not exist"%moduleset)
    if comp_moduleset_svc_attached(svc_id, modset_id, slave):
        return dict(info="moduleset %s is already attached to this service"%moduleset)
    if not comp_moduleset_svc_attachable(svc_id, modset_id):
        return dict(error="moduleset %s is not attachable"%moduleset)
    n = db.comp_modulesets_services.insert(svc_id=svc_id,
                                           modset_id=modset_id,
                                           slave=slave)
    table_modified("comp_modulesets_services")
    if n == 0:
        return dict(error="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.service.attach',
         '%(moduleset)s attached to service',
        dict(moduleset=moduleset),
        svc_id=svc_id,
    )
    ws_send('comp_modulesets_services_change', {'modset_id': modset_id})
    return dict(info="moduleset %s attached"%moduleset)

#
# ruleset attachments
#
def lib_comp_ruleset_attach_node(node_id, ruleset_id):
    ruleset = comp_ruleset_name(ruleset_id)
    if ruleset is None:
        return dict(error="ruleset %s does not exist"%ruleset)
    if comp_ruleset_attached(node_id, ruleset_id):
        return dict(info="ruleset %s is already attached to this node"%ruleset)
    if not comp_ruleset_attachable(node_id, ruleset_id):
        return dict(error="ruleset %s is not attachable"%ruleset)

    n = db.comp_rulesets_nodes.insert(node_id=node_id,
                                      ruleset_id=ruleset_id)
    table_modified("comp_rulesets_nodes")
    update_dash_rsetdiff_node(node_id)

    if n == 0:
        return dict(error="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.node.attach',
         '%(ruleset)s attached to node %(node)s',
         dict(node=get_nodename(node_id), ruleset=ruleset),
         node_id=node_id,
    )
    ws_send('comp_rulesets_nodes_change', {'ruleset_id': ruleset_id})
    return dict(info="ruleset %s attached"%ruleset)


def lib_comp_ruleset_detach_node(node_id, ruleset_id):
    if type(ruleset_id) == list:
        ruleset = "all"
        if len(ruleset_id) == 0:
            return dict(info="this node has no ruleset attached")
    else:
        ruleset = comp_ruleset_name(ruleset_id)
        if ruleset is None:
            return dict(error="ruleset %s does not exist"%ruleset)
        if not comp_ruleset_attached(node_id, ruleset_id):
            return dict(info="ruleset %s is not attached to this node"%ruleset)
    q = db.comp_rulesets_nodes.node_id == node_id
    if isinstance(ruleset_id, list):
        q &= db.comp_rulesets_nodes.ruleset_id.belongs(ruleset_id)
    else:
        q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    n = db(q).delete()
    table_modified("comp_rulesets_nodes")
    if n == 0:
        return dict(error="failed to detach the ruleset")
    update_dash_rsetdiff_node(node_id)

    _log('compliance.ruleset.node.detach',
         '%(ruleset)s detached from node %(node)s',
         dict(node=get_nodename(node_id), ruleset=ruleset),
         node_id=node_id,
    )
    ws_send('comp_rulesets_nodes_change', {'ruleset_id': ruleset_id})
    return dict(info="ruleset %s detached"%ruleset)


def lib_comp_ruleset_detach_service(svc_id, ruleset_id, slave=False):
    if type(ruleset_id) == list:
        ruleset = "all"
        if len(ruleset_id) == 0:
            return dict(info="this service has no ruleset attached")
    else:
        ruleset = comp_ruleset_name(ruleset_id)
        if ruleset is None:
            return dict(error="ruleset %s does not exist"%ruleset)
        if not comp_ruleset_svc_attached(svc_id, ruleset_id, slave):
            return dict(info="ruleset %s is not attached to this service"%ruleset)
    q = db.comp_rulesets_services.svc_id == svc_id
    q &= db.comp_rulesets_services.slave == slave
    if isinstance(ruleset_id, list):
        q &= db.comp_rulesets_services.ruleset_id.belongs(ruleset_id)
    else:
        q &= db.comp_rulesets_services.ruleset_id == ruleset_id
    n = db(q).delete()
    table_modified("comp_rulesets_services")
    if n == 0:
        return dict(error="failed to detach the ruleset")
    _log('compliance.ruleset.service.detach',
         '%(ruleset)s detached from service',
         dict(ruleset=ruleset),
         svc_id=svc_id,
    )
    ws_send('comp_rulesets_services_change', {'ruleset_id': ruleset_id})
    return dict(info="ruleset %s detached"%ruleset)


def lib_comp_ruleset_attach_service(svc_id, ruleset_id, slave):
    ruleset = comp_ruleset_name(ruleset_id)
    if ruleset is None:
        return dict(error="ruleset %s does not exist"%ruleset)
    if comp_ruleset_svc_attached(svc_id, ruleset_id, slave):
        return dict(info="ruleset %s is already attached to this service"%ruleset)
    if not comp_ruleset_svc_attachable(svc_id, ruleset_id):
        return dict(error="ruleset %s is not attachable"%ruleset)
    n = db.comp_rulesets_services.insert(svc_id=svc_id,
                                           ruleset_id=ruleset_id,
                                           slave=slave)
    table_modified("comp_rulesets_services")
    if n == 0:
        return dict(error="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.service.attach',
         '%(ruleset)s attached to service',
        dict(ruleset=ruleset),
        svc_id=svc_id,
    )
    ws_send('comp_rulesets_services_change', {'ruleset_id': ruleset_id})
    return dict(info="ruleset %s attached"%ruleset)

def get_modset_tree_nodes(modset_ids=None):
    modset_tree_nodes = {}
    modset_relations = get_modset_relations()

    if modset_ids is None:
        modset_ids = modset_relations.keys()

    def recurse_relations(head):
        l = []
        if head not in modset_relations:
            return l
        for child_id in modset_relations[head]:
            l.append(child_id)
            l += recurse_relations(child_id)
        return l

    for parent_id in modset_ids:
        modset_tree_nodes[parent_id] = recurse_relations(parent_id)

    return modset_tree_nodes

def get_modset_relations_s():
    # modset relation cache (strings)
    modset_names = get_modset_names()
    modset_relations = get_modset_relations()
    modset_relations_s = {}
    for modset_id, l in modset_relations.items():
        try:
            modset_relations_s[modset_names[modset_id]] = map(lambda x: modset_names[x], l)
        except KeyError as e:
            print e
    return modset_relations_s

def get_modset_names(modset_ids=None):
    # init modset name cache
    if modset_ids is not None:
        q = db.comp_moduleset.id.belongs(modset_ids)
    else:
        q = db.comp_moduleset.id > 0
    rows = db(q).select(cacheable=True)
    modset_names = {}
    for row in rows:
        modset_names[row.id] = row.modset_name
    return modset_names

def get_modset_relations():
    # modset relation cache (modset ids)
    q = db.comp_moduleset_moduleset.id > 0
    rows = db(q).select(cacheable=True)
    modset_relations = {}
    for row in rows:
        if row.parent_modset_id in modset_relations:
            modset_relations[row.parent_modset_id] += [row.child_modset_id]
        else:
            modset_relations[row.parent_modset_id] = [row.child_modset_id]
    return modset_relations

def get_fset_relations():
    fset_relations = {}
    q = db.gen_filtersets_filters.encap_fset_id > 0
    rows = db(q).select()
    for row in rows:
        if row.fset_id not in fset_relations:
            fset_relations[row.fset_id] = [row.encap_fset_id]
        else:
            fset_relations[row.fset_id] += [row.encap_fset_id]
    return fset_relations

def get_fset_tree_nodes(fset_ids=None):
    fset_tree_nodes = {}
    fset_relations = get_fset_relations()

    if fset_ids is None:
        fset_ids = fset_relations.keys()

    def recurse_relations(head):
        l = []
        if head not in fset_relations:
            return l
        for child_id in fset_relations[head]:
            l.append(child_id)
            l += recurse_relations(child_id)
        return l

    for parent_id in fset_ids:
        fset_tree_nodes[parent_id] = recurse_relations(parent_id)

    return fset_tree_nodes

def _get_rset_relations():
    q = db.comp_rulesets_rulesets.id > 0
    q &= db.comp_rulesets_rulesets.child_rset_id == db.comp_rulesets.id
    rows = db(q).select(cacheable=True)
    rset_relations = {}
    for row in rows:
        if row.comp_rulesets_rulesets.parent_rset_id not in rset_relations:
            rset_relations[row.comp_rulesets_rulesets.parent_rset_id] = []
        rset_relations[row.comp_rulesets_rulesets.parent_rset_id].append(row.comp_rulesets_rulesets.child_rset_id)
    return rset_relations

def get_rset_tree_nodes(rset_ids=None):
    rset_tree_nodes = {}
    rset_relations = _get_rset_relations()

    if rset_ids is None:
        rset_ids = rset_relations.keys()

    def recurse_relations(head):
        l = []
        if head not in rset_relations:
            return l
        for child_id in rset_relations[head]:
            l.append(child_id)
            l += recurse_relations(child_id)
        return l

    for parent_id in rset_ids:
        rset_tree_nodes[parent_id] = recurse_relations(parent_id)

    return rset_tree_nodes


def get_modset_rset_relations():
    modset_rset_relations = {}
    q = db.comp_moduleset_ruleset.id > 0
    rows = db(q).select()
    for row in rows:
        if row.modset_id not in modset_rset_relations:
            modset_rset_relations[row.modset_id] = [row.ruleset_id]
        else:
            modset_rset_relations[row.modset_id] += [row.ruleset_id]
    return modset_rset_relations

def get_modset_rset_relations_s():
    modset_rset_relations = {}
    q = db.comp_moduleset_ruleset.id > 0
    q &= db.comp_moduleset_ruleset.ruleset_id == db.comp_rulesets.id
    q &= db.comp_moduleset_ruleset.modset_id == db.comp_moduleset.id
    rows = db(q).select()
    for row in rows:
        if row.comp_moduleset.modset_name not in modset_rset_relations:
            modset_rset_relations[row.comp_moduleset.modset_name] = [row.comp_rulesets.ruleset_name]
        else:
            modset_rset_relations[row.comp_moduleset.modset_name] += [row.comp_rulesets.ruleset_name]
    return modset_rset_relations

def get_fset_names(fset_ids=None):
    if fset_ids is not None:
        q = db.gen_filtersets.id.belongs(fset_ids)
    else:
        q = db.gen_filtersets.id > 0
    rows = db(q).select()
    fset_names = {}
    for row in rows:
        fset_names[row.id] = row.fset_name
    return fset_names

def get_rset_names(ruleset_ids=None):
    if ruleset_ids is None:
        q = db.comp_rulesets.id > 0
    elif type(ruleset_ids) == int:
        q = db.comp_rulesets.id = ruleset_ids
    elif type(ruleset_ids) == list:
        q = db.comp_rulesets.id.belongs(ruleset_ids)
    else:
        return {}
    rows = db(q).select(cacheable=True)
    rset_names = {}
    for row in rows:
        rset_names[row.id] = row.ruleset_name
    return rset_names



def _export_modulesets(modset_ids):
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)

    modset_ids_with_children = set(modset_ids)
    for modset_id, children in modset_tree_nodes.items():
        modset_ids_with_children |= set(children)

    modset_names =  get_modset_names(modset_ids_with_children)
    modset_relations = get_modset_relations()

    modset_relations_s = {}
    for modset_id, child_modset_ids in modset_relations.items():
        if modset_id not in modset_ids_with_children:
            continue
        modset_relations_s[modset_names[modset_id]] = map(lambda x: modset_names[x], child_modset_ids)

    q = db.comp_moduleset_modules.modset_id.belongs(modset_ids_with_children)
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    moduleset_modules = db(q).select()
    moduleset_modules_s = {}
    for row in moduleset_modules:
        if row.comp_moduleset.modset_name not in moduleset_modules_s:
            moduleset_modules_s[row.comp_moduleset.modset_name] = []
        d = {
          'modset_mod_name': row.comp_moduleset_modules.modset_mod_name,
          'autofix': row.comp_moduleset_modules.autofix,
        }
        moduleset_modules_s[row.comp_moduleset.modset_name].append(d)

    modset_rset_relations = get_modset_rset_relations()
    rset_names =  get_rset_names()
    rset_ids = set([])

    modset_rset_relations_s = {}
    for modset_id, _rset_ids in modset_rset_relations.items():
        if modset_id not in modset_ids_with_children:
            continue
        rset_ids |= set(_rset_ids)
        modset_rset_relations_s[modset_names[modset_id]] = map(lambda x: rset_names[x] , _rset_ids)

    data = _export_rulesets(rset_ids)

    #
    q = db.comp_moduleset.id.belongs(modset_ids_with_children)
    q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset_team_publication.group_id == db.auth_group.id
    rows = db(q).select()
    team_publication_s = {}
    for row in rows:
        if row.comp_moduleset.modset_name not in team_publication_s:
            team_publication_s[row.comp_moduleset.modset_name] = [row.auth_group.role]
        else:
            team_publication_s[row.comp_moduleset.modset_name] += [row.auth_group.role]

    #
    q = db.comp_moduleset.id.belongs(modset_ids_with_children)
    q &= db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset_team_responsible.group_id == db.auth_group.id
    rows = db(q).select()
    team_responsible_s = {}
    for row in rows:
        if row.comp_moduleset.modset_name not in team_responsible_s:
            team_responsible_s[row.comp_moduleset.modset_name] = [row.auth_group.role]
        else:
            team_responsible_s[row.comp_moduleset.modset_name] += [row.auth_group.role]

    # modulesets
    q = db.comp_moduleset.id.belongs(modset_ids_with_children)
    rows = db(q).select(db.comp_moduleset.id, db.comp_moduleset.modset_name)
    modulesets = []
    for row in rows:
        d = {
          'id': row.id,
          'modset_name': row.modset_name,
        }
        if row.modset_name in moduleset_modules_s:
            d['modules'] = moduleset_modules_s[row.modset_name]
        else:
            d['modules'] = []
        if row.modset_name in modset_relations_s:
            d['modulesets'] = modset_relations_s[row.modset_name]
        else:
            d['modulesets'] = []
        if row.modset_name in modset_rset_relations_s:
            d['rulesets'] = modset_rset_relations_s[row.modset_name]
        else:
            d['rulesets'] = []
        if row.modset_name in team_publication_s:
            d['publications'] = team_publication_s[row.modset_name]
        else:
            d['publications'] = []
        if row.modset_name in team_responsible_s:
            d['responsibles'] = team_responsible_s[row.modset_name]
        else:
            d['responsibles'] = []
        modulesets.append(d)

    data['modulesets'] = modulesets
    return data


def _export_rulesets(rset_ids):
    rset_names =  get_rset_names()
    rset_tree_nodes = get_rset_tree_nodes(rset_ids)
    rset_relations = _get_rset_relations()
    rset_ids_with_children = set(rset_ids)
    for _rset_ids in rset_tree_nodes.values():
        rset_ids_with_children |= set(_rset_ids)

    rset_relations_s = {}
    for rset_id, child_rset_ids in rset_relations.items():
        rset_relations_s[rset_names[rset_id]] = map(lambda x: rset_names[x], child_rset_ids)

    # ruleset vars
    q = db.comp_rulesets_variables.ruleset_id.belongs(rset_ids_with_children)
    q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    rows = db(q).select()
    ruleset_vars = {}
    for row in rows:
        if row.comp_rulesets.ruleset_name not in ruleset_vars:
            ruleset_vars[row.comp_rulesets.ruleset_name] = []
        d = {
          'id': row.comp_rulesets_variables.id,
          'var_name': row.comp_rulesets_variables.var_name,
          'var_value': row.comp_rulesets_variables.var_value,
          'var_class': row.comp_rulesets_variables.var_class,
          'var_author': row.comp_rulesets_variables.var_author,
          'var_updated': row.comp_rulesets_variables.var_updated.strftime("%Y-%m-%d %H:%M:%S"),
        }
        ruleset_vars[row.comp_rulesets.ruleset_name].append(d)

    #
    q = db.comp_rulesets.id.belongs(rset_ids_with_children)
    q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
    q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
    rows = db(q).select()
    team_publication_s = {}
    for row in rows:
        if row.comp_rulesets.ruleset_name not in team_publication_s:
            team_publication_s[row.comp_rulesets.ruleset_name] = [row.auth_group.role]
        else:
            team_publication_s[row.comp_rulesets.ruleset_name] += [row.auth_group.role]

    #
    q = db.comp_rulesets.id.belongs(rset_ids_with_children)
    q &= db.comp_ruleset_team_responsible.ruleset_id == db.comp_rulesets.id
    q &= db.comp_ruleset_team_responsible.group_id == db.auth_group.id
    rows = db(q).select()
    team_responsible_s = {}
    for row in rows:
        if row.comp_rulesets.ruleset_name not in team_responsible_s:
            team_responsible_s[row.comp_rulesets.ruleset_name] = [row.auth_group.role]
        else:
            team_responsible_s[row.comp_rulesets.ruleset_name] += [row.auth_group.role]


    # rulesets
    q = db.comp_rulesets.id.belongs(rset_ids_with_children)
    j1 = db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    l1 = db.comp_rulesets_filtersets.on(j1)
    j2 = db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id
    l2 = db.gen_filtersets.on(j2)
    rows = db(q).select(db.comp_rulesets.id,
                            db.comp_rulesets.ruleset_name,
                            db.comp_rulesets.ruleset_public,
                            db.comp_rulesets.ruleset_type,
                            db.gen_filtersets.id,
                            db.gen_filtersets.fset_name,
                            left=(l1,l2))

    rulesets = []
    fset_ids = []
    for row in rows:
        if row.gen_filtersets.id is not None:
            fset_ids.append(row.gen_filtersets.id)
        d = {
          'id': row.comp_rulesets.id,
          'ruleset_name': row.comp_rulesets.ruleset_name,
          'ruleset_public': row.comp_rulesets.ruleset_public,
          'ruleset_type': row.comp_rulesets.ruleset_type,
          'fset_name': row.gen_filtersets.fset_name
        }
        if row.comp_rulesets.ruleset_name in ruleset_vars:
            d['variables'] = ruleset_vars[row.comp_rulesets.ruleset_name]
        else:
            d['variables'] = []
        if row.comp_rulesets.ruleset_name in rset_relations_s:
            d['rulesets'] = rset_relations_s[row.comp_rulesets.ruleset_name]
        else:
            d['rulesets'] = []
        if row.comp_rulesets.ruleset_name in team_publication_s:
            d['publications'] = team_publication_s[row.comp_rulesets.ruleset_name]
        else:
            d['publications'] = []
        if row.comp_rulesets.ruleset_name in team_responsible_s:
            d['responsibles'] = team_responsible_s[row.comp_rulesets.ruleset_name]
        else:
            d['responsibles'] = []
        rulesets.append(d)

    data = _export_filtersets(fset_ids)
    data['rulesets'] = rulesets

    return data

def _export_filtersets(fset_ids):
    fset_tree_nodes = get_fset_tree_nodes(fset_ids)
    fset_ids_with_children = set(fset_ids)
    for fset_id, child_fset_ids in fset_tree_nodes.items():
        fset_ids_with_children |= set(child_fset_ids)
    fset_names = get_fset_names(fset_ids_with_children)

    # filtersets filters
    q = db.gen_filtersets_filters.fset_id.belongs(fset_ids_with_children)
    fset_filters_rows = db(q).select()
    filterset_filters = {}
    f_ids = set([])
    for row in fset_filters_rows:
        if row.f_id is not None:
            f_ids.add(row.f_id)

    # filters
    q = db.gen_filters.id.belongs(f_ids)
    rows = db(q).select()
    filters = {}
    for row in rows:
        d = {
          'id': row.id,
          'f_table': row.f_table,
          'f_field': row.f_field,
          'f_op': row.f_op,
          'f_value': row.f_value,
        }
        filters[row.id] = d

    for row in fset_filters_rows:
        fset_name = fset_names[row.fset_id]
        if fset_name not in filterset_filters:
            filterset_filters[fset_name] = []
        d = {
          'f_log_op': row.f_log_op,
          'f_order': row.f_order,
          'filter': filters[row.f_id] if row.f_id > 0 and row.f_id is not None else None,
          'filterset': fset_names[row.encap_fset_id] if row.encap_fset_id is not None else None,
        }
        filterset_filters[fset_name].append(d)


    q = db.gen_filtersets.id.belongs(fset_ids_with_children)
    rows = db(q).select()
    filtersets = []
    for row in rows:
        d = {
          'id': row.id,
          'fset_name': row.fset_name,
          'fset_stats': row.fset_stats,
          'filters': filterset_filters[row.fset_name] if row.fset_name in filterset_filters else [],
        }
        filtersets.append(d)

    return {
      'filtersets': filtersets,
    }

def export_modulesets(modset_ids):
    data = _export_modulesets(modset_ids)
    return json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)

def export_rulesets(rset_ids):
    data = _export_rulesets(rset_ids)
    return json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)

def export_filtersets(fset_ids):
    data = _export_filtersets(fset_ids)
    return json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)


#
# Designer functions
#
class CompError(Exception):
    pass

class CompInfo(Exception):
    pass

@auth.requires_membership('CompManager')
def create_moduleset(modset_name):
    q = db.comp_moduleset.modset_name == modset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        raise CompError("a moduleset named '%(modset_name)s' already exists"%dict(modset_name=modset_name))

    obj_id = db.comp_moduleset.insert(
      modset_name=modset_name,
      modset_author=user_name(),
      modset_updated=datetime.datetime.now(),
    )
    table_modified("comp_moduleset")
    add_default_teams_to_modset(modset_name)
    _log('compliance.moduleset.add',
         'added moduleset %(modset_name)s',
         dict(modset_name=modset_name))
    return obj_id

@auth.requires_membership('CompManager')
def delete_moduleset(modset_id):
    q = db.comp_moduleset.id == modset_id
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("moduleset not found or not owned by you")

    q = db.comp_node_moduleset.modset_id == modset_id
    db(q).delete()
    table_modified("comp_node_moduleset")

    q = db.comp_modulesets_services.modset_id == modset_id
    db(q).delete()
    table_modified("comp_modulesets_services")

    q = db.comp_moduleset_team_publication.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_team_publication")

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_team_responsible")

    q = db.comp_moduleset_modules.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_modules")

    q = db.comp_moduleset.id == modset_id
    db(q).delete()
    table_modified("comp_moduleset")

    q = db.comp_moduleset_moduleset.parent_modset_id == modset_id
    db(q).delete()
    q = db.comp_moduleset_moduleset.child_modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_moduleset")

    q = db.comp_moduleset_ruleset.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_ruleset")

    _log('compliance.moduleset.delete',
         'deleted moduleset %(modset_name)s',
         dict(modset_name=v.modset_name))

@auth.requires_membership('CompManager')
def create_ruleset(rset_name, published=True):
    if rset_name is None:
        raise Exception("The 'ruleset_name' key is mandatory")
    q = db.comp_rulesets.ruleset_name == rset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        raise CompError("a ruleset named '%(rset_name)s' already exists"%dict(rset_name=rset_name))

    obj_id = db.comp_rulesets.insert(
      ruleset_name=rset_name,
      ruleset_type="explicit",
      ruleset_public=published,
    )
    table_modified("comp_rulesets")
    add_default_teams(rset_name)
    _log('compliance.ruleset.add',
         'added ruleset %(rset_name)s',
         dict(rset_name=rset_name))
    comp_rulesets_chains()
    return obj_id

@auth.requires_membership('CompManager')
def delete_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    if 'Manager' not in user_groups():
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset not found or not owned by you")

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")

    q = db.comp_rulesets_nodes.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_nodes")

    q = db.comp_rulesets_services.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_services")

    q = db.comp_ruleset_team_publication.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_ruleset_team_publication")

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_ruleset_team_responsible")

    q = db.comp_rulesets_rulesets.parent_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")

    q = db.comp_rulesets_rulesets.child_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")

    q = db.comp_rulesets_variables.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_variables")

    q = db.comp_rulesets.id == rset_id
    db(q).delete()
    table_modified("comp_rulesets")

    q = db.comp_moduleset_ruleset.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_moduleset_ruleset")

    comp_rulesets_chains()

    _log('compliance.ruleset.delete',
         'deleted ruleset %(rset_name)s',
         dict(rset_name=v.ruleset_name))


def add_default_teams(ruleset_name):
    group_id = user_default_group_id()
    if group_id is None:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    q = db.comp_rulesets.ruleset_name == ruleset_name
    ruleset_id = db(q).select(cacheable=True)[0].id
    db.comp_ruleset_team_responsible.insert(ruleset_id=ruleset_id, group_id=group_id)
    table_modified("comp_ruleset_team_responsible")
    db.comp_ruleset_team_publication.insert(ruleset_id=ruleset_id, group_id=group_id)
    table_modified("comp_ruleset_team_publication")

def add_default_team_responsible_to_filterset(name):
    q = db.gen_filtersets.fset_name == name
    fset_id = db(q).select(cacheable=True)[0].id
    group_id = user_default_group_id()
    if group_id is None:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    db.gen_filterset_team_responsible.insert(fset_id=fset_id, group_id=group_id)
    table_modified("gen_filterset_team_responsible")

def add_default_teams_to_modset(modset_name):
    group_id = user_default_group_id()
    if group_id is None:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    q = db.comp_moduleset.modset_name == modset_name
    modset_id = db(q).select(cacheable=True)[0].id
    db.comp_moduleset_team_responsible.insert(modset_id=modset_id, group_id=group_id)
    table_modified("comp_moduleset_team_responsible")
    db.comp_moduleset_team_publication.insert(modset_id=modset_id, group_id=group_id)
    table_modified("comp_moduleset_team_publication")

@auth.requires_membership('CompManager')
def detach_moduleset_from_moduleset(child_modset_id, parent_modset_id):
    q = db.comp_moduleset.id == parent_modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("parent moduleset not found or not owned by you")

    q = db.comp_moduleset.id == child_modset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("child ruleset not found")

    q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
    q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
    db(q).delete()
    table_modified("comp_moduleset_moduleset")
    _log('compliance.moduleset.detach',
         'detach moduleset %(child_modset_name)s from moduleset %(parent_modset_name)s',
         dict(parent_modset_name=v.comp_moduleset.modset_name,
              child_modset_name=w.modset_name))
    #comp_rulesets_chains()

@auth.requires_membership('CompManager')
def detach_ruleset_from_moduleset(rset_id, modset_id):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("parent moduleset not found or not owned by you")

    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("child ruleset not found or not published to you")

    q = db.comp_moduleset_ruleset.modset_id == modset_id
    q &= db.comp_moduleset_ruleset.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_moduleset_ruleset")
    _log('compliance.ruleset.detach',
         'detach ruleset %(rset_name)s from moduleset %(modset_name)s',
         dict(rset_name=w.comp_rulesets.ruleset_name,
              modset_name=v.comp_moduleset.modset_name))
    #comp_rulesets_chains()

@auth.requires_membership('CompManager')
def detach_ruleset_from_ruleset(rset_id, parent_rset_id):
    q = db.comp_rulesets.id == parent_rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("parent ruleset not found or not owned by you")

    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("child ruleset not found or not published to you")

    q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
    q &= db.comp_rulesets_rulesets.child_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")
    _log('compliance.ruleset.detach',
         'detach ruleset %(rset_name)s from %(parent_rset_name)s',
         dict(rset_name=w.comp_rulesets.ruleset_name,
              parent_rset_name=v.comp_rulesets.ruleset_name))
    comp_rulesets_chains()

@auth.requires_membership('CompManager')
def detach_group_from_ruleset(group_id, rset_id, gtype="responsible"):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset not found or not owned by you")

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("group not found")

    q = db["comp_ruleset_team_"+gtype].ruleset_id == rset_id
    q &= db["comp_ruleset_team_"+gtype].group_id == group_id
    db(q).delete()
    table_modified("comp_ruleset_team_"+gtype)
    _log('compliance.ruleset.detach',
         'detach %(gtype)s group %(role)s from ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              gtype=gtype,
              role=w.role))
    ws_send('comp_rulesets_change', {'ruleset_id': rset_id, 'group_id': group_id})

@auth.requires_membership('CompManager')
def detach_group_from_moduleset(group_id, modset_id, gtype="responsible"):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("moduleset not found or not owned by you")

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("group not found")

    q = db["comp_moduleset_team_"+gtype].modset_id == modset_id
    q &= db["comp_moduleset_team_"+gtype].group_id == group_id
    db(q).delete()
    table_modified("comp_moduleset_team_"+gtype)
    _log('compliance.moduleset.detach',
         'detach %(gtype)s group %(role)s from moduleset %(modset_name)s',
         dict(modset_name=v.comp_moduleset.modset_name,
              gtype=gtype,
              role=w.role))
    ws_send('comp_moduleset_change',{'modset_id': modset_id, 'group_id': group_id})


@auth.requires_membership('CompManager')
def attach_ruleset_to_ruleset(rset_id, dst_rset_id):
    if dst_rset_id == rset_id:
        raise CompError("abort action to avoid introducing a recursion loop")

    q = db.comp_rulesets_rulesets.parent_rset_id == dst_rset_id
    q &= db.comp_rulesets_rulesets.child_rset_id == rset_id
    if db(q).count() > 0:
        raise CompError("ruleset already attached")

    q = db.comp_rulesets.id == rset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("attached ruleset not found")

    q2 = db.comp_rulesets.id == dst_rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("destination ruleset not found or not owned by you")

    if rset_loop(rset_id, dst_rset_id):
        raise CompError("the parent ruleset is already a child of the encapsulated ruleset. abort encapsulation not to cause infinite recursion")

    db.comp_rulesets_rulesets.insert(
      parent_rset_id=dst_rset_id,
      child_rset_id=rset_id,
    )
    table_modified("comp_rulesets_rulesets")
    _log('compliance.ruleset.attach',
         'attach ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name))
    comp_rulesets_chains()

@auth.requires_membership('CompManager')
def attach_ruleset_to_moduleset(rset_id, modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == modset_id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("moduleset not found or not owned by you")

    q = db.comp_rulesets.id == rset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("ruleset not found")

    q = db.comp_moduleset_ruleset.ruleset_id == rset_id
    q &= db.comp_moduleset_ruleset.modset_id == modset_id
    if db(q).count() > 0:
        return "0"

    db.comp_moduleset_ruleset.update_or_insert(ruleset_id=rset_id,
                                               modset_id=modset_id)
    table_modified("comp_moduleset_ruleset")
    _log('compliance.moduleset.ruleset.attach',
         'attach ruleset %(rset_name)s to moduleset %(modset_name)s',
         dict(modset_name=v.modset_name,
              rset_name=w.ruleset_name))

@auth.requires_membership('CompManager')
def create_module(modset_id, modset_mod_name):
    q = db.comp_moduleset.id == modset_id
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("moduleset does not exist or not owned by you")

    obj_id = db.comp_moduleset_modules.insert(
      modset_id=modset_id,
      modset_mod_name=modset_mod_name,
      modset_mod_author=user_name(),
      modset_mod_updated=datetime.datetime.now(),
    )
    table_modified("comp_moduleset_modules")
    _log('compliance.moduleset.module.add',
         'added module %(modset_mod_name)s in moduleset %(modset_name)s',
         dict(modset_mod_name=modset_mod_name,
              modset_name=v.modset_name))
    return obj_id

@auth.requires_membership('CompManager')
def create_variable(rset_id, var_name):
    q = db.comp_rulesets.id == rset_id
    if 'Manager' not in user_groups():
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset does not exist or not owned by you")

    obj_id = db.comp_rulesets_variables.insert(
      ruleset_id=rset_id,
      var_name=var_name,
      var_author=user_name(),
      var_updated=datetime.datetime.now(),
      var_class="raw",
      var_value="",
    )
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.add',
         'added variable %(var_name)s in ruleset %(rset_name)s',
         dict(var_name=var_name,
              rset_name=v.ruleset_name))
    return obj_id

@auth.requires_membership('CompManager')
def delete_module(mod_id):
    q = db.comp_moduleset_modules.id == mod_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_modules.modset_id
    v = db(q & q1).select(cacheable=True).first()
    if v is None:
        raise CompInfo("module does not exist")
    db(q).delete()
    table_modified("comp_moduleset_modules")
    _log('compliance.moduleset.module.delete',
         'deleted module %(modset_mod_name)s from moduleset %(modset_name)s',
         dict(modset_mod_name=v.comp_moduleset_modules.modset_mod_name,
              modset_name=v.comp_moduleset.modset_name))

@auth.requires_membership('CompManager')
def delete_variable(var_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
    v = db(q & q1).select(cacheable=True).first()
    if v is None:
        raise CompInfo("variable does not exist")
    db(q).delete()
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.delete',
         'deleted variable %(var_name)s from ruleset %(rset_name)s',
         dict(var_name=v.comp_rulesets_variables.var_name,
              rset_name=v.comp_rulesets.ruleset_name))

@auth.requires_membership('CompManager')
def attach_group_to_ruleset(group_id, rset_id, gtype="publication"):
    ug = user_groups()
    q = db.comp_rulesets.id == rset_id
    if 'Manager' not in ug:
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset not found or not owned by you")

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("group not found")

    if w.role == "Everybody":
        if gtype == "publication" and v.ruleset_type == "contextual":
            raise CompError("Publishing a contextual ruleset to Everybody is not allowed")
        if gtype == "responsible":
            raise CompError("Giving responsibility of a ruleset to Everybody is not allowed")
    if 'Manager' not in ug and int(group_id) not in user_group_ids():
        raise CompError("you can't attach a group you are not a member of")

    q = db["comp_ruleset_team_"+gtype].ruleset_id == rset_id
    q &= db["comp_ruleset_team_"+gtype].group_id == group_id
    if db(q).count() > 0:
        raise CompInfo(gtype+" group already attached")

    db["comp_ruleset_team_"+gtype].update_or_insert(ruleset_id=rset_id,
                                                      group_id=group_id)
    table_modified("comp_ruleset_team_"+gtype)
    _log('compliance.ruleset.change',
         'attach %(gtype)s group %(role)s to ruleset %(rset_name)s publications',
         dict(rset_name=v.ruleset_name,
              gtype=gtype,
              role=w.role))
    ws_send('comp_rulesets_change', {'ruleset_id': rset_id, 'group_id': group_id})

@auth.requires_membership('CompManager')
def attach_group_to_moduleset(group_id, modset_id, gtype="publication"):
    ug = user_groups()
    q = db.comp_moduleset.id == modset_id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("moduleset not found or not owned by you")

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("group not found")

    if w.role == "Everybody":
        if gtype == "responsible":
            raise CompError("Giving responsibility of a moduleset to Everybody is not allowed")
    if 'Manager' not in ug and int(group_id) not in user_group_ids():
        raise CompError("you can't attach a group you are not a member of")

    q = db["comp_moduleset_team_"+gtype].modset_id == modset_id
    q &= db["comp_moduleset_team_"+gtype].group_id == group_id
    if db(q).count() > 0:
        raise CompInfo(gtype+" group already attached")

    db["comp_moduleset_team_"+gtype].update_or_insert(modset_id=modset_id,
                                                      group_id=group_id)
    table_modified("comp_moduleset_team_"+gtype)
    _log('compliance.moduleset.change',
         'attach %(gtype)s group %(role)s to moduleset %(modset_name)s',
         dict(modset_name=v.modset_name,
              gtype=gtype,
              role=w.role))
    ws_send('comp_moduleset_change',{'modset_id': modset_id, 'group_id': group_id})

@auth.requires_membership('CompManager')
def attach_filterset_to_ruleset(fset_id, rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset not found or not owned by you")

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filterset not found")

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    q &= db.comp_rulesets_filtersets.fset_id == fset_id
    if db(q).count() > 0:
        return "0"

    db.comp_rulesets_filtersets.update_or_insert(db.comp_rulesets_filtersets.ruleset_id==rset_id,
                                                 ruleset_id=rset_id,
                                                 fset_id=fset_id)
    table_modified("comp_rulesets_filtersets")
    _log('compliance.ruleset.change',
         'attach filterset %(fset_name)s to ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              fset_name=w.fset_name))

@auth.requires_membership('CompManager')
def detach_filterset_from_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("ruleset not found or not owned by you")

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    q &= db.gen_filtersets.id == db.comp_rulesets_filtersets.fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filterset not found")

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")
    _log('compliance.filterset.detach',
         'detach filterset %(fset_name)s from ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              fset_name=w.gen_filtersets.fset_name))

@auth.requires_membership('CompManager')
def move_variable_to_ruleset(var_id, rset_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_responsible.ruleset_id
    q1 &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("variable not found or originating ruleset not owned by you")

    q2 = db.comp_rulesets.id == rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("destination ruleset not found or not owned by you")

    db(q).update(ruleset_id=rset_id)
    _log('compliance.variable.change',
         'move variable %(var_name)s from ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name,
              var_name=v.comp_rulesets_variables.var_name))

@auth.requires_membership('CompManager')
def copy_variable_to_ruleset(var_id, rset_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_publication.ruleset_id
    q1 &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("variable not found or originating ruleset not published to you")

    q2 = db.comp_rulesets.id == rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("destination ruleset not found or not owned by you")

    _v = v.comp_rulesets_variables
    obj_id = db.comp_rulesets_variables.insert(
      ruleset_id=rset_id,
      var_name=_v.var_name,
      var_class=_v.var_class,
      var_value=_v.var_value,
      var_author=user_name(),
      var_updated=datetime.datetime.now(),
    )
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.copy',
         'copy variable %(var_name)s from ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name,
              var_name=v.comp_rulesets_variables.var_name))
    return obj_id

@auth.requires_membership('CompManager')
def clone_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("source ruleset not found")

    rset_name = v.ruleset_name
    clone_rset_name = rset_name+"_clone"
    q = db.comp_rulesets.ruleset_name == clone_rset_name
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is not None:
        raise CompError("a ruleset named %s already exists" % clone_rset_name)

    newid = db.comp_rulesets.insert(ruleset_name=clone_rset_name,
                                    ruleset_type=v.ruleset_type,
                                    ruleset_public=v.ruleset_public)
    table_modified("comp_rulesets")

    # clone filterset for contextual rulesets
    if v.ruleset_type == 'contextual':
        q = db.comp_rulesets.id == rset_id
        q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
        rows = db(q).select(cacheable=True)
        if len(rows) > 0 and  rows[0].comp_rulesets_filtersets.fset_id is not None:
            db.comp_rulesets_filtersets.insert(ruleset_id=newid,
                                               fset_id=rows[0].comp_rulesets_filtersets.fset_id)
            table_modified("comp_rulesets_filtersets")

    # clone ruleset variables
    q = db.comp_rulesets_variables.ruleset_id == rset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_rulesets_variables.insert(ruleset_id=newid,
                                          var_name=row.var_name,
                                          var_class=row.var_class,
                                          var_value=row.var_value,
                                          var_author=user_name())
    table_modified("comp_rulesets_variables")
    add_default_teams(clone_rset_name)

    # clone parent to children relations
    q = db.comp_rulesets_rulesets.parent_rset_id==rset_id
    rows = db(q).select(cacheable=True)
    for child_rset_id in [r.child_rset_id for r in rows]:
        db.comp_rulesets_rulesets.insert(parent_rset_id=newid,
                                         child_rset_id=child_rset_id)
    table_modified("comp_rulesets_rulesets")

    comp_rulesets_chains()

    _log('compliance.ruleset.clone',
         'cloned ruleset %(o)s from %(n)s',
         dict(n=rset_name, o=clone_rset_name))

    return {"id": newid, "name": clone_rset_name}

@auth.requires_membership('CompManager')
def clone_moduleset(modset_id):
    q = db.comp_moduleset.id == modset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("source moduleset not found")

    modset_name = v.modset_name
    clone_modset_name = modset_name+"_clone"
    q = db.comp_moduleset.modset_name == clone_modset_name
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is not None:
        raise CompError("a moduleset named %s already exists" % clone_modset_name)

    newid = db.comp_moduleset.insert(modset_name=clone_modset_name,
                                     modset_author=user_name(),
                                     modset_updated=datetime.datetime.now())
    table_modified("comp_moduleset")

    # clone moduleset modules
    q = db.comp_moduleset_modules.modset_id == modset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_moduleset_modules.insert(modset_id=newid,
                                         modset_mod_name=row.modset_mod_name,
                                         modset_mod_author=row.modset_mod_author,
                                         modset_mod_updated=datetime.datetime.now())
    table_modified("comp_moduleset_modules")
    add_default_teams_to_modset(clone_modset_name)

    # clone moduleset-ruleset attachments
    q = db.comp_moduleset_ruleset.modset_id == modset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_moduleset_ruleset.insert(modset_id=newid,
                                         ruleset_id=row.ruleset_id)
    table_modified("comp_moduleset_ruleset")

    # clone moduleset-moduleset attachments
    q = db.comp_moduleset_moduleset.parent_modset_id == modset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_moduleset_moduleset.insert(parent_modset_id=newid,
                                         child_modset_id=row.child_modset_id)
    table_modified("comp_moduleset_moduleset")

    _log('compliance.moduleset.clone',
         'cloned moduleset %(o)s from %(n)s',
         dict(n=modset_name, o=clone_modset_name))

    return {"id": newid, "name": clone_modset_name}

#
# filtersets
#
def lib_filterset_id(fset_id):
    try:
        fset_id = int(fset_id)
        return fset_id
    except:
        q = db.gen_filtersets.fset_name == fset_id
        fset = db(q).select().first()
        if fset:
            return fset.id
        return

def lib_filter_id(f_id):
    try:
        f_id = int(f_id)
        return f_id
    except:
        q = db.gen_filters.f_label == f_id
        f = db(q).select().first()
        if f:
            return f.id
        return

@auth.requires_membership('CompManager')
def create_filterset(fset_name=None, fset_stats="F"):
    q = db.gen_filtersets.fset_name == fset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        CompError("a filterset named '%(name)s' already exists"%dict(name=fset_name))

    obj_id = db.gen_filtersets.insert(
      fset_name=fset_name,
      fset_stats=fset_stats,
      fset_author=user_name(),
      fset_updated=datetime.datetime.now(),
    )
    table_modified("gen_filtersets")
    _log('filterset.create',
         'added filterset %(name)s',
         dict(name=fset_name))
    ws_send('gen_filtersets_change', {'id': obj_id})
    return obj_id

@auth.requires_membership('CompManager')
def delete_filterset(fset_id):
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filterset not found")

    q = db.gen_filtersets_filters.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filtersets_filters")

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    db(q).delete()
    table_modified("gen_filtersets_filters")

    q = db.comp_rulesets_filtersets.fset_id == fset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")

    q = db.gen_filterset_team_responsible.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_team_responsible")

    q = db.gen_filterset_check_threshold.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_check_threshold")

    q = db.gen_filterset_user.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_user")

    q = db.stats_compare_fset.fset_id == fset_id
    db(q).delete()
    table_modified("stats_compare_fset")

    q = db.stat_day_billing.fset_id == fset_id
    db(q).delete()
    table_modified("stat_day_billing")

    q = db.gen_filtersets.id == fset_id
    db(q).delete()
    table_modified("gen_filtersets")

    _log('filterset.delete',
         'deleted filterset %(fset_name)s',
         dict(fset_name=v.fset_name))
    ws_send('gen_filtersets_change', {'id': fset_id})
    raise CompInfo("filterset deleted")

@auth.requires_membership('CompManager')
def detach_filterset_from_filterset(fset_id, parent_fset_id):
    q = db.gen_filtersets.id == parent_fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filterset not found")

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filterset not found")

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    q &= db.gen_filtersets_filters.fset_id == parent_fset_id
    if len(db(q).select()) == 0:
        raise CompInfo("filterset already detached")

    db(q).delete()
    table_modified("gen_filtersets_filters")
    _log('filterset.detach',
         'detach filterset %(fset_name)s from filterset %(parent_fset_name)s',
         dict(fset_name=w.fset_name,
              parent_fset_name=v.fset_name))
    ws_send('gen_filtersets_filters_change', {'parent_fset_id': parent_fset_id, 'fset_id': fset_id})
    raise CompInfo("filterset detached")

@auth.requires_membership('CompManager')
def detach_filter_from_filterset(f_id, fset_id):
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filterset not found")

    q = db.gen_filters.id == f_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filter not found")

    q = db.gen_filtersets_filters.f_id == f_id
    q &= db.gen_filtersets_filters.fset_id == fset_id
    if len(db(q).select()) == 0:
        raise CompInfo("filter already detached")

    db(q).delete()
    table_modified("gen_filtersets_filters")
    _log('filter.detach',
         'detach filter %(f_name)s from filterset %(fset_name)s',
         dict(fset_name=v.fset_name,
              f_name=w.f_table+'.'+w.f_field+' '+w.f_op+' '+w.f_value))
    ws_send('gen_filtersets_filters_change', {'f_id': f_id, 'fset_id': fset_id})
    raise CompInfo("filter detached")

@auth.requires_membership('CompManager')
def attach_filterset_to_filterset(fset_id, dst_fset_id, **vars):
    q = db.gen_filtersets.id == dst_fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filterset not found")

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filterset not found")

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    q &= db.gen_filtersets_filters.fset_id == dst_fset_id
    x = db(q).select().first()
    f_order = vars.get("f_order")
    f_log_op = vars.get("f_log_op")
    try:
        f_order = int(f_order)
    except:
        pass
    if x is not None and (f_order is None or x.f_order == f_order) and (f_log_op is None or x.f_log_op == f_log_op):
        raise CompInfo("filterset %s already attached to filterset %s" % (str(fset_id), str(dst_fset_id)))
    if "f_id" in vars:
        del(vars["f_id"])
    vars["fset_id"] = dst_fset_id
    vars["encap_fset_id"] = fset_id
    if x is None and "f_order" not in vars:
        vars["f_order"] = 0
    if x is None and "f_log_op" not in vars:
        vars["f_log_op"] = "AND"

    if x is not None:
        db(q).update(**vars)
    else:
        if fset_loop(fset_id, dst_fset_id):
            raise CompError("the parent filterset is already a child of the encapsulated filterset. abort encapsulation not to cause infinite recursion")
        db.gen_filtersets_filters.insert(**vars)

    table_modified("gen_filtersets_filters")

    _log('filterset.attach',
         'attach filterset %(fset_name)s to filterset %(dst_fset_name)s',
         dict(dst_fset_name=v.fset_name,
              fset_name=w.fset_name))
    ws_send('gen_filtersets_filters_change', {'parent_fset_id': dst_fset_id, 'fset_id': fset_id})
    raise CompInfo("filterset attached")

@auth.requires_membership('CompManager')
def attach_filter_to_filterset(f_id, fset_id, **vars):
    q = db.gen_filters.id == f_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filter %s not found" % str(f_id))

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        raise CompError("filterset %s not found" % str(fset_id))

    q = db.gen_filtersets_filters.f_id == f_id
    q &= db.gen_filtersets_filters.fset_id == fset_id
    rows = db(q).select(cacheable=True)
    x = rows.first()
    f_order = vars.get("f_order")
    f_log_op = vars.get("f_log_op")
    try:
        f_order = int(f_order)
    except:
        pass
    if x is not None and (f_order is None or x.f_order == f_order) and (f_log_op is None or x.f_log_op == f_log_op):
        raise CompInfo("filter %s already attached to filterset %s" % (str(f_id), str(fset_id)))
    vars["f_id"] = f_id
    vars["fset_id"] = fset_id
    vars["encap_fset_id"] = None
    if x is None and "f_order" not in vars:
        vars["f_order"] = 0
    if x is None and "f_log_op" not in vars:
        vars["f_log_op"] = "AND"
    if x is not None:
        db(q).update(**vars)
    else:
        db.gen_filtersets_filters.insert(**vars)
    table_modified("gen_filtersets_filters")

    _log('filter.attach',
         'attach filter %(f_name)s to filterset %(fset_name)s',
         dict(fset_name=w.fset_name,
              f_name=v.f_table+'.'+v.f_field+' '+v.f_op+' '+v.f_value))
    ws_send('gen_filtersets_filters_change', {'f_id': f_id, 'fset_id': fset_id})
    raise CompInfo("filter %s attached to filterset %s" % (str(f_id), str(fset_id)))

@auth.requires_membership('CompManager')
def delete_filter(f_id):
    q = db.gen_filters.id == f_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        raise CompError("filter not found")

    q = db.gen_filtersets_filters.f_id == f_id
    db(q).delete()
    table_modified("gen_filtersets_filters")

    q = db.gen_filters.id == f_id
    db(q).delete()
    table_modified("gen_filters")

    _log('filter.delete',
         'deleted filter %(t)s.%(f)s %(o)s %(val)s',
         dict(t=v.f_table, f=v.f_field, o=v.f_op, val=v.f_value))
    ws_send('gen_filters_change', {'id': f_id})
    raise CompInfo("filterset deleted")

@auth.requires_membership('CompManager')
def create_filter(f_table=None, f_field=None, f_op=None, f_value=None):
    tables = [
        'nodes',
        'services',
        'svcmon',
        'resmon',
        'apps',
        'node_hba',
        'diskinfo',
        'svcdisks',
        'v_comp_moduleset_attachments',
        'v_tags',
        'packages',
    ]
    operators = ['=', 'LIKE', '>', '>=', '<', '<=', 'IN']

    q = db.gen_filters.f_table == f_table
    q &= db.gen_filters.f_field == f_field
    q &= db.gen_filters.f_op == f_op
    q &= db.gen_filters.f_value == f_value
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        raise CompError("a filter with the same definition already exists: %d" % v.id)

    if f_table is None:
        raise CompError("f_table is mandatory")
    if f_field is None:
        raise CompError("f_field is mandatory")
    if f_op is None:
        raise CompError("f_op is mandatory")
    if f_value is None:
        raise CompError("f_value is mandatory")

    f_op = f_op.upper()
    if f_table not in tables:
        raise CompError("f_table must be one of %s" % ', '.join(tables))
    if f_op not in operators:
        raise CompError("f_op must be one of %s" % ', '.join(operators))

    if f_table not in db:
        raise CompError("table not found in model")
    if f_field not in db[f_table]:
        raise CompError("field not found in model's table")

    data = {
      "f_table": f_table,
      "f_field": f_field,
      "f_op": f_op,
      "f_value": f_value,
      "f_author": user_name(),
      "f_updated": datetime.datetime.now(),
    }
    obj_id = db.gen_filters.insert(**data)
    table_modified("gen_filters")
    _log('filter.create',
         'added filter %(t)s.%(f)s %(o)s %(val)s',
         dict(t=f_table, f=f_field, o=f_op, val=f_value))
    ws_send('gen_filters_change', {'id': obj_id})

    return obj_id

def lib_compliance_import(data):
    l = []
    u = user_name()
    now = datetime.datetime.now()

    # filters
    filter_id = {}
    for fset in data.get('filtersets', []):
        for f in fset.get('filters', []):
            _f = f.get('filter')
            if _f is None:
                continue
            if 'f_op' not in _f or \
               'f_field' not in _f or \
               'f_value' not in _f or \
               'f_table' not in _f:
                return T("Error: invalid filter format: %(r)s", dict(r=str(_f)))
            _f_s = _f['f_table']+'.'+_f['f_field']+' '+_f['f_op']+' '+_f['f_value']
            q = db.gen_filters.f_op == _f['f_op']
            q &= db.gen_filters.f_field == _f['f_field']
            q &= db.gen_filters.f_value == _f['f_value']
            q &= db.gen_filters.f_table == _f['f_table']
            row = db(q).select(db.gen_filters.id).first()
            if row is not None:
                filter_id[_f_s] = row.id
                l.append(T("Filter already exists: %(r)s", dict(r=_f_s)))
                continue
            n = db.gen_filters.insert(
              f_op=_f['f_op'],
              f_field=_f['f_field'],
              f_value=_f['f_value'],
              f_table=_f['f_table'],
              f_author=u,
              f_updated=now,
            )
            filter_id[_f_s] = n
            l.append(T("Filter added: %(r)s", dict(r=_f_s)))

    # filtersets
    filterset_id = {}
    for fset in data.get('filtersets', []):
        if 'fset_name' not in fset:
            return T("Error: invalid filterset format: %(r)s", dict(r=str(fset)))
        q = db.gen_filtersets.fset_name == fset['fset_name']
        row = db(q).select(db.gen_filtersets.id).first()
        if row is not None:
            filterset_id[fset['fset_name']] = row.id
            l.append(T("Filterset already exists: %(r)s", dict(r=fset['fset_name'])))
            # todo: verify the existing filterset has the same definition
            continue
        n = db.gen_filtersets.insert(
          fset_name=fset['fset_name'],
          fset_stats=False,
          fset_author=u,
          fset_updated=now,
        )
        filterset_id[fset['fset_name']] = n
        l.append(T("Filterset added: %(r)s", dict(r=fset["fset_name"])))

    # filtersets relations
    for fset in data.get('filtersets', []):
        fset_id = filterset_id[fset["fset_name"]]
        for f in fset.get('filters', []):
            _f = f.get('filter')
            encap_fset_name = f.get('filterset')
            if _f is not None:
                if 'f_op' not in _f or \
                   'f_field' not in _f or \
                   'f_value' not in _f or \
                   'f_table' not in _f:
                    return T("Error: invalid filter format: %(r)s", dict(r=str(_f)))
                _f_s = _f['f_table']+'.'+_f['f_field']+' '+_f['f_op']+' '+_f['f_value']
                f_id = filter_id[_f_s]
                rel_s = fset["fset_name"]+" -> "+f['f_log_op']+" "+_f_s+" (%s)"%str(f['f_order'])
                q = db.gen_filtersets_filters.fset_id == fset_id
                q &= db.gen_filtersets_filters.f_id == f_id
                q &= db.gen_filtersets_filters.f_log_op == f['f_log_op']
                q &= db.gen_filtersets_filters.f_order == f['f_order']
                row = db(q).select(db.gen_filtersets_filters.id).first()
                if row is not None:
                    l.append(T("Filterset relation already exists: %(r)s", dict(r=rel_s)))
                    continue
                n = db.gen_filtersets_filters.insert(
                  fset_id=fset_id,
                  f_id=f_id,
                  f_log_op=f['f_log_op'],
                  f_order=f['f_order'],
                  encap_fset_id=None,
                )
                l.append(T("Filterset relation added: %(r)s", dict(r=rel_s)))
            elif encap_fset_name is not None:
                f_id = filter_id[_f_s]
                encap_fset_id = filterset_id[encap_fset_name]
                rel_s = fset["fset_name"]+" -> "+f['f_log_op']+" "+encap_fset_name+" (%s)"%str(f['f_order'])
                q = db.gen_filtersets_filters.fset_id == fset_id
                q &= db.gen_filtersets_filters.encap_fset_id == encap_fset_id
                q &= db.gen_filtersets_filters.f_log_op == f['f_log_op']
                q &= db.gen_filtersets_filters.f_order == f['f_order']
                row = db(q).select(db.gen_filtersets_filters.id).first()
                if row is not None:
                    l.append(T("Filterset relation already exists: %(r)s", dict(r=rel_s)))
                    continue
                n = db.gen_filtersets_filters.insert(
                  fset_id=fset_id,
                  f_log_op=f['f_log_op'],
                  f_order=f['f_order'],
                  encap_fset_id=encap_fset_id,
                )
                l.append(T("Filterset relation added: %(r)s", dict(r=rel_s)))

    # rulesets
    ruleset_id = {}
    for rset in data.get('rulesets', []):
        if 'ruleset_name' not in rset or \
           'ruleset_type' not in rset or \
           'ruleset_public' not in rset:
            return T("Error: invalid ruleset format: %(r)s", dict(r=str(rset)))
        q = db.comp_rulesets.ruleset_name == rset['ruleset_name']
        row = db(q).select(db.comp_rulesets.id).first()
        if row is not None:
            ruleset_id[rset['ruleset_name']] = row.id
            l.append(T("Ruleset already exists: %(r)s", dict(r=rset['ruleset_name'])))
            # todo: verify the existing ruleset has the same definition
            continue
        n = db.comp_rulesets.insert(
          ruleset_name=rset['ruleset_name'],
          ruleset_type=rset['ruleset_type'],
          ruleset_public=rset['ruleset_public'],
        )
        add_default_teams(rset['ruleset_name'])
        ruleset_id[rset['ruleset_name']] = n
        l.append(T("Ruleset added: %(r)s", dict(r=rset["ruleset_name"])))

    # rulesets filterset
    for rset in data.get('rulesets', []):
        rset_id = ruleset_id[rset['ruleset_name']]
        fset_name = rset.get('fset_name')
        if fset_name is not None:
            rel_s = rset['ruleset_name']+" -> "+fset_name
            if fset_name in filterset_id:
                fset_id = filterset_id[fset_name]
            else:
                q = db.gen_filtersets.fset_name == fset_name
                fset_id = db(q).select().first().id
            q = db.comp_rulesets_filtersets.ruleset_id == rset_id
            q &= db.comp_rulesets_filtersets.fset_id == fset_id
            n = db(q).count()
            if n > 0:
                l.append(T("Ruleset filterset relation already exists: %(r)s", dict(r=rel_s)))
                continue
            n = db.comp_rulesets_filtersets.insert(
              ruleset_id=rset_id,
              fset_id=fset_id,
            )
            l.append(T("Ruleset filterset relation added: %(r)s", dict(r=rel_s)))

    # rulesets relations
    for rset in data.get('rulesets', []):
        parent_rset_id = ruleset_id[rset['ruleset_name']]
        for child_rset_name in rset.get('rulesets', []):
            rel_s = rset['ruleset_name']+" -> "+child_rset_name
            child_rset_id = ruleset_id[child_rset_name]
            q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
            q &= db.comp_rulesets_rulesets.child_rset_id == child_rset_id
            n = db(q).count()
            if n > 0:
                l.append(T("Ruleset relation already exists: %(r)s", dict(r=rel_s)))
                continue
            n = db.comp_rulesets_rulesets.insert(
              parent_rset_id=parent_rset_id,
              child_rset_id=child_rset_id,
            )
            l.append(T("Ruleset relation added: %(r)s", dict(r=rel_s)))

    # rulesets variables
    for rset in data.get('rulesets', []):
        rset_id = ruleset_id[rset['ruleset_name']]
        for var in rset.get('variables', []):
            if 'var_name' not in var or \
               'var_class' not in var or \
               'var_value' not in var:
                return T("Error: invalid variable format: %(r)s", dict(str(var)))
            var_s = rset['ruleset_name']+" :: "+var['var_name']+" (%s)"%var['var_class']
            q = db.comp_rulesets_variables.ruleset_id == rset_id
            q &= db.comp_rulesets_variables.var_name == var['var_name']
            q &= db.comp_rulesets_variables.var_class == var['var_class']
            q &= db.comp_rulesets_variables.var_value == var['var_value']
            n = db(q).count()
            if n > 0:
                l.append(T("Variable already exists: %(r)s", dict(r=var_s)))
                continue
            n = db.comp_rulesets_variables.update_or_insert(
              dict(
                  ruleset_id=rset_id,
                  var_name=var['var_name'],
              ),
              ruleset_id=rset_id,
              var_name=var['var_name'],
              var_class=var['var_class'],
              var_value=var['var_value'],
              var_updated=now,
              var_author=u,
            )
            l.append(T("Variable added: %(r)s", dict(r=var_s)))

    # modulesets
    moduleset_id = {}
    for modset in data.get('modulesets', []):
        if 'modset_name' not in modset:
            return T("Error: invalid moduleset format: %(r)s", dict(str(modset)))
        q = db.comp_moduleset.modset_name == modset['modset_name']
        row = db(q).select(db.comp_moduleset.id).first()
        if row is not None:
            moduleset_id[modset['modset_name']] = row.id
            l.append(T("Moduleset already exists: %(r)s", dict(r=modset['modset_name'])))
            # todo: verify the existing ruleset has the same definition
            continue
        n = db.comp_moduleset.insert(
          modset_name=modset['modset_name'],
          modset_author=u,
          modset_updated=now,
        )
        add_default_teams_to_modset(modset['modset_name'])
        moduleset_id[modset['modset_name']] = n
        l.append(T("Moduleset added: %(r)s", dict(r=modset["modset_name"])))

    # modulesets modules
    for modset in data.get('modulesets', []):
        modset_id = moduleset_id[modset["modset_name"]]
        for mod in modset.get("modules", []):
            if 'autofix' not in mod or \
               'modset_mod_name' not in mod:
                return T("Error: invalid module format: %(r)s", dict(r=str(mod)))
            rel_s = modset["modset_name"]+" :: "+mod['modset_mod_name']+ ' (%s)'%mod['autofix']
            q = db.comp_moduleset_modules.modset_id == modset_id
            q &= db.comp_moduleset_modules.modset_mod_name == mod['modset_mod_name']
            q &= db.comp_moduleset_modules.autofix == mod['autofix']
            n = db(q).count()
            if n > 0:
                l.append(T("Module already exists: %(r)s", dict(r=rel_s)))
                continue
            n = db.comp_moduleset_modules.insert(
              modset_id=modset_id,
              modset_mod_name=mod['modset_mod_name'],
              autofix=mod['autofix'],
              modset_mod_author=u,
              modset_mod_updated=now,
            )
            l.append(T("Module added: %(r)s", dict(r=rel_s)))

    # modulesets relations
    for modset in data.get('modulesets', []):
        parent_modset_id = moduleset_id[modset['modset_name']]
        for child_modset_name in modset.get('modulesets', []):
            rel_s = modset['modset_name']+" -> "+child_modset_name
            child_modset_id = moduleset_id[child_modset_name]
            q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
            q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
            n = db(q).count()
            if n > 0:
                l.append(T("Moduleset relation already exists: %(r)s", dict(r=rel_s)))
                continue
            n = db.comp_moduleset_moduleset.insert(
              parent_modset_id=parent_modset_id,
              child_modset_id=child_modset_id,
            )
            l.append(T("Moduleset relation added: %(r)s", dict(r=rel_s)))

    # modulesets rulesets
    for modset in data.get('modulesets', []):
        modset_id = moduleset_id[modset['modset_name']]
        for ruleset_name in modset.get('rulesets', []):
            rel_s = modset['modset_name']+" -> "+ruleset_name
            rset_id = ruleset_id[ruleset_name]
            q = db.comp_moduleset_ruleset.modset_id == modset_id
            q &= db.comp_moduleset_ruleset.ruleset_id == rset_id
            n = db(q).count()
            if n > 0:
                l.append(T("Moduleset ruleset relation already exists: %(r)s", dict(r=rel_s)))
                continue
            n = db.comp_moduleset_ruleset.insert(
              modset_id=modset_id,
              ruleset_id=rset_id,
            )
            l.append(T("Moduleset ruleset relation added: %(r)s", dict(r=rel_s)))

    comp_rulesets_chains()
    return l

