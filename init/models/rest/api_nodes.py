from gluon.dal import smart_query
import datetime

#
class rest_delete_node_compliance_moduleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a moduleset from a node",
          "Modules of attached modulesets are scheduled for check or fix by the node OpenSVC agent.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/nodes/mynode/compliance/modulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/nodes/<nodename>/compliance/modulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, nodename, modset_id, **vars):
        node_responsible(nodename)
        return lib_comp_moduleset_detach_node(nodename, modset_id)

#
class rest_post_node_compliance_moduleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a moduleset to a node",
          "Modules of attached modulesets are scheduled for check or fix by the node OpenSVC agent.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/nodes/mynode/compliance/modulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/nodes/<nodename>/compliance/modulesets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, nodename, modset_id, **vars):
        node_responsible(nodename)
        return lib_comp_moduleset_attach_node(nodename, modset_id)

#
class rest_get_node_compliance_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attached to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/compliance/rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/compliance/rulesets",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.comp_rulesets_nodes.nodename == nodename
        q &= db.comp_rulesets_nodes.ruleset_id == db.comp_rulesets.id
        q &= _where(None, 'comp_rulesets_nodes', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_compliance_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attached to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/compliance/modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/compliance/modulesets",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.comp_node_moduleset.modset_node == nodename
        q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
        q &= _where(None, 'comp_node_moduleset', domain_perms(), 'modset_node')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_interfaces(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node network interfaces.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/interfaces?props=intf,mac",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/interfaces",
          tables=["node_ip"],
          props_blacklist=["type", "addr", "mask"],
          groupby=db.node_ip.intf,
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.node_ip.nodename == nodename
        q &= _where(None, 'node_ip', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_ips(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node ips.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/ips?props=prio,net_network,net_netmask",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/ips",
          tables=["v_nodenetworks"],
          props_blacklist=db.nodes.fields,
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.v_nodenetworks.nodename == nodename
        q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_disks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node disks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/disks?props=b_disk_app.disk_nodename,b_disk_app.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/disks",
          tables=["b_disk_app", "stor_array"],
          left=db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name),
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.b_disk_app.disk_nodename == nodename
        l = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
        q &= _where(None, 'b_disk_app', domain_perms(), 'disk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_checks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node checks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/checks",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/checks",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.checks_live.chk_nodename == nodename
        q &= _where(None, 'checks_live', domain_perms(), 'chk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)




#
class rest_get_node_hbas(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node storage host bus adapters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/hbas",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/hbas",
          tables=["node_hba"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.node_hba.nodename == nodename
        q &= _where(None, 'node_hba', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List node OpenSVC services.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/services",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/services",
          tables=["svcmon", "services"],
          left=db.services.on(db.svcmon.mon_svcname == db.services.svc_name),
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.svcmon.mon_nodname == nodename
        q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_service(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the specified service on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/services",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/nodes/<nodename>/services/<svcname>",
          tables=["svcmon", "services"],
          left=db.services.on(db.svcmon.mon_svcname == db.services.svc_name),
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, svcname, **vars):
        q = db.svcmon.mon_nodname == nodename
        q = db.svcmon.mon_svcname == svcname
        q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_alerts(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node alerts.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/alerts?props=dash_nodename,dash_type",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/alerts",
          tables=["dashboard"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.dashboard.dash_nodename == nodename
        q &= _where(None, 'dashboard', domain_perms(), 'dash_nodename')
        self.set_q(q)
        data = self.prepare_data(**vars)
        data["data"] = mangle_alerts(data["data"])
        return data


#
class rest_get_node(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display all node properties.",
          "Display selected node properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode?props=nodename,loc_city",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/nodes/<nodename>",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.nodes.nodename == nodename
        q &= _where(None, 'nodes', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
#
class rest_get_nodes(rest_get_table_handler):
    def __init__(self):
        params = {
          "fset_id": {
             "desc": "Filter the list using the filterset identified by fset_id."
          }
        }
        desc = [
          "List all node names and their selected properties.",
          "List node names and their selected properties for nodes matching a specified filterset id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes?props=nodename,loc_city&fset_id=10",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes",
          tables=["nodes"],
          params=params,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.nodes.id > 0
        q = _where(q, 'nodes', domain_perms(), 'nodename')
        fset_id = vars.get("fset_id")
        if fset_id:
            q = apply_filters(q, node_field=db.nodes.nodename, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_node(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a set of node properties.",
          "The user must be responsible for the node.",
          "The user must be in the NodeManager privilege group.",
          "The updated timestamp is automatically updated.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d loc_city="Zanzibar" -d project="ERP" https://%(collector)s/init/rest/api/nodes/mynode""",
        ]
        rest_post_handler.__init__(
          self,
          path="/nodes/<nodename>",
          tables=["nodes"],
          desc=desc,
          examples=examples
        )

    def handler(self, nodename, **vars):
        check_privilege("NodeManager")
        node_responsible(nodename)
        q = db.nodes.nodename == nodename
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db(q).update(**vars)
        _log('rest.nodes.update',
             'update properties %(data)s',
             dict(data=str(vars)),
             nodename=nodename)
        l = {
          'event': 'nodes_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_node().handler(nodename, props=','.join(["nodename","updated"]+vars.keys()))


#
class rest_post_nodes(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a new node",
          "If ``team_responsible``:green is not specified, default to user's primary group",
        ]
        examples = [
          """# curl -u %(email)s -o- -d nodename=mynode -d loc_city="Zanzibar" -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/nodes""",
        ]
        rest_post_handler.__init__(
          self,
          path="/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("NodeManager")
        if 'nodename' not in vars:
            raise Exception("the nodename property must be set in the POST data")
        nodename = vars['nodename']
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "team_responsible" not in vars:
            vars["team_responsible"] = user_primary_group()
        db.nodes.insert(**vars)
        _log('rest.nodes.create',
             'create properties %(data)s',
             dict(data=str(vars)),
             nodename=nodename)
        l = {
          'event': 'nodes_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_node().handler(nodename)


#
class rest_delete_node(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a node.",
          "The user must be responsible for the node.",
          "The user must be in the NodeManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/nodes/mynode",
        ]
        rest_delete_handler.__init__(
          self,
          path="/nodes/<nodename>",
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        node_responsible(nodename)
        check_privilege("NodeManager")
        q = db.nodes.nodename == nodename
        db(q).delete()
        _log('rest.nodes.delete',
             '',
             dict(),
             nodename=nodename)
        l = {
          'event': 'nodes_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Node %s deleted" % nodename)

#
class rest_get_node_compliance_status(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' last check run on specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/compliance/status?query=run_status=1",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<nodename>/compliance/status",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, nodename, **vars):
        q = db.comp_status.run_nodename == nodename
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


