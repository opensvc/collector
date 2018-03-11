def lib_safe_check_file_responsible(uuid):
    if "Manager" in user_groups():
        return

    q = db.safe.uuid == uuid

    q1 = db.safe.uploader == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    q1 = db.safe.id == db.safe_team_responsible.file_id
    q1 &= db.safe_team_responsible.group_id == db.auth_membership.group_id
    q1 &= db.auth_membership.user_id == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    raise HTTP(401, "you are not authorized to manage this file")

def lib_safe_check_file_publication(uuid):
    q = db.safe.uuid == uuid

    if auth_is_svc():
        q1 = db.safe.id == db.safe_team_publication.file_id
        q1 &= db.safe_team_publication.group_id == db.apps_responsibles.group_id
        q1 &= db.apps_responsibles.app_id == db.apps.id
        q1 &= db.apps.app == db.services.svc_app
        q1 &= db.services.svc_id == auth.user.svc_id
        ok = db(q&q1).select().first()
        if ok:
            return
        else:
            raise HTTP(401, "this service is not authorized to access this file")
    elif auth_is_node():
        q1 = db.safe.id == db.safe_team_publication.file_id
        q1 &= db.safe_team_publication.group_id == db.auth_group.id
        q1 &= db.auth_group.role == db.nodes.team_responsible
        q1 &= db.nodes.node_id == auth.user.node_id
        ok = db(q&q1).select().first()
        if ok:
            return
        else:
            #raise Exception(db(q&q1)._select())
            raise HTTP(401, "this node is not authorized to access this file")

    if "Manager" in user_groups():
        return

    q1 = db.safe.uploader == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    q1 = db.safe.id == db.safe_team_publication.file_id
    q1 &= db.safe_team_publication.group_id == db.auth_membership.group_id
    q1 &= db.auth_membership.user_id == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    raise HTTP(401, "you are not authorized to access this file")

def lib_safe_md5(f):
    import hashlib
    f.seek(0, os.SEEK_SET)
    hash = hashlib.md5()
    for chunk in iter(lambda: f.read(4096), b""):
        hash.update(chunk)
    f.seek(0, os.SEEK_SET)
    return hash.hexdigest()

def lib_safe_upload(name=None, file=None):
    if not auth_is_node():
        check_privilege("SafeUploader")

    uploader = auth.user_id
    uploaded_from = request.env.REMOTE_ADDR
    uploaded_date = datetime.datetime.now()

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0, os.SEEK_SET)

    md5 = lib_safe_md5(file.file)

    id = db.safe.insert(
      uploader=uploader,
      uploaded_from=uploaded_from,
      uploaded_date=uploaded_date,
      name=name,
      size=size,
      uuid=file,
      md5=md5,
    )

    if auth_is_node():
        # give and display the file to the node's team_responsible
        gid = auth_node_group_id()
        if gid is not None:
            db.safe_team_responsible.update_or_insert(file_id=id, group_id=gid)
            db.safe_team_publication.update_or_insert(file_id=id, group_id=gid)

    d = db(db.safe.id==id).select().as_dict()
    return d[id]

def lib_safe_download(uuid):
    lib_safe_check_file_publication(uuid)

    import cStringIO
    import contenttype as c
    s = cStringIO.StringIO()

    filename, file = db.safe.uuid.retrieve(uuid)

    md5 = lib_safe_md5(file)
    meta_md5 = db(db.safe.uuid==uuid).select().first().md5
    if md5 != meta_md5:
        raise HTTP(403, "the file is compromised: current md5 = %s, expected md5 = %s" % (md5, meta_md5))

    s.write(file.read())
    response.headers['Content-Type'] = c.contenttype(filename)
    response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
    return s.getvalue()

def lib_safe_preview(uuid):
    lib_safe_check_file_publication(uuid)

    import contenttype as c

    filename, file = db.safe.uuid.retrieve(uuid)

    md5 = lib_safe_md5(file)
    meta_md5 = db(db.safe.uuid==uuid).select().first().md5
    if md5 != meta_md5:
        raise HTTP(403, "the file is compromised: current md5 = %s, expected md5 = %s" % (md5, meta_md5))

    data = {}
    data['content_type'] = c.contenttype(filename)
    if "text/plain" not in data['content_type']:
        raise HTTP(400, "The file content is not plain text")
    data["data"] = file.read()
    return data


