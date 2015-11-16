
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
        q = db.resmon.id > 0
        q = _where(q, 'resmon', domain_perms(), 'svcname')
        fset_id = vars.get("fset_id")
        if fset_id:
            q = apply_filters(q, service_field=db.resmon.svcname, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)


