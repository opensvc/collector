function table_action_queue(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': 'table_action_queue',
		'id': 'action_queue',
		'name': 'action_queue',
		'ajax_url': '/init/action_queue/ajax_actions',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'status', 'nodename', 'svcname', 'connect_to', 'username', 'form_id', 'action_type', 'date_queued', 'date_dequeued', 'ret', 'command', 'stdout', 'stderr'],
		'default_columns': ['status', 'nodename', 'svcname', 'connect_to', 'username', 'form_id', 'action_type', 'date_queued', 'date_dequeued', 'ret', 'command'],
		'colprops': {
			"action_type": {"img": "action16"},
			"status": {
				"_class": "action_q_status",
				"field": "status",
				"img": "action16",
				"title": "Status"
			}
		},
		'wsable': true,
		'events': ['action_q_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_actions(divid, options) {
	var defaults = {
		'name': 'actions',
		'id': 'actions',
		'caller': 'table_actions',
		'divid': divid,
		'ajax_url': '/init/svcactions/ajax_actions',
		'span': ['pid'],
		'force_cols': ['os_name', 'ack', 'acked_by', 'acked_date', 'acked_comment', 'end'],
		'columns': [].concat(['svcname', 'hostname', 'pid', 'action', 'status', 'begin', 'end', 'time', 'id', 'status_log', 'cron', 'ack', 'acked_by', 'acked_date', 'acked_comment'], objcols.node),
		"default_columns": ["svcname", "action", "begin", "cron", "end", "hostname", "pid", "status", "status_log"],
		"colprops": {
			"begin": {
				"_class": "datetime_no_age",
				"_dataclass": "",
				"default_filter": ">-1d",
				"img": "time16",
				"title": "Begin"
			},
			"end": {
				"_class": "action_end",
				"_dataclass": "",
				"img": "time16",
				"title": "End"
			},
			"status": {
				"_class": "action_status",
				"img": "action16",
			}
		},
		'volatile_filters': false,
		'child_tables': [],
		'parent_tables': [],
		'dataable': true,
		'linkable': true,
		'dbfilterable': true,
		'filterable': true,
		'refreshable': true,
		'bookmarkable': true,
		'exportable': true,
		'columnable': true,
		'commonalityable': true,
		'headers': true,
		'wsable': true,
		'pageable': true,
		'on_change': false,
		'events': ['begin_action', 'end_action', 'svcactions_change'],
		'request_vars': {}
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_actions_node(divid, nodename) {
	var id = "actions_" + nodename.replace(/[\.-]/g, "_")
	var f_hostname = id+"_f_hostname"
	var f_begin = id+"_f_begin"
	var request_vars = {}
	request_vars[f_hostname] = nodename
	request_vars[f_begin] = ">-60d"
	return table_actions(divid, {
		"id": id,
		"caller": "table_actions_node",
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
			'svcname',
			'pid',
			'action',
			'status',
			'begin',
			'end',
			'time',
			'id',
			'status_log',
			'cron',
			'ack',
			'acked_by',
			'acked_date',
			'acked_comment'
		]
	})
}

function table_actions_svc(divid, svcname) {
	var id = "actions_" + svcname.replace(/[\.-]/g, "_")
	var f_svcname = id+"_f_svcname"
	var f_begin = id+"_f_begin"
	var perpage = id+"_perpage"
	var request_vars = {}
	request_vars[f_svcname] = svcname
	request_vars[f_begin] = ">-60d"
	return table_actions(divid, {
		"id": id,
		"caller": "table_actions_svc",
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
			'hostname',
			'pid',
			'action',
			'status',
			'begin',
			'end',
			'time',
			'id',
			'status_log',
			'cron',
			'ack',
			'acked_by',
			'acked_date',
			'acked_comment'
		]
	})
}

function table_appinfo(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "appinfo",
		'caller': "table_appinfo",
		'name': "appinfo",
		'ajax_url': '/init/appinfo/ajax_appinfo',
		'span': ['app_svcname', 'app_nodename', 'app_launcher'],
		'columns': ['id', 'app_svcname', 'app_nodename', 'app_launcher', 'app_key', 'app_value', 'app_updated'],
		'default_columns': ['app_svcname', 'app_nodename', 'app_launcher', 'app_key', 'app_value', 'app_updated'],
		'force_cols': ['id'],
		'wsable': true,
		'events': ['appinfo_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_apps(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "apps",
		'caller': "table_apps",
		'name': "apps",
		'ajax_url': '/init/apps/ajax_apps',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': objcols.app,
		'default_columns': [
			"app",
			"app_domain",
			"app_team_ops",
			"roles",
			"responsibles"
		],
		'colprops': {
			"app": {"title": "Application code"}
		},
		'wsable': true,
		'events': ['apps_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

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
			'chk_nodename',
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

function table_comp_log(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "comp_log",
		'caller': "table_comp_log",
		'name': "comp_log",
		'ajax_url': '/init/compliance/ajax_comp_log',
		'span': ['run_date', 'run_nodename', 'run_svcname', 'run_module', 'run_action'],
		'columns': ['run_date', 'run_nodename', 'run_svcname', 'run_module', 'run_action', 'run_status', 'run_log', 'rset_md5'],
		'default_columns': ["run_action", "run_date", "run_module", "run_nodename", "run_status", "run_svcname"],
		'colprops': {
			"run_date": {"default_filter": ">-1d"}
		},
		'wsable': true,
		'events': ['comp_log_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_modules(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "comp_modules",
		'caller': "table_comp_modules",
		'name': "comp_modules",
		'ajax_url': '/init/compliance/ajax_comp_moduleset',
		'span': ['modset_name'],
		'force_cols': ["id"],
		'columns': ['modset_name', 'teams_responsible', 'teams_publication', 'modset_mod_name', 'autofix', 'modset_mod_updated', 'modset_mod_author'],
		'default_columns': ["autofix", "modset_mod_author", "modset_mod_name", "modset_mod_updated", "modset_name", "teams_publication", "teams_responsible"],
		'wsable': true,
		'events': ['comp_moduleset_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_rules(divid, options) {
	var defaults = {
		'id': "cr0",
		'name': "comp_rulesets",
		'caller': "table_comp_rules",
		'divid': divid,
		'ajax_url': '/init/compliance/ajax_comp_rulesets',
		'span': ['ruleset_name', 'ruleset_type', 'ruleset_public', 'fset_name', 'teams_responsible', 'teams_publication'],
		'force_cols': ['id', 'var_class', 'encap_rset', 'ruleset_id'],
		'columns': ['id', 'ruleset_id', 'ruleset_name', 'ruleset_type', 'ruleset_public', 'teams_responsible', 'teams_publication', 'fset_name', 'chain', 'chain_len', 'encap_rset', 'var_class', 'var_name', 'var_value', 'var_updated', 'var_author'],
		'default_columns': ["encap_rset", "fset_name", "ruleset_name", "ruleset_public", "ruleset_type", "teams_publication", "teams_responsible", "var_author", "var_class", "var_name", "var_updated", "var_value"],
		'wsable': true,
		'events': ['comp_rulesets_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_module_status(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "cms",
		'name': "comp_module_status",
		'caller': "table_comp_module_status",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_mod_status',
		'span': ['mod_name'],
		'columns': ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'mod_log'],
		'default_columns': ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'mod_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_node_status(divid, options) {
	var defaults = {
		'id': "cns",
		'divid': divid,
		'caller': "table_comp_node_status",
		'name': "comp_node_status",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_node_status',
		'span': ['node_name'],
		'columns': ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'node_log'],
		'default_columns': ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'node_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_service_status(divid, options) {
	var defaults = {
		'divid': divid,
		'name': "comp_service_status",
		'caller': "table_comp_service_status",
		'id': "css",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_svc_status',
		'span': ['svc_name'],
		'columns': ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'svc_log'],
		'default_columns': ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'svc_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_status(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "cs0",
		'name': "comp_status",
		'caller': "table_comp_status",
		'ajax_url': '/init/compliance/ajax_comp_status',
		'span': ['run_nodename', 'run_svcname', 'run_module'],
		'force_cols': ['id', 'os_name'],
		'columns': ['id', 'run_date', 'run_nodename', 'run_svcname', 'run_module', 'run_status', 'run_status_log', 'rset_md5', 'run_log', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
		'default_columns': ["run_date", "run_module", "run_nodename", "run_status", "run_svcname"],
		'child_tables': ['cms', 'cns', 'css'],
		'wsable': true,
		'events': ['comp_status_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function comp_status_agg(divid, options) {
	var t = options.table
	var data = {
	  "table_id": t.id
	}
	for (c in t.colprops) {
		var current = $("#"+t.id+"_f_"+c).val()
		if ((current != "") && (typeof current !== 'undefined')) {
			data[t.id+"_f_"+c] = current
		} else if (t.colprops[c].force_filter != "") {
			data[t.id+"_f_"+c] = t.colprops[c].force_filter
		}
	}
	$.getJSON("/init/compliance/call/json/json_comp_status_agg", data, function(data) {
			var total = data.ok + data.nok + data.obs + data.na
			if (total == 0) {
				var p_ok = 0
				var p_nok = 0
				var p_obs = 0
				var p_na = 0
				var fp_ok = "0%"
				var fp_nok = "0%"
				var fp_obs = "0%"
				var fp_na = "0%"
			} else {
				var fp_ok = 100 * data.ok / total
				var fp_nok = 100 * data.nok / total
				var fp_obs = 100 * data.obs / total
				var fp_na = 100 * data.na / total
				var p_ok = fp_ok.toFixed(0) + "%"
				var p_nok = fp_nok.toFixed(0) + "%"
				var p_obs = fp_obs.toFixed(0) + "%"
				var p_na = fp_na.toFixed(0) + "%"
				var fp_ok = fp_ok.toFixed(1) + "%"
				var fp_nok = fp_nok.toFixed(1) + "%"
				var fp_obs = fp_obs.toFixed(1) + "%"
				var fp_na = fp_na.toFixed(1) + "%"
			}
			var d1 = $("<div style='margin:auto;text-align:center;width:100%'></div>")
			var d2 = $("<div style='text-align:left;margin:2px auto;background:#FF7863;overflow:hidden'></div>")
			var d3 = $("<div></div>")

			var div_obs = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#15367A'></div>")
			div_obs.css({"max-width": p_obs, "width": p_obs})
			var div_ok = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#3aaa50'></div>")
			div_ok.css({"max-width": p_ok, "width": p_ok})
			var div_na = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#acacac'></div>")
			div_na.css({"max-width": p_na, "width": p_na})

			var span_obs = $("<span style='color:#15367A;padding:3px'></span>")
			span_obs.text(data.obs + " (" + fp_obs + ") " + i18n.t("views.comp_status.obs"))
			var span_ok = $("<span style='color:#3aaa50;padding:3px'></span>")
			span_ok.text(data.ok + " (" + fp_ok + ") " + i18n.t("views.comp_status.ok"))
			var span_na = $("<span style='color:#acacac;padding:3px'></span>")
			span_na.text(data.na + " (" + fp_na + ") " + i18n.t("views.comp_status.na"))
			var span_nok = $("<span style='color:#FF7863;padding:3px'></span>")
			span_nok.text(data.nok + " (" + fp_nok + ") " + i18n.t("views.comp_status.nok"))

			d1.append(d2)
			d1.append(d3)
                        d2.append(div_obs)
                        d2.append(div_ok)
                        d2.append(div_na)
                        d3.append(span_obs)
                        d3.append(span_ok)
                        d3.append(span_na)
                        d3.append(span_nok)
			$("#"+divid).html(d1)
	})
}

function view_comp_status(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/comp_status.html", function() {
		$(this).i18n()
		var t = table_comp_status("cs0", options)
		t.options.on_change = function() {
			comp_status_agg("agg", {"table": t})
		}
		$("#cms_a").bind("click", function() {
			if (!$("#cms").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cms").show()
				table_comp_module_status("cms", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cms").hide()
			}
		})
		$("#cns_a").bind("click", function() {
			if (!$("#cns").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cns").show()
				table_comp_node_status("cns", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cns").hide()
			}
		})
		$("#css_a").bind("click", function() {
			if (!$("#css").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#css").show()
				table_comp_service_status("css", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#css").hide()
			}
		})
	})

}

function comp_status_log_on_hover(t) {
	t.div.find("[name$=_c_run_status]").hover(
	function() {
		line = $(this).parents("tr")
		var s = line.children("[name$=_c_run_status]")
		var e = line.children("[name$=_c_run_log]")
		var pos = s.position()
		e.width($(window).width()*0.8)
		e.css({"left": pos.left - e.width() - 10 + "px", "top": pos.top+s.parent().height() + "px"})
		e.addClass("white_float")
		cell_decorator_run_log(e)
		e.show()
	},
	function() {
		$(this).parents("tr").children("[name$=_c_run_log]").hide()
	})
}

function table_comp_status_node(divid, nodename) {
	var id = "cs_node_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_run_nodename"
	var request_vars = {}
	request_vars[f] = nodename

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_node",
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
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_svcname', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}

function table_comp_status_svc(divid, svcname) {
	var id = "cs_svc_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_run_svcname"
	var request_vars = {}
	request_vars[f] = svcname

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_svc",
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
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_nodename', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}


function table_dashboard(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': 'table_dashboard',
		'id': 'dashboard',
		'name': 'dashboard',
		'ajax_url': '/init/dashboard/ajax_dashboard',
		'columns': ['id', 'dash_severity', 'dash_links', 'dash_type', 'dash_svcname', 'dash_nodename', 'dash_env', 'dash_entry', 'dash_md5', 'dash_created', 'dash_updated', 'dash_dict', 'dash_fmt'],
		'force_cols': ['id', 'dash_svcname', 'dash_nodename', 'dash_type', 'dash_created', 'dash_dict', 'dash_fmt', 'dash_md5'],
		'default_columns': ['dash_updated', 'dash_env', 'dash_type', 'dash_nodename', 'dash_links', 'dash_severity', 'dash_created', 'dash_svcname', 'dash_entry'],
		'wsable': true,
		'events': ['dashboard_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_dashboard_node(divid, nodename) {
	var id = "dashboard_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_dash_nodename"
	var request_vars = {}
	request_vars[f] = nodename
	table_dashboard(divid, {
		"id": id,
		"caller": "table_dashboard_node",
		"request_vars": request_vars,
		"visible_columns": ['dash_updated', 'dash_type', 'dash_links', 'dash_entry', 'dash_env', 'dash_svcname', 'dash_severity', 'dash_created'],
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false
	})
}

function table_dashboard_svc(divid, svcname) {
	var id = "dashboard_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_dash_svcname"
	var request_vars = {}
	request_vars[f] = svcname
	table_dashboard(divid, {
		"id": id,
		"caller": "table_dashboard_svc",
		"request_vars": request_vars,
		"visible_columns": ['dash_updated', 'dash_type', 'dash_links', 'dash_entry', 'dash_env', 'dash_nodename', 'dash_severity', 'dash_created'],
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false
	})
}

function table_disks_charts(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "disks_charts",
		'caller': "view_disks",
		'name': "disks_charts",
		'checkboxes': false,
		'ajax_url': '/init/disks/ajax_disk_charts',
		'span': ['chart'],
		'force_cols': [],
		'columns': ['chart'],
		'default_columns': ['chart'],
		'colprops': {
			'chart': {"_class": "disks_charts"}
		},
		'parent_tables': ['disks'],
		'linkable': false,
		'dbfilterable': false,
		'filterable': false,
		'refreshable': false,
		'bookmarkable': false,
		'exportable': false,
		'columnable': false,
		'commonalityable': false,
		'headers': false,
		'pageable': false
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_disks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_disks",
		'id': "disks",
		'name': "disks",
		'ajax_url': '/init/disks/ajax_disks',
		'span': ['disk_id', 'disk_size', 'disk_alloc', 'disk_arrayid', 'disk_devid', 'disk_name', 'disk_raid', 'disk_group', 'array_model'],
		'force_cols': ['id', 'os_name'],
		'columns': ['disk_id', 'disk_region', 'disk_vendor', 'disk_model', 'app', 'disk_nodename', 'disk_svcname', 'disk_local', 'disk_dg', 'svcdisk_updated', 'disk_used', 'disk_size', 'disk_alloc', 'disk_name', 'disk_devid', 'disk_raid', 'disk_group', 'disk_arrayid', 'disk_level', 'array_model', 'disk_created', 'disk_updated', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2'],
		'default_columns': ["app", "array_model", "disk_alloc", "disk_arrayid", "disk_created", "disk_devid", "disk_dg", "disk_group", "disk_id", "disk_level", "disk_local", "disk_model", "disk_name", "disk_nodename", "disk_raid", "disk_size", "disk_svcname", "disk_updated", "disk_used", "disk_vendor", "svcdisk_updated"],
		'child_tables': ['charts'],
		'wsable': true,
		'events': ['disks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_disks(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/disks.html", function() {
		$(this).i18n()
		table_disks_charts("charts", options)
		table_disks("disks", options)
		$("#charts_a").bind("click", function() {
			if (!$("#charts").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#charts").show()
				table_disks_charts("charts", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#charts").hide()
			}
		})
	})
}

function table_dns_records(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "dnsr",
		'caller': "table_dns_records",
		'name': "dns_records",
		'ajax_url': '/init/dns/ajax_dns_records',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'domain_id', 'name', 'type', 'content', 'ttl', 'prio', 'change_date'],
		'default_columns': ['domain_id', 'name', 'type', 'content', 'ttl', 'prio'],
		'colprops': {
			"name": {
				"_class": "dns_record",
				"_dataclass": "",
				"img": "dns16",
				"title": "Name"
			},
			"prio": {
				"_class": "",
				"_dataclass": "",
				"img": "dns16",
				"title": "Priority"
			},
			"type": {
				"_class": "dns_records_type",
				"_dataclass": "",
				"img": "dns16",
				"title": "Type"
			}
		},
		'wsable': true,
		'events': ['pdns_records_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_dns_records_domain_id(divid, domain_id) {
	var id = "dnsr_" + domain_id
	var f = id+"_f_domain_id"
	var request_vars = {}
	request_vars[f] = domain_id
	table_dns_records(divid, {
		"id": id,
		"caller": "table_dns_records_domain_id",
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
	})
}

function table_dns_domains(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_dns_domains",
		'id': "dnsd",
		'name': "dns_domains",
		'ajax_url': '/init/dns/ajax_dns_domains',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'name', 'master', 'last_check', 'type', 'notified_serial', 'account'],
		'default_columns': ['name', 'master', 'type', 'notified_serial'],
		"colprops": {
			"name": {
				"_class": "dns_domain",
				"_dataclass": "",
				"img": "dns16",
				"title": "Name"
			},
			"type": {
				"_class": "",
				"_dataclass": "",
				"img": "dns16",
				"title": "Type"
			}
		},
		'wsable': true,
		'events': ['pdns_domains_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_dns(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/dns.html", function() {
		$(this).i18n()
		table_dns_domains("dnsddiv", options)
		table_dns_records("dnsrdiv", options)
	})
}

function table_filtersets(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "filtersets",
		'caller': "table_filtersets",
		'name': "filtersets",
		'checkboxes': true,
		'ajax_url': '/init/filtersets/ajax_filtersets',
		'span': ['fset_name', 'fset_stats'],
		'force_cols': ['fset_id', 'f_id', 'encap_fset_id'],
		'columns': ['fset_id', 'fset_name', 'fset_stats', 'fset_updated', 'fset_author', 'f_id', 'f_order', 'f_log_op', 'encap_fset_id', 'encap_fset_name', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'default_columns': ['fset_name', 'f_order', 'f_log_op', 'encap_fset_name', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'wsable': true,
		'events': ['gen_filtersets_change', 'gen_filtersets_filters_change', 'gen_filters_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}


function table_filters(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "table_filters",
		'id': "filters",
		'name': "filters",
		'ajax_url': '/init/filtersets/ajax_filters',
		'span': ['f_table', 'f_field'],
		'force_cols': ['id'],
		'columns': ['id', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'colprops': {
			"f_author": {"display": 1},
			"f_field": {"display": 1},
			"f_op": {"display": 1},
			"f_table": {"display": 1},
			"f_updated": {"display": 1},
			"f_value": {"display": 1}
		},
		'wsable': true,
		'events': ['gen_filters_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_forms(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_forms",
		'id': "forms",
		'name': "forms",
		'ajax_url': '/init/forms/ajax_forms_admin',
		'span': ['id'],
		'force_cols': ['id', 'form_type'],
		'columns': ['id', 'form_name', 'form_type', 'form_folder', 'form_team_responsible', 'form_team_publication', 'form_yaml', 'form_created', 'form_author'],
		'default_columns': ['form_name', 'form_type', 'form_folder', 'form_team_responsible', 'form_team_publication', 'form_yaml'],
		'colprops': {
			"form_name": {"_class": "form_name"},
		},
		'wsable': true,
		'events': ['forms_change'],
		'request_vars': {}
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_log(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "log",
		'caller': "table_log",
		'name': "log",
		'checkboxes': false,
		'ajax_url': '/init/log/ajax_log',
		'span': ['id'],
		'force_cols': ['id', 'log_fmt', 'log_dict'],
		'default_columns': ['log_date', 'log_icons', 'log_level', 'log_svcname', 'log_nodename', 'log_user', 'log_action', 'log_evt'],
		'columns': ['id', 'log_date', 'log_icons', 'log_level', 'log_svcname', 'log_nodename', 'log_user', 'log_action', 'log_evt', 'log_fmt', 'log_dict', 'log_gtalk_sent', 'log_email_sent'],
		'wsable': true
	}
	var _options = $.extend({}, defaults, options)

	wsh[_options.id] = function(data) {
		if (data["event"] == "log_change") {
			_data = []
			_data.push({"key": "id", "val": data["data"]["id"], "op": "="})
			osvc.tables[_options.id].insert(_data)
		}
	}

	return table_init(_options)
}

function table_log_node(divid, nodename) {
	var id = "log_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_log_nodename"
	var request_vars = {}
	request_vars[f] = nodename
	table_log(divid, {
		"id": id,
		"caller": "table_log_node",
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
		"wsable": false
	})
}

function table_log_svc(divid, svcname) {
	var id = "log_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_log_svcname"
	var request_vars = {}
	request_vars[f] = svcname
	table_log(divid, {
		"id": id,
		"caller": "table_log_svc",
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
		"wsable": false
	})
}
function table_networks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_networks",
		'id': "networks",
		'name': "networks",
		'ajax_url': '/init/networks/ajax_networks',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'name', 'pvid', 'network', 'broadcast', 'netmask', 'gateway', 'begin', 'end', 'prio', 'team_responsible', 'comment', 'updated'],
		'default_columns': ['name', 'pvid', 'network', 'broadcast', 'netmask', 'gateway', 'begin', 'end', 'prio', 'team_responsible', 'comment', 'updated'],
		'wsable': true,
		'events': ['networks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_nodenetworks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_nodenetworks",
		'id': "nodenetworks",
		'name': "nodenetworks",
		'ajax_url': '/init/nodenetworks/ajax_nodenetworks',
		'span': ['nodename'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(
			['id', 'nodename'],
			objcols.node,
			['updated', 'mac', 'intf', 'addr_type', 'addr', 'mask', 'flag_deprecated', 'addr_updated', 'net_name', 'net_network', 'net_broadcast', 'net_comment', 'net_gateway', 'net_begin', 'net_end', 'prio', 'net_pvid', 'net_netmask', 'net_team_responsible']
		),
		'default_columns': ["addr_type", "addr", "addr_updated", "intf", "mac", "mask", "net_begin", "net_end", "net_broadcast", "net_comment", "net_gateway", "net_name", "net_netmask", "net_network", "net_pvid", "net_team_responsible", "nodename"],
		'wsable': true,
		'events': ['node_ip_change', 'nodes_change', 'networks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_nodenetworks_addr(divid, addr) {
	var id = "nodenetworks_" + addr.replace(/[\.-]/g, "_")
	var f = id+"_f_addr"
	var request_vars = {}
	request_vars[f] = addr
	table_nodenetworks(divid, {
		"id": id,
		"caller": "table_table_nodenetworks_addr",
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
			'nodename',
			'fqdn',
			'loc_city',
			'team_responsible',
			'project',
			'host_mode',
			'environnement',
			'status',
			'mac',
			'intf',
			'addr',
			'mask',
			'flag_deprecated',
			'addr_updated',
			'net_name',
			'net_network',
			'net_gateway',
			'net_pvid',
			'net_netmask'
		]
	})
}

function table_nodesan(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_nodesan",
		'id': "nodesan",
		'name': "nodesan",
		'ajax_url': '/init/nodesan/ajax_nodesan',
		'span': ['nodename'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(['id', 'nodename'], objcols.node, ['node_updated', 'hba_id', 'tgt_id', 'array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated', 'array_level']),
		'default_columns': ["array_model", "array_name", "hba_id", "nodename", "tgt_id"],
		'colprops': {
			"array_name": {
				"_dataclass": "bluer",
				"_class": "",
			},
		},
		'wsable': false,
		'events': []
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_uids(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_nodes",
		'id': "uids",
		'name': "uids",
		'ajax_url': '/init/nodes/ajax_uids',
		'span': ['user_id'],
		'columns': ['user_id', 'user_id_count', 'user_name'],
		'default_columns': ['user_id', 'user_id_count', 'user_name'],
		'parent_tables': ["nodes"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_gids(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "gids",
		'caller': "view_nodes",
		'name': "gids",
		'ajax_url': '/init/nodes/ajax_gids',
		'span': ['group_id'],
		'columns': ['group_id', 'group_id_count', 'group_name'],
		'default_columns': ['group_id', 'group_id_count', 'group_name'],
		'parent_tables': ["nodes"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_nodes(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_nodes",
		'id': "nodes",
		'name': "nodes",
		'ajax_url': '/init/nodes/ajax_nodes',
		'span': ['nodename'],
		'force_cols': ['os_name'],
		'columns': [].concat(['id', 'nodename'], objcols.node, ["updated"]),
		'default_columns': [
			"cpu_cores",
			"cpu_dies",
			"cpu_model",
			"host_mode",
			"loc_building",
			"loc_floor",
			"loc_rack",
			"mem_bytes",
			"nodename",
			"serial",
			"status",
			"team_responsible"
		],
		'child_tables': ['obs_agg', 'uids', 'gids'],
		'wsable': true,
		'events': ['nodes_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_nodes(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/nodes.html", function() {
		$(this).i18n()
		table_nodes("nodes_container", options)
		$("#uids_a").bind("click", function() {
			if (!$("#uids").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#uids").show()
				table_uids("uids", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#uids").hide()
			}
		})
		$("#gids_a").bind("click", function() {
			if (!$("#gids").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#gids").show()
				table_gids("gids", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#gids").hide()
			}
		})
	})
}

function table_obsolescence(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_obsolescence",
		'id': 'obs',
		'name': "obsolescence",
		'ajax_url': '/init/obsolescence/ajax_obs',
		'force_cols': ['id', 'obs_type', 'obs_name'],
		'columns': ['id', 'obs_count', 'obs_type', 'obs_name', 'obs_warn_date', 'obs_alert_date'],
		'default_columns': ['obs_count', 'obs_type', 'obs_name', 'obs_warn_date', 'obs_alert_date'],
		'wsable': true,
		'events': ['obsolescence_change']
	}
	var _options = $.extend({}, defaults, options)
	table_init(_options)
}

function table_packages(divid, options) {
	var defaults = {
		"id": "packages",
		"caller": "table_packages",
		"divid": divid,
		"name": "packages",
		"ajax_url": "/init/packages/ajax_packages",
		"force_cols": ["id", "os_name"],
		"columns": [].concat(["id", "nodename", "pkg_name", "pkg_version", "pkg_arch", "pkg_type", "sig_provider", "pkg_sig", "pkg_install_date", "pkg_updated"], objcols.node),
		"default_columns": ["nodename", "pkg_name", "pkg_version", "pkg_arch", "pkg_type", "sig_provider", "pkg_install_date", "pkg_updated"],
		"wsable": true,
		"events": ["packages_change"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_patches(divid, options) {
	var defaults = {
		'id': "pathces",
		'divid': divid,
		'caller': "table_patches",
		'name': "patches",
		'ajax_url': '/init/patches/ajax_patches',
		'span': ['id'],
		'force_cols': ['os_name'],
		'columns': [].concat(['nodename', 'id', 'patch_num', 'patch_rev', 'patch_install_date', 'patch_updated'], objcols.node),
		'default_columns': ['nodename', 'id', 'patch_num', 'patch_rev', 'patch_install_date', 'patch_updated'],
		'wsable': false,
		'events': ['patches_change']
	}
	var _options = $.extend({}, defaults, options)
	table_init(_options)
}

function table_prov_templates(divid, options) {
	var defaults = {
		'id': "templates",
		'divid': divid,
		'caller': "table_prov_templates",
		'name': "templates",
		'ajax_url': '/init/provisioning/ajax_prov_admin',
		'span': [],
		'force_cols': ['id', 'tpl_name'],
		'columns': ['id', 'tpl_name', 'tpl_command', 'tpl_comment', 'tpl_created', 'tpl_author', 'tpl_team_responsible'],
		'default_columns': ['tpl_name', 'tpl_command', 'tpl_comment', 'tpl_created', 'tpl_author', 'tpl_team_responsible'],
		'wsable': true,
		'events': ['prov_templates_change', 'prov_template_responsible_change']
	}
	var _options = $.extend({}, defaults, options)
	table_init(_options)
}

function table_quota(divid, options) {
	var defaults = {
	     'id': "quota",
	     'divid': divid,
	     'caller': "table_quota",
	     'name': "quota",
	     'ajax_url': '/init/disks/ajax_quota',
	     'span': ['array_name', 'dg_name', 'app'],
	     'force_cols': ['id'],
	     'columns': ['id', 'array_name', 'array_model', 'dg_name', 'dg_size', 'dg_reserved', 'dg_reservable', 'dg_used', 'dg_free', 'app', 'quota', 'quota_used'],
	     'default_columns': ['array_name', 'array_model', 'dg_name', 'dg_size', 'dg_reserved', 'dg_reservable', 'dg_used', 'dg_free', 'app', 'quota', 'quota_used'],
	     'wsable': true,
	     'events': ['stor_array_dg_quota_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_quota_array(divid, array_name) {
	var id = "quota_" + array_name.replace(/[ \.-]/g, "_")
	var f = id+"_f_array_name"
	var request_vars = {}
	request_vars[f] = array_name
	return table_quota(divid, {
		"id": id,
		"caller": "table_quota_array",
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
		"wsable": false
	})
}

function table_quota_app(divid, app) {
	var id = "quota_" + app.replace(/[ \.-]/g, "_")
	var f = id+"_f_app"
	var request_vars = {}
	request_vars[f] = app
	return table_quota(divid, {
		"id": id,
		"caller": "table_quota_app",
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
		"wsable": false
	})
}

function table_quota_array_dg(divid, array_name, dg_name) {
	var id = "quota_" + array_name.replace(/[ \.-]/g, "_") + dg_name.replace(/[ \.-]/g, "_")
	var request_vars = {}
	var f1 = id+"_f_array_name"
	var f2 = id+"_f_dg_name"
	request_vars[f1] = array_name
	request_vars[f2] = dg_name
	return table_quota(divid, {
		"id": id,
		"caller": "table_quota_array_dg",
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
		"wsable": false
	})
}


function table_replication(divid, options) {
	var defaults = {
	     'caller': "table_replication",
	     'divid': divid,
	     'id': "replication",
	     'name': "replication",
	     'ajax_url': '/init/replication/ajax_replication_status',
	     'span': [],
	     'force_cols': [],
	     'columns': ['mode', 'remote', 'table_schema', 'table_name', 'need_resync', 'current_cksum', 'last_cksum', 'table_updated'],
	     'default_columns': ['mode', 'remote', 'table_schema', 'table_name', 'need_resync', 'current_cksum', 'last_cksum', 'table_updated']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_metrics(divid, options) {
	var defaults = {
		'id': "table_metrics",
		'divid': divid,
		'id': "metrics",
		'name': "metrics",
		'ajax_url': '/init/charts/ajax_metrics_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'metric_name', 'metric_sql', 'metric_col_value_index', 'metric_col_instance_index', 'metric_col_instance_label', 'metric_created', 'metric_author'],
		'default_columns': ['metric_name', 'metric_sql', 'metric_col_value_index', 'metric_col_instance_index', 'metric_col_instance_label'],
		'wsable': true,
		'events': ['metrics_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_charts(divid, options) {
	var defaults = {
		'id': "table_charts",
		'divid': divid,
		'id': "charts",
		'name': "charts",
		'ajax_url': '/init/charts/ajax_charts_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'chart_name', 'chart_yaml'],
		'default_columns': ['chart_name', 'chart_yaml'],
		'wsable': true,
		'events': ['charts_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_reports(divid, options) {
	var defaults = {
		'caller': "table_reports",
		'divid': divid,
		'id': "reports",
		'name': "reports",
		'ajax_url': '/init/charts/ajax_reports_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'report_name', 'report_yaml'],
		'default_columns': ['report_name', 'report_yaml'],
		'wsable': true,
		'events': ['reports_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}


function table_resources(divid, options) {
	var defaults = {
		'name': 'resmon',
		'divid': divid,
		'caller': 'table_resmon',
		'id': 'resmon',
		'ajax_url': '/init/resmon/ajax_resmon',
		'span': ['nodename', 'svcname'],
		'force_cols': ['id', 'svcname', 'nodename', 'vmname', 'rid', 'updated', 'os_name'],
		'columns': [].concat(['svcname', 'nodename', 'vmname', 'rid', 'res_status', 'res_desc', 'res_log', 'res_monitor', 'res_disable', 'res_optional', 'updated'], objcols.node, ['node_updated']),
		'default_columns': ['svcname', 'nodename', 'vmname', 'rid', 'res_status', 'res_desc', 'res_log', 'res_monitor', 'res_disable', 'res_optional', 'updated'],
		'wsable': true,
		'events': ['resmon_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_resources_node(divid, nodename) {
	var id = "resmon_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_nodename"
	var request_vars = {}
	request_vars[f] = nodename
	return table_resources(divid, {
		"id": id,
		"caller": "table_resources_node",
		"request_vars": request_vars,
		"visible_columns": ['svcname', 'vmname', 'rid', 'res_status', 'res_desc', 'res_log', 'res_monitor', 'res_disable', 'res_optional', 'updated'],
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false
	})
}

function table_resources_svc(divid, svcname) {
	var id = "resmon_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_svcname"
	var request_vars = {}
	request_vars[f] = svcname
	return table_resources(divid, {
		"id": id,
		"caller": "table_resources_svc",
		"request_vars": request_vars,
		"visible_columns": ['nodename', 'vmname', 'rid', 'res_status', 'res_desc', 'res_log', 'res_monitor', 'res_disable', 'res_optional', 'updated'],
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false
	})
}
function table_sanswitches(divid, options) {
	var defaults = {
		'id': "sanswitches",
		'divid': divid,
		'caller': "table_sanswitches",
		'name': "sanswitches",
		'checkboxes': false,
		'ajax_url': '/init/sanswitches/ajax_sanswitches',
		'span': ['sw_name', 'sw_index'],
		'columns': ['sw_fabric', 'sw_name', 'sw_index', 'sw_slot', 'sw_port', 'sw_portspeed', 'sw_portnego', 'sw_porttype', 'sw_portstate', 'sw_portname', 'sw_rportname', 'sw_rname', 'sw_updated'],
		'default_columns': ['sw_fabric', 'sw_name', 'sw_index', 'sw_slot', 'sw_port', 'sw_portspeed', 'sw_portnego', 'sw_porttype', 'sw_portstate', 'sw_portname', 'sw_rportname', 'sw_rname', 'sw_updated']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_saves(divid, options) {
	var defaults = {
		'id': "saves",
		'divid': divid,
		'caller': "view_saves",
		'name': "saves",
		'ajax_url': '/init/saves/ajax_saves',
		'span': ['save_nodename', 'save_svcname'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(['id', 'save_server', 'save_id', 'save_app', 'save_nodename', 'save_svcname', 'save_name', 'save_group', 'save_level', 'save_size', 'save_volume', 'save_date', 'save_retention'], objcols.node),
		'default_columns': ['save_server', 'save_app', 'save_nodename', 'save_svcname', 'save_name', 'save_group', 'save_level', 'save_size', 'save_volume', 'save_date', 'save_retention'],
		'child_tables': ['charts'],
		'wsable': true,
		'events': ['saves_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_saves_charts(divid, options) {
	var defaults = {
		'id': "charts",
		'divid': divid,
		'caller': "view_saves",
		'name': "saves_charts",
		'checkboxes': false,
		'ajax_url': '/init/saves/ajax_saves_charts',
		'span': ['chart'],
		'force_cols': [],
		'columns': ['chart'],
		'default_columns': ['chart'],
		'colprops': {
			'chart': {
				'img': 'spark16',
				'_dataclass': '',
				'title': 'Chart',
				'_class': 'saves_charts',
			}
		},
		'parent_tables': ['saves'],
		'linkable': false,
		'filterable': false,
		'refreshable': false,
		'bookmarkable': false,
		'exportable': false,
		'columnable': false,
		'commonalityable': false,
		'headers': false,
		'pageable': false
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_saves(divid, options) {
	o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.div.load("/init/static/views/saves.html", function() {
		o.div.i18n()
		table_saves("saves_div", options)
		table_saves_charts("stats_div", options)
		$("#stats_a").bind("click", function() {
			if (!$("#stats_div").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#stats_div").show()
				table_saves_charts("stats_div", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#stats_div").hide()
			}
		})

	})
}

function table_service_instances(divid, options) {
	var defaults = {
		'caller': 'table_service_instances',
		'id': 'svcmon',
		'divid': divid,
		'name': 'service_instances',
		'extrarow': true,
		'extrarow_class': "svcmon_links",
		'ajax_url': '/init/default/ajax_svcmon',
		'span': [].concat(['mon_svcname'], objcols.service, ['svc_updated', 'app_domain', 'app_team_ops']),
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
function table_services(divid, options) {
	var defaults = {
		'caller': 'table_services',
		'divid': divid,
		'name': 'services',
		'id': 'services',
		'ajax_url': '/init/services/ajax_services',
		'span': ['svc_name'],
		'force_cols': ['svc_name', 'svc_status_updated'],
		'columns': [].concat(['svc_name'], objcols.service, ["updated"]),
		'default_columns': ["svc_status", "svc_name", "svc_cluster_type", "svc_availstatus", "svc_status_updated", "svc_ha", "updated"],
		'colprops': {
			"updated": colprops.svc_updated
		},
		'wsable': true,
		'events': ['services_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_tagattach(divid, options) {
	var defaults = {
		'id': 'tagattach',
		'name': 'tagattach',
		'caller': 'table_tagattach',
		'divid': divid,
		'ajax_url': '/init/tags/ajax_tagattach',
		'span': ['tag_id'],
		'force_cols': ['ckid'],
		'columns': ['tag_id', 'tag_name', 'nodename', 'svcname', 'created'],
		'default_columns': ['tag_name', 'nodename', 'svcname', 'created'],
		'wsable': true,
		'events': ['tags', 'node_tags_change', 'svc_tags_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_tags(divid, options) {
	var defaults = {
		'name': "tags",
		'id': "tags",
		'divid': divid,
		'caller': "table_tags",
		'ajax_url': '/init/tags/ajax_tags',
		'span': ['id'],
		'force_cols': ['id', 'tag_name'],
		'columns': ['id', 'tag_name', 'tag_exclude', 'tag_created'],
		'default_columns': ['tag_name', 'tag_exclude', 'tag_created'],
		'wsable': true,
		'events': ['tags_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_users(divid, options) {
	var defaults = {
		'name': "users",
		'id': "users",
		'caller': "table_users",
		'divid': divid,
		'ajax_url': '/init/users/ajax_users',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['manager', 'id', 'fullname', 'email', 'phone_work', 'primary_group', 'groups', 'lock_filter', 'fset_name', 'domains', 'last'],
		'default_columns': ['manager', 'fullname', 'email', 'phone_work', 'primary_group', 'groups', 'lock_filter', 'fset_name', 'domains', 'last'],
		'wsable': true,
		'events': ['auth_user_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_workflows(divid, options) {
	var defaults = {
		'name': "workflows",
		'id': "workflows",
		'caller': "table_workflows",
		'divid': divid,
		'checkboxes': false,
		'ajax_url': '/init/forms/ajax_workflows',
		'span': ['form_head_id'],
		'force_cols': ["form_head_id"],
		'columns': ['form_head_id', 'form_name', 'last_form_id', 'last_form_name', 'form_folder', 'status', 'steps', 'creator', 'last_assignee', 'create_date', 'last_update', 'form_yaml'],
		'default_columns': ['form_head_id', 'form_name', 'last_form_id', 'last_form_name', 'status', 'steps', 'creator', 'last_assignee', 'create_date', 'last_update'],
		'wsable': true,
		'events': ["forms_store_change"]
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_workflows_assigned_to_me(divid, options) {
	$.when(osvc.user_loaded).then(function() {
		var me = _self.first_name + " " + _self.last_name
		var notme = "!" + me
		for (var i=0; i<_groups.length; i++) {
			if (_groups[i].privilege == true) {
				continue
			}
			me += "|" + _groups[i].role
			notme += "&!" + _groups[i].role
		}
		var defaults = {
			"id": "workflows_atm",
			"caller": "table_workflows_assigned_to_me",
			"colprops": {
				"status": {
					"force_filter": "!closed",
				},
				"last_assignee": {
					"force_filter": me,
				}
			}
		}
		var _options = $.extend({}, defaults, options)
		return table_workflows(divid, _options)
	})
}

function table_workflows_assigned_to_tiers(divid, options) {
	$.when(osvc.user_loaded).then(function() {
		var me = _self.first_name + " " + _self.last_name
		var notme = "!" + me
		for (var i=0; i<_groups.length; i++) {
			if (_groups[i].privilege == true) {
				continue
			}
			me += "|" + _groups[i].role
			notme += "&!" + _groups[i].role
		}
		var defaults = {
			"id": "workflows_att",
			"caller": "table_workflows_assigned_to_tiers",
			"colprops": {
				"status": {
					"force_filter": "!closed",
				},
				"last_assignee": {
					"force_filter": notme,
				},
				"creator": {
					"force_filter": me,
				}
			}
		}
		var _options = $.extend({}, defaults, options)
		return table_workflows(divid, _options)
	})
}

