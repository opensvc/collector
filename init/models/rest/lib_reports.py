import gluon.contrib.simplejson as sjson
from applications.init.modules import gittrack

#
def metric_published_ids():
    q = db.metric_team_publication.group_id.belongs(user_group_ids())
    return [r.metric_id for r in db(q).select(db.metric_team_publication.metric_id)]

def chart_published_ids():
    q = db.chart_team_publication.group_id.belongs(user_group_ids())
    return [r.chart_id for r in db(q).select(db.chart_team_publication.chart_id)]

def report_published_ids():
    q = db.report_team_publication.group_id.belongs(user_group_ids())
    return [r.report_id for r in db(q).select(db.report_team_publication.report_id)]

#
def metric_published(metric_id):
    if 'Manager' in user_groups():
        return
    q = db.metric_team_publication.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to access the metric %s" % str(metric_id))

def chart_published(chart_id):
    if 'Manager' in user_groups():
        return
    q = db.chart_team_publication.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to access the chart %s" % str(chart_id))

def report_published(report_id):
    if 'Manager' in user_groups():
        return
    q = db.report_team_publication.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to access the report %s" % str(report_id))

#
def chart_responsible(report_id):
    if 'Manager' in user_groups():
        return
    q = db.chart_team_responsible.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to do this operation on the chart %s" % str(chart_id))

def report_responsible(report_id):
    if 'Manager' in user_groups():
        return
    q = db.report_team_responsible.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to do this operation on the report %s" % str(report_id))

#
def lib_charts_add_default_team_responsible(chart_id):
    group_id = user_default_group_id()
    db.chart_team_responsible.insert(chart_id=chart_id, group_id=group_id)

def lib_reports_add_default_team_responsible(report_id):
    group_id = user_default_group_id()
    db.report_team_responsible.insert(report_id=report_id, group_id=group_id)

#
def lib_metrics_add_default_team_publication(metric_id):
    group_id = user_default_group_id()
    db.metric_team_publication.insert(metric_id=metric_id, group_id=group_id)

def lib_charts_add_default_team_publication(chart_id):
    group_id = user_default_group_id()
    db.chart_team_publication.insert(chart_id=chart_id, group_id=group_id)

def lib_reports_add_default_team_publication(report_id):
    group_id = user_default_group_id()
    db.report_team_publication.insert(report_id=report_id, group_id=group_id)

#
def get_metric_id(metric_id):
    try:
        metric_id = int(metric_id)
        return metric_id
    except ValueError:
        pass
    q = db.metrics.metric_name == metric_id
    metric = db(q).select().first()
    if metric is None:
        return
    return metric.id

def get_chart_id(chart_id):
    try:
        chart_id = int(chart_id)
        return chart_id
    except ValueError:
        pass
    q = db.charts.chart_name == chart_id
    chart = db(q).select().first()
    if chart is None:
        return
    return chart.id

def get_report_id(report_id):
    try:
        report_id = int(report_id)
        return report_id
    except ValueError:
        pass
    q = db.reports.report_name == report_id
    report = db(q).select().first()
    if report is None:
        return
    return report.id

#
def lib_reports_add_to_git(report_id, content, otype="reports"):
    if content is None:
        return
    o = gittrack.gittrack(otype=otype)
    r = o.commit(report_id, content, author=user_name(email=True))

def lib_reports_revision(report_id, cid, otype="reports"):
    o = gittrack.gittrack(otype=otype)
    data = o.lstree_data(cid, report_id)
    oid = data[0]["oid"]
    return {"data": o.show_file_unvalidated(cid, oid, report_id)}

def lib_reports_revisions(id, otype="reports"):
    o = gittrack.gittrack(otype=otype)
    r = o.timeline([id])
    return {"data": r}

def lib_reports_diff(id, cid, other=None, otype="reports"):
    o = gittrack.gittrack(otype=otype)
    if other:
        r = o.diff_cids(id, cid, other, filename="reports")
    else:
        r = o.show(cid, id, numstat=True)
    return {"data": r}

def lib_reports_rollback(id, cid, otype="reports"):
    if otype == "reports":
        table = db.reports
        field = "report_yaml"
    elif otype == "charts":
        table = db.charts
        field = "chart_yaml"
    elif otype == "metrics":
        table = db.metrics
        field = "metric_sql"
    else:
        raise Exception("unsupported object type")
    o = gittrack.gittrack(otype=otype)
    r = o.rollback(id, cid, author=user_name(email=True))
    row = db(table["id"] == id).select().first()
    here_d = os.path.dirname(__file__)
    collect_d = os.path.join(here_d, '..', 'private', otype)
    with open(collect_d+"/"+report_id+"/"+otype, "r") as myfile:
        data=myfile.read()
    row.update_record(**{field:data})


