def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

class table_compare(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.dbfilterable = False
        self.refreshable = False
        self.linkable = False
        self.bookmarkable = False
        self.pageable = False
        self.commonalityable = False
        self.exportable = False
        self.columnable = False
        self.object_list = []
        self.nodatabanner = False
        self.additional_tools.append('compare')
        self += HtmlTableMenu('Scenario', 'spark16', [
                                'compare_add',
                                'compare_del',
                               ]
                )

    def compare_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='compare_del'),
              ),
              DIV(
                self.form_compare_del(),
                _style='display:none',
                _class='white_float',
                _name='compare_del',
                _id='compare_del',
              ),
            )
        return d

    def compare_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='compare_add'),
              ),
              DIV(
                self.form_compare_add(),
                _style='display:none',
                _class='white_float',
                _name='compare_add',
                _id='compare_add',
              ),
            )
        return d

    def form_compare_del(self):
        action = 'ajax_del_compare'
        return self.compare_selector("del_compare", action)

    def form_compare_add(self):
        name = DIV(
                 T("Name"),
                 INPUT(
                   _name="compare_name",
                   _id="compare_name",
                 )
               )
        q = db.gen_filtersets.id > 0
        o = db.gen_filtersets.fset_name
        rows = db(q).select(orderby=o)
        opts = []
        for row in rows:
            o = SPAN(
                  SPAN(
                    INPUT(
                      _type="checkbox",
                      _name="ckfset",
                      _id="ckfset_%d"%row.id,
                      _value='false',
                      _onclick='this.value=this.checked',
                      value=False,
                    ),
                  ),
                  SPAN(
                    row.fset_name,
                    _style="margin:2px",
                  ),
                  BR(),
                  _style="white-space:nowrap",
                )
            opts.append(o)
        filters = DIV(opts)
        submit = INPUT(
                   _type="submit",
                   _onclick=self.ajax_submit(additional_inputs=['compare_name'],
                                             additional_input_name="ckfset",
                                             args=['compare_add']),
                 )
        d = DIV(
              name,
              HR(),
              filters,
              HR(),
              submit,
            )
        return d

    def format_compare_option(self, row):
        if row is None:
            name = T("None")
            compare_id = 0
        else:
            name = row.name
            compare_id = row.id
        return OPTION(
                 name,
                 _value=compare_id,
                 )

    def get_current_scenario(self):
        q = db.stats_compare_user.user_id == auth.user_id
        row = db(q).select().first()
        if row is None:
            active_compare_id = 0
        else:
            active_compare_id = row.compare_id
        return active_compare_id

    def compare_selector(self, id, action):
        # get user's current selected compare
        active_compare_id = self.get_current_scenario()

        # create the compare select()
        q = db.stats_compare.id > 0
        rows = db(q).select()
        av = [self.format_compare_option(None)]
        for row in rows:
            av.append(self.format_compare_option(row))
        content = SELECT(
                    av,
                    value=active_compare_id,
                    _onchange="""
                       ajax('%(url)s/'+this.options[this.selectedIndex].value, [], '%(div)s');
                    """%dict(url=URL(
                                   r=request, c='ajax',
                                   f=action,
                                ),
                              div="foo",
                             )+self.ajax_submit(),
                  )

        return SPAN(
                 content,
                 _class='floatw',
               )

    def compare(self):
        action = 'ajax_select_compare'
        return self.compare_selector("foo", action)

@auth.requires_login()
def compare_add():
    l = [k for k in request.vars if 'ckfset_' in k and request.vars[k] == 'true']
    if len(l) == 0:
        raise ToolError("at least one filterset must be selected")
    fset_ids = map(lambda x: x.replace('ckfset_',''), l)
    cname = request.vars['compare_name']
    rows = db(db.stats_compare.name==cname).select()
    if len(rows) > 0:
        raise ToolError("compare scenario name already exists")
    db.stats_compare.insert(name=cname)
    cid = db(db.stats_compare.name==cname).select().first()
    if cid is None:
        raise ToolError("error creating compare scenario")
    cid = cid.id
    db.stats_compare_user.insert(compare_id=cid, user_id=auth.user_id)
    for i in fset_ids:
        db.stats_compare_fset.insert(compare_id=cid, fset_id=i)

@auth.requires_login()
def ajax_compare():
    session.forget(response)
    t = table_compare('stats', 'ajax_compare')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'compare_add':
                compare_add()
        except ToolError, e:
            t.flash = str(e)


    d = DIV(
     DIV(
       t.html(),
     ),
     DIV(
       H2(T("Services")),
       DIV(
         DIV(T("Number of services")),
         DIV(
           _id='stat_day_svc',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         DIV(T("Production ratio")),
         DIV(
           _id='stat_day_svc_prd_ratio',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         DIV(T("DRP ratio")),
         DIV(
           _id='stat_day_svc_drp_ratio',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         DIV(T("Clustering ratio")),
         DIV(
           _id='stat_day_svc_clu_ratio',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Nodes")),
       DIV(
         DIV(T("Number of nodes")),
         DIV(
           _id='stat_day_nodes',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         DIV(T("Virtualization ratio")),
         DIV(
           _id='stat_day_nodes_virt_ratio',
         ),
         _class='float',
         _style='min-width:500px',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     SCRIPT(
       "stat_compare_day('%(url)s', 'stat_day');"%dict(
         url=URL(r=request,
                 f='call/json/json_stat_compare_day'),
       ),
       _name=t.id+'_to_eval',
     ),
     _id="stats",
    )
    return d

@auth.requires_login()
def compare():
    return dict(table=ajax_compare())

def compare_load():
    return ajax_compare()

class table_stats(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['fset_name',
                     'day',
                     'nb_svc',
                     'nb_svc_prd',
                     'nb_svc_cluster',
                     'nb_action',
                     'nb_action_err',
                     'nb_action_warn',
                     'nb_action_ok',
                     'disk_size',
                     'local_disk_size',
                     'ram_size',
                     'nb_cpu_core',
                     'nb_cpu_die',
                     'nb_vcpu',
                     'nb_vmem',
                     'watt',
                     'rackunit',
                     'nb_apps',
                     'nb_accounts',
                     'nb_svc_with_drp',
                     'nb_nodes',
                     'nb_virt_nodes',
                     'nb_nodes_prd',
                     'nb_resp_accounts']
        self.colprops = {
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     table='gen_filtersets',
                     field='fset_name',
                     img='filter16',
                     display=True,
                    ),
            'day': HtmlTableColumn(
                     title='Day',
                     table='stat_day',
                     field='day',
                     img='time16',
                     display=True,
                    ),
            'nb_svc': HtmlTableColumn(
                     title='Number of service',
                     table='stat_day',
                     field='nb_svc',
                     img='spark16',
                     display=True,
                    ),
            'nb_svc_prd': HtmlTableColumn(
                     title='Number of production service',
                     table='stat_day',
                     field='nb_svc_prd',
                     img='spark16',
                     display=True,
                    ),
            'nb_svc_cluster': HtmlTableColumn(
                     title='Number of clustered service',
                     table='stat_day',
                     field='nb_svc_cluster',
                     img='spark16',
                     display=True,
                    ),
            'nb_action': HtmlTableColumn(
                     title='Number of actions',
                     table='stat_day',
                     field='nb_action',
                     img='spark16',
                     display=True,
                    ),
            'nb_action_err': HtmlTableColumn(
                     title='Number of error actions',
                     table='stat_day',
                     field='nb_action_err',
                     img='spark16',
                     display=True,
                    ),
            'nb_action_warn': HtmlTableColumn(
                     title='Number of warn actions',
                     table='stat_day',
                     field='nb_action_warn',
                     img='spark16',
                     display=True,
                    ),
            'nb_action_ok': HtmlTableColumn(
                     title='Number of ok actions',
                     table='stat_day',
                     field='nb_action_ok',
                     img='spark16',
                     display=True,
                    ),
            'disk_size': HtmlTableColumn(
                     title='SAN Disk size (GB)',
                     table='stat_day',
                     field='disk_size',
                     img='spark16',
                     display=True,
                    ),
            'local_disk_size': HtmlTableColumn(
                     title='DAS Disk size (GB)',
                     table='stat_day',
                     field='local_disk_size',
                     img='spark16',
                     display=True,
                    ),
            'ram_size': HtmlTableColumn(
                     title='Ram size (GB)',
                     table='stat_day',
                     field='ram_size',
                     img='spark16',
                     display=True,
                    ),
            'nb_cpu_core': HtmlTableColumn(
                     title='Number of cpu cores',
                     table='stat_day',
                     field='nb_cpu_core',
                     img='spark16',
                     display=True,
                    ),
            'nb_cpu_die': HtmlTableColumn(
                     title='Number of cpu dies',
                     table='stat_day',
                     field='nb_cpu_die',
                     img='spark16',
                     display=True,
                    ),
            'nb_vmem': HtmlTableColumn(
                     title='Vram size (GB)',
                     table='stat_day',
                     field='nb_vmem',
                     img='spark16',
                     display=True,
                    ),
            'nb_vcpu': HtmlTableColumn(
                     title='Number of vcpus',
                     table='stat_day',
                     field='nb_vcpu',
                     img='spark16',
                     display=True,
                    ),
            'watt': HtmlTableColumn(
                     title='Watt',
                     table='stat_day',
                     field='watt',
                     img='spark16',
                     display=True,
                    ),
            'rackunit': HtmlTableColumn(
                     title='Number of rack units',
                     table='stat_day',
                     field='rackunit',
                     img='spark16',
                     display=True,
                    ),
            'nb_apps': HtmlTableColumn(
                     title='Number of apps',
                     table='stat_day',
                     field='nb_apps',
                     img='spark16',
                     display=True,
                    ),
            'nb_accounts': HtmlTableColumn(
                     title='Number of accounts',
                     table='stat_day',
                     field='nb_accounts',
                     img='spark16',
                     display=True,
                    ),
            'nb_svc_with_drp': HtmlTableColumn(
                     title='Number of services with DRP',
                     table='stat_day',
                     field='nb_svc_with_drp',
                     img='spark16',
                     display=True,
                    ),
            'nb_nodes': HtmlTableColumn(
                     title='Number of nodes',
                     table='stat_day',
                     field='nb_nodes',
                     img='spark16',
                     display=True,
                    ),
            'nb_virt_nodes': HtmlTableColumn(
                     title='Number of virtual nodes',
                     table='stat_day',
                     field='nb_virt_nodes',
                     img='spark16',
                     display=True,
                    ),
            'nb_nodes_prd': HtmlTableColumn(
                     title='Number of production nodes',
                     table='stat_day',
                     field='nb_nodes_prd',
                     img='spark16',
                     display=True,
                    ),
            'nb_resp_accounts': HtmlTableColumn(
                     title='Number of sysresponsible',
                     table='stat_day',
                     field='nb_resp_accounts',
                     img='spark16',
                     display=True,
                    ),
        }

        self.dbfilterable = True
        self.headers = False
        self.filterable = False
        self.refreshable = False
        self.linkable = False
        self.bookmarkable = False
        self.pageable = False
        self.commonalityable = False
        self.exportable = True
        self.columnable = False
        self.object_list = []
        self.nodatabanner = False
        self.fset_stats = True

@auth.requires_login()
def ajax_stats():
    session.forget(response)
    t = table_stats('stats', 'ajax_stats')

    q = db.stat_day.id > 0
    q &= db.stat_day.fset_id == db.gen_filtersets.id
    t.csv_q = q
    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    d = DIV(
     DIV(
       t.html(),
     ),
     DIV(
       H2(T("Services")),
       DIV(
         DIV(_id='stat_day_svc_drp'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_svc_cluster'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_svc_type'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_nb_vcpu'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_nb_vmem'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_apps'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Nodes")),
       DIV(
         DIV(_id='stat_day_nodes'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_virt_nodes'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_nodes_core'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_nodes_ram'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Actions")),
       DIV(
         DIV(_id='stat_day_actions'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_err'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Disks")),
       DIV(
         DIV(_id='stat_day_disk'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_svc_disk'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_svc_disk'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Computing ressource usage")),
       DIV(
         DIV(_id='stat_day_node_cpu'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_node_mem'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_node_swp'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_node_proc_runq_sz'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_node_proc_plist_sz'),
         _class='float',
       ),
       DIV(
         DIV(_id='tps_stat_day_node_block'),
         _class='float',
       ),
       DIV(
         DIV(_id='bps_stat_day_node_block'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     DIV(
       H2(T("Collector user accounts")),
       DIV(
         DIV(_id='stat_day_accounts'),
         _class='float',
       ),
       DIV(
         DIV(_id='stat_day_resp_accounts'),
         _class='float',
       ),
       DIV(
         XML('&nbsp;'),
         _class='spacer',
       ),
       _class='container',
     ),
     SCRIPT(
       "stat_day('%(url)s', 'stat_day');"%dict(
         url=URL(r=request,
                 f='call/json/json_stat_day'),
       ),
       "stats_avg_cpu_for_nodes('%(url)s', 'stat_day_node_cpu');"%dict(
         url=URL(r=request,
                 f='call/json/json_avg_cpu_for_nodes',
                 vars={'higher':15}
          )
       ),
       "stats_avg_mem_for_nodes('%(url)s', 'stat_day_node_mem');"%dict(
         url=URL(r=request,
                 f='call/json/json_avg_mem_for_nodes',
                 vars={'lower':15}
          )
       ),
       "stats_avg_proc_for_nodes('%(url)s', 'stat_day_node_proc');"%dict(
         url=URL(r=request,
                 f='call/json/json_avg_proc_for_nodes',
                 vars={'higher':15}
          )
       ),
       "stats_avg_block_for_nodes('%(url)s', 'stat_day_node_block');"%dict(
         url=URL(r=request,
                 f='call/json/json_avg_block_for_nodes',
                 vars={'higher':15}
          )
       ),
       "stats_avg_swp_for_nodes('%(url)s', 'stat_day_node_swp');"%dict(
         url=URL(r=request,
                 f='call/json/json_avg_swp_for_nodes',
                 vars={'lower':15}
          )
       ),
       "stats_disk_for_svc('%(url)s', 'stat_day_svc_disk');"%dict(
         url=URL(r=request,
                 f='call/json/json_disk_for_svc',
                 vars={'higher':15}
          )
       ),
       "jqplot_img()",
       _name=t.id+'_to_eval',
     ),
     _id="stats",
   )
    return d

@auth.requires_login()
def stats():
    return dict(table=ajax_stats())

def stats_load():
    return stats()["table"]

@auth.requires_login()
def ajax_containerperf_plot():
    session.forget(response)
    containers = []
    for s in request.vars.node.split(','):
        l = s.split('@')
        if len(l) == 2:
            containers.append(l)

    b = None
    e = None
    bs = ''
    es = ''
    rowid = request.vars.rowid

    for v in request.vars:
       if 'begin' in v:
           bs = v
           l = v.split('_')
           if l > 1: rowid = l[-1]
       if 'end' in v:
           es = v

    if len(containers) == 0:
         return DIV(T("No data"))


    sc = ""
    l = []
    for container_name, nodename in containers:
        did = '_'.join((rowid, nodename.replace('.','_'), container_name.replace('.','_')))
        l.append(H3('@'.join((container_name, nodename))))
        l.append(DIV(_id=did))
        sc += """sync_ajax('%(url)s', ['%(bs)s', '%(es)s'], '%(did)s', function(){});"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_svc_plot_short',
                                     args=[nodename, did, container_name]),
                             rowid=rowid,
                             did=did,
                             bs=bs,
                             es=es,
             )

    d = DIV(
          SPAN(l),
          SCRIPT(
            sc,
            _name='plot_to_eval',
          ),
        )

    return d

@auth.requires_login()
def ajax_perfcmp_plot():
    session.forget(response)
    nodes = request.vars.node
    b = None
    e = None
    rowid = ''

    def add_rowid(s):
        if rowid is None: return s
        return '_'.join((s, rowid))

    for v in request.vars:
       if 'begin' in v:
           b = request.vars[v]
           l = v.split('_')
           if l > 1: rowid = l[-1]
       if 'end' in v:
           e = request.vars[v]

    if len(request.vars.node.split(',')) == 0:
         return DIV(T("No nodes selected"))

    plots = []
    plots.append("stats_avg_cpu_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_cpu_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_cpu_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_mem_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_mem_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_mem_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_swp_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_swp_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_swp_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_proc_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_proc_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_proc_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_block_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_block_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_block_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_disk_for_svc('%(url)s', '%(did)s');"%dict(
      did=add_rowid('disk_for_svc_plot'),
      url=URL(r=request,
              f='call/json/json_disk_for_svc',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))

    d = DIV(
          DIV(
            DIV(_id=add_rowid('avg_cpu_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('avg_mem_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('avg_swp_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('runq_sz_avg_proc_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('plist_sz_avg_proc_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('tps_avg_block_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('bps_avg_block_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('disk_for_svc_plot')),
            _class='float',
          ),
          DIV(
            XML('&nbsp;'),
            _class='spacer',
          ),
          SCRIPT(
            plots,
            _name='plot_to_eval',
          ),
        )

    return d

#
# raw data extractors
#
@auth.requires_login()
def rows_stat_compare_day():
    q = db.stats_compare_user.user_id == auth.user_id
    q &= db.stats_compare_fset.compare_id == db.stats_compare_user.compare_id
    q &= db.stats_compare_fset.fset_id == db.gen_filtersets.id
    rows = db(q).select()
    fset_ids = [0] + [r.gen_filtersets.id for r in rows]
    labels = ['global'] + [r.gen_filtersets.fset_name for r in rows]
    data = []
    for fset_id in fset_ids:
        data.append(rows_stat_day(fset_id))
    return labels, data

@auth.requires_login()
def rows_stat_day(fset_id=None):
    if fset_id is None:
        fset_id = user_fset_id()
    o = db.stat_day.id
    q = o > 0
    q &= db.stat_day.fset_id == fset_id
    try:
        b = db(q).select(orderby=o, limitby=(0,1)).first().day
        e = db(q).select(orderby=~o, limitby=(0,1)).first().day
    except:
        return []
    sql = """select *, %(d)s as d
             from stat_day
             where fset_id=%(fset_id)d
             group by d
             order by d"""%dict(d=period_concat(b, e, field='day'),
                                fset_id=fset_id)
    return db.executesql(sql)

@auth.requires_login()
def rows_stats_disks_per_svc(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        svcnames = ""
    else:
        q = db.svcmon.id > 0
        q = apply_filters(q, db.svcmon.mon_nodname, db.svcmon.mon_svcname)
        nodes = [repr(r.mon_nodname) for r in db(q).select(db.svcmon.mon_nodname)]
        svcnames = [repr(r.mon_svcname) for r in db(q).select(db.svcmon.mon_svcname)]
        svcnames = 'and v.mon_svcname in (%s)'%','.join(svcnames)
    nodes = 'and v.mon_nodname in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
        end = end + datetime.timedelta(days=0,
                                       hours=23-end.hour,
                                       minutes=59-end.minute,
                                       seconds=59-end.second,
                                      )
    sql = """select s.svcname,
                    s.disk_size
             from stat_day_svc s, svcmon v
             where day=(select max(day)
                        from stat_day_svc
                        where day>'%(begin)s'
                              and day<='%(end)s')
                   and s.day>'%(begin)s'
                   and s.day<='%(end)s'
                   and s.svcname=v.mon_svcname
                   and v.mon_nodname like '%(dom)s'
                   %(nodes)s
                   %(svcnames)s
             group by s.svcname
             order by s.disk_size
          """%dict(dom=dom, begin=begin, end=end, nodes=nodes, svcnames=svcnames)

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_cpu_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ last day avg cpu usage per node
    """
    if len(nodes) > 0:
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select nodename,
                    0,
                    cpu,
                    avg(usr) as avg_usr,
                    avg(nice) as avg_nice,
                    avg(sys) as avg_sys,
                    avg(iowait) as avg_iowait,
                    avg(steal) as avg_steal,
                    avg(irq) as avg_irq,
                    avg(soft) as avg_soft,
                    avg(guest) as avg_guest
             from stats_cpu%(period)s
             where cpu='all'
               and date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by 100-avg(usr+sys)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes, period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    return db.executesql(sql)

@auth.requires_login()
def rows_avg_mem_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ available mem
    """
    if len(nodes) > 0:
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(kbmemfree+kbcached) as avail,
                      avg(kbmemfree),
                      avg(kbcached)
               from stats_mem_u%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_swp_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(kbswpfree) as avail,
                      avg(kbswpused)
               from stats_swap%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_proc_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(runq_sz),
                      avg(plist_sz),
                      avg(ldavg_1),
                      avg(ldavg_5),
                      avg(ldavg_15) as o
               from stats_proc%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by o
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_block_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select nodename,
                    avg(rtps),
                    avg(wtps),
                    avg(rbps),
                    avg(wbps)
             from stats_block%(period)s
             where date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by avg(rbps)+avg(wbps)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes, period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    return db.executesql(sql)

#
# json data servers
#
@service.json
def json_stat_compare_day():
    labels, data = rows_stat_compare_day()
    data = map(_json_stat_day, data)
    d = []
    n = len(data)
    if n == 0:
        return [[],[]]
    for i, foo in enumerate(data[0]):
        t = []
        for j in range(0, n):
            t.append(data[j][i])
        d.append(t)
    return [labels, d]

@service.json
def json_stat_day():
    return _json_stat_day()

@service.json
def _json_stat_day(rows=None):
    if rows is None:
        rows = rows_stat_day()
    d = []
    nb_svc_not_prd = []
    nb_action = []
    nb_action_err = []
    nb_action_warn = []
    nb_action_ok = []
    disk_size = []
    local_disk_size = []
    ram_size = []
    nb_cpu_core = []
    nb_cpu_die = []
    watt = []
    rackunit = []
    nb_apps = []
    nb_accounts = []
    nb_svc_with_drp = []
    nb_nodes_not_prd = []
    nb_svc_prd = []
    nb_svc_cluster = []
    nb_nodes_prd = []
    nb_svc_not_cluster = []
    nb_svc_without_drp = []
    nb_vcpu = []
    nb_vmem = []
    nb_resp_accounts = []
    nb_virt_nodes = []
    nb_phys_nodes = []
    nb_virt_ratio = []
    nb_svc = []
    nb_nodes = []
    nb_svc_prd_ratio = []
    nb_svc_drp_ratio = []
    nb_svc_clu_ratio = []
    for r in rows:
        if r[2] is None or r[17] is None:
            v = None
        else:
            v = r[2] - r[17]
        nb_svc_not_prd.append([r[1], v])
        nb_action.append([r[1], r[3]])
        nb_action_err.append([r[1], r[4]])
        nb_action_warn.append([r[1], r[5]])
        nb_action_ok.append([r[1], r[6]])
        disk_size.append([r[1], r[7]])
        local_disk_size.append([r[1], r[25]])
        ram_size.append([r[1], r[8]])
        nb_cpu_core.append([r[1], r[9]])
        nb_cpu_die.append([r[1], r[10]])
        watt.append([r[1], r[11]])
        rackunit.append([r[1], r[12]])
        nb_apps.append([r[1], r[13]])
        nb_accounts.append([r[1], r[14]])
        nb_svc_with_drp.append([r[1], r[15]])
        if r[16] is None or r[19] is None:
            v = None
        else:
            v = r[16]-r[19]
        nb_nodes_not_prd.append([r[1], v])
        nb_svc_prd.append([r[1], r[17]])
        nb_svc_cluster.append([r[1], r[18]])
        nb_nodes_prd.append([r[1], r[19]])
        if r[15] is None or r[2] is None:
            v = None
        else:
            v = r[2]-r[15]
        nb_svc_without_drp.append([r[1], v])
        if r[18] is None or r[2] is None:
            v = None
        else:
            v = r[2]-r[18]
        nb_svc_not_cluster.append([r[1], v])
        nb_vcpu.append([r[1], r[21]])
        nb_vmem.append([r[1], r[22]])
        nb_resp_accounts.append([r[1], r[23]])
        nb_virt_nodes.append([r[1], r[24]])
        if r[16] is None or r[24] is None:
            v = None
        else:
            v = r[16]-r[24]
        nb_phys_nodes.append([r[1], v])
        nb_svc.append([r[1], r[2]])
        nb_nodes.append([r[1], r[16]])
        try:
            nb_virt_ratio.append([r[1], int(100*r[24]/r[16])])
        except:
            nb_virt_ratio.append([r[1], 0])
        try:
            nb_svc_prd_ratio.append([r[1], int(100*r[17]/r[2])])
        except:
            nb_svc_prd_ratio.append([r[1], 0])
        try:
            nb_svc_drp_ratio.append([r[1], int(100*r[15]/r[2])])
        except:
            nb_svc_drp_ratio.append([r[1], 0])
        try:
            nb_svc_clu_ratio.append([r[1], int(100*r[18]/r[2])])
        except:
            nb_svc_clu_ratio.append([r[1], 0])
    return [nb_svc_not_prd,
            nb_action,
            nb_action_err,
            nb_action_warn,
            nb_action_ok,
            disk_size,
            ram_size,
            nb_cpu_core,
            nb_cpu_die,
            watt,
            rackunit,
            nb_apps,
            nb_accounts,
            nb_svc_with_drp,
            nb_nodes_not_prd,
            nb_svc_prd,
            nb_svc_cluster,
            nb_nodes_prd,
            nb_svc_not_cluster,
            nb_svc_without_drp,
            nb_vcpu,
            nb_vmem,
            nb_resp_accounts,
            nb_virt_nodes,
            nb_phys_nodes,
            nb_svc,
            nb_nodes,
            nb_virt_ratio,
            nb_svc_prd_ratio,
            nb_svc_drp_ratio,
            nb_svc_clu_ratio,
            local_disk_size]

@service.json
def json_avg_cpu_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_cpu_for_nodes(nodes, begin, end, lower, higher)
    d = []
    u = []
    usr = []
    nice = []
    sys = []
    iowait = []
    steal = []
    irq = []
    soft = []
    guest = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        usr.append([r[3], j])
        nice.append([r[4], j])
        sys.append([r[5], j])
        iowait.append([r[6], j])
        steal.append([r[7], j])
        irq.append([r[8], j])
        soft.append([r[9], j])
        guest.append([r[10], j])
    return [d, [usr, nice, sys, iowait, steal, irq, soft, guest]]

@service.json
def json_avg_swp_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_swp_for_nodes(nodes, begin, end, lower, higher)
    d = []
    kbswpfree = []
    kbswpused = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        kbswpfree.append([int(r[1]/1024), j])
        kbswpused.append([int(r[2]/1024), j])
    return [d, [kbswpfree, kbswpused]]

@service.json
def json_avg_proc_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_proc_for_nodes(nodes, begin, end, lower, higher)
    d = []
    runq_sz = []
    plist_sz = []
    ldavg_1 = []
    ldavg_5 = []
    ldavg_15 = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        runq_sz.append([float(r[1]), j])
        plist_sz.append([float(r[2]), j])
        ldavg_1.append([float(r[3]), j])
        ldavg_5.append([float(r[4]), j])
        ldavg_15.append([float(r[5]), j])
    return [d, [runq_sz, plist_sz, ldavg_1, ldavg_5, ldavg_15]]

@service.json
def json_avg_mem_for_nodes():
    begin = request.vars.b
    end = request.vars.e
    nodes = request.vars.node
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_mem_for_nodes(nodes, begin, end, lower, higher)
    d = []
    free = []
    cache = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        free.append([int(r[2]/1024), j])
        cache.append([int(r[3]/1024), j])
    return [d, [free, cache]]

@service.json
def json_avg_block_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_block_for_nodes(nodes, begin, end, lower, higher)
    d = []
    rtps = []
    wtps = []
    rbps = []
    wbps = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        rtps.append([r[1]/2, j])
        wtps.append([r[2]/2, j])
        rbps.append([r[3]/2, j])
        wbps.append([r[4]/2, j])
    return [d, [rtps, wtps, rbps, wbps]]

@service.json
def json_disk_for_svc():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_stats_disks_per_svc(nodes, begin, end, 15, higher)
    d = []
    disk_size = []
    n = len(rows)
    for i, r in enumerate(rows):
        j = n-i
        d.append(r[0])
        disk_size.append([r[1], j])
    d.reverse()
    return [d, [disk_size]]


