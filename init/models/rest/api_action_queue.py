from gluon.dal import smart_query
import json

#
class rest_get_action_queue(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List service and node actions posted in the action_queue.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/actions?query=status=R",
        ]

        q = db.action_queue.id > 0
        q &= _where(q, 'action_queue', domain_perms(), 'nodename')

        rest_get_table_handler.__init__(
          self,
          path="/actions",
          tables=["action_queue"],
          q=q,
          desc=desc,
          examples=examples,
        )


#
class rest_post_action_queue(rest_post_handler):
    def __init__(self):
        desc = [
          "Enqueue an action that will be executed by opensvc agents.",
          "The user must be responsible for the target node or service.",
          "The action is logged in the collector's log.",
        ]
        data = """
- <property>=<value> pairs.
- **nodename**
. The node targeted by the action. If svcname is not specified, the
  action is run using the nodemgr opensvc agent command
- **svcname**
. The service targeted by the action. The action is run using the
  svcmgr opensvc agent command on the node specified by **nodename**.
- **action**
. The opensvc agent action to execute.
- **module**
. The compliance module to run **action** on.
- **moduleset**
. The compliance moduleset to run **action** on.
- **rid**
. The service resource id to limit **action** to.

Each action has specific property requirements:

- ``compliance_check``:green requires **nodename**, **module** or **moduleset**, optionally
  **svcname**
- ``compliance_fix``:green requires **nodename**, **module** or **moduleset**, optionally
  **svcname**
- ``start``:green requires **nodename**, **svcname**, optionally **rid**
- ``stop``:green requires **nodename**, **svcname**, optionally **rid**
- ``restart``:green requires **nodename**, **svcname**, optionally **rid**
- ``syncall``:green requires **nodename**, **svcname**, optionally **rid**
- ``syncnodes``:green requires **nodename**, **svcname**, optionally **rid**
- ``syncdrp``:green requires **nodename**, **svcname**, optionally **rid**
- ``enable``:green requires **nodename**, **svcname**, optionally **rid**
- ``disable``:green requires **nodename**, **svcname**, optionally **rid**
- ``freeze``:green requires **nodename**, **svcname**, optionally **rid**
- ``thaw``:green requires **nodename**, **svcname**, optionally **rid**
- ``pushasset``:green requires **nodename**
- ``pushdisks``:green requires **nodename**
- ``push``:green requires **nodename**
- ``pushpkg``:green requires **nodename**
- ``pushpatch``:green requires **nodename**
- ``pushstats``:green requires **nodename**
- ``checks``:green requires **nodename**
- ``sysreport``:green requires **nodename**
- ``updatecomp``:green requires **nodename**
- ``updatepkg``:green requires **nodename**
- ``rotate_root_pw``:green requires **nodename**
- ``scanscsi``:green requires **nodename**
- ``reboot``:green requires **nodename**
- ``schedule_reboot``:green requires **nodename**
- ``unschedule_reboot``:green requires **nodename**
- ``shutdown``:green requires **nodename**
- ``wol``:green requires **nodename**
"""
        examples = [
          "# curl -u %(email)s -o- -X POST -d nodename=clementine -d action=pushasset https://%(collector)s/init/rest/api/actions",
        ]

        rest_post_handler.__init__(
          self,
          path="/actions",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, **vars):
        n = json_action_one(vars)
        if n > 0:
            action_q_event()
        return dict(info="Accepted to enqueue %d actions" % n)

#
class rest_get_action_queue_stats(rest_get_handler):
    def __init__(self):
        desc = [
          "Display action queue statistics",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/actions/stats",
        ]

        rest_get_handler.__init__(
          self,
          path="/actions/stats",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        return dict(data=action_queue_ws_data())


#
class rest_get_action_queue_one(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of a specific action posted in the action queue.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/actions/10",
        ]

        rest_get_line_handler.__init__(
          self,
          path="/actions/<id>",
          tables=["action_queue"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.action_queue.id == int(id)
        q &= _where(q, 'action_queue', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_action_queue_one(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete an action posted in the action queue.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/actions/10",
        ]

        rest_delete_handler.__init__(
          self,
          path="/actions/<id>",
          tables=["action_queue"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("NodeManager")
        q = db.action_queue.id == int(id)
        q &= _where(q, 'action_queue', domain_perms(), 'nodename')
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
        action_q_event()
        return dict(info="Action %s deleted" % id)


#
class rest_post_action_queue_one(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify properties of an action posted in the action queue.",
          "The user must be responsible for the node.",
          "The user must be in the NodeManager privilege group.",
          "The modification is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(props="status")
        examples = [
          '# curl -u %(email)s -o- -X POST -d status="C" https://%(collector)s/init/rest/api/actions/10',
        ]

        rest_post_handler.__init__(
          self,
          path="/actions/<id>",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, _id, **vars):
        check_privilege("NodeManager")
        q = db.action_queue.id == int(_id)
        q &= _where(q, 'action_queue', domain_perms(), 'nodename')
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
        action_q_event()
        return rest_get_action_queue_one().handler(_id)


