//
function table_comp_rulesets_nodes(divid, options) {
	var defaults = {
		'id': "crn",
		'caller': "table_comp_rulesets_nodes",
		'name': "comp_rulesets_nodes",
		'divid': divid,
		'ajax_url': '/init/compliance/ajax_comp_rulesets_nodes',
		'span': ['nodename'],
		'force_cols': ['os_name', 'ruleset_id'],
		'columns': ['nodename', 'ruleset_id', 'ruleset_name', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
		'default_columns': ["nodename", "ruleset_name"],
		'colprops': {
			"ruleset_id": {"img": "key"}
		},
		'wsable': false,
		'events': ['comp_rulesets_nodes_change']
	}

	var _options = $.extend({}, defaults, options)

	wsh[_options.id] = function(data) {
		if (data["event"] == "comp_rulesets_nodes_change") {
			_data = []
			_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
			osvc.tables[_options.id].insert(_data)
		}
	}

	return table_init(_options)
}

//
function table_comp_modulesets_nodes(divid, options) {
	var defaults = {
		'name': "comp_modulesets_nodes",
		'id': "cmn",
		'caller': "table_comp_modulesets_nodes",
		'divid': divid,
		'ajax_url': '/init/compliance/ajax_comp_modulesets_nodes',
		'span': ['nodename'],
		'force_cols': ['os_name', 'modset_id'],
		'columns': ['nodename', 'modset_id', 'modset_name', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
		'default_columns': ["nodename", "modset_name"],
		'wsable': false,
		'events': ['comp_node_moduleset_change']
	}

	var _options = $.extend({}, defaults, options)

	wsh[_options.id] = function(data) {
		if (data["event"] == "comp_modulesets_nodes_change") {
			_data = []
			_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
			osvc.tables[_options.id].insert(_data)
		}
	}

	return table_init(_options)
}

//
function table_comp_rulesets_services(divid, options) {
	defaults = {
		'name': "comp_rulesets_services",
		'id': "crs",
		'caller': "table_comp_rulesets_services",
		'divid': divid,
		'ajax_url': '/init/compliance/ajax_comp_rulesets_services',
		'span': ['svc_name'],
		'force_cols': ['svc_name', 'encap', 'ruleset_id', 'svc_status_updated'],
		'columns': ['svc_name', 'encap', 'ruleset_id', 'ruleset_name', 'svc_status', 'svc_availstatus', 'svc_app', 'svc_type', 'svc_ha', 'svc_cluster_type', 'svc_flex_min_nodes', 'svc_flex_max_nodes', 'svc_flex_cpu_low_threshold', 'svc_flex_cpu_high_threshold', 'svc_drptype', 'svc_containertype', 'svc_autostart', 'svc_nodes', 'svc_drpnode', 'svc_drpnodes', 'svc_comment', 'svc_created', 'svc_updated', 'svc_status_updated'],
		'default_columns': ["svc_name", "encap", "ruleset_name"],
		'colprops': {
			"ruleset_id": {"img": "key"}
		},
		'wsable': false,
		'events': ['comp_rulesets_services_change']
	}

	var _options = $.extend({}, defaults, options)

	wsh[_options.id] = function(data) {
		if (data["event"] == "comp_rulesets_services_change") {
			_data = []
			_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
			osvc.tables[_options.id].insert(_data)
		}
	}

	return table_init(_options)
}

//
function table_comp_modulesets_services(divid, options) {
	var defaults = {
		'id': "cms",
		'divid': divid,
		'caller': "table_comp_modulesets_services",
		'name': "comp_modulesets_services",
		'ajax_url': '/init/compliance/ajax_comp_modulesets_services',
		'span': ['svc_name'],
		'force_cols': ['svc_name', 'encap', 'modset_id', 'svc_status_updated'],
		'columns': ['svc_name', 'encap', 'modset_id', 'modset_name', 'svc_status', 'svc_availstatus', 'svc_app', 'svc_type', 'svc_ha', 'svc_cluster_type', 'svc_flex_min_nodes', 'svc_flex_max_nodes', 'svc_flex_cpu_low_threshold', 'svc_flex_cpu_high_threshold', 'svc_drptype', 'svc_containertype', 'svc_autostart', 'svc_nodes', 'svc_drpnode', 'svc_drpnodes', 'svc_comment', 'svc_created', 'svc_updated', 'svc_status_updated'],
		'default_columns': ["svc_name", "encap", "modset_name"],
		'wsable': false,
		'events': ['comp_modulesets_services_change']
	}

	var _options = $.extend({}, defaults, options)

	wsh[_options.id] = function(data) {
		if (data["event"] == "comp_modulesets_services_change") {
			_data = []
			_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
			osvc.tables[_options.id].insert(_data)
		}
	}

	return table_init(_options)
}

