table_log_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/log/ajax_log',
     'span': ['id'],
     'force_cols': ['id', 'log_fmt', 'log_dict'],
     'columns': ['id', 'log_date', 'log_icons', 'log_level', 'log_svcname', 'log_nodename', 'log_user', 'log_action', 'log_evt', 'log_fmt', 'log_dict', 'log_gtalk_sent', 'log_email_sent'],
     'colprops': {'log_nodename': {'field': 'log_nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': '', 'display': 1, 'default_filter': ''}, 'log_entry_id': {'field': 'log_entry_id', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Entry id', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'log_evt': {'field': 'dummy', 'filter_redirect': 'log_dict', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Event', '_class': 'log_event', 'table': '', 'display': 1, 'default_filter': ''}, 'log_user': {'field': 'log_user', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'User', '_class': 'username', 'table': '', 'display': 1, 'default_filter': ''}, 'log_date': {'field': 'log_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Date', '_class': 'datetime_no_age', 'table': '', 'display': 1, 'default_filter': '>-1d'}, 'log_gtalk_sent': {'field': 'log_gtalk_sent', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Sent via gtalk', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'log_level': {'field': 'log_level', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Severity', '_class': 'log_level', 'table': '', 'display': 1, 'default_filter': ''}, 'log_icons': {'field': 'log_icons', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Icons', '_class': 'log_icons', 'table': '', 'display': 1, 'default_filter': ''}, 'log_email_sent': {'field': 'log_email_sent', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Sent via email', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'log_dict': {'field': 'log_dict', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Dictionary', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'log_svcname': {'field': 'log_svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': '', 'display': 1, 'default_filter': ''}, 'log_fmt': {'field': 'log_fmt', 'filter_redirect': '', 'force_filter': '', 'img': 'log16', '_dataclass': '', 'title': 'Format', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Id', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'log_action': {'field': 'log_action', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Action', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': false,
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

function table_log(divid, options) {
  var _options = {"id": "log"}
  $.extend(true, _options, table_log_defaults, options)
  _options.divid = divid
  _options.caller = "table_log"

  wsh[_options.id] = function(data) {
    if (data["event"] == "log_change") {
      _data = []
      _data.push({"key": "id", "val": data["data"]["id"], "op": "="})
      osvc.tables[_options.id].insert(_data)
    }
  }

  table_init(_options)
}

function table_log_node(divid, nodename) {
  var id = "log_" + nodename.replace(/[\.-]/g, "_")
  var f = id+"_f_log_nodename"
  var request_vars = {}
  request_vars[f] = nodename
  table_log(divid, {
    "id": id,
    "caller": "table_log_node",
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

function table_log_svc(divid, svcname) {
  var id = "log_" + svcname.replace(/[\.-]/g, "_")
  var f = id+"_f_log_svcname"
  var request_vars = {}
  request_vars[f] = svcname
  table_log(divid, {
    "id": id,
    "caller": "table_log_svc",
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
