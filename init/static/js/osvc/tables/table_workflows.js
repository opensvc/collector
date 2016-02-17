function table_workflows(divid, options) {
	var defaults = {
		'name': "workflows",
		'id': "workflows",
		'caller': "table_workflows",
		'divid': divid,
		'checkboxes': false,
		'ajax_url': '/init/forms/ajax_workflows',
		'span': ['form_head_id'],
		'force_cols': ["form_head_id"],
		'columns': ['form_head_id', 'form_name', 'last_form_id', 'last_form_name', 'form_folder', 'status', 'steps', 'creator', 'last_assignee', 'create_date', 'last_update', 'form_yaml'],
		'default_columns': ['form_head_id', 'form_name', 'last_form_id', 'last_form_name', 'status', 'steps', 'creator', 'last_assignee', 'create_date', 'last_update'],
		'wsable': true,
		'events': ["forms_store_change"]
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_workflows_assigned_to_me(divid, options) {
	$.when(osvc.user_loaded).then(function() {
		var me = _self.first_name + " " + _self.last_name
		var notme = "!" + me
		for (var i=0; i<_groups.length; i++) {
			if (_groups[i].privilege == true) {
				continue
			}
			me += "|" + _groups[i].role
			notme += "&!" + _groups[i].role
		}
		var defaults = {
			"id": "workflows_atm",
			"caller": "table_workflows_assigned_to_me",
			"colprops": {
				"status": {
					"force_filter": "!closed",
				},
				"last_assignee": {
					"force_filter": me,
				}
			}
		}
		var _options = $.extend({}, defaults, options)
		return table_workflows(divid, _options)
	})
}

function table_workflows_assigned_to_tiers(divid, options) {
	$.when(osvc.user_loaded).then(function() {
		var me = _self.first_name + " " + _self.last_name
		var notme = "!" + me
		for (var i=0; i<_groups.length; i++) {
			if (_groups[i].privilege == true) {
				continue
			}
			me += "|" + _groups[i].role
			notme += "&!" + _groups[i].role
		}
		var defaults = {
			"id": "workflows_att",
			"caller": "table_workflows_assigned_to_tiers",
			"colprops": {
				"status": {
					"force_filter": "!closed",
				},
				"last_assignee": {
					"force_filter": notme,
				},
				"creator": {
					"force_filter": me,
				}
			}
		}
		var _options = $.extend({}, defaults, options)
		return table_workflows(divid, _options)
	})
}

