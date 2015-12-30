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
        q = db.forms_revisions.id == int(id)
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data





