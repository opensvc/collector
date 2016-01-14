table_obsolescence_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/obsolescence/ajax_obs',
     'span': [],
     'force_cols': ['id', 'obs_type', 'obs_name'],
     'columns': ['id', 'obs_count', 'obs_type', 'obs_name', 'obs_warn_date', 'obs_alert_date'],
     'colprops': {'obs_count': {'field': 'obs_count', 'filter_redirect': '', 'force_filter': '', 'img': 'obs16', '_dataclass': '', 'title': 'Count', '_class': 'obs_count', 'table': 'v_obsolescence', 'display': 1, 'default_filter': ''}, 'obs_name': {'field': 'obs_name', 'filter_redirect': '', 'force_filter': '', 'img': 'obs16', '_dataclass': '', 'title': 'Name', '_class': '', 'table': 'v_obsolescence', 'display': 1, 'default_filter': ''}, 'obs_alert_date': {'field': 'obs_alert_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Alert date', '_class': 'datetime_no_age', 'table': 'v_obsolescence', 'display': 1, 'default_filter': ''}, 'obs_warn_date': {'field': 'obs_warn_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Warn date', '_class': 'datetime_no_age', 'table': 'v_obsolescence', 'display': 1, 'default_filter': ''}, 'obs_type': {'field': 'obs_type', 'filter_redirect': '', 'force_filter': '', 'img': 'obs16', '_dataclass': '', 'title': 'Type', '_class': 'obs_type', 'table': 'v_obsolescence', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_obsolescence', 'display': 0, 'default_filter': ''}},
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
     'events': ['obsolescence_change'],
     'request_vars': {}
}

function table_obsolescence(divid, options) {
  var _options = {"id": "obs"}
  $.extend(true, _options, table_obsolescence_defaults, options)
  _options.divid = divid
  _options.caller = "table_obsolescence"
  table_init(_options)
}

