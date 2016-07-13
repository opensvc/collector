import yaml
import datetime
from hashlib import md5


def mangle_form_data(data):
    for i, row in enumerate(data):
        try:
            data[i]["form_definition"] = yaml.load(data[i]["form_yaml"])
        except:
            pass
    return data
class rest_get_workflows(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List workflows.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/workflows"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/workflows",
          tables=["workflows"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.workflows.id > 0
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data



class rest_get_workflow_dump(rest_get_handler):
    def __init__(self):
        desc = [
          "Dump full workflow <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/workflows/1/dump"
        ]

        rest_get_handler.__init__(
          self,
          path="/workflows/<id>/dump",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        data = rest_get_workflow().handler(id)
        if "data" not in data or len(data["data"]) == 0:
            return data
        data["data"][0]["head"] = rest_get_store_form().handler(data["data"][0]["form_head_id"])["data"][0]
        data["data"][0]["tail"] = rest_get_store_form().handler(data["data"][0]["last_form_id"])["data"][0]
        return data


class rest_get_workflow(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List workflow <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/workflows/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/workflows/<id>",
          tables=["workflows"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.workflows.id == int(id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


class rest_get_store_forms(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List forms stored for workflows.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms_store"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/forms_store",
          tables=["v_forms_store"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.v_forms_store.id > 0
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


class rest_get_store_form(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a form stored for a workflow properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms_store/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/forms_store/<id>",
          tables=["v_forms_store"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_forms_store.id == int(id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_get_store_form_dump(rest_get_handler):
    def __init__(self):
        desc = [
          "List a form stored for a workflow properties and its workflow properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms_store/1/dump"
        ]

        rest_get_handler.__init__(
          self,
          path="/forms_store/<id>/dump",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        data = rest_get_store_form().handler(id)
        form_head_id = data["data"][0]["form_head_id"]
        q = db.workflows.form_head_id == form_head_id
        wf_id = db(q).select(db.workflows.id).first().id
        data["data"][0]["workflow"] = rest_get_workflow_dump().handler(wf_id)["data"][0]
        return data


class rest_get_forms_revisions(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List forms revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms_revisions"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/forms_revisions",
          tables=["forms_revisions"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.forms_revisions.id > 0
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


class rest_get_forms_revision(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List a form revision properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms_revisions/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/forms_revisions/<id>",
          tables=["forms_revisions"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            q = db.forms_revisions.id == int(id)
        except:
            q = db.forms_revisions.form_md5 == id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data





