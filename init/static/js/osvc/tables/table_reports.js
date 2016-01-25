table_metrics_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/charts/ajax_metrics_admin',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'metric_name', 'metric_sql', 'metric_col_value_index', 'metric_col_instance_index', 'metric_col_instance_label', 'metric_created', 'metric_author'],
     'colprops': {'metric_col_instance_label': {'field': 'metric_col_instance_label', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Instance label', '_class': '', 'table': 'metrics', 'display': 1, 'default_filter': ''}, 'metric_col_value_index': {'field': 'metric_col_value_index', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Value column index', '_class': '', 'table': 'metrics', 'display': 1, 'default_filter': ''}, 'metric_sql': {'field': 'metric_sql', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'SQL request', '_class': 'sql', 'table': 'metrics', 'display': 1, 'default_filter': ''}, 'metric_name': {'field': 'metric_name', 'filter_redirect': '', 'force_filter': '', 'img': 'prov', '_dataclass': '', 'title': 'Name', '_class': 'metric_name', 'table': 'metrics', 'display': 1, 'default_filter': ''}, 'metric_col_instance_index': {'field': 'metric_col_instance_index', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Instance column index', '_class': '', 'table': 'metrics', 'display': 1, 'default_filter': ''}, 'metric_author': {'field': 'metric_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'metrics', 'display': 0, 'default_filter': ''}, 'metric_created': {'field': 'metric_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Created on', '_class': '', 'table': 'metrics', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'metrics', 'display': 1, 'default_filter': ''}},
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
     'events': ['metrics_change'],
     'request_vars': {}
}

function table_metrics(divid, options) {
  var _options = {"id": "metrics"}
  $.extend(true, _options, table_metrics_defaults, options)
  _options.divid = divid
  _options.caller = "table_metrics"
  table_init(_options)
}

table_charts_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/charts/ajax_charts_admin',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'chart_name', 'chart_yaml'],
     'colprops': {'chart_name': {'field': 'chart_name', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Name', '_class': 'chart_name', 'table': 'charts', 'display': 1, 'default_filter': ''}, 'chart_yaml': {'field': 'chart_yaml', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Definition', '_class': 'yaml', 'table': 'charts', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'charts', 'display': 1, 'default_filter': ''}},
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
     'events': ['charts_change'],
     'request_vars': {}
}

function table_charts(divid, options) {
  var _options = {"id": "charts"}
  $.extend(true, _options, table_charts_defaults, options)
  _options.divid = divid
  _options.caller = "table_charts"
  table_init(_options)
}


table_reports_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/charts/ajax_reports_admin',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'report_name', 'report_yaml'],
     'colprops': {'report_yaml': {'field': 'report_yaml', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Definition', '_class': 'yaml', 'table': 'reports', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'reports', 'display': 1, 'default_filter': ''}, 'report_name': {'field': 'report_name', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Name', '_class': 'report_name', 'table': 'reports', 'display': 1, 'default_filter': ''}},
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
     'events': ['reports_change'],
     'request_vars': {}
}

function table_reports(divid, options) {
  var _options = {"id": "reports"}
  $.extend(true, _options, table_reports_defaults, options)
  _options.divid = divid
  _options.caller = "table_reports"
  table_init(_options)
}


