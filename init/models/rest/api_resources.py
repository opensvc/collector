
#
class rest_get_resources_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services resources status changes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/resources_logs",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/resources_logs",
          tables=["v_resmon_log"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.v_resmon_log.svc_id)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, svc_field=db.v_resmon_log.svc_id, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_resources(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services resources.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/resources?props=svc_id,rid&query=res_desc contains :/",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.resmon.svc_id)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, svc_field=db.resmon.svc_id, fset_id=fset_id)
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
class rest_get_resource(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the specified resource.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/resource/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/resources/<id>",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.resmon.id == id
        q = q_filter(q, svc_field=db.resmon.id)
        self.set_q(q)
        return self.prepare_data(**vars)

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
        svc_responsible(row.svc_id)
        db(q).delete()
        fmt = 'resource %(rid)s of service %(svcname)s instance on node %(nodename)s deleted'
        d = {
          "rid": row.rid,
          "nodename": get_nodename(row.node_id),
          "svcname": get_svcname(row.svc_id),
        }
        _log('service.resource.delete', fmt, d,
             node_id=row.node_id,
             svc_id=row.svc_id,
            )
        ws_send('resmon_change', {'id': id})
        return dict(info=fmt%d)

