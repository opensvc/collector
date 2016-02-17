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

