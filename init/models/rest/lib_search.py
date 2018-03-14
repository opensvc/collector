max_search_result = 10
hard_max_search_result = 1000

def search_cap_limit(limit):
    if limit > hard_max_search_result:
        return hard_max_search_result
    return limit

def lib_search_arrays(pattern, limit):
    t = datetime.datetime.now()
    o = db.stor_array.array_name
    q = db.stor_array.array_name.like(pattern)
    try:
        id = int(pattern.strip("%"))
        q |= db.stor_array.id == id
    except:
        pass
    if not "Manager" in user_groups():
        q &= db.stor_array.id == db.stor_array_dg.array_id
        q &= db.stor_array_dg.id == db.stor_array_dg_quota.dg_id
        q &= db.stor_array_dg_quota.app_id.belongs(user_published_app_ids())

    row = db(q).select(o.count(), groupby=o).first()
    if row is None:
        n = 0
    else:
        n = row._extra[o.count()]

    data = db(q).select(o,
                        db.stor_array.id,
                        groupby=o,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(array_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_prov_templates(pattern, limit):
    t = datetime.datetime.now()
    o = db.prov_templates.tpl_name
    q = db.prov_templates.tpl_name.like(pattern)
    try:
        id = int(pattern.strip("%"))
        q |= db.prov_templates.id == id
    except:
        pass
    q &= db.prov_templates.id == db.prov_template_team_publication.tpl_id
    q &= db.prov_template_team_publication.group_id.belongs(user_org_group_ids())
    n = db(q).count()
    data = db(q).select(db.prov_templates.tpl_name,
                        db.prov_templates.id,
                        groupby=o,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(tpl_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_tag(pattern, limit):
    t = datetime.datetime.now()
    g = db.tags.id
    o = db.tags.tag_name
    q = db.tags.tag_name.like(pattern)
    try:
        id = int(pattern.strip("%"))
        q |= db.tags.id == id
    except:
        pass
    n = db(q).count()
    data = db(q).select(db.tags.tag_name,
                        db.tags.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(tag_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_form(pattern, limit):
    t = datetime.datetime.now()
    g = db.forms.id
    o = db.forms.form_name
    q = db.forms.form_name.like(pattern)
    try:
        id = int(pattern.strip("%"))
        q |= db.forms.id == id
    except:
        pass
    q &= db.forms.id == db.forms_team_publication.form_id
    q &= db.forms_team_publication.group_id.belongs(user_org_group_ids())
    n = len(db(q).select(g, distinct=True))
    data = db(q).select(db.forms.form_name,
                        db.forms.id,
                        groupby=g,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(form_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_fset(pattern, limit):
    t = datetime.datetime.now()
    o = db.gen_filtersets.fset_name
    q = _where(None, 'gen_filtersets', pattern, 'fset_name')
    try:
        id = int(pattern.strip("%"))
        q |= db.gen_filtersets.id == id
    except:
        pass
    n = db(q).count()
    data = db(q).select(db.gen_filtersets.id,
                        o,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(fset_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_disk(pattern, limit):
    t = datetime.datetime.now()
    o = db.svcdisks.disk_id
    q = _where(None, 'svcdisks', pattern, 'disk_id')
    q = q_filter(q, node_field=db.svcdisks.node_id)
    q = apply_filters_id(q, db.svcdisks.node_id)
    n = len(db(q).select(o, groupby=o))
    data = db(q).select(o,
                        orderby=o,
                        groupby=o,
                        limitby=(0,search_cap_limit(limit))
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(disk_id)s", "name": "%(disk_id)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_app(pattern, limit):
    t = datetime.datetime.now()
    o = db.apps.app
    q = db.apps.app.like(pattern)
    try:
        id = int(pattern.strip("%"))
        q |= db.apps.id == id
    except:
        pass
    if not "Manager" in user_groups():
        q &= db.apps.id.belongs(user_app_ids())
    n = db(q).count()
    data = db(q).select(db.apps.id, o, orderby=o, limitby=(0,search_cap_limit(limit))).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(app)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_service(pattern, limit):
    t = datetime.datetime.now()
    o = db.services.svcname
    q = _where(None, 'services', pattern, 'svcname')
    q |= _where(None, 'services', pattern.decode("utf8").encode("ascii", errors="ignore"), 'svc_id')
    q = q_filter(q, app_field=db.services.svc_app)
    q = apply_filters_id(q, None, db.services.svc_id)
    n = db(q).count()
    data = db(q).select(o, db.services.svc_id, db.services.svc_app, orderby=o, groupby=db.services.svc_id, limitby=(0,search_cap_limit(limit)),).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(svc_id)s", "name": "%(svcname)s *%(svc_app)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_vm(pattern, limit):
    t = datetime.datetime.now()
    o = db.svcmon.mon_vmname
    q = _where(None, 'svcmon', pattern, 'mon_vmname')
    q = _where(q, 'svcmon', "!empty", 'mon_vmname')
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    q = apply_filters_id(q, None, db.svcmon.svc_id)
    n = db(q).count()
    data = db(q).select(o,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(mon_vmname)s", "name": "%(mon_vmname)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_ip(pattern, limit):
    t = datetime.datetime.now()
    o = db.node_ip.addr
    q = _where(None, 'node_ip', pattern, 'addr')
    q &= db.node_ip.node_id == db.nodes.id
    q = q_filter(q, app_field=db.nodes.app)
    q = apply_filters_id(q, db.node_ip.node_id, None)

    n = db(q).count()
    data = db(q).select(o,
                        db.nodes.node_id,
                        db.nodes.nodename,
                        db.nodes.app,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(node_id)s", "name": "%(nodename)s *%(app)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }


def lib_search_node(pattern, limit):
    t = datetime.datetime.now()
    o = db.nodes.nodename
    q = _where(None, 'nodes', pattern, 'nodename')
    q |= _where(None, 'nodes', pattern.decode("utf8").encode("ascii", errors="ignore"), 'node_id')
    q = q_filter(q, app_field=db.nodes.app)
    q = apply_filters_id(q, db.nodes.node_id, None)
    n = db(q).count()
    data = db(q).select(o,
                        db.nodes.node_id,
                        db.nodes.app,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(node_id)s", "name": "%(nodename)s *%(app)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_user(pattern, limit):
    t = datetime.datetime.now()
    o = db.v_users.fullname
    q = _where(None, 'v_users', pattern, 'fullname')
    q |= _where(None, 'v_users', pattern, 'email')
    try:
        id = int(pattern.strip("%"))
        q |= db.v_users.id == id
    except:
        pass
    if "Manager" not in user_groups():
        q &= db.v_users.id == db.auth_membership.user_id
        q &= db.auth_membership.group_id.belongs(user_org_group_ids())
        q &= db.auth_membership.group_id == db.auth_group.id
        q &= db.auth_group.role != "Everybody"
    row = db(q).select(db.v_users.id.count(), groupby=db.v_users.id).first()
    if row is None:
        n = 0
    else:
        n = row._extra[db.v_users.id.count()]
    data = db(q).select(db.v_users.fullname,
                        db.v_users.id,
                        db.v_users.email,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
                        groupby=db.v_users.id,
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(fullname)s <%(email)s>"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_group(pattern, limit):
    t = datetime.datetime.now()
    o = db.auth_group.role
    q = db.auth_group.privilege == 'F'
    q = _where(q, 'auth_group', pattern, 'role')
    try:
        id = int(pattern.strip("%"))
        q |= db.auth_group.id == id
    except:
        pass
    q = q_filter(q, group_field=db.auth_group.role)
    n = db(q).count()
    data = db(q).select(o,
                        db.auth_group.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(role)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_priv(pattern, limit):
    t = datetime.datetime.now()
    o = db.auth_group.role
    q = db.auth_group.privilege == 'T'
    q = _where(q, 'auth_group', pattern, 'role')
    try:
        id = int(pattern.strip("%"))
        q |= db.auth_group.id == id
    except:
        pass
    n = db(q).count()
    data = db(q).select(o,
                        db.auth_group.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(role)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_safe_file(pattern, limit):
    t = datetime.datetime.now()
    o = db.safe.uuid
    q = db.safe.uuid.like(pattern) | db.safe.name.like(pattern)
    l = db.safe_team_publication.on(db.safe.id == db.safe_team_publication.file_id)
    q &= db.safe_team_publication.group_id.belongs(user_org_group_ids()) | \
         (db.safe.uploader == auth.user_id)
    n = db(q).count()
    data = db(q).select(o,
                        db.safe.name,
                        left=l,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(uuid)s", "name": "%(name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_metric(pattern, limit):
    t = datetime.datetime.now()
    o = db.metrics.metric_name
    g = db.metrics.id
    q = db.metrics.metric_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.metric_team_publication.metric_id == db.metrics.id
        q &= db.metric_team_publication.group_id.belongs(user_org_group_ids())
    n = len(db(q).select(g, distinct=True))
    data = db(q).select(o,
                        db.metrics.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(metric_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_chart(pattern, limit):
    t = datetime.datetime.now()
    o = db.charts.chart_name
    g = db.charts.id
    q = db.charts.chart_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.chart_team_publication.chart_id == db.charts.id
        q &= db.chart_team_publication.group_id.belongs(user_org_group_ids())
    n = len(db(q).select(g, distinct=True))
    data = db(q).select(o,
                        db.charts.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(chart_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_report(pattern, limit):
    t = datetime.datetime.now()
    o = db.reports.report_name
    g = db.reports.id
    q = db.reports.report_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.report_team_publication.report_id == db.reports.id
        q &= db.report_team_publication.group_id.belongs(user_org_group_ids())
    n = len(db(q).select(g, distinct=True))
    data = db(q).select(o,
                        db.reports.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(report_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_modulesets(pattern, limit):
    t = datetime.datetime.now()
    o = db.comp_moduleset.modset_name
    q = db.comp_moduleset.modset_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.comp_moduleset_team_publication.modset_id == db.comp_moduleset.id
        q &= db.comp_moduleset_team_publication.group_id.belongs(user_org_group_ids())
    n = db(q).count()
    data = db(q).select(o,
                        db.comp_moduleset.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(modset_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_rulesets(pattern, limit):
    t = datetime.datetime.now()
    o = db.comp_rulesets.ruleset_name
    q = db.comp_rulesets.ruleset_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.comp_ruleset_team_publication.ruleset_id == db.comp_rulesets.id
        q &= db.comp_ruleset_team_publication.group_id.belongs(user_org_group_ids())
    n = db(q).count()
    data = db(q).select(o,
                        db.comp_rulesets.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(ruleset_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }


def lib_search_docker_registries(pattern, limit):
    t = datetime.datetime.now()
    o = db.docker_registries.service
    q = db.docker_registries.service.like(pattern)
    q |= db.docker_registries.url.like(pattern)
    if "Manager" not in user_groups():
        q &= db.docker_registries_publications.registry_id == db.docker_registries.id
        q &= db.docker_registries_publications.group_id.belongs(user_org_group_ids())
    n = db(q).count()
    data = db(q).select(o,
                        db.docker_registries.url,
                        db.docker_registries.id,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(service)s @ %(url)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_docker_repositories(pattern, limit):
    t = datetime.datetime.now()
    o = db.docker_repositories.repository
    q = db.docker_repositories.repository.like(pattern)
    q &= db.docker_repositories.registry_id == db.docker_registries.id
    if "Manager" not in user_groups():
         q &= docker_repositories_acls_query()
    n = db(q).count()
    rows = db(q).select(o,
                        db.docker_repositories.id,
                        db.docker_registries.url,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    )
    data = []
    for row in rows:
        data.append({
          "id": row.docker_repositories.id,
          "repository": row.docker_registries.url.split("://")[-1] + "/" + row.docker_repositories.repository,
        })
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(repository)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

def lib_search_variables(pattern, limit):
    t = datetime.datetime.now()
    o = db.v_comp_rulesets.var_name
    q = db.v_comp_rulesets.var_name.like(pattern)
    if "Manager" not in user_groups():
        q &= db.comp_ruleset_team_publication.ruleset_id == db.v_comp_rulesets.ruleset_id
        q &= db.comp_ruleset_team_publication.group_id.belongs(user_org_group_ids())
    n = db(q).count()
    data = db(q).select(o,
                        db.v_comp_rulesets.id,
                        db.v_comp_rulesets.ruleset_id,
                        db.v_comp_rulesets.ruleset_name,
                        orderby=o,
                        limitby=(0,search_cap_limit(limit)),
    ).as_list()
    t = datetime.datetime.now() - t
    return {
      "total": n,
      "data": data,
      "fmt": {"id": "%(id)d", "name": "%(var_name)s in %(ruleset_name)s"},
      "elapsed": "%f" % (t.seconds + 1. * t.microseconds / 1000000),
    }

