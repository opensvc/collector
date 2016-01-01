table_forms_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/forms/ajax_forms_admin',
     'span': ['id'],
     'force_cols': ['id', 'form_type'],
     'columns': ['id', 'form_name', 'form_type', 'form_folder', 'form_team_responsible', 'form_team_publication', 'form_yaml', 'form_created', 'form_author'],
     'colprops': {'form_author': {'field': 'form_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'v_forms', 'display': 0, 'default_filter': ''}, 'form_team_responsible': {'field': 'form_team_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team responsible', '_class': 'groups', 'table': 'v_forms', 'display': 1, 'default_filter': ''}, 'form_yaml': {'field': 'form_yaml', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Definition', '_class': 'yaml', 'table': 'v_forms', 'display': 1, 'default_filter': ''}, 'form_created': {'field': 'form_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Created on', '_class': 'datetime_no_age', 'table': 'v_forms', 'display': 0, 'default_filter': ''}, 'form_team_publication': {'field': 'form_team_publication', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team publication', '_class': 'groups', 'table': 'v_forms', 'display': 1, 'default_filter': ''}, 'form_type': {'field': 'form_type', 'filter_redirect': '', 'force_filter': '', 'img': 'edit16', '_dataclass': '', 'title': 'Type', '_class': '', 'table': 'v_forms', 'display': 1, 'default_filter': ''}, 'form_name': {'field': 'form_name', 'filter_redirect': '', 'force_filter': '', 'img': 'prov', '_dataclass': '', 'title': 'Name', '_class': 'form_name', 'table': 'v_forms', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_forms', 'display': 0, 'default_filter': ''}, 'form_folder': {'field': 'form_folder', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Folder', '_class': '', 'table': 'v_forms', 'display': 1, 'default_filter': ''}},
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
     'events': ['forms_change'],
     'request_vars': {}
}

function table_forms(divid, options) {
  var _options = {"id": "forms"}
  $.extend(true, _options, table_forms_defaults, options)
  _options.divid = divid
  _options.caller = "table_forms"
  table_init(_options)
}

