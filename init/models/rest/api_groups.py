from gluon.dal import smart_query

api_groups_doc = {}

api_groups_doc["/groups"] = {}
api_groups_doc["/groups"]["GET"] = """
Description:

- List existing groups
- Managers and UserManager are allowed to see all groups
- Others can only see their groups

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

api_groups_doc["/groups/<id>"] = {}
api_groups_doc["/groups/<id>"]["GET"] = """
Description:

- Display group property
- Managers and UserManager are allowed to see all groups
- Others can only see their groups

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


api_groups_doc["/groups/<id>/apps"] = {}
api_groups_doc["/groups/<id>/apps"]["GET"] = """
Description:

- Display apps the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see their groups

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

api_groups_doc["/groups/<id>/nodes"] = {}
api_groups_doc["/groups/<id>/nodes"]["GET"] = """
Description:

- Display nodes the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see their groups

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

api_groups_doc["/groups/<id>/services"] = {}
api_groups_doc["/groups/<id>/services"]["GET"] = """
Description:

- Display services the group is responsible for
- Managers and UserManager are allowed to see all groups' information
- Others can only see their groups

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

api_groups_doc["/groups/<id>/users"] = {}
api_groups_doc["/groups/<id>/users"]["GET"] = """
Description:

- Display users member of the specified group
- Managers and UserManager are allowed to see all groups' information
- Others can only see their groups

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/groups/%(email)s/users``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.auth_user.fields)),
      )

def get_group_users(id, props=None, query=None):
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

    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_user.id == db.auth_membership.user_id
    if query:
        cols = props_to_cols(None, tables=["auth_user"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["auth_user"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_groups_doc["/groups"]["POST"] = """
Description:

- Create a group.
- The user must be in the UserManager privilege group
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the groups table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d role=NodeManager -d privilege=T https://%(collector)s/init/rest/api/groups``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.auth_group.fields)),
      )

def add_group(**vars):
    check_privilege("UserManager")
    db.auth_group.insert(**vars)
    _log('rest.groups.add',
         'add group %(data)s',
         dict(data=str(vars)),
        )
    l = {
      'event': 'auth_group',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    return get_group(vars["role"])


#
api_groups_doc["/groups/<id>"]["POST"] = """
Description:

- Modify a group properties.
- The user must be in the UserManager privilege group
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the groups table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -d privilege=T https://%(collector)s/init/rest/api/groups/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.auth_group.fields)),
      )

def set_group(id, **vars):
    check_privilege("UserManager")
    try:
        id = int(id)
        q = db.auth_group.id == id
    except:
        q = db.auth_group.role == id
    row = db(q).select().first()
    if row is None:
        return dict(error="Group %s does not exist" % id)
    if "id" in vars.keys():
        del(vars["id"])
    db(q).update(**vars)
    l = []
    for key in vars:
        l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))

    _log('rest.groups.change',
         'change group %(data)s',
         dict(data=', '.join(l)),
        )
    l = {
      'event': 'auth_group',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    return get_group(row.id)


#
api_groups_doc["/groups"]["DELETE"] = """
Description:

- Delete a group.
- Delete all group membership, apps/forms/rulesets/modulesets responsabilities
  and publications
- The user must be in the UserManager privilege group
- The action is logged in the collector's log.
- A websocket event is sent to announce the change in the changed tables.

Example:

``# curl -u %(email)s -o- -d role=NodeManager -d privilege=T https://%(collector)s/init/rest/api/groups``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_group(id):
    check_privilege("UserManager")
    try:
        id = int(id)
        q = db.auth_group.id == id
    except:
        q = db.auth_group.role == id

    row = db(q).select().first()
    if row is None:
        return dict(info="Group %s does not exists" % str(id))

    # group
    db(q).delete()
    _log('rest.groups.delete',
         'deleted group %(g)s',
         dict(g=row.role))
    l = {
      'event': 'auth_group',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

    # apps responsibles
    q = db.apps_responsibles.group_id == row.id
    db(q).delete()

    # forms responsibles and publication
    q = db.forms_team_responsible.group_id == row.id
    db(q).delete()
    q = db.forms_team_publication.group_id == row.id
    db(q).delete()

    # modset responsibles
    q = db.comp_moduleset_team_responsible.group_id == row.id
    db(q).delete()

    # ruleset responsibles
    q = db.comp_ruleset_team_responsible.group_id == row.id
    db(q).delete()

    return dict(info="Group %s deleted" % row.role)

