from gluon.dal import smart_query
import json

def moduleset_id_q(id):
    try:
        id = int(id)
        q = db.comp_moduleset.id == id
    except:
        q = db.comp_moduleset.modset_name == id
    return q

def ruleset_id_q(id):
    try:
        id = int(id)
        q = db.comp_rulesets.id == id
    except:
        q = db.comp_rulesets.ruleset_name == id
    return q

#
class rest_get_compliance_status(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' last check run."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/status?query=run_status=1 and run_module=mymod"
        ]
        q = db.comp_status.id > 0
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        rest_get_table_handler.__init__(
          self,
          path="/compliance/status",
          tables=["comp_status"],
          q=q,
          desc=desc,
          examples=examples,
        )

#
class rest_get_compliance_status_one(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of the last check run of a specific module-node-service tuple"
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/status/10"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/compliance/status/<id>",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.comp_status.id == int(id)
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_compliance_status_run(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete the last check run information of a specific module-node-service tuple.",
          "Requires the CompManager privilege and node ownership.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/status/10"
        ]

        rest_delete_handler.__init__(
          self,
          path="/compliance/status/<id>",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CompManager")
        q = db.comp_status.id == int(id)
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        row = db(q).select().first()
        if row is None:
            return dict(info="Task %s does not exist in the scheduler" % id)
        node_responsible(row.run_nodename)
        db(q).delete()
        _log('rest.compliance.status.delete',
             'deleted run %(u)s',
             dict(u="-".join((row.run_module, row.run_nodename, row.run_svcname if row.run_svcname else ""))),
             nodename=row.run_nodename,
             svcname=row.run_svcname,
        )
        return dict(info="Run %s deleted" % id)

#
class rest_delete_compliance_ruleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a ruleset.",
          "All ruleset parent and child relations are also removed.",
          "All ruleset nodes and services attachements are also removed.",
          "All ruleset publication and responsible groups are also detached.",
          "The user have the CompManager privilege.",
          "One of the user's groups must be responsible for the ruleset.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/rulesets/10"
        ]

        rest_delete_handler.__init__(
          self,
          path="/compliance/rulesets/<id>",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
        except:
            id = comp_ruleset_id(id)
        delete_ruleset(id)
        return dict(info="Ruleset %s deleted" % id)

#
class rest_post_compliance_rulesets(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a ruleset.",
          "The user have the CompManager privilege.",
          "The created ruleset inherits the user's primary group as publication and responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the rulesets table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d ruleset_name="testapi" https://%(collector)s/init/rest/api/compliance/rulesets""",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/rulesets",
          tables=["comp_rulesets"],
          props_blacklist=["created", "author"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        ruleset_name = vars.get("ruleset_name")
        obj_id = create_ruleset(ruleset_name)
        return rest_get_compliance_ruleset().handler(obj_id)

#
class rest_delete_compliance_moduleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a moduleset.",
          "All moduleset parent and child relations are also removed.",
          "All moduleset nodes and services attachements are also removed.",
          "All moduleset publication and responsible groups are also detached.",
          "The user have the CompManager privilege.",
          "One of the user's groups must be responsible for the moduleset.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/modulesets/10"
        ]

        rest_delete_handler.__init__(
          self,
          path="/compliance/modulesets/<id>",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
        except:
            id = comp_moduleset_id(id)
        delete_moduleset(id)
        return dict(info="Moduleset %s deleted" % id)

#
class rest_post_compliance_modulesets(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a moduleset.",
          "The user have the CompManager privilege.",
          "The created moduleset inherits the user's primary group as publication and responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the modulesets table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d modset_name="testapi" https://%(collector)s/init/rest/api/compliance/modulesets""",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/modulesets",
          tables=["comp_moduleset"],
          props_blacklist=["created", "author"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        modset_name = vars.get("modset_name")
        obj_id = create_moduleset(modset_name)
        return rest_get_compliance_moduleset().handler(obj_id)

#
class rest_get_compliance_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List modulesets published to the requesting user's groups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/modulesets"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/compliance/modulesets",
          tables=["comp_moduleset"],
          groupby=db.comp_moduleset.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_moduleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_compliance_moduleset(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the moduleset properties, if published to the requesting users's group.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/modulesets/2"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/compliance/modulesets/<id>",
          tables=["comp_moduleset"],
          groupby=db.comp_moduleset.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= moduleset_id_q(id)
        q &= db.comp_moduleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_compliance_moduleset_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export the moduleset in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/modulesets/2/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/compliance/modulesets/<id>/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
        except:
            id = comp_moduleset_id(id)
        return _export_modulesets([id])


#
class rest_get_compliance_modulesets_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export all modulesets in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/modulesets/2/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/compliance/modulesets/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_moduleset.id > 0
        q &= db.comp_moduleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
        ids = [r.id for r in db(q).select(db.comp_moduleset.id)]
        return _export_modulesets(ids)


#
class rest_get_compliance_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List rulesets published to the requesting users's group.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/rulesets"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/compliance/rulesets",
          tables=["comp_rulesets"],
          groupby=db.comp_rulesets.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_compliance_ruleset(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the ruleset properties, if published to the requesting users's group.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/rulesets/2"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/compliance/rulesets/<id>",
          tables=["comp_rulesets"],
          groupby=db.comp_rulesets.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= ruleset_id_q(id)
        q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_compliance_ruleset_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export the ruleset in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/rulesets/2/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/compliance/rulesets/<id>/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
        except:
            id = comp_ruleset_id(id)
        return _export_rulesets([id])


#
class rest_get_compliance_rulesets_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export all rulesets in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/rulesets/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/compliance/rulesets/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.auth_group.id.belongs(user_group_ids())
        q &= db.comp_rulesets.id > 0
        q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
        q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
        ids = [r.id for r in db(q).select(db.comp_rulesets.id)]
        return _export_rulesets(ids)


#
class rest_delete_compliance_moduleset_moduleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a moduleset from a moduleset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/modulesets/10/modulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/compliance/modulesets/<id>/modulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_modset_id, child_modset_id, **vars):
        try:
            parent_modset_id = int(parent_modset_id)
        except:
            parent_modset_id = comp_moduleset_id(parent_modset_id)
        try:
            child_modset_id = int(child_modset_id)
        except:
            child_modset_id = comp_moduleset_id(child_modset_id)
        try:
            detach_moduleset_from_moduleset(child_modset_id, parent_modset_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="moduleset detached")

#
class rest_post_compliance_moduleset_moduleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a moduleset to a moduleset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/compliance/modulesets/10/modulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/modulesets/<id>/modulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_modset_id, child_modset_id, **vars):
        try:
            parent_modset_id = int(parent_modset_id)
        except:
            parent_modset_id = comp_moduleset_id(parent_modset_id)
        try:
            child_modset_id = int(child_modset_id)
        except:
            child_modset_id = comp_moduleset_id(child_modset_id)
        try:
            attach_moduleset_to_moduleset(child_modset_id, parent_modset_id)
        except CompError as e:
            return dict(error=str(e))
        except CompInfo as e:
            return dict(info=str(e))
        return dict(info="moduleset attached")

#
class rest_delete_compliance_moduleset_ruleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a ruleset from a moduleset",
          "Attached rulesets add their variables to the moduleset's modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/modulesets/10/rulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/compliance/modulesets/<id>/rulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, modset_id, rset_id, **vars):
        try:
            modset_id = int(modset_id)
        except:
            modset_id = comp_moduleset_id(modset_id)
        try:
            rset_id = int(rset_id)
        except:
            rset_id = comp_ruleset_id(rset_id)
        try:
            detach_ruleset_from_moduleset(rset_id, modset_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="ruleset detached")

#
class rest_post_compliance_moduleset_ruleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a ruleset to a moduleset",
          "Attached rulesets add their variables to the moduleset's modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/compliance/modulesets/10/rulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/modulesets/<id>/rulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, modset_id, rset_id, **vars):
        try:
            modset_id = int(modset_id)
        except:
            modset_id = comp_moduleset_id(modset_id)
        try:
            rset_id = int(rset_id)
        except:
            rset_id = comp_ruleset_id(rset_id)
        try:
            attach_ruleset_to_moduleset(rset_id, modset_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="ruleset attached")

#
class rest_delete_compliance_ruleset_ruleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a ruleset from a ruleset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/rulesets/10/rulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/compliance/rulesets/<id>/rulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_rset_id, child_rset_id, **vars):
        try:
            parent_rset_id = int(parent_rset_id)
        except:
            parent_rset_id = comp_ruleset_id(parent_rset_id)
        try:
            child_rset_id = int(child_rset_id)
        except:
            child_rset_id = comp_ruleset_id(child_rset_id)
        try:
            detach_ruleset_from_ruleset(child_rset_id, parent_rset_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="ruleset detached")

#
class rest_post_compliance_ruleset_ruleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a ruleset to a ruleset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/compliance/rulesets/10/rulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/rulesets/<id>/rulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_rset_id, child_rset_id, **vars):
        try:
            parent_rset_id = int(parent_rset_id)
        except:
            parent_rset_id = comp_ruleset_id(parent_rset_id)
        try:
            child_rset_id = int(child_rset_id)
        except:
            child_rset_id = comp_ruleset_id(child_rset_id)
        try:
            attach_ruleset_to_ruleset(child_rset_id, parent_rset_id)
        except CompError as e:
            return dict(error=str(e))
        return dict(info="ruleset attached")

#
class rest_post_compliance_ruleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a set of ruleset properties.",
          "The user must be responsible for the ruleset.",
          "The user must be in the CompManager privilege group.",
          "The updated timestamp is automatically updated.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the rulesets table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d public=true https://%(collector)s/init/rest/api/compliance/rulesets/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/compliance/rulesets/<id>",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("CompManager")
        try:
            id = int(id)
        except:
            id = comp_ruleset_id(id)
        if id is None:
            return dict(error="ruleset not found")
        if not ruleset_responsible(id):
            return dict(error="you are not responsible for this ruleset")
        q = db.comp_rulesets.id == id
        #vars["ruleset_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db(q).update(**vars)
        _log('compliance.ruleset.change',
             'update properties %(data)s',
             dict(data=str(vars)),
        )
        l = {
          'event': 'comp_rulesets_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_compliance_ruleset().handler(id, props=','.join(["ruleset_name"]+vars.keys()))


