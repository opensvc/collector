table_users_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/users/ajax_users',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['manager', 'id', 'fullname', 'email', 'phone_work', 'primary_group', 'groups', 'lock_filter', 'fset_name', 'domains', 'last'],
     'colprops': {'primary_group': {'field': 'primary_group', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Primary group', '_class': '', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'last': {'field': 'last', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last events', '_class': 'datetime_no_age', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'fset_name': {'field': 'fset_name', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Filterset', '_class': '', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'phone_work': {'field': 'phone_work', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Work desk phone', '_class': '', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'email': {'field': 'email', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Email', '_class': '', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'manager': {'field': 'manager', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Role', '_class': 'users_role', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'groups': {'field': 'groups', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Groups', '_class': 'groups', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'domains': {'field': 'domains', 'filter_redirect': '', 'force_filter': '', 'img': 'filter16', '_dataclass': '', 'title': 'Domains', '_class': 'users_domain', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'fullname': {'field': 'fullname', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Full name', '_class': 'username', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'User Id', '_class': '', 'table': 'v_users', 'display': 1, 'default_filter': ''}, 'lock_filter': {'field': 'lock_filter', 'filter_redirect': '', 'force_filter': '', 'img': 'attach16', '_dataclass': '', 'title': 'Lock filterset', '_class': 'boolean', 'table': 'v_users', 'display': 1, 'default_filter': ''}},
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
     'events': ['auth_user_change'],
     'request_vars': {}
}

function table_users(divid, options) {
  var _options = {"id": "users"}
  $.extend(true, _options, table_users_defaults, options)
  _options.divid = divid
  _options.caller = "table_users"
  table_init(_options)
}

