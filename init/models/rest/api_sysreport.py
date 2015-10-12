from gluon.dal import smart_query
import json

#
class rest_get_node_sysreport(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node file changes timeline for files tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/sysreport",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
          "begin": {
            "desc": "A date, like 2010-01-01 00:00, limiting the sysreport extract to more recent changes.",
          },
          "end": {
            "desc": "A date, like 2010-01-01 00:00, limiting the sysreport extract to older changes.",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<nodename>/sysreport",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        return dict(data=lib_get_sysreport(nodename, **vars))

#
class rest_get_node_sysreport_commit(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node detailled changes detected at a specified date, expressed as a commit id, on files tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<nodename>/sysreport/<cid>",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, nodename, cid, **vars):
        return dict(data=lib_get_sysreport_commit(nodename, cid, **vars))

#
class rest_get_node_sysreport_commit_tree(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node tracked file tree at a specific date, expressed as a commit id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0/tree",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<nodename>/sysreport/<cid>/tree",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, nodename, cid, **vars):
        return dict(data=lib_get_sysreport_commit_tree(nodename, cid, **vars))

#
class rest_get_node_sysreport_commit_tree_file(rest_get_handler):
    def __init__(self):
        desc = [
          "Display a node specific file content at a specific date, expressed as a commit id. The file is identified by its id, as reported in the /node/<nodename>sysreport/<cid>/tree output",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0/tree/c5bc459a691a0eab9b8c93b7f31e5a8d73c409ad",
        ]

        rest_get_handler.__init__(
          self,
          path="/nodes/<nodename>/sysreport/<cid>/tree/<oid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, cid, oid, **vars):
        return dict(data=lib_get_sysreport_commit_tree_file(nodename, cid, oid, **vars))

#
class rest_get_node_sysreport_timediff(rest_get_handler):
    def __init__(self):
        desc = [
          "Display changes between begin and end dates as a single diff per file tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/sysreport/timediff?begin=2015-01-01 00:00:00",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
          "begin": {
            "desc": "A date specifying the diff initial file state",
          },
          "end": {
            "desc": "A date specifying the diff terminal file state",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<nodename>/sysreport/timediff",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        return dict(data=lib_get_sysreport_timediff(nodename, **vars))


#
# Secure pattern handlers
#

#
class rest_get_sysreport_secure_patterns(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List sysreport secure patterns.",
          "A secure pattern is a regular expression.",
          "The content and diffs on files whose path matches any pattern are only shown to managers and node responsibles.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/secure_patterns"
        ]
        q = db.sysrep_secure.id > 0
        o = db.sysrep_secure.pattern > 0
        rest_get_table_handler.__init__(
          self,
          path="/sysreport/secure_patterns",
          tables=["sysrep_secure"],
          q=q,
          orderby=o,
          desc=desc,
          examples=examples,
        )

#
class rest_get_sysreport_secure_pattern(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a sysreport secure pattern.",
          "A secure pattern is a regular expression.",
          "The content and diffs on files whose path matches any pattern are only shown to managers and node responsibles.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/secure_patterns"
        ]
        q = db.sysrep_secure.id > 0
        o = db.sysrep_secure.pattern > 0
        rest_get_line_handler.__init__(
          self,
          path="/sysreport/secure_patterns/<id>",
          tables=["sysrep_secure"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.sysrep_secure.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_sysreport_secure_pattern(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a sysreport secure pattern.",
          "A secure pattern is a regular expression.",
          "The content and diffs on files whose path matches any pattern are only shown to managers and node responsibles.",
          "The user must be in the Manager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/sysreport/secure_patterns/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/sysreport/secure_patterns/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")
        q = db.sysrep_secure.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="secure pattern does not exist")
        db(q).delete()
        _log('rest.sysreport.secure_pattern.delete',
             'secure pattern %(s)s deleted',
             dict(s=row.pattern),
            )
        l = {
          'event': 'sysrep_secure_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="secure pattern %(s)s deleted" % dict(s=row.pattern))

#
class rest_post_sysreport_secure_pattern(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a secure pattern.",
          "A secure pattern is a regular expression.",
          "The content and diffs on files whose path matches any pattern are only shown to managers and node responsibles.",
          "The user must be in the Manager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d pattern=".*/etc/passwd" https://%(collector)s/init/rest/api/sysreport/secure_patterns""",
        ]
        rest_post_handler.__init__(
          self,
          path="/sysreport/secure_patterns",
          tables=["sysrep_secure"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("Manager")
        if len(vars) == 0 or "pattern" not in vars:
            raise Exception("Insufficient data")
        q = db.sysrep_secure.id > 0
        for v in vars:
            q &= db.sysrep_secure[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return dict(info="Secure pattern already exists")
        response = db.sysrep_secure.validate_and_insert(**vars)
        raise_on_error(response)
        row = db(q).select().first()
        _log('rest.sysreport.secure_pattern.create',
             'pattern %(s)s created.',
             dict(s=row.pattern),
            )
        l = {
          'event': 'sysrep_secure_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_sysreport_secure_pattern().handler(row.id)


