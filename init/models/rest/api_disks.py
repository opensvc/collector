#
class rest_get_disk(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a disk properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/disks/1?props=svcdisks.node_id,svcdisks.disk_id,stor_array.array_name",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/disks/<id>",
          tables=["svcdisks", "diskinfo", "stor_array"],
          left=(
              db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id),
              db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
          ),
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.diskinfo.disk_id == id
        q = q_filter(q, node_field=db.svcdisks.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

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

#
class rest_post_disks(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a disk.",
        ]
        examples = [
        ]
        rest_post_handler.__init__(
          self,
          path="/disks",
          tables=["diskinfo"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "Manager" not in user_groups():
            raise Exception("you are not allowed to use this handler")
        if "disk_id" not in vars:
            raise Exception("The 'disk_id' key is mandatory")
        if "disk_arrayid" not in vars:
            raise Exception("The 'disk_arrayid' key is mandatory")
        db.diskinfo.update_or_insert(
            {"disk_id": vars["disk_id"]},
            **vars
        )
        table_modified("disks")
        ws_send("disks_change")
        return rest_get_disk().handler(vars["disk_id"])

#
class rest_delete_disks(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete disks.",
        ]
        examples = [
        ]
        rest_delete_handler.__init__(
          self,
          path="/disks",
          tables=["diskinfo"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "disk_id" not in vars:
            raise Exception("The 'disk_id' key is mandatory")
        return rest_delete_disk().handler(vars["disk_id"])

#
class rest_delete_disk(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete disks.",
        ]
        examples = [
        ]
        rest_delete_handler.__init__(
          self,
          path="/disks/<id>",
          tables=["diskinfo"],
          desc=desc,
          examples=examples,
        )

    def handler(self, disk_id, **vars):
        if "Manager" not in user_groups():
            raise Exception("you are not allowed to use this handler")
        q = db.diskinfo.disk_id == disk_id
        n = db(q).count()
        if n == 0:
            return {"info": "Disk %s does not exist" % disk_id}
        db(q).delete()
        table_modified("disks")
        ws_send("disks_change")
        return {"info": "Disk %s deleted" % disk_id}


