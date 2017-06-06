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
class rest_get_user_dump(rest_get_handler):
    def __init__(self):
        desc = [
          "Display aggregate user information.",
          "Managers and UserManager are allowed to see all users.",
          "Others can only see users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/self/dump",
        ]
        rest_get_handler.__init__(
          self,
          path="/users/<id>/dump",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            if dev_mode:
                import uuid
                _code_rev = str(uuid.uuid4())
        except:
                _code_rev = code_rev
        return {
            "code_rev": _code_rev,
            "server_timezone": config_get("server_timezone", "Europe/Paris"),
            "user": rest_get_user().handler(id)["data"],
            "prefs": rest_get_user_prefs().handler(id)["data"],
            "groups": rest_get_user_groups().handler(id, limit=0)["data"],
            "filterset": rest_get_user_filterset().handler(id, meta=0)["data"],
            "internal_forms": form_data_internal,
            "hidden_menu_entries_stats": rest_get_user_hidden_menu_entries().handler(id, stats="menu_entry", props="menu_entry", limit=0, meta=0)["data"],
        }

#
class rest_get_user(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display user properties.",
          "Managers and UserManager are allowed to see all users.",
          "Others can only see users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s?props=lock_filter",
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
class rest_get_user_prefs(rest_get_handler):
    def __init__(self):
        desc = [
          "Fetch the user preferences: visible columns, column filters, live "
          "mode enabled flag, hidden group entries, ...",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/prefs"
        ]
        rest_get_handler.__init__(
          self,
          path="/users/<id>/prefs",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.auth_user.id == db.user_prefs.user_id
        row = db(q).select(db.user_prefs.prefs).first()
        if row is None or row.prefs is None:
            return {"data": {}}
        try:
            prefs = json.loads(row.prefs)
        except:
            prefs = {}
        return {"data": prefs}

#
class rest_post_user_prefs(rest_post_handler):
    def __init__(self):
        desc = [
          "Save the user preferences: visible columns, column filters, live "
          "mode enabled flag, hidden group entries, ...",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/users/%(email)s/prefs"
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>/prefs",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        row = db(q).select().first()
        if row is None:
            raise Exception("Not authorized")
        prefs = json.dumps(vars["data"])
        db.user_prefs.update_or_insert(
            {"user_id": row.id},
            user_id=row.id,
            prefs=prefs,
        )
        ws_send("user_prefs_change", {
            "user_id": row.id,
            "uuid": vars.get("uuid", ""),
        })
        return {"info": "user prefs saved"}

#
class rest_get_user_apps_responsible(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List apps the user is responsible for.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/apps/responsible",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/apps/responsible",
          tables=["apps"],
          desc=desc,
          groupby=db.apps.id,
          examples=examples,
        )

    def handler(self, id, **vars):
        if "Manager" in user_groups(id):
            q = db.apps.id > 0
        else:
            q = allowed_user_ids_q()
            q &= user_id_q(id)
            q &= db.apps_responsibles.group_id == db.auth_membership.group_id
            q &= db.auth_membership.user_id == db.auth_user.id
            q &= db.apps.id == db.apps_responsibles.app_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_user_apps_publication(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List apps visible to the user.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/apps/publication",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/apps/publication",
          tables=["apps"],
          desc=desc,
          groupby=db.apps.id,
          examples=examples,
        )

    def handler(self, id, **vars):
        if "Manager" in user_groups(id):
            q = db.apps.id > 0
        else:
            q = allowed_user_ids_q()
            q &= user_id_q(id)
            q &= db.apps_publications.group_id == db.auth_membership.group_id
            q &= db.auth_membership.user_id == db.auth_user.id
            q &= db.apps.id == db.apps_publications.app_id
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
          "# curl -u %(email)s -X POST -o- -d first_name=John -d last_name=Smith https://%(collector)s/init/rest/api/users",
        ]
        rest_post_handler.__init__(
          self,
          path="/users",
          tables=["auth_user"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if 'id' in vars:
            user_id = vars["id"]
            del(vars["id"])
            return rest_post_user().handler(user_id, **vars)

        check_privilege("UserManager")

        if "quota_docker_registries" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_docker_registries"])

        if "quota_app" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_app"])

        if "quota_org_group" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_org_group"])

        q = db.auth_user.id > 0
        if "email" in vars:
            q &= db.auth_user.email == vars["email"]
        elif "username" in vars:
            q &= db.auth_user.username == vars["username"]
        else:
            raise Exception("email or username are mandatory")
        user = db(q).select().first()
        if user is not None:
            return rest_post_user().handler(user.id, **vars)

        row = db.auth_user.validate_and_insert(**vars)
        if row.id is None:
            return dict(error=row.errors)
        if "password" in vars:
            vars["password"] = "xxxxx"
        _log('user.create',
             'add user %(data)s',
             dict(data=beautify_data(vars)),
            )
        ws_send("auth_user_change")
        table_modified("auth_user")

        user = db.auth_user(row.id)

        if auth.settings.create_user_groups:
            q = db.auth_group.role == "user_%d" % user.id
            group = db(q).select(db.auth_group.id).first()
            if group is None:
                group_id = auth.add_group(auth.settings.create_user_groups % user)
            else:
                group_id = group.id
            auth.add_membership(group_id, user.id)

        set_quota_app_on_register(user)
        set_quota_org_group_on_register(user)
        set_quota_docker_registries_on_register(user)
        do_create_app_on_register(user)
        do_membership_on_register(user)

        return rest_get_user().handler(row.id)


#
class rest_post_user(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a user properties.",
          "The user must be in the UserManager privilege group to modify tiers users properties.",
          "The user must be in the SelfManager privilege group to modify its user properties.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d first_name=joe https://%(collector)s/init/rest/api/users/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>",
          tables=["auth_user"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        q = user_id_q(id)
        row = db(q).select().first()
        if row is None:
            return dict(error="User %s does not exist" % str(id))
        if "id" in vars.keys():
            del(vars["id"])

        if row.id != auth.user_id:
            check_privilege("UserManager")
        else:
            # allow modifying our own primary group
            check_privilege(["UserManager", "SelfManager"])

        if "quota_docker_registries" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_docker_registries"])

        if "quota_app" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_app"])

        if "quota_org_group" in vars:
            try:
                check_privilege("QuotaManager")
            except:
                del(vars["quota_org_group"])

        if "username" in vars and not login_form_username:
            raise Exception(T("The 'username' property is updatable only with a collector setup for ldap authentication"))

        if "email" in vars and row.email == vars["email"]:
            # avoid the IS_IN_DB raising an undue error
            del vars["email"]

        result = db(q).validate_and_update(**vars)
        if len(result.errors.as_dict()) > 0:
            return dict(error=result.errors)
        if "password" in vars:
            vars["password"] = "xxxxx"
        l = []
        fmt = "change user %(email)s: %(data)s"
        d = dict(email=row.email, data=beautify_change(row, vars))
        _log('user.change', fmt, d)
        ws_send("auth_user_change")
        table_modified("auth_user")
        ret = rest_get_user().handler(row.id)
        ret["info"] = fmt % d
        return ret


#
class rest_delete_users(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete users.",
          "Delete all group membership.",
          "The user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/users",
        ]

        rest_delete_handler.__init__(
          self,
          path="/users",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'id' in vars:
            user_id = vars["id"]
            del(vars["id"])
        elif 'email' in vars:
            user_id = vars["email"]
            del(vars["email"])
        else:
            raise Exception("Either the 'id' or 'email' key is mandatory")
        return rest_delete_user().handler(user_id, **vars)

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
        ws_send("auth_user_change")

        # group membership
        q = db.auth_membership.user_id == row.id
        db(q).delete()
        table_modified("auth_membership")
        ws_send("auth_membership_change")

        return dict(info="User %s deleted" % row.email)

#
# /users/<id>/group...
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
        check_privilege("GroupManager")
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
        try:
            check_privilege("Manager")
        except:
            q &= db.auth_group.id.belongs(user_group_ids())

        group = db(q).select().first()
        if group is None:
            return dict(error="Group %s does not exist" % str(group_id))

        primary_group = vars.get("primary_group", "F")
        if primary_group in TRUE_VALUES:
            primary_group = True
        else:
            primary_group = False
        q = db.auth_membership.user_id == user.id
        q &= db.auth_membership.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            if row.primary_group == primary_group:
                return dict(info="User %s is already attached to group %s" % (str(user.email), str(group.role)))
            elif primary_group:
                return rest_post_user_primary_group().handler(user_id, group_id)
            elif row.primary_group == True:
                return rest_delete_user_primary_group().handler(user_id)

        db.auth_membership.insert(user_id=user_id, group_id=group_id, primary_group=primary_group)
        table_modified("auth_membership")
        _log('user.group.attach',
             'user %(u)s attached to group %(g)s',
             dict(u=user.email, g=group.role),
            )
        ws_send("auth_membership_change")
        table_modified("auth_membership")
        return dict(info="User %s attached to group %s" % (str(user.email), str(group.role)))


#
class rest_post_users_groups(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach users to groups.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the changes in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X POST https://%(collector)s/init/rest/api/users_groups",
        ]
        rest_post_handler.__init__(
          self,
          path="/users_groups",
          tables=["auth_membership"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if "user_id" not in vars:
            raise Exception("The 'user_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_post_user_group().handler(vars["user_id"], vars["group_id"])

#
class rest_delete_users_groups(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach users from groups.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the changes in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/users_groups",
        ]
        rest_delete_handler.__init__(
          self,
          path="/users_groups",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if "user_id" not in vars:
            raise Exception("The 'user_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_delete_user_group().handler(vars["user_id"], vars["group_id"])

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
        check_privilege("GroupManager")
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
        try:
            check_privilege("Manager")
        except:
            q &= db.auth_group.id.belongs(user_group_ids())
        group = db(q).select().first()
        if group is None:
            return dict(error="Group %s does not exist" % str(group_id))

        q = db.auth_membership.user_id == user.id
        q &= db.auth_membership.group_id == group.id
        row = db(q).select().first()
        if row is None:
            return dict(info="User %s is already detached from group %s" % (str(user.email), str(group.role)))

        db(q).delete()
        table_modified("auth_membership")
        _log('user.group.detach',
             'user %(u)s detached from group %(g)s',
             dict(u=user.email, g=group.role),
            )
        ws_send("auth_membership_change")
        return dict(info="User %s detached from group %s" % (str(user.email), str(group.role)))


#
# /users/<id>/primary_group
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
class rest_post_user_primary_group(rest_post_handler):
    def __init__(self):
        desc = [
          "Set a user's primary group.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/users/10/primary_group/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>/primary_group/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, group_id, **vars):
        if group_id in (0, "0"):
            return rest_delete_user_primary_group().handler(user_id)
        try:
            id = int(user_id)
            q = db.auth_user.id == user_id
        except:
            q = db.auth_user.email == user_id
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user_id))

        if user.id != auth.user_id:
            check_privilege("UserManager")
        else:
            # allow modifying our own primary group
            check_privilege(["UserManager", "SelfManager"])

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            return dict(error="Group %s does not exist" % str(group_id))

        q = db.auth_membership.user_id == user.id
        q &= db.auth_membership.group_id == group.id
        q &= db.auth_membership.primary_group == True
        row = db(q).select().first()
        if row is not None:
            return dict(info="User %s primary group is already %s" % (str(user.id), str(group.id)))

        q = db.auth_membership.user_id == user.id
        q &= db.auth_membership.primary_group == True
        db(q).delete()

        db.auth_membership.update_or_insert({
          "user_id": user.id,
          "group_id": group.id,
        }, user_id=user.id, group_id=group.id, primary_group=True)
        table_modified("auth_membership")
        _log('user.primary_group.set',
             'user %(u)s primary group set to %(g)s',
             dict(u=user.email, g=group.role),
            )
        ws_send("auth_membership_change")
        table_modified("auth_membership")
        return dict(info="User %s primary group set to %s" % (str(user.email), str(group.role)))


#
class rest_delete_user_primary_group(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unset a user's primary group.",
          "The api user must be in the UserManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/users/10/primary_group/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/users/<id>/primary_group",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, **vars):
        try:
            id = int(user_id)
            q = db.auth_user.id == user_id
        except:
            q = db.auth_user.email == user_id
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user.email))

        if user.id != auth.user_id:
            check_privilege("UserManager")
        else:
            # allow modifying our own primary group
            check_privilege(["UserManager", "SelfManager"])

        q = db.auth_membership.user_id == user.id
        q &= db.auth_membership.primary_group == 'T'
        row = db(q).select().first()
        if row is None:
            return dict(info="User %s has already no primary group" % str(user.email))

        db(q).update(primary_group=False)
        table_modified("auth_membership")
        _log('user.primary_group.unset',
             'user %(u)s primary group unset',
             dict(u=user.email),
            )
        ws_send("auth_membership_change")
        return dict(info="User %s primary group unset" % str(user.email))


#
# /users/<id>/filterset...
#
class rest_get_user_filterset(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the user's current filterset.",
          "Managers and UserManager are allowed to see all users' current filterset.",
          "Others can only see the current filterset of users in their organisational groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/filterset",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/users/<id>/filterset",
          tables=["gen_filtersets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = allowed_user_ids_q()
        q &= user_id_q(id)
        q &= db.gen_filterset_user.user_id == db.auth_user.id
        q &= db.gen_filtersets.id == db.gen_filterset_user.fset_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_user_filterset(rest_post_handler):
    def __init__(self):
        desc = [
          "Set a user's current filterset.",
          "The api user must be in the UserManager privilege group or the specified user himself.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/users/10/filterset/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/users/<id>/filterset/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, fset_id, **vars):
        q = user_id_q(user_id)
        q &= db.auth_user.id == auth.user_id
        row = db(q).select().first()
        if row is None:
            check_privilege("UserManager")

        q = user_id_q(user_id)
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user_id))

        if user.lock_filter:
            if "UserManager" not in user_groups():
                return dict(error="User %s filterset is locked" % str(user_id))

        try:
            id = int(fset_id)
            q = db.gen_filtersets.id == fset_id
        except:
            q = db.gen_filtersets.fset_name == fset_id
        fset = db(q).select().first()
        if fset is None:
            return dict(error="Filterset %s does not exist" % str(fset_id))

        q = db.gen_filterset_user.user_id == user.id
        q &= db.gen_filterset_user.fset_id == fset.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="User %s filterset is already %s" % (str(user.email), str(fset.fset_name)))

        q = db.gen_filterset_user.user_id == user.id
        db(q).delete()
        db.gen_filterset_user.insert(user_id=user.id, fset_id=fset.id)
        _log('user.filterset.attach',
             'user %(u)s filterset set to %(g)s',
             dict(u=user.email, g=fset.fset_name),
            )
        ws_send("gen_filterset_user_change", {
            'user_id': user.id,
            'fset_id': fset.id,
            'fset_name': fset.fset_name,
        })
        table_modified("gen_filterset_user")
        return dict(info="User %s filterset set to %s" % (str(user.email), str(fset.fset_name)))

#
class rest_delete_user_filterset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unset a user's current filterset.",
          "The api user must be in the UserManager privilege group or the specified user himself.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the users table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/users/10/filterset",
        ]
        rest_delete_handler.__init__(
          self,
          path="/users/<id>/filterset",
          desc=desc,
          examples=examples
        )

    def handler(self, user_id, **vars):
        q = user_id_q(user_id)
        q &= db.auth_user.id == auth.user_id
        row = db(q).select().first()
        if row is None:
            check_privilege("UserManager")

        q = user_id_q(user_id)
        user = db(q).select().first()
        if user is None:
            return dict(error="User %s does not exist" % str(user_id))

        if user.lock_filter:
            if "UserManager" not in user_groups():
                return dict(error="User %s filterset is locked" % str(user_id))

        q = db.gen_filterset_user.user_id == user.id
        row = db(q).select().first()
        if row is None:
            return dict(info="User %s has already no filterset" % str(user.email))
        db(q).delete()
        _log('user.filterset.detach',
             'user %(u)s filterset unset',
             dict(u=user.email),
            )
        ws_send('gen_filterset_user_delete', {'user_id': user.id})
        table_modified("gen_filterset_user")
        return dict(info="User %s filterset unset" % str(user.email))

#
class rest_get_user_hidden_menu_entries(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List menu entries hidden from the menu for the specified user.",
          "Managers and UserManager are allowed to all hidden menu entries.",
          "Others can only see hidden menu entries for their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/self/hidden_menu_entries"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/users/<id>/hidden_menu_entries",
          tables=["group_hidden_menu_entries"],
          desc=desc,
          groupby=db.group_hidden_menu_entries.group_id|db.group_hidden_menu_entries.menu_entry,
          examples=examples,
        )

    def handler(self, user_id, **vars):
        q = user_id_q(user_id)
        q &= db.auth_membership.user_id == db.auth_user.id
        q &= db.group_hidden_menu_entries.group_id == db.auth_membership.group_id
        q &= db.auth_membership.group_id == db.auth_group.id
        q &= db.auth_group.role != "Everybody"
        q &= db.auth_group.privilege == False
        try:
            check_privilege("UserManager")
        except:
            q = db.group_hidden_menu_entries.group_id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)


