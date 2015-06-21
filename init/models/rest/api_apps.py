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


