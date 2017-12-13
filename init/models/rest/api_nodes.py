import datetime
from applications.init.modules import timeseries

#
class rest_delete_node_compliance_ruleset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a ruleset from a node",
          "Attached rulesets add their variables to the modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/nodes/mynode/compliance/rulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/nodes/<id>/compliance/rulesets/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, rset_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        return lib_comp_ruleset_detach_node(node_id, rset_id)

#
class rest_post_node_compliance_ruleset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a ruleset to a node",
          "Attached rulesets add their variables to the modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/nodes/mynode/compliance/rulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/nodes/<id>/compliance/rulesets/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, rset_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        return lib_comp_ruleset_attach_node(node_id, rset_id)

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
          path="/nodes/<id>/compliance/modulesets/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, modset_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        return lib_comp_moduleset_detach_node(node_id, modset_id)

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
          path="/nodes/<id>/compliance/modulesets/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, modset_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        return lib_comp_moduleset_attach_node(node_id, modset_id)

#
class rest_get_node_compliance_candidate_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attachable to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/compliance/candidate_rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/compliance/candidate_rulesets",
          tables=["comp_rulesets"],
          groupby=db.comp_rulesets.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)

        q = db.comp_rulesets_nodes.node_id == node_id
        attached = [r.ruleset_id for r in db(q).select(db.comp_rulesets_nodes.ruleset_id)]

        q = db.comp_rulesets.ruleset_type == 'explicit'
        q &= db.comp_rulesets.ruleset_public == True
        q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
        q &= db.nodes.node_id == node_id
        q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
        q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
        q &= ~db.comp_rulesets.id.belongs(attached)
        q = q_filter(q, node_field=db.comp_rulesets_nodes.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_compliance_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attached to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/compliance/rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/compliance/rulesets",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.comp_rulesets_nodes.node_id == node_id
        q &= db.comp_rulesets_nodes.ruleset_id == db.comp_rulesets.id
        q = q_filter(q, node_field=db.comp_rulesets_nodes.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_compliance_candidate_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attachable to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/compliance/candidate_modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/compliance/candidate_modulesets",
          tables=["comp_moduleset"],
          groupby=db.comp_moduleset.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)

        q = db.comp_node_moduleset.node_id == node_id
        attached = [r.modset_id for r in db(q).select(db.comp_node_moduleset.modset_id)]

        q = db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
        q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
        q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
        q &= db.nodes.node_id == node_id
        q &= ~db.comp_moduleset.id.belongs(attached)
        q = q_filter(q, node_field=db.comp_node_moduleset.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_compliance_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attached to the node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/compliance/modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/compliance/modulesets",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.comp_node_moduleset.node_id == node_id
        q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
        q = q_filter(q, node_field=db.comp_node_moduleset.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_interfaces(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node network interfaces.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/interfaces?props=intf,mac",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/interfaces",
          tables=["node_ip"],
          props_blacklist=["type", "addr", "mask"],
          groupby=db.node_ip.intf,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.node_ip.node_id == node_id
        q = q_filter(q, node_field=db.node_ip.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_ips(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node ips.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/ips?props=prio,net_network,net_netmask",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/ips",
          tables=["v_nodenetworks"],
          props_blacklist=db.nodes.fields,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.v_nodenetworks.node_id == node_id
        q = q_filter(q, app_field=db.v_nodenetworks.app)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_disks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node disks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/mynode/disks?props=svcdisks.node_id,svcdisks.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/disks",
          tables=["svcdisks", "diskinfo", "stor_array"],
          left=(db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id), db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)),
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        node_id = get_node_id(id)
        q = db.svcdisks.node_id == node_id
        q = q_filter(q, node_field=db.svcdisks.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_checks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node checks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/checks",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/checks",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.checks_live.node_id == node_id
        q = q_filter(q, node_field=db.checks_live.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)




#
class rest_get_node_targets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List the target ports visible through the node storage host bus adapters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/targets",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/targets",
          tables=["stor_zone", "stor_array"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.stor_zone.node_id == node_id
        q &= db.stor_zone.tgt_id == db.stor_array_tgtid.array_tgtid
        q &= db.stor_array_tgtid.array_id == db.stor_array.id
        q = q_filter(q, node_field=db.stor_zone.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_hbas(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node storage host bus adapters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/hbas",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/hbas",
          tables=["node_hba"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.node_hba.node_id == node_id
        q = q_filter(q, node_field=db.node_hba.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List node OpenSVC services.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/services",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/services",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.svcmon.node_id == node_id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_service(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display the specified service on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/services/2",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/nodes/<id>/services/<id>",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, svc_id, **vars):
        node_id = get_node_id(node_id)
        svc_id = get_svc_id(svc_id)
        q = db.svcmon.node_id == node_id
        q = db.svcmon.svc_id == svc_id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_node_alerts(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a node alerts.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/alerts?props=dash_type",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/alerts",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.dashboard.node_id == node_id
        f1 = q_filter(svc_field=db.dashboard.svc_id)
        f2 = q_filter(node_field=db.dashboard.node_id)
        q &= (f1|f2)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


#
class rest_get_node(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display all node properties.",
          "Display selected node properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a?props=nodename,loc_city",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/nodes/<id>",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        q = db.nodes.node_id == get_node_id(node_id)
        q = q_filter(q, app_field=db.nodes.app)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_node_uuid(rest_get_line_handler):
    def __init__(self):
        desc = [
          "- Display node uuid.",
          "- Only node responsibles and managers are allowed to see this information.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/uuid",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/nodes/<id>/uuid",
          tables=["auth_node"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        q = db.auth_node.node_id == node_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_node_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/nodes/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        return dict(data=True)

 #
class rest_get_node_root_password(rest_get_handler):
    def __init__(self):
        desc = [
          "- Display node root password set by the 'rotate root password' opensvc agent action.",
          "- Only node responsibles and managers are allowed to see this information.",
          "- The password retrieval is logged for audit.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/5c977246-0562-11e6-8c70-7e9e6cf13c8a/root_password",
        ]
        rest_get_handler.__init__(
          self,
          path="/nodes/<id>/root_password",
          tables=["auth_node"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)

        config = local_import('config', reload=True)
        try:
            salt = config.aes_salt
        except Exception as e:
            salt = "tlas"

        node = db(db.auth_node.node_id==node_id).select().first()
        if node is None:
            raise Exception(T("node not found"))
        node_uuid = node.uuid
        sql = """select aes_decrypt(pw, "%(sec)s") from node_pw where
                 node_id="%(node_id)s"
              """ % dict(node_id=node_id, sec=node_uuid+salt)
        pwl = db.executesql(sql)
        if len(pwl) == 0:
            raise Exception(T("This node has not reported its root password (opensvc agent feature not activated or agent too old)"))

        _log('password.retrieve',
             'retrieved root password of node %(nodename)s',
             dict(nodename=get_nodename(node_id)),
             node_id=node_id)

        return dict(data=pwl[0][0])

#
class rest_get_nodes_hardwares(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List all nodes pci and mem hardware.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes_hardware?props=nodes.nodename,hw_class",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes_hardware",
          tables=["node_hw"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(node_field=db.node_hw.node_id)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, node_field=db.node_hw.node_id, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_node_hardwares(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List node pci and mem hardware.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/node1/hardware?props=hw_class",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/hardware",
          tables=["node_hw"],
          desc=desc,
          examples=examples,
        )

    def handler(self, node_id, **vars):
        node_id = get_node_id(node_id)
        q = db.node_hw.node_id == node_id
        q = q_filter(node_field=db.node_hw.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List all node names and their selected properties.",
          "List node names and their selected properties for nodes matching a specified filterset id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes?props=nodename,loc_city",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(app_field=db.nodes.app)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, node_field=db.nodes.node_id, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_node(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete an OpenSVC node.",
          "- The user must be responsible for the node.",
          "- The user must be in the NodeManager privilege group.",
          "- Cascade delete services instances, dashboard, checks, packages and patches entries.",
          "- Log the deletion.",
          "- Send websocket change events on nodes, services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/nodes/mynode",
        ]
        rest_delete_handler.__init__(
          self,
          path="/nodes/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, **vars):
        check_privilege("NodeManager")
        node_id = get_node_id(node_id)

        q = db.nodes.node_id == node_id
        node_responsible(node_id=node_id)

        q = db.nodes.node_id == node_id
        db(q).delete()

        nodename = get_nodename(node_id)

        fmt = 'delete node %(data)s'
        d = dict(data=nodename)
        _log('node.delete', fmt, d, node_id=node_id)
        ws_send('nodes_change', {'node_id': node_id})
        table_modified("nodes")

        q = db.svcmon.node_id == node_id
        db(q).delete()
        ws_send('svcmon_change', {'node_id': node_id})
        table_modified("svcmon")

        q = db.dashboard.node_id == node_id
        db(q).delete()
        ws_send('dashboard_change', {'node_id': node_id})
        table_modified("dashboard")

        q = db.checks_live.node_id == node_id
        db(q).delete()
        ws_send('checks_change', {'node_id': node_id})
        table_modified("checks_live")

        q = db.packages.node_id == node_id
        db(q).delete()
        ws_send('packages_change', {'node_id': node_id})
        table_modified("packages")

        q = db.patches.node_id == node_id
        db(q).delete()
        ws_send('patches_change', {'node_id': node_id})
        table_modified("patches")

        q = db.node_tags.node_id == node_id
        db(q).delete()
        ws_send('node_tags_change', {'node_id': node_id})
        table_modified("node_tags")

        q = db.node_ip.node_id == node_id
        db(q).delete()
        ws_send('node_ip_change', {'node_id': node_id})
        table_modified("node_ip")

        q = db.node_hba.node_id == node_id
        db(q).delete()
        ws_send('node_hba_change', {'node_id': node_id})
        table_modified("node_hba")

        q = db.stor_zone.node_id == node_id
        db(q).delete()
        ws_send('stor_zone_change', {'node_id': node_id})
        table_modified("stor_zone")

        q = db.auth_node.node_id == node_id
        db(q).delete()
        ws_send('auth_node', {'node_id': node_id})
        table_modified("auth_node")

        timeseries.wsp_delete("nodes", node_id)

        return dict(info=fmt%d)


#
class rest_delete_nodes(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete OpenSVC nodes.",
          "- Cascade delete services instances, dashboard, checks, packages and patches entries.",
          "- Log the deletion.",
          "- Send websocket change events on nodes, services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/nodes?filter[]=nodename=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/nodes",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if 'node_id' not in vars:
            raise Exception("The 'node_id' key must be specified")
        node_id = vars["node_id"]
        return rest_delete_node().handler(node_id)


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
          """# curl -u %(email)s -o- -d loc_city="Zanzibar" -d app="ERP" https://%(collector)s/init/rest/api/nodes/mynode""",
        ]
        rest_post_handler.__init__(
          self,
          path="/nodes/<id>",
          tables=["nodes"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, node_id, **vars):
        check_privilege("NodeManager")
        node_id = get_node_id(node_id)
        node_responsible(node_id=node_id)
        q = db.nodes.node_id == node_id
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # a node can not set its team responsible, for it not to gain access to
        # rulesets and safe files it should not see
        if "team_responsible" in vars and auth_is_node():
            del(vars["team_responsible"])

        row = db(q).select().first()
        if row is None:
            raise Exception("node %s does not exist" % node_id)

        if "node_id" in vars:
            del(vars["node_id"])

        vars["updated"] = datetime.datetime.now()
        if "app" in vars and (
             vars["app"] == "" or \
             vars["app"] is None or \
             not common_responsible(app=vars["app"], user_id=auth.user_id)
           ):
            vars["app"] = user_default_app()

        db(q).update(**vars)
        _log('node.change',
             'update properties %(data)s',
             dict(data=beautify_change(row, vars)),
             node_id=node_id)
        ws_send('nodes_change', {'node_id': node_id})
        if "nodename" in vars:
            # update the nodename in auth_node too, so the node does not have
            # to register again on hostname change
            q = db.auth_node.node_id == node_id
            db(q).update(nodename=vars["nodename"], updated=vars["updated"])
        enqueue_async_task("node_dashboard_updates", [node_id])
        return rest_get_node().handler(node_id, props=','.join(["node_id", "nodename", "app", "updated"]+vars.keys()))


#
class rest_post_nodes(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_nodes()
        self.update_one_handler = rest_post_node()
        self.update_one_param = "id"
        desc = [
          "Create a new node",
          "Update nodes matching the specified query.",
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
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        if 'nodename' not in vars and 'node_id' not in vars:
            raise Exception("The 'nodename' or 'id' property must be set in the POST data")

        try:
            _vars = {}
            _vars.update(vars)
            if 'node_id' in vars:
                node_id = vars['node_id']
                del(_vars["node_id"])
            elif 'nodename' in vars:
                node_id = vars['nodename']
                del(_vars["nodename"])
            return rest_post_node().handler(node_id, **_vars)
        except:
            pass

        # create node code path
        check_privilege("NodeManager")
        if 'nodename' not in vars:
            raise Exception("The 'nodename' property must be set in the POST data: %s" % vars)
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "team_responsible" not in vars:
            vars["team_responsible"] = user_primary_group()

        # a node can not set its team responsible, for it not to gain access to
        # rulesets and safe files it should not see
        if "team_responsible" in vars and auth_is_node():
            del(vars["team_responsible"])

        # choose a default app for new nodes
        if "app" not in vars or \
           vars["app"] == "" or \
           vars["app"] is None or \
           not common_responsible(app=vars["app"], user_id=auth.user_id):
            vars["app"] = user_default_app()

        node_id = get_new_node_id()
        vars["node_id"] = node_id

        db.nodes.insert(**vars)
        _log('node.add',
             'create properties %(data)s',
             dict(data=beautify_data(vars)),
             node_id=node_id)
        ws_send('nodes_change', {'node_id': node_id})
        enqueue_async_task("node_dashboard_updates", [node_id])
        return rest_get_node().handler(node_id)


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
          path="/nodes/<id>/compliance/status",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        node_id = get_node_id(id)
        q = db.comp_status.node_id == node_id
        q = q_filter(q, node_field=db.comp_status.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_node_compliance_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' check, fixable and fix logs for the node."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/nodes/clementine/compliance/logs"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/nodes/<id>/compliance/logs",
          tables=["comp_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        node_id = get_node_id(id)
        q = db.comp_log.node_id == node_id
        q = q_filter(q, node_field=db.comp_log.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

