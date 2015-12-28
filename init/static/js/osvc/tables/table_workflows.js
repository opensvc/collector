table_workflows_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/forms/ajax_workflows',
     'span': ['form_head_id'],
     'force_cols': [],
     'columns': ['form_head_id', 'form_name', 'last_form_id', 'last_form_name', 'form_folder', 'status', 'steps', 'creator', 'last_assignee', 'create_date', 'last_update', 'form_yaml'],
     'colprops': {
	'status': {'field': 'status', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Status', '_class': '', 'table': 'workflows', 'display': 1, 'default_filter': ''},
	'create_date': {'field': 'create_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Created on', '_class': 'datetime_no_age', 'table': 'workflows', 'display': 1, 'default_filter': ''},
	'creator': {'field': 'creator', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Creator', '_class': '', 'table': 'workflows', 'display': 1, 'default_filter': ''},
	'last_assignee': {'field': 'last_assignee', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Last assignee', '_class': '', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'last_update': {'field': 'last_update', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last updated', '_class': 'datetime_no_age', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'form_head_id': {'field': 'form_head_id', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Head form id', '_class': 'form_id', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'last_form_id': {'field': 'last_form_id', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Last form id', '_class': 'form_id', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'steps': {'field': 'steps', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Steps', '_class': '', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'form_name': {'field': 'form_name', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Name', '_class': '', 'table': 'forms_revisions', 'display': 1, 'default_filter': ''}, 'last_form_name': {'field': 'last_form_name', 'filter_redirect': '', 'force_filter': '', 'img': 'wf16', '_dataclass': '', 'title': 'Last form name', '_class': '', 'table': 'workflows', 'display': 1, 'default_filter': ''}, 'form_yaml': {'field': 'form_yaml', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Definition', '_class': 'yaml', 'table': 'forms_revisions', 'display': 0, 'default_filter': ''}, 'form_folder': {'field': 'form_folder', 'filter_redirect': '', 'force_filter': '', 'img': 'hd16', '_dataclass': '', 'title': 'Folder', '_class': '', 'table': 'forms_revisions', 'display': 1, 'default_filter': ''}},
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
     'events': [],
     'request_vars': {}
}

function table_workflows(divid, options) {
  var _options = {"id": "workflows"}
  $.extend(true, _options, table_workflows_defaults, options)
  _options.divid = divid
  _options.caller = "table_workflows"
  table_init(_options)
}

function table_workflows_assigned_to_me(divid, options) {
  var _options = {"id": "workflows_atm"}
  var me = _self.first_name + " " + _self.last_name
  var notme = "!" + me
  for (var i=0; i<_groups.length; i++) {
    if (_groups[i].privilege == true) {
      continue
    }
    me += "|" + _groups[i].role
    notme += "&!" + _groups[i].role
  }
  $.extend(true, _options, table_workflows_defaults, options)
  _options.divid = divid
  _options.caller = "table_workflows_assigned_to_me"
  _options.request_vars["workflows_atm_f_status"] = "!closed"
  _options.request_vars["workflows_atm_f_last_assignee"] = me
  table_init(_options)
}

function table_workflows_assigned_to_tiers(divid, options) {
  var _options = {"id": "workflows_att"}
  var me = _self.first_name + " " + _self.last_name
  var notme = "!" + me
  for (var i=0; i<_groups.length; i++) {
    if (_groups[i].privilege == true) {
      continue
    }
    me += "|" + _groups[i].role
    notme += "&!" + _groups[i].role
  }
  $.extend(true, _options, table_workflows_defaults, options)
  _options.divid = divid
  _options.caller = "table_workflows_assigned_to_tiers"
  _options.request_vars["workflows_att_f_status"] = "!closed"
  _options.request_vars["workflows_att_f_last_assignee"] = notme
  _options.request_vars["workflows_att_f_creator"] = me
  table_init(_options)
}

