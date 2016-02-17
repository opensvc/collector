function table_forms(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_forms",
		'id': "forms",
		'name': "forms",
		'ajax_url': '/init/forms/ajax_forms_admin',
		'span': ['id'],
		'force_cols': ['id', 'form_type'],
		'columns': ['id', 'form_name', 'form_type', 'form_folder', 'form_team_responsible', 'form_team_publication', 'form_yaml', 'form_created', 'form_author'],
		'default_columns': ['form_name', 'form_type', 'form_folder', 'form_team_responsible', 'form_team_publication', 'form_yaml'],
		'colprops': {
			"form_name": {"_class": "form_name"},
		},
		'wsable': true,
		'events': ['forms_change'],
		'request_vars': {}
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

