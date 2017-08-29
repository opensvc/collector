def lib_array_id(id):
    try:
        id = int(id)
        return id
    except:
        pass
    q = db.stor_array.array_name == id
    row = db(q).select(db.stor_array.id).first()
    if row is None:
        return
    return row.id

#
class rest_get_arrays(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage arrays.",
        ]
        examples = [
          """# curl -u %(email)s -o- "https://%(collector)s/init/rest/api/arrays?props=array_name&query=array_model contains hitachi"""
        ]
        q = db.stor_array.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/arrays",
          tables=["stor_array"],
          q=q,
          desc=desc,
          examples=examples,
        )


#
class rest_get_array(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a storage array properties.",
          "<id> can be either the id or the array name.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray?props=array_name,array_model"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/arrays/<id>",
          tables=["stor_array"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        n = db(q).count()
        if n == 0:
            try: id = int(id)
            except: return dict(data=[])
            q = db.stor_array.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_array_diskgroup(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a storage array diskgroup.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroup/1"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>",
          tables=["stor_array_dg"],
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, **vars):
        if not array_id in (0, "0"):
            q = db.stor_array.array_name == array_id
            try:
                array_id = db(q).select().first().id
            except:
                array_id = int(array_id)
            q = db.stor_array_dg.array_id == array_id
        else:
            q = db.stor_array_dg.id > 0

        try:
            dg_id = int(dg_id)
            q &= db.stor_array_dg.id == dg_id
        except:
            q &= db.stor_array_dg.dg_name == dg_id

        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_array_diskgroups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array diskgroups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups",
          tables=["stor_array_dg"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_dg.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_array_diskgroup_quotas(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array diskgroup quotas.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas",
          tables=["stor_array_dg_quota"],
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, **vars):
        q = db.stor_array_dg_quota.dg_id == dg_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_array_diskgroup_quota(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a storage array diskgroup quota.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas/1"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas/<id>",
          tables=["stor_array_dg_quota"],
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, id, **vars):
        q = db.stor_array_dg_quota.id == id
        if not dg_id in (0, "0"):
            q &= db.stor_array_dg_quota.dg_id == dg_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_array_diskgroup_quota(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a storage array diskgroup quota.",
        ]
        examples = [
          "# curl -u %(email)s -d quota=10000 -X POST -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas/1"
        ]
        rest_post_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas/<id>",
          tables=["stor_array_dg_quota"],
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, quota_id, **vars):
        check_privilege("StorageManager")

        q = db.stor_array_dg_quota.id == quota_id
        quota = db(q).select().first()
        if quota is None:
            raise Exception("quota %s not found" % str(quota_id))

        if "app_id" in vars:
            q = db.apps.id == vars["app_id"]
            app = db(q).select().first()
            if app is None:
                raise Exception("app %s not found" % str(vars["app_id"]))
        elif "app" in vars:
            q = db.apps.app == vars["app"]
            app = db(q).select().first()
            if app is None:
                raise Exception("app %s not found" % str(vars["app"]))
            del(vars["app"])
            vars["app_id"] = app.id
        else:
            q = db.apps.id == quota.app_id
            app = db(q).select().first()

        q = db.stor_array_dg.id == dg_id
        dg = db(q).select().first()
        if dg is None:
            raise Exception("dg %s not found" % str(dg_id))

        q = db.stor_array_dg_quota.id == quota_id
        db(q).update(**vars)

        fmt = "%(quota)s quota change for app %(app)s in dg %(dg)s: %(data)s"
        d = dict(quota=str(vars.get("quota", "")), app=app.app, dg=dg.dg_name, data=beautify_change(quota, vars))

        _log('quota.change', fmt, d)
        ws_send('stor_array_dg_quota_change', {'id': quota.id})
        table_modified("stor_array_dg_quota")

        ret = rest_get_array_diskgroup_quota().handler(array_id, dg_id, quota_id)
        ret["info"] = fmt % d
        return ret

#
class rest_post_array_diskgroup_quotas(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a storage array diskgroup quota.",
        ]
        examples = [
          "# curl -u %(email)s -d app_id=1 -d quota=10000 -X POST -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas"
        ]
        rest_post_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas",
          tables=["stor_array_dg_quota"],
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, **vars):
        check_privilege("StorageManager")

        if not "quota" in vars:
            raise Exception("The 'quota' key is mandatory")

        if "app_id" in vars:
            q = db.apps.id == vars["app_id"]
            app = db(q).select().first()
            if app is None:
                raise Exception("app %s not found" % str(vars["app_id"]))
        elif "app" in vars:
            q = db.apps.app == vars["app"]
            app = db(q).select().first()
            if app is None:
                raise Exception("app %s not found" % str(vars["app"]))
            del(vars["app"])
        else:
            raise Exception("Either 'app' or 'app_id' is mandatory")

        q = db.stor_array_dg.id == dg_id
        dg = db(q).select().first()
        if dg is None:
            raise Exception("dg %s not found" % str(dg_id))

        q = db.stor_array_dg_quota.dg_id == dg_id
        q &= db.stor_array_dg_quota.app_id == app.id
        quota = db(q).select().first()

        vars["app_id"] = app.id
        vars["dg_id"] = dg_id
        d = dict(quota=str(vars.get("quota", "")), app=app.app, dg=dg.dg_name)

        if quota is None:
            id = db.stor_array_dg_quota.insert(**vars)
            fmt = "%(quota)s quota added for app %(app)s in dg %(dg)s"
            _log('quota.add', fmt, d)
        else:
            id = quota.id
            db(q).update(**vars)
            fmt = "%(quota)s quota updated for app %(app)s in dg %(dg)s"
            _log('quota.change', fmt, d)

        ws_send('stor_array_dg_quota_change', {'id': id})
        table_modified("stor_array_dg_quota")

        ret = rest_get_array_diskgroup_quota().handler(array_id, dg_id, id)
        ret["info"] = fmt % d
        return ret

#
class rest_delete_array_diskgroup_quotas(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete storage array diskgroup quotas.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas"
        ]
        rest_delete_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")
        quota_id = vars.get("id")
        del(vars["id"])
        return rest_delete_array_diskgroup_quota().handler(array_id, dg_id, quota_id, **vars)

#
class rest_delete_array_diskgroup_quota(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a storage array diskgroup quota.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups/1/quotas/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups/<id>/quotas/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, dg_id, quota_id, **vars):
        check_privilege("StorageManager")

        q = db.stor_array_dg_quota.id == quota_id
        quota = db(q).select().first()
        if quota is None:
            raise Exception("quota %s not found" % str(quota_id))

        q = db.apps.id == quota.app_id
        app = db(q).select().first()

        q = db.stor_array_dg.id == quota.dg_id
        dg = db(q).select().first()

        fmt = "%(quota)s quota deleted for app %(app)s in dg %(dg)s"
        d = dict(quota=str(quota.quota), app=str(app.app), dg=str(dg.dg_name))

        _log('quota.del', fmt, d)
        ws_send('stor_array_dg_quota_change', {'id': quota.id})
        table_modified("stor_array_dg_quota")

        ret = {}
        ret["info"] = fmt % d
        return ret


#
class rest_get_array_proxies(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array proxies.",
          "Proxies are OpenSVC agent inventoring the array.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/proxies",
          tables=["stor_array_proxy"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_proxy.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_array_proxy(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a storage array proxy.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies/9d5ae2e6-9ca7-47b2-ab25-cd026be434f4"
        ]
        rest_post_handler.__init__(
          self,
          path="/arrays/<id>/proxies/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, node_id, **vars):
        check_privilege("StorageManager")
        array_id = lib_array_id(array_id)
        q = db.stor_array_proxy.array_id == array_id
        q &= db.stor_array_proxy.node_id == node_id
        row = db(q).select().first()
        if row is not None:
            raise Exception("node %s is already proxy for array %d" % (node_id, array_id))
        row_id = db.stor_array_proxy.insert(
            node_id=node_id,
            array_id=array_id,
        )
        fmt = "node %(node_id)s set as proxy for array %(array_id)s"
        d = dict(node_id=str(node_id), array_id=str(array_id))

        _log('storage.array.proxy.add', fmt, d)
        ws_send('stor_array_proxy_change', {'id': row_id})
        table_modified("stor_array_proxy")

        ret = {}
        ret["info"] = fmt % d
        return ret

class rest_post_array_proxies(rest_post_handler):
    def __init__(self):
        desc = [
          "Add storage array proxies.",
        ]
        examples = [
                """# echo '[{"node_id": "9d5ae2e6-9ca7-47b2-ab25-cd026be434f4"}]' >/tmp/list.json\n"""
                """# curl -u %(email)s -X POST --header 'Content-Type: application/json' -d @/tmp/list.json -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies"""
        ]
        rest_post_handler.__init__(
          self,
          path="/arrays/<id>/proxies",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, **vars):
        check_privilege("StorageManager")
        if "node_id" not in vars:
            raise Exception("The 'node_id' key is mandatory")
        node_id = vars.get("node_id")
        del(vars["node_id"])
        return rest_post_array_proxy().handler(array_id, node_id, **vars)

class rest_delete_array_proxy(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a storage array proxy.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies/9d5ae2e6-9ca7-47b2-ab25-cd026be434f4"
        ]
        rest_delete_handler.__init__(
          self,
          path="/arrays/<id>/proxies/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, node_id, **vars):
        check_privilege("StorageManager")
        array_id = lib_array_id(array_id)
        q = db.stor_array_proxy.array_id == array_id
        q &= db.stor_array_proxy.node_id == node_id
        row = db(q).select().first()
        if row is None:
            raise Exception("node %s is not proxy for array %d" % (node_id, array_id))
        db(q).delete()
        fmt = "node %(node_id)s unset as proxy for array %(array_id)s"
        d = dict(node_id=str(node_id), array_id=str(array_id))

        _log('storage.array.proxy.del', fmt, d)
        ws_send('stor_array_proxy_change', {'id': row.id})
        table_modified("stor_array_proxy")

        ret = {}
        ret["info"] = fmt % d
        return ret

class rest_delete_array_proxies(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete storage array proxies.",
        ]
        examples = [
                """# echo '[{"node_id": "9d5ae2e6-9ca7-47b2-ab25-cd026be434f4"}]' >/tmp/list.json\n"""
                """# curl -u %(email)s -X DELETE --header 'Content-Type: application/json' -d @/tmp/list.json -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies"""
        ]
        rest_delete_handler.__init__(
          self,
          path="/arrays/<id>/proxies",
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, **vars):
        check_privilege("StorageManager")
        if "node_id" not in vars:
            raise Exception("The 'node_id' key is mandatory")
        node_id = vars.get("node_id")
        del(vars["node_id"])
        return rest_delete_array_proxy().handler(array_id, node_id, **vars)

#
class rest_get_array_targets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array target ports.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/targets"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/targets",
          tables=["stor_array_tgtid"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_tgtid.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_array_disks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a specific array disks.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/array/1/disks?props=svcdisks.node_id,svcdisks.disk_id,stor_array.array_name",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/disks",
          tables=["svcdisks", "diskinfo", "stor_array"],
          left=(
              db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id),
              db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
          ),
          desc=desc,
          examples=examples,
        )

    def handler(self, array_id, **vars):
        q = db.stor_array.id == array_id
        q = q_filter(q, node_field=db.svcdisks.node_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_array(rest_post_handler):
    def __init__(self):
        desc = [
          "Change an array properties.",
          "The user must be in the StorageManager or Manager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d array_comment="Moui importante" https://%(collector)s/init/rest/api/arrays/1""",
        ]
        rest_post_handler.__init__(
          self,
          path="/arrays/<id>",
          tables=["stor_array"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("StorageManager")
        id = lib_array_id(id)
        if id is None:
            return Exception("array id not found")
        q = db.stor_array.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("array %s does not exist" % str(id))
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        table_modified("stor_array")
        fmt = 'array %(name)s changed: %(data)s'
        d = dict(name=row.array_name, data=beautify_change(row, vars))
        _log('array.change', fmt, d)
        ws_send('stor_array_change', {'id': row.id})
        ret = rest_get_array().handler(row.id)
        ret["info"] = fmt % d
        return ret


