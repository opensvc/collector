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
                table = 'v_svcactions',
                field='svcname',
            ),
            'hostname': HtmlTableColumn(
                table = 'v_svcactions',
                field='hostname',
            ),
            'pid': HtmlTableColumn(
                table = 'v_svcactions',
                field='pid',
            ),
            'action': HtmlTableColumn(
                table = 'v_svcactions',
                field='action',
            ),
            'status': HtmlTableColumn(
                table = 'v_svcactions',
                field='status',
            ),
            'begin': HtmlTableColumn(
                table = 'v_svcactions',
                field='begin',
            ),
            'end': HtmlTableColumn(
                table = 'v_svcactions',
                field='end',
            ),
            'status_log': HtmlTableColumn(
                table = 'v_svcactions',
                field='status_log',
            ),
            'cron': HtmlTableColumn(
                table = 'v_svcactions',
                field='cron',
            ),
            'time': HtmlTableColumn(
                table = 'v_svcactions',
                field='time',
            ),
            'id': HtmlTableColumn(
                table = 'v_svcactions',
                field='id',
            ),
            'ack': HtmlTableColumn(
                table = 'v_svcactions',
                field='ack',
            ),
            'acked_comment': HtmlTableColumn(
                table = 'v_svcactions',
                field='acked_comment',
            ),
            'acked_by': HtmlTableColumn(
                table = 'v_svcactions',
                field='acked_by',
            ),
            'acked_date': HtmlTableColumn(
                table = 'v_svcactions',
                field='acked_date',
            ),
            'app': HtmlTableColumn(
                table = 'v_svcactions',
                field='app',
            ),
        }
        cp = nodes_colprops
        for k in cp.keys():
            cp[k].table = "v_svcactions"
        del(cp['status'])
        self.colprops.update(cp)
        self.colprops.update(v_services_colprops)
        ncols = nodes_cols
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
        self.ajax_col_values = 'ajax_actions_col_values'
        self.span = ['pid']
        self.keys = ["id"]

@auth.requires_login()
def ajax_actions_col_values():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
    col = request.args[0]
    o = db.v_svcactions[col]
    q = q_filter(svc_field=db.v_svcactions.svcname)
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
    q = q_filter(svc_field=db.v_svcactions.svcname)
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
          """table_actions("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def svcactions_load():
    return svcactions()["table"]

