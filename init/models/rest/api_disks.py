#
class rest_get_disks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List disks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/disks?props=svcdisks.node_id,svcdisks.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/disks",
          tables=["svcdisks", "diskinfo", "stor_array"],
          left=(
              db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id),
              db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
          ),
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.diskinfo.id > 0
        q = q_filter(q, node_field=db.svcdisks.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


