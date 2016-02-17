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

