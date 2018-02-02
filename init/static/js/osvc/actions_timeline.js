function table_actions_timeline(t) {
	var divid = t.divid + "_timeline"
	if (!t.actions_timeline) {
		var div = $("<div>")
		div.attr("id", divid)
		div.insertBefore(t.div)
	}
	var data = []
	var cols = t.get_ordered_visible_columns()
	var col = {}
	for (var i=0; i<cols.length; i++) {
		col[cols[i]] = i
	}
	for (var i=0; i<t.lines.length; i++) {
		var line = t.lines[i]
		if (line[col["end"]] === null) {
			continue
		}
		data.push({
			"svcactions": {
				"id": line[col["id"]],
				"action": line[col["action"]],
				"begin": line[col["begin"]],
				"end": line[col["end"]],
				"node_id": line[col["node_id"]],
				"svc_id": line[col["svc_id"]],
				"status": line[col["status"]],
				"status_log": line[col["status_log"]]
			},
			"services": {
				"svcname": line[col["svcname"]]
			},
			"nodes": {
				"nodename": line[col["nodename"]]
			}
		})
	}
	if (!t.actions_timeline) {
		t.e_sticky.empty()
		t.actions_timeline = actions_timeline(divid, {data: data})
	} else {
		t.actions_timeline.update_timeline({data: data})
	}
}

function actions_timeline(divid, options) {
	var o = {}
	o.options = options
	o.divid = divid
	o.div = $("#"+divid)
	o.expanded = []

	// Configuration for the Timeline
	o.colors = {
		"err": "red",
		"ok": "green",
		"warn": "orange"
	}

	var options = {
		//zoomKey: "metaKey",
		stack: false,
		stackSubgroups: false,
		zoomable: true,
		clickToUse: false,
		groupOrder: "id"
	}

	o.get_actions_data = function(options) {
		if (options.data) {
			o.parse_actions_data(options.data)
			return
		}
		var opts = {
			"meta": "false",
			"limit": 200,
			"props": "id,action,begin,end,node_id,svc_id,status,status_log,nodes.nodename,services.svcname",
			"orderby": "~id",
			"filters": ["end !empty"]
		}

		var svc_ids = []
		var node_ids = []
		for (var i=0; i<o.expanded.length; i++) {
			var l = o.expanded[i].split("@")
			svc_ids.push(l[0])
			node_ids.push(l[1])
		}
		if (options && options.services) {
			opts.filters.push("svc_id ("+options.services.join(",")+")")
		}
		if (options && options.nodes) {
			opts.filters.push("node_id ("+options.nodes.join(",")+")")
		}
		if (options && options.begin) {
			opts.filters.push("begin >"+options.begin)
		}
		if (options && options.end) {
			opts.filters.push("end <"+options.end)
		}
		services_osvcgetrest("/services_actions", "", opts, function(jd) {
			o.parse_actions_data(flatten_data(jd.data))
		})
	}

	o.parse_actions_data = function(data) {
		var _data = []
		var groupids = []
		var groups = []
		var nodes = {}
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			if (d.svcactions.end == "empty") {
				d.svcactions.end = d.svcactions.begin
			}
			var group_id = d.svcactions.svc_id+"@"+d.svcactions.node_id
			if (!(group_id in nodes)) {
				var group_content = d.services.svcname+"@"+d.nodes.nodename
				nodes[group_id] = {
					"id": group_id,
					"content": group_content,
					"nestedGroups": []
				}
				groups.push(nodes[group_id])
			}
			var action = d.svcactions.action.split(/\s+/)
			var base_action = action.pop()
			var group_id = d.svcactions.svc_id+"@"+d.svcactions.node_id+"@"+base_action
			var subgroup = action[0]
			if (nodes[d.svcactions.svc_id+"@"+d.svcactions.node_id].nestedGroups.indexOf(group_id) < 0) {
				var group_content = "<span>"+base_action+"</span>"
				groups.push({
					"id": group_id,
					"content": group_content
				})
				nodes[d.svcactions.svc_id+"@"+d.svcactions.node_id].nestedGroups.push(group_id)
			}
			if (d.svcactions.action.match(/#/)) {
				var itemtype = null
				var classname = "box-"+o.colors[d.svcactions.status]
			} else {
				var itemtype = "background"
				var classname = "box-light"+o.colors[d.svcactions.status]
			}
			_data.push({
				"start": moment.tz(d.svcactions.begin, osvc.server_timezone),
				"end": moment.tz(d.svcactions.end, osvc.server_timezone),
				"group": group_id,
				"subgroup": subgroup,
				"range_id": d.svcactions.id,
				"status": d.svcactions.status,
				"title": d.svcactions.action+"<br>"+d.svcactions.status_log,
				"content": "&nbsp;",
				"type": itemtype,
				"className": classname
			})
		}
		delete(data)
		o.data = [].concat(_data)
		delete(_data)
		o.groups = [].concat(groups)
		delete(groups)
		o.actions_loaded.resolve(true)
	}

	o.init_timeline = function() {
		require(["vis"], function(vis) {
			o.timeline = new vis.Timeline(o.div[0], o.data, o.groups, options)
		})
	}

	o.update_timeline = function(options) {
		o.get_actions_data(options)
		o.timeline.setGroups(o.groups)
		o.timeline.setItems(o.data)
		o.timeline.moveTo(new Date())
		o.timeline.redraw()
	}

	o.init = function() {
		o.div.empty()
		o.groups = []
		o.data = []
		o.actions_loaded = $.Deferred()

		spinner_add(o.div)
		o.get_actions_data(o.options)

		$.when(
			o.actions_loaded
		).then(function(){
			spinner_del(o.div)
			o.init_timeline()
		})
	}

	o.init()

	return o
}

