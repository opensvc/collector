from gluon.dal import smart_query
import datetime

def network_responsible(id):
    q = db.networks.id == id
    n = db(q).count()
    if n == 0:
        raise Exception("Network %s does not exist" % id)
    ug = user_groups()
    if "Manager" in ug:
        return
    q &= db.networks.team_responsible.belongs(ug)
    n = db(q).count()
    if n != 1:
        raise Exception("Not authorized: user is not responsible for network %s" % id)


#
class rest_get_network_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a nodes on the specified network.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/nodes",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/networks/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(id, self, **vars):
        q = db.networks.id == id
        net = db(q).select().first()
        if net is None:
            return dict(data=[])
        q = db.v_nodenetworks.net_network == net.network
        q &= db.v_nodenetworks.net_netmask == net.netmask
        q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_network(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display all network properties.",
          "Display selected network properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10?props=id,netmask",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/networks/<id>",
          tables=["networks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.networks.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_networks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List all networks and their selected properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks?props=id,network,netmask,gateway",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/networks",
          tables=["networks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.networks.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_network(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a set of network properties.",
          "The user must be responsible for the network",
          "The user must be in the NetworkManager privilege group",
          "The updated timestamp is automatically updated.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the networks table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=", ".join(sorted(db.networks.fields)),
      )
        examples = [
          """# curl -u %(email)s -o- -d pvid=12 -d comment="foo" https://%(collector)s/init/rest/api/networks/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("NetworkManager")
        network_responsible(id)
        q = db.networks.id == id
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db(q).update(**vars)
        _log('rest.networks.update',
             'update properties %(data)s',
             dict(data=str(vars)),
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_network().handler(id, props=','.join(["id","updated"]+vars.keys()))


#
class rest_post_networks(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a new network",
          "If ``team_responsible``:green is not specified, default to user's primary group",
        ]
        data = """
- <property>=<value> pairs.
- The id property is mandatory.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=", ".join(sorted(db.networks.fields)),
      )
        examples = [
          """# curl -u %(email)s -o- -d comment="foo" -d network="192.168.0.0" -d netmask=22 -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/networks""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("NetworkManager")
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "team_responsible" not in vars:
            vars["team_responsible"] = user_primary_group()
        id = db.networks.insert(**vars)
        _log('rest.networks.create',
             'create properties %(data)s',
             dict(data=str(vars))
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_network().handler(id, props=','.join(["id","updated"]+vars.keys()))


#
class rest_delete_network(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a network.",
          "The user must be responsible for the network.",
          "The user must be in the NetworkManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the networks table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        network_responsible(id)
        check_privilege("NetworkManager")
        q = db.networks.id == id
        net = db(q).select().first()
        if net is None:
            return dict(info="network does not exist")
        db(q).delete()
        _log('rest.networks.delete',
             '%(network)s/%(netmask)s',
             dict(network=net.network, netmask=net.netmask),
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Network %s deleted" % id)

