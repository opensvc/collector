def lib_org_group(s):
    q = db.auth_group.id == s
    q |= db.auth_group.role == s
    if "Manager" not in user_groups():
        q &= db.auth_group.id.belongs(user_group_ids())
    rows = db(q).select()
    if len(rows) > 1:
        raise HTTP(400, "Ambiguous group id: %s" % str(s))
    if len(rows) == 0:
        raise HTTP(404, "Group not found: %s" % str(s))
    g = rows.first()
    if g.privilege:
        raise HTTP(403, "Operation not allowed on privilege group: %s" % str(g.role))
    return g

#
class rest_get_groups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing groups.",
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
class rest_get_group_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List modulesets published to the specified group.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/mygroup/modulesets"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/modulesets",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id
        q &= db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_moduleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List rulesets published to the specified group.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/mygroup/rulesets"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/rulesets",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id
        q &= db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group_users(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List users member of the specified group.",
          "Managers are allowed to see all groups.",
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
            check_privilege("Manager")
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
        self.get_handler = rest_get_groups()
        self.update_one_handler = rest_post_group()
        self.update_one_param = "role"
        desc = [
          "Create a group.",
          "Update groups matching the specified query.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d role=NodeManager -d privilege=T https://%(collector)s/init/rest/api/groups",
        ]
        rest_post_handler.__init__(
          self,
          path="/groups",
          tables=["auth_group"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if 'id' in vars:
            q = db.auth_group.id == vars["id"]
        elif 'role' in vars:
            q = db.auth_group.role == vars["role"]
        else:
            q = None
        if q:
            group = db(q).select().first()
            if group:
                return rest_post_group().handler(group.id, **vars)

        if 'privilege' in vars and vars["privilege"] in ("T", True):
            check_privilege("Manager")
        else:
            check_privilege("GroupManager")

        check_quota_org_group()

        group_id = db.auth_group.insert(**vars)
        ws_send("auth_group_change")
        table_modified("auth_group")

        db.auth_membership.insert(group_id=group_id, user_id=auth.user_id)
        table_modified("auth_membership")
        ws_send("auth_membership_change")

        _log('groups.add',
             'add group %(data)s',
             dict(data=beautify_data(vars)),
            )
        return rest_get_group().handler(vars["role"])


#
class rest_post_group(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a group properties.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d privilege=T https://%(collector)s/init/rest/api/groups/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/groups/<id>",
          tables=["auth_group"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        if 'privilege' in vars and vars["privilege"] in ("T", True):
            check_privilege("Manager")
        else:
            check_privilege("GroupManager")
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id
        try:
            check_privilege("Manager")
            q &= db.auth_group.id > 0
        except:
            q &= db.auth_group.id.belongs(user_group_ids())
        row = db(q).select().first()
        if row is None:
            return dict(error="Group %s does not exist" % str(id))
        if row.role == "Everybody":
            raise HTTP(400, "The 'Everybody' group is immutable")
        if "id" in vars.keys():
            del(vars["id"])
        db(q).update(**vars)
        fmt = "change group %(role)s: %(data)s"
        d = dict(role=row.role, data=beautify_change(row, vars))
        _log('groups.change', fmt, d)
        ws_send("auth_group_change")
        ret = rest_get_group().handler(row.id)
        ret["info"] = fmt % d
        return ret


#
class rest_delete_groups(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete groups.",
          "Delete all group membership, apps/forms/rulesets/modulesets responsabilities and publications.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/groups",
        ]

        rest_delete_handler.__init__(
          self,
          path="/groups",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            group_id = vars["id"]
        elif "role" in vars:
            group_id = vars["role"]
        else:
            raise HTTP(400, "Either the 'id' or the 'role' key is mandatory")
        return rest_delete_group().handler(group_id)

#
class rest_delete_group(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a group.",
          "Delete all group membership, apps/forms/rulesets/modulesets responsabilities and publications.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/groups/10",
        ]

        rest_delete_handler.__init__(
          self,
          path="/groups/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("GroupManager")
        try:
            id = int(id)
            q = db.auth_group.id == id
        except:
            q = db.auth_group.role == id
        try:
            check_privilege("Manager")
            q &= db.auth_group.id > 0
        except:
            q &= db.auth_group.id.belongs(user_group_ids())
            q &= db.auth_group.privilege == False

        row = db(q).select().first()
        if row is None:
            return dict(info="Group %s does not exists" % str(id))

        if row.role == "Everybody":
            raise HTTP(400, "The 'Everybody' group is immutable")

        # group
        db(q).delete()
        _log('groups.delete',
             'deleted group %(g)s',
             dict(g=row.role))
        ws_send("auth_group_change")

        # group membership
        q = db.auth_membership.group_id == row.id
        db(q).delete()
        table_modified("auth_membership")
        ws_send("auth_membership_change")

        # apps responsibles
        q = db.apps_responsibles.group_id == row.id
        db(q).delete()
        table_modified("apps_responsibles")
        ws_send("apps_responsible_change")

        # forms responsibles and publication
        q = db.forms_team_responsible.group_id == row.id
        db(q).delete()
        table_modified("forms_team_responsible")
        ws_send("forms_team_responsible_change")
        q = db.forms_team_publication.group_id == row.id
        db(q).delete()
        table_modified("forms_team_publication")
        ws_send("forms_team_publication_change")

        # modset responsibles
        q = db.comp_moduleset_team_responsible.group_id == row.id
        db(q).delete()
        table_modified("comp_moduleset_team_responsible")
        ws_send("comp_moduleset_team_responsible_change")

        # modset publications
        q = db.comp_moduleset_team_publication.group_id == row.id
        db(q).delete()
        table_modified("comp_moduleset_team_publication")
        ws_send("comp_moduleset_team_publication_change")

        # ruleset responsibles
        q = db.comp_ruleset_team_responsible.group_id == row.id
        db(q).delete()
        table_modified("comp_ruleset_team_responsible")
        ws_send("comp_ruleset_team_responsible_change")

        # ruleset publications
        q = db.comp_ruleset_team_publication.group_id == row.id
        db(q).delete()
        table_modified("comp_ruleset_team_publication")
        ws_send("comp_ruleset_team_publication_change")

        return dict(info="Group %s deleted" % row.role)

#
class rest_get_frontend_hidden_menu_entries(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List menu entries hidden from the menu for each group.",
          "Managers are allowed to all hidden menu entries.",
          "Others can only see hidden menu entries for their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/frontend/hidden_menu_entries"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/frontend/hidden_menu_entries",
          tables=["group_hidden_menu_entries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        try:
            check_privilege("Manager")
            q = db.group_hidden_menu_entries.id > 0
        except:
            q = db.group_hidden_menu_entries.group_id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_group_hidden_menu_entries(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List menu entries hidden from the menu for the specified group.",
          "Managers are allowed to all hidden menu entries.",
          "Others can only see hidden menu entries for their groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/1/hidden_menu_entries"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/groups/<id>/hidden_menu_entries",
          tables=["group_hidden_menu_entries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, group_id, **vars):
        try:
            group_id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id

        group = db(q).select().first()
        if group is None:
            return dict(info="Group %s does not exists" % str(group_id))

        if group.privilege:
            raise HTTP(400, "Can not set hidden menu entries for privilege groups")

        q = db.group_hidden_menu_entries.group_id == group_id
        try:
            check_privilege("Manager")
        except:
            q &= db.group_hidden_menu_entries.group_id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_post_group_hidden_menu_entries(rest_post_handler):
    def __init__(self):
        desc = [
          "Set menu entries as hidden for the specified group.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d 'menu_entry=key-f' https://%(collector)s/init/rest/api/groups/10/hidden_menu_entries",
        ]

        rest_post_handler.__init__(
          self,
          path="/groups/<id>/hidden_menu_entries",
          desc=desc,
          examples=examples,
        )

    def handler(self, group_id, **vars):
        check_privilege("GroupManager")

        if "menu_entry" not in vars:
            raise HTTP(400, "'menu_entry' key must be set")
        menu_entry = vars["menu_entry"]

        if menu_entry not in menu_entries:
            raise HTTP(400, "invalid menu entry %s" % menu_entry)

        try:
            group_id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        try:
            check_privilege("Manager")
            q &= db.auth_group.id > 0
        except:
            q &= db.auth_group.id.belongs(user_group_ids())

        group = db(q).select().first()
        if group is None:
            return dict(info="Group %s does not exists" % str(group_id))

        if "Manager" not in user_groups() and row.role == "Everybody":
            raise HTTP(400, "The 'Everybody' group is immutable")

        if group.privilege:
            raise HTTP(400, "Can not set hidden menu entries for privilege groups")

        q = db.group_hidden_menu_entries.group_id == group.id
        q &= db.group_hidden_menu_entries.menu_entry == menu_entry
        row = db(q).select().first()
        if row is not None:
            return dict(info="menu entry %s is already hidden for group %s" % (menu_entry, group.role))

        db.group_hidden_menu_entries.insert(group_id=group.id, menu_entry=menu_entry)
        _log('groups.hidden_menu_entries.add',
             'hide %(m)s for group %(g)s',
             dict(m=menu_entry, g=group.role))
        return dict(info="menu entry %s hidden for group %s" % (menu_entry, group.role))


class rest_delete_group_hidden_menu_entries(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unset menu entries as hidden for the specified group.",
          "The user must be in the GroupManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the changed tables.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE -d 'menu_entry=key-f' https://%(collector)s/init/rest/api/groups/10/hidden_menu_entries",
        ]

        rest_delete_handler.__init__(
          self,
          path="/groups/<id>/hidden_menu_entries",
          desc=desc,
          examples=examples,
        )

    def handler(self, group_id, **vars):
        check_privilege("GroupManager")

        if "menu_entry" not in vars:
            raise HTTP(400, "'menu_entry' key must be set")
        menu_entry = vars["menu_entry"]

        try:
            group_id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        try:
            check_privilege("Manager")
            q &= db.auth_group.id > 0
        except:
            q &= db.auth_group.id.belongs(user_group_ids())

        group = db(q).select().first()
        if group is None:
            return dict(info="Group %s does not exists" % str(group_id))

        if "Manager" not in user_groups() and row.role == "Everybody":
            raise HTTP(400, "The 'Everybody' group is immutable")

        if group.privilege:
            raise HTTP(400, "Can not set hidden menu entries for privilege groups")

        q = db.group_hidden_menu_entries.group_id == group.id
        q &= db.group_hidden_menu_entries.menu_entry == menu_entry
        row = db(q).select().first()
        if row is None:
            return dict(info="menu entry %s is already not hidden for group %s" % (menu_entry, group.role))

        db(q).delete()
        _log('groups.hidden_menu_entries.delete',
             'unhide %(m)s for group %(g)s',
             dict(m=menu_entry, g=group.role))

        return dict(info="menu entry %s unhidden for group %s" % (menu_entry, group.role))
