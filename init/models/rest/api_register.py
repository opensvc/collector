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
            raise Exception("The 'nodename' key is mandatory")

        q = db.nodes.nodename == nodename
        row = db(q).select(db.nodes.nodename, db.nodes.team_responsible).first()
        if not row is None:
            if not row.team_responsible in user_groups():
                return dict(error="node already exist and you are not responsible for it")
        else:
            tr = user_primary_group()
            if tr is None:
                tr = user_private_group_id()
            db.nodes.insert(nodename=nodename, team_responsible=tr)
            table_modified("nodes")

        q = db.auth_node.nodename == nodename
        rows = db(q).select()
        if len(rows) != 0:
            _log("node.register",
                 "node '%(node)s' double registration attempt",
                 dict(node=nodename),
                 nodename=nodename,
                 level="warning")
            raise Exception("already registered")
        import uuid
        u = str(uuid.uuid4())
        db.auth_node.insert(nodename=nodename, uuid=u)
        table_modified("auth_node")
        db.commit()
        _log("node.register",
             "node '%(node)s' registered",
             dict(node=nodename),
             nodename=nodename)
        return dict(data={"uuid": u})

