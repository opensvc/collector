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
    if "tags" not in data:
        print(data)
        return
    for tag in data["tags"]:
        vals.append([registry.id, repo.id, tag, now])
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
    token_logger.info(str(request))
    return {}


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


