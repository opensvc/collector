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
        q = q_filter(node_field=db.checks_live.node_id)
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
        q = q_filter(q, node_field=db.checks_live.node_id)
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
        check_privilege("CheckExec")
        q = db.checks_live.id == id
        q = q_filter(q, node_field=db.checks_live.node_id)
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance %s does not exist" % str(id))
        node_responsible(node_id=row.node_id)

        db(q).delete()

        _log('check.delete',
             'delete check instance %(data)s',
             dict(data='-'.join((row.chk_type, row.chk_instance))),
             node_id=row.node_id,
             svc_id=row.svc_id,
            )
        ws_send('checks_change', {'id': row.id})
        table_modified("checks_live")
        update_dash_checks(row.node_id)

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
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/live?filter[]=chk_type=eth%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/live",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("CheckExec")
        s = ""
        if 'id' in vars:
            q = db.checks_live.id == vars["id"]
            s = vars["id"]
        elif 'node_id' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            node_id = get_node_id(vars["node_id"])
            q = db.checks_live.node_id == node_id
            q &= db.checks_live.chk_type == vars["chk_type"]
            q &= db.checks_live.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], get_nodename(node_id))
        else:
            raise Exception("id key or node_id+chk_type+chk_instance[+svc_id] must be specified")
        if 'svc_id' in vars and vars["svc_id"] != "":
            svc_id = get_svc_id(vars["svc_id"])
            q &= db.checks_live.svc_id == svc_id
            s += get_svcname(svc_id)
        q = q_filter(q, node_field=db.checks_live.node_id)
        row = db(q).select().first()
        if row is None:
            raise Exception("check instance %s does not exist" % s)
        return rest_delete_check().handler(row.id)


#
# checks_defaults table handlers
#
class rest_get_checks_defaults(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List check instances threshold defaults.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/defaults",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/checks/defaults",
          tables=["checks_defaults"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.checks_defaults.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_checks_default(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a check instance threshold defaults properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/defaults/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/checks/defaults/<id>",
          tables=["checks_defaults"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.checks_defaults.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_delete_checks_default(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete a check instance threshold defaults.",
          "- Log the deletion.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/defaults/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/defaults/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CheckManager")
        q = db.checks_defaults.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance defaults %s does not exist" % str(id))

        db(q).delete()

        _log('check.defaults.delete',
             'delete check instance defaults %(data)s',
             dict(data='-'.join((row.chk_type, row.chk_inst))),
            )
        table_modified("checks_defaults")
        ws_send('checks_defaults_change', {'id': row.id})

        #q = db.checks_live.chk_type == row.chk_type
        #rows = db(q).select()
        #update_thresholds_batch(rows, one_source=True)

        return dict(info="check instance defaults %s deleted" % str(id))

#
class rest_delete_checks_defaults(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete check instances defaults.",
          "- Log the deletion.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/defaults?filter[]=chk_type=eth%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/defaults",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("CheckManager")
        if 'id' not in vars:
            raise Exception("id key must be specified")
        return rest_delete_checks_default().handler(vars["id"])

#
class rest_post_checks_default(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify a check instance threshold defaults.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the change.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d chk_low=1 -o- https://%(collector)s/init/rest/api/checks/defaults/1",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/defaults/<id>",
          tables=["checks_defaults"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("CheckManager")
        q = db.checks_defaults.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance defaults %s does not exist" % str(id))

        if "id" in vars:
            del vars["id"]

        db(q).update(**vars)

        fmt = 'change check instance defaults %(data)s'
        d = dict(data=beautify_change(row, vars))
        _log('check.defaults.change', fmt, d)
        table_modified("checks_defaults")
        l = {
          'event': 'checks_defaults_change',
          'data': {'id': row.id},
        }

        return_data = rest_get_checks_default().handler(id)
        return_data["info"] = fmt % d
        return return_data

#
class rest_post_checks_defaults(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify or add check instances threshold defaults.",
          "- The user must be in the CheckManager privilege group.",
          "- Log the changes.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d node_id=1 -d chk_type=eth -d chk_inst=eth0.speed -d chk_low=0 -o- https://%(collector)s/init/rest/api/checks/defaults",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/defaults",
          tables=["checks_defaults"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if 'id' not in vars:
            check_privilege("CheckManager")
            if not "chk_type" in vars:
                raise Exception("chk_type must be specified")

            id = db.checks_defaults.insert(**vars)
            fmt = 'add check instance defaults %(data)s'
            d = dict(data=beautify_data(vars))
            _log('check.defaults.add',fmt, d)
            table_modified("checks_defaults")
            ws_send('checks_change', {'id': id})

            return_data = rest_get_checks_default().handler(id)
            return_data["info"] = fmt % d
            return return_data

        return rest_post_checks_default().handler(vars["id"], **vars)

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
        q = q_filter(q, node_field=db.checks_settings.node_id)
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
        q = q_filter(q, node_field=db.checks_settings.node_id)
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
        check_privilege("CheckExec")
        q = db.checks_settings.id == id
        q = q_filter(q, node_field=db.checks_settings.node_id)
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance settings %s does not exist" % str(id))
        node_responsible(node_id=row.node_id)

        db(q).delete()

        _log('check.settings.delete',
             'delete check instance settings %(data)s',
             dict(data='-'.join((row.chk_type, row.chk_instance))),
             node_id=row.node_id,
             svc_id=row.svc_id,
            )
        table_modified("checks_settings")
        ws_send('checks_change', {'id': row.id})

        q = db.checks_live.node_id == row.node_id
        q = db.checks_live.svc_id == row.svc_id
        q = db.checks_live.chk_type == row.chk_type
        q = db.checks_live.chk_instance == row.chk_instance
        rows = db(q).select()
        update_thresholds_batch(rows, one_source=True)
        update_dash_checks(row.node_id)

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
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/settings?filter[]=chk_type=eth%%",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/settings",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("CheckExec")
        s = ""
        if 'id' in vars:
            q = db.checks_settings.id == vars["id"]
            s = vars["id"]
        elif 'node_id' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            node_id = get_node_id(vars["node_id"])
            q = db.checks_settings.node_id == node_id
            q &= db.checks_settings.chk_type == vars["chk_type"]
            q &= db.checks_settings.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], get_nodename(node_id))
        else:
            raise Exception("id key or node_id+chk_type+chk_instance[+svc_id] must be specified")
        if 'svc_id' in vars and vars["svc_id"] != "":
            svc_id = get_svc_id(vars["svc_id"])
            q &= db.checks_settings.svc_id == svc_id
            s += get_svcname(svc_id)
        q = q_filter(q, node_field=db.checks_settings.node_id)
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
          "- The user must be in the CheckExec privilege group.",
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
        check_privilege("CheckExec")
        q = db.checks_settings.id == id
        q = q_filter(q, node_field=db.checks_settings.node_id)
        row = db(q).select().first()
        if row is None:
            raise Exception("Check instance settings %s does not exist" % str(id))
        node_responsible(node_id=row.node_id)

        data = {}
        for key in vars:
            if key in ("chk_low", "chk_high"):
                data[key] = vars[key]
        data["chk_changed"] = datetime.datetime.now()
        data["chk_changed_by"] = user_name()

        db(q).update(**data)

        fmt = 'change check instance settings %(data)s'
        d = dict(data=beautify_change(row, data))
        _log('check.settings.change', fmt, d,
             node_id=row.node_id,
             svc_id=row.svc_id,
            )
        table_modified("checks_settings")
        table_modified("checks_settings")
        l = {
          'event': 'checks_change',
          'data': {'id': row.id},
        }

        q = db.checks_live.node_id == row.node_id
        q = db.checks_live.svc_id == row.svc_id
        q = db.checks_live.chk_type == row.chk_type
        q = db.checks_live.chk_instance == row.chk_instance
        rows = db(q).select()
        update_thresholds_batch(rows, one_source=True)
        update_dash_checks(row.node_id)
        return_data = rest_get_checks_setting().handler(row.id)
        return_data["info"] = fmt % d
        return return_data

#
class rest_post_checks_settings(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify or add check instances threshold settings.",
          "- The user must be responsible for the nodes.",
          "- The user must be in the CheckExec privilege group.",
          "- Log the changes.",
          "- Send websocket change events.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d node_id=1 -d chk_type=eth -d chk_instance=eth0.speed -d chk_low=0 -o- https://%(collector)s/init/rest/api/checks/settings",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/settings",
          tables=["checks_settings"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("CheckExec")
        s = ""
        if 'id' in vars:
            q = db.checks_settings.id == vars["id"]
            s = vars["id"]
        elif 'node_id' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            node_id = get_node_id(vars["node_id"])
            q = db.checks_settings.node_id == node_id
            q &= db.checks_settings.chk_type == vars["chk_type"]
            q &= db.checks_settings.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], get_nodename(node_id))
        else:
            raise Exception("id key or node_id+chk_type+chk_instance[+svc_id] must be specified")
        if 'svc_id' in vars and vars["svc_id"] != "":
            svc_id = get_svc_id(vars["svc_id"])
            q &= db.checks_settings.svc_id == svc_id
            s += get_svcname(svc_id)
        else:
            svc_id = None
        row = db(q).select().first()
        if row is None:
            if not "node_id" in vars or not "chk_type" in vars or not "chk_instance" in vars:
                raise Exception("node_id+chk_type+chk_instance[+svc_id] must be specified")
            check_privilege("CheckManager")
            node_id = get_node_id(vars["node_id"])
            node_responsible(node_id=node_id)
            vars["chk_changed"] = datetime.datetime.now()
            vars["chk_changed_by"] = user_name()

            q = db.checks_live.node_id == node_id
            q = db.checks_live.svc_id == svc_id
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
            fmt = 'add check instance settings %(data)s'
            d = dict(data=beautify_data(vars))
            _log('check.settings.add',fmt, d,
                 node_id=node_id,
                 svc_id=svc_id,
                )
            table_modified("checks_settings")
            ws_send('checks_change', {'id': row.id})

            update_thresholds_batch(rows, one_source=True)
            update_dash_checks(node_id)
            return_data = rest_get_checks_setting().handler(id)
            return_data["info"] = fmt % d
            return return_data

        return rest_post_checks_setting().handler(row.id, **vars)

#
# gen_filterset_check_threshold table handlers
#
class rest_get_checks_contextual_settings(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List checks contextual threshold settings.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/contextual_settings",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/checks/contextual_settings",
          tables=["v_gen_filterset_check_threshold"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.v_gen_filterset_check_threshold.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_checks_contextual_setting(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a checks contextual threshold setting properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/checks/contextual_settings/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/checks/contextual_settings/<id>",
          tables=["v_gen_filterset_check_threshold"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_gen_filterset_check_threshold.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_delete_checks_contextual_setting(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete a checks contextual threshold setting.",
          "- The user must be in the ContextCheckManager privilege group.",
          "- Log the deletion.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/contextual_settings/1",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/contextual_settings/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ContextCheckManager")
        q = db.v_gen_filterset_check_threshold.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("Checks contextual settings %s does not exist" % str(id))

        q = db.gen_filterset_check_threshold.id == id
        db(q).delete()

        _log('check.contextual_settings.delete',
             'delete checks contextual settings %(data)s',
             dict(data=row.name),
            )
        table_modified("gen_filterset_check_threshold")

        enqueue_update_thresholds_batch(row.chk_type)
        return dict(info="checks contextual settings %s deleted" % str(id))

#
class rest_delete_checks_contextual_settings(rest_delete_handler):
    def __init__(self):
        desc = [
          "- Delete checks contextual threshold settings.",
          "- The user must be in the ContextCheckManager privilege group.",
          "- Log the deletion.",
          "- Send a websocket change event.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/checks/contextual_settings",
        ]
        rest_delete_handler.__init__(
          self,
          path="/checks/contextual_settings",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory.")
        return rest_delete_checks_contextual_setting().handler(vars["id"])


#
class rest_post_checks_contextual_setting(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify a checks contextual threshold settings.",
          "- The user must be in the ContextCheckManager privilege group.",
          "- Log the changes.",
          "- Start a background job to update the checks thresholds.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d fset_id=1 -d chk_type=eth -d chk_instance=eth0.speed -d chk_high=90 -d chk_low=0 -o- https://%(collector)s/init/rest/api/checks/contextual_settings",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/contextual_settings/<id>",
          tables=["gen_filterset_check_threshold"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ContextCheckManager")
        q = db.gen_filterset_check_threshold.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("Contextual setting %s not found" % str(id))

        db(q).update(**vars)
        _log('check.contextual_settings.change',
             'changed checks contextual instance settings %(data)s',
             dict(data=beautify_change(row, vars)),
            )
        table_modified("gen_filterset_check_threshold")

        enqueue_update_thresholds_batch()
        return_data = rest_get_checks_contextual_setting().handler(id)
        return_data["info"] = 'changed checks contextual instance settings %(data)s' % dict(data=beautify_change(row, vars))
        return return_data

#
class rest_post_checks_contextual_settings(rest_post_handler):
    def __init__(self):
        desc = [
          "- Modify or add checks contextual threshold settings.",
          "- The user must be in the ContextCheckManager privilege group.",
          "- Log the changes.",
          "- Start a background job to update the checks thresholds.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d fset_id=1 -d chk_type=eth -d chk_instance=eth0.speed -d chk_high=90 -d chk_low=0 -o- https://%(collector)s/init/rest/api/checks/contextual_settings",
        ]
        rest_post_handler.__init__(
          self,
          path="/checks/contextual_settings",
          tables=["gen_filterset_check_threshold"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        s = ""
        if 'id' in vars:
            q = db.gen_filterset_check_threshold.id == vars["id"]
            s = vars["id"]
        elif 'fset_id' in vars and 'chk_type' in vars and 'chk_instance' in vars:
            q = db.gen_filterset_check_threshold.fset_id == vars["fset_id"]
            q &= db.gen_filterset_check_threshold.chk_type == vars["chk_type"]
            q &= db.gen_filterset_check_threshold.chk_instance == vars["chk_instance"]
            s = "%s %s %s" % (vars["chk_type"], vars["chk_instance"], str(vars["fset_id"]))
        else:
            raise Exception("id key or fset_id+chk_type+chk_instance must be specified")
        row = db(q).select().first()
        if row is None:
            if not "fset_id" in vars or not "chk_type" in vars or not "chk_instance" in vars or not "chk_low" in vars or not "chk_high" in vars:
                raise Exception("fset_id+chk_type+chk_instance+chk_low+chk_high must be specified")

            check_privilege("ContextCheckManager")
            id = db.gen_filterset_check_threshold.insert(**vars)
            _log('check.contextual_settings.add',
                 'add checks contextual instance settings %(data)s',
                 dict(data=beautify_data(vars)),
                )
            table_modified("gen_filterset_check_threshold")

            enqueue_update_thresholds_batch()
            return_data = rest_get_checks_contextual_setting().handler(id)
            return_data["info"] = "checks contextual instance %d added" % id
            return return_data

        return rest_post_checks_contextual_setting().handler(row.id, **vars)


