def call():
    session.forget()
    return service()

@auth.requires_login()
@service.json
def create_and_add_tag():
    data = create_tag()
    if data["ret"] != 0:
        return data
    return add_tag()

@auth.requires_login()
@service.json
def create_tag():
    tag_name = request.vars.tag_name
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data (tag_name)"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) != 0:
        return {"ret": 0, "msg": "tag already exists"}

    db.tags.insert(
       tag_name=tag_name
    )
    _log("tag",
         "tag '%(tag_name)s' created",
         dict(tag_name=tag_name)
    )
    return {"ret": 0, "msg": "tag successfully created"}


@auth.requires_login()
@service.json
def add_tag():
    nodename = request.vars.nodename
    svcname = request.vars.svcname
    tag_name = request.vars.tag_name
    if nodename is None and svcname is None:
        return {"ret": 1, "msg": "misformatted data (nodename)"}
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data (tag_name)"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) == 0:
        return {"ret": 2, "msg": "This tag does not exist yet. Press enter again to create it."}
    tag_id = rows.first().id

    if svcname is not None:
        q = db.svc_tags.svcname == svcname
        q &= db.svc_tags.tag_id == tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 3, "msg": "tag is already attached"}
        db.svc_tags.insert(
           svcname=svcname,
           tag_id=tag_id
        )
        _log("service.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             svcname=svcname)
    if nodename is not None:
        q = db.node_tags.nodename == nodename
        q &= db.node_tags.tag_id == tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 3, "msg": "tag is already attached"}
        db.node_tags.insert(
           nodename=nodename,
           tag_id=tag_id
        )
        _log("node.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             nodename=nodename)
    return {"ret": 0, "tag_id": tag_id, "msg": "tag successfully attached"}

@auth.requires_login()
@service.json
def del_tag():
    nodename = request.vars.nodename
    svcname = request.vars.svcname
    tag_id = request.vars.tag_id
    if nodename is None and svcname is None:
        return {"ret": 1, "msg": "misformatted data (nodename)"}
    if tag_id is None:
        return {"ret": 1, "msg": "misformatted data (tag_id)"}

    q = db.tags.id == tag_id
    rows = db(q).select()
    tag = rows.first()
    if tag is None:
        return {"ret": 1, "msg": "tag not found"}

    if svcname is not None:
        q = db.svc_tags.tag_id == tag_id
        q &= db.svc_tags.svcname == svcname
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("service.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag.tag_name),
             svcname=svcname)
    if nodename is not None:
        q = db.node_tags.tag_id == tag_id
        q &= db.node_tags.nodename == nodename
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("node.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag.tag_name),
             nodename=nodename)
    return {"ret": 0, "msg": "tag successfully detached"}

@auth.requires_login()
@service.json
def json_svc_tags(svcname):
    q = db.svc_tags.svcname == svcname
    q &= db.svc_tags.tag_id == db.tags.id
    rows = db(q).select(db.tags.id, db.tags.tag_name, cacheable=True)
    l = []
    for row in rows:
        l.append({"tag_name": row.tag_name, "tag_id": row.id})
    return l

@auth.requires_login()
@service.json
def json_node_tags(nodename):
    q = db.node_tags.nodename == nodename
    q &= db.node_tags.tag_id == db.tags.id
    rows = db(q).select(db.tags.id, db.tags.tag_name, cacheable=True)
    l = []
    for row in rows:
        l.append({"tag_name": row.tag_name, "tag_id": row.id})
    return l

@auth.requires_login()
@service.json
def list_svc_avail_tags(svcname, prefix):
    d = {}
    l = json_svc_tags(svcname)
    l = [r["tag_id"] for r in l]

    q = ~db.tags.id.belongs(l)
    q &= db.tags.tag_name.like(prefix+"%")
    rows = db(q).select()
    if len(rows) == 0:
        return []
    tags = [{"tag_name": r.tag_name.lower(), "tag_id": r.id} for r in rows]
    return tags

@auth.requires_login()
@service.json
def list_node_avail_tags(nodename, prefix):
    d = {}
    l = json_node_tags(nodename)
    l = [r["tag_id"] for r in l]

    q = ~db.tags.id.belongs(l)
    q &= db.tags.tag_name.like(prefix+"%")
    rows = db(q).select()
    if len(rows) == 0:
        return []
    tags = [{"tag_name": r.tag_name.lower(), "tag_id": r.id} for r in rows]
    return tags

