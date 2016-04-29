import json

class rest_get_alert_event(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display alert event on last 30 days following nodename/servicename and MD5 Id .",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alert_event"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/alert_event",
          tables=["dashboard_events"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'md5name' not in vars:
            raise Exception("the md5name property is mandatory")
        md5name = vars['md5name']

        if 'node_id' not in vars or vars["node_id"] == "":
            node_id = ""
        else:
            node_id = get_node_id(vars['node_id'])

        if 'svc_id' not in vars or vars["svc_id"] == "":
            svc_id = ""
        else:
            svc_id = get_svc_id(vars['svc_id'])

        limit = datetime.datetime.now() - datetime.timedelta(days=30)
        q = db.dashboard_events.dash_md5 == md5name
        q &= db.dashboard_events.node_id == node_id
        q &= db.dashboard_events.svc_id == svc_id
        q &= db.dashboard_events.dash_begin > limit
        f1 = q_filter(svc_field=db.dashboard_events.svc_id)
        f2 = q_filter(node_field=db.dashboard_events.node_id)
        q = (f1|f2)
        self.set_q(q)
        return self.prepare_data()
