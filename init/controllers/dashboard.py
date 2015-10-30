def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

class col_dash_chart(HtmlTableColumn):
    def html(self, o):
       h = self.get(o)
       if len(h['nb']) < 2:
           return SPAN()
       return DIV(
                DIV(
                  H3(T("Alerts severity")),
                  DIV(
                    json.dumps(h['sev']),
                    _id='sev_chart',
                  ),
                  _style="float:left;width:350px",
                ),
                DIV(
                  H3(T("Number of alerts")),
                  DIV(
                    h['nb'],
                    _id='nb_chart',
                    _style="float:left;width:350px;padding:1em",
                  ),
                  DIV(
                    _id='chart_info',
                  ),
                  _style="float:left;width:350px;margin-left:1em",
                ),
              )

def spark_data(data):
    if len(data) == 0:
        l = [None]
    elif len(data) == 1:
        l = [str(data[0][1])]
    else:
        d = {}
        l = []
        last_value = data[-1][1]
        begin = data[0][0]
        if begin == 0:
            return str(data[0][1])
        if begin > 20:
            begin = 20
        for a, b in data:
            d[a] = b
        for i in range(0, begin):
            if i in d:
                l.append(d[i])
                last_value = d[i]
            else:
                #l.append(last_value)
                l.append(None)
        l.reverse()
    return l

def html_bar(val, total):
    if total ==  0:
        p = 0
    else:
        p = 100-100*val/total
    p = "%d%%"%int(p)
    n = "%d"%(val)
    d = DIV(
          DIV(
            DIV(
              _style="""font-size: 0px;
                        line-height: 0px;
                        height: 4px;
                        min-width: 0%%;
                        max-width: %(p)s;
                        width: %(p)s;
                        background: #dddddd;
                     """%dict(p=p),
            ),
            _style="""text-align: left;
                      margin: 2px auto;
                      background: #FF7863;
                      overflow: hidden;
                   """,
          ),
          DIV(n),
          _style="""margin: auto;
                    text-align: right;
                    width: 100%;
                 """,
        )
    return d

class table_dash_agg(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops = {
            'chart': col_dash_chart(
                     title='Chart',
                     field='chart',
                     display=True,
                     img='spark16',
                    ),
        }
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.exportable = False
        self.bookmarkable = False
        self.linkable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False
        self.highlight = False


def ajax_dash_history():
    session.forget(response)
    id = request.vars.divid
    id_chart = 'dh_chart'
    d = DIV(
          DIV(
            #IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id=id_chart,
            _style="height:300px",
          ),
          SCRIPT(
            "dash_history('%(url)s', '%(id)s');"%dict(
               url=URL(r=request, f='call/json/json_dash_history'),
               id=id_chart,
            ),
            _name='dh_to_eval'
          ),
        )
    return d

@service.json
def json_dash_history():
    t = table_dashboard('dashboard', 'ajax_dashboard')

    q = db.dashboard_events.id > 0
    for f in set(t.cols):
        if f == 'dash_created':
            continue
        if t.colprops[f].filter_redirect is not None:
            _f = t.colprops[f].filter_redirect
            _t = "dashboard_ref"
        elif f == "dash_type":
            _f = f
            _t = "dashboard_ref"
        else:
            _f = f
            _t = "dashboard_events"
        q = _where(q, _t, t.filter_parse(f),  _f)
    q &= _where(None, 'dashboard_events', domain_perms(), 'dash_svcname')|_where(None, 'dashboard_events', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard_events.dash_nodename, db.dashboard_events.dash_svcname)

    sql = """select
               v.begin,
               count(v.begin)
             from (
               select
                 t.begin,
                 t.end,
                 dashboard_events.dash_md5,
                 dashboard_events.dash_nodename,
                 dashboard_events.dash_svcname
               from
                 dashboard_events
                 join (
                   select
                     date(date_sub(now(), interval inc-1 day)) as begin,
                     date(date_sub(now(), interval inc-2 day)) as end
                   from
                     u_inc
                   where
                     inc<=10
                   order by inc desc
                 ) t on
                   dashboard_events.dash_begin <= t.end and
                   (dashboard_events.dash_end >= t.begin or dashboard_events.dash_end is null)
                 join dashboard_ref on
                   dashboard_events.dash_md5 = dashboard_ref.dash_md5
               where %(where)s
               group by
                 t.begin,
                 t.end,
                 dashboard_events.dash_md5,
                 dashboard_events.dash_nodename,
                 dashboard_events.dash_svcname
             ) v
             group by v.begin, v.end
    """%dict(where=str(q))
    rows = db.executesql(sql)
    data = []
    for row in rows:
        data.append((row[0], row[1]))
    return data

@auth.requires_login()
def ajax_dash_agg():
    session.forget(response)
    t = table_dashboard('dashboard', 'ajax_dashboard')
    mt = table_dash_agg('dash_agg', 'ajax_dash_agg')

    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)

    sql1 = db(q)._select().rstrip(';').replace('services.id, ','').replace('nodes.id, ','').replace('dashboard.id>0 AND', '')
    regex = re.compile("SELECT .* FROM dashboard")
    sql1 = regex.sub('', sql1)

    q = db.dash_agg.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("dash_agg.", "dashboard.")

    mt.additional_inputs = t.ajax_inputs()

    h = {'nb': [], 'sev': []}

    sql2 = """ select
                  dashboard.dash_type,
                  count(dashboard.dash_type)
                from dashboard ignore index (idx1)
                  %(sql)s
                group by dash_type
              """%dict(
                sql=sql1,
                where=where,
           )
    rows = db.executesql(sql2)

    _h = {}
    for r in rows:
        _h[r[0]] = r[1]

    max = 0
    for n in _h.values():
        if n > max: max = n
    min = max
    for n in _h.values():
        if n < min: min = n
    delta = max - min

    l = []
    for s, n in _h.items():
        if delta > 0:
            size = 100 + 100. * (n - min) / delta
        else:
            size = 100
        if n == 1:
            title = "%d occurence"%n
        else:
            title = "%d occurences"%n
        attr = {
          '_class': "cloud_tag",
          '_style': "font-size:%d%%"%size,
          '_title': "%d occurences"%n,
          '_onclick': """
$("#dashboard_f_dash_type").val('%(s)s')
%(submit)s"""%dict(submit=t.ajax_submit(), s=s),
        }
        l.append(A(
                   T(s)+' ',
                   **attr
                ))
    h['nb'] = DIV(l)

    sql2 = """ select
                  dashboard.id,
                  dashboard.dash_severity,
                  count(dashboard.id)
                from dashboard ignore index (idx1)
                  %(sql)s
                group by dash_severity
              """%dict(
                sql=sql1,
                where=where,
           )

    rows = db.executesql(sql2)

    l = map(lambda x: {'dash_severity': x[1],
                       'dash_alerts':x[2]},
             rows)

    for line in l:
        s = T.translate("Severity %(s)s", dict(s=line['dash_severity']))
        h['sev'].append([s, int(line['dash_alerts'])])
    h['sev'].sort(lambda x, y: cmp(y[0], x[0]))

    mt.object_list = [{'chart': h}]

    from hashlib import md5
    o = md5()
    o.update(sql1)
    filters_md5 = str(o.hexdigest())

    q = db.dashboard_log.dash_filters_md5==filters_md5
    row = db(q).select(db.dashboard_log.dash_date,
                       orderby=~db.dashboard_log.id,
                       limitby=(0,1)).first()

    now = datetime.datetime.now()

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()

    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)


    return DIV(
             mt.html(),
             SCRIPT("""osvc.tables["dash_agg"]["on_change"] = plot_dashpie_sev; plot_dashpie_sev() """),
           )

@service.json
def update_dashboard_log(s):
    try:
        md5, dash_type = s.split('-')
        dash_type = dash_type.replace("_", " ")
    except:
        return [None]

    """ Insert a datapoint in dashboard_log with
        the same value as the last point for dash_filters_md5/dash_type
        If a point already has been inserted in the last minute, skip.
    """
    sql = """insert into dashboard_log
               select
                 NULL,
                 dash_type,
                 dash_filters_md5,
                 dash_alerts,
                 now()
               from dashboard_log
               where
                 dash_filters_md5="%(md5)s" and
                 dash_type="%(dash_type)s" and
                 dash_date < date_sub(now(), interval 1 minute)
               order by dash_date desc
               limit 1
          """%dict(md5=md5, dash_type=dash_type)
    db.executesql(sql)
    with open("/tmp/bar", "w") as f:
        f.write(sql+'\n')

    now = datetime.datetime.now()
    thisminute = now.toordinal()*1440+now.hour*60+now.minute

    q = db.dashboard_log.dash_filters_md5 == md5
    q &= db.dashboard_log.dash_type == dash_type
    q &= db.dashboard_log.dash_date > now - datetime.timedelta(minutes=21)
    rows = db(q).select()
    data = []
    for row in rows:
        rowminute = row.dash_date.toordinal()*1440+row.dash_date.hour*60+row.dash_date.minute
        data.append((thisminute-rowminute,
                     row.dash_alerts))

    return s, spark_data(data)


#############################################################################


class col_dash_entry(HtmlTableColumn):
    def get(self, o):
        dash_dict = self.t.colprops['dash_dict'].get(o)
        dash_fmt = self.t.colprops['dash_fmt'].get(o)
        if dash_dict is None or len(dash_dict) == 0:
            return ""
        try:
            d = json.loads(dash_dict)
            for k in d:
                if isinstance(d[k], str) or isinstance(d[k], unicode):
                    d[k] = d[k].encode('utf8')
            s = T.translate(dash_fmt, d)
        except KeyError:
            s = 'error parsing: %s'%dash_dict
        except json.decoder.JSONDecodeError:
            s = 'error loading JSON: %s'%dash_dict
        except UnicodeEncodeError:
            s = 'error transcoding: %s'%dash_dict
        except TypeError:
            s = 'type error: %s'%dash_dict
        return s

class table_dashboard(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'dash_severity',
                     'dash_links',
                     'dash_type',
                     'dash_svcname',
                     'dash_nodename',
                     'dash_env',
                     'dash_entry',
                     'dash_created',
                     'dash_updated',
                     'dash_md5']
        self.colprops = {
            'dash_links': HtmlTableColumn(
                     title='Links',
                     field='dummy',
                     img='link16',
                     display=True,
                     _class="dash_links",
                    ),
            'dash_created': HtmlTableColumn(
                     title='Begin date',
                     table='dashboard',
                     field='dash_created',
                     img='time16',
                     display=True,
                    ),
            'dash_updated': HtmlTableColumn(
                     title='Last update',
                     table='dashboard',
                     field='dash_updated',
                     img='time16',
                     display=True,
                    ),
            'dash_severity': HtmlTableColumn(
                     title='Severity',
                     table='dashboard',
                     field='dash_severity',
                     img='action16',
                     display=True,
                     _class='dash_severity',
                    ),
            'dash_svcname': HtmlTableColumn(
                     title='Service',
                     table='dashboard',
                     field='dash_svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'dash_nodename': HtmlTableColumn(
                     title='Node',
                     table='dashboard',
                     field='dash_nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'dash_entry': col_dash_entry(
                     title='Alert',
                     table='dashboard',
                     field='dummy',
                     filter_redirect='dash_dict',
                     img='log16',
                     display=True,
                     _class='dash_entry',
                    ),
            'dash_env': HtmlTableColumn(
                     title='Env',
                     table='dashboard',
                     field='dash_env',
                     img='svc',
                     display=True,
                     _class='env',
                    ),
            'dash_fmt': HtmlTableColumn(
                     title='Format',
                     table='dashboard',
                     field='dash_fmt',
                     img='log16',
                     display=False,
                    ),
            'dash_md5': HtmlTableColumn(
                     title='Alert md5',
                     table='dashboard',
                     field='dash_md5',
                     img='log16',
                     display=False,
                    ),
            'dash_dict': HtmlTableColumn(
                     title='Dictionary',
                     table='dashboard',
                     field='dash_dict',
                     img='log16',
                     display=False,
                    ),
            'dash_type': HtmlTableColumn(
                     title='Type',
                     table='dashboard',
                     field='dash_type',
                     img='log16',
                     display=True,
                    ),
            'dash_md5': HtmlTableColumn(
                     title='Signature',
                     table='dashboard',
                     field='dash_md5',
                     img='log16',
                     display=False,
                    ),
            'id': HtmlTableColumn(
                     title='Alert id',
                     table='dashboard',
                     field='id',
                     img='log16',
                     display=False,
                    ),
        }
        self.keys = ["dash_nodename", "dash_type", "dash_svcname", "dash_md5"]
        #self.span = ["dash_nodename", "dash_type", "dash_svcname", "dash_md5"]
        self.span = ["id"]
        self.order = ["~dash_severity", "dash_type", "dash_nodename", "dash_svcname"]
        self.colprops['dash_svcname'].t = self
        self.colprops['dash_nodename'].t = self
        self.colprops['dash_links'].t = self
        self.colprops['dash_entry'].t = self
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_table = 'dashboard'
        self.checkbox_id_col = 'id'
        self.special_filtered_cols = ['dash_entry']
        self.wsable = True
        self.dataable = True
        self.child_tables = ['dash_agg']

@auth.requires_login()
def ajax_dashboard_col_values():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    col = request.args[0]
    if t.colprops[col].filter_redirect is None:
        o = db.dashboard[col]
        s = [o]
    else:
        o = db.dashboard[t.colprops[col].filter_redirect]
        s = [db.dashboard.dash_fmt, db.dashboard.dash_dict]
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)
    t.object_list = db(q).select(*s, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dashboard():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    o = ~db.dashboard.dash_severity|db.dashboard.dash_type|db.dashboard.dash_nodename|db.dashboard.dash_svcname
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f), f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)

    t.csv_q = q
    t.csv_orderby = o

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.dashboard.id.count()).first()(db.dashboard.id.count())
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, cacheable=True, limitby=limitby)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def index():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    mt = table_dash_agg('dash_agg', 'ajax_dash_agg')
    t = DIV(
             DIV(
               T("Alerts Statistics"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#dash_agg").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#dash_agg").show(); %s ;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#dash_agg").hide();
               }"""%mt.ajax_submit(additional_inputs=t.ajax_inputs()),
             ),
             DIV(
                mt.html(),
                _style="display:none",
               _id="dash_agg",
             ),
             DIV(
               T("Alerts History"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#dh").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#dh").show(); sync_ajax("%(url)s", [], "dh", function(){});
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#dh").hide();
               }"""%dict(url=URL(r=request,f='ajax_dash_history', vars={"divid": "dh"})),
             ),
             DIV(_id="dh", _style="display:none"),
             DIV(
               t.html(),
               _id='dashboard',
             ),
             SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "dash_change") {
          osvc.tables["%(divid)s"].refresh()
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
              """ % dict(
                     divid=t.innerhtml,
                    )
             ),
        )

    return dict(table=t)

#
# Dashboard change detection
#
def dash_changed():
    sql = """select (now()-update_time)*6/10
             from information_schema.tables
             where
               table_schema = 'opensvc' and
               table_name = 'dashboard'
          """
    rows = db.executesql(sql)
    return rows[0][0]


@auth.requires_login()
def ajax_alert_events():
    session.forget(response)
    limit = datetime.datetime.now() - datetime.timedelta(days=30)
    q = db.dashboard_events.dash_md5 == request.vars.dash_md5
    q &= db.dashboard_events.dash_nodename == request.vars.dash_nodename
    q &= db.dashboard_events.dash_svcname == request.vars.dash_svcname
    q &= db.dashboard_events.dash_begin > limit
    q &= _where(None, 'dashboard_events', domain_perms(), 'dash_svcname')|_where(None, 'dashboard_events', domain_perms(), 'dash_nodename')
    rows = db(q).select(db.dashboard_events.dash_begin,
                        db.dashboard_events.dash_end)

    if len(rows) == 0:
        data_on = [[str(request.vars.dash_created), 1],
                   [str(now), 1],
                   [str(now), 'null']]
    else:
        data_on = []
        last = len(rows)

    for i, row in enumerate(rows):
        data_on += [[str(row.dash_begin), 1]]
        if row.dash_end is None:
            data_on += [[str(now), 1]]
            data_on += [[str(now), 'null']]
        else:
            data_on += [[str(row.dash_end), 1]]
            data_on += [[str(row.dash_end), 'null']]

    data = str([str(data_on).replace("'null'","null"), [[str(now), 1]]]).replace('"','')
    s = """data_%(rowid)s=%(data)s;$('#%(id)s').empty();avail_plot('%(id)s', data_%(rowid)s);"""%dict(
           data=data,
           id='plot_%s'%request.vars.rowid,
           rowid=request.vars.rowid,
         )
    wikipage_name = "alert"
    if request.vars.dash_nodename is not None:
        wikipage_name += "_"+request.vars.dash_nodename
    if request.vars.dash_svcname is not None:
        wikipage_name += "_"+request.vars.dash_svcname
    if request.vars.dash_md5 is not None:
        wikipage_name += "_"+request.vars.dash_md5

    s += "ajax('%(url)s', [], '%(id)s');"%dict(
               id='wiki_%s'%request.vars.rowid,
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['wiki_%s'%request.vars.rowid, wikipage_name]),
         )

    #t = """wiki("%(id)s", {"nodes": "%(node)s"});"""%dict(
    #           id='wiki_%s'%request.vars.rowid,
    #           rid=str(request.vars.rowid),
    #           node=wikipage_name)

    s+=t;
    return TABLE(DIV(
             H2(T("Alert timeline")),
             DIV(
               data,
               _id='plot_%s'%request.vars.rowid,
               _style='width:300px;height:50px',
             ),
             BR(),
             DIV(
               _id='wiki_%s'%request.vars.rowid,
             ),
             SCRIPT(s, _name='%s_to_eval'%request.vars.rowid),
             _style="padding:1em",
           ))

def test_dashboard_events():
    dashboard_events()

#
# alert tab
#
class table_dashboard_node(table_dashboard):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_dashboard.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = True
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.child_tables = []

def ajax_dashboard_node():
    tid = request.vars.table_id
    t = table_dashboard_node(tid, 'ajax_dashboard_node')
    q = _where(None, 'dashboard', domain_perms(), 'dash_nodename')
    for f in ['dash_nodename']:
        q = _where(q, 'dashboard', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

def ajax_dashboard_svc():
    tid = request.vars.table_id
    t = table_dashboard_node(tid, 'ajax_dashboard_svc')
    q = _where(None, 'dashboard', domain_perms(), 'dash_svcname')
    for f in ['dash_svcname']:
        q = _where(q, 'dashboard', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def dashboard_node():
    node = request.args[0]
    tid = 'dashboard_'+node.replace('-', '_').replace('.', '_')
    t = table_dashboard_node(tid, 'ajax_dashboard_node')
    t.colprops['dash_nodename'].force_filter = node

    return DIV(
             t.html(),
             _id=tid,
           )

@auth.requires_login()
def dashboard_svc():
    svcname = request.args[0]
    tid = 'dashboard_'+svcname.replace('-','_').replace('.','_')
    t = table_dashboard_node(tid, 'ajax_dashboard_svc')
    t.colprops['dash_svcname'].force_filter = svcname

    return DIV(
             t.html(),
             _id=tid,
           )


