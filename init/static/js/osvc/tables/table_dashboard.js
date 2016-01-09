table_dashboard_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/dashboard/ajax_dashboard',
     'span': ['id'],
     'columns': ['id', 'dash_severity', 'dash_links', 'dash_type', 'dash_svcname', 'dash_nodename', 'dash_env', 'dash_entry', 'dash_created', 'dash_updated', 'dash_md5'],
     'colprops': {'dash_updated': {'field': 'dash_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last update', '_class': 'datetime_no_age', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_env': {'field': 'dash_env', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Env', '_class': 'env', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_type': {'field': 'dash_type', 'filter_redirect': '', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Type', '_class': 'alert_type', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_nodename': {'field': 'dash_nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_links': {'field': 'dummy', 'filter_redirect': '', 'force_filter': '', 'img': 'dashlink16', '_dataclass': '', 'title': 'Links', '_class': 'dash_links', 'table': '', 'display': 1, 'default_filter': ''}, 'dash_md5': {'field': 'dash_md5', 'filter_redirect': '', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Signature', '_class': '', 'table': 'dashboard', 'display': 0, 'default_filter': ''}, 'dash_dict': {'field': 'dash_dict', 'filter_redirect': '', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Dictionary', '_class': '', 'table': 'dashboard', 'display': 0, 'default_filter': ''}, 'dash_severity': {'field': 'dash_severity', 'filter_redirect': '', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Severity', '_class': 'dash_severity', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_created': {'field': 'dash_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Begin date', '_class': 'datetime_no_age', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_svcname': {'field': 'dash_svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_entry': {'field': 'dummy', 'filter_redirect': 'dash_dict', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Alert', '_class': 'dash_entry', 'table': 'dashboard', 'display': 1, 'default_filter': ''}, 'dash_fmt': {'field': 'dash_fmt', 'filter_redirect': '', 'force_filter': '', 'img': 'alert16', '_dataclass': '', 'title': 'Format', '_class': '', 'table': 'dashboard', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Alert id', '_class': '', 'table': 'dashboard', 'display': 0, 'default_filter': ''}},
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
     'events': ['dashboard_change'],
     'request_vars': {}
}

function table_dashboard(divid, options) {
  var _options = {"id": "dashboard"}
  $.extend(true, _options, table_dashboard_defaults, options)
  _options.divid = divid
  _options.caller = "table_dashboard"
  table_init(_options)
}

function table_dashboard_node(divid, nodename) {
  var id = "dashboard_" + nodename.replace(/[\.-]/g, "_")
  var f = id+"_f_dash_nodename"
  var request_vars = {}
  request_vars[f] = nodename
  table_dashboard(divid, {
    "id": id,
    "caller": "table_dashboard_node",
    "request_vars": request_vars,
    "visible_columns": ['dash_updated', 'dash_type', 'dash_links', 'dash_entry', 'dash_env', 'dash_svcname', 'dash_severity', 'dash_created'],
    "volatile_filters": true,
    "bookmarkable": false,
    "refreshable": false,
    "linkable": false,
    "exportable": false,
    "pageable": false,
    "columnable": false,
    "commonalityable": false,
    "filterable": false,
    "wsable": false
  })
}

function table_dashboard_svc(divid, svcname) {
  var id = "dashboard_" + svcname.replace(/[\.-]/g, "_")
  var f = id+"_f_dash_svcname"
  var request_vars = {}
  request_vars[f] = svcname
  table_dashboard(divid, {
    "id": id,
    "caller": "table_dashboard_svc",
    "request_vars": request_vars,
    "visible_columns": ['dash_updated', 'dash_type', 'dash_links', 'dash_entry', 'dash_env', 'dash_nodename', 'dash_severity', 'dash_created'],
    "volatile_filters": true,
    "bookmarkable": false,
    "refreshable": false,
    "linkable": false,
    "exportable": false,
    "pageable": false,
    "columnable": false,
    "commonalityable": false,
    "filterable": false,
    "wsable": false
  })
}
