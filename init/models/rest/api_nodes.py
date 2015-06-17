from gluon.dal import smart_query
import datetime

api_nodes_doc = {}

def node_responsible(nodename):
    q = db.nodes.nodename == nodename
    n = db(q).count()
    if n == 0:
        raise Exception("Node %s does not exist" % nodename)
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id.belongs(user_group_ids())
    n = db(q).count()
    if n != 1:
        raise Exception("Not authorized: user is not responsible for node %s" % nodename)

#
api_nodes_doc["/nodes/<nodename>/ips"] = {}
api_nodes_doc["/nodes/<nodename>/ips"]["GET"] = """
Description:

- List a node ips.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/ips?props=prio,net_network,net_netmask``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(list(set(db.v_nodenetworks.fields) - set(db.nodes.fields)))),
      )

def get_node_ips(nodename, props=None, query=None):
    q = db.v_nodenetworks.nodename == nodename
    q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, tables=["v_nodenetworks"], blacklist=db.nodes.fields)
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["v_nodenetworks"], blacklist=db.nodes.fields)
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)



#
api_nodes_doc["/nodes/<nodename>/disks"] = {}
api_nodes_doc["/nodes/<nodename>/disks"]["GET"] = """
Description:

- List a node disks.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/disks?props=b_disk_app.disk_nodename,b_disk_app.disk_id,stor_array.array_name``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(map(lambda x: "b_disk_app."+x, db.b_disk_app.fields)+map(lambda x: "stor_array."+x, db.stor_array.fields))),
      )

def get_node_disks(nodename, props=None, query=None):
    q = db.b_disk_app.disk_nodename == nodename
    l = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    q &= _where(None, 'b_disk_app', domain_perms(), 'disk_nodename')
    if query:
        cols = props_to_cols(None, ["b_disk_app", "stor_array"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["b_disk_app", "stor_array"])
    data = db(q).select(*cols, left=l, cacheable=True).as_list()
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>/checks"] = {}
api_nodes_doc["/nodes/<nodename>/checks"]["GET"] = """
Description:

- List a node checks.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/checks``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.checks_live.fields)),
      )

def get_node_checks(nodename, props=None, query=None):
    q = db.checks_live.chk_nodename == nodename
    q &= _where(None, 'checks_live', domain_perms(), 'chk_nodename')
    if query:
        cols = props_to_cols(None, ["checks_live"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["checks_live"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>/hbas"] = {}
api_nodes_doc["/nodes/<nodename>/hbas"]["GET"] = """
Description:

- List a node hbas.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/hbas``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.node_hba.fields)),
      )

def get_node_hbas(nodename, props=None, query=None):
    q = db.node_hba.nodename == nodename
    q &= _where(None, 'node_hba', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, ["node_hba"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["node_hba"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>/services"] = {}
api_nodes_doc["/nodes/<nodename>/services"]["GET"] = """
Description:

- List a node services.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/services``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(map(lambda x: "svcmon."+x, db.svcmon.fields)+map(lambda x: "services."+x, db.services.fields))),
      )

def get_node_services(nodename, props=None, query=None):
    q = db.svcmon.mon_nodname == nodename
    l = db.services.on(db.svcmon.mon_svcname == db.services.svc_name)
    q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    if query:
        cols = props_to_cols(None, ["svcmon", "services"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["svcmon", "services"])
    data = db(q).select(*cols, left=l, cacheable=True).as_list()
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>/services/<svcname>"] = {}
api_nodes_doc["/nodes/<nodename>/services/<svcname>"]["GET"] = """
Description:

- Display the specified service on the specified node.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/services``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(map(lambda x: "svcmon."+x, db.svcmon.fields)+map(lambda x: "services."+x, db.services.fields))),
      )

def get_node_service(nodename, svcname, props=None, query=None):
    q = db.svcmon.mon_nodname == nodename
    q = db.svcmon.mon_svcname == svcname
    l = db.services.on(db.svcmon.mon_svcname == db.services.svc_name)
    q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    if query:
        cols = props_to_cols(None, ["svcmon", "services"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["svcmon", "services"])
    data = db(q).select(*cols, left=l, cacheable=True).as_list()
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>/alerts"] = {}
api_nodes_doc["/nodes/<nodename>/alerts"]["GET"] = """
Description:

- List a node alerts.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/alerts?props=dash_nodename,dash_type``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.dashboard.fields)),
      )

def get_node_alerts(nodename, props=None, query=None):
    q = db.dashboard.dash_nodename == nodename
    q &= _where(None, 'dashboard', domain_perms(), 'dash_nodename')
    if query:
        cols = props_to_cols(None, ["dashboard"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, ["dashboard"])
    data = db(q).select(*cols, cacheable=True).as_list()
    data = mangle_alerts(data)
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>"] = {}
api_nodes_doc["/nodes/<nodename>"]["GET"] = """
Description:

- Display all node properties.
- Display selected node properties.

Optional parameters:

- **props**
. A list of properties to include in node data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode?props=nodename,loc_city``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_node(nodename, props=None):
    q = db.nodes.nodename == nodename
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    cols = props_to_cols(props, tables=["nodes"])
    data = db(q).select(*cols, cacheable=True).as_list()[0]
    return dict(data=data)


#
api_nodes_doc["/nodes"] = {}
api_nodes_doc["/nodes"]["GET"] = """
Description:

- List all node names and their selected properties.
- List node names and their selected properties for nodes matching a specified
  filterset id.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, only the node name is included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **fset_id**
. Filter the node names list using the filterset identified by fset_id.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes?props=nodename,loc_city&fset_id=10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_nodes(props=None, fset_id=None, query=None):
    q = db.nodes.id > 0
    q = _where(q, 'nodes', domain_perms(), 'nodename')
    if fset_id:
        q = apply_filters(q, node_field=db.nodes.nodename, fset_id=fset_id)
    if query:
        cols = props_to_cols(None, tables=["nodes"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["nodes"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)


#
api_nodes_doc["/nodes/<nodename>"]["POST"] = """
Description:

- Update a set of node properties.
- The user must be responsible for the node
- The user must be in the NodeManager privilege group
- The updated timestamp is automatically updated.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the nodes table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d loc_city="Zanzibar" -d project="ERP" https://%(collector)s/init/rest/api/nodes/mynode``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def set_node(nodename, **vars):
    check_privilege("NodeManager")
    node_responsible(nodename)
    q = db.nodes.nodename == nodename
    vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db(q).update(**vars)
    _log('rest.nodes.update',
         'update properties %(data)s',
         dict(data=str(vars)),
         nodename=nodename)
    l = {
      'event': 'nodes_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    return get_node(nodename, props=','.join(["nodename","updated"]+vars.keys()))


#
api_nodes_doc["/nodes"]["POST"] = """
Description:

- Create a new node
- If ``team_responsible``:green is not specified, default to user's primary
  group

Data:

- <property>=<value> pairs.
- The nodename property is mandatory.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d nodename=mynode -d loc_city="Zanzibar" -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/nodes``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )


def create_node(**vars):
    check_privilege("NodeManager")
    if 'nodename' not in vars:
        raise Exception("the nodename property must be set in the POST data")
    nodename = vars['nodename']
    vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "team_responsible" not in vars:
        vars["team_responsible"] = user_primary_group()
    db.nodes.insert(**vars)
    _log('rest.nodes.create',
         'create properties %(data)s',
         dict(data=str(vars)),
         nodename=nodename)
    l = {
      'event': 'nodes_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    return get_node(nodename)


#
api_nodes_doc["/nodes/<nodename>"]["DELETE"] = """
Description:

- Delete a node.
- The user must be responsible for the node.
- The user must be in the NodeManager privilege group.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the nodes table.

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/nodes/mynode``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_node(nodename):
    node_responsible(nodename)
    check_privilege("NodeManager")
    q = db.nodes.nodename == nodename
    db(q).delete()
    _log('rest.nodes.delete',
         '',
         dict(),
         nodename=nodename)
    l = {
      'event': 'nodes_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    return dict(info="Node %s deleted" % nodename)

