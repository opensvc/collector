function comp_log(divid, options) {
	var o = {}
	o.options = options
	o.divid = divid
	o.div = $("#"+divid)

	// Configuration for the Timeline
	o.colors = {
		0: "green",
		1: "red",
		2: "gray"
	}
	o.comp_log_loaded = $.Deferred()
	o.groups = []
	o.data = []

	var options = {
		//zoomKey: "metaKey",
		//stack: false,
		zoomable: true,
		clickToUse: false,
		groupOrder: "id"
	}

	o.get_comp_log_data = function(options) {
		var opts = {
			"meta": "false",
			"limit": 200,
			"orderby": "~id",
			"filters": []
		}
		if (options && options.svc_id) {
			opts.filters.push("svc_id "+options.svc_id)
		} else {
			opts.filters.push("svc_id empty")
		}
		if (options && options.node_id) {
			opts.filters.push("node_id "+options.node_id)
		}
		if (options && options.module) {
			opts.filters.push("run_module "+options.module)
		}
		if (options && options.begin) {
			opts.filters.push("run_date >"+options.begin)
		}
		if (options && options.end) {
			opts.filters.push("run_date <"+options.end)
		}
		services_osvcgetrest("/compliance/logs", "", opts, function(jd) {
			o.parse_comp_log_data(jd.data)
		})
	}

	o.parse_comp_log_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			var group = d.run_action
			if (groupids.indexOf(group) < 0) {
				groupids.push(group)
				groups.push({
					"id": group
				})
			}
			_data.push({
				"start": moment.tz(d.run_date, osvc.server_timezone),
				"group": group,
				"title": d.run_log.replace(/\n/g, "<br>").replace(/ERR:/g, "<span class='highlight'>ERR:</span>"),
				"content": "",
				"className": "box-"+o.colors[d.run_status]
			})
		}
		delete(data)
		o.data = o.data.concat(_data)
		delete(_data)
		o.groups = o.groups.concat(groups)
		delete(groups)
		o.comp_log_loaded.resolve(true)
	}

	o.init_timeline = function() {
		o.timeline = new vis.Timeline(o.timeline_div[0], o.data, o.groups, options)
		o.timeline.on("change", function() {
			o.div.find("[title]").tooltipster({contentAsHTML: true})
		})
	}

	o.add_title = function() {
		var t = $("<h2 class='nowrap'></h2>")
		var mod = $("<span class='mod16 icon_fixed_width'>"+o.options.module+"</span>")
		t.append(mod)
		if (o.options.svc_id) {
			var svc = $("<span svc_id='"+o.options.svc_id+"' style='padding-left:1em'></span>")
			t.append(svc)
			svc.osvc_svcname()
		}
		var node = $("<span node_id='"+o.options.node_id+"' style='padding-left:1em'></span")
                node.append(node)
		t.append(node)
		node.osvc_nodename()
		o.div.append(t)
	}

	o.add_timeline_div = function() {
		var div = $("<div></div>")
		o.div.append(div)
		o.timeline_div = div
	}

	o.init = function() {
		o.div.empty()
		o.add_title()
		o.add_timeline_div()
		spinner_add(o.timeline_div)
		o.get_comp_log_data(o.options)
		$.when(
			o.comp_log_loaded
		).then(function(){
			spinner_del(o.timeline_div)
			o.init_timeline()
		})
	}

	o.init()

	return o
}

