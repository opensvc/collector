from gluon.dal import smart_query

def allowed_user_ids():
    q = db.auth_membership.group_id.belongs(user_group_ids())
    rows = db(q).select(db.auth_membership.user_id)
    return [r.user_id for r in rows]

def allowed_user_ids_q():
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)
    return q

def user_id_q(id):
    if type(id) in (unicode, str) and "@" in id:
        q = db.auth_user.email == id
    else:
        q = db.auth_user.id == id
    return q


#
class rest_get_users(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing users.",
          "Managers and UserManager are allowed to see all users.",
          "Others can only see users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users?query=email contains opensvc",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users",
          tables=["auth_user"],
          props_blacklist=["password", "registration_key"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = allowed_user_ids_q()
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_user(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display user properties.",
          "Managers and UserManager are allowed to see all users.",
          "Others can only see users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s?props=primary_group",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/users/<id>",
          tables=["auth_user"],
          props_blacklist=["password", "registration_key"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_user_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List apps the user is responsible for.",
          "Managers and UserManager are allowed to see all users' information.",
          "Others can only see information for users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/apps",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/apps",
          tables=["apps"],
          desc=desc,
          groupby=db.apps.id,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == db.auth_user.id
        q &= db.apps.id == db.apps_responsibles.app_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_user_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes the user is responsible of.",
          "Managers and UserManager are allowed to see all users' information.",
          "Others can only see information for users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/nodes",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.nodes.team_responsible == db.auth_group.role
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == db.auth_user.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_user_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services the user is responsible of.",
          "Managers and UserManager are allowed to see all users' information.",
          "Others can only see information for users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/services",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/services",
          tables=["services"],
          groupby=db.services.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == db.auth_user.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_user_groups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups the user is member of.",
          "Managers and UserManager are allowed to see all users' information.",
          "Others can only see information for users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/groups",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/groups",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.auth_membership.user_id == db.auth_user.id
        q &= db.auth_group.id == db.auth_membership.group_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_user_primary_group(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the user's primary group properties.",
          "Managers and UserManager are allowed to see all users' information.",
          "Others can only see information for users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/primary_group",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/users/<id>/primary_group",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.auth_membership.user_id == db.auth_user.id
        q &= db.auth_membership.primary_group == True
        q &= db.auth_group.id == db.auth_membership.group_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_users(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_users()
        self.update_one_handler = rest_post_user()
        self.update_one_param = "email"

        desc = [
          "Create a user.",
          "Update users matching the specified query."
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d first_name=John -d last_name=Smith https://%(collector)s/init/rest/api/users",
        ]
        rest_post_handler.__init__(
          self,
          path="/users",
          tables=["auth_user"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("UserManager")
        obj_id = db.auth_user.insert(**vars)
        _log('user.create',
             'add user %(data)s',
             dict(data=str(vars)),
            )
        l = {
          'event': 'auth_user',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_user().handler(obj_id)


#
class rest_post_user(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a user properties.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d perpage=20 https://%(collector)s/init/rest/api/users/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>",
          tables=["auth_user"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("UserManager")
        try:
            id = int(id)
            q = db.auth_user.id == id
        except:
            q = db.auth_user.email == id
        row = db(q).select().first()
        if row is None:
            return dict(error="User %s does not exist" % str(id))
        if "id" in vars.keys():
            del(vars["id"])
        db(q).update(**vars)
        l = []
        for key in vars:
            l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
        _log('user.change',
             'change user %(data)s',
             dict(data=', '.join(l)),
            )
        l = {
          'event': 'auth_user',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_user().handler(row.id)


#
class rest_delete_user(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a user.",
          "Delete all group membership.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/users/10",
        ]

        rest_delete_handler.__init__(
          self,
          path="/users/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("UserManager")
        try:
            id = int(id)
            q = db.auth_user.id == id
        except:
            q = db.auth_user.email == id

        row = db(q).select().first()
        if row is None:
            return dict(info="User %s does not exists" % str(id))

        # group
        db(q).delete()
        _log('user.delete',
             'deleted user %(email)s',
             dict(email=row.email))
        l = {
          'event': 'auth_user',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))

        # group membership
        q = db.auth_membership.user_id == row.id
        db(q).delete()

        return dict(info="User %s deleted" % row.email)

#
class rest_post_user_group(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a user to a group.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/users/10/groups/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>/groups/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, group_id, **vars):
        check_privilege("UserManager")
        try:
            id = int(user_id)
            q = db.auth_user.id == user_id
        except:
            q = db.auth_user.email == user_id
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user_id))

        try:
            id = int(id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            return dict(error="Group %s does not exist" % str(group_id))

        q = db.auth_membership.user_id == user_id
        q &= db.auth_membership.group_id == group_id
        row = db(q).select().first()
        if row is not None:
            return dict(error="User %s is already attached to group %s" % (str(user_id), str(group_id)))

        db.auth_membership.insert(user_id=user_id, group_id=group_id)
        _log('user.group.attach',
             'user %(u)s attached to group %(g)s',
             dict(u=user.email, g=group.role),
            )
        l = {
          'event': 'auth_user',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="User %s attached to group %s" % (str(user_id), str(group_id)))


#
class rest_delete_user_group(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a user from a group.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/users/10/groups/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/users/<id>/groups/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, group_id, **vars):
        check_privilege("UserManager")
        try:
            id = int(user_id)
            q = db.auth_user.id == user_id
        except:
            q = db.auth_user.email == user_id
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user_id))

        try:
            id = int(id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            return dict(error="Group %s does not exist" % str(group_id))

        q = db.auth_membership.user_id == user_id
        q &= db.auth_membership.group_id == group_id
        row = db(q).select().first()
        if row is None:
            return dict(error="User %s is already detached from group %s" % (str(user_id), str(group_id)))

        db(q).delete()
        _log('user.group.detach',
             'user %(u)s detached from group %(g)s',
             dict(u=user.email, g=group.role),
            )
        l = {
          'event': 'auth_user',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="User %s detached from group %s" % (str(user_id), str(group_id)))




