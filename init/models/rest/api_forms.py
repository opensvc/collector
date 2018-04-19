import yaml
import datetime
from hashlib import md5

def form_responsible(id):
    if "Manager" in user_groups():
        return
    q = db.forms.id == id
    q &= db.forms.id == db.forms_team_responsible.form_id
    q &= db.forms_team_responsible.group_id.belongs(user_group_ids())
    form = db(q).select(db.forms.id).first()
    if form is None:
        raise HTTP(404, "Form %s not found or you are not responsible" % str(id))

def form_published(id):
    if "Manager" in user_groups():
        return
    q = db.forms.id == id
    q &= db.forms.id == db.forms_team_publication.form_id
    q &= db.forms_team_publication.group_id.belongs(user_group_ids())
    form = db(q).select(db.forms.id).first()
    if form is None:
        raise HTTP(404, "Form %s not found or not published to you" % str(id))

def mangle_form_data(data):
    for i, row in enumerate(data):
        try:
            data[i]["form_definition"] = yaml.load(data[i]["form_yaml"])
        except:
            pass
    return data


class rest_post_form(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a form properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d form_name=test -o- https://%(collector)s/init/rest/api/forms/1"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms/<id>",
          tables=["forms"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("FormsManager")

        if "id" in vars:
            del(vars["id"])

        q = db.forms.id == id
        form = db(q).select().first()
        if form is None:
            raise HTTP(404, "Form %s not found"%str(id))

        if "form_definition" in vars:
            try:
                form_definition = json.loads(vars["form_definition"])
                vars["form_yaml"] = yaml.dump(form_definition)
                del(vars["form_definition"])
            except Exception as e:
                pass
        elif "form_yaml" in vars:
            form_yaml = yaml.load(vars["form_yaml"])

        form_id = db(q).update(**vars)
        table_modified("forms")

        fmt = "Form %(form_name)s change: %(data)s"
        d = dict(form_name=form.form_name, data=beautify_change(form, vars))

        _log('form.change', fmt, d)
        ws_send('forms_change', {'id': form.id})

        ret = rest_get_form().handler(form.id)
        if "form_definition" in ret["data"][0]:
            content = yaml.dump(ret["data"][0]["form_definition"], default_flow_style=False)
        else:
            content = ""
        lib_form_add_to_git(id, content)
        ret["info"] = fmt % d
        self.cache_clear(["rest_get_forms"])
        return ret

class rest_post_forms(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create forms",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d form_name=test -o- https://%(collector)s/init/rest/api/forms"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms",
          tables=["forms"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("FormsManager")

        if "form_name" not in vars:
            raise HTTP(400, "Key 'form_name' is mandatory")
        form_name = vars.get("form_name")

        vars["form_created"] = datetime.datetime.now()
        vars["form_author"] = user_name()

        form_id = db.forms.insert(**vars)
        ws_send('forms_change', {'id': form_id})
        table_modified("forms")

        lib_forms_add_default_team_responsible(form_name)
        ws_send('forms_team_responsible_change', {'form_id': form_id})

        lib_forms_add_default_team_publication(form_name)
        ws_send('forms_team_publication_change', {'form_id': form_id})

        fmt = "Form %(form_name)s added"
        d = dict(form_name=form_name)

        _log('form.add', fmt, d)
        self.cache_clear(["rest_get_forms"])

        return rest_get_form().handler(form_id)

class rest_get_forms(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List available forms.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms?query=form_name contains dns"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/forms",
          tables=["forms"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          groupby=db.forms.id,
          desc=desc,
          examples=examples,
          _cache=True,
        )

    def handler(self, **vars):
        q = db.forms.id > 0
        if "Manager" not in user_groups():
            q &= db.forms.id == db.forms_team_publication.form_id
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_get_form(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List form <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/forms/<id>",
          tables=["forms"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          groupby=db.forms.id,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.forms.id == int(id)
        if "Manager" not in user_groups():
            q &= db.forms.id == db.forms_team_publication.form_id
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_get_form_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups the form is published to.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/forms/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        form_published(id)
        q = db.forms_team_publication.form_id == id
        q &= db.forms_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_form_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unpublish the form to a group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, group_id, **vars):
        check_privilege("FormsManager")
        form_responsible(form_id)
        q = db.forms_team_publication.form_id == form_id
        q &= db.forms_team_publication.group_id == group_id

        fmt = "Form %(form_id)s unpublished to group %(group_id)s"
        d = dict(form_id=str(form_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Form %(form_id)s already unpublished to group %(group_id)s" % d)

        db(q).delete()

        table_modified("forms_team_publication")
        _log('form.publication.delete', fmt, d)
        ws_send('forms_team_publication_change', {'form_id': form_id, 'group_id': group_id})
        self.cache_clear(["rest_get_forms"])
        return dict(info=fmt%d)

class rest_delete_forms_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unpublish the forms to groups",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms_publications?filters[]="form_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "form_id" in vars:
            raise HTTP(400, "The 'form_id' key is mandatory")
        form_id = vars.get("form_id")
        del(vars["form_id"])

        if not "group_id" in vars:
            raise HTTP(400, "The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_form_publication().handler(form_id, group_id, **vars)

class rest_post_form_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Publish the form to a group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/forms/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, group_id, **vars):
        check_privilege("FormsManager")
        form_responsible(form_id)
        group = lib_org_group(group_id)

        fmt = "Form %(form_id)s published to group %(role)s"
        d = dict(form_id=str(form_id), role=str(group.role))

        q = db.forms_team_publication.form_id == form_id
        q &= db.forms_team_publication.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Form %(form_id)s already published to group %(role)s" % d)

        db.forms_team_publication.insert(form_id=form_id, group_id=group.id)

        table_modified("forms_team_publication")
        _log('form.publication.add', fmt, d)
        ws_send('forms_team_publication_change', {'form_id': form_id, 'group_id': group.id})

        self.cache_clear(["rest_get_forms"])
        return dict(info=fmt%d)

class rest_post_forms_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Publish the forms to groups",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/forms_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "form_id" in vars:
            raise HTTP(400, "The 'form_id' key is mandatory")
        form_id = vars.get("form_id")
        del(vars["form_id"])

        if not "group_id" in vars:
            raise HTTP(400, "The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_form_publication().handler(form_id, group_id, **vars)


class rest_get_form_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups responsible for the form.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/responsibles"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/forms/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        form_published(id)
        q = db.forms_team_responsible.form_id == id
        q &= db.forms_team_responsible.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_get_form_revisions(rest_get_handler):
    def __init__(self):
        desc = [
          "- return form revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/revisions",
        ]
        rest_get_handler.__init__(
          self,
          path="/forms/<id>/revisions",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, **vars):
        r = []
        q = db.forms.id == int(form_id)
        if "Manager" not in user_groups():
            q &= db.forms.id == db.forms_team_publication.form_id
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_form_revisions(form_id)
        return r

class rest_get_form_revision(rest_get_handler):
    def __init__(self):
        desc = [
          "return form content for a specific revision",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/revisions/1234",
        ]
        rest_get_handler.__init__(
          self,
          path="/forms/<id>/revisions/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, cid, **vars):
        r = []
        q = db.forms.id == int(form_id)
        if "Manager" not in user_groups():
            q &= db.forms.id == db.forms_team_publication.form_id
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_form_revision(form_id, cid)
        return r

class rest_get_form_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "Show the commit diff, or differences between <cid> and <other> if"
          "other is set",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/diff/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710",
        ]
        rest_get_handler.__init__(
          self,
          path="/forms/<id>/diff/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, cid, other=None, **vars):
        r = []
        q = db.forms.id == int(form_id)
        if "Manager" not in user_groups():
            q &= db.forms.id == db.forms_team_publication.form_id
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r = lib_form_diff(form_id, cid, other)
        return r

class rest_delete_form_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a form responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms/1/responsibles/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, group_id, **vars):
        check_privilege("FormsManager")
        form_responsible(form_id)
        q = db.forms_team_responsible.form_id == form_id
        q &= db.forms_team_responsible.group_id == group_id

        fmt = "Form %(form_id)s responsibility to group %(group_id)s removed"
        d = dict(form_id=str(form_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Form %(form_id)s responsibility to group %(group_id)s already removed" % d)

        db(q).delete()

        table_modified("forms_team_responsible")
        _log('form.responsible.delete', fmt, d)
        ws_send('forms_team_responsible_change', {'form_id': form_id, 'group_id': group_id})
        self.cache_clear(["rest_get_forms"])

        return dict(info=fmt%d)

class rest_delete_forms_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove responsible groups from the forms",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms_responsibles?filters[]="form_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "form_id" in vars:
            raise HTTP(400, "The 'form_id' key is mandatory")
        form_id = vars.get("form_id")
        del(vars["form_id"])

        if not "group_id" in vars:
            raise HTTP(400, "The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_form_responsible().handler(form_id, group_id, **vars)

class rest_post_form_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a form responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/forms/1/responsibles/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, group_id, **vars):
        check_privilege("FormsManager")
        form_responsible(form_id)
        group = lib_org_group(group_id)

        fmt = "Form %(form_id)s responsibility to group %(role)s added"
        d = dict(form_id=str(form_id), role=str(group.role))

        q = db.forms_team_responsible.form_id == form_id
        q &= db.forms_team_responsible.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Form %(form_id)s responsibility to group %(role)s already added" % d)

        db.forms_team_responsible.insert(form_id=form_id, group_id=group.id)

        table_modified("forms_team_responsible")
        _log('form.responsible.add', fmt, d)
        ws_send('forms_team_responsible_change', {'form_id': form_id, 'group_id': group.id})
        self.cache_clear(["rest_get_forms"])

        return dict(info=fmt%d)

class rest_post_forms_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Add responsible groups to forms",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/forms_responsibles"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "form_id" in vars:
            raise HTTP(400, "The 'form_id' key is mandatory")
        form_id = vars.get("form_id")
        del(vars["form_id"])

        if not "group_id" in vars:
            raise HTTP(400, "The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_form_responsible().handler(form_id, group_id, **vars)

class rest_post_form_rollback(rest_post_handler):
    def __init__(self):
        desc = [
          "Restore an old revision of a form",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/forms/1/rollback/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710"
        ]

        rest_post_handler.__init__(
          self,
          path="/forms/<id>/rollback/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, cid, **vars):
        check_privilege("FormsManager")
        form_responsible(form_id)
        lib_form_rollback(form_id, cid)
        return

#
class rest_put_form(rest_put_handler):
    def __init__(self):
        desc = [
          "Submit form <id>.",
        ]
        data = {
          "data": {
             "desc": """The information the form expects. The information data type is given by the 'Outputs[].Format' property if the form definition. The key names and constraints are available in the Inputs section of the form defintion."""
          },
          "prev_wfid": {
            "desc": "The previous step id in an existing workflow"
          },
        }
        examples = [
          """# curl -u %(email)s -d data='{"nodename": "foooo"}' -X PUT -o- https://%(collector)s/init/rest/api/forms/10"""
        ]

        rest_put_handler.__init__(
          self,
          path="/forms/<id>",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, form_id, data=None, prev_wfid=None):
        form_id = int(form_id)
        if form_id < 0:
            # internal form
            form = get_internal_form(form_id)
        else:
            q = db.forms.id == form_id

            if "Manager" not in user_groups():
                q &= (db.forms.id == db.forms_team_publication.form_id)
                q &= db.forms_team_publication.group_id.belongs(user_group_ids())

            form = db(q).select(db.forms.ALL, cacheable=True).first()

        if form is None:
            raise HTTP(404, "the requested form does not exist or you don't have permission to use it")

        try:
            form_data = json.loads(data)
        except ValueError:
            raise HTTP(400, "unparsable form data: " + str(data))

        return form_submit(form, _d=form_data, prev_wfid=prev_wfid)


class rest_delete_form(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a form",
          "Delete also the form publications and responsibles",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("FormsManager")
        form_responsible(id)

        q = db.forms.id == id
        row = db(q).select().first()
        if row is None:
            raise HTTP(404, "Form %s not found"%str(id))

        form_id = db(q).delete()
        table_modified("forms")
        ws_send('forms_delete', {'id': id})

        q = db.forms_team_publication.form_id == id
        db(q).delete()
        ws_send('forms_team_publication_change', {'form_id': id})

        q = db.forms_team_responsible.form_id == id
        db(q).delete()
        ws_send('forms_team_responsible_change', {'form_id': id})

        fmt = "Form %(form_name)s deleted"
        d = dict(form_name=row.form_name)

        _log('form.del', fmt, d)

        return dict(info=fmt%d)

class rest_delete_forms(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete forms",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/forms"
        ]

        rest_delete_handler.__init__(
          self,
          path="/forms",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not 'id' in vars:
            raise HTTP(400, "The 'id' key is mandatory")

        form_id = vars["id"]
        del(vars["id"])
        return rest_delete_form().handler(form_id, **vars)

#
class rest_get_form_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this form.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/forms/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, form_id, **vars):
        try:
            form_responsible(form_id)
            return dict(data=True)
        except:
            return dict(data=False)

#
class rest_get_form_output_result(rest_get_handler):
    def __init__(self):
        desc = [
          "Show a submited form results properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/form_output_results/1"
        ]

        rest_get_handler.__init__(
          self,
          path="/form_output_results/<id>",
          tables=["form_output_results"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.form_output_results.id == int(id)
        q = q_filter(
            q,
            user_field=db.form_output_results.user_id,
            node_field=db.form_output_results.node_id,
            svc_field=db.form_output_results.svc_id,
        )
        row = db(q).select().first()
        if row is None:
            raise HTTP(404, "results not found")
        return json.loads(row.results)

#
class rest_put_form_output_result(rest_put_handler):
    def __init__(self):
        desc = [
          "Add the <output_id> result to the results structure.",
        ]
        data = {
          "result": {
              "desc": """The result to add for <output_id>"""
          },
          "output_id": {
              "desc": "The id of the form output for which to store the result"
          },
        }
        examples = [
          """# curl -u %(email)s -d output_id="add disk" --result='{"lun": 1}' -X PUT -o- https://%(collector)s/init/rest/api/form_output_results/10"""
        ]

        rest_put_handler.__init__(
          self,
          path="/form_output_results/<id>",
          desc=desc,
          data=data,
          examples=examples,
        )

    def handler(self, results_id, output_id=None, result=None):
        results = rest_get_form_output_result().handler(results_id)
        if output_id not in results["outputs"]:
	    results["outputs"][output_id] = []
        import gluon.contrib.simplejson as sjson
        try:
            results["outputs"][output_id] += [sjson.loads(result)]
        except TypeError:
            results["outputs"][output_id] += [result]
        s_results = sjson.dumps(results, default=datetime.datetime.isoformat)

        q = db.form_output_results.id == int(results_id)
        db(q).update(results=s_results)
        db.commit()
        ws_send("form_output_results_change", {
            "results_id": results_id
        })
        return results


