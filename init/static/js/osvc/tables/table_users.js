function table_users(divid, options) {
	var defaults = {
		'name': "users",
		'id': "users",
		'caller': "table_users",
		'divid': divid,
		'ajax_url': '/init/users/ajax_users',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['manager', 'id', 'fullname', 'email', 'phone_work', 'primary_group', 'groups', 'lock_filter', 'fset_name', 'domains', 'last'],
		'default_columns': ['manager', 'fullname', 'email', 'phone_work', 'primary_group', 'groups', 'lock_filter', 'fset_name', 'domains', 'last'],
		'wsable': true,
		'events': ['auth_user_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

