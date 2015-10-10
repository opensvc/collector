from gluon.dal import smart_query
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

        q = db.dashboard.id > 0
        o = ~db.dashboard.id

        rest_get_table_handler.__init__(
          self,
          path="/alerts",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          orderby=o,
          q=q,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        data = self.prepare_data(**vars)
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

