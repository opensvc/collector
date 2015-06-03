from gluon.dal import smart_query
import datetime

api_networks_doc = {}

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
api_networks_doc["/networks/<id>/nodes"] = """
### GET

Description:

- List a nodes on the specified network.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/nodes``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_network_nodes(id, props=None, query=None):
    q = db.networks.id == id
    net = db(q).select().first()
    if net is None:
        return dict(data=[])
    q = db.v_nodenetworks.net_network == net.network
    q &= db.v_nodenetworks.net_netmask == net.netmask
    q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, ["v_nodenetworks"], blacklist=db.networks.fields)
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["v_nodenetworks"], blacklist=db.networks.fields)
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_networks_doc["/networks/<id>"] = """
### GET

Description:

- Display all network properties.
- Display selected network properties.

Optional parameters:

- **props**
. A list of properties to include in network data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10?props=id,netmask``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.networks.fields)),
      )

def get_network(id, props=None):
    q = db.networks.id == id
    q &= _where(None, 'networks', domain_perms(), 'id')
    cols = props_to_cols(props, tables=["networks"])
    data = db(q).select(*cols, cacheable=True).as_list()[0]
    return dict(data=data)


#
api_networks_doc["/networks"] = """
### GET

Description:

- List all networks and their selected properties.

Optional parameters:

- **props**
. A list of properties to include in each network data.
. If omitted, only the network name is included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks?props=id,network,netmask,gateway``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.networks.fields)),
      )

def get_networks(props=None, query=None):
    q = db.networks.id > 0
    if query:
        cols = props_to_cols(None, tables=["networks"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["networks"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_networks_doc["/networks/<id>"] += """
### POST

Description:

- Update a set of network properties.
- The user must be responsible for the network
- The user must be in the NetworkManager privilege group
- The updated timestamp is automatically updated.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the networks table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d pvid=12 -d comment="foo" https://%(collector)s/init/rest/api/networks/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.networks.fields)),
      )

def set_network(id, **vars):
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

    return get_network(id, props=','.join(["id","updated"]+vars.keys()))


#
api_networks_doc["/networks"] += """
### POST

Description:

- Create a new network
- If ``team_responsible``:green is not specified, default to user's primary
  group

Data:

- <property>=<value> pairs.
- The id property is mandatory.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d comment="foo" -d network="192.168.0.0" -d netmask=22 -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/networks``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.networks.fields)),
      )


def create_network(**vars):
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
    return get_network(id)


#
api_networks_doc["/networks/<id>"] += """
### DELETE

Description:

- Delete a network.
- The user must be responsible for the network.
- The user must be in the NetworkManager privilege group.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the networks table.

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_network(id):
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

