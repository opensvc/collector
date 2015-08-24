from gluon.dal import smart_query

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
        _log('rest.apps.create',
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
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        _log('rest.apps.change',
             'app %(app)s changed. data %(data)s',
             dict(app=row.app, data=str(vars)),
            )
        l = {
          'event': 'apps_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_app().handler(row.app)


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
        db(q).delete()
        q = db.apps_responsibles.app_id == row.id
        db(q).delete()
        _log('rest.apps.delete',
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
        try:
            group_id = int(group_id)
        except:
            group_id = lib_group_id(group_id)
        if group_id is None:
            raise Exception("group not found")
        try:
            attach_group_to_app(group_id, app_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="group attached")

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
        try:
            group_id = int(group_id)
        except:
            group_id = lib_group_id(group_id)
        if group_id is None:
            raise Exception("group not found")
        try:
            detach_group_from_app(group_id, app_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="group detached")

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



