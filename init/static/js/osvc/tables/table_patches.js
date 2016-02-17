function table_patches(divid, options) {
	var defaults = {
		'id': "pathces",
		'divid': divid,
		'caller': "table_patches",
		'name': "patches",
		'ajax_url': '/init/patches/ajax_patches',
		'span': ['id'],
		'force_cols': ['os_name'],
		'columns': [].concat(['nodename', 'id', 'patch_num', 'patch_rev', 'patch_install_date', 'patch_updated'], objcols.node),
		'default_columns': ['nodename', 'id', 'patch_num', 'patch_rev', 'patch_install_date', 'patch_updated'],
		'wsable': false,
		'events': ['patches_change']
	}
	var _options = $.extend({}, defaults, options)
	table_init(_options)
}

