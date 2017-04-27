def prov_template_id(tpl_id):
    try:
        q = db.prov_templates.id == int(tpl_id)
        t = db(q).select(db.prov_templates.id).first()
    except:
        q = db.prov_templates.tpl_name == tpl_id
        t = db(q).select(db.prov_templates.id).first()
    if t is None:
        raise Exception("provisioning template %s not found" % str(tpl_id))
    return t.id

def prov_template_published(tpl_id):
    if 'Manager' in user_groups():
        return
    q = db.prov_template_team_publication.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to access the provisioning template %s" % str(tpl_id))

def prov_template_responsible(tpl_id):
    if 'Manager' in user_groups():
        return
    q = db.prov_template_team_responsible.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to do this operation on the provisioning template %s" % str(tpl_id))

def lib_provisioning_templates_add_default_team_responsible(tpl_id):
    group_id = user_default_group_id()
    db.prov_template_team_responsible.insert(tpl_id=tpl_id, group_id=group_id)

def lib_provisioning_templates_add_default_team_publication(tpl_id):
    group_id = user_default_group_id()
    db.prov_template_team_publication.insert(tpl_id=tpl_id, group_id=group_id)

class rest_get_provisioning_templates(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List available provisioning templates.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates?query=tpl_name contains dns"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/provisioning_templates",
          tables=["prov_templates"],
          desc=desc,
          left=db.prov_template_team_publication.on(db.prov_templates.id==db.prov_template_team_publication.tpl_id),
          groupby=db.prov_templates.id,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.prov_templates.id > 0
        if "Manager" not in user_groups():
            q &= db.prov_template_team_publication.group_id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_get_provisioning_template(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List provisioning_template <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/provisioning_templates/<id>",
          tables=["prov_templates"],
          left=db.prov_template_team_publication.on(db.prov_templates.id==db.prov_template_team_publication.tpl_id),
          groupby=db.prov_templates.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        tpl_id = prov_template_id(tpl_id)
        q = db.prov_templates.id == tpl_id
        if "Manager" not in user_groups():
            q &= db.prov_template_team_publication.group_id.belongs(user_group_ids())
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_put_provisioning_template(rest_put_handler):
    def __init__(self):
        desc = [
          "Enqueue a service provisioning command based on the template <id>.",
        ]
        data = """
- **depends on the template definition**
. The information the template expects, ie the env section keys.
. The 'node_id' and 'svcname' are mandatory, even if not present in the form definition.
"""
        examples = [
          """# curl -u %(email)s -d node_id=5c977246-0562-11e6-8c70-7e9e6cf13c8a -d svcname=newsvc -d foo=bar -X PUT -o- https://%(collector)s/init/rest/api/provisioning_templates/10"""
        ]

        rest_put_handler.__init__(
          self,
          path="/provisioning_templates/<id>",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        tpl_id = prov_template_id(tpl_id)
        q = db.prov_templates.id == tpl_id
        provisioning_template = db(q).select(db.prov_templates.ALL).first()
        if provisioning_template is None:
            return dict("error", "the requested provisioning template does not exist or you don't have permission to use it")

        definition = provisioning_template.tpl_definition
        data = rest_post_services().handler(
          svcname=vars["svcname"],
          svc_config=definition
        )

        svc = data["data"][0]

        command = 'create --provision --template %d' % provisioning_template.id
        for k, v in vars.items():
            if k in ("svcname", "node_id"):
                continue
            command += ' --env %s="%s"' % (k, v)

        n = do_svc_action(vars["node_id"], svc["svc_id"], command)
        if n == 0:
            return dict(error="service provision command enqueue refused")

        return dict(info="service provision command queued")


class rest_post_provisioning_template(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a provisioning template properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d tpl_name=test -o- https://%(collector)s/init/rest/api/provisioning_templates/1"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates/<id>",
          tables=["prov_templates"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)

        if "id" in vars:
            del(vars["id"])

        q = db.prov_templates.id == tpl_id
        tpl = db(q).select().first()
        if tpl is None:
            raise Exception("Provisioning template %s not found"%str(tpl_id))

        tpl_id = db(q).update(**vars)

        fmt = "Provisioning template %(tpl_name)s change: %(data)s"
        d = dict(tpl_name=tpl.tpl_name, data=beautify_change(tpl, vars))

        _log('provisioning_template.change', fmt, d)
        ws_send('prov_templates_change', {'id': tpl.id})

        ret = rest_get_provisioning_template().handler(tpl.id)
        lib_provisioning_templates_add_to_git(str(tpl.id), ret["data"][0]["tpl_definition"])
        ret["info"] = fmt % d
        return ret

class rest_post_provisioning_templates(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create provisioning templates",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d tpl_name=test -o- https://%(collector)s/init/rest/api/provisioning_templates"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates",
          tables=["prov_templates"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("ProvisioningManager")

        if 'id' in vars:
            tpl_id = vars["id"]
            del(vars["id"])
            return rest_post_provisioning_template().handler(tpl_id, **vars)

        if "tpl_name" not in vars:
            raise Exception("Key 'tpl_name' is mandatory")
        tpl_name = vars.get("tpl_name")

        vars["tpl_created"] = datetime.datetime.now()
        vars["tpl_author"] = user_name()

        tpl_id = db.prov_templates.insert(**vars)
        lib_provisioning_templates_add_default_team_responsible(tpl_id)
        lib_provisioning_templates_add_default_team_publication(tpl_id)

        fmt = "Provisioning template %(tpl_name)s added"
        d = dict(tpl_name=tpl_name)

        _log('provisioning_template.add', fmt, d)
        ws_send('prov_templates_change', {'id': tpl_id})

        return rest_get_provisioning_template().handler(tpl_id)

class rest_delete_provisioning_template(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a provisioning template",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)

        q = db.prov_templates.id == tpl_id
        tpl = db(q).select().first()
        if tpl is None:
            raise Exception("Provisioning template %s not found"%str(tpl_id))

        db(q).delete()

        fmt = "Provisioning template %(tpl_name)s deleted"
        d = dict(tpl_name=tpl.tpl_name)

        _log('provisioning_template.del', fmt, d)
        ws_send('prov_templates_change', {'id': tpl.id})

        return dict(info=fmt%d)

class rest_delete_provisioning_templates(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete provisioning templates",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates"
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not 'id' in vars:
            raise Exception("The 'id' key is mandatory")

        tpl_id = vars["id"]
        del(vars["id"])
        return rest_delete_provisioning_template().handler(tpl_id, **vars)

class rest_get_provisioning_template_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups responsible for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_template/1/responsibles"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/provisioning_templates/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        tpl_id = prov_template_id(tpl_id)
        prov_template_published(tpl_id)
        q = db.prov_template_team_responsible.tpl_id == tpl_id
        q &= db.prov_template_team_responsible.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_provisioning_template_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates/1/responsibles/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, group_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)
        q = db.prov_template_team_responsible.tpl_id == tpl_id
        q &= db.prov_template_team_responsible.group_id == group_id

        fmt = "Form %(tpl_id)s responsibility to group %(group_id)s removed"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Form %(tpl_id)s responsibility to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'provisioning_template.responsible.delete',
          fmt,
          d
        )
        ws_send('prov_template_responsible_change', {'id': tpl_id})

        return dict(info=fmt%d)

class rest_delete_provisioning_templates_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove responsible groups from provisioning templates",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates_responsibles?filters[]="tpl_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "tpl_id" in vars:
            raise Exception("The 'tpl_id' key is mandatory")
        tpl_id = vars.get("tpl_id")
        del(vars["tpl_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_provisioning_template_responsible().handler(tpl_id, group_id, **vars)

class rest_post_provisioning_template_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/provisioning_templates/1/responsibles/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, group_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Form %(tpl_id)s responsibility to group %(group_id)s added"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        q = db.prov_template_team_responsible.tpl_id == tpl_id
        q &= db.prov_template_team_responsible.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Form %(tpl_id)s responsibility to group %(group_id)s already added" % d)

        db.prov_template_team_responsible.insert(tpl_id=tpl_id, group_id=group.id)

        _log(
          'provisioning_template.responsible.add',
          fmt,
          d
        )
        ws_send('prov_template_responsible_change', {'id': tpl_id})

        return dict(info=fmt%d)

class rest_post_provisioning_templates_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Add responsible groups to provisioning templates",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/provisioning_templates_responsibles"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "tpl_id" in vars:
            raise Exception("The 'tpl_id' key is mandatory")
        tpl_id = vars.get("tpl_id")
        del(vars["tpl_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_provisioning_template_responsible().handler(tpl_id, group_id, **vars)


class rest_get_provisioning_template_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups publication for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_template/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/provisioning_templates/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        prov_template_published(tpl_id)
        tpl_id = prov_template_id(tpl_id)
        q = db.prov_template_team_publication.tpl_id == tpl_id
        q &= db.prov_template_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_provisioning_template_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, group_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)
        q = db.prov_template_team_publication.tpl_id == tpl_id
        q &= db.prov_template_team_publication.group_id == group_id

        fmt = "Form %(tpl_id)s publication to group %(group_id)s removed"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Form %(tpl_id)s publication to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'provisioning_template.publication.delete',
          fmt,
          d
        )
        ws_send('prov_template_publication_change', {'id': tpl_id})

        return dict(info=fmt%d)

class rest_delete_provisioning_templates_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove publication groups from provisioning templates",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/provisioning_templates_publications?filters[]="tpl_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/provisioning_templates_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "tpl_id" in vars:
            raise Exception("The 'tpl_id' key is mandatory")
        tpl_id = vars.get("tpl_id")
        del(vars["tpl_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_provisioning_template_publication().handler(tpl_id, group_id, **vars)

class rest_post_provisioning_template_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/provisioning_templates/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, group_id, **vars):
        check_privilege("ProvisioningManager")
        tpl_id = prov_template_id(tpl_id)
        prov_template_responsible(tpl_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Form %(tpl_id)s publication to group %(group_id)s added"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        q = db.prov_template_team_publication.tpl_id == tpl_id
        q &= db.prov_template_team_publication.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Form %(tpl_id)s publication to group %(group_id)s already added" % d)

        db.prov_template_team_publication.insert(tpl_id=tpl_id, group_id=group.id)

        _log(
          'provisioning_template.publication.add',
          fmt,
          d
        )
        ws_send('prov_template_publication_change', {'id': tpl_id})

        return dict(info=fmt%d)

class rest_post_provisioning_templates_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Add publication groups to provisioning templates",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/provisioning_templates_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "tpl_id" in vars:
            raise Exception("The 'tpl_id' key is mandatory")
        tpl_id = vars.get("tpl_id")
        del(vars["tpl_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_provisioning_template_publication().handler(tpl_id, group_id, **vars)

class rest_post_provisioning_template_rollback(rest_post_handler):
    def __init__(self):
        desc = [
          "Restore an old revision of a provisioning template",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/provisioning_templates/1/rollback/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710"
        ]

        rest_post_handler.__init__(
          self,
          path="/provisioning_templates/<id>/rollback/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, cid, **vars):
        check_privilege("ProvisioningManager")
        prov_template_responsible(tpl_id)
        lib_provisioning_templates_rollback(tpl_id, cid)
        return

#
class rest_get_provisioning_template_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/provisioning_templates/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        try:
            tpl_id = prov_template_id(tpl_id)
            prov_template_responsible(tpl_id)
            return dict(data=True)
        except:
            return dict(data=False)

class rest_get_provisioning_template_revision(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the provisioning template content for the given revision.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates/1/revision/1234",
        ]
        rest_get_handler.__init__(
          self,
          path="/provisioning_templates/<id>/revisions/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, cid, **vars):
        r = []
        q = db.prov_templates.id == int(tpl_id)
        if "Manager" not in user_groups():
            q &= db.prov_templates.id == db.prov_template_team_publication.tpl_id
            q &= db.prov_template_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_provisioning_templates_revision(tpl_id, cid)
        return r

class rest_get_provisioning_template_revisions(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the provisioning template revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates/1/revisions",
        ]
        rest_get_handler.__init__(
          self,
          path="/provisioning_templates/<id>/revisions",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, **vars):
        r = []
        q = db.prov_templates.id == int(tpl_id)
        if "Manager" not in user_groups():
            q &= db.prov_templates.id == db.prov_template_team_publication.tpl_id
            q &= db.prov_template_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_provisioning_templates_revisions(tpl_id)
        return r

class rest_get_provisioning_template_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "Show the commit diff, or differences between <cid> and <other> if"
          "other is set",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/provisioning_templates/1/diff/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710",
        ]
        rest_get_handler.__init__(
          self,
          path="/provisioning_templates/<id>/diff/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, tpl_id, cid, other=None, **vars):
        r = []
        q = db.prov_templates.id == int(tpl_id)
        if "Manager" not in user_groups():
            q &= db.prov_templates.id == db.prov_template_team_publication.tpl_id
            q &= db.prov_template_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_provisioning_templates_diff(tpl_id, cid, other=other)
        return r
