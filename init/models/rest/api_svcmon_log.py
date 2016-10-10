#
class rest_get_services_instances_status_log(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services instances status log. Each log entry is a time range where a service instance status was stable.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_instances_status_log",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services_instances_status_log",
          tables=["v_svcmon_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.v_svcmon_log.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#

class rest_get_services_status_log(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services status log. Each log entry is a time range where a service status was stable.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_status_log",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services_status_log",
          tables=["v_services_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.v_services_log.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


