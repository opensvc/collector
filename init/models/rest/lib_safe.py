def lib_safe_check_file_responsible(uuid):
    if "Manager" in user_groups():
        return

    q = db.safe.uuid == uuid

    q1 = db.safe.uploader == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    q1 = db.safe.id == db.safe_responsible.file_id
    q1 &= db.safe_responsible.group_id == db.auth_membership.group_id
    q1 &= db.auth_membership.user_id == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    raise Exception("you are not authorized to manage this file")

def lib_safe_check_file_publication(uuid):
    if "Manager" in user_groups():
        return

    q = db.safe.uuid == uuid

    q1 = db.safe.uploader == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    q1 = db.safe.id == db.safe_publication.file_id
    q1 &= db.safe_publication.group_id == db.auth_membership.group_id
    q1 &= db.auth_membership.user_id == auth.user_id
    ok = db(q&q1).select().first()
    if ok:
        return

    raise Exception("you are not authorized to access this file")


def lib_safe_upload(name=None, file=None):
    check_privilege("SafeUploader")
    uploader = auth.user_id
    uploaded_from = request.env.REMOTE_ADDR
    uploaded_date = datetime.datetime.now()

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0, os.SEEK_SET)

    id = db.safe.insert(
      uploader=uploader,
      uploaded_from=uploaded_from,
      uploaded_date=uploaded_date,
      name=name,
      size=size,
      uuid=file,
    )
    return db(db.safe.id==id).select().as_dict()[id]

def lib_safe_download(uuid):
    lib_safe_check_file_publication(uuid)

    import cStringIO
    import contenttype as c
    s = cStringIO.StringIO()

    filename, file = db.safe.uuid.retrieve(uuid)
    s.write(file.read())
    response.headers['Content-Type'] = c.contenttype(filename)
    response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
    return s.getvalue()
