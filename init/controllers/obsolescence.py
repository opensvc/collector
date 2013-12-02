def ajax_obsolete_os_nodes():
    if request.vars.obs_type == "os":
        query = (db.obsolescence.obs_type=="os")&(db.v_nodes.os_concat==request.vars.obs_name)
    elif request.vars.obs_type == "hw":
        query = (db.obsolescence.obs_type=="hw")&(db.v_nodes.model==request.vars.obs_name)
    else:
        return DIV()

    q = db.obsolescence.id > 0
    q = apply_filters(q, db.v_nodes.nodename, None)

    rows = db(query).select(db.v_nodes.nodename, orderby=db.v_nodes.nodename, groupby=db.v_nodes.nodename)
    nodes = [row.nodename for row in rows]
    return DIV(
             H3(T("""Nodes in %(os)s""",dict(os=request.vars.obs_name))),
             PRE('\n'.join(nodes)),
           )

def refresh_obsolescence():
    cron_obsolescence_os()
    cron_obsolescence_hw()
    purge_dash_obs_without()
    update_nodes_fields()

def update_nodes_fields():
    q = db.obsolescence.id > 0
    for row in db(q).select():
        _update_nodes_fields(row.obs_type, row.obs_name,
                             row.obs_warn_date, row.obs_alert_date)

def _update_nodes_fields(obs_type, obs_name, obs_warn_date, obs_alert_date):
        if obs_type == 'hw':
            sql = """update nodes set
                       hw_obs_warn_date="%(warn_date)s",
                       hw_obs_alert_date="%(alert_date)s"
                     where
                       model="%(name)s"
                  """%dict(warn_date=obs_warn_date,
                           alert_date=obs_alert_date,
                           name=obs_name)
        elif obs_type == 'os':
            sql = """update nodes set
                       os_obs_warn_date="%(warn_date)s",
                       os_obs_alert_date="%(alert_date)s"
                     where
                       concat_ws(" ", os_name, os_vendor, os_release, os_update)="%(name)s"
                  """%dict(warn_date=obs_warn_date,
                           alert_date=obs_alert_date,
                           name=obs_name)
        db.executesql(sql)

def cron_obsolescence_hw():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "hw", model
             from nodes
             where model!=''
             group by model
          """
    db.executesql(sql)
    db.commit()
    update_dash_obs_hw_alert()
    update_dash_obs_hw_warn()
    return dict(message=T("done"))

def cron_obsolescence_os():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "os", concat_ws(" ", os_name, os_vendor, os_release, os_update)
             from nodes
             where os_name!='' or os_vendor!='' or os_release!='' or os_update!=''
             group by os_name, os_vendor, os_release, os_update
          """
    db.executesql(sql)
    db.commit()
    update_dash_obs_os_alert()
    update_dash_obs_os_warn()
    return dict(message=T("done"))


class col_obs_warn_date(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no date)'
        else:
            ss = s
        tid = 'wd_t_%s'%o.obsolescence.id
        iid = 'wd_i_%s'%o.obsolescence.id
        sid = 'wd_s_%s'%o.obsolescence.id
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""$('#%(tid)s').hide();$('#%(sid)s').show();$('#%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _class="date",
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="warn_date_set"),
                ),
                A(
                  T("save"),
                  _onclick=self.t.ajax_submit(additional_inputs=[iid], args="warn_date_set"),
                  _class="toola",
                ),
                A(
                  T("cancel"),
                  _onclick="""$('#%(sid)s').hide();$('#%(tid)s').show()"""%dict(tid=tid, sid=sid, iid=iid),
                  _class="toola",
                ),
                _id=sid,
                _style="display:none",
              ),
              SCRIPT(
                """$(".date").datepicker({dateFormat: "yy-mm-dd"})""",
              ),
            )
        return d

class col_obs_alert_date(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no date)'
        else:
            ss = s
        tid = 'ad_t_%s'%o.obsolescence.id
        iid = 'ad_i_%s'%o.obsolescence.id
        sid = 'ad_s_%s'%o.obsolescence.id
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _class="date",
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                            args="alert_date_set"),
                ),
                A(
                  T("save"),
                  _onclick=self.t.ajax_submit(additional_inputs=[iid], args="alert_date_set"),
                  _class="toola",
                ),
                A(
                  T("cancel"),
                  _onclick="""$('#%(sid)s').hide();$('#%(tid)s').show()"""%dict(tid=tid, sid=sid, iid=iid),
                  _class="toola",
                ),
                _id=sid,
                _style="display:none",
              ),
              SCRIPT(
                """$(".date").datepicker({dateFormat: "yy-mm-dd"})""",
              ),
            )
        return d

class col_obs_count(HtmlTableColumn):
    def get(self, o):
        return o['COUNT(v_nodes.id)']

    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        d = DIV(
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='obsolescence',f='ajax_obsolete_os_nodes',
                          vars={'obs_name': o.obsolescence.obs_name,
                                'obs_type': o.obsolescence.obs_type}),
                  id=id,
                ),
              ),
            )
        return d

class col_obs_type(HtmlTableColumn):
    img_h = {
        'os': 'os',
        'hw': 'hw',
    }
    def html(self, o):
        t = self.get(o)
        return IMG(
                 _src=URL(r=request,c='static',f=self.img_h[t]+'.png'),
               )

class table_obs(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['obs_count',
                     'obs_type',
                     'obs_name',
                     'obs_warn_date',
                     'obs_alert_date']
        self.colprops = {
            'obs_type': col_obs_type(
                     title='Type',
                     table='obsolescence',
                     field='obs_type',
                     img='svc',
                     display=True,
                    ),
            'obs_name': HtmlTableColumn(
                     title='Name',
                     table='obsolescence',
                     field='obs_name',
                     img='svc',
                     display=True,
                    ),
            'obs_warn_date': col_obs_warn_date(
                     title='Warn date',
                     table='obsolescence',
                     field='obs_warn_date',
                     img='time16',
                     display=True,
                    ),
            'obs_alert_date': col_obs_alert_date(
                     title='Alert date',
                     table='obsolescence',
                     field='obs_alert_date',
                     img='time16',
                     display=True,
                    ),
            'obs_count': col_obs_count(
                     title='Count',
                     table='v_nodes',
                     field='count',
                     img='svc',
                     display=True,
                    ),
        }
        self.checkbox_id_table = 'obsolescence'
        self.colprops['obs_warn_date'].t = self
        self.colprops['obs_alert_date'].t = self
        self.colprops['obs_count'].t = self
        self.ajax_col_values = 'ajax_obs_col_values'
        self.dbfilterable = True
        self.checkboxes = True
        self.extraline = True
        if 'ObsManager' in user_groups():
            self.additional_tools.append('item_del')
            self.additional_tools.append('item_refresh')

    def item_refresh(self):
        d = DIV(
              A(
                T("Refresh items"),
                _onclick=self.ajax_submit(args=['item_refresh'])
              ),
              _class='floatw',
            )
        return d

    def item_del(self):
        d = DIV(
              A(
                T("Delete items"),
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['item_del']),
                                  text=T("Deleting an obsolescence configuration item also deletes the warning and alert dates. Please confirm deletion"),
                                 ),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def ajax_obs_col_values():
    t = table_obs('obs', 'ajax_obs')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = (db.obsolescence.obs_type=="os")&(db.obsolescence.obs_name==db.v_nodes.os_concat)
    q |= (db.obsolescence.obs_type=="hw")&(db.obsolescence.obs_name==db.v_nodes.model)
    q &= ~db.v_nodes.model.like("%virtual%")
    q &= ~db.v_nodes.model.like("%virtuel%")
    q &= ~db.v_nodes.model.like("%cluster%")
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_gen_filters(q, ['v_nodes', 'obsolescence'])

    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_membership('ObsManager')
def item_del(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete item failed: no item selected")
    q = db.obsolescence.id.belongs(ids)
    rows = db(q).select(db.obsolescence.obs_name)
    x = ', '.join([r.obs_name for r in rows])
    db(q).delete()
    _log('obsolescence.item.delete',
         'deleted items %(x)s',
         dict(x=x))

@auth.requires_membership('ObsManager')
def warn_date_set():
    date_set('warn')

@auth.requires_membership('ObsManager')
def alert_date_set():
    date_set('alert')

@auth.requires_membership('ObsManager')
def date_set(t):
    prefix = t[0]+'d_i_'
    l = [k for k in request.vars if prefix in k]
    if len(l) == 0:
        raise ToolError("set date failed: no item selected")
    elif len(l) > 1:
        raise ToolError("set date failed: too many item selected")
    id = int(l[0].replace(prefix,''))
    new = request.vars[l[0]]
    q = db.obsolescence.id==id
    rows = db(q).select()
    n = len(rows)
    if n != 1:
        raise ToolError("set date failed: can't find selected item")
    iid = rows[0].obs_name
    if t == 'warn':
        db(q).update(obs_warn_date=new)
        _update_nodes_fields(rows[0].obs_type, rows[0].obs_name,
                             new, rows[0].obs_alert_date)
    elif t == 'alert':
        db(q).update(obs_alert_date=new)
        _update_nodes_fields(rows[0].obs_type, rows[0].obs_name,
                             rows[0].obs_warn_date, new)
    else:
        raise Exception()
    _log('obsolescence.item.change',
         'set %(t)s date %(d)s for obsolescence item %(x)s',
         dict(t=t, x=iid, d=new))
    if rows[0].obs_type == "os":
        update_dash_obs_os_warn(iid)
        update_dash_obs_os_alert(iid)
    elif rows[0].obs_type == "hw":
        update_dash_obs_hw_alert(iid)
        update_dash_obs_hw_warn(iid)
    delete_dash_obs_without(iid, rows[0].obs_type, t)

@auth.requires_login()
def ajax_obs():
    t = table_obs('obs', 'ajax_obs')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'warn_date_set':
                warn_date_set()
            if action == 'alert_date_set':
                alert_date_set()
            if action == 'item_del':
                item_del(t.get_checked())
            if action == 'item_refresh':
                refresh_obsolescence()
        except ToolError, e:
            t.flash = str(e)

    o = db.obsolescence.obs_type
    o |= db.obsolescence.obs_name
    o |= db.obsolescence.obs_warn_date
    o |= db.obsolescence.obs_alert_date

    g = db.obsolescence.obs_type|db.obsolescence.obs_name

    q = (db.obsolescence.obs_type=="os")&(db.obsolescence.obs_name==db.v_nodes.os_concat)
    q2 = ~db.v_nodes.model.like("%virtual%")
    q2 &= ~db.v_nodes.model.like("%virtuel%")
    q2 &= ~db.v_nodes.model.like("%cluster%")
    q |= (db.obsolescence.obs_type=="hw")&(db.obsolescence.obs_name==db.v_nodes.model)&q2
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_gen_filters(q, ['v_nodes', 'obsolescence'])

    n = len(db(q).select(g, groupby=g))
    t.setup_pager(n)
    t.object_list = db(q).select(db.obsolescence.ALL,
                                 db.v_nodes.id.count(),
                                 limitby=(t.pager_start,t.pager_end),
                                 orderby=o, groupby=g)
    return t.html()

@auth.requires_login()
def obsolescence_config():
    t = DIV(
          ajax_obs(),
          _id='obs',
        )
    return dict(table=t)


#
# Dashboard updates
#
def _update_dash_obs_hw_warn():
    update_dash_obs_hw_warn()

def update_dash_obs_hw_warn(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
        where_dash_dict = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)
        where_dash_dict = """dash_dict like '%%"o": "%(obs_name)s"%%' and"""%dict(obs_name=obs_name)

    sql = """select n.model from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_type = "hw" and (
                  o.obs_alert_date is NULL or
                  o.obs_name like "%%virtual%%" or
                  o.obs_name like "%%virtuel%%" or
                  o.obs_name like "%%cluster%%" or
                  o.obs_alert_date = "0000-00-00 00:00:00" or
                  o.obs_warn_date >= now() or
                  o.obs_alert_date <= now()
                 )
          """%dict(where_obs_name=where_obs_name)
    rows = db.executesql(sql)
    for row in rows:
        sql = """delete from dashboard
                  where
                    dash_dict like '%%"o": "%(obs_name)s"%%' and
                    dash_type="hardware obsolescence warning"
              """%dict(obs_name=row[0])
        db.executesql(sql)
    db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "hardware obsolescence warning",
                 "",
                 n.nodename,
                 0,
                 "%%(o)s warning since %%(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.host_mode,
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_name not like "%%virtual%%" and
                 o.obs_name not like "%%virtuel%%" and
                 o.obs_name not like "%%cluster%%" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def _update_dash_obs_hw_alert():
    update_dash_obs_hw_alert()

def update_dash_obs_hw_alert(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
        where_dash_dict = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)
        where_dash_dict = """dash_dict like '%%"o": "%(obs_name)s"%%' and"""%dict(obs_name=obs_name)


    sql = """select n.model from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_type = "hw" and (
                  o.obs_alert_date is NULL or
                  o.obs_name like "%%virtual%%" or
                  o.obs_name like "%%virtuel%%" or
                  o.obs_name like "%%cluster%%" or
                  o.obs_alert_date = "0000-00-00 00:00:00" or
                  o.obs_alert_date >= now()
                 )
          """%dict(where_obs_name=where_obs_name)
    rows = db.executesql(sql)
    for row in rows:
        sql = """delete from dashboard
                  where
                    dash_dict like '%%"o": "%(obs_name)s"%%' and
                    dash_type="hardware obsolescence alert"
              """%dict(obs_name=row[0])
        db.executesql(sql)
    db.commit()


    sql = """insert into dashboard
               select
                 NULL,
                 "hardware obsolescence alert",
                 "",
                 n.nodename,
                 1,
                 "%%(o)s obsolete since %%(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.host_mode,
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_name not like "%%virtual%%" and
                 o.obs_name not like "%%virtuel%%" and
                 o.obs_name not like "%%cluster%%" and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()


def _update_dash_obs_os_warn():
    update_dash_obs_os_warn()

def update_dash_obs_os_warn(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
        where_dash_dict = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)
        where_dash_dict = """dash_dict like '%%"o": "%(obs_name)s"%%' and"""%dict(obs_name=obs_name)

    if obs_name is not None:
        sql = """select o.obs_name from obsolescence o
                     join nodes n on
                       o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
                   where
                     %(where_obs_name)s
                     o.obs_type = "os" and (
                      o.obs_alert_date is NULL or
                      o.obs_alert_date = "0000-00-00 00:00:00" or
                      o.obs_warn_date >= now() or
                      o.obs_alert_date <= now()
                     )
              """%dict(where_obs_name=where_obs_name)
        rows = db.executesql(sql)
        for row in rows:
            sql = """delete from dashboard
                      where
                        dash_dict like '%%"o": "%(obs_name)s"%%' and
                        dash_type="os obsolescence warning"
                  """%dict(obs_name=row[0])
            db.executesql(sql)
        db.commit()
    else:
        sql = """delete from dashboard
                      where
                        dash_updated < date_sub(now(), interval 2 day) and
                        dash_type="os obsolescence warning"
                  """
        db.executesql(sql)
        db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "os obsolescence warning",
                 "",
                 n.nodename,
                 0,
                 "%%(o)s warning since %%(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.host_mode,
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def _update_dash_obs_os_alert():
    update_dash_obs_os_alert()

def update_dash_obs_os_alert(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
        where_dash_dict = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)
        where_dash_dict = """dash_dict like '%%"o": "%(obs_name)s"%%' and"""%dict(obs_name=obs_name)

    if obs_name is not None:
        sql = """select o.obs_name from obsolescence o
                     join nodes n on
                       o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
                   where
                     %(where_obs_name)s
                     o.obs_type = "os" and (
                      o.obs_alert_date is NULL or
                      o.obs_alert_date = "0000-00-00 00:00:00" or
                      o.obs_alert_date >= now()
                     )
              """%dict(where_obs_name=where_obs_name)
        rows = db.executesql(sql)
        for row in rows:
            sql = """delete from dashboard
                      where
                        dash_dict like '%%"o": "%(obs_name)s"%%' and
                        dash_type="os obsolescence alert"
                  """%dict(obs_name=row[0])
            db.executesql(sql)
        db.commit()
    else:
        sql = """delete from dashboard
                      where
                        dash_updated < date_sub(now(), interval 2 day) and
                        dash_type="os obsolescence alert"
                  """
        db.executesql(sql)
        db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "os obsolescence alert",
                 "",
                 n.nodename,
                 1,
                 "%%(o)s obsolete since %%(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.host_mode,
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def delete_dash_obs_without(obs_name, t, a):
    if t == "hw":
        tl = "hardware"
    else:
        tl = t
    if a == "warn":
        al = "warning"
    else:
        al = a
    sql = """delete from dashboard
             where
               dash_dict = '{"o": "%(obs_name)s"}' and
               dash_type="%(tl)s obsolescence %(al)s date not set"
          """%dict(obs_name=obs_name, tl=tl, al=al)
    db.executesql(sql)
    db.commit()

def purge_dash_obs_without():
    data_hw = (
             ("hardware obsolescence warning date not set", "hw"),
             ("hardware obsolescence alert date not set", "hw"),
           )
    data_os = (
             ("os obsolescence alert date not set", "os"),
             ("os obsolescence warning date not set", "os")
           )

    for dash_type, obs_type in data_hw:
        sql = """select d.id from dashboard d
                 join nodes n on d.dash_nodename=n.nodename
                 where
                   d.dash_type="%(dash_type)s" and
                   d.dash_dict != concat('{"o": "', n.model, '"}')
        """%dict(dash_type=dash_type)
        rows = db.executesql(sql, as_dict=True)

        q = db.dashboard.id.belongs([r["id"] for r in rows])
        db(q).delete()
        db.commit()

    for dash_type, obs_type in data_os:
        sql = """select d.id from dashboard d
                 join nodes n on d.dash_nodename=n.nodename
                 where
                   d.dash_type="%(dash_type)s" and
                   d.dash_dict != concat('{"o": "', n.os_name, " ", n.os_vendor, " ", n.os_release, ' "}')
        """%dict(dash_type=dash_type)
        rows = db.executesql(sql, as_dict=True)

        q = db.dashboard.id.belongs([r["id"] for r in rows])
        db(q).delete()
        db.commit()

    for dash_type, obs_type in data_os + data_hw:
        sql = """delete from dashboard
                 where
                   dash_type = "%(dash_type)s" and
                   dash_dict in (
                     select
                       concat('{"o": "', obs_name, '"}')
                     from obsolescence
                     where
                       obs_warn_date is not null and
                       obs_type = "%(obs_type)s"
                   )
        """%dict(dash_type=dash_type, obs_type=obs_type)
        db.executesql(sql)
        db.commit()

