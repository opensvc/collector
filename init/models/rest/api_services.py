
def get_slave(vars):
    slave = vars.get("slave", False)
    return convert_bool(slave)

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
          path="/services/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        svc_responsible(svc_id)
        return dict(data=True)

#
class rest_get_service(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display an OpenSVC service properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc?props=svcname,svc_app",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/services/<id>",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.services.svc_id == svc_id
        if auth_is_node():
            if not common_responsible(svc_id=svc_id, node_id=auth.user.node_id):
                raise HTTP(403, "the node and service must have a common responsible")
        else:
            q = q_filter(q, app_field=db.services.svc_app)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services?props=svcname,svc_app",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services",
          tables=["services"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(app_field=db.services.svc_app)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, svc_field=db.services.svc_id, fset_id=fset_id)
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
          replication=["relay", "local"],
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        svc_responsible(svc_id)

        q = db.services.svc_id == svc_id
        svc = db(q).select().first()
        if svc is None:
            raise HTTP(404, "Service %s not found"%str(id))

        vars["updated"] = datetime.datetime.now()
        if "svc_app" in vars and (
             vars["svc_app"] == "" or \
             vars["svc_app"] is None or \
             not common_responsible(app=vars["svc_app"], user_id=auth.user_id)
           ):
            vars["svc_app"] = user_default_app()

        db(q).update(**vars)

        fmt = "Service %(svc_id)s change: %(data)s"
        d = dict(svc_id=svc.svc_id, data=beautify_change(svc, vars))

        _log('service.change', fmt, d)
        ws_send('services_change', {'id': svc.id})

        ret = rest_get_service().handler(svc.svc_id)
        ret["info"] = fmt % d
        return ret

class rest_post_services(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create services",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d svcname=test -d cluster_id=xxx -o- https://%(collector)s/init/rest/api/services"
        ]

        rest_post_handler.__init__(
          self,
          path="/services",
          tables=["services"],
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        svc_id = vars.get("svc_id")
        svcname = vars.get("svcname")
        if svc_id is None and svcname is None:
            raise HTTP(400, "Either the 'svc_id' or 'svcname' key is mandatory")
        try:
            if svc_id is None:
                svc_id = get_svc_id(svcname)
            q = db.services.svc_id == svc_id
            svc = db(q).select().first()
            if svc is not None:
                return rest_post_service().handler(svc_id, **vars)
        except HTTP as exc:
            if exc.status == 404:
                pass
            else:
                raise

        cluster_id = vars.get("cluster_id")
        if cluster_id is None or svcname is None:
            raise HTTP(400, "Either the 'svcname' or 'cluster_id' key is mandatory when service need to be created.")

        # TODO: verify if user is allowed for cluster_id
        svc_id = object_id_find_or_create(svcname, cluster_id)
        vars["svc_id"] = svc_id
        vars["updated"] = datetime.datetime.now()
        if "svc_app" not in vars or \
           vars["svc_app"] == "" or \
           vars["svc_app"] is None or \
           not common_responsible(app=vars["svc_app"], user_id=auth.user_id):
            vars["svc_app"] = user_default_app()

        db.services.insert(**vars)

        fmt = "Service %(data)s added"
        d = dict(data=beautify_data(vars))

        _log('service.add', fmt, d)
        ws_send('services_change', {'id': svc_id})

        ret = rest_get_service().handler(svc_id)
        ret["info"] = fmt % d
        return ret

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
          path="/services/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.services.svc_id == svc_id
        q = q_filter(q, app_field=db.services.svc_app)
        row = db(q).select(db.services.svc_id).first()
        if row is None:
            raise HTTP(404, "service %s does not exist" % svc_id)
        svc_responsible(row.svc_id)
        svcname = get_svcname(svc_id)

        _log('service.delete', 'delete service %(data)s', dict(data=svcname))

        for t in ["services", "drpservices", "checks_settings", "comp_rulesets_services", "comp_modulesets_services", "action_queue", "svc_tags", "svcmon", "dashboard", "svcdisks", "resmon", "checks_live", "comp_status", "action_queue", "resinfo", "saves"]:
            delete_svc_from_table(t, svc_id)

        for t in ["svcactions", "svcmon_log", "resmon_log", "svcmon_log_ack", "comp_log", "comp_log_daily", "log", "form_output_results", "svcmon_log_last", "resmon_log_last", "dashboard_events"]:
            enqueue_async_task("delete_svc_from_table", [t, svc_id])

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
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services?filter[]=svcname=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        q = None
        if 'svc_id' in vars:
            s = vars["svc_id"]
            q = db.services.svc_id == s
        if q is None:
            raise HTTP(400, "The 'svc_id' key must be specified")
        q = q_filter(q, app_field=db.services.svc_app)
        row = db(q).select(db.services.svc_id).first()
        if row is None:
            raise HTTP(404, "service %s does not exist" % s)
        return rest_delete_service().handler(row.svc_id)


#
class rest_get_services_instances(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List OpenSVC services instances.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_instances",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services_instances",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
          allow_fset_id=True,
        )

    def handler(self, **vars):
        q = q_filter(svc_field=db.svcmon.svc_id)
        fset_id = vars.get("fset-id")
        if fset_id:
            q = apply_filters_id(q, svc_field=db.svcmon.svc_id, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_instance(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a OpenSVC service instance details.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services_instances/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/services_instances/<id>",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.svcmon.svc_id == svc_id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
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
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services_instances/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services_instances/<id>",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, id, **vars):
        q = db.svcmon.id == id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
        row = db(q).select(db.svcmon.id, db.svcmon.svc_id, db.svcmon.node_id).first()
        if row is None:
            raise HTTP(404, "service instance %s does not exist" % str(id))

        nodename = get_nodename(row.node_id)
        svcname = get_svcname(row.svc_id)

        # allow anybody to remove a service instance with no service entry in
        # the services table
        q2 = db.services.svc_id == row.svc_id
        n = db(q2).count()
        if n > 0:
            svc_responsible(row.svc_id)

        db(q).delete()

        fmt = 'delete service %(svcname)s instance on node %(nodename)s'
        d = dict(svcname=svcname, nodename=nodename)

        _log('service_instance.delete', fmt, d, node_id=row.node_id, svc_id=row.svc_id)
        ws_send('svcmon_change', {'id': row.id})

        q = db.dashboard.svc_id == row.svc_id
        q &= db.dashboard.node_id == row.node_id
        db(q).delete()
        ws_send('dashboard_change', {'svc_id': row.svc_id, 'node_id': row.node_id})

        q = db.resmon.svc_id == row.svc_id
        q &= db.resmon.node_id == row.node_id
        db(q).delete()
        ws_send('resmon_change', {'svc_id': row.svc_id, 'node_id': row.node_id})

        q = db.resinfo.svc_id == row.svc_id
        q &= db.resinfo.node_id == row.node_id
        db(q).delete()
        ws_send('resinfo_change', {'svc_id': row.svc_id, 'node_id': row.node_id})

        q = db.checks_live.svc_id == row.svc_id
        q &= db.checks_live.node_id == row.node_id
        db(q).delete()
        ws_send('checks_live_change', {'svc_id': row.svc_id, 'node_id': row.node_id})

        return dict(info=fmt%d)

#
class rest_delete_services_instances(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete OpenSVC service instances.",
          "- Cascade delete dashboard entries.",
          "- Log the deletion.",
          "- Send websocket change events on services instances and dashboard tables.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/services_instances?filter[]=svc_id=52%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/services_instances",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, **vars):
        q = None
        if 'svc_id' in vars and 'node_id' in vars:
            q = db.svcmon.svc_id == vars["svc_id"]
            q &= db.svcmon.node_id == vars["node_id"]
            s = get_svcname(vars["svc_id"]) + " @ " + get_nodename(vars["node_id"])
        if 'id' in vars:
            s = vars["id"]
            q = db.svcmon.id == vars["id"]
        if q is None:
            raise HTTP(400, "'svc_id+node_id' or 'id' keys must be specified")
        q = q_filter(q, svc_field=db.svcmon.svc_id)
        svc = db(q).select(db.svcmon.id).first()
        if svc is None:
            raise HTTP(404, "service instance %s does not exist" % s)
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
          path="/services/<id>/alerts",
          tables=["dashboard"],
          vprops={"alert": ["dash_fmt", "dash_dict"]},
          vprops_fn=mangle_alerts,
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.dashboard.svc_id == svc_id
        q = q_filter(q, svc_field=db.dashboard.svc_id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


#
class rest_get_service_resinfos(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service resources info key/value pairs.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/resinfo",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/resinfo",
          tables=["resinfo"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.resinfo.svc_id == svc_id
        q = q_filter(q, svc_field=db.resinfo.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

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
          path="/services/<id>/checks",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.checks_live.svc_id == svc_id
        q = q_filter(q, svc_field=db.checks_live.svc_id)
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
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/disks?props=svcdisks.svc_id,svcdisks.node_id,svcdisks.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/disks",
          tables=["svcdisks", "diskinfo", "stor_array"],
          left=(db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id), db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)),
          count_prop="svcdisks.id",
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svcdisks.svc_id == svc_id
        q = q_filter(q, svc_field=db.svcdisks.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List an OpenSVC service instance status on each of its nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes?props=svc_id,mon_availstatus",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/nodes",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        svc_id = get_svc_id(id)
        q = db.svcmon.svc_id == svc_id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_resources(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display service resources on all nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/resources?props=node_id,rid,res_status",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.resmon.svc_id == svc_id
        q = q_filter(q, svc_field=db.resmon.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_resources_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display a service resources state changes on all nodes.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/resources_logs",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/resources_logs",
          tables=["v_resmon_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.v_resmon_log.svc_id == svc_id
        q = q_filter(q, svc_field=db.v_resmon_log.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_node(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display service instance status on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes/mynode?props=svc_id,mon_availstatus",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/services/<id>/nodes/<id>",
          tables=["svcmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, node_id, **vars):
        svc_id = get_svc_id(svc_id)
        node_id = get_node_id(node_id)
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        q = q_filter(q, svc_field=db.svcmon.svc_id)
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
          path="/services/<id>/nodes/<id>/resources",
          tables=["resmon"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, node_id, **vars):
        node_id = get_node_id(node_id)
        svc_id = get_svc_id(svc_id)
        q = db.resmon.svc_id == svc_id
        q &= db.resmon.node_id == node_id
        q = q_filter(q, svc_field=db.resmon.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_node_resources_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display a service instance resources state changes on the specified node.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/nodes/mynode/resources_logs",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/nodes/<id>/resources_logs",
          tables=["v_resmon_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, node_id, **vars):
        node_id = get_node_id(node_id)
        svc_id = get_svc_id(svc_id)
        q = db.v_resmon_log.svc_id == svc_id
        q &= db.v_resmon_log.node_id == node_id
        q = q_filter(q, svc_field=db.v_resmon_log.svc_id)
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
          path="/services/<id>/compliance/status",
          tables=["comp_status"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.comp_status.svc_id == svc_id
        q = q_filter(q, svc_field=db.comp_status.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_compliance_candidate_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attachable to the service.",
        ]
        params = {
          "slave": {
             "desc": "If set to true, list attachable to the encapsulated service."
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/candidate_modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/compliance/candidate_modulesets",
          tables=["comp_moduleset"],
          groupby=db.comp_moduleset.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)

        if "slave" in vars:
            slave = convert_bool(vars.get("slave"))
            del(vars["slave"])
        else:
            slave = False
        q = db.comp_modulesets_services.svc_id == svc_id
        q &= db.comp_modulesets_services.slave == slave
        attached = [r.modset_id for r in db(q).select(db.comp_modulesets_services.modset_id)]

        q = db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
        q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
        q &= (db.apps_responsibles.group_id == db.auth_group.id)|(db.auth_group.role=="Everybody")
        q &= db.services.svc_id == svc_id
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        q &= ~db.comp_moduleset.id.belongs(attached)
        q = q_filter(q, svc_field=db.comp_modulesets_services.svc_id)

        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_compliance_modulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modulesets attached to the service.",
        ]
        params = {
          "slave": {
             "desc": "If set to true, list attachable to the encapsulated service."
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/modulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/compliance/modulesets",
          tables=["comp_moduleset"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        if "slave" in vars:
            slave = convert_bool(vars.get("slave"))
            del(vars["slave"])
        else:
            slave = False
        svc_id = get_svc_id(svc_id)
        q = db.comp_modulesets_services.svc_id == svc_id
        q &= db.comp_modulesets_services.slave == slave
        q &= db.comp_modulesets_services.modset_id == db.comp_moduleset.id
        q = q_filter(q, svc_field=db.comp_modulesets_services.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_compliance_candidate_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attachable to the service.",
        ]
        params = {
          "slave": {
             "desc": "If set to true, list attachable to the encapsulated service."
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/candidate_rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/compliance/candidate_rulesets",
          tables=["comp_rulesets"],
          groupby=db.comp_rulesets.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)

        if "slave" in vars:
            slave = convert_bool(vars.get("slave"))
            del(vars["slave"])
        else:
            slave = False
        q = db.comp_rulesets_services.svc_id == svc_id
        q &= db.comp_rulesets_services.slave == slave
        attached = [r.ruleset_id for r in db(q).select(db.comp_rulesets_services.ruleset_id)]

        q = db.comp_rulesets.ruleset_type == 'explicit'
        q &= db.comp_rulesets.ruleset_public == True
        q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
        q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
        q &= (db.apps_responsibles.group_id == db.auth_group.id)|(db.auth_group.role=="Everybody")
        q &= db.services.svc_id == svc_id
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        q &= ~db.comp_rulesets.id.belongs(attached)
        q = q_filter(q, svc_field=db.comp_rulesets_services.svc_id)

        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_service_compliance_rulesets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance rulesets attached to the service.",
        ]
        params = {
          "slave": {
             "desc": "If set to true, list attachable to the encapsulated service."
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/rulesets",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/compliance/rulesets",
          tables=["comp_rulesets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        if "slave" in vars:
            slave = convert_bool(vars.get("slave"))
            del(vars["slave"])
        else:
            slave = False
        svc_id = get_svc_id(svc_id)
        q = db.comp_rulesets_services.svc_id == svc_id
        q &= db.comp_rulesets_services.slave == slave
        q &= db.comp_rulesets_services.ruleset_id == db.comp_rulesets.id
        q = q_filter(q, svc_field=db.comp_rulesets_services.svc_id)
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
          path="/services/<id>/compliance/rulesets/<id>",
          desc=desc,
          params=params,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, svc_id, rset_id, **vars):
        svc_id = get_svc_id(svc_id)
        svc_responsible(svc_id)
        slave = get_slave(vars)
        return lib_comp_ruleset_detach_service(svc_id, rset_id, slave)

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
          path="/services/<id>/compliance/rulesets/<id>",
          desc=desc,
          params=params,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, svc_id, rset_id, **vars):
        svc_id = get_svc_id(svc_id)
        svc_responsible(svc_id)
        slave = get_slave(vars)
        return lib_comp_ruleset_attach_service(svc_id, rset_id, slave)

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
          path="/services/<id>/compliance/modulesets/<id>",
          desc=desc,
          params=params,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, svc_id, modset_id, **vars):
        svc_id = get_svc_id(svc_id)
        svc_responsible(svc_id)
        slave = get_slave(vars)
        return lib_comp_moduleset_detach_service(svc_id, modset_id, slave)

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
          path="/services/<id>/compliance/modulesets/<id>",
          desc=desc,
          params=params,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, svc_id, modset_id, **vars):
        svc_id = get_svc_id(svc_id)
        svc_responsible(svc_id)
        slave = get_slave(vars)
        return lib_comp_moduleset_attach_service(svc_id, modset_id, slave)

class rest_get_service_compliance_logs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List compliance modules' check, fixable and fix logs for the service."
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/mysvc/compliance/logs"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/compliance/logs",
          tables=["comp_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.comp_log.svc_id == svc_id
        q = q_filter(q, svc_field=db.comp_log.svc_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_put_service_orchestration_queue(rest_put_handler):
    def __init__(self):
        desc = [
          "Enqueue an orchestrated action that will be executed by opensvc agents on *any* service instances.",
          "The user must be responsible for the target node or service.",
          "The action is logged in the collector's log.",
        ]
        data = """
- <property>=<value> pairs.
- **svc_id**
. The service targeted by the action. The action is run using the
  svcmgr opensvc agent command on the node specified by **node_id**.
- **action**
. The opensvc agent action to execute.

Each action has specific property requirements:

- ``start``:green requires **svc_id**
- ``stop``:green requires **svc_id**
- ``restart``:green requires **svc_id**
- ``freeze``:green requires **svc_id**
- ``thaw``:green requires **svc_id**
"""
        examples = [
          "# curl -u %(email)s -o- -X PUT -d action=start https://%(collector)s/init/rest/api/services/test/queue_orchestration",
        ]

        rest_put_handler.__init__(
          self,
          path="/services/<id>/queue_orchestration",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, svc_id, **vars):
        data = []
        svc_id = get_svc_id(svc_id)
        vars["svc_id"] = svc_id
        if "node_id" in vars:
            del vars["node_id"]
        action_id = json_action_one(vars)
        if action_id > 0:
            data += rest_get_action_queue_one().handler(action_id)["data"]
            action_q_event()
        return dict(data=data)

#
class rest_put_service_action_queue(rest_put_handler):
    def __init__(self):
        desc = [
          "Enqueue an action that will be executed by opensvc agents on *all* service instances.",
          "The user must be responsible for the target node or service.",
          "The action is logged in the collector's log.",
        ]
        data = """
- <property>=<value> pairs.
- **svc_id**
. The service targeted by the action. The action is run using the
  svcmgr opensvc agent command on the node specified by **node_id**.
- **action**
. The opensvc agent action to execute.
- **module**
. The compliance module to run **action** on.
- **moduleset**
. The compliance moduleset to run **action** on.
- **rid**
. The service resource id to limit **action** to.

Each action has specific property requirements:

- ``compliance_check``:green requires **node_id**, **module** or **moduleset**, optionally
  **svc_id**
- ``compliance_fix``:green requires **node_id**, **module** or **moduleset**, optionally
  **svc_id**
- ``start``:green requires **node_id**, **svc_id**, optionally **rid**
- ``stop``:green requires **node_id**, **svc_id**, optionally **rid**
- ``restart``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncall``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncnodes``:green requires **node_id**, **svc_id**, optionally **rid**
- ``syncdrp``:green requires **node_id**, **svc_id**, optionally **rid**
- ``enable``:green requires **node_id**, **svc_id**, optionally **rid**
- ``disable``:green requires **node_id**, **svc_id**, optionally **rid**
- ``freeze``:green requires **node_id**, **svc_id**, optionally **rid**
- ``thaw``:green requires **node_id**, **svc_id**, optionally **rid**
- ``push``:green requires **node_id**
- ``shutdown``:green requires **node_id**
"""
        examples = [
          "# curl -u %(email)s -o- -X PUT -d action=push https://%(collector)s/init/rest/api/services/test/queue_action",
        ]

        rest_put_handler.__init__(
          self,
          path="/services/<id>/queue_action",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svcmon.svc_id == svc_id
        rows = db(q).select(db.svcmon.node_id)
        n = 0
        data = []
        vars["svc_id"] = svc_id
        for row in rows:
            vars["node_id"] = row.node_id
            action_id = json_action_one(vars)
            if action_id > 0:
                n += 1
                data += rest_get_action_queue_one().handler(action_id)["data"]
        if n > 0:
            action_q_event()
        return dict(data=data)

#
class rest_get_service_targets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List the target ports visible through the service nodes storage host bus adapters.",
        ]
        examples = [
          "# curl -u %(email)s -o- "
          "https://%(collector)s/init/rest/api/services/1/targets",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/targets",
          tables=["stor_zone", "stor_array"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.stor_zone.node_id
        q &= db.stor_zone.tgt_id == db.stor_array_tgtid.array_tgtid
        q &= db.stor_array_tgtid.array_id == db.stor_array.id
        q = q_filter(q, node_field=db.stor_zone.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_service_hbas(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a service's nodes storage host bus adapters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services/1/hbas",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/services/<id>/hbas",
          tables=["node_hba"],
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.node_hba.node_id
        q = q_filter(q, node_field=db.node_hba.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_put_service_disks(rest_put_handler):
    def __init__(self):
        desc = [
          "Provision/Unprovision a service disk.",
        ]
        examples = [
          "# curl -u %(email)s -X PUT -d action=provision -o- https://%(collector)s/init/rest/api/services/1/disks",
        ]
        rest_put_handler.__init__(
          self,
          path="/services/<id>/disks",
          desc=desc,
          examples=examples,
        )

    def handler(self, svc_id, **vars):
        svc_id = get_svc_id(svc_id)
        svc_responsible(svc_id)
        if "action" not in vars:
            raise HTTP(400, "The 'action' parameter is mandatory")
        action = vars["action"]
        if action == "unprovision":
            if "disk_id" not in vars:
                raise HTTP(400, "The 'disk_id' parameter is mandatory")
            disk_id = vars["disk_id"]
            q = db.forms.form_name == "storage.array.disk.del"
            form = db(q).select().first()
            if form is None:
                raise HTTP(500, "The 'storage.array.disk.del' form is not defined")
            q = db.diskinfo.disk_id == disk_id
            q &= db.diskinfo.disk_arrayid == db.stor_array.array_name
            disk = db(q).select().first()
            if disk is None:
                raise HTTP(404, "disk %s not found" % disk_id)
            q &= db.diskinfo.disk_id == db.svcdisks.disk_id
            q &= db.svcdisks.svc_id == svc_id
            disk = db(q).select().first()
            if disk is None:
                raise HTTP(403, "service %s is not responsible of disk %s" % (svc_id, disk_id))
            form_data = {
                "array_id": disk.stor_array.id,
                "disk_id": disk.diskinfo.disk_id,
                "disk_name": disk.diskinfo.disk_name,
                "action": "del_array_disk",
            }
        elif action == "provision":
            if "size" not in vars:
                raise HTTP(400, "The 'size' parameter is mandatory")
            if "array_name" not in vars:
                raise HTTP(400, "The 'array_name' parameter is mandatory")
            if "diskgroup" not in vars:
                raise HTTP(400, "The 'diskgroup' parameter is mandatory")
            size = vars["size"]
            q = db.forms.form_name == "storage.svc.disk.add"
            form = db(q).select().first()
            if form is None:
                raise HTTP(500, "The 'storage.array.disk.del' form is not defined")
            q = db.stor_array_dg.dg_name == vars["diskgroup"]
            q &= db.stor_array_dg.array_id == db.stor_array.id
            q &= db.stor_array.array_name == vars["array_name"]
            row = db(q).select().first()
            if row is None:
                raise HTTP(404, "array diskgroup not found")
            q = db.services.svc_id == svc_id
            svc = db(q).select(db.services.svcname,db.services.svc_app).first()
            if svc is None:
                raise HTTP(404, "service not found")
            q = db.apps.app == svc.svc_app
            app = db(q).select(db.apps.id,db.apps.app).first()
            if app is None:
                raise HTTP(404, "service app not found")
            form_data = {
                "size": size,
                "svcname": svc.svcname,
                "svc_id": svc_id,
                "svc_app": app.app,
                "app_id": app.id,
                "array_id": row.stor_array.id,
                "dg_name": row.stor_array_dg.dg_name,
                "dg_id": row.stor_array_dg.id,
                "action": "add_svc_disk",
            }
            if "slo" in vars:
                form_data["slo"] = slo
        return form_submit(form, _d=form_data)

#
class rest_post_service_snooze(rest_post_handler):
    def __init__(self):
        desc = [
          "Snooze notifications on a service",
          "The user must be responsible for the service.",
          "The service can snooze itself.",
          "The updated timestamp is updated.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the services table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d duration="1h" https://%(collector)s/init/rest/api/services/mysvc/snooze""",
        ]
        rest_post_handler.__init__(
          self,
          path="/services/<id>/snooze",
          desc=desc,
          examples=examples,
          replication=["relay", "local"],
        )

    def handler(self, svc_id, **vars):
        if auth_is_svc():
            svc_id = auth.user.svc_id
        else:
            svc_responsible(svc_id)
            svc_id = get_svc_id(svc_id)
            if svc_id is None:
                raise HTTP(400, "service does not exist")
        duration = vars.get("duration")
        if duration is None:
            action = "unsnooze"
            fmt = ''
            d = dict()
        else:
            action = "snooze"
            duration = convert_duration(duration, _to="m")
            duration = datetime.datetime.now() + datetime.timedelta(minutes=duration)
            fmt = 'duration %(duration)s'
            d = dict(duration=vars.get("duration"))
        q = db.services.svc_id == svc_id
        db(q).update(svc_snooze_till=duration)
        _log('service.%s' % action, fmt, d, svc_id=svc_id)
        ws_send('services_change', {'svc_id': svc_id})
        return {"info": action+"d"}


