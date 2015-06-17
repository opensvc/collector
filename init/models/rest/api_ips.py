from gluon.dal import smart_query

api_ips_doc = {}

#
api_ips_doc["/ips"] = {}
api_ips_doc["/ips"]["GET"] = """
Description:

- List ips detected on nodes.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/ips``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(list((set(db.v_nodenetworks.fields)-set(db.nodes.fields))|set(["nodename"])))),
      )

def get_ips(props=None, query=None):
    import copy
    bl_fields = copy.copy(db.nodes.fields)
    bl_fields.remove("nodename")
    q = db.v_nodenetworks.id > 0
    q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, tables=["v_nodenetworks"], blacklist=bl_fields)
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["v_nodenetworks"], blacklist=bl_fields)
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)



#
api_ips_doc["/ips/<id>"] = {}
api_ips_doc["/ips/<id>"]["GET"] = """
Description:

- Display a node ip properties.
- <id> can be either the proper id or the ip addr

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/ips/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(list((set(db.v_nodenetworks.fields)-set(db.nodes.fields))|set(["nodename"])))),
      )

def get_ip(id, props=None, query=None):
    import copy
    bl_fields = copy.copy(db.nodes.fields)
    if "." in id or ":" in id:
        q = db.v_nodenetworks.addr == id
    else:
        q = db.v_nodenetworks.id == id
    q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, tables=["v_nodenetworks"], blacklist=bl_fields)
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["v_nodenetworks"], blacklist=bl_fields)
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


