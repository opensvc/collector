function sysrep(divid, options) {
	var o = {}
	o.options = options
	o.link = {
		"fn": "sysrep",
		"title": "link.sysreport",
	}

	// store parameters
	o.divid = divid
	if (Array.isArray(options.node_id)) {
		o.nodes = options.node_id
	} else if (options.nodes) {
		o.nodes = options.nodes
	} else {
		o.nodes = [options.node_id]
	}
	o.begin = options.begin
	o.end = options.end
	o.path = options.path
	o.cid = options.cid

	o.direct_access_url = "S_SYSREPVIEW"
	o.div = $("#"+divid)

	o.sysrep_init = function(){
		return sysrep_init(this)
	}
	o.sysrep_timeline = function(){
		o.timeline_title.html(i18n.t("sysrep.timeline_title"))
		o.timeline_title.append(": ")
		for (var i=0; i<o.nodes.length; i++) {
			var ne = $("<span node_id='"+o.nodes[i]+"'></span>")
			o.timeline_title.append(ne)
			ne.osvc_nodename()
			if (i < (o.nodes.length-1)) {
				o.timeline_title.append(", ")
			}
		}

		var params = o.sysrep_getparams()
		if ("cid" in params) {
			delete params.cid
		}
		params["nodes"] = o.nodes
		spinner_add(o.timeline_graph)
		services_osvcgetrest("R_SYSREPORT_TIMELINE", "", params, function(jd) {
			spinner_del(o.timeline_graph)
			o.sysrep_timeline_data(jd)
		})
	}
	o.sysrep_timediff = function(){
		var params = o.sysrep_getparams()
		if (("cid" in params) || (!("begin" in params) && !("end" in params))) {
			o.time_diff.hide()
			return
		}
		nodes = o.nodes
		if (nodes.length == 0) {
			o.time_diff.hide()
			return
		}
		o.time_diff.empty()
		o.time_diff.show("vertical-slide")
		for (var i=0; i<nodes.length; i++) {
			o._sysrep_timediff(nodes[i])
		}
	}
	o._sysrep_timediff = function(node_id){
		var params = o.sysrep_getparams()
		_params = {
			"begin": params.begin ? params.begin : i18n.t("sysrep.begining"),
			"end": params.end ? params.end : i18n.t("sysrep.now"),
		}
		if ("nodes" in params) {
			delete params["nodes"]
		}
		var title = $("<div id='sysrep_time_diff_title' class='sectiontitle'></div>")
		title.html(i18n.t("sysrep.timeline_time_diff_title", _params))
		var detail = $("<div></div>")
		o.time_diff.append(title)
		o.time_diff.append(detail)
		spinner_add(detail)
		services_osvcgetrest("R_NODE_SYSREPORT_TIMEDIFF", [node_id], params, function(jd) {
			spinner_del(detail)
			o.sysrep_timediff_data(jd, node_id, detail)
		})
	}
	o.sysrep_timeline_data = function(jd){
		o.timeline_graph.empty()
		o.tree_diff.hide()
		o.tree.hide()

		var data = jd.data
		if (data.length == 0) {
			e = $("<span class='icon alert16'></span>")
			e.text(i18n.t("sysrep.error.no_change"))
			o.timeline_graph.append(e)
			return
		}

		// DOM element where the Timeline will be attached
		var container = o.timeline_graph[0]

		// Handle max lines
		var max_fpath = 5
		for (i=0; i<data.length; i++) {
			if (!("summary" in data[i])) {
				// git-filter allows to purge a file from the history.
				// In this case, some commits might end up empty. We don't
				// want to display those.
				data.splice(i, 1)
				i -= 1
				continue
			}
			data[i].start = moment.tz(data[i].start, osvc.server_timezone)
			if (data[i].stat.length > max_fpath) {
				var lastline = data[i].stat.length - max_fpath
				data[i].stat = data[i].stat.slice(0, max_fpath)
				data[i].stat.push("... " + lastline + " more.")
			}
			data[i].stat[0] += '\n'
			for(j=1; j<data[i].stat.length; j++) {
				data[i].stat[0] += data[i].stat[j] + "\n"
			}
			data[i].stat = data[i].stat.slice(0, 1)
		}


		// Configuration for the Timeline
		var options = {
			template: function (item) {
				return '<div class="pre" style="text-align:left">' + item.stat + '</div>'
			},
			//zoomKey: "metaKey",
			zoomable: false,
			clickToUse: false
		}

		// Create a Timeline
		var groups = []
		var groupids = []
		for (i=0; i<data.length; i++) {
			var group_id = data[i]['group']
			if (groupids.indexOf(group_id) >= 0) {
				continue
			}
			var group_content = "<span node_id="+group_id+">"+group_id+"</span>"
			groupids.push(group_id)
			groups.push({
				"id": group_id,
				"content": group_content
			})
		}
		if (groupids.length == 1) {
			groups = null
		}

		if (!o.timeline_graph.is(':visible')) {
			o.timeline_graph.slideToggle()
		}

		require(["vis"], function(vis) {
			o.timeline = new vis.Timeline(container, data, groups, options)
			o.timeline.on("change", function() {
				o.div.find("[node_id]").osvc_nodename({
					callback: function(){o.timeline.redraw()}
				})
			})

			o.timeline.on('select', function (properties) {
				var item_id = properties.items[0]
				var item = null
				for (i=0; i<data.length; i++) {
					if (data[i]['id'] == item_id) {
						item = data[i]
						break
					}
				}

				// double event prevention
				if (item && (o.cid == item.cid)) {
					return
				}

				// remember the click for link generation
				if (item) {
					o.cid = item.cid
				} else {
					delete o.cid
				}

				o.sysreport_timeline_on_select(item)
			})

			// if a cid is selected, simulate a click on the cid box to
			// display diff and file tree for the commit
			if (o.cid) {
				for (i=0; i<data.length; i++) {
					if (data[i]['cid'] == o.cid) {
						o.timeline.setSelection(data[i]['id'])
						o.sysreport_timeline_on_select(data[i])
						break
					}
				}
			}
		})
		o.sysrep_timediff()
	}
	o.sysrep_timediff_data = function(jd, node_id, detail){
		if (jd.error) {
			detail.append(services_error_fmt(jd))
			return
		}
		var result = jd.data

		for (var d in result.blocks) {
			var diff =""
			if (result.blocks[d].secure) {
				var highlight_cl = "highlight"
			} else {
				var highlight_cl = ""
			}

			// item title
			var e = $("<h4></h4>")
			e.addClass("clickable")
			e.addClass(highlight_cl)
			e.bind("click", function() {
				var je = $(this).next()
				je.slideToggle()
				require(["hljs"], function(hljs) {
					hljs.highlightBlock(je[0])
				})
			})
			e.text(d)

			// item folded content
			var p = $("<pre></pre>")
			p.addClass("diff hljs")
			p.css({"display": "none"})
			p.text(result.blocks[d].diff)

			detail.append(e)
			detail.append(p)
		}
		if (detail.children().length == 0) {
			e = $("<span class='icon alert16'></span>")
			e.text(i18n.t("sysrep.error.no_change"))
			detail.append(e)
		}
	}
	o.sysrep_getparams = function(){
		return sysrep_getparams(this)
	}
	o.sysrep_on_change_filters = function(){
		o.sysrep_timeline()
	}
	o.sysrep_admin_secure = function(){
		return sysrep_admin_secure(this)
	}
	o.sysrep_admin_allow = function(){
		return sysrep_admin_allow(this)
	}
	o.sysrep_admin_secure_handle = function(tid, func){
		return sysrep_admin_secure_handle(this, tid, func)
	}
	o.sysrep_admin_allow_handle = function(tid, func){
		return sysrep_admin_allow_handle(this, tid, func)
	}
	o.sysrep_tree_file_detail = function(detail, node_id, cid){
		if (detail.is(':visible')) {
			detail.slideToggle()
		} else { 
			oid = detail.attr("oid")
			spinner_add(detail)
			services_osvcgetrest("R_NODE_SYSREPORT_CID_TREE_OID", [node_id, cid, oid], "", function(jd) {
				spinner_del(detail)
				var result = jd.data
				detail.text(result.content)
				//hljs.highlightBlock(detail[0])
				detail.show("vertical-slide")
			})
		}
	}

	o.sysrep_define_maxchanges = function(res) {
		var max = 0
		for (var d in res.stat) {
			var z = res.stat[d]
			var tot = z[0] + z[1]
			if (tot > max) {
				max = tot
			}
		}
		return max
	}

	o.sysreport_timeline_on_select = function(item){
		o.tree_diff_detail.empty()
		o.tree_file.empty()
		o.time_diff.hide()
		o.tree_diff.hide()
		o.tree.hide()

		if (!item) {
			o.sysrep_timediff()
			return
		}

		params = {}
		var filter_value = o.filter_path.val()
		if (filter_value != "" && filter_value != undefined) {
			params["path"] = filter_value
		}
		// list commit diffs
		spinner_add(o.tree_diff)
		services_osvcgetrest("R_NODE_SYSREPORT_CID", [item.group, item.cid], params, function(jd) {
			spinner_del(o.tree_diff)
			var result = jd.data
			o.tree_diff_date.html(result.date)
			o.tree_date.html(result.date)
			var maximum = o.sysrep_define_maxchanges(result)
			var stat_width = 30
			for (var d in result.stat) {
				// diff stats in title
				var diff =""
				var total = result.stat[d][0] + result.stat[d][1]
				var quota = Math.round((stat_width*total)/maximum)
				if (quota == 0) {
					quota = 1
				} else if (quota > total) {
					quota = total
				}
				_inse = Math.round((result.stat[d][0]*quota)/total)
				_dele = quota-_inse
				var stat = total + " "
				for (j=0;j<_inse;j++) stat += "+"
				for (j=0;j<_dele;j++) stat += "-"

				// diff title
				var e = $("<h4></h4>")
				e.addClass("clickable")
				if (result.blocks[d].secure) {
					e.addClass("highlight")
				}
				e.bind("click", function(){
					var je = $(this).next()
					je.slideToggle()
					require(["hljs"], function(hljs) {
						hljs.highlightBlock(je[0])
					})
				})
				e.html(d+"<pre>"+stat+"</pre>")

				// diff text
				var p = $("<pre></pre>")
				p.addClass("diff hljs")
				p.css({"display": "none"})
				p.text(result.blocks[d].diff)

				o.tree_diff_detail.append(e)
				o.tree_diff_detail.append(p)
			}
			if (!o.tree_diff.is(':visible')) {
				o.tree_diff.slideToggle()
			}
		})

		// List Tree File/Cmd
		o.tree_title.html(i18n.t("sysrep.timeline_tree_file_title"))
		spinner_add(o.tree)
		services_osvcgetrest("R_NODE_SYSREPORT_CID_TREE", [item.group, item.cid], params, function(jd) {
			spinner_del(o.tree)
			var result = jd.data
			for (var i=0; i<result.length; i++) {
				if (result[i].content_type == "command") {
					cl = "icon action16"
				} else {
					cl = "icon log16"
				}
				var e = $("<h4>" + result[i].fpath + "</h4>")
				e.addClass("clickable")
				if (result[i].secure) {
					e.addClass("highlight")
				}
				e.addClass(cl)
				e.bind("click", function () {
					o.sysrep_tree_file_detail($(this).next(), item.group, item.cid)
				})
				o.tree_file.append(e)

				var e = $("<pre></pre>")
				e.addClass('diff hljs')
				e.attr("oid", result[i].oid)
				e.css({"display": "none"})

				o.tree_file.append(e)
			}
			if (!o.tree.is(':visible')) {
				o.tree.slideToggle()
			}
		})
	}
	o.div.load('/init/static/views/sysreport.html?v='+osvc.code_rev, function() {
		o.sysrep_init()
		o.sysrep_timeline()
	})
	return o
}

function sysrep_init(o)
{
	// initialize useful object refs to avoid DOM lookups
	o.ql_link = o.div.find("#sysrep_ql_link")
	o.ql_filter = o.div.find("#sysrep_ql_filter")
	o.ql_admin = o.div.find("#sysrep_ql_admin")

	o.filter = o.div.find("#sysrep_filter")
	o.filter_begin = o.filter.find("#sysrep_filter_begindate")
	o.filter_end = o.filter.find("#sysrep_filter_enddate")
	o.filter_path = o.filter.find("#sysrep_filter_value")
	o.filter_ignore_blanks = o.filter.find("#sysrep_filter_ignore_blanks")
	o.form_filter = o.filter.find("#sysrep_form_filter")

	o.administration = o.div.find("#sysrep_administration")
	o.form_allow = o.administration.find("#sysrep_form_allow")
	o.form_secure = o.administration.find("#sysrep_form_secure")
	o.secure_list_item = o.administration.find("#sysrep_secure_list_item")
	o.authorizations_list_item = o.administration.find("#sysrep_authorizations_list_item")
	o.secure_pattern_button = o.administration.find("#sysrep_secure_pattern_button")
	o.secure_pattern_new = o.administration.find("#sysrep_secure_pattern_new")
	o.secure_pattern_error = o.administration.find("#sysrep_secure_pattern_error")
	o.admin_allow_error = o.administration.find("#sysrep_admin_allow_error")
	o.allow_button = o.administration.find("#sysrep_allow_button")
	o.allow_filterset = o.administration.find('#sysreport_allow_filterset')
	o.allow_groups = o.administration.find('#sysreport_allow_groups')
	o.allow_pattern = o.administration.find("#sysreport_allow_pattern")

	o.timeline_title = o.div.find("#sysrep_timeline_title")
	o.timeline_graph = o.div.find("#sysrep_timeline_graph")
	o.tree_diff_detail = o.div.find("#sysrep_tree_diff_detail")
	o.tree_diff_title = o.div.find("#sysrep_tree_diff_title")
	o.tree_diff_date = o.div.find("#sysrep_tree_diff_date")
	o.tree_diff = o.div.find("#sysrep_tree_diff")
	o.tree_date = o.div.find("#sysrep_tree_date")
	o.tree_file = o.div.find("#sysrep_tree_file")
	o.tree_title = o.div.find("#sysrep_tree_title")
	o.tree = o.div.find("#sysrep_tree")
	o.time_diff = o.div.find("#sysrep_time_diff")
	o.diff = o.div.find("#sysrep_diff")

	o.div.i18n()
	o.filter_begin.datetimepicker({dateFormat:'yy-mm-dd'})
	o.filter_end.datetimepicker({dateFormat:'yy-mm-dd'})

	osvc_tools(o.div, {
		"link": {
			"fn": o.link.fn,
			"parameters": o.options,
			"title": o.link.title
		}
	})

	o.ql_filter.on("click", function() {
		o.filter.slideToggle()
	})

	o.form_filter.on("submit", function (event) {
		event.preventDefault()
		o.sysrep_on_change_filters()
	})

	// apply initial filters as default values
	if (o.begin) {
		o.filter_begin.val(o.begin)
	}
	if (o.end) {
		o.filter_end.val(o.end)
	}
	if (o.path) {
		o.filter_path.val(o.path)
	}
	if (o.ignore_blanks) {
		o.filter_ignore_blanks.attr("checked", true)
	}
	if ((o.begin) || (o.end) || (o.path) || (o.ignore_blanks)) {
		o.filter.slideToggle()
	}

	if (services_ismemberof("Manager")) {
		// Authorization process
		o.ql_admin.on("click", function() {
			o.administration.slideToggle()
		})
		o.ql_admin.show()

		o.secure_pattern_button.on("click", function () {
			mul_toggle('sysrep_secure_pattern_button','sysrep_secure_pattern_add', o.divid)
		})

		o.allow_button.on("click", function () {
			mul_toggle('sysrep_allow_button','sysrep_allow_input', o.divid)
		})

		o.form_allow.on("submit", function (event) {
			event.preventDefault()
			o.sysrep_admin_allow_handle('','add')
		})

		o.form_secure.on("submit", function (event) {
			event.preventDefault()
			o.sysrep_admin_secure_handle('','add')
		})

		// Feed FilterSet
		var fsets = []
		services_osvcgetrest("R_FILTERSETS", "", {"meta": "false", "limit": "0"}, function(jd) {
			var data = jd.data
			for (var i=0;i<data.length;i++) {
				fsets.push(data[i].fset_name)
			}
		})
		o.allow_filterset.autocomplete({
			source: fsets,
			minLength: 0
		})

		// Feed Groups
		var groups = []
		services_osvcgetrest("R_GROUPS", [], {"meta": "false", "limit": "0", "query": "not role starts with user_ and privilege=F"}, function(jd) {
			var data = jd.data
			for (var i=0;i<data.length;i++) {
				groups.push(data[i].role)
			}
		})
		o.allow_groups.autocomplete({
			source: groups,
			minLength: 0
		})

		// Show section
		o.sysrep_admin_allow()
		o.sysrep_admin_secure()
	}
}

function sysrep_getparams(o) {
	var data = {}
	fval = o.filter_path.val()
	if (fval && (fval != "")) {
		data["path"] = fval
	}
	fval = o.filter_begin.val()
	if (fval && (fval != "")) {
		m = moment(fval).tz(osvc.server_timezone)
		data["begin"] = m.format(m._f)
	}
	fval = o.filter_end.val()
	if (fval && (fval != "")) {
		m = moment(fval).tz(osvc.server_timezone)
		data["end"] = m.format(m._f)
	}
	if (o.filter_ignore_blanks.is(":checked")) {
		data["ignore_blanks"] = true
	}
	if (o.cid) {
		data["cid"] = o.cid
	}
	data["nodes"] = o.nodes
	return data
}

function sysrep_admin_secure(o) {
	services_osvcgetrest("R_SYSREPORT_SECURE_PATTERNS", "", "", function(jd) {
		o.secure_list_item.empty()
		var data = jd.data
		for (i=0; i<data.length; i++) {
			var e = $("<tr><td class='button_div'><span class='icon del16_allow'>" + data[i].pattern + "</span></td></tr>")
			var tid = data[i].id
			e.attr("id", tid)
			e.bind("click", function() {
				o.sysrep_admin_secure_handle($(this).attr("id"), 'del')
			})
			o.secure_list_item.append(e)
		}
	})  
}

function sysrep_admin_allow(o) {
	services_osvcgetrest("R_SYSREPORT_AUTHORIZATIONS", "", "", function(jd) {
		o.authorizations_list_item.empty()
		var data = jd.data
		for (var i=0; i<data.length; i++) {
			var filter = {
				"pattern" : data[i].pattern,
				"group" : data[i].group_name,
				"filterset" : data[i].fset_name
			}
			var e = $("<tr><td class='button_div'><span class='icon del16_allow'>" + i18n.t("sysrep.allow_read_sentence", filter) + "</span></td></tr>")
			var tid = data[i].id
			e.attr("id", tid)
			e.bind("click", function() {
				o.sysrep_admin_allow_handle($(this).attr("id"), 'del')
			})
			o.authorizations_list_item.append(e)
		}
	})
}

function sysrep_admin_secure_handle(o, tid, func) {
	if (func=="add") {
		var value = o.secure_pattern_new.val()
		services_osvcpostrest("R_SYSREPORT_SECURE_PATTERNS", "", "", {"pattern": value}, function(jd) {
			if (jd.data === undefined) {
				o.secure_pattern_error.html(jd.info)
				return
			}
			o.secure_pattern_error.empty()
			o.sysrep_admin_secure()
			mul_toggle('sysrep_secure_pattern_add','sysrep_secure_pattern_button', o.divid)
		})
	} else if (func=="del") {
		services_osvcdeleterest("R_SYSREPORT_SECURE_PATTERN", [tid], "", "", function(jd) {
			var result = jd
			o.sysrep_admin_secure()
		})  
	}
}

function sysrep_admin_allow_handle(o, tid, func) {
	if (func=="add") {
		var meta_pattern = o.allow_pattern.val()
		var meta_role = o.allow_groups.val()
		var meta_fset_name = o.allow_filterset.val()
		var data = {
			"pattern": meta_pattern,
			"group_name": meta_role,
			"fset_name": meta_fset_name,
		}
		services_osvcpostrest("R_SYSREPORT_AUTHORIZATIONS", "", "", data, function(jd) {
			if (jd.data === undefined) {
				if (jd.info !== undefined) {
					o.admin_allow_error.html(jd.info)
				} else {
					jd = JSON.parse(jd)
					o.admin_allow_error.html(jd.error)
				}
				return
			}
			o.admin_allow_error.empty()
			o.sysrep_admin_allow()
			mul_toggle('sysrep_allow_input','sysrep_allow_button', o.divid)
		})
	} else if (func=="del") {
		services_osvcdeleterest("R_SYSREPORT_AUTHORIZATION", [tid], "", "", function(jd) {
			var result = jd
			o.sysrep_admin_allow()
		})
	}
}

//
// Sysreport diff
//
function sysrepdiff(divid, options)
{
	var o = {}
	o.options = options
	o.link = {
		"fn": "sysrepdiff",
		"title": "link.sysrepdiff",
	}

	// store parameters
	o.divid = divid
	o.nodes = options.nodes
	o.path = options.path
	o.ignore_blanks = options.ignore_blanks

	o.direct_access_url = "S_SYSREPDIFFVIEW"
	o.div = $("#"+divid)

	o.sysrep_init = function(){
		return sysrep_init(this)
	}

	o.sysrep_diff = function(){
		o.done = []

		// clone the node list for shift() not to corrupt our reference
		var nodes = o.nodes.slice(0)

		o.diff.empty()
		if (nodes.length < 2) {
			e = $("<div></div")
			e.addClass("icon alert16")
			e.text(i18n.t("sysrep.sysrepdiff.error.not_enough_nodes"))
			o.diff.append(e)
			return
		}
		for (var i=0; i<nodes.length; i++) {
			ref_node = nodes.shift()
			for (var j=0; j<nodes.length; j++) {
				o._sysrep_diff(ref_node, nodes[j])
			}
		}
	}
	o._sysrep_diff = function(node1, node2){
		if (node1 == node2) {
			return
		}
		var key = [node1, node2]
		key = key.sort().join(",")
		if (o.done.indexOf(key) >= 0) {
			return
		}
		o.done.push(key)

		var params = o.sysrep_getparams()
		_params = {
			"node1": node1,
			"node2": node2,
		}
		var title = $("<div class='sectiontitle'></div>")
		title.html(i18n.t("sysrep.sysrepdiff.section_title"))
		ne1 = $("<span node_id='"+node1+"'>"+node1+"</span>")
		ne2 = $("<span node_id='"+node2+"'>"+node2+"</span>")
		title.append(["<br>", ne1, "<span class='fa fa-arrow-right' style='padding:0 1em'></span>", ne2])
		ne1.osvc_nodename()
		ne2.osvc_nodename()
		var detail = $("<div></div>")
		o.diff.append(title)
		o.diff.append(detail)
		params = o.sysrep_getparams()
		params["nodes"] = [node1, node2]
		spinner_add(detail)
		services_osvcgetrest("R_SYSREPORT_NODEDIFF", "", params, function(jd) {
			spinner_del(detail)
			o.sysrep_diff_data(jd, node1, node2, detail)
		})
	}
	o.sysrep_diff_data = function(jd, node1, node2, detail){
		if (jd.error) {
			detail.append(services_error_fmt(jd))
			return
		}
		var result = jd.data
		if (result.length == 0) {
			e = $("<span class='icon alert16'></span>")
			e.text(i18n.t("sysrep.sysrepdiff.error.no_diff"))
			detail.append(e)
		}

		for (var i=0; i<result.length; i++) {
			var d = result[i]
			var diff =""
			if (d.secure) {
				var highlight_cl = "highlight"
			} else {
				var highlight_cl = ""
			}

			// item title
			var e = $("<h4></h4>")
			e.addClass("clickable")
			e.addClass(highlight_cl)
			e.bind("click", function() {
				var je = $(this).next()
				je.slideToggle()
				require(["hljs"], function(hljs) {
					hljs.highlightBlock(je[0])
				})
			})
			e.text(d.path)

			// item folded content
			var p = $("<pre></pre>")
			p.addClass("diff hljs")
			p.css({"display": "none"})
			p.text(d.diff)

			detail.append(e)
			detail.append(p)
		}
		if (!o.diff.is(':visible')) {
			o.diff.slideToggle()
		}
	}
	o.sysrep_getparams = function(){
		return sysrep_getparams(this)
	}
	o.sysrep_on_change_filters = function(){
		return o.sysrep_diff()
	}
	o.sysrep_admin_secure = function(){
		return sysrep_admin_secure(this)
	}
	o.sysrep_admin_allow = function(){
		return sysrep_admin_allow(this)
	}
	o.sysrep_admin_secure_handle = function(tid, func){
		return sysrep_admin_secure_handle(this, tid, func)
	}
	o.sysrep_admin_allow_handle = function(tid, func){
		return sysrep_admin_allow_handle(this, tid, func)
	}
	o.div.load('/init/static/views/sysreport_diff.html?v='+osvc.code_rev, function() {
		o.sysrep_init()
		o.sysrep_diff()
	})
	return o
}

