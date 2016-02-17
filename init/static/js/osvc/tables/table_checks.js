function table_checks(divid, options) {
	var defaults = {
		'divid': divid,
		'id': 'checks',
		'caller': 'table_checks',
		'name': 'checks',
		'ajax_url': '/init/checks/ajax_checks',
		'span': ['chk_nodename'],
		'columns': ['chk_nodename', 'chk_svcname', 'chk_type', 'chk_instance', 'chk_value', 'chk_low', 'chk_high', 'chk_err', 'chk_threshold_provider', 'chk_created', 'chk_updated', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'app_team_ops', 'team_support', 'project', 'app_domain', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
		'default_columns': ["chk_err", "chk_high", "chk_instance", "chk_low", "chk_nodename", "chk_svcname", "chk_threshold_provider", "chk_type", "chk_updated", "chk_value"],
		'wsable': true,
		'force_cols': [
			'os_name',
			'chk_type',
			'chk_instance',
			'chk_value',
			'chk_high',
			'chk_low'
		],
		'events': ['checks_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_checks_node(divid, nodename) {
	var id = "checks_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_chk_nodename"
	var request_vars = {}
	request_vars[f] = nodename
	table_checks(divid, {
		"id": id,
		"caller": "table_checks_node",
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
			'chk_svcname',
			'chk_type',
			'chk_instance',
			'chk_value',
			'chk_low', 
			'chk_high',
			'chk_err',
			'chk_threshold_provider',
			'chk_created',
			'chk_updated'
		]
	})
}

function table_checks_svc(divid, svcname) {
	var id = "checks_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_chk_svcname"
	var request_vars = {}
	request_vars[f] = svcname
	table_checks(divid, {
		"id": id,
		"caller": "table_checks_svc",
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
			'chk_nodename',
			'chk_type',
			'chk_instance',
			'chk_value',
			'chk_low', 
			'chk_high',
			'chk_err',
			'chk_threshold_provider',
			'chk_created',
			'chk_updated'
		]
	})
}
