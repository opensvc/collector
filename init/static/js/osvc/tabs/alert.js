//
// alert
//
function alert_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.alert
	o.options.icon = osvc.icons.alert
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "alert",
			"name": o.options.alert_id,
			"id": o.options.id
		}
	}

	o.load(function(){
		services_osvcgetrest("/alerts/%1", [o.options.alert_id], "", function(jd) {
			o.options.alert_data = jd.data[0]
			o._load()
		})
	})

	o.wiki_page_name = function() {
		var s = "alert"
		if (o.options.alert_data.node_id) {
 		       s += "_" + o.options.alert_data.node_id
		} else if (o.options.alert_data.node_id) {
 		       s += "_" + o.options.alert_data.svc_id
		}
		if (o.options.alert_data.dash_md5) {
 		       s += "_" + o.options.alert_data.dash_md5
		}
		return s
	}

	o._load = function() {
		o.closetab.text(o.options.alert_id)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			alert_properties(divid, o.options)
		}

		// tab wiki
		i = o.register_tab({
			"title": "node_tabs.wiki",
			"title_class": "icon edit"
		})
		var name = o.wiki_page_name()
		o.tabs[i].callback = function(divid) {
			wiki(divid, {"nodes": name})
		}

		o.set_tab(o.options.tab)
	}

	return o
}


function alert_properties(divid, options) {
	var o = {}
	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "alert",
		}
	}

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_content = o.div.find("#content")
		o.info_timeline = o.div.find("#timeline")
		o.info_dash_dict = o.div.find("#dash_dict")
		o.info_dash_severity = o.div.find("#dash_severity")
		o.info_dash_type = o.div.find("#dash_type")
		o.info_dash_instance = o.div.find("#dash_instance")
		o.info_dash_md5 = o.div.find("#dash_md5")
		o.info_dash_env = o.div.find("#dash_env")
		o.info_dash_created = o.div.find("#dash_created")
		o.info_dash_updated = o.div.find("#dash_updated")
		o.info_node = o.div.find("#node")
		o.info_service = o.div.find("#service")
		o.info_tools = o.div.find("#tools")
		o.load()
	}

	o.load = function() {
		if (o.options.reload) {
			o.options.alert_data = null
		}
		if (o.options.alert_data) {
			o._load(o.options.alert_data)
		} else {
			var options = {
				"props": "dash_fmt,dash_dict,id,dash_type,dash_instance,dash_severity,dash_created,dash_updated,dash_md5,dash_env,node_id,svc_id"
			}
			services_osvcgetrest("/alerts/%1", [o.options.alert_id], options, function(jd) {
				if (!jd.data || (jd.data.length == 0)) {
					return
				}
				o._load(jd.data[0])
			})
		}
	}

	o._load = function(data) {
		//o.link.title_args.name = data.alert_name
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_content.html(data.alert)
		o.info_id.html(data.id)
		o.info_dash_type.html(data.dash_type)
		o.info_dash_instance.html(data.dash_instance)
		o.info_dash_md5.html(data.dash_md5)
		o.info_dash_env.html(data.dash_env)
		o.info_node.html(data.node_id)
		o.info_service.html(data.svc_id)
		o.info_dash_created.html(osvc_date_from_collector(data.dash_created))
		o.info_dash_updated.html(osvc_date_from_collector(data.dash_updated))
		o.info_dash_dict.html(JSON.stringify(data.dash_dict, null, 4))

		_cell_decorator_dash_entry(o.info_content, data.dash_fmt, data.dash_dict)
		_cell_decorator_dash_severity(o.info_dash_severity, data.dash_severity)
		o.info_node.osvc_nodename()
		o.info_service.osvc_svcname()

		alert_timeline(o.info_timeline, data)

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
								"fn": "data_action_del_alerts",
								"privileges": ["Manager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"alert_id": data.alert_id},
			"am_data": am_data
		})
	}

	o.div.load("/init/static/views/alert_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o

}

function alert_timeline(div, options) {
	var o = {}

	o.loaded = $.Deferred()
	o.data = []

	o.timeline_options = {
		//zoomKey: "metaKey",
		stack: false,
		zoomable: true,
		clickToUse: false
	}

	// store parameters
	o.div = div
	o.options = options

	o.load = function() {
		spinner_add(o.div)
		var _params = {
			"filters": ["dash_md5 "+o.options.dash_md5],
		}
		if (o.options.node_id && o.options.node_id != "") {
			_params.filters.push("node_id "+o.options.node_id)
		} else {
			_params.filters.push("node_id empty")
		}
		if (o.options.svc_id && o.options.svc_id != "") {
			_params.filters.push("svc_id "+o.options.svc_id)
		} else {
			_params.filters.push("svc_id empty")
		}
		services_osvcgetrest("R_ALERT_EVENT", "", _params, function(jd) {
			spinner_del(o.div)
			if (jd.data === undefined) {
				return
			}
			o.parse_data(jd.data)
		})
	}
	o.parse_data = function(data) {
		var _data = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			var _start = moment.tz(d.dash_begin, osvc.server_timezone)
			if (!d.dash_end) {
				var _end = moment()
			} else {
				var _end = moment.tz(d.dash_end, osvc.server_timezone)
			}
			var d = (_start - _end) / 60000
			_data.push({
				"start": _start,
				"end": _end,
				"title": delta_properties(d).text,
				"content": "&nbsp;",
				"className": "box-red"
			})
		}
		o.data = _data
		o.loaded.resolve(true)
	}

	o.init_timeline = function() {
		require(["vis"], function(vis) {
			o.timeline = new vis.Timeline(o.div[0], o.data, o.timeline_options)
			o.timeline.on("change", function() {
				o.div.find("[title]").tooltipster()
			})
		})
	}

	o.init = function() {
		o.div.empty()
		o.load(o.options)
		$.when(
			o.loaded
		).then(function(){
			o.init_timeline()
		})
	}

	o.init()

	return o
}

