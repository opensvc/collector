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

class col_yaml(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        val = re.sub(r'(%\(\w+\)s)', r'<span class=syntax_red>\1</span>', val)
        val = re.sub(r'(\w+:)', r'<span class=syntax_green>\1</span>', val)
        return PRE(XML(val))

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
                img = 'spark16'
            ),
            'chart_yaml': col_yaml(
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
        self.checkboxes = False
        self.dataable = True
        self.wsable = True
        self.extrarow = True
        self.extrarow_class = 'charts_links'
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_chart')

    def format_extrarow(self, o):
        d = ""

    def add_chart(self):
        d = DIV(
              A(
                T("Add chart"),
                _href=URL(r=request, f='charts_editor'),
                _class='add16',
              ),
              _class='floatw',
            )
        return d

@auth.requires_membership('Manager')
def charts_editor():
    q = db.charts.id == request.vars.chart_id
    rows = db(q).select()

    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    form = SQLFORM(db.charts,
                 record=record,
                 deletable=True,
                 fields=['chart_name',
                         'chart_yaml',],
                 labels={'chart_name': T('Chart name'),
                         'chart_yaml': T('Chart definition'),
                        }
                )
    form.custom.widget.chart_yaml['_class'] = 'pre'
    form.custom.widget.chart_yaml['_style'] = 'min-width:60em;min-height:60em'
    if form.accepts(request.vars):
        if request.vars.chart_id is None:
            _log('chart.add',
                 "Created chart '%(chart_name)s' with definition:\n%(chart_yaml)s",
                     dict(chart_name=request.vars.chart_name,
                          chart_yaml=request.vars.chart_yaml))
        elif request.vars.delete_this_record == 'on':
            _log('chart.delete',
                 "Deleted chart '%(chart_name)s' with definition:\n%(chart_yaml)s",
                     dict(chart_name=request.vars.chart_name,
                          chart_yaml=request.vars.chart_yaml))
        else:
            _log('chart.change',
                 "Changed chart '%(chart_name)s' with definition:\n%(chart_yaml)s",
                     dict(chart_name=request.vars.chart_name,
                          chart_yaml=request.vars.chart_yaml))

        session.flash = T("Chart recorded")
        redirect(URL(r=request, c='charts', f='charts_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_charts_admin_col_values():
    t = table_charts('charts', 'ajax_charts_admin')

    col = request.args[0]
    o = db.charts[col]
    q = db.charts.id > 0
    for f in t.cols:
        q = _where(q, 'charts', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_charts_admin():
    t = table_charts('charts', 'ajax_charts_admin')

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
    t = table_charts('charts', 'ajax_charts_admin')
    t = DIV(
          t.html(),
          _id='charts',
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
                img = 'spark16'
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
        self.checkboxes = False
        self.extrarow = True
        self.extrarow_class = 'reports_links'
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_report')

    def format_extrarow(self, o):
        d = ''

    def add_report(self):
        d = DIV(
              A(
                T("Add report"),
                _href=URL(r=request, f='reports_editor'),
                _class='add16',
              ),
              _class='floatw',
            )
        return d

@auth.requires_membership('Manager')
def reports_editor():
    q = db.reports.id == request.vars.report_id
    rows = db(q).select()

    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    form = SQLFORM(db.reports,
                 record=record,
                 deletable=True,
                 fields=['report_name',
                         'report_yaml',],
                 labels={'report_name': T('Chart name'),
                         'report_yaml': T('Chart definition'),
                        }
                )
    form.custom.widget.report_yaml['_class'] = 'pre'
    form.custom.widget.report_yaml['_style'] = 'min-width:60em;min-height:60em'
    if form.accepts(request.vars):
        if request.vars.report_id is None:
            _log('report.add',
                 "Created report '%(report_name)s' with definition:\n%(report_yaml)s",
                     dict(report_name=request.vars.report_name,
                          report_yaml=request.vars.report_yaml))
        elif request.vars.delete_this_record == 'on':
            _log('report.delete',
                 "Deleted report '%(report_name)s' with definition:\n%(report_yaml)s",
                     dict(report_name=request.vars.report_name,
                          report_yaml=request.vars.report_yaml))
        else:
            _log('report.change',
                 "Changed report '%(report_name)s' with definition:\n%(report_yaml)s",
                     dict(report_name=request.vars.report_name,
                          report_yaml=request.vars.report_yaml))

        session.flash = T("Report recorded")
        redirect(URL(r=request, c='charts', f='reports_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_reports_admin_col_values():
    t = table_reports_admin('reports', 'ajax_reports_admin')

    col = request.args[0]
    o = db.reports[col]
    q = db.reports.id > 0
    for f in t.cols:
        q = _where(q, 'reports', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_reports_admin():
    t = table_reports_admin('reports', 'ajax_reports_admin')

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
    t = table_reports_admin('reports', 'ajax_reports_admin')
    t = DIV(
          t.html(),
          _id='reports',
        )
    return dict(table=t)

def reports_admin_load():
    return reports_admin()["table"]


@auth.requires_login()
def reports():
    d = DIV(
          DIV(
           _id="reports_div",
          ),
          SCRIPT( """reports('reports_div');""")
        )
    return dict(table=d)

def reports_load():
    return reports()["table"]

def batch_task_metrics():
    task_metrics()
