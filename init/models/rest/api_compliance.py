from gluon.dal import smart_query
import json

#
class rest_get_compliance_status(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' last check run."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/status?query=run_status=1 and run_module=mymod"
        ]
        q = db.comp_status.id > 0
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        rest_get_table_handler.__init__(
          self,
          path="/compliance/status",
          tables=["comp_status"],
          q=q,
          desc=desc,
          examples=examples,
        )

#
class rest_get_compliance_status_one(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of the last check run of a specific module-node-service tuple"
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/status/10"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/compliance/status/<id>",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.comp_status.id == int(id)
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_compliance_status_run(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete the last check run information of a specific module-node-service tuple.",
          "Requires the CompManager privilege and node ownership.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/status/10"
        ]

        rest_delete_handler.__init__(
          self,
          path="/compliance/status/<id>",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CompManager")
        q = db.comp_status.id == int(id)
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        row = db(q).select().first()
        if row is None:
            return dict(info="Task %s does not exist in the scheduler" % id)
        node_responsible(row.run_nodename)
        db(q).delete()
        _log('rest.compliance.status.delete',
             'deleted run %(u)s',
             dict(u="-".join((row.run_module, row.run_nodename, row.run_svcname if row.run_svcname else ""))),
             nodename=row.run_nodename,
             svcname=row.run_svcname,
        )
        return dict(info="Run %s deleted" % id)


