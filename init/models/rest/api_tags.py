

#
class rest_get_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing tags.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags",
          tables=["tags"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.tags.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List tags attached to a node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/tags",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/tags",
          tables=["tags"],
          props_blacklist=["id"],
          orderby=db.tags.tag_name,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == db.tags.tag_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_node_candidate_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List attachable tags for node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/candidate_tags",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/candidate_tags",
          tables=["tags"],
          props_blacklist=["id"],
          desc=desc,
          orderby=db.tags.tag_name,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == db.tags.tag_id
        rows = db(q).select(db.tags.ALL)

        tag_ids = set([r.tag_id for r in rows])
        pattern = '|'.join([r.tag_exclude for r in rows if r.tag_exclude is not None and r.tag_exclude != ""])
        q = db.tags.id > 0
        q &= ~db.tags.tag_id.belongs(tag_ids)
        if len(pattern) > 0:
            qx = _where(None, "tags", pattern, "tag_name")
            q &= ~qx
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List tags attached to a service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/52243ac9-9897-45ed-bd03-89e1eb7c53ba/tags",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/tags",
          tables=["tags"],
          props_blacklist=["id"],
          orderby=db.tags.tag_name,
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == db.tags.tag_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_candidate_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List attachable tags for service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/52243ac9-9897-45ed-bd03-89e1eb7c53ba/candidate_tags",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/candidate_tags",
          tables=["tags"],
          props_blacklist=["id"],
          orderby=db.tags.tag_name,
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == db.tags.tag_id
        rows = db(q).select(db.tags.ALL)

        tag_ids = set([r.tag_id for r in rows])
        pattern = '|'.join([r.tag_exclude for r in rows if r.tag_exclude is not None and r.tag_exclude != ""])
        q = db.tags.id > 0
        q &= ~db.tags.tag_id.belongs(tag_ids)
        if len(pattern) > 0:
            qx = _where(None, "tags", pattern, "tag_name")
            q &= ~qx
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_tag(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a tag properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/<id>",
          tables=["tags"],
          desc=desc,
          examples=examples
        )

    def handler(self, tag_id, **vars):
        check_privilege("TagManager")
        q = db.tags.tag_id == tag_id
        row = db(q).select().first()
        if row is None:
            raise Exception("tag %s not found" % tag_id)
        db(q).update(**vars)
        _log('tag.change',
             'change tag %(tag_name)s: %(data)s',
             dict(tag_name=row.tag_name, data=beautify_change(row, vars)),
            )
        table_modified("tags")
        ws_send("tags_change")
        return rest_get_tag().handler(row.tag_id)


#
class rest_post_tags(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_tags()
        self.update_one_handler = rest_post_tag()
        self.update_one_param = "id"
        desc = [
          "Create a tag.",
          "Update tags matching the specified query.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/tags",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags",
          tables=["tags"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("TagManager")
        if 'tag_name' not in vars:
            raise Exception("the tag_name property is mandatory")
        tag_name = vars['tag_name']
        q = db.tags.tag_name == tag_name
        if db(q).count() == 1:
            raise Exception("tag already exist")
        db.tags.insert(**vars)
        data = db(q).select().first()
        _log('tag.create',
             "tag '%(tag_name)s' created",
             dict(tag_name=data.tag_name),
            )
        table_modified("tags")
        ws_send("tags_change")
        return dict(info="tag created", data=data)


#
class rest_get_tag(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display tag property.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/tags/<id>",
          tables=["tags"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tag_id, **vars):
        q = db.tags.tag_id == tag_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_tags(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete the tags.",
          "Also delete the attachments to nodes and services",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE --header 'Content-Type: application/json' -d @/tmp/data.json https://%(collector)s/init/rest/api/tags",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")

        tag_id = vars.get("tag_id")
        del(vars["tag_id"])

        return rest_delete_tag().handler(tag_id, **vars)


#
class rest_delete_tag(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete the tag with id <id>.",
          "Also delete the attachments to nodes and services",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tag_id, **vars):
        check_privilege("TagManager")

        info = []

        q = db.tags.tag_id == tag_id
        tag = db(q).select().first()
        if tag is None:
            return dict(info="tag not found")

        q = db.node_tags.tag_id == tag_id
        q = q_filter(q, node_field=db.node_tags.node_id)
        n = db(q).delete()
        info += ["%d node attachments deleted"%n]
        table_modified("node_tags")
        ws_send("node_tags_change")

        q = db.svc_tags.tag_id == tag_id
        q = q_filter(q, svc_field=db.svc_tags.svc_id)
        n = db(q).delete()
        info += ["%d service attachments deleted"%n]
        table_modified("svc_tags")
        ws_send("svc_tags_change")

        q = db.node_tags.tag_id == tag_id
        n = db(q).count()
        q = db.svc_tags.tag_id == tag_id
        n += db(q).count()
        if n > 0:
            info += ["tag not deleted: still attached to %d objects you are not responsible for"%n]
            return dict(info=', '.join(info))

        q = db.tags.tag_id == tag_id
        n = db(q).delete()
        info += ["%d tag deleted"%n]
        table_modified("tags")
        ws_send("tags_change")

        _log('tag.delete',
             "tag '%(tag_name)s' deleted",
             dict(tag_name=tag.tag_name),
            )
        return dict(info=', '.join(info))


#
class rest_get_tag_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes where tag <id> is attached.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/nodes?props=nodename",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/<id>/nodes",
          tables=["nodes"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tag_id, **vars):
        q = db.node_tags.tag_id == tag_id
        q &= db.node_tags.node_id == db.nodes.node_id
        q = q_filter(q, app_field=db.nodes.app)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_tag_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services where tag <id> is attached.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/services?props=svc_id",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/<id>/services",
          tables=["services"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tag_id, **vars):
        q = db.svc_tags.tag_id == tag_id
        q &= db.svc_tags.svc_id == db.services.svc_id
        q = q_filter(q, svc_field=db.svc_tags.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_tag_node(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a tag to a node",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/<id>/nodes/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, tag_id, node_id, **vars):
        return lib_tag_attach_node(tag_id, node_id)


#
class rest_delete_tag_node(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a tag from a node.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>/nodes/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, tag_id, node_id, **vars):
        return lib_tag_detach_node(tag_id, node_id)



#
class rest_post_tag_service(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a tag to a service",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/services/mysvc",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/<id>/services/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, tag_id, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        return lib_tag_attach_service(tag_id, svc_id)

#
class rest_delete_tag_service(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a tag from a service.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/d7dacae2c968388960bf8970080a980ed5c5dcb7/services/mysvc",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>/services/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, tag_id, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        return lib_tag_detach_service(tag_id, svc_id)


#
# /tags/nodes :: GET
#
class rest_get_tags_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List tags-nodes attachments.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/nodes",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/nodes",
          tables=["node_tags"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(node_field=db.node_tags.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
# /tags/nodes :: POST
#
class rest_post_tags_nodes(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach tags to nodes",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d node_id=5c977246-0562-11e6-8c70-7e9e6cf13c8a -d tag_id=d7dacae2c968388960bf8970080a980ed5c5dcb7 https://%(collector)s/init/rest/api/tags/nodes",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/nodes",
          tables=["node_tags"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if "node_id" not in vars:
            raise Exception("the 'node_id' key is mandatory")
        if "tag_id" not in vars:
            raise Exception("the 'tag_id' key is mandatory")
        return lib_tag_attach_node(vars["tag_id"], vars["node_id"])

#
# /tags/nodes :: DELETE
#
class rest_delete_tags_nodes(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach tags from a nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE -d node_id=5c977246-0562-11e6-8c70-7e9e6cf13c8a -d tag_id=d7dacae2c968388960bf8970080a980ed5c5dcb7 https://%(collector)s/init/rest/api/tags/nodes",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/nodes",
          tables=["node_tags"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if "node_id" not in vars:
            raise Exception("the 'node_id' key is mandatory")
        if "tag_id" not in vars:
            raise Exception("the 'tag_id' key is mandatory")
        return lib_tag_detach_node(vars["tag_id"], vars["node_id"])

#
# /tags/services :: GET
#
class rest_get_tags_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List tags-services attachments.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/services",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/services",
          tables=["svc_tags"],
          props_blacklist=["id"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.svc_tags.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
# /tags/services :: POST
#
class rest_post_tags_services(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach tags to services",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d svc_id=5c977246-0562-11e6-8c70-7e9e6cf13c8a -d tag_id=d7dacae2c968388960bf8970080a980ed5c5dcb7 https://%(collector)s/init/rest/api/tags/services",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/services",
          tables=["svc_tags"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if "svc_id" not in vars:
            raise Exception("the 'svc_id' key is mandatory")
        if "tag_id" not in vars:
            raise Exception("the 'tag_id' key is mandatory")
        return lib_tag_attach_service(vars["tag_id"], vars["svc_id"])

#
# /tags/services :: DELETE
#
class rest_delete_tags_services(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach tags from services.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE -d svc_id=5c977246-0562-11e6-8c70-7e9e6cf13c8a -d tag_id=d7dacae2c968388960bf8970080a980ed5c5dcb7 https://%(collector)s/init/rest/api/tags/services",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/services",
          tables=["svc_tags"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if "svc_id" not in vars:
            raise Exception("the 'svc_id' key is mandatory")
        if "tag_id" not in vars:
            raise Exception("the 'tag_id' key is mandatory")
        return lib_tag_detach_service(vars["tag_id"], vars["svc_id"])

