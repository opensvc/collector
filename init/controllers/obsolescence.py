def ajax_obsolete_os_nodes():
    if request.vars.obs_type == "os":
        query = (db.obsolescence.obs_type=="os")&(db.v_nodes.os_concat==request.vars.obs_name)
    elif request.vars.obs_type == "hw":
        query = (db.obsolescence.obs_type=="hw")&(db.v_nodes.model==request.vars.obs_name)
    else:
        return DIV()

    query = apply_db_filters(query, 'v_nodes')
    rows = db(query).select(db.v_nodes.nodename, orderby=db.v_nodes.nodename, groupby=db.v_nodes.nodename)
    nodes = [row.nodename for row in rows]
    return DIV(
             H3(T("""Nodes in %(os)s""",dict(os=request.vars.obs_name))),
             PRE('\n'.join(nodes)),
           )

def refresh_obsolescence():
    cron_obsolescence_os()
    cron_obsolescence_hw()

def cron_obsolescence_hw():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "hw", model
             from nodes
             where model!=''
             group by model;
          """
    db.executesql(sql)
    return dict(message=T("done"))

def cron_obsolescence_os():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "os", concat_ws(" ", os_name, os_vendor, os_release, os_update)
             from nodes
             where os_name!='' or os_vendor!='' or os_release!='' or os_update!=''
             group by os_name, os_vendor, os_release, os_update;
          """
    db.executesql(sql)
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
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _class="datetime",
                  _onfocus='timepicker(this)',
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s');"""%dict(sid=sid, tid=tid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="warn_date_set"),
                ),
                _id=sid,
                _style="display:none",
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
                  _class="datetime",
                  _onfocus='timepicker(this)',
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s');"""%dict(sid=sid, tid=tid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                            args="alert_date_set"),
                ),
                _id=sid,
                _style="display:none",
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
        if 'Manager' in user_groups():
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
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_membership('Manager')
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

@auth.requires_membership('Manager')
def warn_date_set():
    date_set('warn')

@auth.requires_membership('Manager')
def alert_date_set():
    date_set('alert')

@auth.requires_membership('Manager')
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
    elif t == 'alert':
        db(q).update(obs_alert_date=new)
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
    q |= (db.obsolescence.obs_type=="hw")&(db.obsolescence.obs_name==db.v_nodes.model)
    q &= ~db.v_nodes.model.like("%virtual%")
    q &= ~db.v_nodes.model.like("%virtuel%")
    q &= ~db.v_nodes.model.like("%cluster%")
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

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
def update_dash_obs_hw_warn(obs_name):
    sql = """delete from dashboard
              where
                dash_dict = '{"o": "%(obs_name)s"}' and
                dash_type="hardware obsolescence warning"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

    sql = """insert ignore into dashboard
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
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_name = "%(obs_name)s" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

def update_dash_obs_hw_alert(obs_name):
    sql = """delete from dashboard
              where
                dash_dict = '{"o": "%(obs_name)s"}' and
                dash_type="hardware obsolescence alert"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

    sql = """insert ignore into dashboard
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
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_name = "%(obs_name)s" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

def update_dash_obs_os_warn(obs_name):
    sql = """delete from dashboard
              where
                dash_dict = '{"o": "%(obs_name)s"}' and
                dash_type="os obsolescence warning"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

    sql = """insert ignore into dashboard
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
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_name = "%(obs_name)s" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

def update_dash_obs_os_alert(obs_name):
    sql = """delete from dashboard
              where
                dash_dict = '{"o": "%(obs_name)s"}' and
                dash_type="os obsolescence alert"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

    sql = """insert ignore into dashboard
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
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_name = "%(obs_name)s" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
          """%dict(obs_name=obs_name)
    db.executesql(sql)

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


