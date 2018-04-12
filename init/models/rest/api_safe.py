#
class rest_post_safe_file(rest_post_handler):
    def __init__(self):
        desc = [
          "Change the properties of a file in the collector safe.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -F "file=@/etc/resolv.conf" https://%(collector)s/init/rest/api/safe/upload""",
        ]
        data = """
- **name**
. A symbolic name to identify the file in the safe.
"""
        rest_post_handler.__init__(
          self,
          path="/safe/<id>",
          tables=["safe"],
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, id, **vars):
        lib_safe_check_file_responsible(id)
        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        current = db(q).select().first()

        if current is None:
            raise Exception("file %s not found" % id)

        data = {}
        if "name" in vars:
            data["name"] = vars.get("name")

        db(q).update(**data)

        changes = []
        for k, v in data.items():
            changes += "(%s: %s => %s)" % (k, str(current), str(v))
        changes = ", ".join(changes)

        _log(
          'safe.change',
          'file %(id)s properties changed: %(changes)s.',
          dict(uuid=current.uuid, changes=changes),
        )
        ws_send('safe_change')
        return rest_get_safe_file().handler(id)

#
class rest_post_safe_upload(rest_post_handler):
    def __init__(self):
        desc = [
          "Upload a file into the collector safe.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -F "file=@/etc/resolv.conf" https://%(collector)s/init/rest/api/safe/upload""",
        ]
        data = """
- **file**
. A reference to a path to the local file to upload in the safe.
- **name**
. A symbolic name to identify the file in the safe.
"""
        rest_post_handler.__init__(
          self,
          path="/safe/upload",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, **vars):
        data = lib_safe_upload(**vars)
        _log(
          'safe.upload',
          'file %(uuid)s uploaded.',
          dict(uuid=data.get("uuid", "")),
        )
        ws_send('safe_change')
        return {"data": data}

#
class rest_get_safe(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List files in the collector safe, that the requester is allowed to see.",
        ]
        examples = [
          """# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe""",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/safe",
          tables=["safe"],
          desc=desc,
          groupby=db.safe.id,
          left=db.safe_team_publication.on(db.safe.id == db.safe_team_publication.file_id),
          examples=examples,
        )

    def handler(self, **vars):
        ug = user_groups()
        q = db.safe.id > 0
        if "Manager" not in ug:
            q &= db.safe_team_publication.group_id.belongs(user_group_ids()) | \
                 (db.safe.uploader == auth.user_id)
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_safe_file(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a file in the collector safe, if the requester is allowed to see it.",
        ]
        examples = [
          """# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe/1""",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/safe/<id>",
          tables=["safe"],
          desc=desc,
          groupby=db.safe.id,
          left=db.safe_team_publication.on(db.safe.id == db.safe_team_publication.file_id),
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        if auth_is_node():
            q &= db.safe_team_publication.group_id == auth_node_group_id()
        else:
            ug = user_groups()
            if "Manager" not in ug:
                q &= db.safe_team_publication.group_id.belongs(user_group_ids()) | \
                     (db.safe.uploader == auth.user_id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_safe_file_download(rest_get_handler):
    def __init__(self):
        desc = [
          "Download a file from the collector safe.",
        ]
        examples = [
          """# curl -u %(email)s -o /tmp/foo https://%(collector)s/init/rest/api/safe/1/download""",
        ]
        params = {
            "md5": {
                "desc": "Optional. If set, the client announces the md5 of the "
                        "file content it has a cached version of, and the "
                        "server can return a 204 (no content) status code to "
                        "signal this content is valid.",
            }
        }
        rest_get_handler.__init__(
          self,
          path="/safe/<id>/download",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            uuid = db.safe[id].uuid
        except:
            uuid = str(id)
        data = lib_safe_download(uuid, **vars)
        return data

#
class rest_get_safe_file_preview(rest_get_handler):
    def __init__(self):
        desc = [
          "Preview a file in the collector safe.",
        ]
        examples = [
          """# curl -u %(email)s https://%(collector)s/init/rest/api/safe/1/preview""",
        ]
        rest_get_handler.__init__(
          self,
          path="/safe/<id>/preview",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            uuid = db.safe[id].uuid
        except:
            uuid = str(id)
        data = lib_safe_preview(uuid)
        return data

#
# ACL management
#

#
class rest_post_safe_files_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Share safe files with groups.",
          "Members of the publication groups can list and download the file, and read its properties."
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d group_name="mygroup" https://%(collector)s/init/rest/api/safe/files_publications""",
        ]
        rest_post_handler.__init__(
          self,
          path="/safe/files_publications",
          tables=["safe_team_publication"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "file_id" not in vars:
            raise Exception("The 'file_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_post_safe_file_publication().handler(vars["file_id"], vars["group_id"])

class rest_post_safe_file_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Share a safe file with a group.",
          "Members of the publication groups can list and download the file, and read its properties."
          "The user must be the file uploader or be a member of the file responsible groups.",
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

"""

        examples = [
          """# curl -u %(email)s -o- -X POST -d group_name="mygroup" https://%(collector)s/init/rest/api/safe/1/publications""",
        ]
        rest_post_handler.__init__(
          self,
          path="/safe/<id>/publications/<group>",
          tables=["safe_team_publication"],
          data=data,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, gid, **vars):
        lib_safe_check_file_responsible(id)

        g = lib_get_group(gid)

        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        f = db(q).select().first()
        if f is None:
            raise Exception("File %s not found" % id)

        q = db.safe_team_publication.group_id == g.id
        q &= db.safe_team_publication.file_id == f.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Publication already exists")

        response = db.safe_team_publication.validate_and_insert(
          group_id=g.id,
          file_id=f.id,
        )
        raise_on_error(response)
        row = db(q).select().first()
        _log('safe.publication.create',
             'file %(uuid)s published to group %(group)s.',
             dict(uuid=f.uuid, group=g.role)
            )
        ws_send('safe_team_publication_change')
        return dict(info='File %(uuid)s published to group %(group)s.' % dict(uuid=f.uuid, group=g.role))

#
class rest_post_safe_files_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Share safe files with groups.",
          "Members of the responsible groups can list and download the file, and read its properties."
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/safe/files_responsibles""",
        ]
        rest_post_handler.__init__(
          self,
          path="/safe/files_responsibles",
          tables=["safe_team_responsible"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "file_id" not in vars:
            raise Exception("The 'file_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_post_safe_file_responsible().handler(vars["file_id"], vars["group_id"])

#
class rest_post_safe_file_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Share a safe file with a group.",
          "Members of the responsible groups can list and download the file, and read its properties."
          "The user must be the file uploader or be a member of the file responsible groups.",
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

"""

        examples = [
          """# curl -u %(email)s -o- -X POST -d group_name="mygroup" https://%(collector)s/init/rest/api/safe/1/responsibles""",
        ]
        rest_post_handler.__init__(
          self,
          path="/safe/<id>/responsibles/<group>",
          tables=["safe_team_responsible"],
          data=data,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, gid, **vars):
        lib_safe_check_file_responsible(id)

        g = lib_get_group(gid)

        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        f = db(q).select().first()
        if f is None:
            raise Exception("File %s not found" % id)

        q = db.safe_team_responsible.group_id == g.id
        q &= db.safe_team_responsible.file_id == f.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Responsability already exists")

        response = db.safe_team_responsible.validate_and_insert(
          group_id=g.id,
          file_id=f.id,
        )
        raise_on_error(response)
        row = db(q).select().first()
        _log('safe.responsible.create',
             'file %(uuid)s responsibility added to group %(group)s.',
             dict(uuid=f.uuid, group=g.role)
            )
        ws_send('safe_team_responsible_change')
        return dict(info='File %(uuid)s responsibility added to group %(group)s.' % dict(uuid=f.uuid, group=g.role))

class rest_delete_safe_files_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Mass delete safe files publications.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/safe/files_publications"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe/files_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "file_id" not in vars:
            raise Exception("The 'file_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_delete_safe_file_publication().handler(vars["file_id"], vars["group_id"])

class rest_delete_safe_file_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a safe file publication.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/safe/1/publications/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe/<file>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, gid, **vars):
        lib_safe_check_file_responsible(id)

        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        f = db(q).select().first()

        if f is None:
            raise Exception("File %s not found" % id)

        g = lib_get_group(gid)

        q = db.safe_team_publication.file_id == f.id
        q = db.safe_team_publication.group_id == g.id
        row = db(q).select().first()
        if row is None:
            return dict(info="Publication does not exist")

        db(q).delete()
        _log('safe.publication.delete',
             'file %(uuid)s unpublished to %(group)s',
             dict(uuid=f.uuid, group=g.role),
            )
        ws_send('safe_team_publication_change')
        return dict(info="file %(uuid)s unpublished to %(group)s" % dict(uuid=f.uuid, group=g.role))

class rest_delete_safe_files_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Mass delete safe files responsibles.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/safe/files_responsibles"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe/files_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "file_id" not in vars:
            raise Exception("The 'file_id' key is mandatory")
        if "group_id" not in vars:
            raise Exception("The 'group_id' key is mandatory")
        return rest_delete_safe_file_responsible().handler(vars["file_id"], vars["group_id"])


class rest_delete_safe_file_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a safe file responsible.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/safe/1/responsibles/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe/<file>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, gid, **vars):
        lib_safe_check_file_responsible(id)

        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        f = db(q).select().first()
        if f is None:
            raise Exception("File %s not found" % id)

        g = lib_get_group(gid)

        q = db.safe_team_responsible.file_id == f.id
        q = db.safe_team_responsible.group_id == g.id
        row = db(q).select().first()
        if row is None:
            return dict(info="Publication does not exist")

        db(q).delete()
        _log('safe.responsible.delete',
             'file %(uuid)s responsibility to %(group)s removed',
             dict(uuid=f.uuid, group=g.role),
            )
        ws_send('safe_team_responsible_change')
        return dict(info="file %(uuid)s responsibility to %(group)s removed" % dict(uuid=f.uuid, group=g.role))

#
class rest_get_safe_file_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups allowed to access the safe file.",
        ]
        examples = [
          """# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe/1/publications""",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/safe/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        lib_safe_check_file_publication(id)
        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        q &= db.safe.id == db.safe_team_publication.file_id
        q &= db.safe_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_safe_file_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups allowed to access the safe file.",
        ]
        examples = [
          """# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe/1/responsibles""",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/safe/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        lib_safe_check_file_publication(id)
        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        q &= db.safe.id == db.safe_team_responsible.file_id
        q &= db.safe_team_responsible.group_id == db.auth_group.id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_safe_file_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this safe file.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/safe/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            lib_safe_check_file_responsible(id)
            return dict(data=True)
        except:
            return dict(data=False)

#
class rest_get_safe_file_usage(rest_get_handler):
    def __init__(self):
        desc = [
          "Display a safe file usage.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/safe/10/usage"
        ]
        rest_get_handler.__init__(
          self,
          path="/safe/<id>/usage",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        lib_safe_check_file_publication(id)
        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        row = db(q).select().first()
        if row is None:
            raise HTTP(404, "safe file %s does not exist" % str(id))
        data = {}

        # services
        q = db.services.svc_config.like("%{safe://"+row.uuid+"}%")
        q = q_filter(q, app_field=db.services.svc_app)
        o = db.services.svcname
        i = db.services.svc_id
        rows = db(q).select(o, i, orderby=o, cacheable=False)
        data["services"] = [{"svcname": r[o], "svc_id": r[i]} for r in rows]

        # rules
        ug = user_group_ids()
        q = db.comp_rulesets_variables.var_value.like("%"+row.uuid+"%")
        q &= db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_publication.ruleset_id
        q &= db.comp_ruleset_team_publication.group_id.belongs(ug)
        q &= db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
        o = db.comp_rulesets_variables.var_name
        i = db.comp_rulesets_variables.id
        ro = db.comp_rulesets.ruleset_name
        ri = db.comp_rulesets.id
        rows = db(q).select(o, i, ro, ri, orderby=o, cacheable=False)
        data["variables"] = [{"var_name": r[o], "id": r[i], "ruleset_name": r[ro], "ruleset_id": r[ri]} for r in rows]

        return dict(data=data)

class rest_delete_safe_file(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a safe file.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/safe/1"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        lib_safe_check_file_responsible(id)

        try:
            id = int(id)
            q = db.safe.id == id
        except:
            q = db.safe.uuid == id
        f = db(q).select().first()

        if f is None:
            raise HTTP(404, "File %s not found" % id)

        fpath = os.path.join(db.safe.uuid.uploadfolder, f.uuid)
        if os.path.exists(fpath):
            os.unlink(fpath)

        db(q).delete()
        _log('safe.delete',
             'file %(uuid)s deleted',
             dict(uuid=f.uuid),
            )
        ws_send('safe_change')
        return dict(info="file %(uuid)s deleted" % dict(uuid=f.uuid))

class rest_delete_safe_files(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete multiple safe file.",
          "The user must be the file uploader or be a member of the file responsible groups.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -d id=1 -o- https://%(collector)s/init/rest/api/safe"
        ]
        rest_delete_handler.__init__(
          self,
          path="/safe",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            id = vars["id"]
        elif "uuid" in vars:
            id = vars["uuid"]
        else:
            raise HTTP(400, "The 'uuid' or 'id' key is mandatory")
        return rest_delete_safe_file().handler(id)


