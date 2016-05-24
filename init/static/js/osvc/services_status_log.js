function services_status_log(divid, options) {
	var o = {}
	o.options = options
	o.divid = divid
	o.div = $("#"+divid)

	// Configuration for the Timeline
	o.colors = {
		"warn": "orange",
		"up": "green",
		"stdby up": "green",
		"down": "red",
		"stdby down": "red",
		"undef": "gray",
		"n/a": "gray"
	}
	o.services_status_log_loaded = $.Deferred()
	o.services_instances_status_log_loaded = $.Deferred()
	o.groups = []
	o.data = []


	var options = {
		//zoomKey: "metaKey",
		stack: false,
		zoomable: true,
		clickToUse: false,
		groupOrder: "id"
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
			"orderby": "~id",
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
			"orderby": "~id",
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

	o.parse_services_instances_status_log_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			var group_id = d.svc_id+"@"+d.node_id
			if (groupids.indexOf(group_id) < 0) {
				var group_content = "<span node_id="+d.node_id+">"+d.node_id+"</span>"
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
				var group_content = "<span svc_id="+d.svc_id+">"+d.svc_id+"</span>"
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
				o.div.find("[node_id]").osvc_nodename({
					callback: function(){o.timeline.redraw()}
				})
				o.div.find("[svc_id]").osvc_svcname({
					callback: function(){o.timeline.redraw()}
				})
				o.div.find("[title]").tooltipster()
			})
		})
	}

	o.init = function() {
		o.div.empty()
		spinner_add(o.div)
		o.get_services_status_log_data(o.options)
		o.get_services_instances_status_log_data(o.options)
		$.when(
			o.services_status_log_loaded,
			o.services_instances_status_log_loaded
		).then(function(){
			spinner_del(o.div)
			o.init_timeline()
		})
	}

	o.init()

	return o
}

