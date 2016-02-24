#
class rest_get_services_actions(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services action log.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_actions",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services_actions",
          tables=["SVCactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.SVCactions.id > 0
        q &= _where(None, 'SVCactions', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_services_action(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a services action log entry.",
          "Responsibles can modify only the acknowledged and comment fields",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d ack=1 ack_comment='foo' -o- https://%(collector)s/init/rest/api/services_action/123445",
        ]

        rest_post_handler.__init__(
          self,
          path="/services_actions/<id>",
          tables=["SVCactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.SVCactions.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("log entry %s does not exist" % str(id))
        svc_responsible(row.svcname)

        # purge data of unauthorized keys
        for c in set(db.SVCactions.fields) - set(["ack", "acked_comment"]):
            if c in vars:
                del(vars[c])

        if "ack" in vars and vars["ack"] == 1:
            if row.status == "ok":
                return dict(info="skip acknowledge of action %s in status 'ok'" % str(id))
            vars["acked_by"] = user_name()
            vars["acked_date"] = datetime.datetime.now()

        db(q).update(**vars)
        _log('actions.change',
             'changed action %(id)s: %(data)s',
             dict(id=str(id), data=beautify_change(row, vars)),
             nodename=row.hostname,
             svcname=row.svcname)

        l = {
          'event': 'svcactions_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))
        table_modified("SVCactions")

        update_action_errors()
        update_dash_action_errors(row.svcname, row.hostname)
        return dict(info="actions log entry %s successfully changed" %str(id))

#
class rest_post_services_actions(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify services action log entries.",
          "Responsibles can modify only the acknowledged and comment fields",
        ]
        examples = [
          "# curl -u %(email)s -X POST --header 'Content-Type: application/json' -d @/tmp/list.json -o- https://%(collector)s/init/rest/api/services_action",
        ]

        rest_post_handler.__init__(
          self,
          path="/services_actions",
          tables=["SVCactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'id' not in vars:
           raise Exception("The 'id' key must be specified")
        id = vars["id"]
        del(vars["id"])
        return rest_post_services_action().handler(id, **vars)

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

