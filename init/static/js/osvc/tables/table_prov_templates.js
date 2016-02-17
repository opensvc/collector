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

