import json

class rest_get_alert_event(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display alert events time ranges.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alert_event"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/alert_event",
          tables=["dashboard_events"],
          desc=desc,
          orderby=~db.dashboard_events.id,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.dashboard_events.id > 0
        f1 = q_filter(svc_field=db.dashboard_events.svc_id)
        f2 = q_filter(node_field=db.dashboard_events.node_id)
        q = (f1|f2)
        self.set_q(q)
        return self.prepare_data(**vars)
