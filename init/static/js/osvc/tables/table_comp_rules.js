table_comp_rules_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/compliance/ajax_comp_rulesets',
     'span': ['ruleset_name', 'ruleset_type', 'ruleset_public', 'fset_name', 'teams_responsible', 'teams_publication'],
     'force_cols': [],
     'columns': ['ruleset_name', 'ruleset_type', 'ruleset_public', 'teams_responsible', 'teams_publication', 'fset_name', 'chain', 'chain_len', 'encap_rset', 'var_class', 'var_name', 'var_value', 'var_updated', 'var_author'],
     'colprops': {'fset_name': {'field': 'fset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Filterset', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'teams_publication': {'field': 'teams_publication', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Teams publication', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'var_author': {'field': 'var_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'chain': {'field': 'chain', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Chain', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'var_class': {'field': 'var_class', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Class', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'var_value': {'field': 'var_value', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Value', '_class': 'rule_value', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'fset_id': {'field': 'fset_id', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Filterset id', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'encap_rset': {'field': 'encap_rset', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Encapsulated ruleset', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'var_updated': {'field': 'var_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_no_age', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'ruleset_type': {'field': 'ruleset_type', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Ruleset type', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Rule id', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'var_name': {'field': 'var_name', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Variable', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'ruleset_public': {'field': 'ruleset_public', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Ruleset public', '_class': 'boolean', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'ruleset_id': {'field': 'ruleset_id', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Ruleset id', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'ruleset_name': {'field': 'ruleset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Ruleset', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'chain_len': {'field': 'chain_len', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Chain length', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}, 'teams_responsible': {'field': 'teams_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'admins16', '_dataclass': '', 'title': 'Teams responsible', '_class': '', 'table': 'v_comp_rulesets', 'display': 1, 'default_filter': ''}, 'encap_rset_id': {'field': 'encap_rset_id', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Encapsulated ruleset id', '_class': '', 'table': 'v_comp_rulesets', 'display': 0, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': false,
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
     'events': [],
     'request_vars': {}
}

function table_comp_rules(divid, options) {
  var _options = {"id": "cr0"}
  $.extend(true, _options, table_comp_rules_defaults, options)
  _options.divid = divid
  _options.caller = "table_comp_rules"
  table_init(_options)
}

