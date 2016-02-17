function table_filtersets(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "filtersets",
		'caller': "table_filtersets",
		'name': "filtersets",
		'checkboxes': true,
		'ajax_url': '/init/filtersets/ajax_filtersets',
		'span': ['fset_name', 'fset_stats'],
		'force_cols': ['fset_id', 'f_id', 'encap_fset_id'],
		'columns': ['fset_id', 'fset_name', 'fset_stats', 'fset_updated', 'fset_author', 'f_id', 'f_order', 'f_log_op', 'encap_fset_id', 'encap_fset_name', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'default_columns': ['fset_name', 'f_order', 'f_log_op', 'encap_fset_name', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'wsable': true,
		'events': ['gen_filtersets_change', 'gen_filtersets_filters_change', 'gen_filters_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}


function table_filters(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "table_filters",
		'id': "filters",
		'name': "filters",
		'ajax_url': '/init/filtersets/ajax_filters',
		'span': ['f_table', 'f_field'],
		'force_cols': ['id'],
		'columns': ['id', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
		'colprops': {
			"f_author": {"display": 1},
			"f_field": {"display": 1},
			"f_op": {"display": 1},
			"f_table": {"display": 1},
			"f_updated": {"display": 1},
			"f_value": {"display": 1}
		},
		'wsable': true,
		'events': ['gen_filters_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

