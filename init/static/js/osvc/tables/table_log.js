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
