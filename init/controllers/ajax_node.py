@auth.requires_login()
def perf_stats(node, rowid):
    def format_ajax(id, f, e):
        return """getElementById('%(e)s').innerHTML='%(spinner)s';
                  ajax("%(url)s",
                       ['node_%(id)s',
                        'begin_%(id)s',
                        'end_%(id)s'
                       ],"%(e)s");
               """%dict(url=URL(r=request,c='ajax_perf',f=f),
                               id=rowid,
                               e=e,
                               spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                       )
    def perf_group(title='', group=''):
        group_img_h = {
                        'trend': 'spark16.png',
                        'memswap': 'mem16.png',
                        'cpu': 'cpu16.png',
                        'proc': 'action16.png',
                        'block': 'hd16.png',
                        'blockdev': 'hd16.png',
                        'netdev': 'action_sync_16.png',
                        'netdev_err': 'action_sync_16.png',
                        'fs': 'hd16.png',
                        'svc': 'svc.png',
                      }
        divid = 'prf_cont_%s_%s'%(group,rowid)
        d = DIV(
              IMG(_src=URL(r=request,c='static',f=group_img_h[group])),
              A(
                T(title),
                _onClick="""toggle_plot('%(url)s', '%(rowid)s','%(div)s')"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_%s_plot'%group,
                                     args=[node, rowid]),
                             rowid=rowid,
                             div=divid),
              ),
              A(
                IMG(_src=URL(r=request,c='static',f='nok.png')),
                _onClick="""toggle_plot('%(url)s', '%(rowid)s','%(div)s')"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_%s_plot'%group,
                                     args=[node, rowid]),
                             rowid=rowid,
                             div=divid),
                _id='close_'+divid,
                _style='float:right;display:none',
              ),
              A(
                IMG(_src=URL(r=request,c='static',f='refresh16.png')),
                _onClick="""refresh_plot('%(url)s', '%(rowid)s','%(div)s')"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_%s_plot'%group,
                                     args=[node, rowid]),
                             rowid=rowid,
                             div=divid),
                _id='refresh_'+divid,
                _style='float:right;display:none',
              ),
              DIV(
               _id=divid,
               _style='display:none',
              ),
              _class='container',
            ),
        return d

    now = datetime.datetime.now()
    s = now - datetime.timedelta(days=0,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = s + datetime.timedelta(days=1)

    timepicker = """Calendar.setup({inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24" });"""
    t = DIV(
          SPAN(
            IMG(
              _title=T('Start'),
              _src=URL(r=request, c='static', f='begin16.png'),
              _style="vertical-align:middle",
            ),
            INPUT(
              _value=s.strftime("%Y-%m-%d %H:%M"),
              _id='begin_'+rowid,
              _class='datetime',
              _onfocus=timepicker,
            ),
            INPUT(
              _value=e.strftime("%Y-%m-%d %H:%M"),
              _id='end_'+rowid,
              _class='datetime',
              _onfocus=timepicker,
            ),
            IMG(
              _title=T('End'),
              _src=URL(r=request, c='static', f='end16.png'),
              _style="vertical-align:middle",
            ),
            SPAN(perf_group('Plot service resource usage', 'svc')),
            SPAN(perf_group('Plot resource usage trends', 'trend')),
            SPAN(perf_group('Plot cpu usage', 'cpu')),
            SPAN(perf_group('Plot mem/swap usage', 'memswap')),
            SPAN(perf_group('Plot process activity', 'proc')),
            SPAN(perf_group('Plot filesystem usage', 'fs')),
            SPAN(perf_group('Plot aggregated block device usage', 'block')),
            SPAN(perf_group('Plot per block device usage', 'blockdev')),
            SPAN(perf_group('Plot per net device usage', 'netdev')),
            SPAN(perf_group('Plot per net device errors', 'netdev_err')),
          ),
        )
    return t

@auth.requires_login()
def ajax_node():
    rowid = request.vars.rowid
    nodes = db(db.v_nodes.nodename==request.vars.node).select()
    if len(nodes) == 0:
        return DIV(
                 T("No asset information for %(node)s",
                   dict(node=request.vars.node)
                 ),
                 P(
                   A(
                     T("insert"),
                     _href=URL(r=request, f='node_insert'),
                   ),
                   _style='text-align:center',
                 ),
               )

    q = db.auth_node.nodename == request.vars.node
    rows = db(q).select(db.auth_node.uuid)

    if len(rows) == 0:
        node_uuid = T("not registered")
    else:
        q &= db.auth_node.nodename == db.nodes.nodename
        ug = user_groups()
        if "Manager" not in ug:
            q &= db.nodes.team_responsible.belongs(ug)
        rows = db(q).select(db.auth_node.uuid)
        if len(rows) == 0:
            node_uuid = T("hidden (you are not responsible of this node)")
        else:
            node_uuid = rows[0].uuid

    node = nodes[0]
    loc = TABLE(
      TR(TD(T('country'), _style='font-style:italic'), TD(node['loc_country'])),
      TR(TD(T('city'), _style='font-style:italic'), TD(node['loc_city'])),
      TR(TD(T('zip'), _style='font-style:italic'), TD(node['loc_zip'])),
      TR(TD(T('address'), _style='font-style:italic'), TD(node['loc_addr'])),
      TR(TD(T('building'), _style='font-style:italic'), TD(node['loc_building'])),
      TR(TD(T('floor'), _style='font-style:italic'), TD(node['loc_floor'])),
      TR(TD(T('room'), _style='font-style:italic'), TD(node['loc_room'])),
      TR(TD(T('rack'), _style='font-style:italic'), TD(node['loc_rack'])),
    )
    power = TABLE(
      TR(TD(T('nb power supply'), _style='font-style:italic'), TD(node['power_supply_nb'])),
      TR(TD(T('power cabinet #1'), _style='font-style:italic'), TD(node['power_cabinet1'])),
      TR(TD(T('power cabinet #2'), _style='font-style:italic'), TD(node['power_cabinet2'])),
      TR(TD(T('power protector'), _style='font-style:italic'), TD(node['power_protect'])),
      TR(TD(T('power protector breaker'), _style='font-style:italic'), TD(node['power_protect_breaker'])),
      TR(TD(T('power breaker #1'), _style='font-style:italic'), TD(node['power_breaker1'])),
      TR(TD(T('power breaker #2'), _style='font-style:italic'), TD(node['power_breaker1'])),
    )
    server = TABLE(
      TR(TD(T('model'), _style='font-style:italic'), TD(node['model'])),
      TR(TD(T('type'), _style='font-style:italic'), TD(node['type'])),
      TR(TD(T('serial'), _style='font-style:italic'), TD(node['serial'])),
      TR(TD(T('warranty end'), _style='font-style:italic'), TD(node['warranty_end'])),
      TR(TD(T('team responsible'), _style='font-style:italic'), TD(node['team_responsible'])),
      TR(TD(T('integration'), _style='font-style:italic'), TD(node['team_integ'])),
      TR(TD(T('support'), _style='font-style:italic'), TD(node['team_support'])),
      TR(TD(T('project'), _style='font-style:italic'), TD(node['project'])),
      TR(TD(T('status'), _style='font-style:italic'), TD(node['status'])),
      TR(TD(T('role'), _style='font-style:italic'), TD(node['role'])),
      TR(TD(T('host mode'), _style='font-style:italic'), TD(node['host_mode'])),
      TR(TD(T('env'), _style='font-style:italic'), TD(node['environnement'])),
      TR(TD(T('uuid'), _style='font-style:italic'), TD(node_uuid)),
    )
    cpu = TABLE(
      TR(TD(T('cpu frequency'), _style='font-style:italic'), TD(node['cpu_freq'])),
      TR(TD(T('cpu cores'), _style='font-style:italic'), TD(node['cpu_cores'])),
      TR(TD(T('cpu dies'), _style='font-style:italic'), TD(node['cpu_dies'])),
      TR(TD(T('cpu vendor'), _style='font-style:italic'), TD(node['cpu_vendor'])),
      TR(TD(T('cpu model'), _style='font-style:italic'), TD(node['cpu_model'])),
    )
    mem = TABLE(
      TR(TD(T('memory banks'), _style='font-style:italic'), TD(node['mem_banks'])),
      TR(TD(T('memory slots'), _style='font-style:italic'), TD(node['mem_slots'])),
      TR(TD(T('memory total'), _style='font-style:italic'), TD(node['mem_bytes'])),
    )
    os = TABLE(
      TR(TD(T('os name'), _style='font-style:italic'), TD(node['os_name'])),
      TR(TD(T('os vendor'), _style='font-style:italic'), TD(node['os_vendor'])),
      TR(TD(T('os release'), _style='font-style:italic'), TD(node['os_release'])),
      TR(TD(T('os kernel'), _style='font-style:italic'), TD(node['os_kernel'])),
      TR(TD(T('os arch'), _style='font-style:italic'), TD(node['os_arch'])),
    )

    # storage
    q = db.node_hba.nodename == request.vars.node
    hbas = db(q).select()
    _hbas = [TR(
               TH("id"),
               TH("type"),
             )]
    for hba in hbas:
        _hbas.append(TR(
                       TD(hba.hba_id),
                       TD(hba.hba_type),
                     ))
    if len(_hbas) == 1:
        _hbas.append(TR(
                       TD('-'),
                       TD('-'),
                     ))

    q = db.svcdisks.disk_nodename == request.vars.node
    q &= db.diskinfo.id > 0
    q &= db.svcdisks.disk_id==db.diskinfo.disk_id
    q &= db.diskinfo.disk_arrayid==db.stor_array.array_name
    disks = db(q).select()
    _disks = [TR(
          TH("wwid"),
          TH("size"),
          TH("service"),
          TH("array model"),
          TH("array id"),
          TH("array disk group"),
        )]
    for disk in disks:
        _disks.append(TR(
          TD(disk.svcdisks.disk_id),
          TD(disk.svcdisks.disk_size, T('MB')),
          TD(disk.svcdisks.disk_svcname),
          TD(disk.stor_array.array_model),
          TD(disk.diskinfo.disk_arrayid),
          TD(disk.diskinfo.disk_group),
        ))
    if len(_disks) == 1:
        _disks.append(TR(
          TD('-'),
          TD('-'),
          TD('-'),
          TD('-'),
          TD('-'),
          TD('-'),
        ))

    stor = DIV(
      H3(T("Host Bus Adapters")),
      TABLE(_hbas),
      H3(T("Disks")),
      TABLE(_disks),
    )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 11):
            buff += """$('#%(tab)s_%(id)s').hide();$('#li%(tab)s_%(id)s').removeClass('tab_active');"""%dict(tab='tab'+str(i), id=rowid)
        buff += """$('#%(tab)s_%(id)s').show();$('#li%(tab)s_%(id)s').addClass('tab_active');"""%dict(tab=tab, id=rowid)
        return buff

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("%(n)s", dict(n=request.vars.node)),
                _class='nok',
                _onclick="""$('#%(id)s').hide()"""%dict(id=rowid),
              ),
              _class="closetab",
            ),
            LI(
              P(
                T("server"),
                _class='node16',
                _onclick=js('tab1', rowid),
              ),
              _class="tab_active",
              _id="litab1_"+str(rowid),
            ),
            LI(P(T("os"), _class='os16', _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("mem"), _class='mem16', _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("cpu"), _class='cpu16', _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("storage"), _class='hd16', _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("location"), _class='loc', _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
            LI(P(T("power"), _class='pwr', _onclick=js('tab7', rowid)), _id="litab7_"+str(rowid)),
            LI(P(T("stats"), _class='spark16', _onclick=js('tab8', rowid)), _id="litab8_"+str(rowid)),
            LI(P(T("wiki"), _class='edit', _onclick=js('tab9', rowid)), _id="litab9_"+str(rowid)),
            LI(P(T("compliance"), _class='comp16', _onclick=js('tab10', rowid)), _id="litab10_"+str(rowid)),
          ),
          _class="tab",
        ),
      ),
      TR(
        TD(
          DIV(
            server,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            os,
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            mem,
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            cpu,
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            stor,
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            loc,
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            power,
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            perf_stats(request.vars.node, rowid),
            _id='tab8_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab9_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab10_'+str(rowid),
            _class='cloud',
          ),
          SCRIPT(
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab9_'+str(rowid),
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['tab9_'+str(rowid), request.vars.node])
            ),
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab10_'+str(rowid),
               url=URL(r=request, c='compliance', f='ajax_compliance_node',
                       args=[request.vars.node])
            ),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
    )
    return t


