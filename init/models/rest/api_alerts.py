from gluon.dal import smart_query
import json

api_alerts_doc = {}


#
api_alerts_doc["/alerts"] = """
### GET

Description:

- List existing alerts.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alerts?query=not dash_type contains save``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.dashboard.fields)),
      )

def mangle_alerts(data):
    for i, row in enumerate(data):
        try:
            data[i]['dash_dict'] = json.loads(data[i]['dash_dict'])
            data[i]['alert'] = data[i]['dash_fmt'] % data[i]['dash_dict']
        except:
            pass
    return data

def get_alerts(props=None, query=None):
    q = db.dashboard.id > 0
    if query:
        cols = props_to_cols(None, tables=["dashboard"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["dashboard"])
    data = db(q).select(*cols, cacheable=True).as_list()
    data = mangle_alerts(data)
    return dict(data=data)


api_alerts_doc["/alerts/<id>"] = """
### GET

Description:

- Display alert properties

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alerts/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.dashboard.fields)),
      )

def get_alert(tagid, props=None):
    q = db.dashboard.id == int(tagid)
    cols = props_to_cols(props, tables=["dashboard"])
    data = db(q).select(*cols, cacheable=True).as_list()
    data = mangle_alerts(data)
    return dict(data=data)

