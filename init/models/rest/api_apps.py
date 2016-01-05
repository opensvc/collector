def lib_app_id(id):
    try:
        id = int(id)
        return id
    except:
        pass
    q = db.apps.app == id
    row = db(q).select(db.apps.id).first()
    if row is not None:
        return row.id

#
class rest_get_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List application codes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps"
        ]
        q = db.apps.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/apps",
          tables=["apps"],
          q=q,
          desc=desc,
          examples=examples,
        )

#
class rest_get_app(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display an application code properties.",
          "<id> can be either the proper id or the application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/10"
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/apps/<id>",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_apps(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_apps()
        self.update_one_handler = rest_post_app()
        self.update_one_param = "app"

        desc = [
          "Create an application code.",
          "Update applications matching the specified query.",
          "The user must be in the AppManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d app="MYPROJ" https://%(collector)s/init/rest/api/apps""",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            app_id = vars["id"]
            del(vars["id"])
            return rest_post_app(app_id, **vars)

        check_privilege("AppManager")
        if len(vars) == 0 or "app" not in vars:
            raise Exception("Insufficient data")
        q = db.apps.id > 0
        for v in vars:
            q &= db.apps[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return dict(info="App already exists")
        response = db.apps.validate_and_insert(**vars)
        raise_on_error(response)
        row = db(q).select().first()
        _log('apps.create',
             'app %(app)s created. data %(data)s',
             dict(app=row.app, data=str(vars)),
            )
        l = {
          'event': 'apps_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_app().handler(row.app)


#
class rest_post_app(rest_post_handler):
    def __init__(self):
        desc = [
          "Change an application code properties.",
          "The user must be in the AppManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d desc="Moui importante" https://%(collector)s/init/rest/api/apps/MYPROJ""",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps/<id>",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        if id is None:
            return Exception("app code not found")
        q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("app %s does not exist" % str(id))
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        fmt = 'app %(app)s changed: %(data)s'
        d = dict(app=row.app, data=beautify_change(row, vars))
        _log('apps.change', fmt, d)
        l = {
          'event': 'apps_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))
        ret = rest_get_app().handler(row.id)
        ret["info"] = fmt % d
        return ret


#
class rest_delete_apps(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete application codes.",
          "Also deletes all responsible group attachments",
          "The user must be in the AppManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/apps/MYPROJ""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            app_id = vars["id"]
        elif "app" in vars:
            app_id = vars["app"]
        else:
            raise Exception("Either the 'id' or 'app' key is mandatory")
        return rest_delete_app().handler(app_id)

#
class rest_delete_app(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete an application code.",
          "Also deletes all responsible group attachments",
          "The user must be in the AppManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/apps/MYPROJ""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        if id is None:
            return dict(info="app code does not exist")
        q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="app code %s does not exist" % str(id))
        db(q).delete()
        q = db.apps_responsibles.app_id == row.id
        db(q).delete()
        _log('apps.delete',
             'app %(app)s deleted',
             dict(app=row.app),
            )
        l = {
          'event': 'apps_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="app %(app)s deleted" % dict(app=row.app))


#
class rest_get_app_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes with the <id> application codes."
          "<id> can be either the proper id or the application code."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/nodes"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps.id == id
        q &= db.nodes.project == db.apps.app
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_app_quotas(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage disk group quotas usage for the <id> application code.",
          "<id> can be either the proper id or the application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/quotas"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps/<id>/quotas",
          tables=["v_disk_quota"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps.id == id
        q &= db.v_disk_quota.app == db.apps.app
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_app_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services with the <id> application codes.",
          "<id> can be either the proper id or the application code."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/services"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps/<id>/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps.id == id
        q &= db.services.svc_app == db.apps.app
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_post_apps_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach responsible groups to application codes.",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -o- -X POST https://%(collector)s/init/rest/api/apps_responsibles",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps_responsibles",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "app_id" in vars:
            raise Exception("The 'app_id' key is mandatory")
        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_post_app_responsible().handler(vars["app_id"], vars["group_id"])

class rest_post_app_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a responsible group to an application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/apps/10/responsibles/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps/<id>/responsibles/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, app_id, group_id, **vars):
        check_privilege("AppManager")
        app_id = lib_app_id(app_id)
        if app_id is None:
            raise Exception("app code not found")
        app = db(db.apps.id==app_id).select().first()
        try:
            group_id = int(group_id)
        except:
            group_id = lib_group_id(group_id)
        if group_id is None:
            raise Exception("group not found")
        group = db(db.auth_group.id==group_id).select().first()

        q = db.apps_responsibles.app_id == app_id
        q &= db.apps_responsibles.group_id == group_id
        row = db(q).select().first()
        if row is not None:
            raise Exception("group %s is already responsible for app %s" % (group.role, app.app))

        id = db.apps_responsibles.insert(app_id=app_id, group_id=group_id)

        fmt = 'attached group %(g)s to app %(u)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_responsibles")
        _log('apps.group.attach', fmt, d)

        l = {
          'event': 'apps_change',
          'data': {'id': id},
        }
        _websocket_send(event_msg(l))

        # remove dashboard alerts
        q = db.dashboard.dash_type == "application code without responsible"
        q &= db.dashboard.dash_dict.like('%%:"%s"%%'%app.app)
        db(q).delete()
        table_modified("dashboard")

        return dict(info=fmt % d)

class rest_delete_apps_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach responsible groups from application codes.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/apps_responsibles",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps_responsibles",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "app_id" in vars:
            raise Exception("The 'app_id' key is mandatory")
        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_delete_app_responsible().handler(vars["app_id"], vars["group_id"])

class rest_delete_app_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a responsible group from a application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/apps/10/responsibles/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps/<id>/responsibles/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, app_id, group_id, **vars):
        check_privilege("AppManager")
        app_id = lib_app_id(app_id)
        if app_id is None:
            raise Exception("app code not found")
        app = db(db.apps.id==app_id).select().first()
        try:
            group_id = int(group_id)
        except:
            group_id = lib_group_id(group_id)
        if group_id is None:
            raise Exception("group not found")
        group = db(db.auth_group.id==group_id).select().first()

        q = db.apps_responsibles.app_id == app_id
        q &= db.apps_responsibles.group_id == group_id
        row = db(q).select().first()
        if row is None:
            raise Exception("group %s is already not responsible for app %s" % (group.role, app.app))

        db(q).delete()

        fmt = 'detached group %(g)s from app %(u)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_responsibles")
        _log('apps.group.detach', fmt, d)

        l = {
          'event': 'apps_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))

        return dict(info=fmt % d)

#
class rest_get_app_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an application code responsible groups."
          "<id> can be either the proper id or the application code."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/responsibles"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps_responsibles.app_id == id
        q &= db.auth_group.id == db.apps_responsibles.group_id
        self.set_q(q)
        return self.prepare_data(**vars)



