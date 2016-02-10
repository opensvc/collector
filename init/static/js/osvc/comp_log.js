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
		if (options && options.svcname) {
			opts.filters.push("run_svcname "+options.svcname)
		}
		if (options && options.nodename) {
			opts.filters.push("run_nodename "+options.nodename)
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
				"start": d.run_date,
				"group": group,
				"title": d.run_log,
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
	}

	o.add_title = function() {
		var t = $("<h3></h3>")
		var text = o.options.module
		if (o.options.svcname) {
			text += "@"+o.options.svcname
		}
		text += "@"+o.options.nodename
		t.text(text)
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

