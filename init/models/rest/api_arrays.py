from gluon.dal import smart_query

api_arrays_doc = {}

api_arrays_doc["/arrays/<arrayname>"] = {}
api_arrays_doc["/arrays/<arrayname>"]["GET"] = """
Description:

- Display all array properties.
- Display selected array properties.

Optional parameters:

- **props**
. A list of properties to include.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(arrays_props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray?props=array_name,array_model``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        arrays_props=", ".join(sorted(db.stor_array.fields)),
    )

def get_array(array_name, props=None):
    q = db.stor_array.array_name == array_name
    cols = props_to_cols(props, tables=["stor_array"])
    data = db(q).select(*cols, cacheable=True).first().as_dict()
    return dict(data=data)

api_arrays_doc["/arrays"] = {}
api_arrays_doc["/arrays"]["GET"] = """
Description:

- List storage arrays.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(arrays_props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- "https://%(collector)s/init/rest/api/arrays?props=array_name&query=array_model contains hitachi"``
""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        arrays_props=", ".join(sorted(db.stor_array.fields)),
    )

def get_arrays(props=None, query=None):
    q = db.stor_array.id > 0
    if query:
        cols = props_to_cols(None, tables=["stor_array"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["stor_array"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)

api_arrays_doc["/arrays/<arrayname>/diskgroups"] = {}
api_arrays_doc["/arrays/<arrayname>/diskgroups"]["GET"] = """
Description:

- Display array diskgroups.

Optional parameters:

- **props**
. A list of properties to include.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(arrays_diskgroups_props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        arrays_diskgroups_props=", ".join(sorted(db.stor_array_dg.fields)),
    )


def get_array_dgs(array_name, props=None, query=None):
    q = db.stor_array.array_name == array_name
    array_id = db(q).select(db.stor_array.id).first().id
    q = db.stor_array_dg.array_id == array_id
    if query:
        cols = props_to_cols(None, tables=["stor_array_dg"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["stor_array_dg"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)

api_arrays_doc["/arrays/<arrayname>/proxies"] = {}
api_arrays_doc["/arrays/<arrayname>/proxies"]["GET"] = """
Description:

- Display array proxies.
- Proxies are OpenSVC agent inventoring the array.

Optional parameters:

- **props**
. A list of properties to include.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(arrays_proxies_props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        arrays_proxies_props=", ".join(sorted(db.stor_array_proxy.fields)),
    )

def get_array_proxies(array_name, props=None, query=None):
    q = db.stor_array.array_name == array_name
    array_id = db(q).select(db.stor_array.id).first().id
    q = db.stor_array_proxy.array_id == array_id
    if query:
        cols = props_to_cols(None, tables=["stor_array_proxy"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["stor_array_proxy"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)

api_arrays_doc["/arrays/<arrayname>/targets"] = {}
api_arrays_doc["/arrays/<arrayname>/targets"]["GET"] = """
Description:

- Display array target ports.

Optional parameters:

- **props**
. A list of properties to include.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/targets``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.stor_array_tgtid.fields)),
    )

def get_array_targets(array_name, props=None, query=None):
    q = db.stor_array.array_name == array_name
    array_id = db(q).select(db.stor_array.id).first().id
    q = db.stor_array_tgtid.array_id == array_id
    if query:
        cols = props_to_cols(None, tables=["stor_array_tgtid"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["stor_array_tgtid"])
    rows = db(q).select(*cols, cacheable=True)
    data = [r.as_dict() for r in rows]
    return dict(data=data)


