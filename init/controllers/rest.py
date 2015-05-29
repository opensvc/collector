import datetime

def call():
    session.forget()
    return service()

@request.restful()
@auth.requires_login()
def api():
    def GET(*args, **vars):
        # the default restful wrapper suppress the trailing .xxx
        # we need it for nodenames and svcname though.
        args = request.raw_args.split('/')

        try:
            n_args = len(args)
            if n_args == 0:
                return doc()
            if n_args == 1:
                if args[0] == "":
                    return doc()
                if args[0] == "nodes":
                    return get_nodes(**vars)
                if args[0] == "filtersets":
                    return get_filtersets(**vars)
            if n_args == 2:
                if args[0] == "nodes":
                    return get_node(args[1], **vars)
            if n_args == 3:
                if args[0] == "nodes" and args[2] == "disks":
                    return get_node_disks(args[1], **vars)
                if args[0] == "nodes" and args[2] == "ips":
                    return get_node_ips(args[1], **vars)
                if args[0] == "nodes" and args[2] == "alerts":
                    return get_node_alerts(args[1], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    def POST(*args, **vars):
        args = request.raw_args.split('/')
        try:
            n_args = len(args)
            if n_args == 1:
                if args[0] == "nodes":
                    return create_node(**vars)
            if n_args == 2:
                if args[0] == "nodes":
                    return set_node(args[1], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    def PUT(*args, **vars):
        args = request.raw_args.split('/')
        return dict()
    def DELETE(*args, **vars):
        args = request.raw_args.split('/')
        try:
            n_args = len(args)
            if n_args == 2:
                if args[0] == "nodes":
                    return delete_node(args[1], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    return locals()

def doc():
    s = MARKMIN("""
# RESTful API documentation


## ``/api/nodes``:red

### GET

Description:

- List all node names and their selected properties.
- List node names and their selected properties for nodes matching a specified
  filterset id.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, only the node name is included.
. The separator is ','.
. Available properties are: ``%(nodes_props)s``:green.

- **fset_id**
. Filter the node names list using the filterset identified by fset_id.

Example:

``# curl -u me:mypass -o- https://%(collector)s/init/rest/api/nodes?props=nodename,loc_city&fset_id=10``

### POST

Description:

- Create a new node
- Don't forget to set a ``team_responsible``:green, or you won't be able to change
  properties through the API afterwards

Data:

- <property>=<value> pairs.
- The nodename property is mandatory.
- Available properties are: ``%(nodes_props)s``:green.

Example:

``# curl -u me:mypass -o- -d nodename=mynode -d loc_city="Zanzibar" -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/nodes``


## ``/api/nodes/<nodename>``:red

### GET

Description:

- Display all node properties.
- Display selected node properties.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(nodes_props)s``:green.

Example:

``# curl -u me:mypass -o- https://%(collector)s/init/rest/api/nodes/mynode?props=nodename,loc_city``

### POST

Description:

- Update a set of node properties.
- The user must be responsible for the node
- The user must be in the NodeManager privilege group
- The updated timestamp is automatically updated.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the nodes table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(nodes_props)s``:green.

Example:

``# curl -u me:mypass -o- -d loc_city="Zanzibar" -d project="ERP" https://%(collector)s/init/rest/api/nodes/mynode``


### DELETE

Description:

- Delete a node.
- The user must be responsible for the node.
- The user must be in the NodeManager privilege group.
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the nodes table.

Example:

``# curl -u me:mypass -o- -X DELETE https://%(collector)s/init/rest/api/nodes/mynode``


## ``/api/nodes/<nodename>/alerts``:red

### GET

Description:

- List a node alerts.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(nodes_alerts_props)s``:green.

Example:

``# curl -u me:mypass -o- https://%(collector)s/init/rest/api/nodes/mynode/alerts?props=dash_nodename,dash_type``


## ``/api/nodes/<nodename>/disks``:red

### GET

Description:

- List a node disks.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(nodes_disks_props)s``:green.

Example:

``# curl -u me:mypass -o- https://%(collector)s/init/rest/api/nodes/mynode/disks?props=b_disk_app.disk_nodename,b_disk_app.disk_id,stor_array.array_name``


## ``/api/nodes/<nodename>/ips``:red

### GET

Description:

- List a node disks.

Optional parameters:

- **props**
. A list of properties to include in each node data.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(nodes_ips_props)s``:green.

Example:

``# curl -u readonly:readonly -o- https://%(collector)s/init/rest/api/nodes/mynode/ips?props=prio,net_network,net_netmask``


## ``/api/filtersets``:red

### GET

Description:

- List all existing filtersets.
- List the existing filtersets matching a pattern.

Optional parameters:

- **like**
. Filter the filtersets list using this like sql pattern.
. The multi-character wildcard is '%%'.
. The one-character wildcard is '_'.

Example:

``# curl -u readonly:readonly -o- https://%(collector)s/init/rest/api/filtersets?like=%%aix%%``


""" % dict(
        collector=request.env.http_host,
        nodes_props=", ".join(sorted(db.nodes.fields)),
        nodes_ips_props=", ".join(sorted(list(set(db.v_nodenetworks.fields) - set(db.nodes.fields)))),
        nodes_alerts_props=", ".join(sorted(db.dashboard.fields)),
        nodes_disks_props=", ".join(sorted(map(lambda x: "b_disk_app."+x, db.b_disk_app.fields)+map(lambda x: "stor_array."+x, db.stor_array.fields))),
      )
    )
    return dict(doc=DIV(s, _style="padding:1em;text-align:left"))

def props_to_cols(props, tables=[], blacklist=[]):
    if props is None:
        if len(tables) == 1:
            table = tables[0]
            cols = []
            for p in set(db[table].fields) - set(blacklist):
                cols.append(db[table][p])
            return cols
        else:
            cols = []
            for table in tables:
                for p in set(db[table].fields) - set(blacklist):
                    cols.append(db[table][p])
            return cols
    cols = []
    for p in props.split(","):
        v = p.split(".")
        if len(v) == 1 and len(tables) == 1:
            v = [tables[0], p]
        cols.append(db[v[0]][v[1]])
    return cols

def get_node_ips(nodename, props=None):
    q = db.v_nodenetworks.nodename == nodename
    q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
    cols = props_to_cols(props, tables=["v_nodenetworks"], blacklist=db.nodes.fields)
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

def get_node_disks(nodename, props=None):
    q = db.b_disk_app.disk_nodename == nodename
    l = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    q &= _where(None, 'b_disk_app', domain_perms(), 'disk_nodename')
    cols = props_to_cols(props, ["b_disk_app", "stor_array"])
    data = db(q).select(*cols, left=l, cacheable=True).as_list()
    return dict(data=data)

def get_node_alerts(nodename, props=None):
    q = db.dashboard.dash_nodename == nodename
    q &= _where(None, 'dashboard', domain_perms(), 'dash_nodename')
    cols = props_to_cols(props, ["dashboard"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

def get_node(nodename, props=None):
    q = db.nodes.nodename == nodename
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    cols = props_to_cols(props, tables=["nodes"])
    data = db(q).select(*cols, cacheable=True).as_list()[0]
    return dict(data=data)

def get_nodes(props="nodename", fset_id=None):
    q = db.nodes.id > 0
    q &= _where(None, 'nodes', domain_perms(), 'nodename')
    if fset_id:
        q = apply_filters(q, node_field=db.nodes.nodename, fset_id=fset_id)
    cols = props_to_cols(props, tables=["nodes"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)

def get_filtersets(like=None):
    q = db.gen_filtersets.id > 0
    if like:
        q &= db.gen_filtersets.fset_name.like(like)
    data = db(q).select().as_list()
    return dict(data=data)

def check_privilege(priv):
    ug = user_groups()
    if priv not in ug:
        raise Exception("Not authorized: user has no %s privilege" % priv)

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

def create_node(**vars):
    check_privilege("NodeManager")
    if 'nodename' not in vars:
        raise Exception("the nodename property must be set in the POST data")
    nodename = vars['nodename']
    vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
