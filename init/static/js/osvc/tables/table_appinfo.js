table_appinfo_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/appinfo/ajax_appinfo',
     'span': ['app_svcname', 'app_nodename', 'app_launcher'],
     'columns': ['id', 'app_svcname', 'app_nodename', 'app_launcher', 'app_key', 'app_value', 'app_updated'],
     'force_cols': ['id'],
     'colprops': {'app_updated': {'field': 'app_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last update', '_class': 'datetime_daily', 'table': 'appinfo', 'display': 1, 'default_filter': ''}, 'app_launcher': {'field': 'app_launcher', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Launcher', '_class': '', 'table': 'appinfo', 'display': 1, 'default_filter': ''}, 'app_key': {'field': 'app_key', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Key', '_class': 'appinfo_key', 'table': 'appinfo', 'display': 1, 'default_filter': ''}, 'app_value': {'field': 'app_value', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Value', '_class': 'appinfo_value', 'table': 'appinfo', 'display': 1, 'default_filter': ''}, 'app_svcname': {'field': 'app_svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'appinfo', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'appinfo', 'display': 0, 'default_filter': ''}, 'app_nodename': {'field': 'app_nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'hw16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': 'appinfo', 'display': 1, 'default_filter': ''}},
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
     'events': ['appinfo_change'],
     'request_vars': {}
}

function table_appinfo(divid, options) {
  var _options = {"id": "appinfo"}
  $.extend(true, _options, table_appinfo_defaults, options)
  _options.divid = divid
  _options.caller = "table_appinfo"
  table_init(_options)
}

