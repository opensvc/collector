table_action_queue_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/action_queue/ajax_actions',
     'span': ['id'],
     'columns': ['id', 'status', 'nodename', 'svcname', 'connect_to', 'username', 'form_id', 'action_type', 'date_queued', 'date_dequeued', 'ret', 'command', 'stdout', 'stderr'],
     'colprops': {'status': {'field': 'status', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Status', '_class': 'action_q_status', 'table': '', 'display': 1, 'default_filter': ''}, 'username': {'field': 'username', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'User name', '_class': 'username', 'table': '', 'display': 1, 'default_filter': ''}, 'date_queued': {'field': 'date_queued', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Queued', '_class': 'datetime_no_age', 'table': '', 'display': 1, 'default_filter': ''}, 'form_id': {'field': 'form_id', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Request form id', '_class': 'form_id', 'table': '', 'display': 1, 'default_filter': ''}, 'stdout': {'field': 'stdout', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Stdout', '_class': 'pre', 'table': '', 'display': 1, 'default_filter': ''}, 'connect_to': {'field': 'connect_to', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Connect to', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'action_type': {'field': 'action_type', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Action type', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'ret': {'field': 'ret', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Return code', '_class': 'action_q_ret', 'table': '', 'display': 1, 'default_filter': ''}, 'date_dequeued': {'field': 'date_dequeued', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Dequeued', '_class': 'datetime_no_age', 'table': '', 'display': 1, 'default_filter': ''}, 'command': {'field': 'command', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Command', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'stderr': {'field': 'stderr', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Stderr', '_class': 'pre', 'table': '', 'display': 1, 'default_filter': ''}, 'svcname': {'field': 'svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': '', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Id', '_class': '', 'table': '', 'display': 0, 'default_filter': ''}, 'nodename': {'field': 'nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'hw16', '_dataclass': '', 'title': 'Nodename', '_class': 'nodename', 'table': '', 'display': 1, 'default_filter': ''}},
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
     'events': ['action_q_change'],
     'request_vars': {}
}

function table_action_queue(divid, options) {
  var _options = {"id": "action_queue"}
  $.extend(true, _options, table_action_queue_defaults, options)
  _options.divid = divid
  _options.caller = "table_action_queue"
  table_init(_options)
}

