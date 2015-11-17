import json

def mangle_logs(data):
    for i, row in enumerate(data):
        try:
            data[i]['log_dict'] = json.loads(data[i]['log_dict'])
            data[i]['log_event'] = data[i]['log_fmt'] % data[i]['log_dict']
        except:
            pass
    return data

#
class rest_get_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List events in the collector log.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/logs?query=log_nodename contains clem"
        ]

        o = ~db.log.id
        q = db.log.id > 0

        rest_get_table_handler.__init__(
          self,
          path="/logs",
          tables=["log"],
          vprops={"log_event": ["log_fmt", "log_dict"]},
          vprops_fn=mangle_logs,
          q=q,
          orderby=o,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        data = self.prepare_data(**vars)
        return data

#
class rest_get_log(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a collector log event properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/logs/10"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/logs/<id>",
          tables=["log"],
          vprops={"log_event": ["log_fmt", "log_dict"]},
          vprops_fn=mangle_logs,
          desc=desc,
          examples=examples,
        )

    def handler(self, _id, **vars):
        q = db.log.id == int(_id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

