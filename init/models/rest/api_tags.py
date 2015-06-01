from gluon.dal import smart_query

api_tags_doc = {}


#
api_tags_doc["/tags"] = """
### GET

Description:

- List existing tags.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags?like=%%aix%%``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.tags.fields)),
      )

def get_tags(props=None, query=None):
    q = db.tags.id > 0
    if query:
        cols = props_to_cols(None, tables=["tags"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["tags"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_tags_doc["/tags"] += """
### POST

Description:

- Create a tag.

Data:

- ``tag_name``:green
- ``tag_exclude``:green : a regexp to match other tags that can not be attached
  to the same object as this tag

Example:

``# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/tags``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.tags.fields)),
      )

def add_tag(**vars):
    check_privilege("TagManager")
    if 'tag_name' not in vars:
        raise Exception({"error": "the tag_name property is mandatory"})
    tag_name = vars['tag_name']
    q = db.tags.tag_name == tag_name
    if db(q).count() == 1:
        raise Exception({"error": "tag already exist"})
    db.tags.insert(**vars)
    data = db(q).select().first()
    return dict(info="tag created", data=data)


#
api_tags_doc["/tags/<id>"] = """
### GET

Description:

- Display tag property

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/10

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.tags.fields)),
      )

def get_tag(tagid, props=None):
    q = db.tags.id == int(tagid)
    cols = props_to_cols(props, tables=["tags"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_tags_doc["/tags/<id>"] += """
### DELETE

Description:

- Delete the tag with id <id>.
- Also delete the attachments to nodes and services

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def del_tag(tagid):
    check_privilege("TagManager")

    info = []

    q = db.node_tags.tag_id == tagid
    q &= _where(None, 'node_tags', domain_perms(), 'nodename')
    n = db(q).delete()
    info += ["%d node attachments deleted"%n]

    q = db.svc_tags.tag_id == tagid
    q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
    n = db(q).delete()
    info += ["%d service attachments deleted"%n]

    q = db.node_tags.tag_id == tagid
    n = db(q).count()
    q = db.svc_tags.tag_id == tagid
    n += db(q).count()
    if n > 0:
        info += ["tag not deleted: still attached to %d objects you are not responsible for"%n]
        return dict(info=', '.join(info))

    q = db.tags.id == tagid
    n = db(q).delete()
    info += ["%d tag deleted"%n]

    return dict(info=', '.join(info))


#
api_tags_doc["/tags/<id>/nodes"] = """
### GET

Description:

- List nodes where tag <id> is attached.

Optional parameters:

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/1001/nodes?props=nodename``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_tag_nodes(tagid, props=None, query=None):
    q = db.node_tags.tag_id == tagid
    q &= _where(None, 'node_tags', domain_perms(), 'nodename')
    if query:
        cols = props_to_cols(None, tables=["node_tags"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["node_tags"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


#
api_tags_doc["/tags/<id>/services"] = """
### GET

Description:

- List services where tag <id> is attached.

Optional parameters:

- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/tags/1001/nodes?props=nodename``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.nodes.fields)),
      )

def get_tag_services(tagid, props=None, query=None):
    q = db.svc_tags.tag_id == tagid
    q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
    if query:
        cols = props_to_cols(None, tables=["svc_tags"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["svc_tags"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

#
api_tags_doc["/tags/<id>/nodes/<nodename>"] = """
### POST

Description:

- Attach a tag to a node

Example:

``# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/1001/nodes/mynode``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def get_tag_name(tagid):
    try:
        q = db.tags.id == tagid
        tag_name = db(q).select().first().tag_name
    except Exception as e:
        raise Exception({"error": "tag does not exist"})
    return tag_name

def tag_node_attach(tagid, nodename):
    node_responsible(nodename)
    tag_name = get_tag_name(tagid)
    q = db.node_tags.tag_id == tagid
    q &= db.node_tags.nodename == nodename
    q &= _where(None, 'node_tags', domain_perms(), 'nodename')
    if db(q).count() == 1:
        return dict(info="tag already attached")
    db.node_tags.insert(tag_id=tagid, nodename=nodename)
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         nodename=nodename)
    return dict(info="tag attached")


#
api_tags_doc["/tags/<id>/nodes/<nodename>"] += """
### DELETE

Description:

- Detach a tag from a node

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001/nodes/mynode``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def tag_node_detach(tagid, nodename):
    node_responsible(nodename)
    tag_name = get_tag_name(tagid)
    q = db.node_tags.tag_id == tagid
    q &= db.node_tags.nodename == nodename
    q &= _where(None, 'node_tags', domain_perms(), 'nodename')
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         nodename=nodename)
    return dict(info="tag detached")



#
api_tags_doc["/tags/<id>/services/<svcname>"] = """
### POST

Description:

- Attach a tag to a service

Example:

``# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/tags/1001/services/mysvc``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def tag_service_attach(tagid, svcname):
    svc_responsible(svcname)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svcname == svcname
    q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
    if db(q).count() == 1:
        return dict(info="tag already attached")
    db.svc_tags.insert(tag_id=tagid, svcname=svcname)
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         svcname=svcname)
    return dict(info="tag attached")


#
api_tags_doc["/tags/<id>/services/<svcname>"] += """
### DELETE

Description:

- Detach a tag from a service

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/tags/1001/services/mysvc``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def tag_service_detach(tagid, svcname):
    svc_responsible(svcname)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svcname == svcname
    q &= _where(None, 'svc_tags', domain_perms(), 'svcname')
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         svcname=svcname)
    return dict(info="tag detached")




