table_tagattach_defaults = {
     'id': 'tagattach',
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/tags/ajax_tagattach',
     'span': ['tag_id'],
     'columns': ['tag_id', 'tag_name', 'nodename', 'svcname', 'created'],
     'colprops': {'tag_name': {'field': 'tag_name', 'filter_redirect': '', 'force_filter': '', 'img': 'tag16', '_dataclass': '', 'title': 'Tag name', '_class': '', 'table': 'v_tags_full', 'display': 1, 'default_filter': ''}, 'svcname': {'field': 'svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'v_tags_full', 'display': 1, 'default_filter': ''}, 'nodename': {'field': 'nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': 'v_tags_full', 'display': 1, 'default_filter': ''}, 'tag_id': {'field': 'tag_id', 'filter_redirect': '', 'force_filter': '', 'img': 'tag16', '_dataclass': '', 'title': 'Tag id', '_class': '', 'table': 'v_tags_full', 'display': 0, 'default_filter': ''}, 'created': {'field': 'created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Attach date', '_class': 'datetime_no_age', 'table': 'v_tags_full', 'display': 1, 'default_filter': ''}},
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
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': ['tags', 'node_tags_change', 'svc_tags_change'],
     'request_vars': {}
}

function table_tagattach(divid, options) {
  var _options = {"id": "tagattach"}
  $.extend(true, _options, table_tagattach_defaults, options)
  _options.divid = divid
  _options.caller = "table_tagattach"
  table_init(_options)
}

