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


