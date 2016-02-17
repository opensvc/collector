function table_service_instances(divid, options) {
	var defaults = {
		'caller': 'table_service_instances',
		'id': 'svcmon',
		'divid': divid,
		'name': 'service_instances',
		'extrarow': true,
		'extrarow_class': "svcmon_links",
		'ajax_url': '/init/default/ajax_svcmon',
		'span': ['mon_svcname', 'svc_status', 'svc_availstatus', 'svc_app', 'svc_type', 'svc_ha', 'svc_cluster_type', 'svc_flex_min_nodes', 'svc_flex_max_nodes', 'svc_flex_cpu_low_threshold', 'svc_flex_cpu_high_threshold', 'svc_drptype', 'svc_containertype', 'svc_autostart', 'svc_nodes', 'svc_drpnode', 'svc_drpnodes', 'svc_comment', 'svc_created', 'svc_updated', 'app_domain', 'app_team_ops'],
		'columns': ['id', 'mon_svcname', 'err', 'svc_ha', 'svc_availstatus', 'svc_status', 'svc_app', 'app_domain', 'app_team_ops', 'svc_drptype', 'svc_containertype', 'svc_flex_min_nodes', 'svc_flex_max_nodes', 'svc_flex_cpu_low_threshold', 'svc_flex_cpu_high_threshold', 'svc_autostart', 'svc_nodes', 'svc_drpnode', 'svc_drpnodes', 'svc_comment', 'svc_created', 'svc_updated', 'svc_type', 'svc_cluster_type', 'mon_vmtype', 'mon_vmname', 'mon_vcpus', 'mon_vmem', 'mon_guestos', 'environnement', 'host_mode', 'mon_nodname', 'mon_availstatus', 'mon_overallstatus', 'mon_frozen', 'mon_containerstatus', 'mon_ipstatus', 'mon_fsstatus', 'mon_diskstatus', 'mon_sharestatus', 'mon_syncstatus', 'mon_appstatus', 'mon_hbstatus', 'mon_updated', 'version', 'listener_port', 'team_responsible', 'team_integ', 'team_support', 'project', 'serial', 'model', 'role', 'warranty_end', 'status', 'type', 'node_updated', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes'],
		'default_columns': [
			"err",
			"host_mode",
			"mon_availstatus",
			"mon_overallstatus",
			"mon_svcname",
			"mon_updated",
			"mon_vmname",
			"mon_vmtype",
			"svc_app",
			"svc_availstatus",
			"svc_cluster_type",
			"svc_containertype",
			"svc_ha",
			"svc_status",
			"svc_type"
		],
		'force_cols': [
			'id',
			'mon_svcname',
			'mon_frozen',
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
			'mon_updated',
			'os_name',
		],
		'wsable': true,
		'events': ['svcmon_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_service_instances_node(divid, nodename) {
	var id = "svcmon_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_mon_nodname"
	var request_vars = {}
	request_vars[f] = nodename
	table_service_instances(divid, {
		"id": id,
		"caller": "table_service_instances_node",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"visible_columns": [
			'mon_svcname',
			'svc_ha',
			'svc_cluster_type',
			'mon_vmtype',
			'mon_vmname',
			'mon_availstatus',
			'mon_overallstatus',
			'mon_updated'
		]
	})
}

function table_service_instances_svc(divid, svcname) {
	var id = "svcmon_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_mon_svcname"
	var request_vars = {}
	request_vars[f] = svcname
	table_service_instances(divid, {
		"id": id,
		"caller": "table_service_instances_svc",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"visible_columns": [
			'svc_ha',
			'svc_cluster_type',
			'mon_nodname',
			'mon_vmtype',
			'mon_vmname',
			'mon_availstatus',
			'mon_overallstatus',
			'mon_updated'
		]
	})
}
