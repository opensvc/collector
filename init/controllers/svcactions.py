def pid_to_filter(pid):
    if pid is None:
        return ''
    return pid.replace(',', '|')

def update_dash_action_errors(svc_name, nodename):
    svc_name = svc_name.strip("'")
    nodename = nodename.strip("'")
    sql = """select e.err, s.svc_type from b_action_errors e
             join services s on e.svcname=s.svc_name
             where
               svcname="%(svcname)s" and
               nodename="%(nodename)s"
          """%dict(svcname=svc_name, nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1:
        if rows[0][1] == 'PRD':
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_env='%(env)s',
                   dash_created="%(now)s",
                   dash_updated="%(now)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_updated="%(now)s"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                       env=rows[0][1],
                       now=str(datetime.datetime.now()),
                       err=rows[0][0])
        db.executesql(sql)
        db.commit()
        sqlws = """select
                     dash_md5
                   from
                     dashboard
                   where
                     dash_type="action errors" and
                     dash_svcname="%(svcname)s" and
                     dash_nodename="%(nodename)s" and
                     dash_fmt="%%(err)s action errors"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                  )
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            _websocket_send(event_msg({
              'event': 'dash_change',
              'data': {
                'dash_md5': rows[0][0],
              }
            }))

    else:
        sqlws = """select dash_md5 from dashboard
                 where
                   dash_type="action errors" and
                   dash_svcname="%(svcname)s" and
                   dash_nodename="%(nodename)s"
              """%dict(svcname=svc_name,
                       nodename=nodename)
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            _websocket_send(event_msg({
              'event': 'dash_delete',
              'data': {
                'dash_md5': rows[0][0],
              }
            }))
        sql = """delete from dashboard
                 where
                   dash_type="action errors" and
                   dash_svcname="%(svcname)s" and
                   dash_nodename="%(nodename)s"
              """%dict(svcname=svc_name,
                       nodename=nodename)
        db.executesql(sql)
        db.commit()

def update_action_errors():
    sql = """truncate b_action_errors
          """
    db.executesql(sql)
    sql = """insert into b_action_errors
               select null, svcname, hostname, count(id)
               from SVCactions
               where
                 status = 'err' and
                 (ack <> 1 or isnull(ack)) and
                 end is not null
               group by svcname, hostname
          """
    db.executesql(sql)
    db.commit()

@auth.requires_login()
def ajax_action_status():
    if len(request.args) == 0:
        return SPAN()
    id = int(request.args[0])

    rows = db(db.SVCactions.id==id).select()

    if len(rows) != 1:
        return SPAN('action not found')

    status = rows[0].status
    if status is not None:
        if rows[0].end is None:
            end = rows[0].begin
        else:
            end = rows[0].end
            pass

        pid = A(
             rows[0].pid,
             _href=URL(
                     r=request,
                     f='svcactions',
                     vars={
                       'actions_f_pid':pid_to_filter(rows[0].pid),
                       'actions_f_hostname':rows[0].hostname,
                       'actions_f_svcname':rows[0].svcname,
                       'actions_f_begin':'>'+str(rows[0].begin-datetime.timedelta(days=1)),
                       'actions_f_end':'<'+str(end+datetime.timedelta(days=1)),
                       'actions_f_perpage':0,
                       'clear_filters': 'true',
                     }
          ),
        )
        return SPAN(
                 IMG(
                   _src=URL(r=request,c='static',f='action16.png'),
                   _border=0,
                   _onload="""
                     document.getElementById('spin_span_pid_%(id)s').innerHTML='%(pid)s';
                     document.getElementById('spin_span_end_%(id)s').innerHTML='%(end)s';
                   """%dict(
                         id=id,
                         pid=pid,
                         end=rows[0].end,
                       ),
                   _style='display:none',
                 ),
                 status,
                 _class="status_"+status,
               )
    else:
        return IMG(
                _src=URL(r=request,c='static',f='spinner.gif'),
                _border=0,
                _title=T("unfinished"),
                _onload="""refresh_action('%(url)s', '%(id)s')"""%dict(
                      url=URL(r=request,f='ajax_action_status', args=[id]),
                      id=id,
                    )
              )

def svcactions_rss():
    #return BEAUTIFY(request)
    import gluon.contrib.rss2 as rss2
    import datetime
    d = svcactions()
    url = request.url[:-4]
    items = []
    desc = 'filtering options for this feed: '
    for key in request.vars.keys():
        if request.vars[key] != '': desc += key+'['+request.vars[key]+'] '
    for action in d['actions']:
        items += [rss2.RSSItem(title="""[osvc] %s %s returned %s"""%(action.action,action.svcname,action.status),
                      link = """http://%s%s?id==%s"""%(request.env.http_host,url,action.id),
                      description="""<b>id:</b> %s<br><b>begin:</b> %s<br>%s"""%(action.begin,action.id,action.status_log))]
    rss = rss2.RSS2(title="OpenSVC actions",
                link = """http://%s%s?%s"""%(request.env.http_host,url,request.env.query_string),
                description = desc,
                lastBuildDate = datetime.datetime.now(),
                items = items
    )
    response.headers['Content-Type']='application/rss+xml'
    return rss2.dumps(rss)

class table_actions(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svcname',
                     'hostname',
                     'pid',
                     'action',
                     'status',
                     'begin',
                     'end',
                     'time',
                     'id',
                     'status_log',
                     'cron',
                     'ack',
                     'acked_by',
                     'acked_date',
                     'acked_comment',
                    ]
        self.colprops = {
            'svcname': HtmlTableColumn(
                title = 'Service',
                table = 'v_svcactions',
                field='svcname',
                display = True,
                img = 'svc',
                _class = 'svcname',
            ),
            'hostname': HtmlTableColumn(
                title = 'Node name',
                table = 'v_svcactions',
                field='hostname',
                display = True,
                img = 'node16',
                _class = 'nodename',
            ),
            'pid': HtmlTableColumn(
                title = 'Pid',
                table = 'v_svcactions',
                field='pid',
                display = True,
                img = 'action16',
                _class = 'action_pid',
            ),
            'action': HtmlTableColumn(
                title = 'Action',
                table = 'v_svcactions',
                field='action',
                display = True,
                img = 'action16',
                _class = 'action',
            ),
            'status': HtmlTableColumn(
                title = 'Status',
                table = 'v_svcactions',
                field='status',
                display = True,
                img = 'action16',
                _class = 'action_status',
            ),
            'begin': HtmlTableColumn(
                title = 'Begin',
                table = 'v_svcactions',
                field='begin',
                display = True,
                img = 'time16',
                default_filter = '>-1d',
                _class = 'datetime_no_age',
            ),
            'end': HtmlTableColumn(
                title = 'End',
                table = 'v_svcactions',
                field='end',
                display = False,
                img = 'time16',
                _class = 'action_end',
            ),
            'status_log': HtmlTableColumn(
                title = 'Log',
                table = 'v_svcactions',
                field='status_log',
                display = True,
                img = 'action16',
                _class = 'action_log',
            ),
            'cron': HtmlTableColumn(
                title = 'Scheduled',
                table = 'v_svcactions',
                field='cron',
                display = True,
                img = 'action16',
                _class = 'action_cron',
            ),
            'time': HtmlTableColumn(
                title = 'Duration',
                table = 'v_svcactions',
                field='time',
                display = False,
                img = 'time16',
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                table = 'v_svcactions',
                field='id',
                display = False,
                img = 'action16',
            ),
            'ack': HtmlTableColumn(
                title = 'Ack',
                table = 'v_svcactions',
                field='ack',
                display = False,
                img = 'action16',
            ),
            'acked_comment': HtmlTableColumn(
                title = 'Ack comment',
                table = 'v_svcactions',
                field='acked_comment',
                display = False,
                img = 'action16',
            ),
            'acked_by': HtmlTableColumn(
                title = 'Acked by',
                table = 'v_svcactions',
                field='acked_by',
                display = False,
                img = 'guy16',
            ),
            'acked_date': HtmlTableColumn(
                title = 'Ack date',
                table = 'v_svcactions',
                field='acked_date',
                display = False,
                img = 'time16',
            ),
            'app': HtmlTableColumn(
                title = 'App',
                table = 'v_svcactions',
                field='app',
                display = False,
                img = 'svc',
            ),
        }
        cp = v_nodes_colprops
        for k in cp.keys():
            cp[k].table = "v_svcactions"
        del(cp['status'])
        self.colprops.update(cp)
        self.colprops.update(v_services_colprops)
        ncols = v_nodes_cols
        ncols.remove('updated')
        ncols.remove('power_supply_nb')
        ncols.remove('power_cabinet1')
        ncols.remove('power_cabinet2')
        ncols.remove('power_protect')
        ncols.remove('power_protect_breaker')
        ncols.remove('power_breaker1')
        ncols.remove('power_breaker2')
        ncols.remove('status')
        self.cols += ncols
        for c in self.cols:
            self.colprops[c].t = self
        self.ajax_col_values = 'ajax_actions_col_values'
        self.extraline = True
        self.force_cols = ['os_name', 'acked_by', 'acked_date', 'acked_comment']
        self.span = ['pid']
        #self.span = ['pid', 'hostname', 'svcname', 'action'] + ncols
        self.wsable = True
        self.dataable = True
        self.dbfilterable = True
        self.checkboxes = True
        self.checkbox_id_table = 'v_svcactions'
        self.additional_tools.append('ack')
        self.keys = ["id"]

    def checkbox_disabled(self, o):
        status = self.colprops['status'].get(o)
        ack = self.colprops['ack'].get(o)
        if status == 'err' and ack != 1:
            return False
        return True

    def ack(self):
        d = DIV(
              A(
                T("Acknowledge error"),
                _class='check16',
                _onclick="""
                  click_toggle_vis(event, '%(div)s', 'block');
                """%dict(div='ackcomment_d'),
              ),
              DIV(
                TABLE(
                  TR(
                    TD(
                      T('Comment'),
                    ),
                    TD(
                      TEXTAREA(
                        _id='ackcomment',
                        _style="width:20em;height:10em;margin-bottom:0.3em",
                      ),
                      BR(),
                      INPUT(
                        _type="submit",
                        _onclick=self.ajax_submit(additional_inputs=['ackcomment'], args="ack"),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='ackcomment_d',
                _id='ackcomment_d',
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def ajax_actions_col_values():
    t = table_actions('actions', 'ajax_actions')
    col = request.args[0]
    o = db.v_svcactions[col]
    q = _where(None, 'v_svcactions', domain_perms(), 'hostname')
    q = apply_filters(q, db.v_svcactions.hostname, db.v_svcactions.svcname)
    for f in t.cols:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)
    t.object_list = db(q).select(db.v_svcactions[col],
                                 orderby=o,
                                 limitby=(0,10000))
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ack(ids=[]):
    if len(ids) == 0:
        raise ToolError("no action selected")
    ackcomment = request.vars.ackcomment
    q = db.SVCactions.id.belongs(ids)
    q &= db.SVCactions.status != "ok"
    rows = db(q).select(db.SVCactions.hostname,
                        db.SVCactions.svcname,
                        db.SVCactions.id,
                        db.SVCactions.action,
                        cacheable=True)
    if len(rows) == 0:
        return

    user = user_name()

    db(q).update(ack=1,
                 acked_comment=ackcomment,
                 acked_by=user,
                 acked_date=datetime.datetime.now())
    db.commit()

    if 'ackcomment' in request.vars:
        del request.vars.ackcomment

    update_action_errors()

    l = []
    for r in rows:
        if (r.svcname, r.hostname) not in l:
            l.append((r.svcname, r.hostname))
        _log('action.ack',
             'acknowledged action error with id %(g)s: %(action)s on %(svc)s@%(node)s',
             dict(g=r.id, action=r.action, svc=r.svcname, node=r.hostname),
             user=user,
             svcname=r.svcname,
             nodename=r.hostname)

    for svcname, hostname in l:
        update_dash_action_errors(svcname, hostname)

@auth.requires_login()
def ajax_actions():
    t = table_actions('actions', 'ajax_actions')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'ack':
                ack(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.v_svcactions.id
    q = _where(None, 'v_svcactions', domain_perms(), 'hostname')
    q = apply_filters(q, db.v_svcactions.hostname, db.v_svcactions.svcname)
    for f in t.cols:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def svcactions():
    t = table_actions('actions', 'ajax_actions')
    t = DIV(
          DIV(
            _id='ackpanel',
            _class='ackpanel',
          ),
          DIV(
            t.html(),
            _id='actions',
          ),
          SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "begin_action") {
          osvc.tables["%(divid)s"].refresh()
          //_data = []
          //_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
          //osvc.tables["%(divid)s"].insert(_data)
        } else if (data["event"] == "end_action") {
          osvc.tables["%(divid)s"].refresh()
          //_data = []
          //_data.push({"key": "id", "val": data["data"]["id"], "op": ">="})
          //_data.push({"key": "pid", "val": data["data"]["pid"], "op": "="})
          //osvc.tables["%(divid)s"].insert(_data)
        } else if (data["event"] == "svcactions_change") {
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
# actions tab
#
class table_actions_node(table_actions):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_actions.__init__(self, id, func, innerhtml)
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

def ajax_actions_node():
    tid = request.vars.table_id
    t = table_actions_node(tid, 'ajax_actions_node')
    o = ~db.v_svcactions.id
    q = _where(None, 'v_svcactions', domain_perms(), 'hostname')
    for f in ['hostname']:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True, orderby=o, limitby=(0,20))
        return t.table_lines_data(-1, html=False)

def ajax_actions_svc():
    tid = request.vars.table_id
    t = table_actions_node(tid, 'ajax_actions_svc')
    o = ~db.v_svcactions.id
    q = _where(None, 'v_svcactions', domain_perms(), 'svcname')
    for f in ['svcname']:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True, orderby=o, limitby=(0,20))
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def actions_node():
    node = request.args[0]
    tid = 'actions_'+node.replace('-', '_').replace('.', '_')
    t = table_actions_node(tid, 'ajax_actions_node')
    t.colprops['hostname'].force_filter = node

    return DIV(
             t.html(),
             _id=tid,
           )

@auth.requires_login()
def actions_svc():
    svcname = request.args[0]
    tid = 'actions_'+svcname.replace('-','_').replace('.','_')
    t = table_actions_node(tid, 'ajax_actions_svc')
    t.colprops['svcname'].force_filter = svcname

    return DIV(
             t.html(),
             _id=tid,
           )

