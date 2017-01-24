token_logger = logging.getLogger("web2py.app.init.token")
token_logger.setLevel(logging.DEBUG)
token_issuer = config_get("registry_jwt_issuer", "opensvc")

token_key_f = config_get("registry_jwt_key", "/opt/web2py/applications/init/private/ssl/server.key")
token_crt_f = config_get("registry_jwt_crt", "/opt/web2py/applications/init/private/ssl/server.crt")

def keyid():
    import hashlib
    import base64
    s = load_pubkey()
    xd = hashlib.sha256(s).digest()[:30]
    xd = base64.b32encode(xd)
    for i in range(11):
        ses = 48-4*(i+1)
        xd = xd[:ses] + ":" + xd[ses:]
    return xd

def load_pubkey():
    from cryptography.x509 import load_pem_x509_certificate
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    with open(token_crt_f ,'r') as f:
        buff = f.read()

    cert_obj = load_pem_x509_certificate(buff, default_backend())
    public_key = cert_obj.public_key()

    return public_key.public_bytes(serialization.Encoding.DER,
                                   serialization.PublicFormat.SubjectPublicKeyInfo)

def load_key():
    with open(token_key_f ,'r') as f:
        buff = f.read()

    return buff

def parse_scope(s):
    l = s.split(":")
    data = {}
    if len(l) == 4:
        data["type"] = l[0]
        data["name"] = l[1] + ":" + l[2]
        data["actions"] = l[3].split(",")
    elif len(l) == 3:
        data["type"] = l[0]
        data["name"] = l[1]
        data["actions"] = l[2].split(",")
    else:
        return
    return data

def create_payload(scope, service):
    data = {
      "iss": token_issuer,
      "aud": service,
      "iat": datetime.datetime.utcnow(),
      "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=900),
    }
    if scope:
        vscope = validated_scope(scope, service)
        if vscope:
            data["access"] = [vscope]
    token_logger.debug("token payload: "+str(data))
    return data

def lib_docker_repository_id(id):
    try:
        id = int(id)
        return id
    except:
        q = db.docker_repositories.repository == id
        row = db(q).select().first()
        if row is not None:
            return row.id
    raise Exception("docker repository '%s' does not exist" % str(id))

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

def docker_repositories_acls_query(action="pull"):
    if "Manager" in user_groups():
        q_acls = db.docker_repositories.id > 0
        return q_acls

    group_ids = user_group_ids()
    if action == "push":
        q = db.docker_registries.restricted == False
        q &= db.docker_registries_publications.registry_id == db.docker_registries.id
        q &= db.docker_registries_publications.group_id.belongs(group_ids)
        allowed_unrestricted_registry_ids = [r.id for r in db(q).select(db.docker_registries.id)]

        q = db.docker_registries.restricted == True
        q &= db.docker_registries_responsibles.registry_id == db.docker_registries.id
        q &= db.docker_registries_responsibles.group_id.belongs(group_ids)
        allowed_restricted_registry_ids = [r.id for r in db(q).select(db.docker_registries.id)]

        allowed_registry_ids = allowed_restricted_registry_ids + allowed_unrestricted_registry_ids
        if len(allowed_registry_ids) == 0:
            return db.docker_repositories.id < 0
        q_published = db.docker_repositories.registry_id.belongs(allowed_registry_ids)
    else:
        q = db.docker_registries_publications.group_id.belongs(group_ids)
        published_registry_ids = [r.registry_id for r in db(q).select()]
        if len(published_registry_ids) == 0:
            return db.docker_repositories.id < 0
        q_published = db.docker_repositories.registry_id.belongs(published_registry_ids)

    acls = []
    if hasattr(auth.user, "id") and auth.user.id > 0:
        acls.append("^users/%d/"%auth.user_id)
    if hasattr(auth.user, "username") and auth.user.username:
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

    if action == "pull":
        acls.append("^(?!(users|groups|apps)/)")

    if len(acls) == 0:
        return db.docker_repositories.id < 0

    q_acls = None
    for chunk in chunker(acls, 20):
        if q_acls is None:
            q_acls = db.docker_repositories.repository.regexp("|".join(chunk))
        else:
            q_acls |= db.docker_repositories.repository.regexp("|".join(chunk))

    return q_published & q_acls

def incr_stars(registry_id, repository):
    sql = """update docker_repositories set stars=stars+1
             where
               repository="%s" and
               registry_id=%d
          """ % (repository, registry_id)
    db.executesql(sql)

def _token(scope, service):
    if scope is None:
        # docker login
        token_logger.info("docker login. "+str(request.vars))
    else:
        token_logger.info("docker auth. "+str(request.vars))
        scope = parse_scope(scope)

    payload = create_payload(scope, service)
    key = load_key()

    import jwt
    token = jwt.encode(payload, key, algorithm='RS256', headers={"kid": keyid()})

    load_pubkey()
    return token

def get_manifest(registry, repo, tag, __token=None):
    if __token is None:
        __token = manager_token(registry.service, repo=repo.repository)

    verify = not registry.insecure
    import requests
    r = requests.get(
      registry.url+"/v2/%s/manifests/%s" % (repo.repository, tag),
      verify=verify,
      headers={
        "Authorization": "Bearer "+__token,
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
      }
    )
    data = json.loads(r.content)
    return data

def get_tag_digest(registry, repo, tag, __token=None):
    if __token is None:
        __token = manager_token(registry.service, repo=repo.repository)

    verify = not registry.insecure
    import requests
    r = requests.head(
      registry.url+"/v2/%s/manifests/%s" % (repo.repository, tag),
      verify=verify,
      headers={
        "Authorization": "Bearer "+__token,
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
      }
    )
    return r.headers["Docker-Content-Digest"]

def manager_token(service, repo=None):
    if repo is None:
        return _token("registry:catalog:*", service)
    else:
        return _token("repository:%s:*" % repo, service)

#
# acl validation
#
def validated_scope(scope, service):
    #
    # refuse to serve token for registries we don't known about
    #
    q = db.docker_registries.service == service
    registry = db(q).select().first()
    if registry is None:
        token_logger.error("unknown registry '%s'" % service)
        scope["actions"] = []
        return scope

    scope = _validated_scope(scope, registry)

    if ((len(scope["actions"]) > 0) and ("pull" in scope["actions"])):
        incr_stars(registry.id, scope["name"])

    return scope

def _validated_scope(scope, registry):
    #
    # tokens asked by the collector for its internal use have all privileges on
    # the registry
    #
    if auth.user is None:
        token_logger.info("allow '*' on all to the collector")
        return scope

    group_ids = user_group_ids()
    scope["actions"] = set(scope["actions"])

    #
    # No registry publication to any of the requester groups disallows push and pull
    #
    q = db.docker_registries_publications.group_id.belongs(group_ids)
    q &= db.docker_registries_publications.registry_id == registry.id
    if db(q).count() == 0:
        token_logger.info("disallow 'push,pull' for account '%s' on repo %s:%s"
                          " (no registry publication)",
                          request.vars.get("account", ""),
                          registry.service, scope["name"])
        scope["actions"] = []
        return scope

    #
    # No registry responsibility to any of the requester groups disallows push
    # on restricted registries
    #
    if registry.restricted:
        q = db.docker_registries_responsibles.group_id.belongs(group_ids)
        q &= db.docker_registries_responsibles.registry_id == registry.id
        if db(q).count() == 0:
            token_logger.info("disallow 'push' for account '%s' on repo %s:%s"
                              " (not restricted registry responsible)",
                              request.vars.get("account", ""),
                              registry.service, scope["name"])
            scope["actions"] -= set(["push"])

    #
    # No registry responsibility to any of the requester groups disallows push
    # on repo not starting with apps/ groups/ and users/
    #
    if scope["name"].count("/") == 0 or not ( \
       scope["name"].startswith("apps/") or \
       scope["name"].startswith("groups/") or \
       scope["name"].startswith("users/")):
        q = db.docker_registries_responsibles.group_id.belongs(group_ids)
        q &= db.docker_registries_responsibles.registry_id == registry.id
        if db(q).count() == 0:
            token_logger.info("disallow 'push' for account '%s' on repo %s:%s"
                              " (not registry responsible)",
                              request.vars.get("account", ""),
                              registry.service, scope["name"])
            scope["actions"] -= set(["push"])

    groups = user_groups()

    #
    # pulling requires the DockerRegistriesPuller privilege for individual
    # users. services bypass this filter.
    #
    if not hasattr(auth.user, "svc_id") and hasattr(auth.user, "id") and \
       "DockerRegistriesPuller" not in groups:
        token_logger.info("disallow 'pull' for account '%s' on repo %s:%s (not"
                          " DockerRegistriesPuller)",
                          request.vars.get("account", ""),
                          registry.service, scope["name"])
        scope["actions"] -= set(["pull"])

    #
    # pushing requires the DockerRegistriesPusher privilege for individual
    # users. services are never allowed to push.
    #
    if not hasattr(auth.user, "id"):
        token_logger.info("disallow 'push' for account '%s' on repo %s:%s"
                          " (service requestor)",
                          request.vars.get("account", ""),
                          registry.service, scope["name"])
        scope["actions"] -= set(["push"])
    if "DockerRegistriesPusher" not in groups:
        token_logger.info("disallow 'push' for account '%s' on repo %s:%s (not"
                          " DockerRegistriesPusher)",
                          request.vars.get("account", ""),
                          registry.service, scope["name"])
        scope["actions"] -= set(["push"])

    if hasattr(auth.user, "id") and scope["name"].startswith("users/%d/" % auth.user.id):
        token_logger.info("no more acl filters on repo %s (personnal)" % scope["name"])
        scope["actions"] = list(scope["actions"])
        return scope

    elif hasattr(auth.user, "username") and scope["name"].startswith("users/%s/" % auth.user.username):
        token_logger.info("no more acl filters on repo %s (personnal)" % scope["name"])
        scope["actions"] = list(scope["actions"])
        return scope

    elif scope["name"].startswith("groups/"):
        for gid in group_ids:
            if scope["name"].startswith("groups/%d/" % gid):
                token_logger.info("no more acl filters on repo %s (group)" % scope["name"])
                scope["actions"] = list(scope["actions"])
                return scope

        for group in groups:
            if scope["name"].lower().startswith("groups/%s/" % group.lower()):
                token_logger.info("no more acl filters on repo %s (group)" % scope["name"])
                scope["actions"] = list(scope["actions"])
                return scope

    elif scope["name"].startswith("apps/"):
        vactions = set([])

        q = db.apps_publications.group_id.belongs(group_ids)
        q &= db.apps_publications.app_id == db.apps.id
        apps = db(q).select()
        for app in apps:
            if scope["name"].startswith("apps/%d/" % app.apps.id):
                token_logger.info("allow 'pull' on repo %s (app publication)" % scope["name"])
                vactions.add("pull")
                break
            if scope["name"].lower().startswith("apps/%s/" % app.apps.app.lower()):
                token_logger.info("allow 'pull' on repo %s (app publication)" % scope["name"])
                vactions.add("pull")
                break

        q = db.apps_responsibles.group_id.belongs(group_ids)
        q &= db.apps_responsibles.app_id == db.apps.id
        apps = db(q).select()
        for app in apps:
            if scope["name"].startswith("apps/%d/" % app.apps.id):
                token_logger.info("allow 'push,pull' on app repo %s (app responsible)" % scope["name"])
                vactions |= set(["push", "pull"])
                break
            if scope["name"].lower().startswith("apps/%s/" % app.apps.app.lower()):
                token_logger.info("allow 'push,pull' on repo %s (app responsible)" % scope["name"])
                vactions |= set(["push", "pull"])
                break

        scope["actions"] = list(scope["actions"] & vactions)

    scope["actions"] = list(scope["actions"])
    return scope

def docker_delete_tag(registry_id, repo_id, tag, __token=None):
    repo = get_docker_repository(repo_id, acl=False)
    registry = get_docker_registry(registry_id)
    if __token is None:
        __token = manager_token(registry.service, repo=repo.repository)

    digest = get_tag_digest(registry, repo, tag, __token)
    token_logger.info("DELETE "+registry.url+"/v2/%s/manifests/%s" % (repo.repository, digest))
    verify = not registry.insecure
    import requests
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
      "docker.tags.delete",
      "docker tag '%(r)s:%(s)s' deleted from registry '%(service)s'",
      dict(r=repo.repository, s=tag, service=registry.service),
    )

def docker_delete_repository(repo_id):
    repo = get_docker_repository(repo_id, acl=False)
    registry = get_docker_registry(repo.registry_id)

    q = db.docker_repositories.id == repo_id
    db(q).delete()
    db.commit()

    ws_send('docker_repositories_change')
    _log(
      "docker.repositories.delete",
      "docker repository '%(s)s' deleted from registry '%(service)s'",
      dict(s=repo.repository, service=registry.service),
    )


