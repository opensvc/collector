def prov_template_responsible(tpl_id):
    if 'Manager' in user_groups():
        return
    q = db.prov_template_team_responsible.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to do this operation on the provisioning template %s" % str(tpl_id))

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
          examples=examples,
        )

    def handler(self, **vars):
        q = db.prov_templates.id > 0
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
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.prov_templates.id == int(id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_put_provisioning_template(rest_put_handler):
    def __init__(self):
        desc = [
          "Submit provisioning_template <id>.",
        ]
        data = """
- **depends on the template definition**
. The information the template expects, marked as %(key>)s in its definition.
. The 'nodename' and 'svcname' are mandatory, even if not present in the form
definition.
"""
        examples = [
          """# curl -u %(email)s -d data='{"nodename": "mynode", "svcname": "mysvc"}' -X PUT -o- https://%(collector)s/init/rest/api/provisioning_templates/10"""
        ]

        rest_put_handler.__init__(
          self,
          path="/provisioning_templates/<id>",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.prov_templates.id == id
        provisioning_template = db(q).select(db.prov_templates.ALL).first()
        if provisioning_template is None:
            return dict("error", "the requested provisioning template does not exist or you don't have permission to use it")

        import re
        command = provisioning_template.tpl_command
        for k, v in vars.items():
            v = str(v)
            command = re.sub('%\('+k+'\)s', v, command)

        # remove the '/opt/opensvc/bin/svcmgr -s svcname ' prefix
        command = re.sub('^.*create ', 'create ', command)

        n = do_svc_action(vars["nodename"],
                          vars["svcname"],
                          command)

        if n == 1:
            return dict(info="provisioning command queued")

        return dict(info="provisioning command refused")

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

    def handler(self, id, **vars):
        check_privilege("ProvisioningManager")
        prov_template_responsible(id)

        if "id" in vars:
            del(vars["id"])

        q = db.prov_templates.id == id
        tpl = db(q).select().first()
        if tpl is None:
            raise Exception("Provisioning template %s not found"%str(id))

        tpl_id = db(q).update(**vars)

        fmt = "Provisioning template %(tpl_name)s change: %(data)s"
        d = dict(tpl_name=tpl.tpl_name, data=beautify_change(tpl, vars))

        _log('provisioning_template.change', fmt, d)
        l = {
          'event': 'prov_templates_change',
          'data': {'id': tpl.id},
        }
        _websocket_send(event_msg(l))

        ret = rest_get_provisioning_template().handler(tpl.id)
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
        lib_provisioning_templates_add_default_team_responsible(tpl_name)
        #lib_provisioning_templates_add_default_team_publication(tpl_name)

        fmt = "Provisioning template %(tpl_name)s added"
        d = dict(tpl_name=tpl_name)

        _log('provisioning_template.add', fmt, d)
        l = {
          'event': 'prov_templates_change',
          'data': {'id': tpl_id},
        }
        _websocket_send(event_msg(l))

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

    def handler(self, id, **vars):
        check_privilege("ProvisioningManager")
        prov_template_responsible(id)

        q = db.prov_templates.id == id
        tpl = db(q).select().first()
        if tpl is None:
            raise Exception("Provisioning template %s not found"%str(id))

        tpl_id = db(q).delete()

        fmt = "Provisioning template %(tpl_name)s deleted"
        d = dict(tpl_name=tpl.tpl_name)

        _log('provisioning_template.del', fmt, d)
        l = {
          'event': 'prov_templates_change',
          'data': {'id': tpl.id},
        }
        _websocket_send(event_msg(l))

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

    def handler(self, id, **vars):
        #prov_template_published(id)
        q = db.prov_template_team_responsible.tpl_id == id
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
        prov_template_responsible(tpl_id)
        q = db.prov_template_team_responsible.tpl_id == tpl_id
        q &= db.prov_template_team_responsible.group_id == group_id

        fmt = "Form %(tpl_id)s responsability to group %(group_id)s removed"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Form %(tpl_id)s responsability to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'provisioning_template.responsible.delete',
          fmt,
          d
        )
        l = {
          'event': 'prov_template_responsible_change',
          'data': {'id': tpl_id},
        }
        _websocket_send(event_msg(l))

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
        prov_template_responsible(tpl_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Form %(tpl_id)s responsability to group %(group_id)s added"
        d = dict(tpl_id=str(tpl_id), group_id=str(group_id))

        q = db.prov_template_team_responsible.tpl_id == tpl_id
        q &= db.prov_template_team_responsible.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Form %(tpl_id)s responsability to group %(group_id)s already added" % d)

        db.prov_template_team_responsible.insert(tpl_id=tpl_id, group_id=group.id)

        _log(
          'provisioning_template.responsible.add',
          fmt,
          d
        )
        l = {
          'event': 'prov_template_responsible_change',
          'data': {'id': tpl_id},
        }
        _websocket_send(event_msg(l))

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



