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

class sandata(object):
    def __init__(self, nodenames):
        self.nodenames = nodenames
        self.n_server = 0
        self.n_array = 0
        self.n_switch = 0
        self.d = {
          'server': {},
          'array': {},
          'switch': {},
          'link': {},
        }
        self.valid_switch = set([])

    def get_endpoints(self, nodename):
        q = db.node_hba.nodename == nodename
        l1 = db.stor_zone.on(db.node_hba.hba_id==db.stor_zone.hba_id)
        l2 = db.stor_array_tgtid.on(db.stor_zone.tgt_id==db.stor_array_tgtid.array_tgtid)
        l3 = db.stor_array.on(db.stor_array_tgtid.array_id==db.stor_array.id)
        l = []
        for r in db(q).select(db.node_hba.hba_id, db.stor_zone.tgt_id, db.stor_array.array_name, left=(l1,l2,l3)):
            l.append((
              r.node_hba.hba_id,
              r.stor_zone.tgt_id,
              r.stor_array.array_name
            ))
        return l

    def get_relations(self, portname, endpoints):
        q = db.switches.sw_rportname == portname
        q |= (db.switches.sw_portname==portname)&(db.switches.sw_rportname==endpoints[2])
        return db(q).select()

    def recurse_relations(self, portname, portindex, endpoints, chain=[]):
        rels = self.get_relations(portname, endpoints)
        if len(rels) == 0:
            return
        for rel in rels:
            if rel.sw_rportname not in self.array_ports and \
               rel.sw_portname in chain:
                # loop
                continue
            _chain = chain + [rel.sw_portname]
            if rel.sw_portname not in self.d['switch']:
                # new switch
                id = 'sw%d'%self.n_switch
                self.n_switch += 1
                s = {'id': id, 'label': rel.sw_name, 'rank': len(chain)}
                self.d['switch'][rel.sw_portname] = s
            elif len(chain) > self.d['switch'][rel.sw_portname]['rank']:
                self.d['switch'][rel.sw_portname]['rank'] = len(chain)
            id = [rel.sw_rportname, rel.sw_portname]
            id.sort()
            id = '-'.join(id)
            if id not in self.d['link']:
                # new link
                count = 1
                speed = [rel.sw_portspeed]
                if rel.sw_rportname == endpoints[2]:
                    # sw -> array
                    head = endpoints[3]
                    headlabel = rel.sw_rportname
                    tail = rel.sw_portname
                    taillabel = str(rel.sw_index)
                    self.valid_switch |= set(_chain)
                elif rel.sw_rportname == endpoints[1]:
                    # node -> sw
                    head = rel.sw_portname
                    headlabel = str(rel.sw_index)
                    tail = endpoints[0]
                    taillabel = rel.sw_rportname
                else:
                    # sw -> sw, single isl or trunks
                    head = rel.sw_portname
                    headlabel = str(rel.sw_index)
                    tail = rel.sw_rportname
                    rportindex = self.get_remote_port_index(rel.sw_portname, rel.sw_rportname)
                    count = len(rportindex)
                    taillabel = ','.join(map(lambda x: str(x), rportindex))
                    if count > 1:
                        _rportindex = self.get_remote_port_index(rel.sw_rportname, rel.sw_portname)
                        headlabel = ','.join(map(lambda x: str(x), _rportindex))
                        speed = self.get_remote_port_speed(rel.sw_rportname, rel.sw_portname)
                s = {
                  'tail': tail,
                  'taillabel': taillabel,
                  'head': head,
                  'headlabel': headlabel,
                  'count': count,
                  'speed': speed,
                }
                self.d['link'][id] = s
            elif rel.sw_rportname == endpoints[1]:
                #self.d['link'][id]['count'] += 1
                if portindex is not None:
                    self.d['link'][id]['headlabel'] += ',%d'%rel.sw_index
                    self.d['link'][id]['taillabel'] += ',%d'%portindex
            if rel.sw_rportname not in self.array_ports:
                self.recurse_relations(rel.sw_portname, rel.sw_index, endpoints, _chain)

    def get_remote_port_speed(self, portname, rportname):
        q = db.switches.sw_portname == rportname
        q &= db.switches.sw_rportname == portname
        return [r.sw_portspeed for r in db(q).select(db.switches.sw_portspeed, orderby=db.switches.sw_index)]

    def get_remote_port_index(self, portname, rportname):
        q = db.switches.sw_portname == rportname
        q &= db.switches.sw_rportname == portname
        return [r.sw_index for r in db(q).select(db.switches.sw_index, orderby=db.switches.sw_index)]

    def main(self):
        for nodename in self.nodenames:
            id = 's%d'%self.n_server
            self.n_server += 1
            s = {
                 'id': id,
                 'label': nodename,
                }
            self.d['server'][nodename] = s

            endpoints = self.get_endpoints(nodename)
            self.array_ports = {}
            for sp, ap, an in endpoints:
                if an not in self.d['array']:
                    # new array
                    id = 'a%d'%self.n_array
                    self.n_array += 1
                    s = {'id': id, 'label': an}
                    self.d['array'][an] = s
                self.array_ports[ap] = an

            for sp, ap, an in endpoints:
                self.recurse_relations(sp, None, (nodename, sp, ap, an))

        # purge unused switches
        import copy
        for switch in copy.copy(self.d['switch'].keys()):
            if switch not in self.valid_switch:
                del(self.d['switch'][switch])
                for link, linkd in copy.copy(self.d['link'].items()):
                    if switch == linkd['tail'] or switch == linkd['head']:
                        del(self.d['link'][link])

        #raise Exception(self.d)
        return self.d


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
    ops = TABLE(
      TR(TD(T('os name'), _style='font-style:italic'), TD(node['os_name'])),
      TR(TD(T('os vendor'), _style='font-style:italic'), TD(node['os_vendor'])),
      TR(TD(T('os release'), _style='font-style:italic'), TD(node['os_release'])),
      TR(TD(T('os kernel'), _style='font-style:italic'), TD(node['os_kernel'])),
      TR(TD(T('os arch'), _style='font-style:italic'), TD(node['os_arch'])),
    )


    # net
    q = db.node_ip.nodename == request.vars.node
    rows = db(q).select(orderby=db.node_ip.mac|db.node_ip.intf)
    _nets = [TR(
               TH("mac"),
               TH("interface"),
               TH("type"),
               TH("addr"),
               TH("mask"),
             )]
    for row in rows:
        _nets.append(TR(
                       TD(row.mac),
                       TD(row.intf),
                       TD(row.type),
                       TD(row.addr),
                       TD(row.mask),
                     ))
    if len(_nets) == 1:
        _nets.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))

    nets = DIV(
      H3(T("Networks")),
      TABLE(_nets),
    )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 14):
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
            LI(P(T("services"), _class='svc', _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("storage"), _class='hd16', _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
            LI(P(T("network"), _class='net16', _onclick=js('tab7', rowid)), _id="litab7_"+str(rowid)),
            LI(P(T("location"), _class='loc', _onclick=js('tab8', rowid)), _id="litab8_"+str(rowid)),
            LI(P(T("power"), _class='pwr', _onclick=js('tab9', rowid)), _id="litab9_"+str(rowid)),
            LI(P(T("stats"), _class='spark16', _onclick=js('tab10', rowid)), _id="litab10_"+str(rowid)),
            LI(P(T("wiki"), _class='edit', _onclick=js('tab11', rowid)), _id="litab11_"+str(rowid)),
            LI(P(T("checks"), _class='check16', _onclick=js('tab12', rowid)), _id="litab12_"+str(rowid)),
            LI(P(T("compliance"), _class='comp16', _onclick=js('tab13', rowid)), _id="litab13_"+str(rowid)),
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
            ops,
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
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab5_'+str(rowid),
            _class='cloud',
            _style='max-width:80em',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            nets,
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            loc,
            _id='tab8_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            power,
            _id='tab9_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            perf_stats(request.vars.node, rowid),
            _id='tab10_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab11_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab12_'+str(rowid),
            _class='cloud',
            _style='max-width:80em',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab13_'+str(rowid),
            _class='cloud',
            _style='max-width:80em',
          ),
          SCRIPT(
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab6_'+str(rowid),
               url=URL(r=request, c='ajax_node', f='ajax_node_stor',
                       args=['tab5_'+str(rowid), request.vars.node])
            ),
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab11_'+str(rowid),
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['tab10_'+str(rowid), request.vars.node])
            ),
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab12_'+str(rowid),
               url=URL(r=request, c='checks', f='checks_node',
                       args=[request.vars.node])
            ),
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab13_'+str(rowid),
               url=URL(r=request, c='compliance', f='ajax_compliance_node',
                       args=[request.vars.node])
            ),
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab5_'+str(rowid),
               url=URL(r=request, c='default', f='svcmon_node',
                       args=[request.vars.node])
            ),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
    )
    return t

@auth.requires_login()
def ajax_node_stor():
    id = request.args[0]
    nodename = request.args[1]

    # storage adapters
    sql = """
      select
        node_hba.hba_id,
        node_hba.hba_type,
        switches.sw_name,
        switches.sw_slot,
        switches.sw_port,
        switches.sw_portspeed,
        switches.sw_portnego,
        san_zone_alias.alias,
        group_concat(san_zone.zone order by san_zone.zone separator ', '),
        switches.sw_index
      from
        node_hba
        left join switches on node_hba.hba_id=switches.sw_rportname
        left join san_zone_alias on node_hba.hba_id=san_zone_alias.port
        left join san_zone on node_hba.hba_id=san_zone.port
      where
        node_hba.nodename = "%s"
      group by node_hba.hba_id
      order by node_hba.hba_id
    """%nodename
    hbas = db.executesql(sql)
    _hbas = [TR(
               TH("hba id"),
               TH("type"),
               TH("switch"),
               TH("index"),
               TH("slot"),
               TH("port"),
               TH("speed"),
               TH("autoneg"),
               TH("alias"),
               TH("zones"),
             )]
    for hba in hbas:
        _hbas.append(TR(
                       TD(hba[0]),
                       TD(hba[1]),
                       TD(hba[2]) if not hba[2] is None else '-',
                       TD(hba[9]) if not hba[9] is None else '-',
                       TD(hba[3]) if not hba[3] is None else '-',
                       TD(hba[4]) if not hba[4] is None else '-',
                       TD(str(hba[5])+' Gb/s') if not hba[5] is None else '-',
                       TD(hba[6]) if not hba[6] is None else '-',
                       TD(hba[7]) if not hba[7] is None else '-',
                       TD(hba[8]) if not hba[8] is None else '-',
                     ))
    if len(_hbas) == 1:
        _hbas.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))
    if len(_hbas) == 1:
        _hbas.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))

    # storage adapters
    sql = """
      select
        stor_zone.hba_id,
        stor_zone.tgt_id,
        switches.sw_name,
        switches.sw_slot,
        switches.sw_port,
        switches.sw_portspeed,
        switches.sw_portnego,
        san_zone_alias.alias,
        san_zone.zone,
        count(san_zone.zone) as c,
        stor_array.array_name,
        switches.sw_index
      from
        stor_zone
        left join switches on stor_zone.tgt_id=switches.sw_rportname
        left join san_zone_alias on stor_zone.tgt_id=san_zone_alias.port
        left join san_zone on stor_zone.tgt_id=san_zone.port and san_zone.zone in (select zone from san_zone where port=stor_zone.hba_id)
        left join stor_array_tgtid on stor_zone.tgt_id=stor_array_tgtid.array_tgtid
        left join stor_array on stor_array_tgtid.array_id=stor_array.id
      where
        stor_zone.nodename = "%s"
      group by stor_zone.hba_id, stor_zone.tgt_id
      order by stor_zone.hba_id, stor_zone.tgt_id
    """%nodename
    tgts = db.executesql(sql)
    _tgts = [TR(
               TH("hba id"),
               TH("tgt id"),
               TH("array"),
               TH("switch"),
               TH("index"),
               TH("slot"),
               TH("port"),
               TH("speed"),
               TH("autoneg"),
               TH("alias"),
               TH("zone"),
             )]
    for tgt in tgts:
        _tgts.append(TR(
                       TD(tgt[0]),
                       TD(tgt[1]),
                       TD(tgt[10]) if not tgt[10] is None else '-',
                       TD(tgt[2]) if not tgt[2] is None else '-',
                       TD(tgt[11]) if not tgt[11] is None else '-',
                       TD(tgt[3]) if not tgt[3] is None else '-',
                       TD(tgt[4]) if not tgt[4] is None else '-',
                       TD(str(tgt[5])+' Gb/s') if not tgt[5] is None else '-',
                       TD(tgt[6]) if not tgt[6] is None else '-',
                       TD(tgt[7]) if not tgt[7] is None else '-',
                       TD(tgt[8]) if not tgt[8] is None else '-',
                     ))
    if len(_tgts) == 1:
        _tgts.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))
    if len(_tgts) == 1:
        _tgts.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))

    # node disk list
    q = db.svcdisks.disk_nodename == nodename
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
          TD(disk.svcdisks.disk_used, T('MB')),
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

    # san graphviz
    from applications.init.modules import san
    import tempfile
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    d = sandata([nodename]).main()
    o = san.Viz(d)
    f = tempfile.NamedTemporaryFile(dir=vizdir, prefix='tempviz')
    sanviz = f.name
    f.close()
    o.write(sanviz)
    sanviz = URL(r=request,c='static',f=os.path.basename(sanviz))
    sanviz_legend = o.html_legend()

    stor = DIV(
      H3("SAN"),
      XML(sanviz_legend),
      IMG(_src=sanviz),
      BR(),
      H3(T("Host Bus Adapters")),
      TABLE(_hbas),
      BR(),
      H3(T("Targets")),
      TABLE(_tgts),
      BR(),
      H3(T("Disks")),
      TABLE(_disks),
    )
    return stor

@auth.requires_login()
def ajax_svc_stor():
    id = request.args[0]
    svcname = request.args[1]

    # storage adapters
    sql = """
      select
        node_hba.hba_id,
        node_hba.hba_type,
        switches.sw_name,
        switches.sw_slot,
        switches.sw_port,
        switches.sw_portspeed,
        switches.sw_portnego,
        san_zone_alias.alias,
        group_concat(san_zone.zone order by san_zone.zone separator ', '),
        switches.sw_index,
        svcmon.mon_nodname
      from
        svcmon
        left join node_hba on svcmon.mon_nodname=node_hba.nodename
        left join switches on node_hba.hba_id=switches.sw_rportname
        left join san_zone_alias on node_hba.hba_id=san_zone_alias.port
        left join san_zone on node_hba.hba_id=san_zone.port
      where
        svcmon.mon_svcname = "%s"
      group by node_hba.hba_id
      order by node_hba.hba_id
    """%svcname
    hbas = db.executesql(sql)
    _hbas = [TR(
               TH("nodename"),
               TH("hba id"),
               TH("type"),
               TH("switch"),
               TH("index"),
               TH("slot"),
               TH("port"),
               TH("speed"),
               TH("autoneg"),
               TH("alias"),
               TH("zones"),
             )]
    for hba in hbas:
        _hbas.append(TR(
                       TD(hba[10]),
                       TD(hba[0]) if not hba[0] is None else '-',
                       TD(hba[1]) if not hba[1] is None else '-',
                       TD(hba[2]) if not hba[2] is None else '-',
                       TD(hba[9]) if not hba[9] is None else '-',
                       TD(hba[3]) if not hba[3] is None else '-',
                       TD(hba[4]) if not hba[4] is None else '-',
                       TD(str(hba[5])+' Gb/s') if not hba[5] is None else '-',
                       TD(hba[6]) if not hba[6] is None else '-',
                       TD(hba[7]) if not hba[7] is None else '-',
                       TD(hba[8]) if not hba[8] is None else '-',
                     ))
    if len(_hbas) == 1:
        _hbas.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))
    if len(_hbas) == 1:
        _hbas.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))

    # storage adapters
    sql = """
      select
        stor_zone.hba_id,
        stor_zone.tgt_id,
        switches.sw_name,
        switches.sw_slot,
        switches.sw_port,
        switches.sw_portspeed,
        switches.sw_portnego,
        san_zone_alias.alias,
        san_zone.zone,
        count(san_zone.zone) as c,
        stor_array.array_name,
        switches.sw_index,
        svcmon.mon_nodname
      from
        svcmon
        left join stor_zone on svcmon.mon_nodname=stor_zone.nodename
        left join switches on stor_zone.tgt_id=switches.sw_rportname
        left join san_zone_alias on stor_zone.tgt_id=san_zone_alias.port
        left join san_zone on stor_zone.tgt_id=san_zone.port and san_zone.zone in (select zone from san_zone where port=stor_zone.hba_id)
        left join stor_array_tgtid on stor_zone.tgt_id=stor_array_tgtid.array_tgtid
        left join stor_array on stor_array_tgtid.array_id=stor_array.id
      where
        svcmon.mon_svcname = "%s"
      group by stor_zone.hba_id, stor_zone.tgt_id
      order by svcmon.mon_nodname, stor_zone.hba_id, stor_zone.tgt_id
    """%svcname
    tgts = db.executesql(sql)
    _tgts = [TR(
               TH("nodename"),
               TH("hba id"),
               TH("tgt id"),
               TH("array"),
               TH("switch"),
               TH("index"),
               TH("slot"),
               TH("port"),
               TH("speed"),
               TH("autoneg"),
               TH("alias"),
               TH("zone"),
             )]
    for tgt in tgts:
        _tgts.append(TR(
                       TD(tgt[12]),
                       TD(tgt[0]) if not tgt[0] is None else '-',
                       TD(tgt[1]) if not tgt[1] is None else '-',
                       TD(tgt[10]) if not tgt[10] is None else '-',
                       TD(tgt[2]) if not tgt[2] is None else '-',
                       TD(tgt[11]) if not tgt[11] is None else '-',
                       TD(tgt[3]) if not tgt[3] is None else '-',
                       TD(tgt[4]) if not tgt[4] is None else '-',
                       TD(str(tgt[5])+' Gb/s') if not tgt[5] is None else '-',
                       TD(tgt[6]) if not tgt[6] is None else '-',
                       TD(tgt[7]) if not tgt[7] is None else '-',
                       TD(tgt[8]) if not tgt[8] is None else '-',
                     ))
    if len(_tgts) == 1:
        _tgts.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))
    if len(_tgts) == 1:
        _tgts.append(TR(
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                       TD('-'),
                     ))

    # node disk list
    q = db.svcdisks.disk_svcname == svcname
    q &= db.diskinfo.id > 0
    q &= db.svcdisks.disk_id==db.diskinfo.disk_id
    q &= db.diskinfo.disk_arrayid==db.stor_array.array_name
    disks = db(q).select(groupby=db.svcdisks.disk_id)
    _disks = [TR(
          TH("wwid"),
          TH("size"),
          TH("nodename"),
          TH("array model"),
          TH("array id"),
          TH("array disk group"),
        )]
    for disk in disks:
        _disks.append(TR(
          TD(disk.svcdisks.disk_id),
          TD(disk.svcdisks.disk_used, T('MB')),
          TD(disk.svcdisks.disk_nodename),
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

    # san graphviz
    q = db.svcmon.mon_svcname == svcname
    rows = db(q).select(db.svcmon.mon_nodname)

    from applications.init.modules import san
    import tempfile
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    d = sandata([r.mon_nodname for r in rows]).main()
    o = san.Viz(d)
    f = tempfile.NamedTemporaryFile(dir=vizdir, prefix='tempviz')
    sanviz = f.name
    f.close()
    o.write(sanviz)
    sanviz = URL(r=request,c='static',f=os.path.basename(sanviz))
    sanviz_legend = o.html_legend()

    stor = DIV(
      H3("SAN"),
      XML(sanviz_legend),
      IMG(_src=sanviz),
      BR(),
      H3(T("Host Bus Adapters")),
      TABLE(_hbas),
      BR(),
      H3(T("Targets")),
      TABLE(_tgts),
      BR(),
      H3(T("Disks")),
      TABLE(_disks),
    )
    return stor


