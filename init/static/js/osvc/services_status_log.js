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
			"props": "id,mon_svcname,mon_nodname,mon_begin,mon_end,mon_availstatus",
			"orderby": "~id",
			"filters": []
		}
		if (options && options.services) {
			opts.filters.push("mon_svcname ("+options.services.join(",")+")")
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
			opts.filters.push("svc_name ("+options.services.join(",")+")")
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
			var group = d.mon_svcname+'@'+d.mon_nodname
			if (groupids.indexOf(group) < 0) {
				groupids.push(group)
				groups.push({
					"id": group
				})
			}
			_data.push({
				"start": d.mon_begin,
				"end": d.mon_end,
				"group": group,
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
			if (groupids.indexOf(d.svc_name) < 0) {
				groupids.push(d.svc_name)
				groups.push({
					"id": d.svc_name
				})
			}
			_data.push({
				"start": d.svc_begin,
				"end": d.svc_end,
				"group": d.svc_name,
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
		o.timeline = new vis.Timeline(o.div[0], o.data, o.groups, options)
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

