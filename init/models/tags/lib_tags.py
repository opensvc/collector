def get_tag_name(tagid):
    try:
        q = db.tags.id == tagid
        tag_name = db(q).select().first().tag_name
    except Exception as e:
        raise Exception({"error": "tag does not exist"})
    return tag_name

def lib_tag_detach_node(tagid, nodename):
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

def lib_tag_detach_service(tagid, svcname):
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


def lib_tag_attach_node(tagid, nodename):
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


def lib_tag_attach_service(tagid, svcname):
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



