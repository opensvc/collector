class col_arrays_chart(HtmlTableColumn):
    def html(self, o):
       return DIV(
                H2(o['array_name']),
                DIV(
                  H3(T("Disk Array Usage")),
                  DIV(
                    o['chart_ar'],
                    _id='arrays_chart_ar_%s'%o['array_name'].replace(" ", "_"),
                  ),
                  _style="float:left;width:500px",
                ),
              )

class col_app_chart(HtmlTableColumn):
    def html(self, o):
       return DIV(
                H2(o['svc_app']),
                DIV(
                  H3(T("Disk Group Usage")),
                  DIV(
                    o['chart_dg'],
                    _id='app_chart_dg_%s'%o['svc_app'],
                  ),
                  _style="float:left;width:500px",
                ),
                DIV(
                  H3(T("Disk Array Usage")),
                  DIV(
                    o['chart_ar'],
                    _id='app_chart_ar_%s'%o['svc_app'],
                  ),
                  _style="float:left;width:500px",
                ),
              )

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
       return DIV("%d %s"%(d/1024, unit), _class="numeric")

class col_size_mb(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d is None:
           return ''
       unit = 'MB'
       return DIV("%d %s"%(d, unit), _class="numeric")

class col_quota(HtmlTableColumn):
    def html(self, o):
        if o.apps.app is None:
            return ""
        s = self.get(o)
        if s is None:
            s = "-"
            ss = ""
        else:
            ss = s
            s = "%s GB"%s
        tid = 'd_t_%s'%o.stor_array_dg_quota.id
        iid = 'd_i_%s'%o.stor_array_dg_quota.id
        sid = 'd_s_%s'%o.stor_array_dg_quota.id
        d = SPAN(
              DIV(
                s,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable numeric",
              ),
              SPAN(
                INPUT(
                  value=ss,
                  _id=iid,
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="quota_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        return d

class table_quota(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['array_name',
                     'array_model',
                     'dg_name',
                     'dg_free',
                     'dg_used',
                     'dg_size',
                     'app',
                     'quota']
        self.colprops.update({
            'array_name': HtmlTableColumn(
                     title='Array',
                     table='stor_array',
                     field='array_name',
                     img='hd16',
                     display=True,
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     table='stor_array',
                     field='array_model',
                     img='hd16',
                     display=True,
                    ),
            'array_id': HtmlTableColumn(
                     title='Array Id',
                     table='stor_array',
                     field='id',
                     img='hd16',
                     display=True,
                    ),
            'dg_name': HtmlTableColumn(
                     title='Array Disk Group',
                     table='stor_array_dg',
                     field='dg_name',
                     img='hd16',
                     display=True,
                    ),
            'dg_free': col_size_mb(
                     title='Free',
                     table='stor_array_dg',
                     field='dg_free',
                     img='hd16',
                     display=True,
                    ),
            'dg_used': col_size_mb(
                     title='Used',
                     table='stor_array_dg',
                     field='dg_used',
                     img='hd16',
                     display=True,
                    ),
            'dg_size': col_size_mb(
                     title='Size',
                     table='stor_array_dg',
                     field='dg_size',
                     img='hd16',
                     display=True,
                    ),
            'dg_id': HtmlTableColumn(
                     title='Array Disk Group Id',
                     table='stor_array_dg',
                     field='id',
                     img='hd16',
                     display=True,
                    ),
            'app': HtmlTableColumn(
                     title='App',
                     table='apps',
                     field='app',
                     img='svc',
                     display=True,
                    ),
            'app_id': HtmlTableColumn(
                     title='App Id',
                     table='apps',
                     field='id',
                     img='svc',
                     display=True,
                    ),
            'quota': col_quota(
                     title='Quota',
                     table='stor_array_dg_quota',
                     field='quota',
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
        self.span = 'dg_name'
        self.sub_span = ['dg_free', 'array_model', 'array_name']

        if 'StorageManager' in user_groups() or \
           'StorageManager' in user_groups():
            self.additional_tools.append('app_attach')
            self.additional_tools.append('app_detach')

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

@auth.requires_membership('StorageManager')
def quota_set():
    l = [k for k in request.vars if 'd_i_' in k]
    if len(l) != 1:
        raise ToolError("one quota must be selected")
    qid = int(l[0].replace('d_i_',''))
    new = request.vars[l[0]]
    try:
        new = int(new)
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


@auth.requires_membership('StorageManager')
def app_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no application selected")

    for id in ids:
        dg_id, array_id, app_id = id.split('_')
        q = db.stor_array_dg_quota.dg_id == int(dg_id)
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
    q = db.stor_array_dg.id>0
    q |= db.stor_array_dg_quota.id<0
    q |= db.apps.id<0
    q &= db.stor_array_dg.array_id == db.stor_array.id
    l1 = db.stor_array_dg_quota.on(db.stor_array_dg.id==db.stor_array_dg_quota.dg_id)
    l2 = db.apps.on(db.apps.id==db.stor_array_dg_quota.app_id)
    q = _where(q, 'stor_array', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o, left=[l1,l2])
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

    o = db.stor_array.array_name | db.stor_array_dg.dg_name
    q = db.stor_array_dg.id>0
    q |= db.stor_array_dg_quota.id<0
    q |= db.apps.id<0
    q &= db.stor_array_dg.array_id == db.stor_array.id
    l1 = db.stor_array_dg_quota.on(db.stor_array_dg.id==db.stor_array_dg_quota.dg_id)
    l2 = db.apps.on(db.apps.id==db.stor_array_dg_quota.app_id)
    q = _where(q, 'stor_array', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = len(db(q).select(left=[l1,l2]))
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=[l1,l2])

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
                     'disk_svcname',
                     'disk_nodename',
                     'disk_vendor',
                     'disk_model',
                     'disk_dg',
                     'disk_updated',
                     'disk_array_updated',
                     'disk_used',
                     'disk_size',
                     'disk_group',
                     'disk_raid',
                     'disk_devid',
                     'array_model',
                     'disk_arrayid']
        self.colprops.update({
            'disk_id': col_disk_id(
                     title='Disk Id',
                     table='diskinfo',
                     field='disk_id',
                     img='hd16',
                     display=True,
                    ),
            'disk_svcname': col_svc(
                     title='Service',
                     table='svcdisks',
                     field='disk_svcname',
                     img='svc',
                     display=True,
                    ),
            'disk_nodename': col_node(
                     title='Nodename',
                     table='svcdisks',
                     field='disk_nodename',
                     img='hw16',
                     display=True,
                    ),
            'disk_used': HtmlTableColumn(
                     title='Used (MB)',
                     table='svcdisks',
                     field='disk_used',
                     img='hd16',
                     display=True,
                    ),
            'disk_size': HtmlTableColumn(
                     title='Size (MB)',
                     table='diskinfo',
                     field='disk_size',
                     img='hd16',
                     display=True,
                    ),
            'disk_vendor': HtmlTableColumn(
                     title='Vendor',
                     table='svcdisks',
                     field='disk_vendor',
                     img='hd16',
                     display=True,
                    ),
            'disk_model': HtmlTableColumn(
                     title='Model',
                     table='svcdisks',
                     field='disk_model',
                     img='hd16',
                     display=True,
                    ),
            'disk_dg': HtmlTableColumn(
                     title='System disk group',
                     table='svcdisks',
                     field='disk_dg',
                     img='hd16',
                     display=True,
                    ),
            'disk_group': HtmlTableColumn(
                     title='Array disk group',
                     table='diskinfo',
                     field='disk_group',
                     img='hd16',
                     display=True,
                    ),
            'disk_raid': HtmlTableColumn(
                     title='Raid',
                     table='diskinfo',
                     field='disk_raid',
                     img='hd16',
                     display=True,
                    ),
            'disk_updated': HtmlTableColumn(
                     title='System Updated',
                     table='svcdisks',
                     field='disk_updated',
                     img='time16',
                     display=True,
                    ),
            'disk_array_updated': HtmlTableColumn(
                     title='Storage Updated',
                     table='diskinfo',
                     field='disk_updated',
                     img='time16',
                     display=True,
                    ),
            'disk_arrayid': HtmlTableColumn(
                     title='Array Id',
                     table='diskinfo',
                     field='disk_arrayid',
                     img='hd16',
                     display=True,
                    ),
            'disk_devid': HtmlTableColumn(
                     title='Array device Id',
                     table='diskinfo',
                     field='disk_devid',
                     img='hd16',
                     display=True,
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     table='stor_array',
                     field='array_model',
                     img='hd16',
                     display=True,
                    ),
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'svcdisks'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_disks_col_values'
        self.span = 'disk_id'
        self.sub_span = ['disk_svcname', 'disk_size', 'disk_arrayid',
                         'disk_devid', 'disk_raid', 'disk_group', 'array_model']

        if 'StorageManager' in user_groups() or \
           'StorageExec' in user_groups():
            self.additional_tools.append('provision')
        self.additional_tools.append('quota')

    def quota(self):
        d = DIV(
              A(
                T("Quota"),
                _class='add16',
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
              _onclick="""$("#stage2").html("");$("#stage3").html("");$("#stage4").html("");ajax('%(url)s', [], '%(id)s')"""%dict(
                id="stage1",
                url=URL(r=request, c='disks', f='ajax_service_list'),
              ),
            ),
          ),
          TD(
            T("Allocate to service"),
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
def ajax_service_list():
    o = db.services.svc_app | db.services.svc_name
    q = db.services.svc_app == db.apps.app
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    q &= db.auth_membership.user_id == auth.user_id
    services = db(q).select(db.services.svc_name,
                            db.services.svc_app,
                            orderby=o)

    l = [OPTION(T("Choose one"))]
    for s in services:
        o = OPTION(
                "%s - %s"%(s.svc_app, s.svc_name),
                _value=s.svc_name
            )
        l.append(o)

    return DIV(
             H3(T("Service")),
             SELECT(
                l,
                _onchange="""$("#stage3").html("");$("#stage4").html("");ajax('%(url)s/'+this.options[this.selectedIndex].value, [], '%(div)s');"""%dict(
                              url=URL(
                                   r=request, c='disks',
                                   f='ajax_dg_list',
                                  ),
                              div="stage2"
                             ),
             ),
           )

@auth.requires_login()
def ajax_dg_list():
    o = db.stor_array.array_name | db.stor_array_dg.dg_name
    q = db.services.svc_name == request.args[0]
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.stor_array_dg_quota.app_id
    q &= db.stor_array_dg_quota.dg_id == db.stor_array_dg.id
    q &= db.stor_array_dg.array_id == db.stor_array.id
    q &= db.stor_array_dg_quota.quota != None
    rows = db(q).select()

    l = [OPTION(T("Choose one"))]
    for s in rows:
        o = OPTION(
                "%s %s - %s - quota %s GB"%(s.stor_array.array_model,
                                            s.stor_array.array_name,
                                            s.stor_array_dg.dg_name,
                                            str(s.stor_array_dg_quota.quota)),
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
                                   f='ajax_nodes_list',
                                  ),
                              div="stage3"
                             ),
             ),
           )


@auth.requires_login()
def ajax_nodes_list():
    svcname = request.args[0]
    dg_id = request.args[1]

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
              _id="-".join((path.stor_array_tgtid.array_tgtid, path.node_hba.hba_id)),
            ),
            TD(path.stor_array_tgtid.array_tgtid),
            TD(path.node_hba.hba_id),
            TD(path.nodes.nodename),
            TD(path.nodes.host_mode),
        )
        l.append(o)
    return DIV(
             H3(T("Presentation")),
             TABLE(l),
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
  l = new Array()
  $("[name=ck_path]").each(function(){
    if (this.checked) {
      l.push(this.id)
    }
  })
  s = l.join(",")
  $("#paths").val(s)
  ajax('%(url)s', ["lusize", "paths"], '%(div)s')
}"""%dict(
                              svcname=svcname,
                              dg_id=dg_id,
                              url=URL(
                                   r=request, c='disks',
                                   f='ajax_disk_provision',
                                   args=[svcname, dg_id]
                                  ),
                              div="stage4"
                             ),
             ),
             T("GB"),
           )

@auth.requires_login()
def ajax_disk_provision():
    svcname = request.args[0]
    dg_id = request.args[1]
    paths = request.vars.paths
    lusize = request.vars.lusize

    try:
        lusize = int(lusize)
    except:
        return "invalid size"

    q = db.stor_array_dg.id == dg_id
    q &= db.stor_array.id == db.stor_array_dg.array_id
    q &= db.stor_array.id == db.stor_array_proxy.array_id
    infos = db(q).select()

    if len(infos) == 0:
        return "no proxy server to provision on this array"

    info = infos.first()
    d = {
      'rtype': 'vg',
      'type': 'raw',
      'array_model': info.stor_array.array_model,
      'array_name': info.stor_array.array_name,
      'dg_name': info.stor_array_dg.dg_name,
      'size': lusize,
      'paths': paths,
    }
    import json
    import uuid
    tmp_svcname = str(uuid.uuid4())
    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'PasswordAuthentication=no',
                  '-tt',
           'opensvc@'+info.stor_array_proxy.nodename,
           '--',
           """(sudo /opt/opensvc/bin/svcmgr -s %(svcname)s create --resource "%(d)s" --provision ; sudo /opt/opensvc/bin/svcmgr -s %(svcname)s delete)"""%dict(svcname=tmp_svcname, d=json.dumps(d))
          ]

    s = "create a %(size)s GB volume in disk group %(dg_name)s of %(array_model)s array %(array_name)s and present it through paths %(paths)s"%dict(
           dg_name=info.stor_array_dg.dg_name,
           array_name=info.stor_array.array_name,
           array_model=info.stor_array.array_model,
           size=lusize,
           paths=paths,
        )
    _log('storage.add',
         '%(s)s',
         dict(s=s))

    return SPAN(HR(), s, HR(), ' '.join(cmd))

@auth.requires_login()
def ajax_disks_col_values():
    t = table_disks('disks', 'ajax_disks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.diskinfo.id>0
    q |= db.svcdisks.id<0
    l1 = db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
    l2 = db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id)
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o, left=(l1,l2))
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_disks():
    t = table_disks('disks', 'ajax_disks')
    o = db.svcdisks.disk_id
    q = db.diskinfo.id>0
    q |= db.svcdisks.id<0
    l1 = db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
    l2 = db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id)
    #q &= db.svcdisks.disk_nodename==db.v_nodes.nodename
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = len(db(q).select(left=(l1,l2)))
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=(l1,l2))

    t.csv_q = q
    t.csv_orderby = o

    nt = table_disk_apps('apps', 'ajax_disk_app')
    mt = table_disk_arrays('arrays', 'ajax_disk_arrays')

    return DIV(
             SCRIPT(
               'if ($("#apps").is(":visible")) {',
               nt.ajax_submit(additional_inputs=t.ajax_inputs()),
               "}",
               'if ($("#arrays").is(":visible")) {',
               mt.ajax_submit(additional_inputs=t.ajax_inputs()),
               "}",
             ),
             DIV(
               T("Applications"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#apps").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#apps").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#apps").hide();
               }"""%nt.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
               _id="apps",
               _style="display:none"
             ),
             DIV(
               T("Arrays"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#arrays").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#arrays").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#arrays").hide();
               }"""%mt.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
               _id="arrays",
               _style="display:none"
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
def ajax_disk_app():
    t = table_disks('disks', 'ajax_disks')
    nt = table_disk_apps('apps', 'ajax_disk_app')

    o = db.svcdisks.disk_id
    q = db.diskinfo.id>0
    q |= db.svcdisks.id<0
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    nt.setup_pager(-1)
    nt.dbfilterable = False
    nt.filterable = True
    nt.additional_inputs = t.ajax_inputs()

    sql = """select
               t.svc_app,
               sum(t.disk_size) size,
               t.disk_arrayid,
               t.disk_group
             from (
               select
                 services.svc_app,
                 diskinfo.disk_size,
                 diskinfo.disk_arrayid,
                 diskinfo.disk_group
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join services on svcdisks.disk_svcname=services.svc_name
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               where %(q)s
               group by diskinfo.disk_id
             ) t
             group by t.svc_app, t.disk_group
             order by t.svc_app, size desc, t.disk_arrayid, t.disk_group"""%dict(q=q)
    rows = db.executesql(sql)

    dg = {}
    ar = {}
    s = {}
    for row in rows:
        svc_app = row[0]
        size = int(row[1])
        array_name = row[2]
        array_dg = row[3]

        if array_name is None:
            array_name = ''
        if array_dg is None:
            array_dg = ''

        label = ' '.join((array_name, array_dg))
        t = [label, size]
        if svc_app not in dg:
            dg[svc_app] = [t]
            s[svc_app] = size
        else:
            dg[svc_app] += [t]
            s[svc_app] += size

        if svc_app not in ar:
            ar[svc_app] = {array_name: size}
        elif array_name not in ar[svc_app]:
            ar[svc_app][array_name] = size
        else:
            ar[svc_app][array_name] += size

    nt.object_list = []
    for svc_app, data_dg in dg.items():
        for i, (label, size) in enumerate(data_dg):
            data_dg[i] = (label +' (%d MB)'%size, 100*size//s[svc_app])

        ardata = ar[svc_app]
        data_ar = []
        for array_name, size in ardata.items():
            data_ar.append([array_name + ' (%d MB)'%size, 100*size//s[svc_app]])

        nt.object_list.append({'svc_app': svc_app,
                               'chart': '',
                               'chart_dg': json.dumps(data_dg),
                               'chart_ar': json.dumps(data_ar)})


    return DIV(
             nt.html(),
             SCRIPT(
"""
function diskpie(o) {
  try{
  var data = $.parseJSON(o.html())
  o.html("")
  $.jqplot(o.attr('id'), [data],
    {
      seriesDefaults: {
        renderer: $.jqplot.PieRenderer,
        rendererOptions: {
          sliceMargin: 4,
          showDataLabels: true
        }
      },
      legend: { show:true, location: 'e' }
    }
  );
  } catch(e) {}
}
$("[id^=app_chart_dg]").each(function(){
  diskpie($(this))
})
$("[id^=app_chart_ar]").each(function(){
  diskpie($(this))
})
""",
               _name="apps_to_eval",
             ),
           )


@auth.requires_login()
def ajax_disk_arrays():
    t = table_disks('disks', 'ajax_disks')
    nt = table_disk_arrays('arrays', 'ajax_disk_arrays')

    q = db.diskinfo.id>0
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    nt.setup_pager(-1)
    nt.dbfilterable = False
    nt.filterable = True
    nt.additional_inputs = t.ajax_inputs()

    sql = """select
               t.app,
               sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
               t.disk_arrayid
             from (
               select
                 services.svc_app as app,
                 svcdisks.disk_used,
                 svcdisks.disk_size,
                 diskinfo.disk_arrayid
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join services on svcdisks.disk_svcname=services.svc_name
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               where %(q)s
               and svcdisks.disk_svcname != ""
               group by diskinfo.disk_id
              union
               select
                 nodes.project as app,
                 svcdisks.disk_used,
                 svcdisks.disk_size,
                 diskinfo.disk_arrayid
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join nodes on svcdisks.disk_nodename=nodes.nodename
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               where %(q)s
               and svcdisks.disk_svcname = ""
               group by diskinfo.disk_id
             ) t
             group by t.app
             order by t.app, size desc
             """%dict(q=q)
    rows = db.executesql(sql)

    data_array = []
    for row in rows:
        label = row[0]
        size = int(row[1])
        data_array += [[str(label) +' (%d MB)'%size, size]]

    nt.object_list = [{'array_name': "All arrays in cursor",
                       'chart': '',
                       'chart_dg': json.dumps([]),
                       'chart_ar': json.dumps(data_array)}]

    sql = """select
               t.app,
               sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
               t.disk_arrayid
             from (
               select
                 services.svc_app as app,
                 svcdisks.disk_used,
                 svcdisks.disk_size,
                 diskinfo.disk_arrayid
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join services on svcdisks.disk_svcname=services.svc_name
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               where %(q)s
               and svcdisks.disk_svcname != ""
               group by diskinfo.disk_id
              union
               select
                 nodes.project as app,
                 svcdisks.disk_used,
                 svcdisks.disk_size,
                 diskinfo.disk_arrayid
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join nodes on svcdisks.disk_nodename=nodes.nodename
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               where %(q)s
               and svcdisks.disk_svcname = ""
               group by diskinfo.disk_id
             ) t
             group by t.app, t.disk_arrayid
             order by t.disk_arrayid, t.app, size desc"""%dict(q=q)
    rows = db.executesql(sql)

    ar = {}
    for row in rows:
        if row[0] is None:
            svc_app = "unknown"
        else:
            svc_app = row[0]
        if row[1] is None:
            size = 0
        else:
            size = int(row[1])
        array_name = row[2]

        label = svc_app
        t = [label, size]
        if array_name not in ar:
            ar[array_name] = [t]
        else:
            ar[array_name] += [t]

    for array_name, data_array in ar.items():
        for i, (label, size) in enumerate(data_array):
            data_array[i] = (str(label) +' (%d MB)'%size, size)

        nt.object_list.append({'array_name': array_name,
                               'chart': '',
                               'chart_dg': json.dumps([]),
                               'chart_ar': json.dumps(data_array)})

    return DIV(
             nt.html(),
             SCRIPT(
"""
function diskpie(o) {
  try {
  var data = $.parseJSON(o.html())
  o.html("")
  $.jqplot(o.attr('id'), [data],
    {
      seriesDefaults: {
        renderer: $.jqplot.PieRenderer,
        rendererOptions: {
          sliceMargin: 4,
          showDataLabels: true
        }
      },
      legend: { show:true, location: 'e' }
    }
  );
  } catch(e) {}
}
$("[id^=arrays_chart_dg]").each(function(){
  diskpie($(this))
})
$("[id^=arrays_chart_ar]").each(function(){
  diskpie($(this))
})
""",
               _name="arrays_to_eval",
             ),
           )


class table_disk_apps(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops.update({
            'chart': col_app_chart(
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

class table_disk_arrays(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops.update({
            'chart': col_arrays_chart(
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


