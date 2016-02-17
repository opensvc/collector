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

