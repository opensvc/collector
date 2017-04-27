import re
import os
import uuid
import yaml

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

###############################################################################
#
# Metrics
#
###############################################################################

class table_metrics(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.span = ['id']
        self.keys = ['id']
        self.cols = ['id',
                     'metric_name',
                     'metric_sql',
                     'metric_col_value_index',
                     'metric_col_instance_index',
                     'metric_col_instance_label',
                     'metric_historize',
                     'metric_created',
                     'metric_author']
        self.colprops = {
            'id': HtmlTableColumn(
                field = 'id',
                table = 'metrics',
            ),
            'metric_name': HtmlTableColumn(
                field = 'metric_name',
                table = 'metrics',
            ),
            'metric_historize': HtmlTableColumn(
                field = 'metric_historize',
                table = 'metrics',
            ),
            'metric_sql': HtmlTableColumn(
                field = 'metric_sql',
                table = 'metrics',
            ),
            'metric_created': HtmlTableColumn(
                field = 'metric_created',
                table = 'metrics',
            ),
            'metric_author': HtmlTableColumn(
                field = 'metric_author',
                table = 'metrics',
            ),
            'metric_col_value_index': HtmlTableColumn(
                field = 'metric_col_value_index',
                table = 'metrics',
            ),
            'metric_col_instance_index': HtmlTableColumn(
                field = 'metric_col_instance_index',
                table = 'metrics',
            ),
            'metric_col_instance_label': HtmlTableColumn(
                field = 'metric_col_instance_label',
                table = 'metrics',
            ),
        }
        self.ajax_col_values = 'ajax_metrics_admin_col_values'

@auth.requires_login()
def ajax_metrics_admin_col_values():
    table_id = request.vars.table_id
    t = table_metrics(table_id, 'ajax_metrics_admin')

    col = request.args[0]
    o = db.metrics[col]
    q = db.metrics.id > 0
    for f in t.cols:
        q = _where(q, 'metrics', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_metrics_admin():
    table_id = request.vars.table_id
    t = table_metrics(table_id, 'ajax_metrics_admin')

    o = t.get_orderby(default=db.metrics.metric_name)
    q = db.metrics.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def metrics_admin():
    t = SCRIPT(
          """table_metrics("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def metrics_admin_load():
    return metrics_admin()["table"]

###############################################################################
#
# Charts
#
###############################################################################

class table_charts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.span = ['id']
        self.keys = ['id']
        self.cols = ['id',
                     'chart_name',
                     'chart_yaml']
        self.colprops = {
            'chart_name': HtmlTableColumn(
                field = 'chart_name',
                table = 'charts',
            ),
            'chart_yaml': HtmlTableColumn(
                field = 'chart_yaml',
                table = 'charts',
            ),
            'id': HtmlTableColumn(
                field = 'id',
                table = 'charts',
            ),
        }
        self.ajax_col_values = 'ajax_charts_admin_col_values'

@auth.requires_login()
def ajax_charts_admin_col_values():
    table_id = request.vars.table_id
    t = table_charts(table_id, 'ajax_charts_admin')

    col = request.args[0]
    o = db.charts[col]
    q = db.charts.id > 0
    for f in t.cols:
        q = _where(q, 'charts', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_charts_admin():
    table_id = request.vars.table_id
    t = table_charts(table_id, 'ajax_charts_admin')

    o = t.get_orderby(default=db.charts.chart_name)
    q = db.charts.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def charts_admin():
    t = SCRIPT(
          """table_charts("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def charts_admin_load():
    return charts_admin()["table"]


###############################################################################
#
# Reports admin
#
###############################################################################

class table_reports_admin(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.span = ['id']
        self.keys = ['id']
        self.cols = ['id',
                     'report_name',
                     'report_yaml']
        self.colprops = {
            'report_name': HtmlTableColumn(
                field = 'report_name',
                table = 'reports',
            ),
            'report_yaml': HtmlTableColumn(
                field = 'report_yaml',
                table = 'reports',
            ),
            'id': HtmlTableColumn(
                field = 'id',
                table = 'reports',
            ),
        }
        self.ajax_col_values = 'ajax_reports_admin_col_values'

@auth.requires_login()
def ajax_reports_admin_col_values():
    table_id = request.vars.table_id
    t = table_reports_admin(table_id, 'ajax_reports_admin')

    col = request.args[0]
    o = db.reports[col]
    q = db.reports.id > 0
    if "Manager" not in user_groups():
        q &= db.reports.id.belongs(report_published_ids())
    for f in t.cols:
        q = _where(q, 'reports', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_reports_admin():
    table_id = request.vars.table_id
    t = table_reports_admin(table_id, 'ajax_reports_admin')

    o = t.get_orderby(default=db.reports.report_name)
    q = db.reports.id > 0
    if "Manager" not in user_groups():
        q &= db.reports.id.belongs(report_published_ids())
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def reports_admin():
    t = SCRIPT(
          """table_reports("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def reports_admin_load():
    return reports_admin()["table"]


@auth.requires_login()
def reports():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){reports("layout")})""",
        )
    return dict(table=t)

def reports_load():
    return reports()["table"]


#
# Batchs
#
def batch_task_metrics():
    task_metrics(verbose=True)
