table_replication_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/replication/ajax_replication_status',
     'span': [],
     'force_cols': [],
     'columns': ['mode', 'remote', 'table_schema', 'table_name', 'need_resync', 'current_cksum', 'last_cksum', 'table_updated'],
     'colprops': {'remote': {'field': 'remote', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Remote', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'table_updated': {'field': 'table_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'table_schema': {'field': 'table_schema', 'filter_redirect': '', 'force_filter': '', 'img': 'db16', '_dataclass': '', 'title': 'Database', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'current_cksum': {'field': 'current_cksum', 'filter_redirect': '', 'force_filter': '', 'img': 'db16', '_dataclass': '', 'title': 'Current csum', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'table_name': {'field': 'table_name', 'filter_redirect': '', 'force_filter': '', 'img': 'db16', '_dataclass': '', 'title': 'Table', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'mode': {'field': 'mode', 'filter_redirect': '', 'force_filter': '', 'img': 'repl16', '_dataclass': '', 'title': 'Mode', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'need_resync': {'field': 'need_resync', 'filter_redirect': '', 'force_filter': '', 'img': 'repl16', '_dataclass': '', 'title': 'Need resync', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}, 'last_cksum': {'field': 'last_cksum', 'filter_redirect': '', 'force_filter': '', 'img': 'db16', '_dataclass': '', 'title': 'Last csum', '_class': '', 'table': '', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': false,
     'filterable': false,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': false,
     'pageable': false,
     'on_change': false,
     'events': [],
     'request_vars': {}
}

function table_replication(divid, options) {
  var _options = {"id": "replication"}
  $.extend(true, _options, table_replication_defaults, options)
  _options.divid = divid
  _options.caller = "table_replication"
  table_init(_options)
}

