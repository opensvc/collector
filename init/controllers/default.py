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
    extra = ""
    if len(request.args) > 0:
        if request.args[0] in auth.settings.actions_disabled:
            return dict(form=T("Feature Disabled"), extra=extra)
        if request.args[-1] == "google":
            auth.settings.login_form = googleAccount()
        if request.args[0] == "login" and auth_google:
            extra = DIV(
                BR(),
                H2(T("Or")),
                A(
                    IMG(
                        _src=URL(c="static",f="images/btn_google_signin_light_normal_web.png"),
                    ),
                    _class="p-3 clickable",
                    _href=URL(args=["login", "google"]),
                )
            )

    try:
        form = auth()
        return dict(form=form, extra=extra)
    except HTTP as e:
        if str(e) in ("404", "500"):
            return dict(form=str(e), extra=extra)
        raise
    except Exception as e:
        return dict(form=str(e), extra=extra)

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
            'id',
            'svc_id',
            'svcname',
            'err',
            'svc_ha',
            'svc_availstatus',
            'svc_status',
            'svc_app',
            'app_domain',
            'app_team_ops',
            'svc_drptype',
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
            'svc_env',
            'svc_topology',
            'mon_vmtype',
            'mon_vmname',
            'mon_vcpus',
            'mon_vmem',
            'mon_guestos',
            'asset_env',
            'node_env',
            'node_id',
            'nodename',
            'mon_availstatus',
            'mon_overallstatus',
            'mon_frozen',
            'mon_monstatus',
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
            'collector',
            'connect_to',
            'team_responsible',
            'team_integ',
            'team_support',
            'serial',
            'model',
            'bios_version',
            'sp_version',
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
            'tz',
            'hv',
            'hvpool',
            'hvvdc',
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
        self.colprops = {
            'id': HtmlTableColumn(
                     field='id',
                    ),
            'svcname': HtmlTableColumn(
                     field='svcname',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                    ),
            'err': HtmlTableColumn(
                     field='err',
                    ),
            'app_domain': HtmlTableColumn(
                     field='app_domain',
                    ),
            'app_team_ops': HtmlTableColumn(
                     field='app_team_ops',
                    ),
        }
        self.colprops.update(svcmon_colprops)
        self.colprops.update(services_colprops)
        self.colprops.update(nodes_colprops)
        self.colprops['svc_updated'].field = 'svc_updated'
        for i in self.cols:
            self.colprops[i].table = 'v_svcmon'
        self.ajax_col_values = 'ajax_svcmon_col_values'

@auth.requires_login()
def ajax_svcmon_col_values():
    table_id = request.vars.table_id
    t = table_svcmon(table_id, 'ajax_svcmon')
    col = request.args[0]
    o = db.v_svcmon[col]
    q = q_filter(app_field=db.v_svcmon.svc_app)
    q = apply_filters_id(q, db.v_svcmon.node_id, db.v_svcmon.svc_id)
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    t.object_list = db(q).select(db.v_svcmon[col], orderby=o,
                                 cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_svcmon():
    table_id = request.vars.table_id
    t = table_svcmon(table_id, 'ajax_svcmon')

    o = t.get_orderby(default=db.v_svcmon.svcname|db.v_svcmon.nodename)

    q = q_filter(app_field=db.v_svcmon.svc_app)
    q = apply_filters_id(q, db.v_svcmon.node_id, db.v_svcmon.svc_id)
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
    t = SCRIPT(
          """table_service_instances("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def svcmon_load():
    return svcmon()["table"]


