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
def attach_modset_to_modset(child_modset_id, parent_modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == parent_modset_id
    if 'Manager' not in ug:
        q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        return {"error": "parent moduleset not found or not owned by you"}

    q = db.comp_moduleset.id == child_modset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"error": "child moduleset not found"}

    q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
    q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
    if db(q).count() > 0:
        return {"info": "already attached"}

    db.comp_moduleset_moduleset.update_or_insert(parent_modset_id=parent_modset_id,
                                                 child_modset_id=child_modset_id)
    table_modified("comp_moduleset_moduleset")
    fmt = 'attached moduleset %(child_modset_name)s to moduleset %(parent_modset_name)s'
    fmt_data = dict(child_modset_name=w.modset_name, parent_modset_name=v.modset_name)
    _log('compliance.moduleset.moduleset.attach', fmt, fmt_data)
    return {"info": fmt % fmt_data}


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

