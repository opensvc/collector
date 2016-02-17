function table_action_queue(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': 'table_action_queue',
		'id': 'action_queue',
		'name': 'action_queue',
		'ajax_url': '/init/action_queue/ajax_actions',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'status', 'nodename', 'svcname', 'connect_to', 'username', 'form_id', 'action_type', 'date_queued', 'date_dequeued', 'ret', 'command', 'stdout', 'stderr'],
		'default_columns': ['status', 'nodename', 'svcname', 'connect_to', 'username', 'form_id', 'action_type', 'date_queued', 'date_dequeued', 'ret', 'command'],
		'colprops': {
			"action_type": {"img": "action16"},
			"status": {
				"_class": "action_q_status",
				"field": "status",
				"img": "action16",
				"title": "Status"
			}
		},
		'wsable': true,
		'events': ['action_q_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

