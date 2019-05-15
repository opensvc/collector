#
class rest_get_services_action(rest_get_handler):
    def __init__(self):
        desc = [
          "List services action log.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_actions/1234",
        ]

        rest_get_handler.__init__(
          self,
          path="/services_actions/<id>",
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.svcactions.id == id
        q = q_filter(q, svc_field=db.svcactions.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

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
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.svcactions.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_services_actions(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete services action log entries.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE --header 'Content-Type: application/json' -d @/tmp/list.json -o- https://%(collector)s/init/rest/api/services_action",
        ]

        rest_delete_handler.__init__(
          self,
          path="/services_actions",
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'id' not in vars:
           raise HTTP(400, "The 'id' key must be specified")
        id = vars["id"]
        del(vars["id"])
        return rest_delete_services_action().handler(id, **vars)

#
class rest_delete_services_action(rest_delete_handler):
    def __init__(self):
        desc = [
          "Modify a services action log entry.",
          "Responsibles can modify only the acknowledged and comment fields",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services_action/123445",
        ]

        rest_delete_handler.__init__(
          self,
          path="/services_actions/<id>",
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.svcactions.id == id
        row = db(q).select(
          db.svcactions.id,
          db.svcactions.node_id,
          db.svcactions.svc_id,
        ).first()
        if row is None:
            raise HTTP(404, "log entry %s does not exist" % str(id))
        svc_responsible(row.svc_id)
        db(q).delete()
        table_modified("svcactions")

        update_instance_action_errors(row.svc_id, row.node_id)
        update_dash_action_errors(row.svc_id, row.node_id)
        return dict(info="actions log entry %s deleted" %str(id))

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
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.svcactions.id == id
        row = db(q).select(
          db.svcactions.id,
          db.svcactions.node_id,
          db.svcactions.svc_id,
          db.svcactions.status,
        ).first()
        if row is None:
            raise HTTP(404, "log entry %s does not exist" % str(id))
        svc_responsible(row.svc_id)

        # purge data of unauthorized keys
        for c in set(db.svcactions.fields) - set(["ack", "acked_comment"]):
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
             node_id=row.node_id,
             svc_id=row.svc_id)

        ws_send('svcactions_change', {'id': row.id})
        table_modified("svcactions")

        update_instance_action_errors(row.svc_id, row.node_id)
        update_dash_action_errors(row.svc_id, row.node_id)
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
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'id' not in vars:
           raise HTTP(400, "The 'id' key must be specified")
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
          path="/services/<id>/actions",
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.svcactions.svc_id == svc_id
        q = q_filter(q, svc_field=db.svcactions.svc_id)
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
          path="/services/<id>/actions_unacknowledged_errors",
          tables=["svcactions"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.svcactions.svc_id == svc_id
        q &= db.svcactions.status == "err"
        q &= db.svcactions.ack == None
        q = q_filter(q, svc_field=db.svcactions.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

