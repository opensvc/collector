def domain_perms():
    domain_perms = "abracadabra@0123456789"
    rows = db(db.domain_permissions.id>0).select()
    if len(rows) == 0:
        # wildcard for collectors with no domain_permissions information
        domain_perms = None
    query = (db.auth_membership.user_id==session.auth.user.id)&(db.domain_permissions.group_id==db.auth_membership.group_id)
    rows = db(query).select(db.domain_permissions.domains)
    if len(rows) == 0:
        return domain_perms
    if rows[0]['domains'] is None:
        return domain_perms
    return rows[0]['domains']

def _domain_perms():
    dom = domain_perms()
    if dom is None:
        return '%'
    return dom


