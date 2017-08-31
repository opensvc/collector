import gluon.contrib.simplejson as json
import datetime
import requests
from gluon.storage import Storage

def call():
    session.forget(response)
    return service()

#
# token manager
#
@auth.requires_login()
def token():
    scope = request.vars.scope
    service = request.vars.service
    return json.dumps({"token": _token(scope, service)})


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
    try:
        r = requests.get(
          registry.url+"/v2/_catalog",
          verify=verify,
          headers={"Authorization": "Bearer "+__token},
          timeout=5,
        )
    except Exception as exc:
        print "get catalog error: %s" % str(exc)
        return 1

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
    try:
        r = requests.get(
          registry.url+"/v2/%s/tags/list" % repo.repository,
          verify=verify,
          headers={"Authorization": "Bearer "+__token},
          timeout=5,
        )
    except Exception as exc:
        print "get catalog error: %s" % str(exc)
        return 1
    token_logger.info(r.content)
    data = json.loads(r.content)
    vars = ["registry_id", "repository_id", "name", "updated", "config_digest", "config_size"]
    vals = []
    now = datetime.datetime.now()
    if "tags" not in data or data["tags"] is None:
        print "delete repository with no tag:", data
        q = db.docker_repositories.registry_id == registry.id
        q &= db.docker_repositories.repository == repo.repository
        db(q).delete()
        return
    for tag in data["tags"]:
        manifest = get_manifest(registry, repo, tag, __token=__token)
        _vals = [registry.id, repo.id, tag, now]
        if "config" in manifest:
            _vals.append(manifest["config"]["digest"])
            _vals.append(manifest["config"]["size"])
        else:
            _vals.append("")
            _vals.append(None)
        vals.append(_vals)
    generic_insert("docker_tags", vars, vals)

    # purge tags deleted registry-side
    q = db.docker_tags.updated < now
    q &= db.docker_tags.registry_id == registry.id
    q &= db.docker_tags.repository_id == repo.id
    db(q).delete()
    db.commit()



#
# events
#
@service.json
def events():
    try:
        buff = request.body.read()
        data = json.loads(buff)
    except:
        token_logger.info("invalid event: %s" % buff)
        return
    """
    {
      'events': [
        {
          'target': {
            'repository': 'busybox',
            'url': 'https://registry.opensvc.com/v2/busybox/manifests/sha256:600e8faca833451845cd067418227fdabb9649625e59dc2d242ee5c5d88e127e',
            'mediaType': 'application/vnd.docker.distribution.manifest.v1+prettyjws',
            'length': 2084,
            'tag': '4',
            'digest': 'sha256:600e8faca833451845cd067418227fdabb9649625e59dc2d242ee5c5d88e127e',
            'size': 2084
          },
          'timestamp': '2016-11-03T10:19:27.741896359+01:00',
          'request': {
            'method': 'PUT',
            'host': 'registry.opensvc.com',
            'useragent': 'docker/1.8.3 go/go1.4.2 git-commit/f4bf5c7 kernel/4.4.0-22-generic os/linux arch/amd64',
            'id': '3c4ba54f-a686-4e4c-b771-c2c3f9219dfb',
            'addr': '82.233.48.227'
          },
          'actor': {},
          'source': {
            'instanceID': '1852d889-f0bc-42bf-a5d5-acf1d9627413',
            'addr': 'd8c052e942a7:5000'
          },
          'action': 'push',
          'id': '47d188d6-e1a9-4c9c-8149-462362f573dc'
        }
      ]
    }
    """
    if "events" not in data:
        return
    for event in data["events"]:
        do_event(event)

    return

def get_registry_from_url(url):
    try:
        s = "/".join(url.split("/")[:3])
    except:
        token_logger.info("malformed url in event: %s" % url)
        return
    q = db.docker_registries.url == s 
    q |= db.docker_registries.url == s+"/"
    return db(q).select().first()

def do_event(event):
    if "action" not in event:
        token_logger.info("no action in event: %s" % str(event))
        return

    token_logger.info(event)
    if event["action"] == "push":
        do_push_event(event)

def do_push_event(event):
    url = event["target"]["url"]
    registry = get_registry_from_url(url)
    if registry is None:
        token_logger.info("unknown registry: %s" % url)
        return

    if "tag" not in event["target"]:
        token_logger.error("do_push_event: tag key not found in event data: %s", str(event))
        return
    tag = event["target"]["tag"]
    repo = event["target"]["repository"]

    token_logger.info("update or insert repository '%s' in registry '%s'" % (repo, registry.service))
    db.docker_repositories.update_or_insert(
      {"registry_id": registry.id, "repository": repo},
      registry_id=registry.id,
      repository=repo,
      updated=datetime.datetime.now()
    )

    q = db.docker_repositories.repository == repo
    q &= db.docker_repositories.registry_id == registry.id
    repository = db(q).select().first()

    if repository is None:
        token_logger.info("repository not found '%s' in registry '%s'" % (repo, registry.service))
        return

    token_logger.info("update or insert repository tag '%s:%s' in registry '%s'" % (repository.repository, tag, registry.service))
    db.docker_tags.update_or_insert(
      {"registry_id": registry.id, "repository_id": repository.id, "name": tag},
      registry_id=registry.id,
      repository_id=repository.id,
      name=tag,
      updated=datetime.datetime.now()
    )
    table_modified("docker_tags")
    _log('docker.push',
         'image %(repo)s:%(tag)s pushed to registry %(service)s',
         dict(repo=repo, tag=tag, service=registry.service),
         user=""
    )
    ws_send('docker_tags_change')



#
# search
#
@service.json
@auth.requires_login()
def search():
    """
      [
        {
            "description": "",
            "is_official": false,
            "is_automated": false,
            "name": "wma55/u1210sshd",
            "star_count": 0
        },
        ...
      ]
    """
    token_logger.info(str(auth.user))
    if "q" in request.vars:
        s = request.vars.q
    else:
        s = None

    q = db.docker_repositories.repository.like("%"+s+"%")
    q &= docker_repositories_acls_query()
    rows = db(q).select()

    data = {
      "query": s,
      "num_results": len(rows),
      "results": [],
    }

    for r in rows:
        data["results"].append({
            "description": r.description,
            "is_official": r.official,
            "is_automated": r.automated,
            "name": r.repository,
            "star_count": r.stars
        })
    return data


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
                     'repository_stars',
                     'repository_official',
                     'repository_automated',
                     'repository_updated',
                     'repository_created',
                     'tag_id',
                     'tag_name',
                     'tag_config_size',
                     'tag_config_digest',
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
            'repository_stars': HtmlTableColumn(
                     table='docker_repositories',
                     field='stars',
                    ),
            'repository_official': HtmlTableColumn(
                     table='docker_repositories',
                     field='official',
                    ),
            'repository_automated': HtmlTableColumn(
                     table='docker_repositories',
                     field='automated',
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
            'tag_config_digest': HtmlTableColumn(
                     table='docker_tags',
                     field='config_digest',
                    ),
            'tag_config_size': HtmlTableColumn(
                     table='docker_tags',
                     field='config_size',
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
    o = t.get_orderby(default=db.docker_registries.service|db.docker_repositories.repository|db.docker_tags.name)

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


