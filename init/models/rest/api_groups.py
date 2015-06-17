from gluon.dal import smart_query

api_groups_doc = {}

api_groups_doc["/groups"] = """
### GET

Description:

- List existing groups
- Managers and UserManager are allowed to see all groups
- Others can only their groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups?query=email contains opensvc``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(set(db.auth_group.fields)-set(["password", "registration_key"]))),
      )

def get_groups(props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_group.id > 0
    except:
        q = db.auth_group.id.belongs(user_group_ids())
    if query:
        cols = props_to_cols(None, tables=["auth_group"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["auth_group"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_groups_doc["/groups/<id>"] = """
### GET

Description:

- Display group property
- Managers and UserManager are allowed to see all groups
- Others can only see groups in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s?props=primary_group``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(set(db.auth_group.fields)-set(["password", "registration_key"]))),
      )

def get_group(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_group.id > 0
    except:
        q = db.auth_group.id.belongs(user_group_ids())

    try:
        id = int(id)
        q &= db.auth_group.id == id
    except:
        q &= db.auth_group.role == id

    if query:
        cols = props_to_cols(None, tables=["auth_group"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["auth_group"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_groups_doc["/groups/<id>/apps"] = """
### GET

Description:

- Display apps the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see information for groups in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/apps``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.apps.fields)),
      )

def get_group_apps(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_group.id > 0
    except:
        q = db.auth_group.id.belongs(user_group_ids())

    try:
        id = int(id)
        q &= db.auth_group.id == id
    except:
        q &= db.auth_group.role == id

    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.apps.id == db.apps_responsibles.app_id
    if query:
        cols = props_to_cols(None, tables=["apps"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["apps"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_groups_doc["/groups/<id>/nodes"] = """
### GET

Description:

- Display nodes the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see information for groups in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/nodes``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_group_nodes(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_group.id > 0
    except:
        q = db.auth_group.id.belongs(user_group_ids())

    try:
        id = int(id)
        q &= db.auth_group.id == id
    except:
        q &= db.auth_group.role == id

    q &= db.nodes.team_responsible == db.auth_group.role
    if query:
        cols = props_to_cols(None, tables=["nodes"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["nodes"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_groups_doc["/groups/<id>/services"] = """
### GET

Description:

- Display services the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see information for groups in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/services``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_group_services(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_group.id > 0
    except:
        q = db.auth_group.id.belongs(user_group_ids())

    try:
        id = int(id)
        q &= db.auth_group.id == id
    except:
        q &= db.auth_group.role == id

    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    if query:
        cols = props_to_cols(None, tables=["services"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["services"])
    data = db(q).select(*cols, cacheable=True, groupby=db.services.id).as_list()
    return dict(data=data)


