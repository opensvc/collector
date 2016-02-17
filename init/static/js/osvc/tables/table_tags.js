function table_tags(divid, options) {
	var defaults = {
		'name': "tags",
		'id': "tags",
		'divid': divid,
		'caller': "table_tags",
		'ajax_url': '/init/tags/ajax_tags',
		'span': ['id'],
		'force_cols': ['id', 'tag_name'],
		'columns': ['id', 'tag_name', 'tag_exclude', 'tag_created'],
		'default_columns': ['tag_name', 'tag_exclude', 'tag_created'],
		'wsable': true,
		'events': ['tags_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

