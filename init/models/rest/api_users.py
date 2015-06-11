from gluon.dal import smart_query

api_users_doc = {}

api_users_doc["/users"] = """
### GET

Description:

- List existing users
- Managers and UserManager are allowed to see all users
- Others can only see users in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users?query=email contains opensvc``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(set(db.auth_user.fields)-set(["password", "registration_key"]))),
      )

def allowed_user_ids():
    q = db.auth_membership.group_id.belongs(user_group_ids())
    rows = db(q).select(db.auth_membership.user_id)
    return [r.user_id for r in rows]

def get_users(props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)
    if query:
        cols = props_to_cols(None, tables=["auth_user"], blacklist=["password", "registration_key"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["auth_user"], blacklist=["password", "registration_key"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_users_doc["/users/<id>"] = """
### GET

Description:

- Display user property
- Managers and UserManager are allowed to see all users
- Others can only see users in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s?props=primary_group``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(set(db.auth_user.fields)-set(["password", "registration_key"]))),
      )

def get_user(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)

    if "@" in id:
        q &= db.auth_user.email == id
    else:
        q &= db.auth_user.id == id

    if query:
        cols = props_to_cols(None, tables=["auth_user"], blacklist=["password", "registration_key"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["auth_user"], blacklist=["password", "registration_key"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_users_doc["/users/<id>/apps"] = """
### GET

Description:

- Display apps the user is responsible for
- Managers and UserManager are allowed to see all users' information
- Others can only see information for users in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/apps``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.apps.fields)),
      )

def get_user_apps(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)

    if "@" in id:
        q &= db.auth_user.email == id
    else:
        q &= db.auth_user.id == id

    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    q &= db.auth_membership.user_id == db.auth_user.id
    q &= db.apps.id == db.apps_responsibles.app_id
    if query:
        cols = props_to_cols(None, tables=["apps"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["apps"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_users_doc["/users/<id>/nodes"] = """
### GET

Description:

- Display nodes the user is responsible for
- Managers and UserManager are allowed to see all users' information
- Others can only see information for users in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/nodes``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_user_nodes(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)

    if "@" in id:
        q &= db.auth_user.email == id
    else:
        q &= db.auth_user.id == id

    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.auth_membership.group_id
    q &= db.auth_membership.user_id == db.auth_user.id
    if query:
        cols = props_to_cols(None, tables=["nodes"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["nodes"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_users_doc["/users/<id>/services"] = """
### GET

Description:

- Display services the user is responsible for
- Managers and UserManager are allowed to see all users' information
- Others can only see information for users in their organisational groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/users/%(email)s/services``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_user_services(id, props=None, query=None):
    try:
        check_privilege("UserManager")
        q = db.auth_user.id > 0
    except:
        user_ids = allowed_user_ids()
        q = db.auth_user.id.belongs(user_ids)

    if "@" in id:
        q &= db.auth_user.email == id
    else:
        q &= db.auth_user.id == id

    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    q &= db.auth_membership.user_id == db.auth_user.id
    if query:
        cols = props_to_cols(None, tables=["services"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["services"])
    data = db(q).select(*cols, cacheable=True, groupby=db.services.id).as_list()
    return dict(data=data)


