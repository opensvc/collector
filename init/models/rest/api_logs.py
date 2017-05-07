import json

def mangle_logs(data):
    for i, row in enumerate(data):
        if "log" in data[i] and isinstance(data[i]["log"], dict):
            try:
                data[i]["log"]['log_dict'] = json.loads(data[i]["log"]['log_dict'])
                data[i]["log"]['log_event'] = data[i]["log"]['log_fmt'] % data[i]["log"]['log_dict']
            except:
                pass
        else:
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
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/logs"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/logs",
          tables=["log"],
          vprops={"log_event": ["log_fmt", "log_dict"]},
          vprops_fn=mangle_logs,
          orderby=~db.log.id,
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = db.log.id > 0
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, node_field=db.log.node_id, svc_field=db.log.svc_id, fset_id=fset_id)
        self.set_q(q)

        return self.prepare_data(**vars)

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

#
class rest_post_logs(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a log event",
          "The entry type is forced to 'message'",
          "The default level is 'info'",
          "Empty log events are discarded",
        ]
        examples = [
          """# curl -u %(email)s -o- -d node_id=d446fee3-328d-4493-9db9-b1118600bee8 -d log_entry="Zanzibar" https://%(collector)s/init/rest/api/logs""",
        ]
        rest_post_handler.__init__(
          self,
          path="/logs",
          tables=["log"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        vars["log_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vars["log_action"] = "message"
        if "log_level" not in vars:
            vars["log_level"] = "info"

        if "log_fmt" not in vars or vars["log_fmt"] is None or \
           len(str(vars["log_fmt"])) == 0:
            raise Exception("empty log event discarded")
        if "log_dict" not in vars:
            vars["log_dict"] = {}

        if auth_is_svc():
            # svc auth
            vars["svc_id"] = auth.user.svc_id
            vars["node_id"] = auth.user.node_id
            vars["log_user"] = "agent"
        elif hasattr(auth.user, "node_id"):
            # node auth
            vars["node_id"] = auth.user.node_id
            vars["log_user"] = "agent"
        elif auth.user.first_name and auth.user.last_name:
            # user auth
            vars["log_user"] = " ".join((auth.user.first_name,
                                         auth.user.last_name))
            # verify the user is responsible for the svc or node
            if "svc_id" in vars:
                svc_responsible(vars["svc_id"])
            elif "node_id" in vars:
                node_responsible(vars["node_id"])
        else:
            raise Exception("unknown log sender")

        log_id = db.log.insert(**vars)
        ws_send('log_change', {"id": log_id})
        return rest_get_log().handler(log_id)



