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

def app_responsible(app_id):
    if "Manager" in user_groups():
        return
    if app_id not in user_app_ids():
        raise Exception("You are not responsible for this app")

#
class rest_get_app_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/apps/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, app_id, **vars):
        app_id = lib_app_id(app_id)
        try:
            app_responsible(app_id)
            return dict(data=True)
        except:
            return dict(data=False)

#
class rest_get_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List application codes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "Manager" in user_groups():
            q = db.apps.id.belongs(user_app_ids())
        else:
            q = db.apps.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

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
        if not "Manager" in user_groups():
            q &= db.apps.id.belongs(user_app_ids())
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
        _vars = {}
        _vars.update(vars)
        if "id" in vars:
            app_id = vars["id"]
            del(_vars["id"])
        elif "app" in vars:
            app_id = vars["app"]
            del(_vars["app"])
        else:
            app_id = None
        if app_id and lib_app_id(app_id):
            return rest_post_app().handler(app_id, **_vars)

        check_privilege("AppManager")
        if len(vars) == 0 or "app" not in vars:
            raise Exception("Insufficient data: %s" % str(vars))
        check_quota_app()
        response = db.apps.validate_and_insert(**vars)
        raise_on_error(response)
        table_modified("apps")
        ws_send('apps_change')
        q = db.apps.id == response
        row = db(q).select().first()

        db.apps_responsibles.insert(app_id=row.id, group_id=user_default_group_id())
        table_modified("apps_responsibles")
        ws_send('apps_responsibles_change')
        db.apps_publications.insert(app_id=row.id, group_id=user_default_group_id())
        table_modified("apps_publications")
        ws_send('apps_publications_change')

        _log('apps.create',
             'app %(app)s created. data %(data)s',
             dict(app=row.app, data=beautify_data(vars)),
            )
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
        check_privilege("AppManager")
        id = lib_app_id(id)
        if id is None:
            return Exception("app code not found")
        app_responsible(id)
        q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("app %s does not exist" % str(id))
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        table_modified("apps")
        fmt = 'app %(app)s changed: %(data)s'
        d = dict(app=row.app, data=beautify_change(row, vars))
        _log('apps.change', fmt, d)
        ws_send('apps_change', {'id': row.id})
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
        check_privilege("AppManager")
        id = lib_app_id(id)
        if id is None:
            return dict(info="app code does not exist")
        app_responsible(id)
        q = db.apps.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="app code %s does not exist" % str(id))
        db(q).delete()
        table_modified("apps")
        ws_send('apps_change', {'id': row.id})

        q = db.apps_responsibles.app_id == row.id
        db(q).delete()
        table_modified("apps_responsibles")
        ws_send('apps_responsibles_change')

        q = db.apps_publications.app_id == row.id
        db(q).delete()
        table_modified("apps_publications")
        ws_send('apps_publications_change')

        _log('apps.delete',
             'app %(app)s deleted',
             dict(app=row.app),
            )
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
        if not "Manager" in user_groups():
            q &= db.apps.id.belongs(user_app_ids())
        q &= db.nodes.app == db.apps.app
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
        if not "Manager" in user_groups():
            q &= db.apps.id.belongs(user_app_ids())
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
        if not "Manager" in user_groups():
            q &= db.apps.id.belongs(user_app_ids())
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
        app_responsible(app_id)
        app = db(db.apps.id==app_id).select().first()
        group = lib_org_group(group_id)

        q = db.apps_responsibles.app_id == app_id
        q &= db.apps_responsibles.group_id == group_id
        row = db(q).select().first()
        if row is not None:
            raise Exception("group %s is already responsible for app %s" % (group.role, app.app))

        id = db.apps_responsibles.insert(app_id=app_id, group_id=group_id)

        fmt = 'app %(u)s responsibility given to group %(g)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_responsibles")
        _log('apps.responsible.add', fmt, d)

        ws_send('apps_responsibles_change', {'id': id})

        # remove dashboard alerts
        q = db.dashboard.dash_type == "application code without responsible"
        q &= db.dashboard.dash_dict.like('%%:"%s"%%'%app.app)
        db(q).delete()
        table_modified("dashboard")
        ws_send('dashboard_change')

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
        app_responsible(app_id)
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

        fmt = 'app %(u)s responsibility revoked for group %(g)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_responsibles")
        _log('apps.responsible.delete', fmt, d)

        ws_send('apps_responsibles_change', {'id': row.id})

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
        if not "Manager" in user_groups():
            q &= db.apps_responsibles.app_id.belongs(user_app_ids())
        q &= db.auth_group.id == db.apps_responsibles.group_id
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_post_apps_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach publication groups to application codes.",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -o- -X POST https://%(collector)s/init/rest/api/apps_publications",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps_publications",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "app_id" in vars:
            raise Exception("The 'app_id' key is mandatory")
        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_post_app_publication().handler(vars["app_id"], vars["group_id"])

class rest_post_app_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a publication group to an application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/apps/10/publications/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/apps/<id>/publications/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, app_id, group_id, **vars):
        check_privilege("AppManager")
        app_id = lib_app_id(app_id)
        if app_id is None:
            raise Exception("app code not found")
        app_responsible(app_id)
        app = db(db.apps.id==app_id).select().first()
        group = lib_org_group(group_id)

        q = db.apps_publications.app_id == app_id
        q &= db.apps_publications.group_id == group_id
        row = db(q).select().first()
        if row is not None:
            raise Exception("app %s is already unpublished to group %s" % (app.app, group.role))

        id = db.apps_publications.insert(app_id=app_id, group_id=group_id)

        fmt = 'app %(u)s published to group %(g)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_publications")
        _log('apps.publication.add', fmt, d)

        ws_send('apps_publications_change', {'id': id})

        # remove dashboard alerts
        q = db.dashboard.dash_type == "application code without publication"
        q &= db.dashboard.dash_dict.like('%%:"%s"%%'%app.app)
        db(q).delete()
        table_modified("dashboard")

        return dict(info=fmt % d)

class rest_delete_apps_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach publication groups from application codes.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/apps_publications",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps_publications",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "app_id" in vars:
            raise Exception("The 'app_id' key is mandatory")
        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_delete_app_publication().handler(vars["app_id"], vars["group_id"])

class rest_delete_app_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a publication group from a application code.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/apps/10/publications/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/apps/<id>/publications/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, app_id, group_id, **vars):
        check_privilege("AppManager")
        app_id = lib_app_id(app_id)
        if app_id is None:
            raise Exception("app code not found")
        app_responsible(app_id)
        app = db(db.apps.id==app_id).select().first()
        try:
            group_id = int(group_id)
        except:
            group_id = lib_group_id(group_id)
        if group_id is None:
            raise Exception("group not found")
        group = db(db.auth_group.id==group_id).select().first()

        q = db.apps_publications.app_id == app_id
        q &= db.apps_publications.group_id == group_id
        row = db(q).select().first()
        if row is None:
            raise Exception("app %s is already unpublished to group %s" % (app.app, group.role))

        db(q).delete()

        fmt = 'app %(u)s unpublished to group %(g)s'
        d = dict(g=group.role, u=app.app)

        table_modified("apps_publications")
        _log('apps.publication.delete', fmt, d)

        ws_send('apps_publications_change', {'id': row.id})

        return dict(info=fmt % d)

#
class rest_get_app_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an application code publication groups."
          "<id> can be either the proper id or the application code."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/publications"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/apps/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_app_id(id)
        q = db.apps_publications.app_id == id
        if not "Manager" in user_groups():
            q &= db.apps_publications.app_id.belongs(user_app_ids())
        q &= db.auth_group.id == db.apps_publications.group_id
        self.set_q(q)
        return self.prepare_data(**vars)



