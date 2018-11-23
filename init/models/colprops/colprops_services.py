services_cols = [
    'cluster_id',
    'svc_status',
    'svc_availstatus',
    'svc_app',
    'svc_env',
    'svc_ha',
    'svc_topology',
    'svc_frozen',
    'svc_placement',
    'svc_provisioned',
    'svc_flex_min_nodes',
    'svc_flex_max_nodes',
    'svc_flex_cpu_low_threshold',
    'svc_flex_cpu_high_threshold',
    'svc_drptype',
    'svc_autostart',
    'svc_nodes',
    'svc_drpnode',
    'svc_drpnodes',
    'svc_comment',
    'svc_created',
    'svc_updated',
    'svc_notifications',
    'svc_snooze_till',
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
    'mon_smon_status',
    'mon_smon_global_expect',
    'mon_monstatus',
    'mon_containerstatus',
    'mon_ipstatus',
    'mon_fsstatus',
    'mon_diskstatus',
    'mon_sharestatus',
    'mon_syncstatus',
    'mon_appstatus',
    'mon_hbstatus'
]

services_colprops = {
    'cluster_id': HtmlTableColumn(
             field='cluster_id',
             table = 'cluster_id',
            ),
    'svcname': HtmlTableColumn(
             field='svcname',
             table = 'services',
            ),
    'svc_hostid': HtmlTableColumn(
             field='svc_hostid',
             table = 'services',
            ),
    'svc_wave': HtmlTableColumn(
             field='svc_wave',
             table = 'services',
            ),
    'svc_availstatus': HtmlTableColumn(
             field='svc_availstatus',
             table = 'services',
            ),
    'svc_status': HtmlTableColumn(
             field='svc_status',
             table = 'services',
            ),
    'svc_frozen': HtmlTableColumn(
             field='svc_frozen',
             table = 'services',
            ),
    'svc_placement': HtmlTableColumn(
             field='svc_placement',
             table = 'services',
            ),
    'svc_provisioned': HtmlTableColumn(
             field='svc_provisioned',
             table = 'services',
            ),
    'svc_app': HtmlTableColumn(
             field='svc_app',
             table = 'services',
            ),
    'svc_ha': HtmlTableColumn(
             field='svc_ha',
             table = 'services',
            ),
    'svc_env': HtmlTableColumn(
             field='svc_env',
             table = 'services',
            ),
    'svc_autostart': HtmlTableColumn(
             field='svc_autostart',
             table = 'services',
            ),
    'svc_nodes': HtmlTableColumn(
             field='svc_nodes',
             table = 'services',
            ),
    'svc_drpnode': HtmlTableColumn(
             field='svc_drpnode',
             table = 'services',
            ),
    'svc_drpnodes': HtmlTableColumn(
             field='svc_drpnodes',
             table = 'services',
            ),
    'svc_drptype': HtmlTableColumn(
             field='svc_drptype',
             table = 'services',
            ),
    'svc_comment': HtmlTableColumn(
             field='svc_comment',
             table = 'services',
            ),
    'svc_created': HtmlTableColumn(
             field='svc_created',
             table = 'services',
            ),
    'svc_updated': HtmlTableColumn(
             field='updated',
             table = 'services',
            ),
    'svc_status_updated': HtmlTableColumn(
             table='services',
             field='svc_status_updated',
            ),
    'svc_topology': HtmlTableColumn(
             field='svc_topology',
             table = 'services',
            ),
    'svc_flex_min_nodes': HtmlTableColumn(
             field='svc_flex_min_nodes',
             table = 'services',
            ),
    'svc_flex_max_nodes': HtmlTableColumn(
             field='svc_flex_max_nodes',
             table = 'services',
            ),
    'svc_flex_cpu_low_threshold': HtmlTableColumn(
             field='svc_flex_cpu_low_threshold',
             table = 'services',
            ),
    'svc_flex_cpu_high_threshold': HtmlTableColumn(
             field='svc_flex_cpu_high_threshold',
             table = 'services',
            ),
    'svc_config': HtmlTableColumn(
             field='svc_config',
             table = 'services',
            ),
    'svc_config_updated': HtmlTableColumn(
             field='svc_config_updated',
             table = 'services',
            ),
    'svc_notifications': HtmlTableColumn(
             field='svc_notifications',
             table = 'services',
            ),
    'svc_snooze_till': HtmlTableColumn(
             field='svc_snooze_till',
             table = 'services',
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
    'svc_id': HtmlTableColumn(
             field='svc_id',
             table = 'svcmon',
            ),
    'node_id': HtmlTableColumn(
             field='node_id',
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
    'mon_smon_status': HtmlTableColumn(
             field='mon_smon_status',
             table = 'svcmon',
            ),
    'mon_smon_global_expect': HtmlTableColumn(
             field='mon_smon_global_expect',
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
    'mon_monstatus': HtmlTableColumn(
             field='mon_monstatus',
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


