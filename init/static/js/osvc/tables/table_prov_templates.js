table_prov_templates_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/provisioning/ajax_prov_admin',
     'span': [],
     'force_cols': ['id', 'tpl_name'],
     'columns': ['id', 'tpl_name', 'tpl_command', 'tpl_comment', 'tpl_created', 'tpl_author', 'tpl_team_responsible'],
     'colprops': {'tpl_created': {'field': 'tpl_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Created on', '_class': '', 'table': 'v_prov_templates', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'v_prov_templates', 'display': 0, 'default_filter': ''}, 'tpl_comment': {'field': 'tpl_comment', 'filter_redirect': '', 'force_filter': '', 'img': 'edit16', '_dataclass': '', 'title': 'Comment', '_class': '', 'table': 'v_prov_templates', 'display': 1, 'default_filter': ''}, 'tpl_author': {'field': 'tpl_author', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Author', '_class': '', 'table': 'v_prov_templates', 'display': 0, 'default_filter': ''}, 'tpl_team_responsible': {'field': 'tpl_team_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team responsible', '_class': 'groups', 'table': 'v_prov_templates', 'display': 1, 'default_filter': ''}, 'tpl_name': {'field': 'tpl_name', 'filter_redirect': '', 'force_filter': '', 'img': 'prov', '_dataclass': '', 'title': 'Name', '_class': 'prov_template', 'table': 'v_prov_templates', 'display': 1, 'default_filter': ''}, 'tpl_command': {'field': 'tpl_command', 'filter_redirect': '', 'force_filter': '', 'img': 'action16', '_dataclass': '', 'title': 'Command', '_class': 'tpl_command', 'table': 'v_prov_templates', 'display': 1, 'default_filter': ''}},
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
     'events': ['prov_templates_change', 'prov_template_responsible_change'],
     'request_vars': {}
}

function table_prov_templates(divid, options) {
  var _options = {"id": "templates"}
  $.extend(true, _options, table_prov_templates_defaults, options)
  _options.divid = divid
  _options.caller = "table_prov_templates"
  table_init(_options)
}

