import re
import os
import yaml

dbro = DAL('mysql://readonly:readonly@dbopensvc/opensvc')

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

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
        return PRE(XML(val))

class table_metrics(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['metric_name',
                     'metric_sql',
                     'metric_col_value_index',
                     'metric_col_instance_index',
                     'metric_col_instance_label',
                     'metric_created',
                     'metric_author']
        self.colprops = {
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
        self.dbfilterable = False
        self.checkboxes = True
        self.extrarow = True
        self.extraline = True

        if 'Manager' in user_groups():
            self.additional_tools.append('add_metrics')


    def format_extrarow(self, o):
        d = DIV(
              A(
                _href=URL(r=request, c='charts', f='metrics_editor', vars={'metric_id': o.id}),
                _title=T("Edit metric"),
                _class="edit16",
              ),
              A(
                _onclick="""toggle_extra("%(url)s", "%(id)s")
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

        session.flash = T("Chart recorded")
        redirect(URL(r=request, c='charts', f='metrics_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_metric_test():
    q = db.metrics.id == request.vars.metric_id
    row = db(q).select().first()
    if row is None:
        return T("No metric request definition")
    try:
        rows = dbro.executesql(row.metric_sql)
    except Exception as e:
        return str(e)

    return format_test(rows, row)

def format_test(rows, m):
    n = len(rows)
    if n == 0:
        return T("No data")
    elif n == 1:
        return rows[0][m.metric_col_value_index]

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



def _metrics_cron(m):
    rows = dbro.executesql(m.metric_sql)

    now = datetime.datetime.now()
    for row in rows:
        if m.metric_col_instance_index is not None:
            instance = row[m.metric_col_instance_index]
            print "  insert", instance, row[m.metric_col_value_index]
        else:
            instance = None
            print "  insert", row[m.metric_col_value_index]

        mid = db.metrics_log.insert(
               date=now,
               metric_id=m.id,
               instance=instance,
               value=row[m.metric_col_value_index],
              )

def metrics_cron():
    q = db.metrics.id > 0
    rows = db(q).select()
    for row in rows:
        print "* metric:", row.metric_name
        try:
            _metrics_cron(row)
        except Exception as e:
            print e
            continue
    db.commit()
