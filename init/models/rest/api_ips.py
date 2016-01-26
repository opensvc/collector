
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

#
class rest_delete_ips(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete node ips.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/ips",
        ]

        rest_delete_handler.__init__(
          self,
          path="/ips",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")
        id = vars["id"]
        del(vars["id"])
        return rest_delete_ip().handler(id, **vars)

 #
class rest_delete_ip(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a node ip.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/ips/10",
        ]

        rest_delete_handler.__init__(
          self,
          path="/ips/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("NodeManager")
        q = db.node_ip.id == id
        q &= _where(None, 'node_ip', domain_perms(), 'nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("ip %s not found" % str(id))
        node_responsible(row.nodename)
        db(q).delete()

        fmt = "ip %(addr)s on node %(nodename)s deleted"
        d = dict(addr=row.addr, nodename=row.nodename)
        _log("node.ip.delete", fmt, d, nodename=row.nodename)
        l = {
          'event': 'node_ip_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))

        return dict(info=fmt%d)


