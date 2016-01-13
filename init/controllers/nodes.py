class table_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']+nodes_cols
        self.colprops = nodes_colprops
        self.span = ["nodename"]
        self.keys = ["nodename"]
        self.colprops.update({
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     field='nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'nodes'

        self.colprops.update({
            'app_domain': HtmlTableColumn(
                     title='App domain',
                     field='app_domain',
                     img='svc',
                     table='apps',
                     display=False,
                    ),
            'app_team_ops': HtmlTableColumn(
                     title='Ops team',
                     field='app_team_ops',
                     img='guys16',
                     table='apps',
                     display=False,
                    ),
        })
        self.cols.insert(self.cols.index('team_integ')+1, 'app_team_ops')
        self.cols.insert(self.cols.index('project')+1, 'app_domain')

        for c in ['loc_building', 'loc_floor', 'loc_rack',
                  'cpu_dies', 'cpu_cores', 'cpu_model', 'mem_bytes',
                  'serial', 'team_responsible', 'host_mode', 'status']:
            self.colprops[c].display = True
        self.colprops['nodename'].t = self
        self.force_cols = ['os_name']
        self.wsable = True
        self.dataable = True
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'nodename'
        self.checkbox_id_table = 'nodes'
        self.dbfilterable = True
        self.events = ["nodes_change"]
        self.child_tables = ["uids", "gids"]
        self.ajax_col_values = 'ajax_nodes_col_values'

@auth.requires_login()
def ajax_grpprf():
    nodes = request.vars.get("node", "")
    divid = 'grpperf'
    now = datetime.datetime.now()
    s = now - datetime.timedelta(days=0,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = s + datetime.timedelta(days=1)

    d = DIV(
            DIV(
              INPUT(
                _value=s.strftime("%Y-%m-%d %H:%M"),
                _id='begin',
                _class='datetime',
              ),
              INPUT(
                _value=e.strftime("%Y-%m-%d %H:%M"),
                _id='end',
                _class='datetime',
              ),
              INPUT(
                _value='gen',
                _type='button',
                _onClick="""sync_ajax("%(url)s?node=%(nodes)s",['begin', 'end'],"%(div)s",function(){})"""%dict(nodes=nodes,url=URL(r=request,c='stats',f='ajax_perfcmp_plot'), div="prf_cont"),
              ),
            ),
            DIV(
              T("Please define a timeframe and click the 'gen' button."),
              _style='padding:0.5em',
              _id="prf_cont"
            ),
            SCRIPT(
              """$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})""",
            ),
            _name=divid,
            _id=divid,
        )
    return d


@auth.requires_login()
def ajax_nodes_col_values():
    table_id = request.vars.table_id
    t = table_nodes(table_id, 'ajax_nodes')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.nodes.id > 0
    j = db.apps.app == db.nodes.project
    l = db.apps.on(j)
    q = _where(q, 'nodes', domain_perms(), 'nodename')
    q = apply_filters(q, db.nodes.nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=l)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_nodes():
    table_id = request.vars.table_id
    t = table_nodes(table_id, 'ajax_nodes')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'node_del':
                node_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = db.nodes.nodename
    q = db.nodes.id>0
    j = db.apps.app == db.nodes.project
    l = db.apps.on(j)
    q = _where(q, 'nodes', domain_perms(), 'nodename')
    q = apply_filters(q, db.nodes.nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 10000
        t.csv_left = l
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.nodes.id.count(), left=l).first()(db.nodes.id.count())
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True, left=l)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def nodes():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ view_nodes("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def nodes_load():
    return nodes()["table"]

class col_user_id(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        h = self.get(o)
        d = DIV(
              A(
                o['user_id'],
                _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
                  url=URL(r=request, c='nodes',f='ajax_uid_dispatch',
                          vars={'user_id': o['user_id']}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class table_uids(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['user_id',
                     'user_id_count',
                     'user_name']
        self.keys = ["user_id"]
        self.span = ["user_id"]
        self.colprops = {
            'user_id': col_user_id(
                     title='User id',
                     field='user_id',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
            'user_id_count': HtmlTableColumn(
                     title='User count',
                     field='user_id_count',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
            'user_name': HtmlTableColumn(
                     title='User name',
                     field='user_name',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
        }
        self.colprops['user_id'].t = self
        self.extraline = True
        self.checkboxes = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_uids_col_values'

    def extra_line_key(self, o):
        return "uid_"+str(o['user_id'])

def free_ids(rows, start=500):
    if len(rows) == 0:
        l = range(start, 20)
    else:
        uids = map(lambda x: x[0], rows)
        l = []
        i = start
        while len(l) < 20:
            if i in uids:
                i += 1
                continue
            l.append(i)
            i += 1
    return DIV(
             "\n".join(map(lambda x: str(x), l)),
             _class="pre",
           )

class col_group_id(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        h = self.get(o)
        d = DIV(
              A(
                o['group_id'],
                _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
                  url=URL(r=request, c='nodes',f='ajax_gid_dispatch',
                          vars={'group_id': o['group_id']}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class table_gids(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['group_id',
                     'group_id_count',
                     'group_name']
        self.keys = ["group_id"]
        self.span = ["group_id"]
        self.colprops = {
            'group_id': col_group_id(
                     title='User id',
                     field='group_id',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
            'group_id_count': HtmlTableColumn(
                     title='Group count',
                     field='group_id_count',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
            'group_name': HtmlTableColumn(
                     title='Group name',
                     field='group_name',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
        }
        self.colprops['group_id'].t = self
        self.checkboxes = True
        self.extraline = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_gids_col_values'

    def extra_line_key(self, o):
        return "gid_"+str(o['group_id'])

@auth.requires_login()
def ajax_obs_agg():
    def get_rows(field_date):
        q = db.nodes.id>0
        q = _where(q, 'nodes', domain_perms(), 'nodename')
        q = apply_filters(q, db.nodes.nodename, None)
        if "nodes[]" in request.vars:
            q &= db.nodes.nodename.belongs(request.vars["nodes[]"])
        return db(q).select(db.nodes.id.count(),
                            db.nodes[field_date],
                            groupby=db.nodes[field_date],
                            orderby=db.nodes[field_date])

    def get_data(field_date):
        data = []
        cumul = []
        prev = 0
        max = 0
        rows = get_rows(field_date)
        for row in rows:
            if row.nodes[field_date] is None:
                continue
            val = row(db.nodes.id.count())
            if prev+val > max: max = prev+val
            data.append([row.nodes[field_date].strftime('%Y-%m-%d %H:%M:%S'),
                         val])
            cumul.append([row.nodes[field_date].strftime('%Y-%m-%d %H:%M:%S'),
                          prev+val])
            prev = cumul[-1][1]
        nowserie = [[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0],
                    [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), max]]
        return [data, cumul, nowserie]

    h = {}
    h['hw_warn_chart_data'] = get_data('hw_obs_warn_date')
    h['hw_alert_chart_data'] = get_data('hw_obs_alert_date')
    h['os_warn_chart_data'] = get_data('os_obs_warn_date')
    h['os_alert_chart_data'] = get_data('os_obs_alert_date')

    return DIV(
             STYLE("""
.chartcontainer {
  float:left;
  width:45%;
  min-width:350px;
  padding:10px;
  padding-left:30px;
  padding-right:30px
}

             """),
             DIV(
               H3(T("Hardware obsolescence warnings roadmap")),
               DIV(
                 XML(json.dumps(h['hw_warn_chart_data'])),
                 _id='hw_warn_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Hardware obsolescence alerts roadmap")),
               DIV(
                 XML(json.dumps(h['hw_alert_chart_data'])),
                 _id='hw_alert_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Operating system obsolescence warnings roadmap")),
               DIV(
                 XML(json.dumps(h['os_warn_chart_data'])),
                 _id='os_warn_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Operating system obsolescence alerts roadmap")),
               DIV(
                 XML(json.dumps(h['os_alert_chart_data'])),
                 _id='os_alert_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(XML('&nbsp;'), _class='spacer'),


             SCRIPT("""
$("#hw_warn_chart").each(function(){
  obsplot($(this))
})
$("#hw_alert_chart").each(function(){
  obsplot($(this))
})
$("#os_warn_chart").each(function(){
  obsplot($(this))
})
$("#os_alert_chart").each(function(){
  obsplot($(this))
})
""",
               _name="obs_agg_to_eval",
             ),
           )

@auth.requires_login()
def ajax_uids_col_values():
    col = request.args[0]
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_uids('uids', 'ajax_uids')

    q = _where(None, 'nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.nodes.nodename).rstrip(';')

    q = db.v_uids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_uids.", "u.")

    o = 'u.'+col

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_users.id as id,
                  node_users.user_id as user_id,
                  count(distinct node_users.user_name) as user_id_count,
                  group_concat(distinct node_users.user_name order by node_users.user_name separator ',') as user_name
                from node_users
                where
                  node_users.nodename in (%(sql)s)
                group by node_users.user_id
              ) u
              where %(where)s
              order by %(o)s
           """%dict(
                sql=sql1,
                where=where,
                o=o,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)
    return mt.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_uids():
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_uids('uids', 'ajax_uids')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.nodes.nodename).rstrip(';')

    q = db.v_uids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_uids.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_users.id as id,
                  node_users.user_id as user_id,
                  count(distinct node_users.user_name) as user_id_count,
                  group_concat(distinct node_users.user_name order by node_users.user_name separator ',') as user_name
                from node_users
                where
                  node_users.nodename in (%(sql)s)
                group by node_users.user_id
              ) u
              where %(where)s
              order by user_id
             """%dict(
                sql=sql1,
                where=where,
           )

    if len(request.args) != 1 or (request.args[0] not in ('csv', 'commonality')):
        sql2 += """
              limit %(limit)d
              offset %(offset)d"""%dict(
                limit=mt.perpage,
                offset=mt.pager_start,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return mt.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)


@auth.requires_login()
def ajax_gids_col_values():
    col = request.args[0]
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_gids('gids', 'ajax_gids')

    q = _where(None, 'nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.nodes.nodename).rstrip(';')

    q = db.v_gids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_gids.", "u.")

    o = 'u.'+col

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_groups.id as id,
                  node_groups.group_id as group_id,
                  count(distinct node_groups.group_name) as group_id_count,
                  group_concat(distinct node_groups.group_name order by node_groups.group_name separator ',') as group_name
                from node_groups
                where
                  node_groups.nodename in (%(sql)s)
                group by node_groups.group_id
              ) u
              where %(where)s
              order by %(o)s
           """%dict(
                sql=sql1,
                where=where,
                o=o,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)
    return mt.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_gids():
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_gids('gids', 'ajax_gids')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.nodes.nodename).rstrip(';')

    q = db.v_gids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_gids.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_groups.id as id,
                  node_groups.group_id as group_id,
                  count(distinct node_groups.group_name) as group_id_count,
                  group_concat(distinct node_groups.group_name order by node_groups.group_name separator ',') as group_name
                from node_groups
                where
                  node_groups.nodename in (%(sql)s)
                group by node_groups.group_id
              ) u
              where %(where)s
              order by group_id
              """%dict(
                sql=sql1,
                where=where,
           )

    if len(request.args) != 1 or (request.args[0] not in ('csv', 'commonality')):
        sql2 += """
              limit %(limit)d
              offset %(offset)d"""%dict(
                limit=mt.perpage,
                offset=mt.pager_start,
           )

    mt.object_list = db.executesql(sql2, as_dict=True)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return mt.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)


#
# Dashboard updates
#
def delete_dash_node_without_asset(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename="%(nodename)s" and
                 dash_type = "node without asset information"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_beyond_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end > now()
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_near_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end < now() and
                     maintenance_end > date_sub(now(), interval 30 day)
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_without_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end is not NULL
                 ) and
                 dash_type = "node without maintenance end date"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def delete_dash_node_not_updated(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "node information not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

@auth.requires_login()
def ajax_uid_dispatch():
    uid = request.vars.user_id
    sql = """select
               user_name,
               count(id) as n,
               group_concat(nodename order by nodename separator ", ") as nodes
             from node_users
             where
               user_id = %(uid)s
             group by user_name"""%dict(
            uid=uid,
          )
    rows = db.executesql(sql, as_dict=True)
    header = TR(
               TH(T('User name')),
               TH(T('Number of nodes')),
               TH(T('Nodes')),
             )
    l = [header]
    for row in rows:
        line = TR(
                 TD(row['user_name']),
                 TD(row['n']),
                 TD(row['nodes']),
               )
        l.append(line)
    return TABLE(SPAN(l))

@auth.requires_login()
def ajax_gid_dispatch():
    gid = request.vars.group_id
    sql = """select
               group_name,
               count(id) as n,
               group_concat(nodename order by nodename separator ", ") as nodes
             from node_groups
             where
               group_id = %(gid)s
             group by group_name"""%dict(
            gid=gid,
          )
    rows = db.executesql(sql, as_dict=True)
    header = TR(
               TH(T('Group name')),
               TH(T('Number of nodes')),
               TH(T('Nodes')),
             )
    l = [header]
    for row in rows:
        line = TR(
                 TD(row['group_name']),
                 TD(row['n']),
                 TD(row['nodes']),
               )
        l.append(line)
    return TABLE(SPAN(l))


@auth.requires_login()
def ajax_free_uids():
    start = request.vars.uid_start
    if start is None:
        start = 500
    else:
        start = int(start)
    sql = "select distinct user_id from node_users order by user_id"
    rows = db.executesql(sql)
    return free_ids(rows, start)

@auth.requires_login()
def ajax_free_gids():
    start = request.vars.gid_start
    if start is None:
        start = 500
    else:
        start = int(start)
    sql = "select distinct group_id from node_groups order by group_id"
    rows = db.executesql(sql)
    return free_ids(rows, start)


