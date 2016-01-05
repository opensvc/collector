table_apps_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/apps/ajax_apps',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'app', 'app_domain', 'app_team_ops', 'roles', 'responsibles', 'mailto'],
     'colprops': {'mailto': {'field': 'mailto', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Mailing list', '_class': '', 'table': 'v_apps', 'display': 0, 'default_filter': ''}, 'app_domain': {'field': 'app_domain', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'App domain', '_class': '', 'table': 'v_apps', 'display': 1, 'default_filter': ''}, 'roles': {'field': 'roles', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Sysresp teams', '_class': 'groups', 'table': 'v_apps', 'display': 1, 'default_filter': ''}, 'app': {'field': 'app', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Application code', '_class': 'app', 'table': 'v_apps', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_apps', 'display': 0, 'default_filter': ''}, 'app_team_ops': {'field': 'app_team_ops', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Ops team', '_class': '', 'table': 'v_apps', 'display': 1, 'default_filter': ''}, 'responsibles': {'field': 'responsibles', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'System Responsibles', '_class': '', 'table': 'v_apps', 'display': 1, 'default_filter': ''}},
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
     'events': ['apps_change'],
     'request_vars': {}
}

function table_apps(divid, options) {
  var _options = {"id": "apps"}
  $.extend(true, _options, table_apps_defaults, options)
  _options.divid = divid
  _options.caller = "table_apps"
  table_init(_options)
}

