def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
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
                    json.dumps(h['nb']),
                    _id='nb_chart',
                  ),
                  DIV(
                    _id='chart_info',
                  ),
                  _style="float:left;width:350px",
                ),
              )

class col_dash_icons(HtmlTableColumn):
    def html(self, o):
        d = SPAN(
              _onclick='$("#dashboard_f_dash_type").val("%s");'%o['dash_type']+self.t.ajax_submit(),
              _class="search16 clickable",
            )
        return d

class col_dash_history(HtmlTableColumn):
    def html(self, o):
        id = self.get(o)
        d = DIV(
              T("loading"),
              _class="dynamicsparkline",
              _id=id
            )
        return d

class col_dash_alerts(HtmlTableColumn):
    def html(self, o):
        return html_bar(o['dash_alerts'], self.t.total_alerts)

class col_dash_cumulated_severity(HtmlTableColumn):
    def html(self, o):
        return html_bar(o['dash_severity'], self.t.total_severity)

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
        self.exportable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False


@auth.requires_login()
def ajax_dash_agg():
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

    mt.dbfilterable = False
    mt.pageable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    h = {'nb': [], 'sev': []}

    for sev in range(0, 5):
        sql2 = """ select
                      dashboard.id,
                      dashboard.dash_type,
                      count(dashboard.dash_type)
                    from dashboard ignore index (idx1)
                      %(sql)s
                      and dash_severity=%(sev)d
                    group by dash_type
                  """%dict(
                    sql=sql1,
                    sev=sev,
                    where=where,
               )

        rows = db.executesql(sql2)

        l = map(lambda x: {'dash_type': x[1],
                           'dash_alerts':x[2]},
                 rows)

        data = []
        for line in l:
            s = T.translate(line['dash_type'], dict())
            data.append([s, int(line['dash_alerts']), line['dash_type']])
        data.sort(lambda x, y: cmp(y[1], x[1]))
        if len(data) == 0:
            data = ['', 0, '']
        h['nb'].append(data)

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

    return DIV(
             mt.html(),
             SCRIPT(
               """
function dashdonut(o) {
  try{
  var data = $.parseJSON(o.html())
  o.html("")
  $.jqplot(o.attr('id'), data,
    {
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          dataLabels: 'value',
          showDataLabels: true
        }
      },
      series: [
        {seriesColors: ["#009900", "#44aa44", "#66bb66"]},
        {seriesColors: ["#ffa500", "#ffb522", "#ffc544", "#ffd566"]},
        {seriesColors: ["#990000", "#992222", "#994444"]},
        {seriesColors: ["#660000", "#772222", "#884444"]},
        {seriesColors: ["#2d2d2d", "#202020", "#101010"]}
      ]
    }
  );
  $('#'+o.attr('id')).bind('jqplotDataHighlight', 
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('sev '+seriesIndex+', '+data[1]+' '+data[0]);
        }
  );
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight', 
        function (ev) {
            $('#chart_info').html('%(msg)s');
        }
  ); 
  $('#'+o.attr('id')).bind('jqplotDataClick',
        function(ev, seriesIndex, pointIndex, data) {
            dash_type = data[2]
            $("#dashboard_f_dash_type").val(dash_type)
            $("#dashboard_f_dash_severity").val(seriesIndex)
            %(submit)s
        }
  );
  } catch(e) {}
}
function dashpie_nb(o) {
  var data = $.parseJSON(o.html())
  o.html("")
  o.height("250px")
  options = {
      seriesDefaults: {
        renderer: $.jqplot.PieRenderer,
        rendererOptions: {
          sliceMargin: 4,
          dataLabelPositionFactor: 0.7,
          startAngle: -90,
          dataLabels: 'value',
          showDataLabels: true
        }
      },
      legend: { show:true, location: 'e' }
    }
  $.jqplot(o.attr('id'), [data], options)
  o.bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
    dash_type = data[seriesIndex]
    $("#dashboard_f_dash_type").val(dash_type)
    %(submit)s
  })
}
function dashpie_sev(o) {
  var data = $.parseJSON(o.html())
  o.html("")
  o.height("300px")
  colors = {
    "4": "#2d2d2d",
    "3": "#660000",
    "2": "#990000",
    "1": "#ffa500",
    "0": "#009900"
  }
  c = []
  for (i=0;i<data.length;i++) {
      c.push(colors[data[i][0][data[i][0].length-1]])
  }
  options = {
      seriesDefaults: {
        renderer: $.jqplot.PieRenderer,
        seriesColors: c,
        rendererOptions: {
          sliceMargin: 4,
          dataLabelPositionFactor: 0.7,
          startAngle: -90,
          dataLabels: 'value',
          showDataLabels: true
        }
      },
      legend: { show:false, location: 'e' }
    }
  $.jqplot(o.attr('id'), [data], options)
  o.bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
    dash_severity = data[seriesIndex][data[seriesIndex].length-1]
    $("#dashboard_f_dash_severity").val(dash_severity)
    %(submit)s
  })
}
$("#nb_chart").each(function(){
  dashdonut($(this))
})
$("#sev_chart").each(function(){
  dashpie_sev($(this))
})
"""%dict(submit=t.ajax_submit(),
         msg=T("Hover over a slice to show data"),
        ),
               _name="dash_agg_to_eval",
             ),
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

class col_dash_links(HtmlTableColumn):
    def link_action_errors(self, o):
       dash_svcname = self.t.colprops['dash_svcname'].get(o)
       i = A(
             _href=URL(r=request,c='svcactions',f='svcactions',
                    vars={'actions_f_svcname': dash_svcname,
                          'actions_f_status': 'err',
                          'actions_f_ack': '!1|empty',
                          'clear_filters': 'true'}),
             _title=T("Service action errors"),
             _class='alert16 clickable',
           )
       return i

    def link_actions(self, o):
       dash_svcname = self.t.colprops['dash_svcname'].get(o)
       i = A(
             _href=URL(r=request,c='svcactions',f='svcactions',
                    vars={'actions_f_svcname': dash_svcname,
                          'actions_f_begin': '>%s'%str(now-datetime.timedelta(days=7)),
                          'clear_filters': 'true'}),
             _title=T("Service actions"),
             _class='action16 clickable',
           )
       return i

    def link_svcmon(self, o):
       dash_svcname = self.t.colprops['dash_svcname'].get(o)
       i = A(
             _href=URL(r=request,c='default',f='svcmon',
                    vars={'svcmon_f_svc_name': dash_svcname,
                          'clear_filters': 'true'}),
             _title=T("Service status"),
             _class='svc clickable',
           )
       return i

    def link_checks(self, o):
       dash_nodename = self.t.colprops['dash_nodename'].get(o)
       i = A(
             _href=URL(r=request,c='checks',f='checks',
                    vars={'checks_f_chk_nodename': dash_nodename,
                          'clear_filters': 'true'}),
             _title=T("Checks"),
             _class='check16 clickable',
           )
       return i

    def link_nodes(self, o):
       dash_nodename = self.t.colprops['dash_nodename'].get(o)
       i = A(
             _href=URL(r=request,c='nodes',f='nodes',
                    vars={'nodes_f_nodename': dash_nodename,
                          'clear_filters': 'true'}),
             _title=T("Node"),
             _class='node16 clickable',
           )
       return i

    def link_obsolescence(self, o, t):
       i = A(
             _href=URL(r=request,c='obsolescence',f='obsolescence_config',
                    vars={'obs_f_obs_type': t,
                          'clear_filters': 'true'}),
             _title=T("Obsolescence configuration"),
             _class='%s16 clickable'%t,
           )
       return i

    def link_compliance_tab(self, o):
       id = self.t.extra_line_key(o)
       i = A(
             _title=T("Compliance tab"),
             _class='comp16 clickable',
             _onclick="""toggle_extra('%(url)s', '%(id)s')"""%dict(
                  url=URL(r=request, c='default',f='ajax_service',
                          vars={'node': self.t.colprops['dash_svcname'].get(o),
                                'rowid': id,
                                'tab': 'tab11'}),
                  id=id,
                      ),
           )
       return i

    def link_pkgdiff_tab(self, o):
       id = self.t.extra_line_key(o)
       i = A(
             _title=T("Pkgdiff tab"),
             _class='pkg16 clickable',
             _onclick="""toggle_extra('%(url)s', '%(id)s')"""%dict(
                  url=URL(r=request, c='default',f='ajax_service',
                          vars={'node': self.t.colprops['dash_svcname'].get(o),
                                'rowid': id,
                                'tab': 'tab10'}),
                  id=id,
                      ),
           )
       return i

    def html(self, o):
       l = []
       dash_type = self.t.colprops['dash_type'].get(o)
       if dash_type == "action errors":
           l.append(self.link_action_errors(o))
           l.append(self.link_actions(o))
       elif dash_type == "check out of bounds" or \
            dash_type == "check value not updated":
           l.append(self.link_checks(o))
       elif dash_type == "service status not updated" or \
            dash_type == "service configuration not updated" or \
            dash_type == "service available but degraded" or \
            dash_type == "service frozen" or \
            dash_type == "service unavailable":
           l.append(self.link_svcmon(o))
       elif dash_type == "node warranty expired" or \
            dash_type == "node information not updated" or \
            dash_type == "node without warranty end date" or \
            dash_type == "node without asset information" or \
            dash_type == "node close to warranty end":
           l.append(self.link_nodes(o))
       elif "os obsolescence" in dash_type:
           l.append(self.link_obsolescence(o, 'os'))
       elif "obsolescence" in dash_type:
           l.append(self.link_obsolescence(o, 'hw'))
       elif dash_type.startswith('comp'):
           l.append(self.link_compliance_tab(o))
       elif dash_type.startswith('package'):
           l.append(self.link_pkgdiff_tab(o))

       return DIV(l)

class col_dash_severity(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       c = "boxed_small "
       if d == 0:
           c += "bggreen"
       elif d == 1:
           c += "bgorange"
       elif d == 2:
           c += "bgred"
       elif d == 3:
           c += "bgdarkred"
       else:
           c += "bgblack"
       return DIV(d, _class=c)

class table_dashboard(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['dash_severity',
                     'dash_links',
                     'dash_type',
                     'dash_svcname',
                     'dash_nodename',
                     'dash_env',
                     'dash_entry',
                     'dash_created']
        self.colprops = {
            'dash_links': col_dash_links(
                     title='Links',
                     field='dummy',
                     img='link16',
                     display=True,
                    ),
            'dash_created': HtmlTableColumn(
                     title='Begin date',
                     table='dashboard',
                     field='dash_created',
                     img='time16',
                     display=True,
                    ),
            'dash_severity': col_dash_severity(
                     title='Severity',
                     table='dashboard',
                     field='dash_severity',
                     img='action16',
                     display=True,
                    ),
            'dash_svcname': col_svc(
                     title='Service',
                     table='dashboard',
                     field='dash_svcname',
                     img='svc',
                     display=True,
                    ),
            'dash_nodename': col_node(
                     title='Node',
                     table='dashboard',
                     field='dash_nodename',
                     img='node16',
                     display=True,
                    ),
            'dash_entry': col_dash_entry(
                     title='Alert',
                     table='dashboard',
                     field='dummy',
                     filter_redirect='dash_dict',
                     img='log16',
                     display=True,
                    ),
            'dash_env': HtmlTableColumn(
                     title='Env',
                     table='dashboard',
                     field='dash_env',
                     img='svc',
                     display=True,
                    ),
            'dash_fmt': HtmlTableColumn(
                     title='Format',
                     table='dashboard',
                     field='dash_fmt',
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
        }
        self.colprops['dash_svcname'].t = self
        self.colprops['dash_nodename'].t = self
        self.colprops['dash_links'].t = self
        self.colprops['dash_entry'].t = self
        self.dbfilterable = True
        self.extraline = True
        self.checkbox_id_table = 'dashboard'
        self.checkbox_id_col = 'id'
        self.special_filtered_cols = ['dash_entry']
        #self.autorefresh = 60000

@auth.requires_login()
def ajax_dashboard_col_values():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    col = request.args[0]
    o = db.dashboard[col]
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_dashboard():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    o = ~db.dashboard.dash_severity|db.dashboard.dash_type
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f), f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)

    sql = "select count(id) from dashboard ignore index (idx1) where "+str(q)
    n = db.executesql(sql)[0][0]
    #n = db(q).count()
    t.setup_pager(n)
    sql = """select *
             from dashboard ignore index (idx1)
             where %s
             order by dash_severity desc, dash_type
             limit %d offset %d"""%(str(q), t.pager_end-t.pager_start, t.pager_start)
    # t.object_list = db(q).select(db.dashboard.ALL, limitby=(t.pager_start,t.pager_end), orderby=o)
    t.object_list = db.executesql(sql, as_dict=True)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    mt = table_dash_agg('dash_agg', 'ajax_dash_agg')
    return DIV(
             SCRIPT(
               mt.ajax_submit(additional_inputs=t.ajax_inputs()),
               _name=t.id+"_to_eval"
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
               _id="dash_agg",
             ),
             t.html(),
           )

@auth.requires_login()
def index():
    t = DIV(
          ajax_dashboard(),
          _id='dashboard',
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

