
#
class rest_get_resources(rest_get_table_handler):
    def __init__(self):
        params = {
          "fset_id": {
             "desc": "Filter the list using the filterset identified by fset_id."
          }
        }
        desc = [
          "List OpenSVC services resources.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/resources?props=svcname,rid&query=res_desc contains :/",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.resmon.svcname)
        fset_id = vars.get("fset_id")
        if fset_id:
            q = apply_filters(q, service_field=db.resmon.svcname, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_resources(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete service resources.",
          "The user must be responsible for the resource service.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/resources""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/resources",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            id = vars["id"]
            del(vars["id"])
        else:
            raise Exception("The 'id' key is mandatory")
        return rest_delete_resource().handler(id)

#
class rest_delete_resource(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a service resource.",
          "The user must be responsible for the service.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/resources/1""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/resources/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.resmon.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="resource does not exist")
        svc_responsible(row.svcname)
        db(q).delete()
        fmt = 'resource %(rid)s of service %(svcname)s instance on node %(nodename)s deleted'
        d = {
          "rid": row.rid,
          "nodename": row.nodename,
          "svcname": row.svcname,
        }
        _log('service.resource.delete', fmt, d,
             nodename=row.nodename,
             svcname=row.svcname,
            )
        l = {
          'event': 'resmon_change',
          'data': {'id': id},
        }
        _websocket_send(event_msg(l))
        return dict(info=fmt%d)


