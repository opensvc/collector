function services_status_log(divid, options) {
	var o = {}
	o.options = options
	o.divid = divid
	o.div = $("#"+divid)
	o.expanded = []

	// Configuration for the Timeline
	o.colors = {
		"warn": "orange",
		"up": "green",
		"stdby up": "lightgreen",
		"down": "red",
		"stdby down": "lightred",
		"undef": "gray",
		"n/a": "gray"
	}


	var options = {
		//zoomKey: "metaKey",
		stack: false,
		zoomable: true,
		clickToUse: false,
		groupOrder: "id"
	}

	o.get_resources_log_data = function(options) {
		if (o.expanded.length == 0) {
			o.resources_log_loaded.resolve(true)
			return
		}
		var opts = {
			"meta": "false",
			"limit": 200,
			"props": "id,rid,svc_id,node_id,res_begin,res_end,res_status",
			"orderby": "~res_begin",
			"filters": []
		}

		var svc_ids = []
		var node_ids = []
		for (var i=0; i<o.expanded.length; i++) {
			var l = o.expanded[i].split("@")
			svc_ids.push(l[0])
			node_ids.push(l[1])
		}
		opts.filters.push("svc_id ("+svc_ids.join(",")+")")
		opts.filters.push("node_id ("+node_ids.join(",")+")")
		if (options && options.begin) {
			opts.filters.push("mon_begin >"+options.begin)
		}
		if (options && options.end) {
			opts.filters.push("mon_end <"+options.end)
		}
		services_osvcgetrest("/resources_logs", "", opts, function(jd) {
			o.parse_resources_log_data(jd.data)
		})
	}

	o.get_services_instances_status_log_data = function(options) {
		if (!o.options.instances) {
			o.services_instances_status_log_loaded.resolve(true)
			return
		}
		var opts = {
			"meta": "false",
			"limit": 200,
			"props": "id,svc_id,node_id,mon_begin,mon_end,mon_availstatus",
			"orderby": "~mon_begin",
			"filters": []
		}
		if (options && options.services) {
			opts.filters.push("svc_id ("+options.services.join(",")+")")
		}
		if (options && options.begin) {
			opts.filters.push("mon_begin >"+options.begin)
		}
		if (options && options.end) {
			opts.filters.push("mon_end <"+options.end)
		}
		services_osvcgetrest("/services_instances_status_log", "", opts, function(jd) {
			o.parse_services_instances_status_log_data(jd.data)
		})
	}

	o.get_services_status_log_data = function(options) {
		var opts = {
			"meta": "false",
			"limit": 200,
			"orderby": "~svc_begin",
			"filters": []
		}
		if (options && options.services) {
			opts.filters.push("svc_id ("+options.services.join(",")+")")
		}
		if (options && options.begin) {
			opts.filters.push("svc_begin >"+options.begin)
		}
		if (options && options.end) {
			opts.filters.push("svc_end <"+options.end)
		}
		services_osvcgetrest("/services_status_log", "", opts, function(jd) {
			o.parse_services_status_log_data(jd.data)
		})
	}

	o.parse_resources_log_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			var group_id = d.svc_id+"@"+d.node_id+"@"+d.rid
			if (groupids.indexOf(group_id) < 0) {
				var group_content = "<span class=resource>"+d.rid+"</span>"
				groupids.push(group_id)
				groups.push({
					"id": group_id,
					"content": group_content
				})
			}
			_data.push({
				"start": moment.tz(d.res_begin, osvc.server_timezone),
				"end": moment.tz(d.res_end, osvc.server_timezone),
				"group": group_id,
				"range_id": d.id,
				"status": d.res_status,
				"title": d.res_status,
				"content": "&nbsp;",
				"className": "box-"+o.colors[d.res_status]
			})
		}
		delete(data)
		o.data = o.data.concat(_data)
		delete(_data)
		o.groups = o.groups.concat(groups)
		delete(groups)
		o.resources_log_loaded.resolve(true)
	}

	o.parse_services_instances_status_log_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			var group_id = d.svc_id+"@"+d.node_id
			if (groupids.indexOf(group_id) < 0) {
				var expanded_entry = d.svc_id + "@" + d.node_id
				var group_content = "<span nodename node_id="+d.node_id+">"+d.node_id+"</span>"
				if (o.expanded.indexOf(expanded_entry) >= 0) {
					var attr = "unexpander"
					var s = i18n.t("avail_tab.hide resources")
					var cl = "clickable grayed icon down16"
				} else {
					var attr = "expander"
					var s = i18n.t("avail_tab.show resources")
					var cl = "clickable grayed icon right16"
				}
				group_content += "<br><span "+attr+" class='"+cl+"' node_id="+d.node_id+" svc_id="+d.svc_id+">"+s+"<span>"
				groupids.push(group_id)
				groups.push({
					"id": group_id,
					"content": group_content
				})
			}
			_data.push({
				"start": moment.tz(d.mon_begin, osvc.server_timezone),
				"end": moment.tz(d.mon_end, osvc.server_timezone),
				"group": group_id,
				"range_id": d.id,
				"status": d.mon_availstatus,
				"title": d.mon_availstatus,
				"content": "&nbsp;",
				"className": "box-"+o.colors[d.mon_availstatus]
			})
		}
		delete(data)
		o.data = o.data.concat(_data)
		delete(_data)
		o.groups = o.groups.concat(groups)
		delete(groups)
		o.services_instances_status_log_loaded.resolve(true)
	}

	o.parse_services_status_log_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			if (groupids.indexOf(d.svc_id) < 0) {
				groupids.push(d.svc_id)
				var group_content = "<span svcname svc_id="+d.svc_id+">"+d.svc_id+"</span>"
				groups.push({
					"id": d.svc_id,
					"content": group_content
				})
			}
			_data.push({
				"start": moment.tz(d.svc_begin, osvc.server_timezone),
				"end": moment.tz(d.svc_end, osvc.server_timezone),
				"group": d.svc_id,
				"range_id": d.id,
				"status": d.svc_availstatus,
				"title": d.svc_availstatus,
				"content": "&nbsp;",
				"className": "box-"+o.colors[d.svc_availstatus]
			})
		}
		delete(data)
		o.data = o.data.concat(_data)
		delete(_data)
		o.groups = o.groups.concat(groups)
		delete(groups)
		o.services_status_log_loaded.resolve(true)
	}

	o.init_timeline = function() {
		require(["vis"], function(vis) {
			o.timeline = new vis.Timeline(o.div[0], o.data, o.groups, options)
			o.timeline.on("change", function() {
				o.div.find("[nodename]").osvc_nodename({
					callback: function(){o.timeline.redraw()}
				})
				o.div.find("[svcname]").osvc_svcname({
					callback: function(){o.timeline.redraw()}
				})
				o.div.find("[title]:not(.vis-label)").tooltipster()
				o.div.find("[expander]").bind("click", function(){
					o.expanded.push($(this).attr("svc_id")+"@"+$(this).attr("node_id"))
					o.init()
				})
				o.div.find("[unexpander]").bind("click", function(){
					var s = $(this).attr("svc_id")+"@"+$(this).attr("node_id")
					var idx = o.expanded.indexOf(s)
					if (idx >= 0) {
						o.expanded.splice(idx, 1)
					}
					o.init()
				})
			})
		})
	}

	o.init = function() {
		o.div.empty()
		o.groups = []
		o.data = []
		o.services_status_log_loaded = $.Deferred()
		o.services_instances_status_log_loaded = $.Deferred()
		o.resources_log_loaded = $.Deferred()

		spinner_add(o.div)
		o.get_services_status_log_data(o.options)
		o.get_services_instances_status_log_data(o.options)
		o.get_resources_log_data(o.options)

		$.when(
			o.services_status_log_loaded,
			o.services_instances_status_log_loaded,
			o.resources_log_loaded
		).then(function(){
			spinner_del(o.div)
			o.init_timeline()
		})
	}

	o.init()

	return o
}

