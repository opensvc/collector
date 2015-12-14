def pid_to_filter(pid):
    if pid is None:
        return ''
    return pid.replace(',', '|')

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
        self.force_cols = ['os_name', 'ack', 'acked_by', 'acked_date', 'acked_comment', 'end']
        self.span = ['pid']
        #self.span = ['pid', 'hostname', 'svcname', 'action'] + ncols
        self.wsable = True
        self.dataable = True
        self.dbfilterable = True
        self.checkboxes = True
        self.checkbox_id_table = 'v_svcactions'
        self.keys = ["id"]
        self.events = ["begin_action", "end_action", "svcactions_change"]

@auth.requires_login()
def ajax_actions_col_values():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
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
def ajax_actions():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')

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
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def svcactions():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_actions("layout") })""",
        )
    return dict(table=t)

def svcactions_load():
    return svcactions()["table"]

