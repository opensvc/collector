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
- **data**
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

    def handler(self, id, data=None):
        q = db.prov_templates.id == id
        provisioning_template = db(q).select(db.prov_templates.ALL).first()
        if provisioning_template is None:
            return dict("error", "the requested provisioning template does not exist or you don't have permission to use it")

        provisioning_template_data = json.loads(data)

        import re
        command = provisioning_template.tpl_command
        for k, v in provisioning_template_data.items():
            v = str(v)
            command = re.sub('%\('+k+'\)s', v, command)

        # remove the '/opt/opensvc/bin/svcmgr -s svcname ' prefix
        command = re.sub('^.*create ', 'create ', command)

        n = do_svc_action(provisioning_template_data["nodename"],
                          provisioning_template_data["svcname"],
                          command)

        if n == 1:
            return dict(info="provisioning command queued")

        return dict(info="provisioning command refused")



