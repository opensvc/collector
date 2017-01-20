//
// disk group
//
function diskgroup_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.disk
	o.options.icon = "diskgroup"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		services_osvcgetrest("R_ARRAY_DISKGROUP", [o.options.array_name, o.options.dg_name], {"meta": "0"}, function(jd) {
			o.data = jd.data[0]
			o._load()
		})
	})

	o._load = function() {
		var title = o.data.dg_name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon diskgroup"
		})
		o.tabs[i].callback = function(divid) {
			diskgroup_properties(divid, {"dg_id": o.data.id})
		}

		// tab quotas
		i = o.register_tab({
			"title": "array_tabs.quotas",
			"title_class": "icon quota16"
		})
		o.tabs[i].callback = function(divid) {
			table_quota_array_dg(divid, o.options.array_name, o.options.dg_name)
		}

		// tab usage
		i = o.register_tab({
			"title": "node_tabs.stats",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			$.ajax({
				"url": "/init/disks/ajax_array_dg",
				"type": "POST",
				"success": function(msg) {$("#"+divid).html(msg)},
				"data": {"array": o.options.array_name, "dg": o.data.dg_name, "rowid": divid}
			})
		}
		o.set_tab(o.options.tab)
	}
	return o
}

function diskgroup_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id = o.div.find("#id")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_size = o.div.find("#dg_size")
		o.info_dg_free = o.div.find("#dg_free")
		o.info_dg_used = o.div.find("#dg_used")
		o.info_dg_reserved = o.div.find("#dg_reserved")
		o.info_dg_updated = o.div.find("#dg_updated")
		o.info_array_name = o.div.find("#array_name")
		o.info_array_model = o.div.find("#array_model")
		o.info_array_firmware = o.div.find("#array_firmware")
		o.load_diskgroup()
	}

	o.load_diskgroup = function() {
		services_osvcgetrest("R_ARRAY_DISKGROUP", [0, o.options.dg_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_diskgroup()
		})
	}

	o._load_diskgroup = function() {
		o.info_id.html(o.data.id)
		o.info_dg_name.html(o.data.dg_name)
		o.info_dg_updated.html(osvc_date_from_collector(o.data.dg_updated))
		$.data(o.info_dg_free[0], "v", o.data.dg_free)
		$.data(o.info_dg_size[0], "v", o.data.dg_size)
		$.data(o.info_dg_used[0], "v", o.data.dg_used)
		$.data(o.info_dg_reserved[0], "v", o.data.dg_reserved)
		cell_decorator_size_mb(o.info_dg_free)
		cell_decorator_size_mb(o.info_dg_size)
		cell_decorator_size_mb(o.info_dg_used)
		cell_decorator_size_mb(o.info_dg_reserved)

		services_osvcgetrest("R_ARRAY", [o.data.array_id], "", function(jd) {
			o.info_array_name.html(jd.data[0].array_name)
			o.info_array_model.html(jd.data[0].array_model)
			o.info_array_firmware.html(jd.data[0].array_firmware)
		})
	}

	o.div.load("/init/static/views/diskgroup_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

