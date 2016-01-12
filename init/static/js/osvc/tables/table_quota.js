table_quota_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/disks/ajax_quota',
     'span': ['array_name', 'dg_name', 'app'],
     'force_cols': ['id'],
     'columns': ['id', 'array_name', 'array_model', 'dg_name', 'dg_size', 'dg_reserved', 'dg_reservable', 'dg_used', 'dg_free', 'app', 'quota', 'quota_used'],
     'colprops': {'array_id': {'field': 'array_id', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Array Id', '_class': '', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_size': {'field': 'dg_size', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Size', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_free': {'field': 'dg_free', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Free', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_reserved': {'field': 'dg_reserved', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Reserved', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'app': {'field': 'app', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'App', '_class': 'app', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_name': {'field': 'dg_name', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Array Disk Group', '_class': 'disk_array_dg', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'app_id': {'field': 'app_id', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'App Id', '_class': '', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'quota': {'field': 'quota', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Quota', '_class': 'quota numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_disk_quota', 'display': 0, 'default_filter': ''}, 'array_model': {'field': 'array_model', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': 'bluer', 'title': 'Array Model', '_class': '', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_id': {'field': 'dg_id', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Array Disk Group Id', '_class': '', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'quota_used': {'field': 'quota_used', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Quota Used', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_reservable': {'field': 'dg_reservable', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Reservable', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'array_name': {'field': 'array_name', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Array', '_class': 'disk_array', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}, 'dg_used': {'field': 'dg_used', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Used', '_class': 'numeric size_mb', 'table': 'v_disk_quota', 'display': 1, 'default_filter': ''}},
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
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': ['stor_array_dg_quota_change'],
     'request_vars': {}
}

function table_quota(divid, options) {
  var _options = {"id": "quota"}
  $.extend(true, _options, table_quota_defaults, options)
  _options.divid = divid
  _options.caller = "table_quota"
  table_init(_options)
}

function table_quota_array(divid, array_name) {
  var id = "quota_" + array_name.replace(/[ \.-]/g, "_")
  var f = id+"_f_array_name"
  var request_vars = {}
  request_vars[f] = array_name
  table_quota(divid, {
    "id": id,
    "caller": "table_quota_array",
    "request_vars": request_vars,
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

function table_quota_app(divid, app) {
  var id = "quota_" + app.replace(/[ \.-]/g, "_")
  var f = id+"_f_app"
  var request_vars = {}
  request_vars[f] = app
  table_quota(divid, {
    "id": id,
    "caller": "table_quota_app",
    "request_vars": request_vars,
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

function table_quota_array_dg(divid, array_name, dg_name) {
  var id = "quota_" + array_name.replace(/[ \.-]/g, "_") + dg_name.replace(/[ \.-]/g, "_")
  var request_vars = {}
  var f1 = id+"_f_array_name"
  var f2 = id+"_f_dg_name"
  request_vars[f1] = array_name
  request_vars[f2] = dg_name
  table_quota(divid, {
    "id": id,
    "caller": "table_quota_array_dg",
    "request_vars": request_vars,
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


