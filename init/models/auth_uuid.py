def auth_uuid(fn):
    def check_auth(node, uuid):
        q = db.auth_node.nodename == node
        q &= db.auth_node.uuid == uuid
        n = db(q).count()
        if n != 1:
            q = db.auth_node.nodename == node
            n = db(q).count()
            if n == 0:
                raise Exception("agent %s not registered"%node)
            else:
                raise Exception("agent authentication error")

    def new(*args, **kwargs):
        try:
            if 'auth' in kwargs:
                uuid, node = kwargs['auth']
            else:
                uuid, node = args[1]
        except:
            raise Exception("no authentication data found in the request")

        try:
            check_auth(node, uuid)
        except Exception as e:
            _log('node.auth',
                 'node authentication error: %(e)s',
                 dict(e=str(e)),
                 nodename=node,
                 user="feed",
                 level="warning")
            raise
        return fn(*args, **kwargs)

    return new

