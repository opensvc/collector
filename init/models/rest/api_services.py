from gluon.dal import smart_query

def svc_responsible(svcname):
    q = db.services.svc_name == svcname
    n = db(q).count()
    if n == 0:
        raise Exception("Service %s does not exist" % svcname)
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    db.apps_responsibles.group_id.belongs(user_group_ids())
    n = db(q).count()
    if n != 1:
        raise Exception("Not authorized: user is not responsible for service %s" % svcname)


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
        q = _where(q, 'services', domain_perms(), 'svc_name')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_services(rest_get_table_handler):
    def __init__(self):
        params = {
          "fset_id": {
             "desc": "Filter the list using the filterset identified by fset_id."
          }
        }
        desc = [
          "List OpenSVC services.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/services?props=svc_name,app&fset_id=10",
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
        fset_id = vars.get("fset_id")
        if fset_id:
            q = apply_filters(q, service_field=db.services.svc_name, fset_id=fset_id)
        self.set_q(q)
        return self.prepare_data(**vars)


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
          desc=desc,
          examples=examples,
        )

    def handler(self, svcname, **vars):
        q = db.dashboard.dash_svcname == svcname
        q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')
        self.set_q(q)
        data = self.prepare_data(**vars)
        data["data"] = mangle_alerts(data["data"])
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


