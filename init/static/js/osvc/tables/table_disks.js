function table_disks_charts(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "disks_charts",
		'caller': "view_disks",
		'name': "disks_charts",
		'checkboxes': false,
		'ajax_url': '/init/disks/ajax_disk_charts',
		'span': ['chart'],
		'force_cols': [],
		'columns': ['chart'],
		'default_columns': ['chart'],
		'colprops': {
			'chart': {"_class": "disks_charts"}
		},
		'parent_tables': ['disks'],
		'linkable': false,
		'dbfilterable': false,
		'filterable': false,
		'refreshable': false,
		'bookmarkable': false,
		'exportable': false,
		'columnable': false,
		'commonalityable': false,
		'headers': false,
		'pageable': false
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_disks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_disks",
		'id': "disks",
		'name': "disks",
		'ajax_url': '/init/disks/ajax_disks',
		'span': ['disk_id', 'disk_size', 'disk_alloc', 'disk_arrayid', 'disk_devid', 'disk_name', 'disk_raid', 'disk_group', 'array_model'],
		'force_cols': ['id', 'os_name'],
		'columns': ['disk_id', 'disk_region', 'disk_vendor', 'disk_model', 'app', 'disk_nodename', 'disk_svcname', 'disk_local', 'disk_dg', 'svcdisk_updated', 'disk_used', 'disk_size', 'disk_alloc', 'disk_name', 'disk_devid', 'disk_raid', 'disk_group', 'disk_arrayid', 'disk_level', 'array_model', 'disk_created', 'disk_updated', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2'],
		'default_columns': ["app", "array_model", "disk_alloc", "disk_arrayid", "disk_created", "disk_devid", "disk_dg", "disk_group", "disk_id", "disk_level", "disk_local", "disk_model", "disk_name", "disk_nodename", "disk_raid", "disk_size", "disk_svcname", "disk_updated", "disk_used", "disk_vendor", "svcdisk_updated"],
		'child_tables': ['charts'],
		'wsable': true,
		'events': ['disks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_disks(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/disks.html", function() {
		$(this).i18n()
		table_disks_charts("charts", options)
		table_disks("disks", options)
		$("#charts_a").bind("click", function() {
			if (!$("#charts").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#charts").show()
				table_disks_charts("charts", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#charts").hide()
			}
		})
	})
}

