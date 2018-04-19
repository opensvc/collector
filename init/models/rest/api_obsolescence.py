class rest_post_obsolescence_setting(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify an absolescence setting",
        ]
        examples = [
          """# curl -u %(email)s -X POST -d "obs_warn_date=2017-01-01" -o- https://%(collector)s/init/rest/api/obsolescence/settings/1"""
        ]

        rest_post_handler.__init__(
          self,
          path="/obsolescence/settings/<id>",
          tables=["obsolescence"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ObsManager")

        if "id" in vars:
            del(vars["id"])

        q = db.obsolescence.id == id
        setting = db(q).select().first()
        if setting is None:
            raise HTTP(404, "Obsolecence setting %s not found"%str(id))

        if "obs_name" in vars:
            raise HTTP(400, "The 'obs_name' key is not allowed")
        if "obs_type" in vars:
            raise HTTP(400, "The 'obs_name' key is not allowed")

        user = user_name()

        if "obs_warn_date" in vars:
            vars["obs_warn_date_updated_by"] = user
            vars["obs_warn_date_updated"] = datetime.datetime.now()
        if "obs_alert_date" in vars:
            vars["obs_alert_date_updated_by"] = user
            vars["obs_alert_date_updated"] = datetime.datetime.now()

        db(q).update(**vars)
        if "obs_warn_date" in vars:
            _update_nodes_fields(setting.obs_type, setting.obs_name,
                                 vars["obs_warn_date"], setting.obs_alert_date)
            delete_dash_obs_without(setting.obs_name, setting.obs_type, "warn")
        if "obs_alert_date" in vars:
            _update_nodes_fields(setting.obs_type, setting.obs_name,
                                 setting.obs_warn_date, vars["obs_alert_date"])
            delete_dash_obs_without(setting.obs_name, setting.obs_type, "alert")

        if setting.obs_type == "os":
            update_dash_obs_os_warn(setting.obs_name)
            update_dash_obs_os_alert(setting.obs_name)
        elif setting.obs_type == "hw":
            update_dash_obs_hw_alert(setting.obs_name)
            update_dash_obs_hw_warn(setting.obs_name)

        fmt = "Obsolescence setting %(obs_type)s:%(obs_name)s change: %(data)s"
        d = dict(obs_name=setting.obs_name, obs_type=setting.obs_type, data=beautify_change(setting, vars))

        _log('obsolescence.setting.change', fmt, d)
        ws_send("obsolescence_change", {'id': id})

        ret = rest_get_obsolescence_setting().handler(id)
        ret["info"] = fmt % d
        return ret

class rest_post_obsolescence_settings(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify absolescence settings",
        ]
        examples = [
          """# curl -u %(email)s -X POST -d "obs_warn_date=2017-01-01" -o- https://%(collector)s/init/rest/api/obsolescence/settings"""
        ]

        rest_post_handler.__init__(
          self,
          path="/obsolescence/settings",
          tables=["obsolescence"],
          props_blacklist=["obs_type", "obs_name"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("ObsManager")

        if "id" not in vars:
            raise HTTP(400, "Key 'id' is mandatory")
        id = vars.get("id")
        del(vars["id"])

        return rest_post_obsolescence_setting().handler(id, **vars)

class rest_get_obsolescence_setting(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List obsolescence settings.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/obsolescence/settings/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/obsolescence/settings/<id>",
          tables=["v_obsolescence"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_obsolescence.id == id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_get_obsolescence_settings(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List obsolescence settings.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/obsolescence/settings"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/obsolescence/settings",
          tables=["v_obsolescence"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.v_obsolescence.id > 0
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_obsolescence_setting(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete an obsolescence setting",
          "Requires the ObsManager privilege",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/obsolescence/settings/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/obsolescence/settings/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ObsManager")
        q = db.obsolescence.id == id

        row = db(q).select().first()
        if row is None:
            return dict(error="Obsolescence setting %s not found" % str(id))

        fmt = "Obsolescence setting %(obs_type)s:%(obs_name)s deleted"
        d = dict(obs_type=str(row.obs_type), obs_name=str(row.obs_name))

        db(q).delete()

        _log('obsolescence.setting.delete', fmt, d)
        ws_send("obsolescence_change", {'id': id})
        return dict(info=fmt%d)

class rest_delete_obsolescence_settings(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete obsolescence settings",
          "Requires the ObsManager privilege",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/obsolescence/settings?filters[]="obs_name %DL381%" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/obsolescence/settings",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "id" in vars:
            raise HTTP(400, "The 'id' key is mandatory")
        id = vars.get("id")
        del(vars["id"])

        return rest_delete_obsolescence_setting().handler(id, **vars)

#
class rest_put_obsolescence_refresh(rest_put_handler):
    def __init__(self):
        desc = [
          "Refresh the hardware models and os full names list in the obsolescence settings",
          "Requires the ObsManager privilege",
        ]
        data = {}
        examples = [
          """# curl -u %(email)s -X PUT -o- https://%(collector)s/init/rest/api/obsolescence/refresh"""
        ]

        rest_put_handler.__init__(
          self,
          path="/obsolescence/refresh",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, **vars):
        cron_obsolescence_os()
        cron_obsolescence_hw()
        purge_dash_obs_without()
        update_nodes_fields()
        ws_send("obsolescence_change")
        return dict(info="Obsolescence settings refreshed")



