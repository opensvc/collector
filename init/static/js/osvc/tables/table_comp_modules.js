function table_comp_modules(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "comp_modules",
		'caller': "table_comp_modules",
		'name': "comp_modules",
		'ajax_url': '/init/compliance/ajax_comp_moduleset',
		'span': ['modset_name'],
		'force_cols': ["id"],
		'columns': ['modset_name', 'teams_responsible', 'teams_publication', 'modset_mod_name', 'autofix', 'modset_mod_updated', 'modset_mod_author'],
		'default_columns': ["autofix", "modset_mod_author", "modset_mod_name", "modset_mod_updated", "modset_name", "teams_publication", "teams_responsible"],
		'wsable': true,
		'events': ['comp_moduleset_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

