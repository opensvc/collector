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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: int(id)
            except: return dict(data=[])
            q = db.apps.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_apps(rest_post_handler):
    def __init__(self):
        desc = [
          "Create an application code.",
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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: int(id)
            except: return dict(data=[])
            q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            return dict(error="App does not exists")
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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: int(id)
            except: return dict(data=[])
            q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="app %(app)s does not exist" % dict(app=id))
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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: id = int(id)
            except: return dict(data=[])
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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: int(id)
            except: return dict(data=[])
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
        q = db.apps.app == id
        n = db(q).count()
        if n == 0:
            try: int(id)
            except: return dict(data=[])
            q = db.apps.id == id
        q &= db.services.svc_app == db.apps.app
        self.set_q(q)
        return self.prepare_data(**vars)


