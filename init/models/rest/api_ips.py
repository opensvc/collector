
#
class rest_get_ips(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List ips detected on nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/ips",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/ips",
          tables=["v_nodenetworks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.v_nodenetworks.id > 0
        q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_ip(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a node ip properties.",
          "<id> can be either the proper id or the ip addr.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/ips/10",
        ]

        rest_get_line_handler.__init__(
          self,
          path="/ips/<id>",
          tables=["v_nodenetworks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        if "." in id or ":" in id:
            q = db.v_nodenetworks.addr == id
        else:
            q = db.v_nodenetworks.id == id
        q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
        return self.prepare_data(**vars)


