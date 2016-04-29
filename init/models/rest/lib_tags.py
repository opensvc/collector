def get_tag_name(tagid):
    try:
        q = db.tags.id == tagid
        tag_name = db(q).select().first().tag_name
    except Exception as e:
        raise Exception({"error": "tag does not exist"})
    return tag_name

def lib_tag_detach_node(tagid, node_id):
    node_responsible(node_id=node_id)
    tag_name = get_tag_name(tagid)
    q = db.node_tags.tag_id == tagid
    q &= db.node_tags.node_id == node_id
    q = q_filter(q, node_field=db.node_tags.node_id)
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         node_id=node_id)
    l = {
      'event': 'tags',
      'data': {'action': 'detach', 'tag_id': tagid, 'node_id': node_id},
    }
    _websocket_send(event_msg(l))
    return dict(info="tag detached")

def lib_tag_detach_service(tagid, svc_id):
    svc_responsible(svc_id)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svc_id == svc_id
    q = q_filter(q, svc_field=db.svc_tags.svc_id)
    if db(q).count() == 0:
        return dict(info="tag already detached")
    db(q).delete()
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' detached",
         dict(tag_name=tag_name),
         svc_id=svc_id)
    l = {
      'event': 'tags',
      'data': {'action': 'detach', 'tag_id': tagid, 'svc_id': svc_id},
    }
    _websocket_send(event_msg(l))
    return dict(info="tag detached")


def lib_tag_attach_node(tagid, node_id):
    if not node_id:
        raise Exception("invalid node_id: '%s'" % str(node_id))
    node_responsible(node_id=node_id)
    tag_name = get_tag_name(tagid)
    q = db.node_tags.tag_id == tagid
    q &= db.node_tags.node_id == node_id
    q = q_filter(q, node_field=db.node_tags.node_id)
    if db(q).count() == 1:
        return dict(info="tag '%s' already attached to node '%s'" % (tag_name, get_nodename(node_id)))
    db.node_tags.insert(tag_id=tagid, node_id=node_id)
    table_modified("node_tags")
    _log("node.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         node_id=node_id)
    l = {
      'event': 'tags',
      'data': {
         'action': 'attach',
         'tag_id': tagid,
         'tag_name': tag_name,
         'node_id': node_id
      },
    }
    _websocket_send(event_msg(l))
    return dict(info="tag '%s' attached to node '%s'" % (tag_name, get_nodename(node_id)))


def lib_tag_attach_service(tagid, svc_id):
    if not svc_id or len(svc_id) == 0:
        raise Exception("invalid svc_id: '%s'" % str(svc_id))
    svc_responsible(svc_id)
    tag_name = get_tag_name(tagid)
    q = db.svc_tags.tag_id == tagid
    q &= db.svc_tags.svc_id == svc_id
    q = q_filter(q, svc_field=db.svc_tags.svc_id)
    if db(q).count() == 1:
        return dict(info="tag '%s' already attached to service '%s'" % (tag_name, svc_id))
    db.svc_tags.insert(tag_id=tagid, svc_id=svc_id)
    table_modified("svc_tags")
    _log("service.tag",
         "tag '%(tag_name)s' attached",
         dict(tag_name=tag_name),
         svc_id=svc_id)
    l = {
      'event': 'tags',
      'data': {
        'action': 'attach',
        'tag_id': tagid,
        'tag_name': tag_name,
        'svc_id': svc_id
      },
    }
    _websocket_send(event_msg(l))
    return dict(info="tag '%s' attached to service '%s'" % (tag_name, svc_id))



