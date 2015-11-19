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
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.forms.id > 0
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
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms?query=form_name contains dns"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/forms/<id>",
          tables=["forms"],
          vprops={"form_definition": ["form_yaml"]},
          vprops_fn=mangle_form_data,
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.forms.id == int(id)
        q &= db.forms.id == db.forms_team_publication.form_id
        q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data


#
class rest_put_form(rest_put_handler):
    def __init__(self):
        desc = [
          "Submit form <id>.",
        ]
        data = """
- **data**
. The information the form expects
. The information data type is given by the 'Outputs[].Format' property if the
form definition
. The key names and constraints are available in the Inputs section of the form
defintion.
"""
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

    def handler(self, form_id, data=None):
        q = db.forms.id == form_id
        q &= db.forms.id == db.forms_team_publication.form_id
        q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        form = db(q).select(db.forms.ALL).first()
        if form is None:
            return dict("error", "the requested form does not exist or you don't have permission to use it")

        form_data = json.loads(data)

        import yaml
        data = yaml.load(form.form_yaml)

        log = form_submit(form, data, form_data)
        infos = []
        errors = []
        for lvl, action, fmt, d in log:
            msg = fmt % d
            if lvl == 0:
                infos.append(msg)
            else:
                errors.append(msg)
        return dict(info=infos, error=errors)



