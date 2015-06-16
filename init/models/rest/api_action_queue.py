from gluon.dal import smart_query
import json

api_action_queue_doc = {}


#
api_action_queue_doc["/action_queue"] = """
### GET

Description:

- List service and node actions posted in the action_queue.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/action_queue?query=status=R``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.action_queue.fields)),
      )

def get_action_queue(props=None, query=None):
    q = db.action_queue.id > 0
    if query:
        cols = props_to_cols(None, tables=["action_queue"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["action_queue"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_action_queue_doc["/action_queue/<id>"] = """
### GET

Description:

- Display properties of a specific action posted in the action queue

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/action_queue/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.action_queue.fields)),
      )

def get_action_queue_one(id, props=None):
    q = db.action_queue.id == int(id)
    cols = props_to_cols(props, tables=["action_queue"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_action_queue_doc["/action_queue/<id>"] += """
### DELETE

Description:

- Delete an action posted in the action queue

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/action_queue/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_action_queue_one(id, props=None):
    check_privilege("NodeManager")
    q = db.action_queue.id == int(id)
    row = db(q).select().first()
    if row is None:
        return dict(info="Action %s does not exist in action queue" % id)
    node_responsible(row.nodename)
    db(q).delete()
    _log('rest.action.delete',
         'deleted actions %(u)s',
         dict(u=row.command),
         nodename=row.nodename)
    l = {
      'event': 'action_queue',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))
    return dict(info="Action %s deleted" % id)

api_action_queue_doc["/action_queue/<id>"] += """
### POST

Description:

- Modify properties of an action posted in the action queue
- The user must be responsible for the node
- The user must be in the NodeManager privilege group
- The modification is logged in the collector's log.
- A websocket event is sent to announce the change in the table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -X POST -d status="C" https://%(collector)s/init/rest/api/action_queue/10``

""" % dict(
        email=user_email(),
        props="status",
        collector=request.env.http_host,
      )

def set_action_queue_one(_id, **vars):
    check_privilege("NodeManager")
    q = db.action_queue.id == int(_id)
    row = db(q).select().first()
    if row is None:
        return dict(error="Action %s does not exist in action queue" % _id)
    node_responsible(row.nodename)
    if vars.keys() != ["status"]:
        invalid = ', '.join(sorted(set(vars.keys())-set(["status"])))
        return dict(error="Permission denied: properties not updateable: %(props)s" % dict(props=invalid))
    db(q).update(**vars)
    _log('rest.action.update',
         'update properties %(data)s',
         dict(data=str(vars)),
         svcname=row.svcname,
         nodename=row.nodename)
    l = {
      'event': 'action_queue',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))
    return get_action_queue_one(_id)


