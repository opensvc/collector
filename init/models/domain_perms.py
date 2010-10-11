domain_perm_magic = "abracadabra@0123456789"

def no_domain_perm(perms):
    if perms == domain_perm_magic:
        return True
    return False

@auth.requires_login()
def add_domain_perm(perm):
    perms = domain_perms()
    if perms is None:
        # collectors with no domain_permissions information
        return
    if no_domain_perm(perms):
        new_perms = perm
    else:
        perms_l = perms.split('|')
        if perm in perms_l:
            return
        new_perms = '|'.join(perms_l+[perm])
    q1 = db.auth_membership.user_id==session.auth.user.id
    q2 = db.domain_permissions.group_id==db.auth_membership.group_id
    rows = db(q1&q2).select(db.domain_permissions.id)
    if len(rows) == 0:
        db.domain_permissions.insert(group_id=auth.user_group(id),
                                     domains=new_perms)
    else:
        q = db.domain_permissions.id==rows[0].id
        db(q).update(domains=new_perms)

@auth.requires_login()
def domain_perms():
    domain_perms = domain_perm_magic
    rows = db(db.domain_permissions.id>0).select()
    if len(rows) == 0:
        # wildcard for collectors with no domain_permissions information
        domain_perms = None
    q1 = db.auth_membership.user_id==session.auth.user.id
    q2 = db.domain_permissions.group_id==db.auth_membership.group_id
    rows = db(q1&q2).select(db.domain_permissions.domains)
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


