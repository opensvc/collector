function quota_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.disk
	o.options.icon = "quota16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		var title = o.options.quota_id
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			quota_properties(divid, o.options)
		}

		// tab usage
		i = o.register_tab({
			"title": "node_tabs.stats",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_ARRAY_DISKGROUP_QUOTA", [0, 0, o.options.quota_id], {"meta": "0"}, function(jd) {
				quota_stats(divid, jd.data[0])
			})
		}

		o.set_tab(o.options.tab)
	})

	return o
}

function quota_properties(divid, options) {
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
		o.info_array_name = o.div.find("#array_name")
		o.info_array_model = o.div.find("#array_model")
		o.info_array_firmware = o.div.find("#array_firmware")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_size = o.div.find("#dg_size")
		o.info_dg_free = o.div.find("#dg_free")
		o.info_dg_used = o.div.find("#dg_used")
		o.info_dg_reserved = o.div.find("#dg_reserved")
		o.info_app_id = o.div.find("#app_id")
		o.info_quota = o.div.find("#quota")
		o.load_quota()
	}

	o.load_quota = function() {
		services_osvcgetrest("R_ARRAY_DISKGROUP_QUOTA", [0, 0, o.options.quota_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_quota()
		})
	}

	o._load_quota = function() {
		o.info_id.html(o.data.id)
		$.data(o.info_quota[0], "v", o.data.quota)
		cell_decorator_size_mb(o.info_quota)

		services_osvcgetrest("R_APP", [o.data.app_id], "", function(jd) {
			o.info_app_id.html(jd.data[0].app)
		})

		services_osvcgetrest("R_ARRAY_DISKGROUP", [0, o.data.dg_id], "", function(jd) {
			o.info_dg_name.html(jd.data[0].dg_name)

			$.data(o.info_dg_free[0], "v", jd.data[0].dg_free)
			$.data(o.info_dg_size[0], "v", jd.data[0].dg_size)
			$.data(o.info_dg_used[0], "v", jd.data[0].dg_used)
			$.data(o.info_dg_reserved[0], "v", jd.data[0].dg_reserved)
			cell_decorator_size_mb(o.info_dg_free)
			cell_decorator_size_mb(o.info_dg_size)
			cell_decorator_size_mb(o.info_dg_used)
			cell_decorator_size_mb(o.info_dg_reserved)

			var am_data = [
				{
					"title": "action_menu.data_actions",
					"children": [
						{
							"selector": ["tab"],
							"foldable": false,
							"cols": [],
							"children": [
								{
									"title": "action_menu.del",
									"class": "del16",
									"fn": "data_action_del_quotas",
									"privileges": ["Manager", "StorageManager"]
								}
							]
						}
					]
				}
			]
			tab_tools({
				"div": o.div.find("#tools"),
				"data": {"id": o.data.id},
				"am_data": am_data
			})

			services_osvcgetrest("R_ARRAY", [jd.data[0].array_id], "", function(jd) {
				o.info_array_name.html(jd.data[0].array_name)
				o.info_array_model.html(jd.data[0].array_model)
				o.info_array_firmware.html(jd.data[0].array_firmware)
			})
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["StorageManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("R_ARRAY_DISKGROUP_QUOTA", [0, o.data.dg_id, o.options.quota_id], "", data, callback, error_callback)
			}
		})
	}

	o.div.load("/init/static/views/quota_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

function quota_stats(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	var div = $("<div style='margin:1em'></div>")
	var title_dg = $("<h2 data-i18n='quota_stats.title_dg'></h2>")
	var chart_dg = $("<div></div>")
	var title_all = $("<h2 data-i18n='quota_stats.title_all'></h2>")
	var chart_all = $("<div></div>")
	div.append([title_dg, chart_dg, title_all, chart_all])
	o.div.append(div)
	div.i18n()
	chart_dg.uniqueId()
	chart_all.uniqueId()
	stats_disk_app("/"+osvc.app+"/disks/call/json/json_disk_app_dg/"+options.app_id+"/"+options.dg_id, chart_dg.attr("id"))
	stats_disk_app("/"+osvc.app+"/disks/call/json/json_disk_app/"+options.app_id, chart_all.attr("id"))
}

