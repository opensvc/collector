
def get_slave(vars):
    slave = vars.get("slave", False)
    if slave in ("true", "True", "T"):
        return True
    return False

#
class rest_get_service_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/services/<svcname>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        svc_responsible(svcname)
        return dict(data=True)

#
class rest_get_service(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display an OpenSVC service properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc?props=svcname,app",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/services/<svcname>",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.services.svc_name == svcname
        if auth_is_node():
            if not common_responsible(svcname=svcname, nodename=auth.user.nodename):
                raise Exception("the node and service must have a common responsible")
        else:
            q = _where(q, 'services', domain_perms(), 'svc_name')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services?props=svc_name,app",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.services.id > 0
        q = _where(q, 'services', domain_perms(), 'svc_name')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_service(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a service properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d svc_wave=3 -o- https://%(collector)s/init/rest/api/services/foo"
        ]

        rest_post_handler.__init__(
          self,
          path="/services/<id>",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        svc_responsible(svcname)

        q = db.services.svc_name == svcname
        svc = db(q).select().first()
        if svc is None:
            raise Exception("Service %s not found"%str(id))

        vars["updated"] = datetime.datetime.now()
        db(q).update(**vars)

        fmt = "Service %(svcname)s change: %(data)s"
        d = dict(svcname=svc.svc_name, data=beautify_change(svc, vars))

        _log('service.change', fmt, d)
        l = {
          'event': 'services_change',
          'data': {'id': svc.id},
        }
        _websocket_send(event_msg(l))

        ret = rest_get_service().handler(svc.svc_name)
        ret["info"] = fmt % d
        return ret

class rest_post_services(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create services",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d svc_name=test -o- https://%(collector)s/init/rest/api/services"
        ]

        rest_post_handler.__init__(
          self,
          path="/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "svc_name" not in vars:
            raise Exception("Key 'svc_name' is mandatory")
        svcname = vars.get("svc_name")

        svc_id = db.services.insert(**vars)

        fmt = "Service %(svcname)s added"
        d = dict(svcname=svcname)

        _log('service.add', fmt, d)
        l = {
          'event': 'services_change',
          'data': {'id': svc_id},
        }
        _websocket_send(event_msg(l))

        return rest_get_service().handler(svcname)

#
class rest_delete_service(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete an OpenSVC service.",
          "- Cascade delete services instances, dashboard entries.",
          "- Log the deletion.",
          "- Send websocket change events on services, services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services/mytestsvc",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services/<svcname>",
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.services.svc_name == svcname
        q = _where(q, 'services', domain_perms(), 'svc_name')
        row = db(q).select(db.services.id, db.services.svc_name).first()
        if row is None:
            raise Exception("service %s does not exist" % svcname)
        svc_responsible(row.svc_name)

        db(q).delete()

        _log('service.delete',
             'delete service %(data)s',
             dict(data=svcname),
            )
        l = {
          'event': 'services_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))

        q = db.svcmon.mon_svcname == svcname
        db(q).delete()
        l = {
          'event': 'svcmon_change',
          'data': {'a': 'b'},
        }
        _websocket_send(event_msg(l))

        q = db.dashboard.dash_svcname == svcname
        db(q).delete()
        l = {
          'event': 'dashboard_change',
          'data': {'a': 'b'},
        }
        _websocket_send(event_msg(l))

        q = db.resmon.svcname == svcname
        db(q).delete()
        l = {
          'event': 'resmon_change',
          'data': {'a': 'b'},
        }
        _websocket_send(event_msg(l))

        return dict(info="service %s deleted" % svcname)

#
class rest_delete_services(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete OpenSVC services.",
          "- Cascade delete services instances and dashboard entries.",
          "- Log the deletion.",
          "- Send websocket change events on services, services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services?filter[]=svc_name=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = None
        if 'svc_name' in vars:
            s = vars["svc_name"]
            q = db.services.svc_name == s
        if 'id' in vars:
            s = vars["id"]
            q = db.services.svc_name == vars["id"]
            s = str(s)
        if q is None:
            raise Exception("svc_name or id key must be specified")
        q = _where(q, 'services', domain_perms(), 'svc_name')
        row = db(q).select(db.services.id, db.services.svc_name).first()
        if row is None:
            raise Exception("service %s does not exist" % s)
        return rest_delete_service().handler(row.svc_name)


#
class rest_get_service_instances(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC service instances.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/service_instances",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/service_instances",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.svcmon.id > 0
        q = _where(q, 'svcmon', domain_perms(), 'mon_nodname')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_instance(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a OpenSVC service instance details.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/service_instances/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/service_instances/<id>",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.svcmon.id == id 
        q = _where(q, 'svcmon', domain_perms(), 'mon_nodname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_service_instance(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete an OpenSVC service instance.",
          "- Cascade the deletion to the dashboard alerts.",
          "- Log the deletion.",
          "- Send websocket change events on the services instances and dashboard table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/service_instances/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/service_instances/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.svcmon.id == id
        q = _where(q, 'svcmon', domain_perms(), 'mon_nodname')
        row = db(q).select(db.svcmon.id, db.svcmon.mon_svcname, db.svcmon.mon_nodname).first()
        if row is None:
            raise Exception("service instance %s does not exist" % str(id))

        # allow anybody to remove a service instance with no service entry in
        # the service
        q2 = db.services.svc_name == row.mon_svcname
        n = db(q2).count()
        if n > 0:
            svc_responsible(row.mon_svcname)

        db(q).delete()

        _log('service_instance.delete',
             'delete service %(svcname)s instance on node %(nodename)s',
             dict(svcname=row.mon_svcname, nodename=row.mon_nodname),
            )
        l = {
          'event': 'svcmon_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))

        q = db.dashboard.dash_svcname == row.mon_svcname
        q = db.dashboard.dash_nodename == row.mon_nodname
        db(q).delete()
        l = {
          'event': 'dashboard_change',
          'data': {'a': 'b'},
        }
        _websocket_send(event_msg(l))

        return dict(info='service %(svcname)s instance on node %(nodename)s deleted' % dict(svcname=row.mon_svcname, nodename=row.mon_nodname))

#
class rest_delete_service_instances(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete OpenSVC service instances.",
          "- Cascade delete dashboard entries.",
          "- Log the deletion.",
          "- Send websocket change events on services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/service_instances?filter[]=mon_svcname=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/service_instances",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = None
        if 'mon_svcname' in vars and 'mon_nodname' in vars:
            q = db.svcmon.mon_svcname == vars["mon_svcname"]
            q &= db.svcmon.mon_nodname == vars["mon_nodname"]
            s = vars["mon_svcname"] + "@" + vars["mon_nodname"]
        if 'id' in vars:
            s = vars["id"]
            q = db.svcmon.id == vars["id"]
        if q is None:
            raise Exception("'mon_svcname+mon_nodname' or 'id' keys must be specified")
        q = _where(q, 'svcmon', domain_perms(), 'mon_nodname')
        svc = db(q).select(db.svcmon.id).first()
        if svc is None:
            raise Exception("service instance %s does not exist" % s)
        return rest_delete_service_instance().handler(svc.id)



#
class rest_get_service_alerts(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service alerts.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/alerts",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/alerts",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.dashboard.dash_svcname == svcname
        q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


#
class rest_get_service_checks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service checks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/checks",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/checks",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.checks_live.chk_svcname == svcname
        q &= _where(None, 'checks_live', domain_perms(), 'chk_svcname')
        self.set_q(q)
        return self.prepare_data(**vars)



#
class rest_get_service_disks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service disks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/disks",
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/disks?props=b_disk_app.disk_svcname,disk_nodename,b_disk_app.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/disks",
          tables=["stor_array", "b_disk_app"],
          left=db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name),
          count_prop="b_disk_app.id",
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.b_disk_app.disk_svcname == svcname
        q &= _where(None, 'b_disk_app', domain_perms(), 'disk_svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service instance status on each of its nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes?props=mon_svcname,mon_availstatus",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/nodes",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.svcmon.mon_svcname == svcname
        q = _where(q, 'svcmon', domain_perms(), 'mon_svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_resources(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display service resources on all nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/resources?props=nodename,rid,res_status",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.resmon.svcname == svcname
        q = _where(q, 'resmon', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_node(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display service instance status on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes/mynode?props=mon_svcname,mon_availstatus",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/services/<svcname>/nodes/<nodename>",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, nodename, **vars):
        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_nodname == nodename
        q = _where(q, 'svcmon', domain_perms(), 'mon_svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_node_resources(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display service instance resources on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes/mynode/resources?props=rid,res_status",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/nodes/<nodename>/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, nodename, **vars):
        q = db.resmon.svcname == svcname
        q &= db.resmon.nodename == nodename
        q = _where(q, 'resmon', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)



#
class rest_get_service_compliance_status(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' last check run on specified service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/status?query=run_status=1",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/compliance/status",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.comp_status.run_svcname == svcname
        q &= _where(q, 'comp_status', domain_perms(), 'run_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_compliance_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attached to the service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/compliance/modulesets",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.comp_modulesets_services.modset_svcname == svcname
        q &= db.comp_modulesets_services.modset_id == db.comp_moduleset.id
        q &= _where(None, 'comp_modulesets_services', domain_perms(), 'modset_svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_compliance_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attached to the service.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/compliance/rulesets",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.comp_rulesets_services.svcname == svcname
        q &= db.comp_rulesets_services.ruleset_id == db.comp_rulesets.id
        q &= _where(None, 'comp_rulesets_services', domain_perms(), 'svcname')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_service_compliance_ruleset(rest_delete_handler):
    def __init__(self):
        params = {
          "slave": {
             "desc": "If set to true, detach from the encapsulated service."
          }
        }
        desc = [
          "Detach a ruleset from a service",
          "Attached rulesets add their variables to the modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/services/mysvc/compliance/rulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services/<svcname>/compliance/rulesets/<id>",
          desc=desc,
          params=params,
          examples=examples
        )

    def handler(self, svcname, rset_id, **vars):
        svc_responsible(svcname)
        slave = get_slave(vars)
        return lib_comp_ruleset_detach_service(svcname, rset_id, slave)

#
class rest_post_service_compliance_ruleset(rest_post_handler):
    def __init__(self):
        params = {
          "slave": {
             "desc": "If set to true, attach to the encapsulated service."
          }
        }
        desc = [
          "Attach a ruleset to a service",
          "Attached rulesets add their variables to the modules execution environment.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/services/mysvc/compliance/rulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/services/<svcname>/compliance/rulesets/<id>",
          desc=desc,
          params=params,
          examples=examples
        )

    def handler(self, svcname, rset_id, **vars):
        svc_responsible(svcname)
        slave = get_slave(vars)
        return lib_comp_ruleset_attach_service(svcname, rset_id, slave)

#
class rest_delete_service_compliance_moduleset(rest_delete_handler):
    def __init__(self):
        params = {
          "slave": {
             "desc": "If set to true, detach from the encapsulated service."
          }
        }
        desc = [
          "Detach a moduleset from a service",
          "Modules of attached modulesets are scheduled for check or fix by the OpenSVC agent.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/services/mysvc/compliance/modulesets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services/<svcname>/compliance/modulesets/<id>",
          desc=desc,
          params=params,
          examples=examples
        )

    def handler(self, svcname, modset_id, **vars):
        svc_responsible(svcname)
        slave = get_slave(vars)
        return lib_comp_moduleset_detach_service(svcname, modset_id, slave)

#
class rest_post_service_compliance_moduleset(rest_post_handler):
    def __init__(self):
        params = {
          "slave": {
             "desc": "If set to true, attach to the encapsulated service."
          }
        }
        desc = [
          "Attach a moduleset to a service",
          "Modules of attached modulesets are scheduled for check or fix by the OpenSVC agent.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/services/mysvc/compliance/modulesets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/services/<svcname>/compliance/modulesets/<id>",
          desc=desc,
          params=params,
          examples=examples
        )

    def handler(self, svcname, modset_id, **vars):
        svc_responsible(svcname)
        slave = get_slave(vars)
        return lib_comp_moduleset_attach_service(svcname, modset_id, slave)

class rest_get_service_compliance_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' check, fixable and fix logs for the service."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/logs"
        ]
        q = db.comp_log.id > 0
        q &= _where(q, 'comp_log', domain_perms(), 'run_nodename')
        rest_get_table_handler.__init__(
          self,
          path="/services/<svcname>/compliance/logs",
          tables=["comp_log"],
          q=q,
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.comp_log.run_svcname == svcname
        q &= _where(q, 'comp_log', domain_perms(), 'run_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

