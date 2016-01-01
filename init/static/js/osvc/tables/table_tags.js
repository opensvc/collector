table_tags_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/tags/ajax_tags',
     'span': ['id'],
     'force_cols': ['id', 'tag_name'],
     'columns': ['id', 'tag_name', 'tag_exclude', 'tag_created'],
     'colprops': {'tag_exclude': {'field': 'tag_exclude', 'filter_redirect': '', 'force_filter': '', 'img': 'tag16', '_dataclass': '', 'title': 'Tag exclude', '_class': 'tag_exclude', 'table': 'tags', 'display': 1, 'default_filter': ''}, 'tag_name': {'field': 'tag_name', 'filter_redirect': '', 'force_filter': '', 'img': 'tag16', '_dataclass': '', 'title': 'Tag name', '_class': '', 'table': 'tags', 'display': 1, 'default_filter': ''}, 'tag_created': {'field': 'tag_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Tag created', '_class': 'datetime_no_age', 'table': 'tags', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'tag16', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'tags', 'display': 0, 'default_filter': ''}},
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
     'events': ['tags_change'],
     'request_vars': {}
}

function table_tags(divid, options) {
  var _options = {"id": "tags"}
  $.extend(true, _options, table_tags_defaults, options)
  _options.divid = divid
  _options.caller = "table_tags"
  table_init(_options)
}

