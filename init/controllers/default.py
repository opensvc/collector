# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def user_load():
    if request.args[0] != "profile":
        raise HTTP(404)
    # only profile is loadable
    return auth()

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def index():
    redirect(URL(r=request, c='dashboard'))

@auth.requires_login()
def ajax_service():
    session.forget(response)
    rowid = request.vars.rowid
    tab = request.vars.tab
    if tab is None:
        tab = "tab1"

    rows = db(db.services.svc_name==request.vars.node).select(cacheable=True)
    if len(rows) == 0:
        return TABLE(
                 DIV(
                  P(
                    T("No service information for %(node)s",
                    dict(node=request.vars.node)),
                   _class="nok",
                  ),
                  _style="padding:1em",
                 ),
               )

    rows = db(db.v_svcmon.mon_svcname==request.vars.node).select(cacheable=True)
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

    containers = set([])
    for row in rows:
        if row.mon_vmtype in ('zone', 'ovm', 'xen'):
            containers.add('@'.join((row.mon_vmname, row.mon_nodname)))

    s = rows[0]

    def containerprf(rowid, containers):
        if len(containers) == 0:
            return SPAN()
        now = datetime.datetime.now()
        b = now - datetime.timedelta(days=0,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
        e = b + datetime.timedelta(days=1)

        d = DIV(
              SPAN(
                IMG(
                  _title=T('Start'),
                  _src=URL(r=request, c='static', f='images/begin16.png'),
                  _style="vertical-align:middle",
                ),
                INPUT(
                  _value=b.strftime("%Y-%m-%d %H:%M"),
                  _id='containerprf_begin_'+str(rowid),
                  _name='begin',
                  _class='datetime',
                ),
                INPUT(
                  _value=e.strftime("%Y-%m-%d %H:%M"),
                  _id='containerprf_end_'+str(rowid),
                  _name='end',
                  _class='datetime',
                ),
                IMG(
                  _title=T('End'),
                  _src=URL(r=request, c='static', f='images/end16.png'),
                  _style="vertical-align:middle",
                ),
                SPAN(
                  A(
                    IMG(
                      _src=URL(r=request, c='static', f='images/refresh16.png'),
                      _style="vertical-align:middle",
                    ),
                    _title=T('Refresh'),
                    _id='refresh_'+str(rowid),
                    _onclick="sync_ajax('%(url)s', ['containerprf_begin_%(id)s', 'containerprf_end_%(id)s'], 'containerprf_%(id)s', function(){});"%dict(
                      id=str(rowid),
                      url=URL(r=request, c='stats', f='ajax_containerperf_plot?node=%s'%','.join(containers)),
                    ),
                  ),
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
                SPAN(
                  _id='containerprf_'+str(rowid),
                ),
                SCRIPT(
                  """$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})""",
                ),
              ),
            )
        return d

    def grpprf(rowid):
        if s['svc_nodes'] is None or s['svc_drpnodes'] is None:
            return SPAN()
        now = datetime.datetime.now()
        b = now - datetime.timedelta(days=0,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
        e = b + datetime.timedelta(days=1)

        d = DIV(
              SPAN(
                IMG(
                  _title=T('Start'),
                  _src=URL(r=request, c='static', f='images/begin16.png'),
                  _style="vertical-align:middle",
                ),
                INPUT(
                  _value=b.strftime("%Y-%m-%d %H:%M"),
                  _id='grpprf_begin_'+str(rowid),
                  _name='begin',
                  _class='datetime',
                ),
                INPUT(
                  _value=e.strftime("%Y-%m-%d %H:%M"),
                  _id='grpprf_end_'+str(rowid),
                  _name='end',
                  _class='datetime',
                ),
                IMG(
                  _title=T('End'),
                  _src=URL(r=request, c='static', f='images/end16.png'),
                  _style="vertical-align:middle",
                ),
                SPAN(
                  A(
                    IMG(
                      _src=URL(r=request, c='static', f='images/refresh16.png'),
                      _style="vertical-align:middle",
                    ),
                    _title=T('Refresh'),
                    _id='refresh_'+str(rowid),
                    _onclick="sync_ajax('%(url)s', ['grpprf_begin_%(id)s', 'grpprf_end_%(id)s'], 'grpprf_%(id)s', function(){});"%dict(
                      id=str(rowid),
                      url=URL(r=request, c='stats', f='ajax_perfcmp_plot?node=%s'%','.join(s['svc_nodes'].split()+s['svc_drpnodes'].split())),
                    ),
                  ),
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
                SPAN(
                  _id='grpprf_'+str(rowid),
                ),
                SCRIPT(
                  """$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})""",
                ),
              ),
            )
        return d

    t = TABLE(
      TR(
        TD(
          UL(
            LI(P(request.vars.node, _class='nok'), _class="closetab"),
            LI(P(T("properties"), _class='svc'), _id="litab1_"+str(rowid), _class="tab_active"),
            LI(P(T("alerts"), _class='alert16'), _id="litab13_"+str(rowid)),
            LI(P(T("status"), _class='svc'), _id="litab2_"+str(rowid)),
            LI(P(T("resources"), _class='svc'), _id="litab3_"+str(rowid)),
            LI(P(T("actions"), _class='action16'), _id="litab14_"+str(rowid)),
            LI(P(T("log"), _class='log16'), _id="litab15_"+str(rowid)),
            LI(P(T("env"), _class='file16'), _id="litab4_"+str(rowid)),
            LI(P(T("topology"), _class='dia16'), _id="litab5_"+str(rowid)),
            LI(P(T("startup"), _class='startup'), _id="litab16_"+str(rowid)),
            LI(P(T("storage"), _class='hd16'), _id="litab6_"+str(rowid)),
            LI(P(T("container stats"), _class='spark16'), _id="litab12_"+str(rowid)),
            LI(P(T("stats"), _class='spark16'), _id="litab7_"+str(rowid)),
            LI(P(T("wiki"), _class='edit'), _id="litab8_"+str(rowid)),
            LI(P(T("avail"), _class='svc'), _id="litab9_"+str(rowid)),
            LI(P(T("pkgdiff"), _class='pkg16'), _id="litab10_"+str(rowid)),
            LI(P(T("compliance"), _class='comp16'), _id="litab11_"+str(rowid)),
          ),
          _class="tab",
        ),
      ),
      TR(
        TD(
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab13_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab14_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab15_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab16_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            containerprf(rowid, containers),
            _id='tab12_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            grpprf(rowid),
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab8_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab9_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab10_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
            _id='tab11_'+str(rowid),
            _class='cloud',
            _style='max-width:80em',
          ),
          SCRIPT(
            """function s%(rid)s_load_service_properties(){service_properties("%(id)s", %(options)s)}"""%dict(
               id='tab1_'+str(rowid),
               rid=str(rowid),
               options=str({"svcname": request.vars.node}),
            ),
            """function s%(rid)s_load_service_env(){service_env("%(id)s", %(options)s)}"""%dict(
               id='tab4_'+str(rowid),
               rid=str(rowid),
               options=str({"svcname": request.vars.node}),
            ),
            """function s%(rid)s_load_svcmon_log(){sync_ajax('%(url)s', [], '%(id)s', function(){});}"""%dict(
               id='tab9_'+str(rowid),
               rid=str(rowid),
               rowid='avail_'+rowid,
               url=URL(r=request, c='svcmon_log', f='ajax_svcmon_log_1',
                       vars={'svcname':request.vars.node, 'rowid':'avail_'+rowid})
            ),
            """function s%(rid)s_load_wiki(){wiki("%(id)s", {"nodes": "%(node)s"})}"""%dict(
               id='tab8_'+str(rowid),
               rid=str(rowid),
               node=request.vars.node,
            ),
            "function s%(rid)s_load_containerprf() {sync_ajax('%(url)s', ['containerprf_begin_%(id)s', 'containerprf_end_%(id)s'], 'containerprf_%(id)s', function(){})};"%dict(
               id=str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='stats', f='ajax_containerperf_plot?node=%s'%','.join(containers)),
            ),
            "function s%(rid)s_load_grpprf() {sync_ajax('%(url)s', ['grpprf_begin_%(id)s', 'grpprf_end_%(id)s'], 'grpprf_%(id)s', function(){})};"%dict(
               id=str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='stats', f='ajax_perfcmp_plot?node=%s'%','.join(str(s['svc_nodes']).split()+str(s['svc_drpnodes']).split())),
            ),
            "function s%(rid)s_load_pkgdiff(){svc_pkgdiff('%(id)s', %(options)s)}"%dict(
               id='tab10_'+str(rowid),
               rid=str(rowid),
               options=str({"svcnames": request.vars.node})
            ),
            "function s%(rid)s_load_comp(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab11_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='compliance', f='ajax_compliance_svc',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_topo(){topology('%(id)s', %(options)s)}"%dict(
               id='tab5_'+str(rowid),
               rid=str(rowid),
               options=str({
                 "svcnames": [
                   request.vars.node
                 ],
                 "display": [
                   "nodes",
                   "services",
                   "countries",
                   "cities",
                   "buildings",
                   "rooms",
                   "racks",
                   "enclosures",
                   "hvs",
                   "hvpools",
                   "hvvdcs",
                   "disks"
                 ]
               })
            ),
            "function s%(rid)s_load_startup(){startup('%(id)s', %(options)s)}"%dict(
               id='tab16_'+str(rowid),
               rid=str(rowid),
               options=str({"svcnames": [request.vars.node]})
            ),
            "function s%(rid)s_load_stor(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab6_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_node', f='ajax_svc_stor',
                       args=['tab6_'+str(rowid), request.vars.node])
            ),
            "function s%(rid)s_load_alerts(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab13_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='dashboard', f='dashboard_svc',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_log(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab15_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='log', f='log_svc',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_actions(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab14_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='svcactions', f='actions_svc',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_svcmon(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab2_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='default', f='svcmon_svc',
                       args=['tab2_'+str(rowid), request.vars.node])
            ),
            "function s%(rid)s_load_resmon(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab3_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='resmon', f='resmon_svc',
                       args=['tab3_'+str(rowid), request.vars.node])
            ),
            """bind_tabs("%(id)s", {
                 "litab1_%(id)s": s%(id)s_load_service_properties,
                 "litab2_%(id)s": s%(id)s_load_svcmon,
                 "litab3_%(id)s": s%(id)s_load_resmon,
                 "litab4_%(id)s": s%(id)s_load_service_env,
                 "litab5_%(id)s": s%(id)s_load_topo,
                 "litab6_%(id)s": s%(id)s_load_stor,
                 "litab7_%(id)s": s%(id)s_load_grpprf,
                 "litab12_%(id)s": s%(id)s_load_containerprf,
                 "litab13_%(id)s": s%(id)s_load_alerts,
                 "litab14_%(id)s": s%(id)s_load_actions,
                 "litab15_%(id)s": s%(id)s_load_log,
                 "litab16_%(id)s": s%(id)s_load_startup,
                 "litab8_%(id)s": s%(id)s_load_wiki,
                 "litab9_%(id)s": s%(id)s_load_svcmon_log,
                 "litab10_%(id)s": s%(id)s_load_pkgdiff,
                 "litab11_%(id)s": s%(id)s_load_comp
               }, "%(tab)s")
            """%dict(id=str(rowid), tab="li"+tab+"_"+str(rowid)),
          ),
        ),
      ),
    )
    return t

class ex(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


#
# services view
#
################

class table_svcmon(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
            'mon_svcname',
            'err',
            'svc_ha',
            'svc_availstatus',
            'svc_status',
            'svc_app',
            'app_domain',
            'app_team_ops',
            'svc_drptype',
            'svc_containertype',
            'svc_flex_min_nodes',
            'svc_flex_max_nodes',
            'svc_flex_cpu_low_threshold',
            'svc_flex_cpu_high_threshold',
            'svc_autostart',
            'svc_nodes',
            'svc_drpnode',
            'svc_drpnodes',
            'svc_comment',
            'svc_created',
            'svc_updated',
            'svc_type',
            'svc_cluster_type',
            'mon_vmtype',
            'mon_vmname',
            'mon_vcpus',
            'mon_vmem',
            'mon_guestos',
            'environnement',
            'host_mode',
            'mon_nodname',
            'mon_availstatus',
            'mon_overallstatus',
            'mon_frozen',
            'mon_containerstatus',
            'mon_ipstatus',
            'mon_fsstatus',
            'mon_diskstatus',
            'mon_sharestatus',
            'mon_syncstatus',
            'mon_appstatus',
            'mon_hbstatus',
            'mon_updated',
            'version',
            'listener_port',
            'team_responsible',
            'team_integ',
            'team_support',
            'project',
            'serial',
            'model',
            'role',
            'warranty_end',
            'status',
            'type',
            'node_updated',
            'power_supply_nb',
            'power_cabinet1',
            'power_cabinet2',
            'power_protect',
            'power_protect_breaker',
            'power_breaker1',
            'power_breaker2',
            'loc_country',
            'loc_zip',
            'loc_city',
            'loc_addr',
            'loc_building',
            'loc_floor',
            'loc_room',
            'loc_rack',
            'os_name',
            'os_release',
            'os_vendor',
            'os_arch',
            'os_kernel',
            'cpu_dies',
            'cpu_cores',
            'cpu_model',
            'cpu_freq',
            'mem_banks',
            'mem_slots',
            'mem_bytes',
        ]
        self.force_cols = [
            'mon_svcname',
            'svc_autostart',
            'mon_guestos',
            'mon_nodname',
            'mon_containerstatus',
            'mon_ipstatus',
            'mon_fsstatus',
            'mon_diskstatus',
            'mon_sharestatus',
            'mon_syncstatus',
            'mon_appstatus',
            'mon_hbstatus',
            'os_name',
        ]
        self.colprops = {
            'err': HtmlTableColumn(
                     title = 'Action errors',
                     field='err',
                     display = True,
                     img = 'action16',
                     _class= 'svc_action_err',
                    ),
            'app_domain': HtmlTableColumn(
                     title='App domain',
                     field='app_domain',
                     img='svc',
                     display=False,
                    ),
            'app_team_ops': HtmlTableColumn(
                     title='Ops team',
                     field='app_team_ops',
                     img='guys16',
                     display=False,
                    ),
        }
        self.colprops.update(svcmon_colprops)
        self.colprops.update(v_services_colprops)
        self.colprops.update(v_nodes_colprops)
        self.colprops['svc_updated'].field = 'svc_updated'
        for i in self.cols:
            self.colprops[i].table = 'v_svcmon'
            self.colprops[i].t = self
        for i in ['mon_nodname', 'mon_svcname', 'svc_containertype', 'svc_app',
                  'svc_type', 'host_mode', 'mon_overallstatus',
                  'mon_availstatus', 'mon_syncstatus']:
            self.colprops[i].display = True
        self.keys = ["mon_nodname", "mon_svcname", "mon_vmname"]
        self.span = ['mon_svcname'] + v_services_cols
        self.span.append('app_domain')
        self.span.append('app_team_ops')
        self.dataable = True
        self.wsable = True
        self.extraline = True
        self.extrarow = True
        self.extrarow_class = "svcmon_links"
        self.checkboxes = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'v_svcmon'
        self.ajax_col_values = 'ajax_svcmon_col_values'
        self.user_name = user_name()
        self.additional_tools.append('tool_provisioning')
        self.additional_tools.append('svc_del')


    def svc_del(self):
        d = DIV(
              A(
                T("Delete instance"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['svc_del']),
                   text=T("Please confirm service instances deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def tool_provisioning(self):
        d = DIV(
              A(
                T("Provisioning"),
                _class='prov',
                _onclick="""$('#prov_container').toggle();ajax('%(url)s', [], '%(id)s')"""%dict(
                  url=URL(r=request, c='provisioning', f='prov_list'),
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
def svc_del(ids):
    groups = user_groups()

    q = db.svcmon.id.belongs(ids)
    if 'Manager' not in groups:
        # Manager can delete any svc
        # A user can delete only services he is responsible of
        l1 = db.services.on(db.svcmon.mon_svcname == db.services.svc_name)
        l2 = db.apps.on(db.services.svc_app == db.apps.app)
        l3 = db.apps_responsibles.on(db.apps.id == db.apps_responsibles.app_id)
        l4 = db.auth_group.on(db.apps_responsibles.group_id == db.auth_group.id)
        q &= (db.auth_group.role.belongs(groups)) | (db.auth_group.role==None)
        ids = map(lambda x: x.id, db(q).select(db.svcmon.id, left=(l1,l2,l3,l4), cacheable=True))
        q = db.svcmon.id.belongs(ids)
    rows = db(q).select(cacheable=True)
    for r in rows:
        q = db.svcmon.id == r.id
        db(q).delete()
        _log('service.delete',
             'deleted service instance %(u)s',
              dict(u='@'.join((r.mon_svcname, r.mon_nodname))),
             svcname=r.mon_svcname,
             nodename=r.mon_nodname)
        purge_svc(r.mon_svcname)
    if len(rows) > 0:
        _websocket_send(event_msg({
             'event': 'svcmon_change',
             'data': {'f': 'b'},
            }))


@auth.requires_login()
def ajax_svcmon_col_values():
    t = table_svcmon('svcmon', 'ajax_svcmon')
    col = request.args[0]
    o = db.v_svcmon[col]
    q = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    q = apply_filters(q, db.v_svcmon.mon_nodname, db.v_svcmon.mon_svcname)
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    t.object_list = db(q).select(db.v_svcmon[col], orderby=o,
                                 limitby=default_limitby,
                                 cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_svcmon():
    t = table_svcmon('svcmon', 'ajax_svcmon')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'svc_del':
                svc_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = db.v_svcmon.mon_svcname
    o |= db.v_svcmon.mon_nodname

    q = _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_filters(q, db.v_svcmon.mon_nodname, db.v_svcmon.mon_svcname)
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)

    t.csv_q = q
    t.csv_orderby = o
    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)


@auth.requires_login()
def svcmon():
    t = table_svcmon('svcmon', 'ajax_svcmon')
    t = DIV(
          t.html(),
          SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "svcmon_change") {
          osvc.tables["%(divid)s"].refresh()
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
           """ % dict(
                  divid=t.innerhtml,
                 )
          ),
          _id='svcmon',
        )
    return dict(table=t)

def svcmon_load():
    return svcmon()["table"]

class table_svcmon_node(table_svcmon):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_svcmon.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.checkboxes = True
        self.extrarow = True
        self.wsable = False
        self.colprops['mon_updated'].display = True

@auth.requires_login()
def svcmon_node():
    node = request.args[0]
    tid = 'svcmon_'+node.replace('-', '_').replace('.', '_')
    t = table_svcmon_node(tid, 'ajax_svcmon_node')
    t.colprops['mon_nodname'].force_filter = node
    return DIV(
             t.html(),
             _id=tid
           )

@auth.requires_login()
def ajax_svcmon_node():
    tid = request.vars.table_id
    t = table_svcmon_node(tid, 'ajax_svcmon_node')
    q = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    for f in ['mon_nodname']:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

class table_svcmon_svc(table_svcmon):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_svcmon.__init__(self, id, func, innerhtml)
        self.cols = [
         'svc_ha',
         'svc_availstatus',
         'svc_status',
         'svc_cluster_type',
         'mon_vmtype',
         'mon_vmname',
         'mon_nodname',
         'mon_availstatus',
         'mon_overallstatus',
         'mon_ipstatus',
         'mon_fsstatus',
         'mon_diskstatus',
         'mon_appstatus',
         'mon_sharestatus',
         'mon_containerstatus',
         'mon_hbstatus',
         'mon_syncstatus',
         'mon_updated',
        ]
        self.colprops['mon_updated'].display = True

        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.checkboxes = False
        self.extrarow = False
        self.wsable = False


@auth.requires_login()
def svcmon_svc():
    tid = request.args[0]
    svcname = request.args[1]
    t = table_svcmon_svc(tid, 'ajax_svcmon_svc')
    t.colprops['mon_svcname'].force_filter = svcname
    return t.html()

@auth.requires_login()
def ajax_svcmon_svc():
    tid = request.vars.table_id
    t = table_svcmon_svc(tid, 'ajax_svcmon_svc')
    q = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    for f in ['mon_svcname']:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)
