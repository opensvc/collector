from gluon.dal import smart_query


#
class rest_get_tags(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List existing tags.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags?like=%%aix%%",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags",
          tables=["tags"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.tags.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_tags(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a tag.",
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
            raise Exception({"error": "the tag_name property is mandatory"})
        tag_name = vars['tag_name']
        q = db.tags.tag_name == tag_name
        if db(q).count() == 1:
            raise Exception({"error": "tag already exist"})
        db.tags.insert(**vars)
        data = db(q).select().first()
        return dict(info="tag created", data=data)


#
class rest_get_tag(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display tag property.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/10",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/tags/<id>",
          tables=["tags"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, **vars):
        q = db.tags.id == int(tagid)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_tag(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete the tag with id <id>.",
          "Also delete the attachments to nodes and services",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, **vars):
        check_privilege("TagManager")

        info = []

        q = db.node_tags.tag_id == tagid
        q &= _where(None, 'node_tags', domain_perms(), 'nodename')
        n = db(q).delete()
        info += ["%d node attachments deleted"%n]

        q = db.svc_tags.tag_id == tagid
        q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
        n = db(q).delete()
        info += ["%d service attachments deleted"%n]

        q = db.node_tags.tag_id == tagid
        n = db(q).count()
        q = db.svc_tags.tag_id == tagid
        n += db(q).count()
        if n > 0:
            info += ["tag not deleted: still attached to %d objects you are not responsible for"%n]
            return dict(info=', '.join(info))

        q = db.tags.id == tagid
        n = db(q).delete()
        info += ["%d tag deleted"%n]

        return dict(info=', '.join(info))


#
class rest_get_tag_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes where tag <id> is attached.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/1001/nodes?props=nodename",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, **vars):
        q = db.node_tags.tag_id == tagid
        q &= db.node_tags.nodename == db.nodes.nodename
        q &= _where(None, 'node_tags', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_tag_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services where tag <id> is attached.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/1001/services?props=svc_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/tags/<id>/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, **vars):
        q = db.svc_tags.tag_id == tagid
        q &= db.svc_tags.svcname == db.services.svc_name
        q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_tag_node(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a tag to a node",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/1001/nodes/mynode",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/<id>/nodes/<nodename>",
          desc=desc,
          examples=examples
        )

    def handler(self, tagid, nodename, **vars):
        return lib_tag_attach_node(tagid, nodename)


#
class rest_delete_tag_node(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a tag from a node.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001/nodes/mynode",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>/nodes/<nodename>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, nodename, **vars):
        return lib_tag_detach_node(tagid, nodename)



#
class rest_post_tag_service(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a tag to a service",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/1001/services/mysvc",
        ]
        rest_post_handler.__init__(
          self,
          path="/tags/<id>/services/<svcname>",
          desc=desc,
          examples=examples
        )

    def handler(self, tagid, svcname, **vars):
        return lib_tag_attach_service(tagid, svcname)

#
class rest_delete_tag_service(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a tag from a service.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001/services/mysvc",
        ]
        rest_delete_handler.__init__(
          self,
          path="/tags/<id>/services/<svcname>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tagid, svcname, **vars):
        return lib_tag_detach_service(tagid, svcname)




