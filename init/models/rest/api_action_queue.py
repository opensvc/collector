#
class rest_get_action_queue(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List service and node actions posted in the action_queue.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/actions?query=status=R",
        ]

        q = q_filter(node_field=db.action_queue.node_id)

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
          "Modify action queue entries",
        ]
        examples = [
          """# curl -u %(email)s -X POST --header 'Content-Type: application/json' -d @/tmp/list.json -o- https://%(collector)s/init/rest/api/actions"""
        ]
        rest_post_handler.__init__(
          self,
          path="/actions",
          tables=["action_queue"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if 'id' not in vars:
           raise Exception("The 'id' key must be specified")
        id = vars["id"]
        del(vars["id"])
        return rest_post_action_queue_one().handler(id, **vars)

#
class rest_put_action_queue(rest_put_handler):
    def __init__(self):
        desc = [
          "Enqueue an action that will be executed by opensvc agents.",
          "The user must be responsible for the target node or service.",
          "The action is logged in the collector's log.",
        ]
        data = """
- <property>=<value> pairs.
- **node_id**
. The node targeted by the action. If svc_id is not specified, the
  action is run using the nodemgr opensvc agent command
- **svc_id**
. The service targeted by the action. The action is run using the
  svcmgr opensvc agent command on the node specified by **node_id**.
- **action**
. The opensvc agent action to execute.
- **module**
. The compliance module to run **action** on.
- **moduleset**
. The compliance moduleset to run **action** on.
- **rid**
. The service resource id to limit **action** to.

Each action has specific property requirements:

- ``compliance_check``:green requires **node_id**, **module** or **moduleset**, optionally
  **svc_id**
- ``compliance_fix``:green requires **node_id**, **module** or **moduleset**, optionally
  **svc_id**
- ``start``:green requires **node_id**, **svc_id**, optionally **rid**
- ``stop``:green requires **node_id**, **svc_id**, optionally **rid**
- ``restart``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncall``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncnodes``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncdrp``:green requires **node_id**, **svc_id**, optionally **rid**
- ``enable``:green requires **node_id**, **svc_id**, optionally **rid**
- ``disable``:green requires **node_id**, **svc_id**, optionally **rid**
- ``freeze``:green requires **node_id**, **svc_id**, optionally **rid**
- ``thaw``:green requires **node_id**, **svc_id**, optionally **rid**
- ``pushasset``:green requires **node_id**
- ``pushdisks``:green requires **node_id**
- ``pull``:green requires **node_id**
- ``push``:green requires **node_id**
- ``pushpkg``:green requires **node_id**
- ``pushpatch``:green requires **node_id**
- ``pushstats``:green requires **node_id**
- ``checks``:green requires **node_id**
- ``sysreport``:green requires **node_id**
- ``updatecomp``:green requires **node_id**
- ``updatepkg``:green requires **node_id**
- ``rotate_root_pw``:green requires **node_id**
- ``scanscsi``:green requires **node_id**
- ``reboot``:green requires **node_id**
- ``schedule_reboot``:green requires **node_id**
- ``unschedule_reboot``:green requires **node_id**
- ``shutdown``:green requires **node_id**
- ``wol``:green requires **node_id**
"""
        examples = [
          "# curl -u %(email)s -o- -X PUT -d node_id=5c977731-0562-11e6-8c70-7e9e6cf13c8a -d action=pushasset https://%(collector)s/init/rest/api/actions",
        ]

        rest_put_handler.__init__(
          self,
          path="/actions",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, **vars):
        action_id = json_action_one(vars)
        if action_id > 0:
            action_q_event()
        else:
            raise Exception("Failed to enqueue action")
        return rest_get_action_queue_one().handler(action_id)

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
        q = q_filter(q, node_field=db.action_queue.node_id)
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
        q = q_filter(q, node_field=db.action_queue.node_id)
        row = db(q).select().first()
        if row is None:
            return dict(info="Action %s does not exist in action queue" % id)
        node_responsible(node_id=row.node_id)
        db(q).delete()
        _log('action_queue.delete',
             'deleted actions %(u)s',
             dict(u=row.command),
             node_id=row.node_id)
        ws_send('action_queue')
        action_q_event()
        return dict(info="Action %s deleted" % id)


#
class rest_post_action_queue_one(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify properties of an action posted in the action queue.",
          "The user must be responsible for the node.",
          "The user must be in the NodeExec or CompExec privilege group.",
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
          tables=["action_queue"],
          examples=examples,
        )

    def handler(self, _id, **vars):
        check_privilege(["NodeExec", "CompExec"])
        q = db.action_queue.id == int(_id)
        q = q_filter(q, node_field=db.action_queue.node_id)
        row = db(q).select().first()
        if row is None:
            return dict(error="Action %s does not exist in action queue" % _id)
        node_responsible(node_id=row.node_id)
        if vars.keys() != ["status"]:
            invalid = ', '.join(sorted(set(vars.keys())-set(["status"])))
            return dict(error="Permission denied: properties not updateable: %(props)s" % dict(props=invalid))
        if row.status == 'T' and vars.get("status") == "C":
            return dict(error="Can not cancel action %d in %s state" % (row.id, row.status))
        if row.status in ('R', 'W') and vars.get("status") == "W":
            return dict(error="Can not redo action %d in %s state" % (row.id, row.status))
        db(q).update(**vars)
        _log('action_queue.update',
             'update properties %(data)s',
             dict(data=beautify_change(row, vars)),
             svc_id=row.svc_id,
             node_id=row.node_id)
        ws_send('action_queue')
        action_q_event()
        return rest_get_action_queue_one().handler(_id)


