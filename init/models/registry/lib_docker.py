def docker_repositories_acls_query():
    if "Manager" in user_groups():
        q_acls = db.docker_repositories.id > 0
        return q_acls

    acls = ["^users/%d/"%auth.user_id]
    if hasattr(auth.user, "username"):
        acls.append("^users/%s/"%auth.user.username)
    for gid in user_group_ids():
        acls.append("^groups/%d/"%gid)
    for group in user_groups():
        group = group.lower()
        acls.append("^groups/%s/"%group)
    for app_id in user_app_ids():
        acls.append("^apps/%d/"%app_id)
    for app in user_apps():
        app = app.lower()
        acls.append("^apps/%s/"%app)

    q_acls = None
    for chunk in chunker(acls, 20):
        if q_acls is None:
            q_acls = db.docker_repositories.repository.regexp("|".join(chunk))
        else:
            q_acls |= db.docker_repositories.repository.regexp("|".join(chunk))

    return q_acls

