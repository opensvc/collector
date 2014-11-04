import re
from gluon.tools import Auth

def user_fullname(id):
    rows = db(db.auth_user.id==id).select()
    if len(rows) != 1:
        return None
    return ' '.join((rows[0].first_name, rows[0].last_name))

def group_role(id):
    rows = db(db.auth_group.id==id).select()
    if len(rows) != 1:
        return None
    return rows[0].role

def user_primary_group():
    sql = """select auth_group.role from
               auth_group,
               auth_membership
             where
               auth_membership.user_id = %(user_id)s and
               auth_membership.primary_group = 'T' and
               auth_membership.group_id = auth_group.id
             limit 1"""%dict(user_id=auth.user_id)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return None
    return rows[0][0]

def user_primary_group_id():
    sql = """select auth_group.id from
               auth_group,
               auth_membership
             where
               auth_membership.user_id = %(user_id)s and
               auth_membership.primary_group = 'T' and
               auth_membership.group_id = auth_group.id
             limit 1"""%dict(user_id=auth.user_id)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return None
    return rows[0][0]

def user_phone_work():
    q = db.auth_user.id == auth.user_id
    row = db(q).select(db.auth_user.phone_work).first()
    return row.phone_work

def user_email():
    q = db.auth_user.id == auth.user_id
    row = db(q).select(db.auth_user.email).first()
    return row.email

def user_groups():
    q = db.auth_membership.user_id==auth.user_id
    q &= db.auth_membership.group_id==db.auth_group.id
    rows = db(q).select(db.auth_group.role)
    return map(lambda x: x.role, rows)

def user_group_ids(id=None):
    if id is None:
        id = auth.user_id
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    rows = db(q).select(db.auth_group.id)
    return map(lambda x: x.id, rows)

def member_of(g):
    groups = user_groups()
    if isinstance(g, str) and g in groups:
        return True
    elif isinstance(g, list) or isinstance(g, tuple):
        for _g in g:
            if _g in groups:
                return True
    else:
        raise Exception("member_of_group param must be a role or a list of roles")
    return False

def email_of(u):
    sql = """select email from auth_user where concat(first_name, " ", last_name) = "%s" """ % u
    rows = db.executesql(sql)
    if len(rows) != 1:
        return
    return rows[0][0]

class MyAuth(Auth):
    def __init__(self, environment, db = None):
        Auth.__init__(self,environment,db)
        self.log_messages = [self.messages[k] for k in self.messages \
                             if self.messages[k] is not None and '_log' in k]
        self.log_patterns = [T(m).replace('%(id)s','(?P<id>[0-9]+)').replace('%(id)s','(?P<group_id>[0-9]+)') for m in self.log_messages]


    def log_event(self, description, vars=None, origin='auth'):
        Auth.log_event(self, description, vars, origin)
        # user_id is now set

        if description is None:
            return

        for i, p in enumerate(self.log_patterns):
            v = re.search(p, description)
            if v is None:
                continue
            d = v.groupdict()
            if 'id' in d:
                d['id'] = user_fullname(int(d['id']))
            if 'group_id' in d:
                d['group_id'] = group_role(int(d['group_id']))
            m = self.log_messages[i]
            action = [origin]
            if 'Registered' in m:
                 action.append('add')
            elif 'reset' in m or 'changed' in m or 'updated' in m:
                 action.append('change')
            _log('.'.join(action), m, d)
            return

    def update_groups(self):
        return

