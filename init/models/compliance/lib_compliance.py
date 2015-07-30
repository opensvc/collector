import copy

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

def comp_moduleset_svc_attachable(svcname, modset_id):
    q = db.services.svc_name == svcname
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

def comp_ruleset_svc_attachable(svcname, rset_id):
    q = db.services.svc_name == svcname
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

def comp_moduleset_attachable(nodename, modset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    q &= db.nodes.nodename == nodename
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) != 1:
        return False
    return True

def comp_ruleset_attachable(nodename, ruleset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
    q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == ruleset_id
    q &= db.comp_rulesets.ruleset_public == True
    q &= db.comp_rulesets.ruleset_type == "explicit"
    q &= db.nodes.nodename == nodename
    rows = db(q).select(cacheable=True)
    if len(rows) != 1:
        return False
    return True

def comp_moduleset_attached(nodename, modset_id):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == modset_id
    if len(db(q).select(db.comp_node_moduleset.id, cacheable=True)) == 0:
        return False
    return True

def comp_ruleset_svc_attached(svcname, rset_id, slave):
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.ruleset_id == rset_id
    q &= db.comp_rulesets_services.slave == slave
    if len(db(q).select(db.comp_rulesets_services.id, cacheable=True)) == 0:
        return False
    return True

def comp_moduleset_svc_attached(svcname, modset_id, slave):
    q = db.comp_modulesets_services.modset_svcname == svcname
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

def comp_ruleset_attached(nodename, ruleset_id):
    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if len(db(q).select(db.comp_rulesets_nodes.id, cacheable=True)) == 0:
        return False
    return True

def comp_slave(svcname, nodename):
    q = db.svcmon.mon_vmname == nodename
    q &= db.svcmon.mon_svcname == svcname
    row = db(q).select(cacheable=True).first()
    if row is None:
        return False
    return True

def has_slave(svcname):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_vmname != None
    q &= db.svcmon.mon_vmname != ""
    row = db(q).select(cacheable=True).first()
    if row is None:
        return False
    return True

def comp_attached_ruleset_id(nodename):
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id, cacheable=True)
    return [r.ruleset_id for r in rows]

def comp_attached_svc_moduleset_id(svcname):
    q = db.comp_modulesets_services.modset_svcname == svcname
    rows = db(q).select(db.comp_modulesets_services.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

def comp_attached_moduleset_id(nodename):
    q = db.comp_node_moduleset.modset_node == nodename
    rows = db(q).select(db.comp_node_moduleset.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

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

def comp_attached_svc_ruleset_id(svcname, slave):
    q = db.comp_rulesets_services.svcname == svcname
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
def lib_comp_moduleset_attach_node(nodename, modset_id):
    moduleset = comp_moduleset_name(modset_id)
    if moduleset is None:
        return dict(error="moduleset %s does not exist"%moduleset)
    if comp_moduleset_attached(nodename, modset_id):
        return dict(info="moduleset %s is already attached to this node"%moduleset)
    if not comp_moduleset_attachable(nodename, modset_id):
        return dict(error="moduleset %s is not attachable"%moduleset)

    n = db.comp_node_moduleset.insert(modset_node=nodename,
                                      modset_id=modset_id)
    table_modified("comp_node_moduleset")
    update_dash_moddiff_node(nodename)

    if n == 0:
        return dict(error="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.node.attach',
         '%(moduleset)s attached to node %(node)s',
         dict(node=nodename, moduleset=moduleset),
         nodename=nodename,
    )
    return dict(info="moduleset %s attached"%moduleset)


def lib_comp_moduleset_detach_node(nodename, modset_id):
    if type(modset_id) == list:
        moduleset = "all"
        if len(modset_id) == 0:
            return dict(info="this node has no moduleset attached")
    else:
        moduleset = comp_moduleset_name(modset_id)
        if moduleset is None:
            return dict(error="moduleset %s does not exist"%moduleset)
        if not comp_moduleset_attached(nodename, modset_id):
            return dict(info="moduleset %s is not attached to this node"%moduleset)
    q = db.comp_node_moduleset.modset_node == nodename
    if isinstance(modset_id, list):
        q &= db.comp_node_moduleset.modset_id.belongs(modset_id)
    else:
        q &= db.comp_node_moduleset.modset_id == modset_id
    n = db(q).delete()
    table_modified("comp_node_moduleset")
    if n == 0:
        return dict(error="failed to detach the moduleset")
    update_dash_moddiff_node(nodename)

    _log('compliance.moduleset.node.detach',
         '%(moduleset)s detached from node %(node)s',
         dict(node=nodename, moduleset=moduleset),
         nodename=nodename,
    )
    return dict(info="moduleset %s detached"%moduleset)


def lib_comp_moduleset_detach_service(svcname, modset_id, slave=False):
    if type(modset_id) == list:
        moduleset = "all"
        if len(modset_id) == 0:
            return dict(info="this service has no moduleset attached")
    else:
        moduleset = comp_moduleset_name(modset_id)
        if moduleset is None:
            return dict(error="moduleset %s does not exist"%moduleset)
        if not comp_moduleset_svc_attached(svcname, modset_id, slave):
            return dict(info="moduleset %s is not attached to this service"%moduleset)
    q = db.comp_modulesets_services.modset_svcname == svcname
    if isinstance(modset_id, list):
        q &= db.comp_modulesets_services.modset_id.belongs(modset_id)
    else:
        q &= db.comp_modulesets_services.modset_id == modset_id
    n = db(q).delete()
    table_modified("comp_modulesets_services")
    if n == 0:
        return dict(error="failed to detach the moduleset")
    _log('compliance.moduleset.service.detach',
         '%(moduleset)s detached from service %(svcname)s',
         dict(svcname=svcname, moduleset=moduleset),
         svcname=svcname,
    )
    return dict(info="moduleset %s detached"%moduleset)


def lib_comp_moduleset_attach_service(svcname, modset_id, slave):
    moduleset = comp_moduleset_name(modset_id)
    if moduleset is None:
        return dict(error="moduleset %s does not exist"%moduleset)
    if comp_moduleset_svc_attached(svcname, modset_id, slave):
        return dict(info="moduleset %s is already attached to this service"%moduleset)
    if not comp_moduleset_svc_attachable(svcname, modset_id):
        return dict(error="moduleset %s is not attachable"%moduleset)
    n = db.comp_modulesets_services.insert(modset_svcname=svcname,
                                           modset_id=modset_id,
                                           slave=slave)
    table_modified("comp_modulesets_services")
    if n == 0:
        return dict(error="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.service.attach',
         '%(moduleset)s attached to service %(svcname)s',
        dict(svcname=svcname, moduleset=moduleset),
        svcname=svcname,
    )
    return dict(info="moduleset %s attached"%moduleset)

#
# ruleset attachments
#
def lib_comp_ruleset_attach_node(nodename, ruleset_id):
    ruleset = comp_ruleset_name(ruleset_id)
    if ruleset is None:
        return dict(error="ruleset %s does not exist"%ruleset)
    if comp_ruleset_attached(nodename, ruleset_id):
        return dict(info="ruleset %s is already attached to this node"%ruleset)
    if not comp_ruleset_attachable(nodename, ruleset_id):
        return dict(error="ruleset %s is not attachable"%ruleset)

    n = db.comp_rulesets_nodes.insert(nodename=nodename,
                                      ruleset_id=ruleset_id)
    table_modified("comp_rulesets_nodes")
    update_dash_rsetdiff_node(nodename)

    if n == 0:
        return dict(error="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.node.attach',
         '%(ruleset)s attached to node %(node)s',
         dict(node=nodename, ruleset=ruleset),
         nodename=nodename,
    )
    return dict(info="ruleset %s attached"%ruleset)


def lib_comp_ruleset_detach_node(nodename, ruleset_id):
    if type(ruleset_id) == list:
        ruleset = "all"
        if len(ruleset_id) == 0:
            return dict(info="this node has no ruleset attached")
    else:
        ruleset = comp_ruleset_name(ruleset_id)
        if ruleset is None:
            return dict(error="ruleset %s does not exist"%ruleset)
        if not comp_ruleset_attached(nodename, ruleset_id):
            return dict(info="ruleset %s is not attached to this node"%ruleset)
    q = db.comp_rulesets_nodes.nodename == nodename
    if isinstance(ruleset_id, list):
        q &= db.comp_rulesets_nodes.ruleset_id.belongs(ruleset_id)
    else:
        q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    n = db(q).delete()
    table_modified("comp_rulesets_nodes")
    if n == 0:
        return dict(error="failed to detach the ruleset")
    update_dash_rsetdiff_node(nodename)

    _log('compliance.ruleset.node.detach',
         '%(ruleset)s detached from node %(node)s',
         dict(node=nodename, ruleset=ruleset),
         nodename=nodename,
    )
    return dict(info="ruleset %s detached"%ruleset)


def lib_comp_ruleset_detach_service(svcname, ruleset_id, slave=False):
    if type(ruleset_id) == list:
        ruleset = "all"
        if len(ruleset_id) == 0:
            return dict(info="this service has no ruleset attached")
    else:
        ruleset = comp_ruleset_name(ruleset_id)
        if ruleset is None:
            return dict(error="ruleset %s does not exist"%ruleset)
        if not comp_ruleset_svc_attached(svcname, ruleset_id, slave):
            return dict(info="ruleset %s is not attached to this service"%ruleset)
    q = db.comp_rulesets_services.svcname == svcname
    if isinstance(ruleset_id, list):
        q &= db.comp_rulesets_services.ruleset_id.belongs(ruleset_id)
    else:
        q &= db.comp_rulesets_services.ruleset_id == ruleset_id
    n = db(q).delete()
    table_modified("comp_rulesets_services")
    if n == 0:
        return dict(error="failed to detach the ruleset")
    _log('compliance.ruleset.service.detach',
         '%(ruleset)s detached from service %(svcname)s',
         dict(svcname=svcname, ruleset=ruleset),
         svcname=svcname,
    )
    return dict(info="ruleset %s detached"%ruleset)


def lib_comp_ruleset_attach_service(svcname, ruleset_id, slave):
    ruleset = comp_ruleset_name(ruleset_id)
    if ruleset is None:
        return dict(error="ruleset %s does not exist"%ruleset)
    if comp_ruleset_svc_attached(svcname, ruleset_id, slave):
        return dict(info="ruleset %s is already attached to this service"%ruleset)
    if not comp_ruleset_svc_attachable(svcname, ruleset_id):
        return dict(error="ruleset %s is not attachable"%ruleset)
    n = db.comp_rulesets_services.insert(svcname=svcname,
                                           ruleset_id=ruleset_id,
                                           slave=slave)
    table_modified("comp_rulesets_services")
    if n == 0:
        return dict(error="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.service.attach',
         '%(ruleset)s attached to service %(svcname)s',
        dict(svcname=svcname, ruleset=ruleset),
        svcname=svcname,
    )
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
          'var_name': row.comp_rulesets_variables.var_name,
          'var_value': row.comp_rulesets_variables.var_value,
          'var_class': row.comp_rulesets_variables.var_class,
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
          'fset_name': row.fset_name,
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
def create_ruleset(rset_name):
    q = db.comp_rulesets.ruleset_name == rset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        raise CompError("a ruleset named '%(rset_name)s' already exists"%dict(rset_name=rset_name))

    obj_id = db.comp_rulesets.insert(
      ruleset_name=rset_name,
      ruleset_type="explicit",
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
    group_id = user_primary_group_id()
    if group_id is None:
        group_id = user_private_group_id()
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
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select(cacheable=True)[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    db.gen_filterset_team_responsible.insert(fset_id=fset_id, group_id=group_id)
    table_modified("gen_filterset_team_responsible")

def add_default_teams_to_modset(modset_name):
    group_id = user_primary_group_id()
    if group_id is None:
        group_id = user_private_group_id()
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


