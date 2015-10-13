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

class col_metrics_sql(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        regex = re.compile(r'(SELECT|FROM|GROUP BY|WHERE)', re.I)
        val = re.sub(regex, r'<span class=syntax_red>\1</span>', val)
        regex = re.compile(r'(COUNT|DATE_SUB|SUM|MAX|MIN|CEIL|FLOOR|AVG|CONCAT|GROUP_CONCAT)', re.I)
        val = re.sub(regex, r'<span class=syntax_green>\1</span>', val)
        regex = re.compile(r'=(\'\w*\')', re.I)
        val = re.sub(regex, r'=<span class=syntax_blue>\1</span>', val)
        regex = re.compile(r'=(\"\w*\")', re.I)
        val = re.sub(regex, r'=<span class=syntax_blue>\1</span>', val)
        regex = re.compile(r'(%%\w+%%)', re.I)
        val = re.sub(regex, r'<span class=syntax_blue>\1</span>', val)
        return PRE(XML(val))

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
                     'metric_created',
                     'metric_author']
        self.colprops = {
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'metrics',
                img = 'prov'
            ),
            'metric_name': HtmlTableColumn(
                title = 'Name',
                field = 'metric_name',
                display = True,
                table = 'metrics',
                img = 'prov'
            ),
            'metric_sql': col_metrics_sql(
                title = 'SQL request',
                field = 'metric_sql',
                display = True,
                table = 'metrics',
                img = 'action16'
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
        self.checkboxes = False
        self.extrarow = True
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_metrics')


    def format_extrarow(self, o):
        d = DIV(
              A(
                "",
                _href=URL(r=request, c='charts', f='metrics_editor', vars={'metric_id': o.id}),
                _title=T("Edit metric"),
                _class="edit16",
              ),
              A(
                _onclick="""toggle_extra("%(url)s", "%(id)s", this, 0)
                """%dict(
                     url=URL(r=request, c='charts', f='ajax_metric_test', vars={'metric_id': o.id}),
                     id=self.extra_line_key(o),
                    ),
                _title=T("Test request"),
                _class="action16",
              ),
            )
        return d

    def add_metrics(self):
        d = DIV(
              A(
                T("Add metric"),
                _href=URL(r=request, f='metrics_editor'),
                _class='add16',
              ),
              _class='floatw',
            )
        return d

@auth.requires_membership('Manager')
def metrics_editor():
    q = db.metrics.id == request.vars.metric_id
    rows = db(q).select()

    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    db.metrics.metric_author.default = user_name()
    form = SQLFORM(db.metrics,
                 record=record,
                 deletable=True,
                 fields=['metric_name',
                         'metric_sql',
                         'metric_col_value_index',
                         'metric_col_instance_index',
                         'metric_col_instance_label',],
                 labels={'metric_name': T('Metric name'),
                         'metric_sql': T('Metric SQL request'),
                         'metric_col_value_index': T('Metric value column index'),
                         'metric_col_instance_index': T('Metric instance column index'),
                         'metric_col_instance_label': T('Metric instance label'),
                        }
                )
    form.custom.widget.metric_sql['_class'] = 'pre'
    form.custom.widget.metric_sql['_style'] = 'min-width:60em;min-height:60em'
    if form.accepts(request.vars):
        if request.vars.metric_id is None:
            _log('metric.add',
                 "Created metric '%(metric_name)s' with definition:\n%(metric_sql)s",
                     dict(metric_name=request.vars.metric_name,
                          metric_sql=request.vars.metric_sql))
        elif request.vars.delete_this_record == 'on':
            _log('metric.delete',
                 "Deleted metric '%(metric_name)s' with definition:\n%(metric_sql)s",
                     dict(metric_name=request.vars.metric_name,
                          metric_sql=request.vars.metric_sql))
        else:
            _log('metric.change',
                 "Changed metric '%(metric_name)s' with definition:\n%(metric_sql)s",
                     dict(metric_name=request.vars.metric_name,
                          metric_sql=request.vars.metric_sql))

        session.flash = T("Metric recorded")
        redirect(URL(r=request, c='charts', f='metrics_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_metric_test():
    return format_metric(request.vars.metric_id)

@auth.requires_login()
def metric():
    return dict(table=format_metric(request.vars.metric_id))

def format_metric(metric_id):
    q = db.metrics.id == metric_id
    row = db(q).select().first()
    if row is None:
        return T("No metric request definition")
    sql = replace_fset_sql(row.metric_sql)
    if row.metric_col_instance_index is None or row.metric_col_value_index is None:
        as_dict = True
    else:
        as_dict = False
    try:
        rows = dbro.executesql(sql, as_dict=as_dict)
    except Exception as e:
        return str(e)

    link = DIV(
             A(
               IMG(_src=URL(r=request, c='static', f='images/link16.png')),
               _onclick="""$(this).siblings().toggle()""",
             ),
             DIV(
               "https://"+request.env.http_host+URL(r=request, f='metric', vars={'metric_id': metric_id}),
               _style="display:none",
             ),
           )
    return DIV(
             link,
             _format_metric(rows, row)
           )

def _format_metric(rows, m):
    n = len(rows)
    if n == 0:
        return T("No data")

    if n == 1 and type(rows[0]) == list:
        if m.metric_col_value_index > len(rows[0])-1:
            response. flash = T("metric column value index (%(idx)s) out of range: %(data)s", dict(idx=str(m.metric_col_value_index), data=str(rows[0])))
        else:
            return rows[0][m.metric_col_value_index]

    if m.metric_col_instance_index is None or m.metric_col_value_index is None:
        l = [TR(map(lambda x: TH(x), rows[0].keys()))]
        for row in rows:
            l.append(map(lambda x: TD(x), row.values()))
        return TABLE(l)

    l = [TR(TH(m.metric_col_instance_label), TH(T("Value")))]
    for row in rows:
        l.append(TR(TD(row[m.metric_col_instance_index]), TD(row[m.metric_col_value_index])))

    return TABLE(l)

@auth.requires_login()
def ajax_metrics_admin_col_values():
    t = table_metrics('metrics', 'ajax_metrics_admin')

    col = request.args[0]
    o = db.metrics[col]
    q = db.metrics.id > 0
    for f in t.cols:
        q = _where(q, 'metrics', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_metrics_admin():
    t = table_metrics('metrics', 'ajax_metrics_admin')

    o = db.metrics.metric_name
    q = db.metrics.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, limitby=limitby)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def metrics_admin():
    t = DIV(
          ajax_metrics_admin(),
          _id='metrics',
        )
    return dict(table=t)


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
        self.span = ['id']
        self.keys = ['id']
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
                img = 'log16'
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'charts',
                img = 'spark16'
            ),
        }
        self.ajax_col_values = 'ajax_charts_admin_col_values'
        self.dbfilterable = True
        self.checkboxes = False
        self.extrarow = True
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_chart')

    def format_extrarow(self, o):
        d = DIV(
              A(
                "",
                _href=URL(r=request, c='charts', f='charts_editor', vars={'chart_id': o.id}),
                _title=T("Edit chart"),
                _class="edit16",
              ),
              A(
                _onclick="""toggle_extra("%(url)s", "%(id)s", this, 0)
                """%dict(
                     url=URL(r=request, c='charts', f='ajax_chart_test', vars={'chart_id': o.id}),
                     id=self.extra_line_key(o),
                    ),
                _title=T("Test chart"),
                _class="action16",
              ),
            )
        return d

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
def ajax_chart_test():
    return ajax_chart_plot(request.vars.chart_id)

@auth.requires_login()
def chart():
    return dict(table=ajax_chart_plot(request.vars.chart_id))

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

    if len(request.args) == 1 and request.args[0] == 'line':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, limitby=limitby)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def charts_admin():
    t = DIV(
          ajax_charts_admin(),
          _id='charts',
        )
    return dict(table=t)

def get_chart(chart_id):
    q = db.charts.id == chart_id
    chart = db(q).select().first()
    if chart is None:
        return
    try:
        chart_yaml = yaml.load(chart.chart_yaml)
    except Exception as e:
        return
    chart.chart_yaml = chart_yaml
    return chart

@auth.requires_login()
def ajax_chart_plot(chart_id):
    fset_id = user_fset_id()
    uid = uuid.uuid1().hex
    s = """charts_plot('%(url)s', '%(id)s');"""%dict(
      id="c%s"%str(uid),
      url=URL(r=request, c='charts', f='call/json/json_chart_data', args=[chart_id, fset_id]),
    )

    chart = get_chart(chart_id)
    if chart is None:
        return T("chart not found")

    title = chart.chart_yaml.get('Title')
    if title is None:
        title = SPAN()
    else:
        title = DIV(H3(T(title)))

    link = DIV(
             A(
               IMG(_src=URL(r=request, c='static', f='images/link16.png')),
               _onclick="""$(this).siblings().toggle()""",
             ),
             DIV(
               "https://"+request.env.http_host+URL(r=request, f='chart', vars={'chart_id': chart_id}),
               _style="display:none",
             ),
           )

    d = DIV(
      link,
      title,
      DIV(
        _id="c%s"%str(uid),
        _style="width:600px",
      ),
      SCRIPT(s),
      _class="chart",
    )
    return d

@service.json
def json_chart_data(chart_id, fset_id):
    q = db.charts.id == int(chart_id)
    chart = db(q).select().first()

    if chart is None:
        return

    try:
        chart_data = yaml.load(chart.chart_yaml)
    except:
        return

    l = []
    instances = []
    options = {
      'stack': False,
    }
    _options = chart_data.get('Options', {})
    if _options is None:
        _options = {}
    options.update(_options)

    for m in chart_data['Metrics']:
        h = get_metric_series(m['metric_id'], fset_id)
        for instance, series in h.items():
            l.append(series)
            i = {
              'label': instance,
              'fill': m.get('fill'),
              'shadow': m.get('shadow'),
              'unit': m.get('unit', ''),
            }
            instances.append(i)

    return {'data': l, 'instances': instances, 'options': options}

def get_metric_series(metric_id, fset_id):
    q = db.metrics_log.metric_id == int(metric_id)
    q &= db.metrics_log.fset_id == int(fset_id)
    rows = db(q).select(db.metrics_log.date,
                        db.metrics_log.value,
                        db.metrics_log.instance)
    h = {}
    for row in rows:
        if row.instance is None or len(row.instance) == 0:
            instance = "empty"
        else:
            instance = row.instance
        if instance not in h:
            h[instance] = [[row.date, row.value]]
        else:
            h[instance].append([row.date, row.value])
    return h


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
                title = 'Name',
                field = 'report_name',
                display = True,
                table = 'reports',
                img = 'spark16'
            ),
            'report_yaml': col_yaml(
                title = 'Definition',
                field = 'report_yaml',
                display = True,
                table = 'reports',
                img = 'log16'
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = True,
                table = 'reports',
                img = 'spark16'
            ),
        }
        self.ajax_col_values = 'ajax_reports_admin_col_values'
        self.dbfilterable = True
        self.checkboxes = False
        self.extrarow = True
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_report')

    def format_extrarow(self, o):
        d = DIV(
              A(
                "",
                _href=URL(r=request, c='charts', f='reports_editor', vars={'report_id': o.id}),
                _title=T("Edit report"),
                _class="edit16",
              ),
              A(
                _onclick="""toggle_extra("%(url)s", "%(id)s", this, 0)
                """%dict(
                     url=URL(r=request, c='charts', f='ajax_report_test', vars={'report_id': o.id}),
                     id=self.extra_line_key(o),
                    ),
                _title=T("Test report"),
                _class="action16",
              ),
            )
        return d

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
def report():
    return dict(table=ajax_report(request.vars.report_id))

@auth.requires_login()
def ajax_report_test():
    return ajax_report(request.vars.report_id)

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

    if len(request.args) == 1 and request.args[0] == 'line':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, limitby=limitby)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def reports_admin():
    t = DIV(
          ajax_reports_admin(),
          _id='reports',
        )
    return dict(table=t)

@auth.requires_login()
def ajax_report(report_id):
    q = db.reports.id == report_id
    report = db(q).select().first()
    if report is None:
        return T("Report not found")

    try:
        report.report_yaml = yaml.load(report.report_yaml)
    except Exception as e:
        return T('Report definition error')+": "+str(e)

    return do_report(report_id, report.report_yaml)

def do_report(report_id, report_yaml):
    link = DIV(
             A(
               IMG(_src=URL(r=request, c='static', f='images/link16.png')),
               _onclick="""$(this).siblings().toggle()""",
             ),
             DIV(
               "https://"+request.env.http_host+URL(r=request, f='report', vars={'report_id': report_id}),
               _style="display:none",
             ),
           )

    d = [link, H1(report_yaml.get('Title', ''))]
    for section in report_yaml.get('Sections', []):
        s = do_section(section)
        _d = DIV(
          s,
          _class="container",
        )
        d.append(_d)
    return DIV(d)

def do_section(section_yaml):
    d = [H2(section_yaml.get('Title', ''))]
    d.append(I(section_yaml.get('Desc', '')))
    d.append(DIV(_class="spacer", _style="height:100px"))
    for chart in section_yaml.get('Charts', []):
        chart_id = chart.get('chart_id')
        if chart_id is None:
            continue
        c = ajax_chart_plot(chart_id)
        _d = DIV(
           c,
           _class="float",
           #_style="width:400px;height:300px",
        )
        d.append(H3(chart.get('Title', '')))
        d.append(_d)

    for metric in section_yaml.get('Metrics', []):
        metric_id = metric.get('metric_id')
        if metric_id is None:
            continue
        d.append(H3(metric.get('Title', '')))
        d.append(I(metric.get('Desc', '')))
        d.append(format_metric(metric_id))

    d.append(DIV(_class="spacer", _style="height:100px"))
    return SPAN(d)


###############################################################################
#
# Reports
#
###############################################################################

class table_reports(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.dbfilterable = True
        self.refreshable = False
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.exportable = False
        self.linkable = False
        self.bookmarkable = False
        self.columnable = False
        self.object_list = []
        self.nodatabanner = False
        self.additional_tools.append('report')

    def format_report_option(self, row):
        if row is None:
            name = T("None")
            report_id = 0
        else:
            name = row.report_name
            report_id = row.id
        return OPTION(
                 name,
                 _value=report_id,
               )

    def get_current_report(self):
        q = db.report_user.user_id == auth.user_id
        row = db(q).select().first()
        if row is None:
            active_report_id = 0
        else:
            active_report_id = row.report_id
        return active_report_id

    def report_selector(self):
        #active_report_id = get_current_report()
        active_report_id = None

        # create the report select()
        q = db.reports.id > 0
        rows = db(q).select(db.reports.id,
                            db.reports.report_name)
        av = [self.format_report_option(None)]
        for row in rows:
            av.append(self.format_report_option(row))
        content = SELECT(
                    av,
                    value=active_report_id,
                    _onchange="""
                       sync_ajax('%(url)s?report_id='+this.options[this.selectedIndex].value, [], '%(div)s', function(){});
                    """%dict(url=URL(
                                   r=request, c='charts',
                                   f='ajax_report_test',
                                ),
                              div="reports_div",
                             ),
                  )

        return SPAN(
                 T('Report'),
                 content,
                 _class='floatw',
               )

    def report(self):
        return self.report_selector()

@auth.requires_login()
def ajax_reports():
    t = table_reports('reports', 'ajax_reports')
    d = DIV(
     DIV(
       t.html(),
       _id="reports",
     ),
     DIV(
       _id="reports_div",
     )
    )
    return d

@auth.requires_login()
def reports():
    return dict(table=ajax_reports())

def batch_task_metrics():
    task_metrics()
