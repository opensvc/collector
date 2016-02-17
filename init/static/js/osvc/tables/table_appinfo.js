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

