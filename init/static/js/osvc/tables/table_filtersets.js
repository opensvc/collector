table_filtersets_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/filtersets/ajax_filtersets',
     'span': ['fset_name', 'fset_stats'],
     'force_cols': ['fset_id', 'f_id', 'encap_fset_id'],
     'columns': ['fset_id', 'fset_name', 'fset_stats', 'fset_updated', 'fset_author', 'f_id', 'f_order', 'f_log_op', 'encap_fset_id', 'encap_fset_name', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
     'colprops': {'encap_fset_id': {'field': 'encap_fset_id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Encap filterset id', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'fset_author': {'field': 'fset_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Fset author', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'fset_stats': {'field': 'fset_stats', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Compute stats', '_class': 'boolean', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'fset_name': {'field': 'fset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Filterset', '_class': 'fset_name', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'encap_fset_name': {'field': 'encap_fset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Encap filterset', '_class': 'fset_name', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'fset_id': {'field': 'fset_id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Filterset id', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'f_id': {'field': 'f_id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Filter id', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'f_op': {'field': 'f_op', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Operator', '_class': '', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_log_op': {'field': 'f_log_op', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Operator', '_class': '', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_author': {'field': 'f_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_value': {'field': 'f_value', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Value', '_class': '', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_order': {'field': 'f_order', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Ordering', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'f_table': {'field': 'f_table', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Table', '_class': 'db_table_name', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_field': {'field': 'f_field', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Field', '_class': 'db_column_name', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'f_updated': {'field': 'f_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_no_age', 'table': 'v_gen_filtersets', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}, 'fset_updated': {'field': 'fset_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Fset updated', '_class': 'datetime_no_age', 'table': 'v_gen_filtersets', 'display': 0, 'default_filter': ''}},
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
     'events': ['gen_filtersets_change', 'gen_filtersets_filters_change', 'gen_filters_change'],
     'request_vars': {}
}

function table_filtersets(divid, options) {
  var _options = {"id": "filtersets"}
  $.extend(true, _options, table_filtersets_defaults, options)
  _options.divid = divid
  _options.caller = "table_filtersets"
  table_init(_options)
}


table_filters_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/filtersets/ajax_filters',
     'span': ['f_table', 'f_field'],
     'force_cols': ['id'],
     'columns': ['id', 'f_table', 'f_field', 'f_op', 'f_value', 'f_updated', 'f_author'],
     'colprops': {'f_op': {'field': 'f_op', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Operator', '_class': '', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'f_author': {'field': 'f_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'f_value': {'field': 'f_value', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Value', '_class': '', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'f_field': {'field': 'f_field', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Field', '_class': 'db_column_name', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'f_table': {'field': 'f_table', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Table', '_class': 'db_table_name', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'f_updated': {'field': 'f_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_no_age', 'table': 'gen_filters', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'gen_filters', 'display': 0, 'default_filter': ''}},
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
     'events': ['gen_filters_change'],
     'request_vars': {}
}

function table_filters(divid, options) {
  var _options = {"id": "filters"}
  $.extend(true, _options, table_filters_defaults, options)
  _options.divid = divid
  _options.caller = "table_filters"
  table_init(_options)
}

