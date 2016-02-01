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
        self.events = ["metrics_change"]
        self.span = ['id']
        self.keys = ['id']
        self.force_cols = ['id']
        self.cols = ['id',
                     'metric_name',
                     'metric_sql',
                     'metric_col_value_index',
                     'metric_col_instance_index',
                     'metric_col_instance_label',
                     'metric_created',
                     'metric_author']
        self.colprops = {
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'metrics',
                img = 'key'
            ),
            'metric_name': HtmlTableColumn(
                title = 'Name',
                field = 'metric_name',
                display = True,
                table = 'metrics',
                img = 'prov',
                _class='metric_name',
            ),
            'metric_sql': HtmlTableColumn(
                title = 'SQL request',
                field = 'metric_sql',
                display = True,
                table = 'metrics',
                img = 'action16',
                _class = 'sql',
            ),
            'metric_created': HtmlTableColumn(
                title = 'Created on',
                field = 'metric_created',
                display = False,
                table = 'metrics',
                img = 'time16'
            ),
            'metric_author': HtmlTableColumn(
                title = 'Author',
                field = 'metric_author',
                display = False,
                table = 'metrics',
                img = 'guy16'
            ),
            'metric_col_value_index': HtmlTableColumn(
                title = 'Value column index',
                field = 'metric_col_value_index',
                display = True,
                table = 'metrics',
                img = 'action16'
            ),
            'metric_col_instance_index': HtmlTableColumn(
                title = 'Instance column index',
                field = 'metric_col_instance_index',
                display = True,
                table = 'metrics',
                img = 'action16'
            ),
            'metric_col_instance_label': HtmlTableColumn(
                title = 'Instance label',
                field = 'metric_col_instance_label',
                display = True,
                table = 'metrics',
                img = 'action16'
            ),
        }
        self.ajax_col_values = 'ajax_metrics_admin_col_values'
        self.dbfilterable = True
        self.dataable = True
        self.wsable = True
        self.checkboxes = True
        self.extraline = True
        self.events = ["metrics_change"]

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

    o = db.metrics.metric_name
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
          """$.when(osvc.app_started).then(function(){ table_metrics("layout", %s) })""" % request_vars_to_table_options(),
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
        self.events = ["charts_change"]
        self.span = ['id']
        self.keys = ['id']
        self.force_cols = ['id']
        self.cols = ['id',
                     'chart_name',
                     'chart_yaml']
        self.colprops = {
            'chart_name': HtmlTableColumn(
                title = 'Name',
                field = 'chart_name',
                display = True,
                table = 'charts',
                img = 'spark16',
                _class = 'chart_name',
            ),
            'chart_yaml': HtmlTableColumn(
                title = 'Definition',
                field = 'chart_yaml',
                display = True,
                table = 'charts',
                img = 'log16',
                _class = 'yaml',
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'charts',
                img = 'key'
            ),
        }
        self.ajax_col_values = 'ajax_charts_admin_col_values'
        self.dbfilterable = True
        self.checkboxes = True
        self.dataable = True
        self.wsable = True
        self.extraline = True

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

    o = db.charts.chart_name
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
          """$.when(osvc.app_started).then(function(){ table_charts("layout", %s) })""" % request_vars_to_table_options(),
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
        self.events = ["reports_change"]
        self.span = ['id']
        self.keys = ['id']
        self.force_cols = ['id']
        self.cols = ['id',
                     'report_name',
                     'report_yaml']
        self.colprops = {
            'report_name': HtmlTableColumn(
                title = 'Name',
                field = 'report_name',
                display = True,
                table = 'reports',
                img = 'spark16',
                _class='report_name',
            ),
            'report_yaml': HtmlTableColumn(
                title = 'Definition',
                field = 'report_yaml',
                display = True,
                table = 'reports',
                img = 'log16',
                _class='yaml',
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'reports',
                img = 'key'
            ),
        }
        self.ajax_col_values = 'ajax_reports_admin_col_values'
        self.dbfilterable = True
        self.dataable = True
        self.wsable = True
        self.checkboxes = True
        self.extraline = True

@auth.requires_login()
def ajax_reports_admin_col_values():
    table_id = request.vars.table_id
    t = table_reports_admin(table_id, 'ajax_reports_admin')

    col = request.args[0]
    o = db.reports[col]
    q = db.reports.id > 0
    for f in t.cols:
        q = _where(q, 'reports', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_reports_admin():
    table_id = request.vars.table_id
    t = table_reports_admin(table_id, 'ajax_reports_admin')

    o = db.reports.report_name
    q = db.reports.id > 0
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
          """$.when(osvc.app_started).then(function(){ table_reports("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def reports_admin_load():
    return reports_admin()["table"]


@auth.requires_login()
def reports():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ reports("layout") })""",
        )
    return dict(table=t)

def reports_load():
    return reports()["table"]


#
# Batchs
#
def batch_task_metrics():
    task_metrics()
