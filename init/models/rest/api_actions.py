#
class rest_get_service_actions(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a service action log.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/service/svc1/actions",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/actions",
          tables=["SVCactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.SVCactions.svcname == svcname
        q &= _where(None, 'SVCactions', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_actions_unacknowledged_errors(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a service unacknowledged action error.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/service/svc1/actions_unacknowledged_errors",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/actions_unacknowledged_errors",
          tables=["SVCactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.SVCactions.svcname == svcname
        q &= db.SVCactions.status == "err"
        q &= db.SVCactions.ack == None
        q &= _where(None, 'SVCactions', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)

