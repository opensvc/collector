function table_comp_rules(divid, options) {
	var defaults = {
		'id': "cr0",
		'name': "comp_rulesets",
		'caller': "table_comp_rules",
		'divid': divid,
		'ajax_url': '/init/compliance/ajax_comp_rulesets',
		'span': ['ruleset_name', 'ruleset_type', 'ruleset_public', 'fset_name', 'teams_responsible', 'teams_publication'],
		'force_cols': ['id', 'var_class', 'encap_rset', 'ruleset_id'],
		'columns': ['id', 'ruleset_id', 'ruleset_name', 'ruleset_type', 'ruleset_public', 'teams_responsible', 'teams_publication', 'fset_name', 'chain', 'chain_len', 'encap_rset', 'var_class', 'var_name', 'var_value', 'var_updated', 'var_author'],
		'default_columns': ["encap_rset", "fset_name", "ruleset_name", "ruleset_public", "ruleset_type", "teams_publication", "teams_responsible", "var_author", "var_class", "var_name", "var_updated", "var_value"],
		'wsable': true,
		'events': ['comp_rulesets_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

