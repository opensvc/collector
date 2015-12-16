table_comp_modules_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/compliance/ajax_comp_moduleset',
     'span': ['modset_name'],
     'force_cols': [],
     'columns': ['modset_name', 'teams_responsible', 'teams_publication', 'modset_mod_name', 'autofix', 'modset_mod_updated', 'modset_mod_author'],
     'colprops': {'autofix': {'field': 'autofix', 'filter_redirect': '', 'force_filter': '', 'img': 'actionred16', '_dataclass': '', 'title': 'Autofix', '_class': 'boolean', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'teams_publication': {'field': 'teams_publication', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Teams publication', '_class': '', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'modset_mod_name': {'field': 'modset_mod_name', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Module', '_class': '', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'modset_name': {'field': 'modset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Moduleset', '_class': '', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'modset_mod_updated': {'field': 'modset_mod_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_no_age', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'modset_mod_author': {'field': 'modset_mod_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}, 'teams_responsible': {'field': 'teams_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'admins16', '_dataclass': '', 'title': 'Teams responsible', '_class': '', 'table': 'v_comp_modulesets', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': true,
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

function table_comp_modules(divid, options) {
  var _options = {"id": "comp_modules"}
  $.extend(true, _options, table_comp_modules_defaults, options)
  _options.divid = divid
  _options.caller = "table_comp_modules"
  table_init(_options)
}

