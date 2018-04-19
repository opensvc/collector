import json

#
class rest_get_node_sysreport(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node file changes timeline for files tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/1/sysreport",
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
          path="/nodes/<id>/sysreport",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        return dict(data=lib_get_sysreport([node_id], **vars))

#
class rest_get_sysreport_timeline(rest_get_handler):
    def __init__(self):
        desc = [
          "Display multiple nodes file changes timeline for files tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport?nodes=1,2",
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
          path="/sysreport/timeline",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        if "nodes" in vars:
            nodes = vars.get("nodes")
            del(vars["nodes"])
        elif "nodes[]" in vars:
            nodes = vars.get("nodes[]")
            del(vars["nodes[]"])
        else:
            raise HTTP(400, "The nodes parameter is mandatory")
        if type(nodes) != list:
            nodes = nodes.split(",")
        nodes = map(lambda x: get_node_id(x), nodes)
        return dict(data=lib_get_sysreport(nodes, **vars))

#
class rest_get_node_sysreport_commit(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node detailled changes detected at a specified date, expressed as a commit id, on files tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/1/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<id>/sysreport/<cid>",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, node_id, cid, **vars):
        node_id = get_node_id(node_id)
        return dict(data=lib_get_sysreport_commit(node_id, cid, **vars))

#
class rest_get_node_sysreport_commit_tree(rest_get_handler):
    def __init__(self):
        desc = [
          "Display node tracked file tree at a specific date, expressed as a commit id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/1/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0/tree",
        ]
        params = {
          "path": {
            "desc": "A path glob to limit the sysreport extract to",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/nodes/<id>/sysreport/<cid>/tree",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, node_id, cid, **vars):
        node_id = get_node_id(node_id)
        return dict(data=lib_get_sysreport_commit_tree(node_id, cid, **vars))

#
class rest_get_node_sysreport_commit_tree_file(rest_get_handler):
    def __init__(self):
        desc = [
          "Display a node specific file content at a specific date, expressed as a commit id. The file is identified by its id, as reported in the /node/<id>sysreport/<cid>/tree output",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/1/sysreport/903e92e2b80a3504d862888e48b2430ae15136f0/tree/c5bc459a691a0eab9b8c93b7f31e5a8d73c409ad",
        ]

        rest_get_handler.__init__(
          self,
          path="/nodes/<id>/sysreport/<cid>/tree/<oid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, cid, oid, **vars):
        node_id = get_node_id(node_id)
        return dict(data=lib_get_sysreport_commit_tree_file(node_id, cid, oid, **vars))

#
class rest_get_node_sysreport_timediff(rest_get_handler):
    def __init__(self):
        desc = [
          "Display changes between begin and end dates as a single diff per file tracked by sysreport.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/1/sysreport/timediff?begin=2015-01-01 00:00:00",
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
          path="/nodes/<id>/sysreport/timediff",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        return dict(data=lib_get_sysreport_timediff(node_id, **vars))


#
class rest_get_sysreport_nodediff(rest_get_handler):
    def __init__(self):
        desc = [
          "Display differences in files tracked by sysreport at the same path on multiple nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/nodediff?nodes=1,2&path=.*resolv.*",
        ]
        params = {
          "nodes": {
            "desc": "The comma-separated list of node ids to compare.",
          },
          "path": {
            "desc": "A path glob to limit the sysreport extract to.",
          },
          "ignore_blanks": {
            "desc": "A true/false value indicating the user wants the report to include differences in lines caused only by whitespacing differences.",
          },
        }

        rest_get_handler.__init__(
          self,
          path="/sysreport/nodediff",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        if "nodes" in vars:
            nodes = vars["nodes"].split(",")
            del(vars["nodes"])
        elif "nodes[]" in vars:
            nodes = vars["nodes[]"]
            del(vars["nodes[]"])
        else:
            raise HTTP(400, T("The nodes parameter is mandatory"))

        nodes = map(lambda x: get_node_id(x), nodes)

        if "ignore_blanks" in vars and vars["ignore_blanks"] in ("True", "true", True, "y", "Y", "yes", "Yes", "1"):
            vars["ignore_blanks"] = True
        else:
            vars["ignore_blanks"] = False

        return dict(data=lib_get_sysreport_nodediff(nodes, **vars))


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
        o = db.sysrep_secure.pattern
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
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/secure_patterns/1"
        ]
        q = db.sysrep_secure.id > 0
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
            return dict(info=T("secure pattern does not exist"))
        db(q).delete()
        _log('rest.sysreport.secure_pattern.delete',
             'secure pattern %(s)s deleted',
             dict(s=row.pattern),
            )
        ws_send('sysrep_secure_change')
        return dict(info=T("secure pattern %(s)s deleted" % dict(s=row.pattern)))

#
class rest_post_sysreport_secure_patterns(rest_post_handler):
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
            raise HTTP(400, T("Insufficient data"))
        q = db.sysrep_secure.id > 0
        for v in vars:
            q &= db.sysrep_secure[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return dict(info=T("Secure pattern already exists"))
        response = db.sysrep_secure.validate_and_insert(**vars)
        raise_on_error(response)
        row = db(q).select().first()
        _log('rest.sysreport.secure_pattern.create',
             'pattern %(s)s created.',
             dict(s=row.pattern),
            )
        ws_send('sysrep_secure_change')
        return rest_get_sysreport_secure_pattern().handler(row.id)


#
# authorizations handlers
#

#
class rest_get_sysreport_authorizations(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List sysreport authorizations.",
          "An authorization is a organizational group - filterset - regular expression tuple.",
          "Members of the group can see sysreport diff and content of files matching the regular expression from the nodes matching the filterset",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/authorizations"
        ]
        q = db.v_sysrep_allow.id > 0
        o = db.v_sysrep_allow.group_name | db.v_sysrep_allow.fset_name | db.v_sysrep_allow.pattern
        rest_get_table_handler.__init__(
          self,
          path="/sysreport/authorizations",
          tables=["v_sysrep_allow"],
          q=q,
          orderby=o,
          desc=desc,
          examples=examples,
        )

#
class rest_get_sysreport_authorization(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display an authorization.",
          "An authorization is a organizational group - filterset - regular expression tuple.",
          "Members of the group can see sysreport diff and content of files matching the regular expression from the nodes matching the filterset",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/sysreport/authorizations/1"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/sysreport/authorizations/<id>",
          tables=["v_sysrep_allow"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_sysrep_allow.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_sysreport_authorization(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a sysreport authorization.",
          "An authorization is a organizational group - filterset - regular expression tuple.",
          "Members of the group can see sysreport diff and content of files matching the regular expression from the nodes matching the filterset",
          "The user must be in the Manager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/sysreport/authorizations/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/sysreport/authorizations/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")
        q = db.sysrep_allow.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info=T("Authorization does not exist"))

        group_name = group_role(row.id)
        if group_name is None:
            group_name = str(row.id)

        fset_name = lib_fset_name(row.fset_id)
        if fset_name is None:
            fset_name = str(row.fset_id)

        s = '-'.join((group_name, fset_name, str(row.pattern)))

        db(q).delete()
        _log('rest.sysreport.authorization.delete',
             'authorization %(s)s deleted',
             dict(s=s),
            )
        ws_send('sysrep_allow_change')
        return dict(info=T("authorization %(s)s deleted" % dict(s=s)))

#
class rest_post_sysreport_authorizations(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a sysreport authorization.",
          "An authorization is a organizational group - filterset - regular expression tuple.",
          "Members of the group can see sysreport diff and content of files matching the regular expression from the nodes matching the filterset.",
          "The user must be in the Manager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        data = """
- **group_name**
. The name of the organizational group to authorize.
. Exclusive with **group_id**.

- **group_id**::
. The id of the organizational group to authorize.
. Exclusive with **group_name**.

- **fset_name**::
. The name of the filterset to use to determine on which nodes the authorization applies.
. Exclusive with **fset_id**.

- **fset_id**::
. The id of the filterset to use to determine on which nodes the authorization applies.
. Exclusive with **fset_name**.
"""

        examples = [
          """# curl -u %(email)s -o- -X POST -d group_name="mygroup" -d fset_name="myfset" -d pattern=".*" https://%(collector)s/init/rest/api/sysreport/authorizations""",
        ]
        rest_post_handler.__init__(
          self,
          path="/sysreport/authorizations",
          tables=["sysrep_allow"],
          data=data,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("Manager")

        if "group_id" in vars:
            try:
                _group_id = int(vars["group_id"])
            except:
                raise HTTP(400, T("Group id %(g)s is not integer", dict(g=vars["group_id"])))
            _group_name = group_role(_group_id)
            if _group_name is None:
                raise HTTP(404, T("Group %(g)s does not exist", dict(vars["group_id"])))
        elif "group_name" in vars:
            _group_id = lib_group_id(vars["group_name"])
            if _group_id is None:
                raise HTTP(404, T("Group %(g)s does not exist", dict(g=vars["group_name"])))
            _group_name = vars["group_name"]
        else:
            raise HTTP(400, T("nor group_id nor group_name found in post data"))


        if "fset_id" in vars:
            try:
                _fset_id = int(vars["fset_id"])
            except:
                raise HTTP(400, T("Fset id %(f)s is not integer", dict(f=vars["fset_id"])))
            _fset_name = lib_fset_name(_fset_id)
        elif "fset_name" in vars:
            _fset_id = lib_fset_id(vars["fset_name"])
            if _fset_id is None:
                raise HTTP(404, T("Filterset %(f)s does not exist", dict(f=vars["fset_name"])))
            _fset_name = vars["fset_name"]
        else:
            raise HTTP(400, T("nor fset_id nor fset_name found in post data"))

        s = "-".join((_group_name, _fset_name, vars["pattern"]))

        q = db.sysrep_allow.pattern == vars["pattern"]
        q &= db.sysrep_allow.group_id == _group_id
        q &= db.sysrep_allow.fset_id == _fset_id
        row = db(q).select().first()
        if row is not None:
            return dict(info=T("Authorization already exists"))
        response = db.sysrep_allow.validate_and_insert(
          group_id=_group_id,
          fset_id=_fset_id,
          pattern=vars["pattern"],
        )
        raise_on_error(response)
        row = db(q).select().first()
        _log('rest.sysreport.authorization.create',
             'authorization %(s)s created.',
             dict(s=s)
            )
        ws_send('sysrep_allow_change')
        return rest_get_sysreport_authorization().handler(row.id)


