import json

def mangle_alerts(data):
    for i, row in enumerate(data):
        try:
            data[i]['dash_dict'] = json.loads(data[i]['dash_dict'])
            data[i]['alert'] = data[i]['dash_fmt'] % data[i]['dash_dict']
        except:
            pass
    return data

#
class rest_get_alerts(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing alerts.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alerts?query=not dash_type contains save"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/alerts",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          orderby=~db.dashboard.id,
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = db.dashboard.id > 0
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, node_field=db.dashboard.node_id, fset_id=fset_id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        data["data"] = mangle_alerts(data["data"])
        return data

#
class rest_get_alert(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display an alert properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alerts/10"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/alerts/<id>",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          desc=desc,
          examples=examples,
        )

    def handler(self, _id, **vars):
        q = db.dashboard.id == int(_id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        data["data"] = mangle_alerts(data["data"])
        return data

#
class rest_delete_alert(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete an alert",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/alerts/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/alerts/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")

        q = db.dashboard.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("Alert %s not found"%str(id))

        db(q).delete()
        table_modified("dashboard")
        ws_send('dashboard_change', {'id': id})

        fmt = "Alert %(id)s deleted"
        d = dict(id=str(id))

        _log('alert.del', fmt, d)

        return dict(info=fmt%d)

class rest_delete_alerts(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete multiple alerts",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -d id=1 -o- https://%(collector)s/init/rest/api/alerts"
        ]

        rest_delete_handler.__init__(
          self,
          path="/alerts",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        return rest_delete_alert().handler(**vars)

