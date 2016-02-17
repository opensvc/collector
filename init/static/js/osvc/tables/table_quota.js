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


