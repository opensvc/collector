from gluon.dal import smart_query

api_filtersets_doc = {}

api_filtersets_doc["/filtersets"] = """
### GET

Description:

- List all existing filtersets.
- List the existing filtersets matching a pattern.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(filtersets_props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets?like=%%aix%%``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        filtersets_props=", ".join(sorted(db.gen_filtersets.fields)),
      )

def get_filtersets(props=None, query=None):
    q = db.gen_filtersets.id > 0
    if query:
        cols = props_to_cols(None, tables=["gen_filtersets"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["gen_filtersets"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


