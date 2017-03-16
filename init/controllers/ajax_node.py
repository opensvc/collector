def test_sandata():
    d = sandata(["foo"]).main()
    print json.dumps(d, indent=4, separators=(',', ': '))

class sandata(object):
    def __init__(self, node_ids):
        self.node_ids = node_ids
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

    def get_endpoints(self, node_id):
        q = db.node_hba.node_id == node_id
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
        for node_id in self.node_ids:
            id = 's%d'%self.n_server
            self.n_server += 1
            s = {
                 'id': id,
                 'label': get_nodename(node_id),
                }
            self.d['server'][node_id] = s

            endpoints = self.get_endpoints(node_id)
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
                self.recurse_relations(sp, None, (node_id, sp, ap, an))

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
def ajax_node_stor():
    id = request.args[0]
    node_id = request.args[1]

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
        node_hba.node_id = "%s"
      group by node_hba.hba_id
      order by node_hba.hba_id
    """%str(node_id)
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
        stor_zone.node_id = "%s"
      group by stor_zone.hba_id, stor_zone.tgt_id
      order by stor_zone.hba_id, stor_zone.tgt_id
    """%str(node_id)
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
    q = db.svcdisks.node_id == node_id
    q &= (db.diskinfo.disk_group != "virtual")|(db.diskinfo.disk_group==None)
    q &= (db.stor_array.array_model != "vdisk provider")|(db.stor_array.array_model==None)
    l1 = db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id)
    l2 = db.stor_array.on(db.diskinfo.disk_arrayid==db.stor_array.array_name)
    l3 = db.services.on(db.svcdisks.svc_id==db.services.svc_id)
    disks = db(q).select(db.svcdisks.ALL,
                         db.diskinfo.ALL,
                         db.stor_array.ALL,
                         db.services.svcname,
                         cacheable=True, left=(l1,l2,l3),
                         orderby=db.svcdisks.disk_id)
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
          TD(disk.services.svcname),
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
          _src=URL(r=request,c='static',f='images/spinner.gif'),
          _style="vertical-align:top;padding-right:0.5em",
        ),
        SPAN(T("Generating SAN topology diagram")),
        _id="sanviz"+id,
      ),
      SCRIPT(
        """sync_ajax("%(url)s", [], "%(id)s", function(){})""" % dict(
          url = URL(c='ajax_node', f='ajax_node_stor_sanviz', args=[node_id]),
          id = "sanviz"+id,
        ),
      ),
      BR(),
      H3(T("Host Bus Adapters")),
      TABLE(_hbas, _class="table"),
      BR(),
      H3(T("Targets")),
      TABLE(_tgts, _class="table"),
      BR(),
      H3(T("Disks")),
      TABLE(_disks, _class="table"),
      _style="padding:1em",
    )
    return stor

@auth.requires_login()
def ajax_node_stor_sanviz():
    node_id = request.args[0]
    from applications.init.modules import san
    import tempfile
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    d = sandata([node_id]).main()
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
    svc_id = request.args[1]

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
        nodes.nodename
      from
        svcmon
        join nodes on svcmon.node_id=nodes.node_id
        left join node_hba on svcmon.node_id=node_hba.node_id
        left join switches on node_hba.hba_id=switches.sw_rportname
        left join san_zone_alias on node_hba.hba_id=san_zone_alias.port
        left join san_zone on node_hba.hba_id=san_zone.port
      where
        svcmon.svc_id = "%s"
      group by node_hba.hba_id
      order by node_hba.hba_id
    """%svc_id
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
        nodes.nodename
      from
        svcmon
        join nodes on svcmon.node_id = nodes.node_id
        left join stor_zone on svcmon.node_id=stor_zone.node_id
        left join switches on stor_zone.tgt_id=switches.sw_rportname
        left join san_zone_alias on stor_zone.tgt_id=san_zone_alias.port
        left join san_zone on stor_zone.tgt_id=san_zone.port and san_zone.zone in (select zone from san_zone where port=stor_zone.hba_id)
        left join stor_array_tgtid on stor_zone.tgt_id=stor_array_tgtid.array_tgtid
        left join stor_array on stor_array_tgtid.array_id=stor_array.id
      where
        svcmon.svc_id = "%s"
      group by stor_zone.hba_id, stor_zone.tgt_id
      order by nodes.nodename, stor_zone.hba_id, stor_zone.tgt_id
    """%svc_id
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
    q = db.svcdisks.svc_id == svc_id
    q &= (db.diskinfo.disk_group != "virtual")|(db.diskinfo.disk_group==None)
    q &= (db.stor_array.array_model != "vdisk provider")|(db.stor_array.array_model==None)
    l1 = db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id)
    l2 = db.stor_array.on(db.diskinfo.disk_arrayid==db.stor_array.array_name)
    disks = db(q).select(db.svcdisks.ALL, db.diskinfo.ALL, db.stor_array.ALL,
                         cacheable=True, left=(l1,l2),
                         orderby=db.svcdisks.disk_id)
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
          TD(get_nodename(disk.svcdisks.node_id)),
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
          _src=URL(r=request,c='static',f='images/spinner.gif'),
          _style="vertical-align:top;padding-right:0.5em",
        ),
        SPAN(T("Generating SAN topology diagram")),
        _id="sanviz"+id,
      ),
      SCRIPT(
        """sync_ajax("%(url)s", [], "%(id)s", function(){})""" % dict(
          url = URL(c='ajax_node', f='ajax_svc_stor_sanviz', args=[svc_id]),
          id = "sanviz"+id,
        ),
      ),
      BR(),
      H3(T("Host Bus Adapters")),
      TABLE(_hbas, _class="table"),
      BR(),
      H3(T("Targets")),
      TABLE(_tgts, _class="table"),
      BR(),
      H3(T("Disks")),
      TABLE(_disks, _class="table"),
      _style="padding:1em",
    )
    return stor

@auth.requires_login()
def ajax_svc_stor_sanviz():
    svc_id = request.args[0]

    q = db.svcmon.svc_id == svc_id
    rows = db(q).select(db.svcmon.node_id, cacheable=True)

    from applications.init.modules import san
    import tempfile
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    d = sandata([r.node_id for r in rows]).main()
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

