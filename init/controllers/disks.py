def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

array_img_h = {
  'DMX3-24': 'emc',
  '3000-M2': 'emc',
  'HSV210': 'hpux',
  'HSV340': 'hpux',
  'HSV400': 'hpux',
  'SANsymphony-V': 'datacore',
}

def refresh_b_disk_app():
    sql = """select max(update_time)>(select update_time from
information_schema.tables where table_schema="opensvc" and
table_name='b_disk_app') as need_update , max(update_time) as
src_tables_last_update, (select update_time from information_schema.tables
where table_schema="opensvc" and table_name='b_disk_app') as
b_disk_app_last_update from information_schema.tables where
table_schema="opensvc" and table_name in ('nodes', 'services', 'apps',
'svcdisks', 'diskinfo')"""
    rows = db.executesql(sql)
    if rows[0][0] is not None and rows[0][0] != 1:
        return "skip " + str(rows)
    sql = """drop table if exists b_disk_app_old"""
    db.executesql(sql)
    sql = """drop table if exists b_disk_app_tmp"""
    db.executesql(sql)
    sql = """create table b_disk_app_tmp as select * from v_disk_app"""
    db.executesql(sql)
    sql = """rename table b_disk_app to b_disk_app_old, b_disk_app_tmp to b_disk_app"""
    db.executesql(sql)
    sql = """drop table if exists b_disk_app_old"""
    db.executesql(sql)

def array_icon(array_model):
    if array_model is None:
        return ''
    if array_model in array_img_h:
        img = IMG(
                _src=URL(r=request,c='static',f=array_img_h[array_model]+'.png'),
                _class='logo'
              )
    else:
        img = ''
    return img

class col_app(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        app = self.get(o)
        app_id = self.t.colprops['app_id'].get(o)
        dg_id = self.t.colprops['dg_id'].get(o)
        if app == 'unknown':
            return T(app)
        if app_id is None:
            return ''
        d = DIV(
              A(
                app,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='disks',f='ajax_app',
                          vars={'app_id': app_id, 'dg_id': dg_id, 'rowid': id}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class col_array_dg(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        dg = self.get(o)
        try:
            s = self.t.colprops['disk_arrayid'].get(o)
        except:
            s = self.t.colprops['array_name'].get(o)
        if dg is None or len(dg) == 0:
            return ''
        d = DIV(
              A(
                dg,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='disks',f='ajax_array_dg',
                          vars={'array': s, 'dg': dg, 'rowid': id}),
                  id=id,
                ),
                _class="bluer",
              ),
              _class='nowrap',
            )
        return d

class col_array(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        if s is None or len(s) == 0:
            return ''
        if 'array_model' in self.t.colprops:
            img = array_icon(self.t.colprops['array_model'].get(o))
        else:
            img = ''
        d = DIV(
              img,
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='disks',f='ajax_array',
                          vars={'array': s, 'rowid': id}),
                  id=id,
                ),
                _class="bluer",
              ),
              _class='nowrap',
            )
        return d

class col_chart(HtmlTableColumn):
    def html(self, o):
       l = []
       if len(o['chart_svc']) > 2:
           l += [DIV(
                      H3(T("Services")),
                      DIV(
                        o['chart_svc'],
                        _id='chart_svc',
                      ),
                      _style="float:left;width:500px",
                    )]
       if len(o['chart_ap']) > 2:
           l += [DIV(
                      H3(T("Applications")),
                      DIV(
                        o['chart_ap'],
                        _id='chart_ap',
                      ),
                      _style="float:left;width:500px",
                    )]
       if len(o['chart_dg']) > 2:
           l += [DIV(
                  H3(T("Disk Groups")),
                  DIV(
                    o['chart_dg'],
                    _id='chart_dg',
                  ),
                  _style="float:left;width:500px",
                )]

       if len(o['chart_ar']) > 2:
           l += [DIV(
                  H3(T("Disk Arrays")),
                  DIV(
                    o['chart_ar'],
                    _id='chart_ar',
                  ),
                  _style="float:left;width:500px",
                )]
       l += [DIV(
               _class='spacer',
             )]
       l += [DIV(
               _id='chart_info',
             )]
       return DIV(l)

class col_disk_id(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       return PRE(d)

class col_size_gb(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d is None:
           return ''
       unit = 'GB'
       return DIV("%d %s"%(d/1024, unit))

class col_size_mb(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       try:
           d = int(d)
       except:
           return ''
       c = "nowrap"
       if d < 0:
           c += " highlight"
       if d is None:
           return ''
       return DIV(beautify_size_mb(d), _class=c)

def beautify_size_mb(d):
       try:
          d = int(d)
       except:
          return '-'
       if d < 0:
           neg = True
           d = -d
       else:
           neg = False
       if d < 1024:
           v = 1.0 * d
           unit = 'MB'
       elif d < 1048576:
           v = 1.0 * d / 1024
           unit = 'GB'
       else:
           v = 1.0 * d / 1048576
           unit = 'TB'
       if v >= 100:
           fmt = "%d"
       elif v >= 10:
           fmt = "%.1f"
       else:
           fmt = "%.2f"
       fmt = fmt + " %s"
       if neg:
           v = -v
       return fmt%(v, unit)

class col_quota_used(HtmlTableColumn):
    def html(self, o):
        if o.app is None:
            return ""
        s = self.get(o)
        ss = s
        c = "nowrap"
        if s is None:
            s = "-"
            ss = ""
        elif s > o.quota:
            c += " highlight"
        if s != "-":
            s = beautify_size_mb(int(s))
        return SPAN(
                 s,
                 _class=c,
                 _title="%s MB"%str(ss),
               )

class col_quota(HtmlTableColumn):
    def html(self, o):
        if o.app is None:
            return ""
        s = self.get(o)
        if s is None:
            s = "-"
            ss = ""
        else:
            ss = s
            s = beautify_size_mb(int(s))

        if o.app == "unknown":
            return DIV(s, _class="status_undef")

        tid = 'd_t_%s'%o.id
        iid = 'd_i_%s'%o.id
        sid = 'd_s_%s'%o.id
        if 'StorageManager' in user_groups():
            d = SPAN(
              DIV(
                s,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable",
                _title="%s MB"%str(ss),
              ),
              SPAN(
                INPUT(
                  value=ss,
                  _id=iid,
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s')"""%dict(tid=tid, sid=sid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="quota_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        else:
            d = SPAN(s)
        return d

class table_quota(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['array_name',
                     'array_model',
                     'dg_name',
                     'dg_size',
                     'dg_reserved',
                     'dg_reservable',
                     'dg_used',
                     'dg_free',
                     'app',
                     'quota',
                     'quota_used']
        self.colprops.update({
            'array_name': col_array(
                     title='Array',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_name',
                     img='hd16',
                     display=True,
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_model',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'array_id': HtmlTableColumn(
                     title='Array Id',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_id',
                     img='hd16',
                     display=True,
                    ),
            'dg_name': col_array_dg(
                     title='Array Disk Group',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_name',
                     img='hd16',
                     display=True,
                    ),
            'dg_free': col_size_mb(
                     title='Free',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_free',
                     img='hd16',
                     display=True,
                    ),
            'dg_used': col_size_mb(
                     title='Used',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_used',
                     img='hd16',
                     display=True,
                    ),
            'dg_reservable': col_size_mb(
                     title='Reservable',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_reservable',
                     img='hd16',
                     display=True,
                    ),
            'dg_reserved': col_size_mb(
                     title='Reserved',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_reserved',
                     img='hd16',
                     display=True,
                    ),
            'dg_size': col_size_mb(
                     title='Size',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_size',
                     img='hd16',
                     display=True,
                    ),
            'dg_id': HtmlTableColumn(
                     title='Array Disk Group Id',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_id',
                     img='hd16',
                     display=True,
                    ),
            'app': col_app(
                     title='App',
                     #table='apps',
                     table='v_disk_quota',
                     field='app',
                     img='svc',
                     display=True,
                    ),
            'app_id': HtmlTableColumn(
                     title='App Id',
                     #table='apps',
                     table='v_disk_quota',
                     field='app_id',
                     img='svc',
                     display=True,
                    ),
            'quota': col_quota(
                     title='Quota',
                     #table='stor_array_dg_quota',
                     table='v_disk_quota',
                     field='quota',
                     img='hd16',
                     display=True,
                    ),
            'quota_used': col_quota_used(
                     title='Quota Used',
                     #table='stor_array_dg_quota',
                     table='v_disk_quota',
                     field='quota_used',
                     img='hd16',
                     display=True,
                    ),
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkboxes = True
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_quota_col_values'
        #self.span = 'array_name'
        #self.sub_span = ['dg_free', 'array_model', 'array_name']

        if 'StorageManager' in user_groups():
            self.additional_tools.append('app_attach')
            self.additional_tools.append('app_detach')
        if 'StorageManager' in user_groups() or \
           'StorageExec' in user_groups():
            self.additional_tools.append('provision')
        self.additional_tools.append('disks_link')

    def provision(self):
        d = DIV(
              A(
                T("Provision"),
                _class='prov',
                _onclick="""$('#prov_container').toggle();ajax('%(url)s', [], '%(id)s')"""%dict(
                  url=URL(r=request, c='disks', f='ajax_provision'),
                  id="prov_container",
                ),
              ),
              DIV(
                _style='display:none',
                _class='white_float',
                _id="prov_container",
              ),
              _class='floatw',
            )
        return d

    def extra_line_key(self, o):
        l = [self.id,
             'x',
             str(self.colprops['dg_id'].get(o)),
             str(self.colprops['array_id'].get(o)),
             str(self.colprops['app_id'].get(o))]
        return '_'.join(l)

    def disks_link(self):
        d = DIV(
              A(
                T("Disks"),
                _class='hd16',
                _href=URL(r=request, f='disks'),
              ),
              _class='floatw',
            )
        return d

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        ids = []
        ids.append(self.colprops['dg_id'].get(o))
        ids.append(self.colprops['array_id'].get(o))
        ids.append(self.colprops['app_id'].get(o))
        return '_'.join([self.id, 'ckid']+map(str,ids))

    def app_select_tool(self, label, action, divid, sid, _class=''):
        q = db.apps.id > 0
        o = db.apps.app
        options = [OPTION(g.app,_value=g.id) for g in db(q).select(orderby=o)]
        d = DIV(
              A(
                T(label),
                _class=_class,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('App')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid,
                               _requires=IS_IN_DB(db, 'apps.id'))
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
                _id=divid,
              ),
              _class="floatw",
            )
        return d

    def app_attach(self):
        d = self.app_select_tool(label="Attach app",
                                 action="app_attach",
                                 divid="app_attach",
                                 sid="app_attach_s",
                                 _class="attach16")
        return d

    def app_detach(self):
        d = DIV(
              A(
                T("Detach app"),
                _class='detach16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['app_detach']),
                                  text=T("Detaching applications from disk groups also drops quota information. Please confirm application detach"),
                                 ),
              ),
              _class="floatw",
            )
        return d

def update_dg_reserved():
    sql = """select dg_id, sum(v_disk_quota.quota)
             from v_disk_quota
             group by dg_id
          """
    rows = db.executesql(sql)
    for row in rows:
        if row[0] is None or row[1] is None:
           continue
        sql = """update stor_array_dg set dg_reserved=%(reserved)s
                 where id=%(dg_id)s
              """%dict(reserved=row[1], dg_id=row[0])
        db.executesql(sql)
    db.commit()

def _update_dg_reserved(dg_id):
    sql = """update stor_array_dg set dg_reserved=(
               select sum(v_disk_quota.quota) as reserved
               from v_disk_quota
               where dg_id=%(dg_id)s
             ) where id=%(dg_id)s
          """%dict(dg_id=dg_id)
    db.executesql(sql)
    db.commit()

@auth.requires_membership('StorageManager')
def quota_set():
    l = [k for k in request.vars if 'd_i_' in k]
    if len(l) != 1:
        raise ToolError("one quota must be selected")
    qid = int(l[0].replace('d_i_',''))
    new = request.vars[l[0]]
    new = new.replace(' ', '')

    try:
        if new.endswith('M'):
            new = new.replace('M', '')
            new = int(new)
        elif new.endswith('m'):
            new = new.replace('m', '')
            new = int(new)
        elif new.endswith('MB'):
            new = new.replace('MB', '')
            new = int(new)
        elif new.endswith('mb'):
            new = new.replace('mb', '')
            new = int(new)
        elif new.endswith('G'):
            new = new.replace('G', '')
            new = int(new) * 1024
        elif new.endswith('g'):
            new = new.replace('g', '')
            new = int(new) * 1024
        elif new.endswith('GB'):
            new = new.replace('GB', '')
            new = int(new) * 1024
        elif new.endswith('gb'):
            new = new.replace('gb', '')
            new = int(new) * 1024
        elif new.endswith('T'):
            new = new.replace('T', '')
            new = int(new) * 1024 * 1024
        elif new.endswith('t'):
            new = new.replace('t', '')
            new = int(new) * 1024 * 1024
        elif new.endswith('TB'):
            new = new.replace('TB', '')
            new = int(new) * 1024 * 1024
        elif new.endswith('tb'):
            new = new.replace('tb', '')
            new = int(new) * 1024 * 1024
    except:
        raise ToolError("quota must be an integer value")

    q = db.stor_array_dg_quota.id == qid
    q &= db.stor_array_dg_quota.app_id == db.apps.id
    q &= db.stor_array_dg_quota.dg_id == db.stor_array_dg.id
    q &= db.stor_array_dg.array_id == db.stor_array.id
    info = db(q).select().first()
    if info is None:
        raise ToolError("quota not found")

    q = db.stor_array_dg_quota.id == qid
    db(q).update(quota=new)
    _log('storage.quota.change',
         'set quota from %(old)s to %(new)s for application %(app)s in disk group %(dg)s of array %(array)s',
         dict(app=info.apps.app,
              new=str(new),
              old=str(info.stor_array_dg_quota.quota),
              dg=info.stor_array_dg.dg_name,
              array=info.stor_array.array_name))

    #_update_dg_reserved(info.stor_array_dg_quota.dg_id)


@auth.requires_membership('StorageManager')
def app_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no application selected")

    for id in ids:
        dg_id, array_id, app_id = id.split('_')
        q = db.stor_array_dg_quota.dg_id == int(dg_id)
        try:
            app_id = int(app_id)
        except:
            apps = db(db.apps.id>0).select(db.apps.id)
            qq = ~db.stor_array_dg_quota.app_id.belongs(apps)
            db(qq).delete()
            continue
        q &= db.stor_array_dg_quota.app_id == int(app_id)
        if db(q).count() == 0:
            continue
        db(q).delete()

        app = db(db.apps.id==app_id).select().first().app
        q = db.stor_array_dg.id == dg_id
        q &= db.stor_array_dg.array_id == db.stor_array.id
        info = db(q).select().first()
        _log('storage.quota.detach',
             'detached application quota %(app)s from disk group %(dg)s of array %(array)s',
             dict(app=app, dg=info.stor_array_dg.dg_name, array=info.stor_array.array_name))


@auth.requires_membership('StorageManager')
def app_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no disk group selected")
    app_id = request.vars.app_attach_s
    app = db(db.apps.id==app_id).select().first().app

    for id in ids:
        dg_id, array_id, _app_id = id.split('_')
        q = db.stor_array_dg_quota.dg_id == int(dg_id)
        q &= db.stor_array_dg_quota.app_id == int(app_id)
        if db(q).count() != 0:
            continue
        db.stor_array_dg_quota.insert(dg_id=dg_id, app_id=app_id)

        q = db.stor_array_dg.id == dg_id
        q &= db.stor_array_dg.array_id == db.stor_array.id
        info = db(q).select().first()
        _log('storage.quota.attach',
             'attached application quota %(app)s to disk group %(dg)s of array %(array)s',
             dict(app=app, dg=info.stor_array_dg.dg_name, array=info.stor_array.array_name))

@auth.requires_login()
def ajax_quota_col_values():
    t = table_quota('quota', 'ajax_quota')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.v_disk_quota.id>0
    q = _where(q, 'v_disk_quota', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_quota():
    t = table_quota('quota', 'ajax_quota')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'app_attach':
                app_attach(t.get_checked())
            elif action == 'app_detach':
                app_detach(t.get_checked())
            elif action == 'quota_set':
                quota_set()
        except ToolError, e:
            t.flash = str(e)

    update_dg_reserved()

    o = db.v_disk_quota.array_name | db.v_disk_quota.dg_name
    q = db.v_disk_quota.array_id > 0
    q = _where(q, 'v_disk_quota', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = len(db(q).select())
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()

@auth.requires_login()
def quota():
    t = DIV(
          ajax_quota(),
          _id='quota',
        )
    return dict(table=t)







class table_disks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['disk_id',
                     'disk_region',
                     'disk_vendor',
                     'disk_model',
                     'app',
                     'disk_nodename',
                     'disk_svcname',
                     'disk_dg',
                     'svcdisk_updated',
                     'disk_used',
                     'disk_size',
                     'disk_alloc',
                     'disk_name',
                     'disk_devid',
                     'disk_raid',
                     'disk_group',
                     'disk_arrayid',
                     'disk_level',
                     'array_model',
                     'disk_updated',
                     'loc_country',
                     'loc_zip',
                     'loc_city',
                     'loc_addr',
                     'loc_building',
                     'loc_floor',
                     'loc_room',
                     'loc_rack',
                     'power_supply_nb',
                     'power_cabinet1',
                     'power_cabinet2',
                     'power_protect',
                     'power_protect_breaker',
                     'power_breaker1',
                     'power_breaker2']
        self.colprops.update({
            'disk_region': col_disk_id(
                     title='Disk Region',
                     table='b_disk_app',
                     field='disk_region',
                     img='hd16',
                     display=False,
                    ),
            'disk_id': col_disk_id(
                     title='Disk Id',
                     table='b_disk_app',
                     field='disk_id',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_name': col_disk_id(
                     title='Disk Name',
                     table='b_disk_app',
                     field='disk_name',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_svcname': col_svc(
                     title='Service',
                     table='b_disk_app',
                     field='disk_svcname',
                     img='svc',
                     display=True,
                    ),
            'disk_nodename': col_node(
                     title='Nodename',
                     table='b_disk_app',
                     field='disk_nodename',
                     img='hw16',
                     display=True,
                    ),
            'disk_used': col_size_mb(
                     title='Disk Used',
                     table='b_disk_app',
                     field='disk_used',
                     img='hd16',
                     display=True,
                    ),
            'disk_size': col_size_mb(
                     title='Disk Size',
                     table='b_disk_app',
                     field='disk_size',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_alloc': col_size_mb(
                     title='Disk Allocation',
                     table='b_disk_app',
                     field='disk_alloc',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_vendor': HtmlTableColumn(
                     title='Disk Vendor',
                     table='b_disk_app',
                     field='disk_vendor',
                     img='hd16',
                     display=True,
                    ),
            'disk_model': HtmlTableColumn(
                     title='Disk Model',
                     table='b_disk_app',
                     field='disk_model',
                     img='hd16',
                     display=True,
                    ),
            'disk_dg': HtmlTableColumn(
                     title='System disk group',
                     table='b_disk_app',
                     field='disk_dg',
                     img='hd16',
                     display=True,
                    ),
            'disk_group': col_array_dg(
                     title='Array disk group',
                     table='b_disk_app',
                     field='disk_group',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_level': HtmlTableColumn(
                     title='Level',
                     table='b_disk_app',
                     field='disk_level',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_raid': HtmlTableColumn(
                     title='Raid',
                     table='b_disk_app',
                     field='disk_raid',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'svcdisk_updated': HtmlTableColumn(
                     title='System Updated',
                     table='b_disk_app',
                     field='svcdisk_updated',
                     img='time16',
                     display=True,
                    ),
            'disk_updated': HtmlTableColumn(
                     title='Storage Updated',
                     table='b_disk_app',
                     field='disk_updated',
                     img='time16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'svcdisk_id': col_array(
                     title='System Disk Id',
                     table='b_disk_app',
                     field='svcdisk_id',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_arrayid': col_array(
                     title='Array Id',
                     table='b_disk_app',
                     field='disk_arrayid',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'disk_devid': col_disk_id(
                     title='Array device Id',
                     table='b_disk_app',
                     field='disk_devid',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     table='stor_array',
                     field='array_model',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'app': HtmlTableColumn(
                     title='App',
                     table='b_disk_app',
                     field='app',
                     img='svc',
                     display=True,
                    ),
        })
        import copy
        nodes_colprops = copy.copy(v_nodes_colprops)
        for i in nodes_colprops:
            nodes_colprops[i].table = 'nodes'
        self.colprops.update(nodes_colprops)
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkbox_id_col = 'svcdisks_id'
        self.checkbox_id_table = 'b_disk_app'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_disks_col_values'
        self.span = 'disk_id'
        self.sub_span = ['disk_size', 'disk_alloc', 'disk_arrayid', 'disk_array_updated',
                         'disk_devid', 'disk_name', 'disk_raid', 'disk_group', 'array_model']

        if 'StorageManager' in user_groups() or \
           'StorageExec' in user_groups():
            self.additional_tools.append('provision')
        self.additional_tools.append('quota')

    def quota(self):
        d = DIV(
              A(
                T("Quota"),
                _class='lock',
                _href=URL(r=request, f='quota'),
              ),
              _class='floatw',
            )
        return d


    def provision(self):
        d = DIV(
              A(
                T("Provision"),
                _class='prov',
                _onclick="""$('#prov_container').toggle();ajax('%(url)s', [], '%(id)s')"""%dict(
                  url=URL(r=request, c='disks', f='ajax_provision'),
                  id="prov_container",
                ),
              ),
              DIV(
                _style='display:none',
                _class='white_float',
                _id="prov_container",
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def ajax_provision():
    l = []
    l.append(TR(
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id="radio_service",
              _onclick="""$("#radio_node").prop('checked',false);$("#stage2").html("");$("#stage3").html("");$("#stage4").html("");ajax('%(url)s', [], '%(id)s')"""%dict(
                id="stage1",
                url=URL(r=request, c='disks', f='ajax_service_list'),
              ),
            ),
          ),
          TD(
            T("Allocate to service"),
          ),
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id="radio_node",
              _onclick="""$("#radio_service").prop('checked',false);$("#stage2").html("");$("#stage3").html("");$("#stage4").html("");ajax('%(url)s', [], '%(id)s')"""%dict(
                id="stage1",
                url=URL(r=request, c='disks', f='ajax_node_list'),
              ),
            ),
          ),
          TD(
            T("Allocate to node"),
          ),
        ))
    d = DIV(
          TABLE(l),
          DIV(
            _id="stage1",
          ),
          DIV(
            _id="stage2",
          ),
          DIV(
            _id="stage3",
          ),
          DIV(
            _id="stage4",
          ),
        )
    return d

@auth.requires_login()
def ajax_node_list():
    o = db.nodes.project | db.nodes.nodename
    q = db.node_hba.nodename == db.nodes.nodename
    if 'StorageManager' not in user_groups():
        q &= db.apps_responsibles.app_id == db.apps.id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == auth.user_id
        q &= db.auth_membership.group_id == db.auth_group.id
        q &= db.nodes.team_responsible == db.auth_group.role
    nodes = db(q).select(db.nodes.nodename,
                         db.nodes.project,
                         groupby=o,
                         orderby=o)

    l = [OPTION(T("Choose one"))]
    for n in nodes:
        o = OPTION(
                "%s - %s"%(str(n.project).upper(), str(n.nodename).lower()),
                _value=n.nodename
            )
        l.append(o)

    return DIV(
             H3(T("Node")),
             SELECT(
                l,
                _onchange="""$("#stage2").html('%(spinner)s');$("#stage3").html("");$("#stage4").html("");ajax('%(url)s/'+this.options[this.selectedIndex].value, [], '%(div)s');"""%dict(
                              url=URL(
                                   r=request, c='disks',
                                   f='ajax_dg_list_by_node',
                                  ),
                              div="stage2",
                              spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
                             ),
             ),
           )

@auth.requires_login()
def ajax_service_list():
    o = db.services.svc_app | db.services.svc_name
    q = db.services.svc_app == db.apps.app
    q &= db.services.svc_name == db.svcmon.mon_svcname
    q &= db.svcmon.mon_nodname == db.node_hba.nodename
    if 'StorageManager' not in user_groups():
        q &= db.apps_responsibles.app_id == db.apps.id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == auth.user_id
    services = db(q).select(db.services.svc_name,
                            db.services.svc_app,
                            groupby=o,
                            orderby=o)

    l = [OPTION(T("Choose one"))]
    for s in services:
        o = OPTION(
                "%s - %s"%(str(s.svc_app).upper(), str(s.svc_name).lower()),
                _value=s.svc_name
            )
        l.append(o)

    return DIV(
             H3(T("Service")),
             SELECT(
                l,
                _onchange="""$("#stage2").html('%(spinner)s');$("#stage3").html("");$("#stage4").html("");ajax('%(url)s/'+this.options[this.selectedIndex].value, [], '%(div)s');"""%dict(
                              url=URL(
                                   r=request, c='disks',
                                   f='ajax_dg_list_by_svc',
                                  ),
                              div="stage2",
                              spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
                             ),
             ),
           )

@auth.requires_login()
def ajax_dg_list_by_node():
    o = db.stor_array.array_name | db.stor_array_dg.dg_name
    q = db.nodes.nodename == request.args[0]
    q &= db.nodes.project == db.apps.app
    q &= db.apps.id == db.v_disk_quota.app_id
    q &= db.v_disk_quota.dg_id == db.stor_array_dg.id
    q &= db.stor_array_dg.array_id == db.stor_array.id
    #q &= db.stor_array_dg_quota.quota != None
    q &= db.node_hba.nodename == request.args[0]
    q &= db.node_hba.hba_id == db.stor_zone.hba_id
    q &= db.stor_zone.tgt_id == db.stor_array_tgtid.array_tgtid
    q &= db.stor_array_tgtid.array_id == db.stor_array_dg.array_id
    rows = db(q).select(groupby=db.stor_array_dg.id)
    return dg_list(rows, 'ajax_path_list_by_node')

def get_free_quota(dg_id, obj):
    sql = """
      select
        (quota-quota_used)/1024
      from
        v_disk_quota
      where
        dg_id=%(dg_id)s and
        app in (
          select
            project
          from
            nodes
          where
            nodename="%(obj)s"
          union all
          select
            svc_app
          from
            services
          where
            svc_name="%(obj)s"
        )
    """%dict(
      dg_id=dg_id,
      obj=obj,
    )
    rows = db.executesql(sql)
    if len(rows) == 0:
        return 0
    return rows[0][0]

def dg_list(rows, fn):
    l = [OPTION(T("Choose one"))]
    for s in rows:
        if s.v_disk_quota.quota is None:
            quota = 0
            quota_free = 0
        else:
            quota = s.v_disk_quota.quota//1024
            quota_free = quota - s.v_disk_quota.quota_used//1024
        o = OPTION(
                T("%(model)s %(name)s - %(dg)s - available quota %(free)d/%(quota)d GB",dict(
                  model=s.stor_array.array_model,
                  name=s.stor_array.array_name,
                  dg=s.stor_array_dg.dg_name,
                  free=quota_free,
                  quota=quota)),
                _value=s.stor_array_dg.id,
            )
        l.append(o)

    return DIV(
             H3(T("Disk Group")),
             SELECT(
                l,
                _onchange="""$("#stage4").html("");ajax('%(url)s/%(svcname)s/'+this.options[this.selectedIndex].value, [], '%(div)s');
"""%dict(
                              svcname=request.args[0],
                              url=URL(
                                   r=request, c='disks',
                                   f=fn,
                                  ),
                              div="stage3"
                             ),
             ),
           )

@auth.requires_login()
def ajax_dg_list_by_svc():
    o = db.stor_array.array_name | db.stor_array_dg.dg_name
    q = db.services.svc_name == request.args[0]
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.v_disk_quota.app_id
    q &= db.v_disk_quota.dg_id == db.stor_array_dg.id
    q &= db.stor_array_dg.array_id == db.stor_array.id
    #q &= db.stor_array_dg_quota.quota != None
    q &= db.svcmon.mon_svcname == request.args[0]
    q &= db.svcmon.mon_nodname == db.node_hba.nodename
    q &= db.node_hba.hba_id == db.stor_zone.hba_id
    q &= db.stor_zone.tgt_id == db.stor_array_tgtid.array_tgtid
    q &= db.stor_array_tgtid.array_id == db.stor_array_dg.array_id
    rows = db(q).select(groupby=db.stor_array_dg.id)
    return dg_list(rows, 'ajax_path_list_by_svc')

@auth.requires_login()
def ajax_path_list_by_node():
    nodename = request.args[0]
    dg_id = request.args[1]

    try:
        int(dg_id)
    except:
        return ""

    o = db.stor_array_tgtid.array_tgtid | db.nodes.host_mode | db.nodes.nodename

    # select nodes who see tgt ids
    q = db.stor_array_dg.id == dg_id
    q &= db.stor_array_tgtid.array_id == db.stor_array_dg.array_id
    q &= db.stor_array_tgtid.array_tgtid == db.stor_zone.tgt_id
    q &= db.stor_zone.hba_id == db.node_hba.hba_id
    q &= db.node_hba.nodename == db.nodes.nodename
    q &= db.nodes.nodename == nodename
    paths = db(q).select()
    return path_list(paths, dg_id, nodename)

def ajax_path_list_by_svc():
    svcname = request.args[0]
    dg_id = request.args[1]

    try:
        int(dg_id)
    except:
        return ""

    o = db.stor_array_tgtid.array_tgtid | db.nodes.host_mode | db.nodes.nodename

    # select nodes who see tgt ids
    q = db.stor_array_dg.id == dg_id
    q &= db.stor_array_tgtid.array_id == db.stor_array_dg.array_id
    q &= db.stor_array_tgtid.array_tgtid == db.stor_zone.tgt_id
    q &= db.stor_zone.hba_id == db.node_hba.hba_id
    q &= db.node_hba.nodename == db.svcmon.mon_nodname
    q &= db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    paths = db(q).select()
    return path_list(paths, dg_id, svcname)

def path_list(paths, dg_id, obj):
    if len(paths) == 0:
        return DIV(
                 H3(T("Presentation")),
                 T("no candidate path"),
               )

    h = {}
    l = [TR(
          INPUT(
            _type="checkbox",
            _onclick="""check_all("ck_path", this.checked)"""
          ),
          TH("target"),
          TH("hba"),
          TH("nodename"),
          TH("env"),
        )]
    for path in paths:
        o = TR(
            INPUT(
              _type="checkbox",
              _name="ck_path",
              _id="-".join((path.node_hba.hba_id, path.stor_array_tgtid.array_tgtid)),
            ),
            TD(path.stor_array_tgtid.array_tgtid.lower()),
            TD(path.node_hba.hba_id.lower()),
            TD(path.nodes.nodename.lower()),
            TD(path.nodes.host_mode.upper()),
        )
        l.append(o)

    q = db.stor_array_dg.id == dg_id
    q &= db.stor_array.id == db.stor_array_dg.array_id
    infos = db(q).select()
    info = infos.first()

    extra_html = ""
    extra_id = []

    if info.stor_array.array_model == 'SANsymphony-V':
        extra_id, extra_html = sansymphony_v()

    return DIV(
             extra_html,
             H3(T("Presentation")),
             TABLE(l),
             INPUT(
               _id="target",
               _type="hidden",
               _value=obj,
             ),
             INPUT(
               _id="paths",
               _type="hidden",
             ),
             H3(T("Size")),
             INPUT(
               _type="text",
               _id="lusize",
               _onKeyUp="""
if(is_enter(event)){
  $("#lusize").attr('disabled', 'disabled')
  $("#lusize").blur()
  $("#stage4").html('<hr>%(spinner)s<hr>')
  l = new Array()
  $("[name=ck_path]").each(function(){
    if (this.checked) {
      l.push(this.id)
    }
  })
  s = l.join(",")
  $("#paths").val(s)
  sync_ajax('%(url)s', %(ids)s, '%(div)s', function(){
    dst=$("#%(div)s").find("[name=res]").attr('id')
    sync_ajax('%(waiturl)s/'+dst, [], dst, function(){
      $("#lusize").removeAttr('disabled')
    })
  })
}"""%dict(
                              spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
                              obj=obj,
                              dg_id=dg_id,
                              ids=["lusize", "paths", "target"]+extra_id,
                              url=URL(
                                   r=request, c='disks',
                                   f='ajax_disk_provision',
                                   args=[dg_id]
                                  ),
                              waiturl=URL(
                                   r=request, c='disks',
                                   f='ajax_disk_provision_wait',
                                  ),
                              div="stage4"
                             ),
             ),
             T("GB"),
           )

class ProvError(Exception):
    pass

def sansymphony_v_dg_name(array_name, dg_name, mirror):
    import config
    array_name = array_name.lower()
    dg_name = dg_name.lower()
    if mirror == "0":
        h = 'sansymphony_v_pool'
    else:
        h = 'sansymphony_v_mirrored_pool'

    if not hasattr(config, h):
        raise ProvError("'%s' is not set in collector configuration"%h)
    _h = getattr(config, h)
    if array_name not in _h:
        raise ProvError("'%s' is not set in pool configuration '%s'"%(array_name, h))
    _h = _h[array_name]
    if dg_name not in _h:
        raise ProvError("'%s' is not set in '%s' pool configuration '%s'"%(dg_name, array_name, h))
    return _h[dg_name]

def sansymphony_v():
    d = DIV(
      H3(T("Mirroring")),
      SELECT(
        OPTION(T("no"), _value="0"),
        OPTION(T("yes"), _value="1"),
        _id="mirror",
      ),
    )
    return ["mirror"], d

@auth.requires_login()
def ajax_disk_provision():
    dg_id = request.args[0]
    paths = request.vars.paths
    target = request.vars.target
    lusize = request.vars.lusize

    try:
        lusize = int(lusize)
    except:
        return SPAN(HR(), T("Invalid size"), HR())

    quota_free = get_free_quota(dg_id, target)
    if quota_free < lusize:
        return  SPAN(HR(), T("Insufficent quota in this disk group"), HR())

    q = db.stor_array_dg.id == dg_id
    q &= db.stor_array.id == db.stor_array_dg.array_id
    q &= db.stor_array.id == db.stor_array_proxy.array_id
    infos = db(q).select()

    if len(infos) == 0:
        return SPAN(HR(), T("No proxy server to provision on this array"), HR())

    provtype = {
      'HSV340': 'eva',
      'HSV400': 'eva',
      'Symmetrix': 'sym',
      'SANsymphony-V': 'dcs',
    }

    info = infos.first()
    if info.stor_array.array_model not in provtype:
        return SPAN(
                 HR(),
                 T("%s array model is not supported by the provisioning agent"%info.stor_array.array_model),
                 HR(),
               )
    t = provtype[info.stor_array.array_model]

    d = {
      'rtype': 'disk',
      'type': t,
      'array_model': info.stor_array.array_model,
      'array_name': info.stor_array.array_name,
      'dg_name': info.stor_array_dg.dg_name,
      'size': lusize,
      'paths': paths,
      'disk_name': target,
    }

    if info.stor_array.array_model == 'SANsymphony-V' and 'mirror' in request.vars:
        try:
            d['dg_name'] = sansymphony_v_dg_name(info.stor_array.array_name,
                                                 d['dg_name'],
                                                 request.vars.mirror)
        except ProvError, e:
            return SPAN(HR(), str(e), HR())

    import json
    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'PasswordAuthentication=no',
                  '-tt',
           'opensvc@'+info.stor_array_proxy.nodename,
           '--',
           """ sudo /opt/opensvc/bin/nodemgr provision --resource '%(d)s' """%dict(d=json.dumps(d))
          ]

    s = "create a %(size)s GB volume in disk group %(dg_name)s of %(array_model)s array %(array_name)s and present it to %(target)s through paths %(paths)s"%dict(
           target=target,
           dg_name=d['dg_name'],
           array_name=info.stor_array.array_name,
           array_model=info.stor_array.array_model,
           size=lusize,
           paths=paths,
        )
    _log('storage.add',
         '%(s)s',
         dict(s=s))
    purge_action_queue()
    action_id = db.action_queue.insert(command=' '.join(cmd))
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()

    # update tables in interim of the array refresh
    import uuid
    disk_id = str(uuid.uuid4()).replace('-','')
    for dg in d['dg_name'].split(','):
        dg = dg.split(':')[-1]
        db.diskinfo.insert(
          disk_id=disk_id,
          disk_size=lusize*1024,
          disk_group=dg,
          disk_arrayid=info.stor_array.array_name,
          disk_updated=datetime.datetime.now()
        )

    q = db.services.svc_name == target
    svc = db(q).select().first()
    if svc is not None:
        svcname = svc.svc_name
    else:
        svcname = ""

    ports = []
    for path in paths.split(','):
        port = path.split('-iqn')[0]
        ports.append(port)
    q = db.node_hba.hba_id.belongs(ports)
    q &= db.nodes.nodename == db.node_hba.nodename
    rows = db(q).select(groupby=db.node_hba.nodename)
    for row in rows:
        db.svcdisks.insert(
          disk_id=disk_id,
          disk_nodename=row.nodes.nodename,
          disk_svcname=svcname,
          disk_size=lusize*1024,
          disk_used=lusize*1024,
          disk_local='F',
          disk_region='0',
          disk_updated=datetime.datetime.now()
        )

    #return SPAN(HR(), s, HR(), ' '.join(cmd))
    return DIV(
             HR(),
             DIV(
              IMG(_src=URL(r=request,c='static',f='spinner.gif')),
              _id=action_id,
              _name="res",
              _style="width:5%;display:table-cell",
             ),
             DIV(
               s,
              _style="width:95%;display:table-cell",
             ),
             HR()
           )

def ajax_disk_provision_wait():
    refresh_b_disk_app()
    id = request.args[0]
    import time
    q = db.action_queue.id == id
    for i in range(300):
        action = db(q).select().first()
        if action is None:
            return T("Action is not queued")
        if action.status != 'T':
            time.sleep(1)
            continue
        break
    if action.ret == 0:
        img = 'check16.png'
    else:
        img = 'nok.png'
    title = ', '.join((str(action.stdout), str(action.stderr)))
    return IMG(_src=URL(r=request,c='static',f=img), _title=title)

@auth.requires_login()
def ajax_disks_col_values():
    t = table_disks('disks', 'ajax_disks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.b_disk_app.id>0
    q |= db.stor_array.id<0
    l1 = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.b_disk_app.disk_arrayid==db.nodes.nodename)
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o, left=(l1,l2))
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_disks():
    t = table_disks('disks', 'ajax_disks')
    o = db.b_disk_app.disk_id | db.b_disk_app.disk_svcname | db.b_disk_app.disk_nodename
    q = db.b_disk_app.id>0
    q |= db.stor_array.id<0
    l1 = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.b_disk_app.disk_arrayid==db.nodes.nodename)
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)
    n = db(q).select(db.b_disk_app.id.count(), left=(l1,l2)).first()._extra[db.b_disk_app.id.count()]
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=(l1,l2))

    t.csv_q = q
    t.csv_orderby = o
    t.csv_left = (l1,l2)
    t.csv_limit = 60000

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    nt = table_disk_charts('charts', 'ajax_disk_charts')

    return DIV(
             SCRIPT(
               #'if ($("#charts").is(":visible")) {',
               nt.ajax_submit(additional_inputs=t.ajax_inputs()),
               #"}",
               _name="disks_to_eval",
             ),
             DIV(
               T("Statistics"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#charts").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#charts").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#charts").hide();
               }"""%nt.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
               _id="charts",
             ),
             t.html(),
           )

@auth.requires_login()
def disks():
    t = DIV(
          ajax_disks(),
          _id='disks',
        )
    return dict(table=t)


@auth.requires_login()
def ajax_disk_charts():
    t = table_disks('disks', 'ajax_disks')
    nt = table_disk_charts('charts', 'ajax_disk_charts')

    o = db.b_disk_app.disk_id
    q = db.b_disk_app.id>0
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    nt.setup_pager(-1)
    nt.dbfilterable = False
    nt.filterable = True
    nt.additional_inputs = t.ajax_inputs()

    h_data_svc = ""
    h_data_app = ""
    h_data_dg = ""
    h_data_array = ""

    sql = """  select
                 count(distinct(b_disk_app.app)),
                 max(b_disk_app.disk_level)
               from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
           """%dict(q=q)
    n_app = db.executesql(sql)[0][0]
    max_level = db.executesql(sql)[0][1]

    if max_level is None:
        return ''
    levels = range(0, max_level+1)

    def pie_data_svc(q, level=0):
        sql = """select
                   t.obj,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL and t.disk_alloc>0, t.disk_alloc, t.disk_size)) alloc
                 from
                   (
                   select
                     u.obj,
                     max(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.disk_svcname as obj,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and b_disk_app.disk_svcname != ""
                     union all
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.disk_nodename as obj,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and (b_disk_app.disk_svcname = "" or b_disk_app.disk_svcname is NULL)
                   ) u
                   group by u.disk_id, u.disk_region
                 ) t
                 group by t.obj
                 order by t.obj, size desc
                 """%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    def data_total(data):
        total = 0
        backend_total = 0
        for l in data:
            total += l[1]
            backend_total += l[2]
        return int(total), int(backend_total)

    if n_app == 1:
        data_svc = []
        for level in levels:
            _data_svc = []
            rows = pie_data_svc(q, level)
            for row in rows:
                if row[0] is None:
                    label = 'unknown'
                else:
                    label = row[0]
                try:
                    size = int(row[1])
                except:
                    continue
                _data_svc += [[str(label) +' (%s)'%beautify_size_mb(size), size]]

            _data_svc.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_svc) == 0:
                _data_svc = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_svc += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_svc.append(_data_svc)
        h_data_svc = {
          'total': total,
          'backend_total': backend_total,
          'data': data_svc,
        }

    def pie_data_app(q, level=0):
        sql = """select
                   t.app,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL and t.disk_alloc>0, t.disk_alloc, t.disk_size)) alloc
                 from (
                   select
                     u.app,
                     max(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.app as app,
                       b_disk_app.disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and b_disk_app.disk_svcname != ""
                     union all
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.app as app,
                       b_disk_app.disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and (b_disk_app.disk_svcname = "" or b_disk_app.disk_svcname is NULL)
                   ) u
                   group by u.disk_id, u.disk_region
                 ) t
                 group by t.app
                 order by t.app, size desc
                 """%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    if n_app > 1:
        data_app = []
        for level in levels:
            rows = pie_data_app(q, level)
            _data_app = []
            for row in rows:
                if row[0] is None:
                    label = 'unknown'
                else:
                    label = row[0]
                try:
                    size = int(row[1])
                except:
                    continue
                _data_app += [[str(label) +' (%s)'%beautify_size_mb(size), size]]

            _data_app.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_app) == 0:
                _data_app = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_app += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_app.append(_data_app)
        h_data_app = {
          'total': total,
          'backend_total': backend_total,
          'data': data_app,
        }


    sql = """select count(distinct b_disk_app.disk_arrayid)
             from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
          """%dict(q=q)
    n_arrays = db.executesql(sql)[0][0]

    sql = """select count(distinct b_disk_app.disk_group)
             from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
          """%dict(q=q)
    n_dg = db.executesql(sql)[0][0]

    if n_arrays == 1 and n_dg > 1:
        sql = """select
                   t.disk_arrayid,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL and t.disk_alloc>0, t.disk_alloc, t.disk_size)) alloc,
                   t.disk_group
                 from (
                   select
                     sum(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc,
                     u.disk_arrayid,
                     u.disk_group
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       max(b_disk_app.disk_used) as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc,
                       b_disk_app.disk_arrayid,
                       b_disk_app.disk_group
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     group by b_disk_app.disk_id, b_disk_app.disk_region
                   ) u
                   group by u.disk_id
                 ) t
                 group by t.disk_arrayid, t.disk_group
                 order by size desc, t.disk_arrayid, t.disk_group"""%dict(q=q)
        rows = db.executesql(sql)

        data_dg = []
        for row in rows:
            if row[3] is None:
                dg = ''
            else:
                dg = ' '.join((row[0],row[3]))

            label = dg
            try:
                size = int(row[1])
            except:
                continue
            data_dg += [[str(label) +' (%s)'%beautify_size_mb(size), size]]
        total, backend_total = data_total(rows)
        data_dg.sort(lambda x, y: cmp(y[1], x[1]))
        data_dg = [data_dg]
        h_data_dg = {
          'total': total,
          'backend_total': backend_total,
          'data': data_dg,
        }


    def pie_data_array(q, level=0):
        sql = """select
                   t.disk_arrayid,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL and t.disk_alloc>0, t.disk_alloc, t.disk_size)) alloc
                 from (
                   select
                     sum(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc,
                     u.disk_arrayid
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       max(b_disk_app.disk_used) as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc,
                       b_disk_app.disk_arrayid
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     group by b_disk_app.disk_id, b_disk_app.disk_region
                   ) u
                   group by u.disk_id
                 ) t
                 group by t.disk_arrayid
                 order by size desc, t.disk_arrayid"""%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    if n_arrays > 1:
        data_array = []
        for level in levels:
            rows = pie_data_array(q, level)
            _data_array = []
            for row in rows:
                if row[0] is None:
                    array = ''
                else:
                    array = row[0]
                label = array
                try:
                    size = int(row[1])
                except:
                    continue
                _data_array += [[str(label) +' (%s)'%beautify_size_mb(size), size]]
            _data_array.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_array) == 0:
                _data_array = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_array += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_array.append(_data_array)
        h_data_array = {
          'total': total,
          'backend_total': backend_total,
          'data': data_array,
        }


    nt.object_list = [{'chart_svc': json.dumps(h_data_svc),
                       'chart_ap': json.dumps(h_data_app),
                       'chart_dg': json.dumps(h_data_dg),
                       'chart_ar': json.dumps(h_data_array)}]

    return DIV(
             nt.html(),
             SCRIPT(
"""
function diskdonut(o) {
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var backend_total = fancy_size_mb(d['backend_total'])
  var title = total + ' (' + backend_total + ')'
  o.html("")
  $.jqplot(o.attr('id'), d['data'],
    {
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          showDataLabels: true
        }
      },
      title: { text: title }
    }
  );
  $('#'+o.attr('id')).bind('jqplotDataHighlight', 
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('level: '+seriesIndex+', data: '+data[0]);
        }
  );
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight', 
        function (ev) {
            $('#chart_info').html('%(msg)s');
        }
  );
  } catch(e) {}
}
$("[id^=chart_svc]").each(function(){
  diskdonut($(this))
})
$("[id^=chart_ap]").each(function(){
  diskdonut($(this))
  $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
    d = data[seriesIndex]
    i = d.lastIndexOf(" (")
    d = d.substring(0, i)
    $("#disks_f_app").val(d)
    %(submit)s
  })
})
$("[id^=chart_dg]").each(function(){
  diskdonut($(this))
})
$("[id^=chart_ar]").each(function(){
  diskdonut($(this))
  $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
    d = data[seriesIndex]
    var reg = new RegExp(" \(.*\)", "g");
    d = d.replace(reg, "")
    $("#disks_f_disk_arrayid").val(d)
    %(submit)s
  })
})
"""%dict(
      submit=t.ajax_submit(),
      msg=T("Hover over a slice to show data"),
    ),
               _name="charts_to_eval",
             ),
           )

class table_disk_charts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops.update({
            'chart': col_chart(
                     title='Chart',
                     field='chart',
                     img='spark16',
                     display=True,
                    ),
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.exportable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False

@auth.requires_login()
def ajax_array_dg():
    array_name = request.vars.array
    dg_name = request.vars.dg
    row_id = request.vars.rowid
    id = 'chart_'+array_name.replace(" ", "").replace("-", "")+'_'+dg_name.replace(" ", "")
    d = DIV(
          H3(T("Array disk group usage history")),
          DIV(
            _id=id,
          ),
          SCRIPT(
           "stats_disk_array('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_array_dg',
                          vars={'array_name': array_name,
                                'dg_name': dg_name},
                      )
                ),
            _name='%s_to_eval'%row_id,
          ),
          _style="float:left;width:500px",
        )
    return d

@auth.requires_login()
def ajax_array():
    array_name = request.vars.array
    row_id = request.vars.rowid
    id = 'chart_'+array_name.replace(" ", "").replace("-", "")
    d = DIV(
          H3(T("Array usage history")),
          DIV(
            _id=id,
          ),
          SCRIPT(
           "stats_disk_array('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_array',
                          vars={'array_name': array_name},
                      )
                ),
            _name='%s_to_eval'%row_id,
          ),
          _style="float:left;width:500px",
        )
    return d

@auth.requires_login()
def ajax_app():
    app_id = request.vars.app_id
    dg_id = request.vars.dg_id
    row_id = request.vars.rowid
    id = row_id + '_chart'
    d = DIV(
        DIV(
          H3(T("Application usage history")),
          DIV(
            _id=id+'_dg',
          ),
          _style="float:left;width:500px",
        ),
        DIV(
          H3(T("Application usage history (all disk groups)")),
          DIV(
            _id=id,
          ),
          _style="float:left;width:500px",
        ),
        SCRIPT(
           "stats_disk_app('%(url)s', '%(id)s');"%dict(
                  id=id+'_dg',
                  url=URL(r=request,
                          f='call/json/json_disk_app_dg',
                          args=[app_id, dg_id]
                      )
                ),
           "stats_disk_app('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_app',
                          args=[app_id]
                      )
                ),
            _name='%s_to_eval'%row_id,
        ),
        )
    return d

@service.json
def json_disk_array_dg():
    array_name = request.vars.array_name
    dg_name = request.vars.dg_name
    q = db.stat_day_disk_array_dg.array_name == array_name
    q &= db.stat_day_disk_array_dg.array_dg == dg_name
    q &= db.stat_day_disk_array_dg.disk_size != None
    q &= db.stat_day_disk_array_dg.disk_size != 0
    rows = db(q).select()
    disk_used = []
    disk_free = []
    disk_reserved = []
    disk_reservable = []
    if len(rows) < 2:
        return [disk_used, disk_free, disk_reserved, disk_reservable]
    for r in rows:
        disk_used.append([r.day, r.disk_used])
        disk_free.append([r.day, r.disk_size-r.disk_used])
        disk_reserved.append([r.day, r.reserved])
        disk_reservable.append([r.day, r.reservable])
    return [disk_used, disk_free, disk_reserved, disk_reservable]

@service.json
def json_disk_array():
    array_name = request.vars.array_name
    q = db.stat_day_disk_array.array_name == array_name
    q &= db.stat_day_disk_array.disk_size != None
    q &= db.stat_day_disk_array.disk_size != 0
    rows = db(q).select()
    disk_used = []
    disk_free = []
    disk_reserved = []
    disk_reservable = []
    if len(rows) < 2:
        return [disk_used, disk_free, disk_reserved, disk_reservable]
    for r in rows:
        disk_used.append([r.day, r.disk_used])
        disk_free.append([r.day, r.disk_size-r.disk_used])
        disk_reserved.append([r.day, r.reserved])
        disk_reservable.append([r.day, r.reservable])
    return [disk_used, disk_free, disk_reserved, disk_reservable]

@service.json
def json_disk_app(app_id):
    q = db.apps.id == int(app_id)
    q &= db.stat_day_disk_app.app == db.apps.app
    rows = db(q).select()
    disk_used = []
    disk_quota = []
    if len(rows) < 2:
        return [disk_used, disk_quota]
    for r in rows:
        disk_used.append([r.stat_day_disk_app.day, r.stat_day_disk_app.disk_used])
        disk_quota.append([r.stat_day_disk_app.day, r.stat_day_disk_app.quota])
    return [disk_used, disk_quota]

@service.json
def json_disk_app_dg(app_id, dg_id):
    q = db.apps.id == int(app_id)
    q &= db.stat_day_disk_app_dg.app == db.apps.app
    q &= db.stat_day_disk_app_dg.dg_id == int(dg_id)
    rows = db(q).select()
    disk_used = []
    disk_quota = []
    if len(rows) < 2:
        return [disk_used, disk_quota]
    for r in rows:
        disk_used.append([r.stat_day_disk_app_dg.day, r.stat_day_disk_app_dg.disk_used])
        if r.stat_day_disk_app_dg.quota is None:
            quota = 0
        else:
            quota = r.stat_day_disk_app_dg.quota
        disk_quota.append([r.stat_day_disk_app_dg.day, quota])
    return [disk_used, disk_quota]
