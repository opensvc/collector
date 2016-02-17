function table_apps(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "apps",
		'caller': "table_apps",
		'name': "apps",
		'ajax_url': '/init/apps/ajax_apps',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': [
			'id',
			'app',
			'app_domain',
			'app_team_ops',
			'roles',
			'responsibles',
			'mailto'
		],
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

