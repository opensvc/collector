token_logger = logging.getLogger("web2py.app.init.token")
token_logger.setLevel(logging.DEBUG)

def lib_docker_registry_id(id):
    try:
        id = int(id)
        return id
    except:
        q = db.docker_registries.service == id
        row = db(q).select().first()
        if row is not None:
            return row.id
    raise Exception("docker registry '%s' does not exist" % str(id))

def get_docker_repository(id, acl=True):
    q = db.docker_repositories.id == int(id)
    if acl:
        q &= docker_repositories_acls_query()
    r = db(q).select().first()
    if r is None:
        raise Exception("docker repository '%s' not found" % str(id))
    return r

def get_docker_registry(id):
    try:
        q = db.docker_registries.id == int(id)
    except:
        q = db.docker_registries.service == id
    r = db(q).select().first()
    if r is None:
        raise Exception("docker registry '%s' not found" % str(id))
    return r

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

def _token(scope, service):
    if scope is None:
        # docker login
        token_logger.info("docker login. "+str(request.vars))
    else:
        token_logger.info("docker auth. "+str(request.vars))
        scope = parse_scope(scope)

    payload = create_payload(scope, service)
    key = load_key()
    token = jwt.encode(payload, key, algorithm='RS256', headers={"kid": keyid()})
    load_pubkey()
    return token

def manager_token(service, repo=None):
    if repo is None:
        return _token("registry:catalog:*", service)
    else:
        return _token("repository:%s:*" % repo, service)

def docker_delete_tag(registry_id, repo_id, tag, __token=None):
    repo = get_docker_repository(repo_id, acl=False)
    registry = get_docker_registry(registry_id)
    if __token is None:
        __token = manager_token(registry.service, repo=repo.repository)

    digest = get_tag_digest(registry, repo, tag, __token)
    token_logger.info("DELETE "+registry.url+"/v2/%s/manifests/%s" % (repo.repository, digest))
    verify = not registry.insecure
    r = requests.delete(
      registry.url+"/v2/%s/manifests/%s" % (repo.repository, digest),
      verify=verify,
      headers={"Authorization": "Bearer "+__token}
    )
    if r.status_code != 202:
        token_logger.error("failed to delete: "+str(r.content))
        return

    # delete from the collector db too
    q = db.docker_tags.name == tag
    q &= db.docker_tags.registry_id == registry.id
    q &= db.docker_tags.repository_id == repo.id
    db(q).delete()
    db.commit()

    ws_send('docker_tags_change')
    _log(
      'docker.tags.delete',
      'docker tag %(s)s deleted',
      dict(s=tag),
    )


