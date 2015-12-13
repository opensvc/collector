#
# checks_live table handlers
#
class rest_get_checks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List check instances.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/live",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/checks/live",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.checks_live.id > 0
        q &= _where(None, 'checks_live', domain_perms(), 'chk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_check(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a check instance properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/live/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/checks/live/<id>",
          tables=["checks_live"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.checks_live.id == id
        q &= _where(None, 'checks_live', domain_perms(), 'chk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_check(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete a check instance.",
          "- The user must be responsible for the node.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the deletion.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/live/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/live/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CheckManager")
        q = db.checks_live.id == id
        q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance %s does not exist" % str(id))
        node_responsible(row.chk_nodename)

        db(q).delete()

        _log('check.delete',
             'delete check instance %(data)s',
             dict(data='-'.join((row.chk_nodename, row.chk_svcname, row.chk_type, row.chk_instance))),
             nodename=row.chk_nodename,
             svcname=row.chk_svcname,
            )
        l = {
          'event': 'checks_change',
          'data': {'id': row.id},
        }
        _websocket_send(event_msg(l))
        table_modified("checks_live")
        update_dash_checks(row.chk_nodename)

        return dict(info="check instance %s deleted" % str(id))

#
class rest_delete_checks(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete check instances.",
          "- Log the deletion.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/live?filter[]=chk_nodename=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/live",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        s = ""
        if 'id' in vars:
            q = db.checks_live.id == vars["id"]
            s = vars["id"]
        elif 'chk_nodename' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            q = db.checks_live.chk_nodename == vars["chk_nodename"]
            q &= db.checks_live.chk_type == vars["chk_type"]
            q &= db.checks_live.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], vars["chk_nodename"])
        else:
            raise Exception("id key or chk_nodename+chk_type+chk_instance[+chk_svcname] must be specified")
        if 'chk_svcname' in vars:
            q &= db.checks_live.chk_svcname == vars["chk_svcname"]
            s += vars["chk_svcname"]
        q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("check instance %s does not exist" % s)
        return rest_delete_check().handler(row.id)


#
# checks_settings table handlers
#
class rest_get_checks_settings(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List check instances threshold settings.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/settings",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/checks/settings",
          tables=["checks_settings"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.checks_settings.id > 0
        q &= _where(None, 'checks_settings', domain_perms(), 'chk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_checks_setting(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a check instance threshold settings properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/settings/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/checks/settings/<id>",
          tables=["checks_settings"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.checks_settings.id == id
        q &= _where(None, 'checks_settings', domain_perms(), 'chk_nodename')
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_checks_setting(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete a check instance threshold settings.",
          "- The user must be responsible for the node.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the deletion.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/settings/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/settings/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CheckManager")
        q = db.checks_settings.id == id
        q = _where(q, 'checks_settings', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance settings %s does not exist" % str(id))
        node_responsible(row.chk_nodename)

        db(q).delete()

        _log('check.settings.delete',
             'delete check instance settings %(data)s',
             dict(data='-'.join((row.chk_nodename, row.chk_svcname, row.chk_type, row.chk_instance))),
             nodename=row.chk_nodename,
             svcname=row.chk_svcname,
            )
        table_modified("checks_settings")

        q = db.checks_live.chk_nodename == row.chk_nodename
        q = db.checks_live.chk_svcname == row.chk_svcname
        q = db.checks_live.chk_type == row.chk_type
        q = db.checks_live.chk_instance == row.chk_instance
        rows = db(q).select()
        update_thresholds_batch(rows, one_source=True)
        update_dash_checks(row.chk_nodename)

        return dict(info="check instance settings %s deleted" % str(id))

#
class rest_delete_checks_settings(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete check instances settings.",
          "- Log the deletion.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/settings?filter[]=chk_nodename=test%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/settings",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        s = ""
        if 'id' in vars:
            q = db.checks_settings.id == vars["id"]
            s = vars["id"]
        elif 'chk_nodename' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            q = db.checks_settings.chk_nodename == vars["chk_nodename"]
            q &= db.checks_settings.chk_type == vars["chk_type"]
            q &= db.checks_settings.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], vars["chk_nodename"])
        else:
            raise Exception("id key or chk_nodename+chk_type+chk_instance[+chk_svcname] must be specified")
        if 'chk_svcname' in vars:
            q &= db.checks_settings.chk_svcname == vars["chk_svcname"]
            s += vars["chk_svcname"]
        q = _where(q, 'checks_settings', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("check instance settings %s does not exist" % s)
        return rest_delete_checks_setting().handler(row.id)

#
class rest_post_checks_setting(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify a check instance threshold settings.",
          "- The user must be responsible for the node.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the change.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d chk_low=1 -o- https://%(collector)s/init/rest/api/checks/settings/1",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/settings/<id>",
          tables=["checks_settings"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CheckManager")
        q = db.checks_settings.id == id
        q = _where(q, 'checks_settings', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance settings %s does not exist" % str(id))
        node_responsible(row.chk_nodename)

        data = {}
        for key in vars:
            if key in ("chk_low", "chk_high"):
                data[key] = vars[key]
        data["chk_changed"] = datetime.datetime.now()
        data["chk_changed_by"] = user_name()

        db(q).update(**data)

        _log('check.settings.change',
             'change check instance settings %(data)s',
             dict(data=beautify_change(row, data)),
             nodename=row.chk_nodename,
             svcname=row.chk_svcname,
            )
        table_modified("checks_settings")

        q = db.checks_live.chk_nodename == row.chk_nodename
        q = db.checks_live.chk_svcname == row.chk_svcname
        q = db.checks_live.chk_type == row.chk_type
        q = db.checks_live.chk_instance == row.chk_instance
        rows = db(q).select()
        update_thresholds_batch(rows, one_source=True)
        update_dash_checks(row.chk_nodename)
        return rest_get_checks_setting().handler(row.id)

#
class rest_post_checks_settings(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify or add check instances threshold settings.",
          "- The user must be responsible for the nodes.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the changes.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d chk_nodename=node1 -d chk_type=eth -d chk_instance=eth0.speed -d chk_low=0 -o- https://%(collector)s/init/rest/api/checks/settings",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/settings",
          tables=["checks_settings"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        s = ""
        if 'id' in vars:
            q = db.checks_settings.id == vars["id"]
            s = vars["id"]
        elif 'chk_nodename' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            q = db.checks_settings.chk_nodename == vars["chk_nodename"]
            q &= db.checks_settings.chk_type == vars["chk_type"]
            q &= db.checks_settings.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], vars["chk_nodename"])
        else:
            raise Exception("id key or chk_nodename+chk_type+chk_instance[+chk_svcname] must be specified")
        if 'chk_svcname' in vars:
            q &= db.checks_settings.chk_svcname == vars["chk_svcname"]
            s += vars["chk_svcname"]
        q = _where(q, 'checks_settings', domain_perms(), 'chk_nodename')
        row = db(q).select().first()
        if row is None:
            if not "chk_nodename" in vars or not "chk_type" in vars or not "chk_instance" in vars:
                raise Exception("chk_nodename+chk_type+chk_instance[+chk_svcname] must be specified")
            vars["chk_changed"] = datetime.datetime.now()
            vars["chk_changed_by"] = user_name()

            q = db.checks_live.chk_nodename == vars.get("chk_nodename")
            q = db.checks_live.chk_svcname == vars.get("chk_svcname", "")
            q = db.checks_live.chk_type == vars.get("chk_type")
            q = db.checks_live.chk_instance == vars.get("chk_instance")
            rows = db(q).select()
            row = rows.first()
            if row is None:
                raise Exception("check instance not found")

            if "chk_low" not in vars:
                vars["chk_low"] = row.chk_low
            if "chk_high" not in vars:
                vars["chk_high"] = row.chk_high

            id = db.checks_settings.insert(**vars)
            _log('check.settings.add',
                 'add check instance settings %(data)s',
                 dict(data=beautify_data(vars)),
                 nodename=vars.get("chk_nodename"),
                 svcname=vars.get("chk_svcname", ""),
                )
            table_modified("checks_settings")

            update_thresholds_batch(rows, one_source=True)
            update_dash_checks(vars.get("chk_nodename"))
            return rest_get_checks_setting().handler(id)

        return rest_post_checks_setting().handler(row.id, **vars)

