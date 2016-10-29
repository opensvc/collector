import gluon.contrib.simplejson as json
import logging
import jwt
import datetime
import requests
from gluon.storage import Storage

key_f = config_get("registry_jwt_key", "/opt/web2py/applications/init/private/ssl/server.key")
crt_f = config_get("registry_jwt_crt", "/opt/web2py/applications/init/private/ssl/server.crt")
issuer = config_get("registry_jwt_issuer", "opensvc")

#
# token manager
#
@auth.requires_login()
def token():
    scope = request.vars.scope
    service = request.vars.service
    return json.dumps({"token": _token(scope, service)})

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

    with open(crt_f ,'r') as f:
        buff = f.read()

    cert_obj = load_pem_x509_certificate(buff, default_backend())
    public_key = cert_obj.public_key()

    return public_key.public_bytes(serialization.Encoding.DER,
                                   serialization.PublicFormat.SubjectPublicKeyInfo)

def load_key():
    with open(key_f ,'r') as f:
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
      "iss": issuer,
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
    registry_id = registry.id

    #
    # tokens asked by the collector for its internal use have all privileges on
    # the registry
    #
    if auth.user is None:
        token_logger.info("allow '*' on all to the collector")
        return scope

    group_ids = user_group_ids()

    #
    # No registry publication to any of the requester groups disallows push and pull
    #
    q = db.docker_registries_publications.group_id.belongs(group_ids)
    q &= db.docker_registries_publications.registry_id == registry_id
    if db(q).count() == 0:
        token_logger.info("disallow 'push,pull' for account '%s' on repo %s:%s (no registry publication)" % (request.vars.get("account", ""), service, scope["name"]))
        scope["actions"] = []
        return scope

    #
    # No registry responsibility to any of the requester groups disallows push
    # on repo not starting with apps/ groups/ and users/
    #
    if scope["name"].count("/") > 1 and ( \
       scope["name"].startswith("apps/") or \
       scope["name"].startswith("groups/") or \
       scope["name"].startswith("users/")):
        q = db.docker_registries_responsibles.group_id.belongs(group_ids)
        q &= db.docker_registries_responsibles.registry_id == registry_id
        if db(q).count() == 0:
            token_logger.info("disallow 'push' for account '%s' on repo %s:%s (not registry responsible)" % (request.vars.get("account", ""), service, scope["name"]))
            scope["actions"] -= set(["push"])

    groups = user_groups()

    #
    # pulling requires the DockerRegistriesPuller privilege for individual
    # users. services bypass this filter.
    #
    if hasattr(auth.user, "id") and "DockerRegistriesPuller" not in groups:
        token_logger.info("disallow 'pull' for account '%s' on repo %s:%s (not DockerRegistriesPuller)" % (request.vars.get("account", ""), service, scope["name"]))
        scope["actions"] -= set(["pull"])

    #
    # pushing requires the DockerRegistriesPusher privilege for individual
    # users. services are never allowed to push.
    #
    if not hasattr(auth.user, "id"):
        token_logger.info("disallow 'push' for account '%s' on repo %s:%s (service requestor)" % (request.vars.get("account", ""), service, scope["name"]))
        scope["actions"] -= set(["push"])
    if "DockerRegistriesPusher" not in groups:
        token_logger.info("disallow 'push' for account '%s' on repo %s:%s (not DockerRegistriesPusher)" % (request.vars.get("account", ""), service, scope["name"]))
        scope["actions"] -= set(["push"])

    if hasattr(auth.user, "id") and scope["name"].startswith("users/%d/" % auth.user.id):
        token_logger.info("no more acl filters on repo %s (personnal)" % scope["name"])
        return scope

    elif hasattr(auth.user, "username") and scope["name"].startswith("users/%s/" % auth.user.username):
        token_logger.info("no more acl filters on repo %s (personnal)" % scope["name"])
        return scope

    elif scope["name"].startswith("groups/"):
        for gid in group_ids:
            if scope["name"].startswith("groups/%d/" % gid):
                token_logger.info("no more acl filters on repo %s (group)" % scope["name"])
                return scope

        for group in groups:
            if scope["name"].lower().startswith("groups/%s/" % group.lower()):
                token_logger.info("no more acl filters on repo %s (group)" % scope["name"])
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

        scope["actions"] = list(set(scope["actions"]) & vactions)

    return scope



#
# Registry discovery
#
def discover_registries():
    q = db.docker_registries.id > 0
    registries = db(q).select()
    for registry in registries:
         try:
             discover_registry(registry)
         except Exception as e:
             token_logger.error("registry '%s' discover failed: %s" % (registry.service, str(e)))

def discover_registry(registry):
    __token = manager_token(registry.service)

    # fetch repos
    verify = not registry.insecure
    r = requests.get(
      registry.url+"/v2/_catalog",
      verify=verify,
      headers={"Authorization": "Bearer "+__token}
    )
    token_logger.info(r.content)

    # insert or update repos
    data = json.loads(r.content)
    vars = ["registry_id", "repository", "updated"]
    vals = []
    now = datetime.datetime.now()
    for repo in data["repositories"]:
        vals.append([registry.id, repo, now])
    generic_insert("docker_repositories", vars, vals)

    # purge repos deleted registry-side
    q = db.docker_repositories.updated < now
    q &= db.docker_repositories.registry_id == registry.id
    db(q).delete()
    db.commit()

    q = db.docker_repositories.registry_id == registry.id
    repos = db(q).select()
    for repo in repos:
        discover_repository_tags(registry, repo)
    db.commit()

def discover_repository_tags(registry, repo):
    __token = manager_token(registry.service, repo=repo.repository)

    verify = not registry.insecure
    r = requests.get(
      registry.url+"/v2/%s/tags/list" % repo.repository,
      verify=verify,
      headers={"Authorization": "Bearer "+__token}
    )
    token_logger.info(r.content)
    data = json.loads(r.content)
    vars = ["registry_id", "repository_id", "name", "updated"]
    vals = []
    now = datetime.datetime.now()
    for tag in data["tags"]:
        vals.append([registry.id, repo.id, tag, now])
    generic_insert("docker_tags", vars, vals)

    # purge tags deleted registry-side
    q = db.docker_tags.updated < now
    q &= db.docker_tags.registry_id == registry.id
    q &= db.docker_tags.repository_id == repo.id
    db(q).delete()
    db.commit()

def get_tag_digest(registry, repo, tag, __token=None):
    if __token is None:
        __token = manager_token(registry.service, repo=repo.repository)

    verify = not registry.insecure
    r = requests.head(
      registry.url+"/v2/%s/manifests/%s" % (repo.repository, tag),
      verify=verify,
      headers={
        "Authorization": "Bearer "+__token,
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
      }
    )
    return r.headers["Docker-Content-Digest"]


def test_del():
    docker_delete_tag(1, 9, "latest")

#
# view
#
class table_registries(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['registry_id',
                     'registry_service',
                     'registry_updated',
                     'registry_created',
                     'repository_id',
                     'repository_name',
                     'repository_updated',
                     'repository_created',
                     'tag_id',
                     'tag_name',
                     'tag_updated',
                     'tag_created']
        self.colprops = {
            'registry_id': HtmlTableColumn(
                     table='docker_registries',
                     field='id',
                    ),
            'registry_service': HtmlTableColumn(
                     table='docker_registries',
                     field='service',
                    ),
            'registry_updated': HtmlTableColumn(
                     table='docker_registries',
                     field='updated',
                    ),
            'registry_created': HtmlTableColumn(
                     table='docker_registries',
                     field='created',
                    ),
            'repository_id': HtmlTableColumn(
                     table='docker_repositories',
                     field='id',
                    ),
            'repository_name': HtmlTableColumn(
                     table='docker_repositories',
                     field='repository',
                    ),
            'repository_updated': HtmlTableColumn(
                     table='docker_repositories',
                     field='updated',
                    ),
            'repository_created': HtmlTableColumn(
                     table='docker_repositories',
                     field='created',
                    ),
            'tag_id': HtmlTableColumn(
                     table='docker_tags',
                     field='id',
                    ),
            'tag_name': HtmlTableColumn(
                     table='docker_tags',
                     field='name',
                    ),
            'tag_updated': HtmlTableColumn(
                     table='docker_tags',
                     field='updated',
                    ),
            'tag_created': HtmlTableColumn(
                     table='docker_tags',
                     field='created',
                    ),
        }
        self.ajax_col_values = 'ajax_registries_col_values'
        self.span = ["repository_id"]
        self.keys = ["repository_id"]

@auth.requires_login()
def ajax_registries_col_values():
    table_id = request.vars.table_id
    t = table_registries(table_id, 'ajax_registries')
    col = request.args[0]

    o = t.colprops[col].field

    q = db.docker_tags.registry_id == db.docker_registries.id
    q &= db.docker_tags.repository_id == db.docker_repositories.id
    q &= docker_repositories_acls_query()

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)

    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_registries():
    table_id = request.vars.table_id
    t = table_registries(table_id, 'ajax_registries')
    o = db.docker_registries.service
    o |= db.docker_repositories.repository
    o |= db.docker_tags.name

    q = db.docker_tags.registry_id == db.docker_registries.id
    q &= db.docker_tags.repository_id == db.docker_repositories.id
    q &= docker_repositories_acls_query()

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start, t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def registries():
    t = SCRIPT(
          """table_registries("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def registries_load():
    return registries()["table"]

