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
                     'disk_size',
                     'disk_group',
                     'disk_raid',
                     'disk_devid',
                     'disk_arrayid']
        self.colprops.update({
            'disk_id': HtmlTableColumn(
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
            'disk_size': HtmlTableColumn(
                     title='Size (GB)',
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
                     title='Updated',
                     table='svcdisks',
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
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'svcdisks'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_disks_col_values'
        self.span = 'disk_id'
        self.sub_span = ['disk_svcname', 'disk_size', 'disk_arrayid', 'disk_devid', 'disk_raid', 'disk_group']

        if 'StorageManager' in user_groups() or \
           'StorageManager' in user_groups():
            self.additional_tools.append('provision')

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
    rows = db(q).select()

    l = [OPTION(T("Choose one"))]
    for s in rows:
        o = OPTION(
                "%s %s - %s - quota %d GB"%(s.stor_array.array_model,
                                            s.stor_array.array_name,
                                            s.stor_array_dg.dg_name,
                                            s.stor_array_dg_quota.quota),
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

    o = db.stor_array_tgtid.array_tgtid | db.nodes.environnement | db.nodes.nodename

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
            TD(path.nodes.environnement),
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
    q |= db.svcdisks.id>0
    l = db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id)
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o, left=l)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_disks():
    t = table_disks('disks', 'ajax_disks')
    o = db.svcdisks.disk_id
    q = db.diskinfo.id>0
    q |= db.svcdisks.id>0
    l = db.svcdisks.on(db.diskinfo.disk_id==db.svcdisks.disk_id)
    #q &= db.svcdisks.disk_nodename==db.v_nodes.nodename
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = len(db(q).select(left=l))
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=l)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()

@auth.requires_login()
def disks():
    t = DIV(
          ajax_disks(),
          _id='disks',
        )
    return dict(table=t)


