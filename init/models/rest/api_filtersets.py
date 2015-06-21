from gluon.dal import smart_query

#
class rest_get_filtersets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List filtersets.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets?query=fset_name contains aix"
        ]
        q = db.gen_filtersets.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/filtersets",
          tables=["gen_filtersets"],
          q=q,
          desc=desc,
          examples=examples,
        )


