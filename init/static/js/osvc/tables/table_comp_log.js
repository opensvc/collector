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

