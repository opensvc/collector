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
          tables=["svcmon_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.svcmon_log.id > 0
        q = _where(q, 'svcmon_log', domain_perms(), 'mon_svcname')
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
          tables=["services_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.services_log.id > 0
        q = _where(q, 'services_log', domain_perms(), 'svc_name')
        self.set_q(q)
        return self.prepare_data(**vars)


