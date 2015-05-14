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
                _onClick="""$('#%(div)s').html('%(spinner)s');
                            toggle_plot('%(url)s', '%(rowid)s','%(div)s')"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_%s_plot'%group,
                                     args=[node, rowid]),
                             spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
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
                _onClick="""$('#%(div)s').html('%(spinner)s');
                            refresh_plot('%(url)s', '%(rowid)s','%(div)s')"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_%s_plot'%group,
                                     args=[node, rowid]),
                             spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
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
    s = now - datetime.timedelta(days=1,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = now

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
              _name="begin",
              _class='datetime',
            ),
            INPUT(
              _value=e.strftime("%Y-%m-%d %H:%M"),
              _id='end_'+rowid,
              _name="end",
              _class='datetime',
            ),
            IMG(
              _title=T('End'),
              _src=URL(r=request, c='static', f='end16.png'),
              _style="vertical-align:middle",
            ),
            STYLE(XML('input {margin-left:2px}')),
            INPUT(
              _value=T("Now"),
              _type="button",
              _onclick="""
                var d = new Date()
                $(this).siblings("input[name='end']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                d.setDate(d.getDate() - 1);
                d.setHours(0);
                d.setMinutes(0);
                $(this).siblings("input[name='begin']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                $(this).siblings().find("a:visible[id^='refresh']").trigger('click')
              """,
            ),
            INPUT(
              _value=T("Last day"),
              _type="button",
              _onclick="""
                var d = new Date()
                d.setHours(0);
                d.setMinutes(0);
                $(this).siblings("input[name='end']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                d.setDate(d.getDate() - 1);
                $(this).siblings("input[name='begin']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                $(this).siblings().find("a:visible[id^='refresh']").trigger('click')
              """,
            ),
            INPUT(
              _value=T("Last week"),
              _type="button",
              _onclick="""
                var d = new Date()
                d.setHours(0);
                d.setMinutes(0);
                $(this).siblings("input[name='end']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                d.setDate(d.getDate() - 7);
                $(this).siblings("input[name='begin']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                $(this).siblings().find("a:visible[id^='refresh']").trigger('click')
              """,
            ),
            INPUT(
              _value=T("Last month"),
              _type="button",
              _onclick="""
                var d = new Date()
                d.setHours(0);
                d.setMinutes(0);
                $(this).siblings("input[name='end']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                d.setDate(d.getDate() - 31);
                $(this).siblings("input[name='begin']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                $(this).siblings().find("a:visible[id^='refresh']").trigger('click')
              """,
            ),
            INPUT(
              _value=T("Last year"),
              _type="button",
              _onclick="""
                var d = new Date()
                d.setHours(0);
                d.setMinutes(0);
                $(this).siblings("input[name='end']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                d.setDate(d.getDate() - 365);
                $(this).siblings("input[name='begin']").each(function(){
                  $(this).val(print_date(d))
                  $(this).effect("highlight")
                })
                $(this).siblings().find("a:visible[id^='refresh']").trigger('click')
              """,
            ),
            SPAN(perf_group('Plot container resource usage', 'svc')),
            SPAN(perf_group('Plot cpu usage', 'cpu')),
            SPAN(perf_group('Plot mem/swap usage', 'memswap')),
            SPAN(perf_group('Plot process activity', 'proc')),
            SPAN(perf_group('Plot filesystem usage', 'fs')),
            SPAN(perf_group('Plot aggregated block device usage', 'block')),
            SPAN(perf_group('Plot per block device usage', 'blockdev')),
            SPAN(perf_group('Plot per net device usage', 'netdev')),
            SPAN(perf_group('Plot per net device errors', 'netdev_err')),
            SCRIPT(
              """$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})"""
            )
          ),
        )
    return t

def test_sandata():
    d = sandata(["foo"]).main()
    print json.dumps(d, indent=4, separators=(',', ': '))

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
        self.relcache = {}

    def get_endpoints(self, nodename):
        q = db.node_hba.nodename == nodename
        l1 = db.stor_zone.on(db.node_hba.hba_id==db.stor_zone.hba_id)
        l2 = db.stor_array_tgtid.on(db.stor_zone.tgt_id==db.stor_array_tgtid.array_tgtid)
        l3 = db.stor_array.on(db.stor_array_tgtid.array_id==db.stor_array.id)
        l = []
        for r in db(q).select(db.node_hba.hba_id, db.stor_zone.tgt_id,
                              db.stor_array.array_name, left=(l1,l2,l3),
                              cacheable=True):
            l.append((
              r.node_hba.hba_id,
              r.stor_zone.tgt_id,
              r.stor_array.array_name
            ))
        return l

    def cache_relations(self):
        self.swname_cache = {}
        q = db.switches.id > 0
        for row in db(q).select(cacheable=True):
            self.swname_cache[row.sw_portname] = row.sw_name
            for t in (row.sw_portname, row.sw_rportname):
                if t in self.relcache:
                    self.relcache[t].append(row)
                else:
                    self.relcache[t] = [row]

    def get_relations(self, portname, endpoints):
        rels = self.relcache.get(portname, []) + self.relcache.get(str(endpoints[2]), [])
        return [r for r in rels if r.sw_rportname == portname or
                (r.sw_portname == portname and r.sw_rportname == endpoints[2])]

    def recurse_relations(self, portname, portindex, endpoints, chain=[]):
        rels = self.get_relations(portname, endpoints)
        if len(rels) == 0:
            return
        for rel in rels:
            if rel.sw_rportname in self.array_ports:
               print "array port found", rel.sw_rportname, "in chain", " => ".join(map(lambda x: self.swname_cache[x], chain))
               self.valid_switch |= set(chain)
            if rel.sw_rportname not in self.array_ports and \
               rel.sw_portname in chain:
                # loop
                continue
            _chain = chain + [rel.sw_portname]
            print "follow", " => ".join(map(lambda x: self.swname_cache[x], _chain))
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
                print "new link", " => ".join(map(lambda x: self.swname_cache.get(x, x), [rel.sw_rportname, rel.sw_portname]))
                # new link
                count = 1
                speed = [rel.sw_portspeed]
                if rel.sw_rportname == endpoints[2]:
                    #print chain, "sw -> array"
                    # sw -> array
                    head = endpoints[3]
                    headlabel = rel.sw_rportname
                    tail = rel.sw_portname
                    taillabel = str(rel.sw_index)
                    self.valid_switch |= set(_chain)
                    print "valid", " => ".join(map(lambda x: self.swname_cache[x], _chain))
                elif rel.sw_rportname == endpoints[1]:
                    #print chain, "nodes -> sw"
                    # node -> sw
                    head = rel.sw_portname
                    headlabel = str(rel.sw_index)
                    tail = endpoints[0]
                    taillabel = rel.sw_rportname
                else:
                    #print chain, "sw -> sw", rel.sw_porttype
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
            if rel.sw_rportname not in self.array_ports and \
               (len(chain)==0 or rel.sw_porttype=="E-Port"):
                self.recurse_relations(rel.sw_portname, rel.sw_index, endpoints, _chain)

    def get_remote_port_speed(self, portname, rportname):
        q = db.switches.sw_portname == rportname
        q &= db.switches.sw_rportname == portname
        return [r.sw_portspeed for r in db(q).select(db.switches.sw_portspeed, groupby=db.switches.sw_index, orderby=db.switches.sw_index, cacheable=True)]

    def get_remote_port_index(self, portname, rportname):
        q = db.switches.sw_portname == rportname
        q &= db.switches.sw_rportname == portname
        return [r.sw_index for r in db(q).select(db.switches.sw_index, groupby=db.switches.sw_index, orderby=db.switches.sw_index, cacheable=True)]

    def main(self):
        self.cache_relations()
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
def fetch_node_pw():
    nodename = request.vars.nodename
    q = db.auth_node.nodename == nodename
    rows = db(q).select(db.auth_node.uuid, cacheable=True)

    if len(rows) == 0:
        return T("not registered")

    q &= db.auth_node.nodename == db.nodes.nodename
    ug = user_groups()
    if "Manager" not in ug:
        q &= db.nodes.team_responsible.belongs(ug)
    rows = db(q).select(db.auth_node.uuid, cacheable=True)

    if len(rows) == 0:
        return T("hidden (you are not responsible of this node)")

    node_uuid = rows[0].uuid
    config = local_import('config', reload=True)
    try:
        salt = config.aes_salt
    except Exception as e:
        salt = "tlas"

    sql = """select aes_decrypt(pw, "%(sec)s") from node_pw where
             nodename="%(nodename)s"
          """ % dict(nodename=nodename, sec=node_uuid+salt)
    pwl = db.executesql(sql)
    if len(pwl) == 0:
        return T("This node has not reported its root password (opensvc agent feature not activated or agent too old)")

    _log('password.retrieve',
         'retrieved root password of node %(nodename)s',
         dict(nodename=nodename),
         nodename=nodename)

    return pwl[0][0]

def node_pw_tool(nodename, id):
    ug = user_groups()
    if "Manager" not in ug and "RootPasswordExec" not in ug:
        return "-"

    return A(
      SPAN(T("Retrieve root password"), _class='lock'),
      _id='pw_'+str(id),
      _onclick="""sync_ajax('%(url)s', [], '%(id)s', function(){})""" % dict(
        url=URL(r=request, f='fetch_node_pw', vars={'nodename': nodename}),
        id='pw_'+str(id),
      ),
    )

def get_node_tags(nodename):
    q = db.nodes.nodename == nodename
    ug = user_groups()
    if "Manager" not in ug:
        q &= db.nodes.team_responsible.belongs(ug)
    rows = db(q).select(db.nodes.id)
    if len(rows) == 0:
        responsible = False
    else:
        responsible = True

    import uuid
    tid = uuid.uuid1().hex

    d = DIV(
      SCRIPT(""" init_tags({"tid": "%s", "responsible": %s, "nodename": "%s"}) """ % (tid, str(responsible).lower(), nodename)),
      _class="tags",
      _id=tid,
    )
    return d

@auth.requires_login()
def ajax_node():
    session.forget(response)
    rowid = request.vars.rowid
    tab = request.vars.tab
    if tab is None:
        tab = "tab1"

    nodes = db(db.v_nodes.nodename==request.vars.node).select(cacheable=True)
    if len(nodes) == 0:
        return TABLE(
                DIV(
                 P(
                  T("No asset information for %(node)s",
                    dict(node=request.vars.node)
                  ),
                  _class="nok",
                 ),
                 BR(),
                 P(
                   A(
                     T("insert"),
                     _href=URL(r=request, c='nodes', f='node_insert'),
                   ),
                   _class="edit16", 
                 ),
                 _style="padding:1em",
                ),
               )

    q = db.auth_node.nodename == request.vars.node
    rows = db(q).select(db.auth_node.uuid, cacheable=True)

    if len(rows) == 0:
        node_uuid = T("not registered")
        node_pw = ""
    else:
        q &= db.auth_node.nodename == db.nodes.nodename
        ug = user_groups()
        if "Manager" not in ug:
            q &= db.nodes.team_responsible.belongs(ug)
        rows = db(q).select(db.auth_node.id, db.auth_node.uuid, cacheable=True)
        if len(rows) == 0:
            node_uuid = T("hidden (you are not responsible of this node)")
            node_pw = ""
        else:
            node_uuid = rows[0].uuid
            node_pw = node_pw_tool(request.vars.node, rows.first().id)

    node = nodes[0]
    loc = TABLE(
      TR(TH(T('country')), TD(node['loc_country'] if node['loc_country'] is not None else '')),
      TR(TH(T('city')), TD(node['loc_city'] if node['loc_city'] is not None else '')),
      TR(TH(T('zip')), TD(node['loc_zip'] if node['loc_zip'] is not None else '')),
      TR(TH(T('address')), TD(node['loc_addr'] if node['loc_addr'] is not None else '')),
      TR(TH(T('building')), TD(node['loc_building'] if node['loc_building'] is not None else '')),
      TR(TH(T('floor')), TD(node['loc_floor'] if node['loc_floor'] is not None else '')),
      TR(TH(T('room')), TD(node['loc_room'] if node['loc_room'] is not None else '')),
      TR(TH(T('rack')), TD(node['loc_rack'] if node['loc_rack'] is not None else '')),
      TR(TH(T('enclosure')), TD(node['enclosure'] if node['enclosure'] is not None else '')),
      TR(TH(T('enclosure slot')), TD(node['enclosureslot'] if node['enclosureslot'] is not None else '')),
    )
    power = TABLE(
      TR(TH(T('nb power supply')), TD(node['power_supply_nb'] if node['power_supply_nb'] is not None else '')),
      TR(TH(T('power cabinet #1')), TD(node['power_cabinet1'] if node['power_cabinet1'] is not None else '')),
      TR(TH(T('power cabinet #2')), TD(node['power_cabinet2'] if node['power_cabinet2'] is not None else '')),
      TR(TH(T('power protector')), TD(node['power_protect'] if node['power_protect'] is not None else '')),
      TR(TH(T('power protector breaker')), TD(node['power_protect_breaker'] if node['power_protect_breaker'] is not None else '')),
      TR(TH(T('power breaker #1')), TD(node['power_breaker1'] if node['power_breaker1'] is not None else '')),
      TR(TH(T('power breaker #2')), TD(node['power_breaker1'] if node['power_breaker1'] is not None else '')),
    )
    server = TABLE(
      TR(TH(T('fqdn')), TD(node['fqdn'] if node['fqdn'] is not None else '')),
      TR(TH(T('asset name')), TD(node['assetname'] if node['assetname'] is not None else '')),
      TR(TH(T('model')), TD(node['model'] if node['model'] is not None else '')),
      TR(TH(T('type')), TD(node['type'] if node['type'] is not None else '')),
      TR(TH(T('serial')), TD(node['serial'] if node['serial'] is not None else '')),
      TR(TH(T('security zone')), TD(node['sec_zone'] if node['sec_zone'] is not None else '')),
      TR(TH(T('status')), TD(node['status'] if node['status'] is not None else '')),
      TR(TH(T('role')), TD(node['role'] if node['role'] is not None else '')),
      TR(TH(T('env')), TD(node['environnement'] if node['environnement'] is not None else '')),
      TR(TH(T('root pwd')), TD(node_pw)),
    )
    dates = TABLE(
      TR(TH(T('updated')), TD(node['updated'] if node['updated'] is not None else '')),
      TR(TH(T('last boot')), TD(node['last_boot'] if node['last_boot'] is not None else '')),
      TR(TH(T('warranty end')), TD(node['warranty_end'] if node['warranty_end'] is not None else '')),
      TR(TH(T('maintenance end')), TD(node['maintenance_end'] if node['maintenance_end'] is not None else '')),
    )
    org = TABLE(
      TR(TH(T('team responsible')), TD(node['team_responsible'] if node['team_responsible'] is not None else '')),
      TR(TH(T('integration')), TD(node['team_integ'] if node['team_integ'] is not None else '')),
      TR(TH(T('support')), TD(node['team_support'] if node['team_support'] is not None else '')),
      TR(TH(T('project')), TD(node['project'] if node['project'] is not None else '')),
    )
    agent = TABLE(
      TR(TH(T('agent version')), TD(node['version'] if node['version'] is not None else '')),
      TR(TH(T('agent listener port')), TD(node['listener_port'])),
      TR(TH(T('host mode')), TD(node['host_mode'])),
      TR(TH(T('uuid')), TD(node_uuid)),
    )
    cpu = TABLE(
      TR(TH(T('cpu frequency')), TD(node['cpu_freq'])),
      TR(TH(T('cpu threads')), TD(node['cpu_threads'] if node['cpu_threads'] is not None else '')),
      TR(TH(T('cpu cores')), TD(node['cpu_cores'])),
      TR(TH(T('cpu dies')), TD(node['cpu_dies'])),
      #TR(TH(T('cpu vendor')), TD(node['cpu_vendor'])),
      TR(TH(T('cpu model')), TD(node['cpu_model'])),
    )
    mem = TABLE(
      TR(TH(T('memory banks')), TD(node['mem_banks'])),
      TR(TH(T('memory slots')), TD(node['mem_slots'])),
      TR(TH(T('memory total')), TD(node['mem_bytes'])),
    )
    ops = TABLE(
      TR(TH(T('os name')), TD(node['os_name'])),
      TR(TH(T('os vendor')), TD(node['os_vendor'])),
      TR(TH(T('os release')), TD(node['os_release'])),
      TR(TH(T('os kernel')), TD(node['os_kernel'])),
      TR(TH(T('os arch')), TD(node['os_arch'])),
    )
    tags = TABLE(
      get_node_tags(request.vars.node),
      _style="width:100%",
    )

    asset = DIV(
      DIV(
        H3(SPAN(SPAN(T("server"), _class="node16")), _class="line"),
        server,
      ),
      DIV(
        H3(SPAN(SPAN(T("tags"), _class="tag16")), _class="line"),
        tags,
      ),
      DIV(
        H3(SPAN(SPAN(T("organization"), _class="guys16")), _class="line"),
        org,
      ),
      DIV(
        H3(SPAN(SPAN(T("location"), _class="loc")), _class="line"),
        loc,
      ),
      DIV(
        H3(SPAN(SPAN(T("opensvc agent"), _class="svc")), _class="line"),
        agent,
      ),
      DIV(
        H3(SPAN(SPAN(T("os"), _class="os16")), _class="line"),
        ops,
      ),
      DIV(
        H3(SPAN(SPAN(T("mem"), _class="hw16")), _class="line"),
        mem,
      ),
      DIV(
        H3(SPAN(SPAN(T("cpu"), _class="cpu16")), _class="line"),
        cpu,
      ),
      DIV(
        H3(SPAN(SPAN(T("power"), _class="pwr")), _class="line"),
        power,
      ),
      DIV(
        H3(SPAN(SPAN(T("dates"), _class="time16")), _class="line"),
        dates,
      ),
      _class="asset_tab",
    )

    # net
    sql = """select
               node_ip.addr,
               node_ip.mask,
               node_ip.mac,
               node_ip.intf,
               node_ip.type,
               networks.name,
               networks.comment,
               networks.pvid,
               networks.network,
               networks.broadcast,
               networks.netmask,
               networks.gateway,
               networks.begin,
               networks.end,
               networks.prio
             from node_ip
             left join networks
             on
               inet_aton(node_ip.addr) >= inet_aton(begin) and
               inet_aton(node_ip.addr) <= inet_aton(end)
             where
               node_ip.nodename = "%(nodename)s"
             order by node_ip.mac, node_ip.intf
          """ % dict(nodename=request.vars.node)
    rows = db.executesql(sql, as_dict=True)
    nets_header = TR(
               TH("mac"),
               TH("interface", _style="width:7em"),
               TH("type"),
               TH("addr", _style="width:20em"),
               TH("mask", _style="width:7em"),
               TH("net name", _style="width:10em"),
               TH("net comment", _style="width:10em"),
               TH("net pvid", _style="width:4em"),
               TH("net base"),
               TH("net gateway", _style="width:7em"),
               TH("net prio", _style="width:5em"),
               TH("net begin", _style="width:7em"),
               TH("net end", _style="width:7em"),
             )
    nets_v4_unicast = [nets_header]
    nets_v6_unicast = [nets_header]
    nets_v4_mcast = [nets_header]
    nets_v6_mcast = [nets_header]
    for row in rows:
        netline = TR(
                       TD(row['mac']),
                       TD(row['intf']),
                       TD(row['type']),
                       TD(row['addr']),
                       TD(row['mask']),
                       TD(row['name'] if row['name'] else '-', _class="bluer"),
                       TD(row['comment'] if row['comment'] else '-', _class="bluer"),
                       TD(row['pvid'] if row['pvid'] else '-', _class="bluer"),
                       TD(row['network'] if row['network'] else '-', _class="bluer"),
                       TD(row['gateway'] if row['gateway'] else '-', _class="bluer"),
                       TD(row['prio'] if row['prio'] is not None else '-', _class="bluer"),
                       TD(row['begin'] if row['begin'] else '-', _class="bluer"),
                       TD(row['end'] if row['end'] else '-', _class="bluer"),
                     )
        if row['type'] == "ipv4":
            if row['mask'] != "":
                nets_v4_unicast.append(netline)
            else:
                nets_v4_mcast.append(netline)
        elif row['type'] == "ipv6":
            if row['mask'] != "":
                nets_v6_unicast.append(netline)
            else:
                nets_v6_mcast.append(netline)
    empty_netline = TR(
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
                     )
    if len(nets_v4_mcast) == 1:
        nets_v4_mcast.append(empty_netline)
    if len(nets_v4_unicast) == 1:
        nets_v4_unicast.append(empty_netline)
    if len(nets_v6_mcast) == 1:
        nets_v6_mcast.append(empty_netline)
    if len(nets_v6_unicast) == 1:
        nets_v6_unicast.append(empty_netline)

    nets = DIV(
      H3(SPAN(T("ipv4 unicast")), _class="line"),
      TABLE(nets_v4_unicast),
      H3(SPAN(T("ipv6 unicast")), _class="line"),
      TABLE(nets_v6_unicast),
      H3(SPAN(T("ipv4 multicast")), _class="line"),
      TABLE(nets_v4_mcast),
      H3(SPAN(T("ipv6 multicast")), _class="line"),
      TABLE(nets_v6_mcast),
    )

    t = TABLE(
      TR(
        TD(
          UL(
            LI(P(request.vars.node, _class='nok'), _class="closetab"),
            LI(P(T("properties"), _class='node16'), _class="tab_active", _id="litab1_"+str(rowid)),
            LI(P(T("alerts"), _class='alert16'), _id="litab14_"+str(rowid)),
            LI(P(T("services"), _class='svc'), _id="litab5_"+str(rowid)),
            LI(P(T("actions"), _class='action16'), _id="litab15_"+str(rowid)),
            LI(P(T("log"), _class='log16'), _id="litab16_"+str(rowid)),
            LI(P(T("topology"), _class='dia16'), _id="litab2_"+str(rowid)),
            LI(P(T("storage"), _class='hd16'), _id="litab6_"+str(rowid)),
            LI(P(T("network"), _class='net16'), _id="litab7_"+str(rowid)),
            LI(P(T("stats"), _class='spark16'), _id="litab10_"+str(rowid)),
            LI(P(T("wiki"), _class='edit'), _id="litab11_"+str(rowid)),
            LI(P(T("checks"), _class='check16'), _id="litab12_"+str(rowid)),
            LI(P(T("compliance"), _class='comp16'), _id="litab13_"+str(rowid)),
            LI(P(T("sysreport"), _class='log16'), _id="litab17_"+str(rowid)),
          ),
          _class="tab",
        ),
      ),
      TR(
        TD(
          DIV(
            asset,
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
            _id='tab16_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab17_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab15_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab14_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab5_'+str(rowid),
            _class='cloud',
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
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab13_'+str(rowid),
            _class='cloud',
          ),
          SCRIPT(
            "function n%(rid)s_load_sysreport(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab17_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_sysreport', f='ajax_sysreport',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_node_log(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab16_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='log', f='log_node',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_node_actions(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab15_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='svcactions', f='actions_node',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_topo(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab2_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='topo', f='ajax_topo',
                       vars={"nodenames": request.vars.node, "display": "nodes,services,countries,cities,buildings,rooms,racks,enclosures,hvs,hvpools,hvvdcs,disks"})
            ),
            "function n%(rid)s_load_node_alerts(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab14_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='dashboard', f='dashboard_node',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_node_stor(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab6_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_node', f='ajax_node_stor',
                       args=['tab6_'+str(rowid), request.vars.node])
            ),
            "function n%(rid)s_load_wiki(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab11_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['tab10_'+str(rowid), request.vars.node])
            ),
            "function n%(rid)s_load_checks(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab12_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='checks', f='checks_node',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_comp(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab13_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='compliance', f='ajax_compliance_node',
                       args=[request.vars.node])
            ),
            "function n%(rid)s_load_svcmon_node(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab5_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='default', f='svcmon_node',
                       args=[request.vars.node])
            ),
            """bind_tabs("%(id)s", {
                "litab6_%(id)s": n%(id)s_load_node_stor,
                "litab2_%(id)s": n%(id)s_load_topo,
                "litab11_%(id)s": n%(id)s_load_wiki,
                "litab12_%(id)s": n%(id)s_load_checks,
                "litab13_%(id)s": n%(id)s_load_comp,
                "litab14_%(id)s": n%(id)s_load_node_alerts,
                "litab15_%(id)s": n%(id)s_load_node_actions,
                "litab16_%(id)s": n%(id)s_load_node_log,
                "litab17_%(id)s": n%(id)s_load_sysreport,
                "litab5_%(id)s": n%(id)s_load_svcmon_node
               }, "%(tab)s")
            """%dict(id=str(rowid), tab="li"+tab+"_"+str(rowid)),
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
    q &= db.svcdisks.disk_local == False
    l1 = db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id)
    l2 = db.stor_array.on(db.diskinfo.disk_arrayid==db.stor_array.array_name)
    disks = db(q).select(db.svcdisks.ALL, db.diskinfo.ALL, db.stor_array.ALL, cacheable=True, left=(l1,l2))
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

    stor = DIV(
      H3("SAN"),
      DIV(
        IMG(
          _src=URL(r=request,c='static',f='spinner.gif'),
          _style="vertical-align:top;padding-right:0.5em",
        ),
        SPAN(T("Generating SAN topology diagram")),
        _id="sanviz"+id,
      ),
      SCRIPT(
        """sync_ajax("%(url)s", [], "%(id)s", function(){})""" % dict(
          url = URL(c='ajax_node', f='ajax_node_stor_sanviz', args=[nodename]),
          id = "sanviz"+id,
        ),
      ),
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
def ajax_node_stor_sanviz():
    nodename = request.args[0]
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

    return DIV(
      XML(sanviz_legend),
      IMG(_src=sanviz),
    )


@auth.requires_login()
def ajax_nodes_stor():
    nodes = request.vars.nodes
    if nodes is None:
        return "No data"
    nodes = set(nodes.split(','))
    nodes -= set([""])

    # san graphviz
    from applications.init.modules import san
    import tempfile
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    d = sandata(nodes).main()
    o = san.Viz(d)
    f = tempfile.NamedTemporaryFile(dir=vizdir, prefix='tempviz')
    sanviz = f.name
    f.close()
    o.write(sanviz)
    sanviz = URL(r=request,c='static',f=os.path.basename(sanviz))
    sanviz_legend = o.html_legend()

    stor = DIV(
      XML(sanviz_legend),
      IMG(_src=sanviz),
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
    disks = db(q).select(groupby=db.svcdisks.disk_id, cacheable=True)
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

    stor = DIV(
      H3("SAN"),
      DIV(
        IMG(
          _src=URL(r=request,c='static',f='spinner.gif'),
          _style="vertical-align:top;padding-right:0.5em",
        ),
        SPAN(T("Generating SAN topology diagram")),
        _id="sanviz"+id,
      ),
      SCRIPT(
        """sync_ajax("%(url)s", [], "%(id)s", function(){})""" % dict(
          url = URL(c='ajax_node', f='ajax_svc_stor_sanviz', args=[svcname]),
          id = "sanviz"+id,
        ),
      ),
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
def ajax_svc_stor_sanviz():
    svcname = request.args[0]

    q = db.svcmon.mon_svcname == svcname
    rows = db(q).select(db.svcmon.mon_nodname, cacheable=True)

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
      XML(sanviz_legend),
      IMG(_src=sanviz),
    )
    return stor

