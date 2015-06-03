from gluon.dal import smart_query

api_apps_doc = {}

#
api_apps_doc["/apps"] = """
### GET

Description:

- List application codes.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.apps.fields)),
      )

def get_apps(props=None, query=None):
    q = db.apps.id > 0
    if query:
        cols = props_to_cols(None, tables=["apps"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["apps"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)



#
api_apps_doc["/apps/<id>"] = """
### GET

Description:

- Display an application code properties.
- <id> can be either the proper id or the application code.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/10``
``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.apps.fields)),
      )

def get_app(id, props=None, query=None):
    q = db.apps.app == id
    n = db(q).count()
    if n == 0:
        try: int(id)
        except: return dict(data=[])
        q = db.apps.id == id
    if query:
        cols = props_to_cols(None, tables=["apps"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["apps"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_apps_doc["/apps/<id>/nodes"] = """
### GET

Description:

- List nodes with the <id> application codes.
- <id> can be either the proper id or the application code.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/nodes``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_app_nodes(id, props=None, query=None):
    q = db.apps.app == id
    n = db(q).count()
    if n == 0:
        try: int(id)
        except: return dict(data=[])
        q = db.apps.id == id
    q &= db.nodes.project == db.apps.app
    if query:
        cols = props_to_cols(None, tables=["nodes"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["nodes"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

#
api_apps_doc["/apps/<id>/services"] = """
### GET

Description:

- List services with the <id> application codes.
- <id> can be either the proper id or the application code.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/apps/MYAPP/services``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.services.fields)),
      )

def get_app_services(id, props=None, query=None):
    q = db.apps.app == id
    n = db(q).count()
    if n == 0:
        try: int(id)
        except: return dict(data=[])
        q = db.apps.id == id
    q &= db.services.svc_app == db.apps.app
    if query:
        cols = props_to_cols(None, tables=["services"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["services"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


