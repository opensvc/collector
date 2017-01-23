//
// array
//
function array_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.disk
	o.options.icon = "array"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		services_osvcgetrest("R_ARRAY", [o.options.array_name], {"meta": "0"}, function(jd) {
			o.data = jd.data[0]
			o._load()
		})
	})

	o._load = function() {
		var title = o.data.array_name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon array"
		})
		o.tabs[i].callback = function(divid) {
			array_properties(divid, {"array_id": o.data.id})
		}

		// tab quotas
		i = o.register_tab({
			"title": "array_tabs.quotas",
			"title_class": "icon quota16"
		})
		o.tabs[i].callback = function(divid) {
			table_quota_array(divid, o.data.array_name)
		}

		// tab usage
		i = o.register_tab({
			"title": "node_tabs.stats",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			array_stats(divid, {"array_name": o.options.array_name})
		}

		o.set_tab(o.options.tab)
	}

	return o
}


function array_properties(divid, options) {
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
		o.info_array_level = o.div.find("#array_level")
		o.info_array_cache = o.div.find("#array_cache")
		o.info_array_updated = o.div.find("#array_updated")
		o.info_proxies = o.div.find("#proxies")
		o.info_proxies_title = o.div.find("#proxies_title")
		o.load_array()
	}

	o.load_array = function() {
		services_osvcgetrest("R_ARRAY", [o.options.array_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_array()
		})
	}

	o._load_array = function() {
		o.info_id.html(o.data.id)
		o.info_array_name.html(o.data.array_name)
		o.info_array_model.html(o.data.array_model)
		o.info_array_firmware.html(o.data.array_firmware)
		o.info_array_level.html(o.data.array_level)
		o.info_array_updated.html(osvc_date_from_collector(o.data.array_updated))
		$.data(o.info_array_cache[0], "v", o.data.array_cache)
		cell_decorator_size_mb(o.info_array_cache)

		tab_properties_generic_list({
			"request_service": "/arrays/%1/proxies",
			"request_parameters": [o.data.id],
			"request_data": {
				"props": "nodes.node_id,nodes.nodename"
			},
			"limit": "50",
			"key": "nodename",
			"item_class": "icon node16",
			"id": "node_id",
			"flash_id_prefix": "node",
			"title": "app_properties.nodes",
			"bgcolor": osvc.colors.node,
			"e_title": o.info_proxies_title,
			"e_list": o.info_proxies,
			"lowercase": true,
			"ondblclick": function(divid, data) {
				node_tabs(divid, {"node_id": data.id})
			}
		})

	}

	o.div.load("/init/static/views/array_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

function array_stats(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	var div = $("<div style='margin:1em'></div>")
	var title = $("<h2 data-i18n='array_stats.title'></h2>")
	var chart = $("<div></div>")
	div.append([title, chart])
	o.div.append(div)
	div.i18n()
	chart.uniqueId()
	stats_disk_array("/"+osvc.app+"/disks/call/json/json_disk_array?array_name="+options.array_name, chart.attr("id"))
}

