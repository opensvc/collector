v_services_cols = [
    'svc_status',
    'svc_availstatus',
    'svc_app',
    'svc_type',
    'svc_ha',
    'svc_cluster_type',
    'svc_flex_min_nodes',
    'svc_flex_max_nodes',
    'svc_flex_cpu_low_threshold',
    'svc_flex_cpu_high_threshold',
    'svc_drptype',
    'svc_containertype',
    'svc_autostart',
    'svc_nodes',
    'svc_drpnode',
    'svc_drpnodes',
    'svc_comment',
    'svc_created',
    'svc_updated',
]

svcmon_cols = [
    'mon_vmname',
    'mon_vmtype',
    'mon_guestos',
    'mon_vcpus',
    'mon_vmem',
    'mon_overallstatus',
    'mon_availstatus',
    'mon_updated',
    'mon_changed',
    'mon_frozen',
    'mon_containerstatus',
    'mon_ipstatus',
    'mon_fsstatus',
    'mon_diskstatus',
    'mon_sharestatus',
    'mon_syncstatus',
    'mon_appstatus',
    'mon_hbstatus'
]

v_services_colprops = {
    'svc_name': HtmlTableColumn(
             field='svc_name',
             table = 'v_services',
            ),
    'svc_hostid': HtmlTableColumn(
             field='svc_hostid',
             table = 'v_services',
            ),
    'svc_wave': HtmlTableColumn(
             field='svc_wave',
             table = 'v_services',
            ),
    'svc_availstatus': HtmlTableColumn(
             field='svc_availstatus',
             table = 'v_services',
            ),
    'svc_status': HtmlTableColumn(
             field='svc_status',
             table = 'v_services',
            ),
    'svc_app': HtmlTableColumn(
             field='svc_app',
             table = 'v_services',
            ),
    'svc_ha': HtmlTableColumn(
             field='svc_ha',
             table = 'v_services',
            ),
    'svc_containertype': HtmlTableColumn(
             field='svc_containertype',
             table = 'v_services',
            ),
    'svc_type': HtmlTableColumn(
             field='svc_type',
             table = 'v_services',
            ),
    'svc_autostart': HtmlTableColumn(
             field='svc_autostart',
             table = 'v_services',
            ),
    'svc_nodes': HtmlTableColumn(
             field='svc_nodes',
             table = 'v_services',
            ),
    'svc_drpnode': HtmlTableColumn(
             field='svc_drpnode',
             table = 'v_services',
            ),
    'svc_drpnodes': HtmlTableColumn(
             field='svc_drpnodes',
             table = 'v_services',
            ),
    'svc_drptype': HtmlTableColumn(
             field='svc_drptype',
             table = 'v_services',
            ),
    'svc_comment': HtmlTableColumn(
             field='svc_comment',
             table = 'v_services',
            ),
    'svc_created': HtmlTableColumn(
             field='svc_created',
             table = 'v_services',
            ),
    'svc_updated': HtmlTableColumn(
             field='updated',
             table = 'v_services',
            ),
    'svc_status_updated': HtmlTableColumn(
             table='services',
             field='svc_status_updated',
            ),
    'responsibles': HtmlTableColumn(
             field='responsibles',
             table = 'v_services',
            ),
    'mailto': HtmlTableColumn(
             field='mailto',
             table = 'v_services',
            ),
    'svc_cluster_type': HtmlTableColumn(
             field='svc_cluster_type',
             table = 'v_services',
            ),
    'svc_flex_min_nodes': HtmlTableColumn(
             field='svc_flex_min_nodes',
             table = 'v_services',
            ),
    'svc_flex_max_nodes': HtmlTableColumn(
             field='svc_flex_max_nodes',
             table = 'v_services',
            ),
    'svc_flex_cpu_low_threshold': HtmlTableColumn(
             field='svc_flex_cpu_low_threshold',
             table = 'v_services',
            ),
    'svc_flex_cpu_high_threshold': HtmlTableColumn(
             field='svc_flex_cpu_high_threshold',
             table = 'v_services',
            ),
    'svc_envfile': HtmlTableColumn(
             field='svc_envfile',
             table = 'v_services',
            ),
    'svc_envdate': HtmlTableColumn(
             field='svc_envdate',
             table = 'v_svcmon',
            ),
}

v_svcmon_colprops = {
    'err': HtmlTableColumn(
             field='err',
             table = 'v_svcmon',
            ),
}

svcmon_colprops = {
    'mon_containerpath': HtmlTableColumn(
             field='mon_containerpath',
             table = 'svcmon',
            ),
    'mon_svcname': HtmlTableColumn(
             field='mon_svcname',
             table = 'svcmon',
            ),
    'mon_nodname': HtmlTableColumn(
             field='mon_nodname',
             table = 'svcmon',
            ),
    'mon_svctype': HtmlTableColumn(
             field='mon_svctype',
             table = 'svcmon',
            ),
    'mon_overallstatus': HtmlTableColumn(
             field='mon_overallstatus',
             table = 'svcmon',
            ),
    'mon_changed': HtmlTableColumn(
             field='mon_changed',
             table = 'svcmon',
            ),
    'mon_updated': HtmlTableColumn(
             field='mon_updated',
             table = 'svcmon',
            ),
    'mon_frozen': HtmlTableColumn(
             field='mon_frozen',
             table = 'svcmon',
            ),
    'mon_containerstatus': HtmlTableColumn(
             field='mon_containerstatus',
             table = 'svcmon',
            ),
    'mon_availstatus': HtmlTableColumn(
             field='mon_availstatus',
             table = 'svcmon',
            ),
    'mon_ipstatus': HtmlTableColumn(
             field='mon_ipstatus',
             table = 'svcmon',
            ),
    'mon_fsstatus': HtmlTableColumn(
             field='mon_fsstatus',
             table = 'svcmon',
            ),
    'mon_sharestatus': HtmlTableColumn(
             field='mon_sharestatus',
             table = 'svcmon',
            ),
    'mon_diskstatus': HtmlTableColumn(
             field='mon_diskstatus',
             table = 'svcmon',
            ),
    'mon_syncstatus': HtmlTableColumn(
             field='mon_syncstatus',
             table = 'svcmon',
            ),
    'mon_appstatus': HtmlTableColumn(
             field='mon_appstatus',
             table = 'svcmon',
            ),
    'mon_hbstatus': HtmlTableColumn(
             field='mon_hbstatus',
             table = 'svcmon',
            ),
    'mon_vmname': HtmlTableColumn(
             field='mon_vmname',
             table = 'svcmon',
            ),
    'mon_vmtype': HtmlTableColumn(
             field='mon_vmtype',
             table = 'svcmon',
            ),
    'mon_vcpus': HtmlTableColumn(
             field='mon_vcpus',
             table = 'svcmon',
            ),
    'mon_vmem': HtmlTableColumn(
             field='mon_vmem',
             table = 'svcmon',
            ),
    'mon_guestos': HtmlTableColumn(
             field='mon_guestos',
             table = 'svcmon',
            ),
}


