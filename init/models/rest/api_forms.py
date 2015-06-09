from gluon.dal import smart_query
import yaml
import datetime
from hashlib import md5


api_forms_doc = {}

api_filtersets_doc["/forms"] = """
### GET

Description:

- List available forms.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms?query=form_name contains dns``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.forms.fields)),
      )

def get_forms(props=None, query=None):
    q = db.forms.id > 0
    q &= db.forms.id == db.forms_team_publication.form_id
    q &= db.forms_team_publication.group_id.belongs(user_group_ids())
    if query:
        cols = props_to_cols(None, tables=["forms"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["forms"])
    data = db(q).select(*cols, cacheable=True).as_list()
    for i, row in enumerate(data):
        try:
            data[i]["form_definiton"] = yaml.load(data[i]["form_yaml"])
            del(data[i]["form_yaml"])
        except:
            pass
    return dict(data=data)



api_filtersets_doc["/forms/<id>"] = """
### GET

Description:

- List form <id> properties.

Optional parameters:

- **props**
. A list of properties to include.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/forms?query=form_name contains dns``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.forms.fields)),
      )

def get_form(form_id, props=None, query=None):
    q = db.forms.id == form_id
    q &= db.forms.id == db.forms_team_publication.form_id
    q &= db.forms_team_publication.group_id.belongs(user_group_ids())
    if query:
        cols = props_to_cols(None, tables=["forms"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["forms"])
    data = db(q).select(*cols, cacheable=True).as_list()
    for i, row in enumerate(data):
        try:
            data[i]["form_definiton"] = yaml.load(data[i]["form_yaml"])
            del(data[i]["form_yaml"])
        except:
            pass
    return dict(data=data)


api_filtersets_doc["/forms/<id>"] = """
### PUT

Description:

- Submit form <id>.

Optional parameters:

- **data**
. The information the form expects
. The information data type is given by the 'Outputs[].Format' property if the
form definition
. The key names and constraints are available in the Inputs section of the form
defintion.

Example:

``# curl -u %(email)s -d "[{"foo": "bar"}]" -o- https://%(collector)s/init/rest/api/forms/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.forms.fields)),
      )

def put_form(form_id, data=None):
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



