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
                               spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                       )

    now = datetime.datetime.now()
    s = now - datetime.timedelta(days=0,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = s + datetime.timedelta(days=1)

    timepicker = """Calendar.setup({inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24" });"""
    t = DIV(
          SPAN(
            INPUT(
              _type='hidden',
              _value=node,
              _id='node_'+rowid,
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
            INPUT(
              _value='gen',
              _type='button',
              _onClick=format_ajax(rowid, 'ajax_perf_stats_cpu', 'perf_cpu_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_mem_u', 'perf_mem_u_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_trends', 'perf_trends_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_swap', 'perf_swap_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_proc', 'perf_proc_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_netdev', 'perf_netdev_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_netdev_err', 'perf_netdev_err_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_block', 'perf_block_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_blockdev', 'perf_blockdev_'+rowid)
            )
          ),
          DIV(
            _id='perf_trends_'+rowid
          ),
          DIV(
            _id='perf_cpu_'+rowid
          ),
          DIV(
            _id='perf_mem_u_'+rowid
          ),
          DIV(
            _id='perf_swap_'+rowid
          ),
          DIV(
            _id='perf_proc_'+rowid
          ),
          DIV(
            _id='perf_netdev_'+rowid
          ),
          DIV(
            _id='perf_netdev_err_'+rowid
          ),
          DIV(
            _id='perf_block_'+rowid
          ),
          DIV(
            _id='perf_blockdev_'+rowid
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
      TR(TD(T('status'), _style='font-style:italic'), TD(node['status'])),
      TR(TD(T('role'), _style='font-style:italic'), TD(node['role'])),
      TR(TD(T('env'), _style='font-style:italic'), TD(node['environnement'])),
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

    def js(tab, rowid):
        buff = ""
        for i in range(1, 8):
            buff += """getElementById('%(tab)s_%(id)s').style['display']='none';
                       getElementById('li%(tab)s_%(id)s').style['backgroundColor']='#EEE';
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """getElementById('%(tab)s_%(id)s').style['display']='block';
                   getElementById('li%(tab)s_%(id)s').style['backgroundColor']='orange';
                """%dict(tab=tab, id=rowid)
        return buff

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("close %(n)s", dict(n=request.vars.node)),
                _class="tab closetab",
                _onclick="""
                    getElementById("tr_id_%(id)s").style['display']='none'
                """%dict(id=rowid),
              ),
            ),
            LI(
              P(
                T("server"),
                _class="tab",
                _onclick=js('tab1', rowid),
              ),
              _id="litab1_"+str(rowid),
              _style="background-color:orange",
            ),
            LI(P(T("os"), _class="tab", _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("mem"), _class="tab", _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("cpu"), _class="tab", _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("location"), _class="tab", _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("power"), _class="tab", _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
            LI(P(T("stats"), _class="tab", _onclick=js('tab7', rowid)), _id="litab7_"+str(rowid)),
            _class="web2py-menu web2py-menu-horizontal",
          ),
          _style="border-bottom:solid 1px orange;padding:1px",
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
            loc,
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            power,
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            perf_stats(request.vars.node, rowid),
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
        ),
      ),
    )
    return t


