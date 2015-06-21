from gluon.dal import smart_query

#
class rest_get_groups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing groups.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups?query=email contains opensvc"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display group properties.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s?props=primary_group"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/groups/<id>",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        try:
            id = int(id)
            q &= db.auth_group.id == id
        except:
            q &= db.auth_group.role == id
        self.set_q(q)
        return self.prepare_data(**vars)



#
class rest_get_group_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List apps the group is responsible for.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/apps"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/apps",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        try:
            id = int(id)
            q &= db.auth_group.id == id
        except:
            q &= db.auth_group.role == id
        q &= db.apps_responsibles.group_id == db.auth_group.id
        q &= db.apps.id == db.apps_responsibles.app_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_group_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes the group is responsible for.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/nodes"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        try:
            id = int(id)
            q &= db.auth_group.id == id
        except:
            q &= db.auth_group.role == id
        q &= db.nodes.team_responsible == db.auth_group.role
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services the group is responsible for.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/services"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/services",
          tables=["services"],
          groupby=db.services.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        try:
            id = int(id)
            q &= db.auth_group.id == id
        except:
            q &= db.auth_group.role == id
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        q &= db.apps_responsibles.group_id == db.auth_group.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group_users(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List users member of the specified group.",
          "Managers and UserManager are allowed to see all groups.",
          "Others can only see their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/users"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/users",
          tables=["auth_user"],
          props_blacklist=["registration_key", "password"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            check_privilege("UserManager")
            q = db.auth_group.id > 0
        except:
            q = db.auth_group.id.belongs(user_group_ids())
        try:
            id = int(id)
            q &= db.auth_group.id == id
        except:
            q &= db.auth_group.role == id
        q &= db.auth_membership.group_id == db.auth_group.id
        q &= db.auth_user.id == db.auth_membership.user_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_groups(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a group.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=", ".join(sorted(db.auth_group.fields)),
      )
        examples = [
          "# curl -u %(email)s -o- -d role=NodeManager -d privilege=T https://%(collector)s/init/rest/api/groups",
        ]
        rest_post_handler.__init__(
          self,
          path="/groups",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("UserManager")
        db.auth_group.insert(**vars)
        _log('rest.groups.add',
             'add group %(data)s',
             dict(data=str(vars)),
            )
        l = {
          'event': 'auth_group',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return get_group(vars["role"])


#
class rest_post_group(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a group properties.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=", ".join(sorted(db.auth_group.fields)),
      )
        examples = [
          "# curl -u %(email)s -o- -d privilege=T https://%(collector)s/init/rest/api/groups/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/groups/<id>",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("UserManager")
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id
        row = db(q).select().first()
        if row is None:
            return dict(error="Group %s does not exist" % id)
        if "id" in vars.keys():
            del(vars["id"])
        db(q).update(**vars)
        l = []
        for key in vars:
            l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
        _log('rest.groups.change',
             'change group %(data)s',
             dict(data=', '.join(l)),
            )
        l = {
          'event': 'auth_group',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return get_group(row.id)


#
class rest_delete_group(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a group.",
          "Delete all group membership, apps/forms/rulesets/modulesets responsabilities and publications.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d role=NodeManager -d privilege=T https://%(collector)s/init/rest/api/groups",
        ]

        rest_delete_handler.__init__(
          self,
          path="/groups/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("UserManager")
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id

        row = db(q).select().first()
        if row is None:
            return dict(info="Group %s does not exists" % str(id))

        # group
        db(q).delete()
        _log('rest.groups.delete',
             'deleted group %(g)s',
             dict(g=row.role))
        l = {
          'event': 'auth_group',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))

        # apps responsibles
        q = db.apps_responsibles.group_id == row.id
        db(q).delete()

        # forms responsibles and publication
        q = db.forms_team_responsible.group_id == row.id
        db(q).delete()
        q = db.forms_team_publication.group_id == row.id
        db(q).delete()

        # modset responsibles
        q = db.comp_moduleset_team_responsible.group_id == row.id
        db(q).delete()

        # ruleset responsibles
        q = db.comp_ruleset_team_responsible.group_id == row.id
        db(q).delete()

        return dict(info="Group %s deleted" % row.role)

