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

