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
    q = q_filter(q, node_field=db.node_tags.nodename)
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         nodename=nodename)
    import hashlib
    hash = hashlib.md5()
    hash.update(nodename)
    l = {
      'event': 'tags',
      'data': {'action': 'detach', 'tag_id': tagid, 'nodename': hash.hexdigest()},
    }
    _websocket_send(event_msg(l))
    return dict(info="tag detached")

def lib_tag_detach_service(tagid, svcname):
    svc_responsible(svcname)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svcname == svcname
    q = q_filter(q, svc_field=db.svc_tags.svcname)
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         svcname=svcname)
    import hashlib
    hash = hashlib.md5()
    hash.update(svcname)
    l = {
      'event': 'tags',
      'data': {'action': 'detach', 'tag_id': tagid, 'svcname': hash.hexdigest()},
    }
    _websocket_send(event_msg(l))
    return dict(info="tag detached")


def lib_tag_attach_node(tagid, nodename):
    if not nodename or len(nodename) == 0:
        raise Exception("invalid nodename: '%s'" % str(nodename))
    node_responsible(nodename)
    tag_name = get_tag_name(tagid)
    q = db.node_tags.tag_id == tagid
    q &= db.node_tags.nodename == nodename
    q = q_filter(q, node_field=db.node_tags.nodename)
    if db(q).count() == 1:
        return dict(info="tag '%s' already attached to node '%s'" % (tag_name, nodename))
    db.node_tags.insert(tag_id=tagid, nodename=nodename)
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         nodename=nodename)
    import hashlib
    hash = hashlib.md5()
    hash.update(nodename)
    l = {
      'event': 'tags',
      'data': {
         'action': 'attach',
         'tag_id': tagid,
         'tag_name': tag_name,
         'nodename': hash.hexdigest()
      },
    }
    _websocket_send(event_msg(l))
    return dict(info="tag '%s' attached to node '%s'" % (tag_name, nodename))


def lib_tag_attach_service(tagid, svcname):
    if not svcname or len(svcname) == 0:
        raise Exception("invalid svcname: '%s'" % str(svcname))
    svc_responsible(svcname)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svcname == svcname
    q = q_filter(q, svc_field=db.svc_tags.svcname)
    if db(q).count() == 1:
        return dict(info="tag '%s' already attached to service '%s'" % (tag_name, nodename))
    db.svc_tags.insert(tag_id=tagid, svcname=svcname)
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         svcname=svcname)
    import hashlib
    hash = hashlib.md5()
    hash.update(svcname)
    l = {
      'event': 'tags',
      'data': {
        'action': 'attach',
        'tag_id': tagid,
        'tag_name': tag_name,
        'svcname': hash.hexdigest()
      },
    }
    _websocket_send(event_msg(l))
    return dict(info="tag '%s' attached to service '%s'" % (tag_name, svcname))



