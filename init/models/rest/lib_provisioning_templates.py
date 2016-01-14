def lib_provisioning_templates_add_default_team_responsible(tpl_id):
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.prov_template_team_responsible.insert(tpl_id=tpl_id, group_id=group_id)


