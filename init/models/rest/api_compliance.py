from gluon.dal import smart_query
import json

api_compliance_doc = {}


#
api_compliance_doc["/compliance/status"] = {}
api_compliance_doc["/compliance/status"]["GET"] = """
Description:

- List compliance modules' last check run.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o-
https://%(collector)s/init/rest/api/compliance/status?query=run_status=1 and run_module=mymod``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.comp_status.fields)),
      )

def get_compliance_status(props=None, query=None):
    q = db.comp_status.id > 0
    q &= _where(q, 'comp_status', domain_perms(), 'run_nodname')
    if query:
        cols = props_to_cols(None, tables=["comp_status"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["comp_status"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_compliance_doc["/compliance/status/<id>"] = {}
api_compliance_doc["/compliance/status/<id>"]["GET"] = """
Description:

- Display properties of the last check run of a specific module-node-service
  tuple

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/compliance/status/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.comp_status.fields)),
      )

def get_compliance_status_one(id, props=None):
    q = db.comp_status.id == int(id)
    q &= _where(q, 'comp_status', domain_perms(), 'run_nodname')
    cols = props_to_cols(props, tables=["comp_status"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_compliance_doc["/compliance/status/<id>"]["DELETE"] = """
Description:

- Delete the last check run information of a specific module-node-service
  tuple.
- Requires the CompManager privilege and node ownership.

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/compliance/status/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_compliance_status(id, props=None):
    check_privilege("CompManager")
    q = db.comp_status.id == int(id)
    q &= _where(q, 'comp_status', domain_perms(), 'run_nodname')
    row = db(q).select().first()
    if row is None:
        return dict(info="Task %s does not exist in the scheduler" % id)
    node_responsible(row.run_nodename)
    db(q).delete()
    _log('rest.compliance.status.delete',
         'deleted run %(u)s',
         dict(u="-".join((row.run_module, row.run_nodename, row.run_svcname if row.run_svcname else ""))),
         nodename=row.run_nodename,
         svcname=row.run_svcname,
    )
    return dict(info="Run %s deleted" % id)


