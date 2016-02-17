function table_tagattach(divid, options) {
	var defaults = {
		'id': 'tagattach',
		'name': 'tagattach',
		'caller': 'table_tagattach',
		'divid': divid,
		'ajax_url': '/init/tags/ajax_tagattach',
		'span': ['tag_id'],
		'force_cols': ['ckid'],
		'columns': ['tag_id', 'tag_name', 'nodename', 'svcname', 'created'],
		'default_columns': ['tag_name', 'nodename', 'svcname', 'created'],
		'wsable': true,
		'events': ['tags', 'node_tags_change', 'svc_tags_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

