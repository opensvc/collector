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
