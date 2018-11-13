class rest_post_register(rest_post_handler):
    def __init__(self):
        desc = [
          "Register a node with user credentials",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d nodename=srv1 -o- https://%(collector)s/init/rest/api/register",
        ]

        rest_post_handler.__init__(
          self,
          path="/register",
          tables=["auth_node"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        nodename = vars.get("nodename")
        if nodename is None:
            raise HTTP(400, "The 'nodename' key is mandatory")

        app = vars.get("app")
        if app is None or app == "None":
            app = user_default_app()
        elif not app in user_apps():
            raise HTTP(403, "You are not responsible for the '%s' app" % app)

        q = db.nodes.nodename == nodename
        q &= db.nodes.app == app
        row = db(q).select(db.nodes.node_id, db.nodes.nodename, db.nodes.app).first()
        if not row is None:
            node_id = row.node_id
        else:
            tr = user_default_group()
            node_id = get_new_node_id()
            db.nodes.insert(
              nodename=nodename,
              team_responsible=tr,
              app=app,
              node_id=node_id
            )
            table_modified("nodes")

        q = db.auth_node.node_id == node_id
        rows = db(q).select()
        if len(rows) == 1:
            _log("node.register",
                 "node %(node)s registered again. resend uuid.",
                 dict(node=node_id),
                 node_id=node_id)
            return dict(
                data={"uuid": rows[0].uuid},
                info="already registered, resend uuid.",
            )
        if len(rows) != 0:
            _log("node.register",
                 "node %(node)s double registration attempt",
                 dict(node=nodename),
                 node_id=node_id,
                 level="warning")
            raise HTTP(200, "already registered")
        import uuid
        u = str(uuid.uuid4())
        db.auth_node.insert(nodename=nodename, uuid=u, node_id=node_id)
        table_modified("auth_node")
        db.commit()
        _log("node.register",
             "node %(node)s registered",
             dict(node=node_id),
             node_id=node_id)
        return dict(data={"uuid": u})

