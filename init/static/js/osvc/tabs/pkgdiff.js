function pkgdiff(divid, options) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	spinner_add(o.div, i18n.t("api.loading"))
	services_osvcgetrest("R_PACKAGES_DIFF", "", o.options, function(jd) {
		spinner_add(o.div, i18n.t("api.formatting"))
		if (jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		o.draw(jd)
	},
	function(xhr, stat, error) {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})

	o.draw = function(data) {
		if (data.data.length == 0) {
			o.div.html(i18n.t("diff.no_diff"))
			return
		}

		var t = $("<table class='table'></table>")

		// table header
		var header1 = $("<tr></tr>")
		header1.append($("<th></th>"))
		header1.append($("<th></th>"))
		header1.append($("<th></th>"))
		header1.append($("<th style='text-align:center' colspan="+data.meta.node_ids.length+" data-i18n='diff.nodes'></th>"))
		t.append(header1)

		var header2 = $("<tr></tr>")
		header2.append($("<th data-i18n='diff.package'></th>"))
		header2.append($("<th data-i18n='diff.arch'></th>"))
		header2.append($("<th data-i18n='diff.type'></th>"))
		for (var i=0; i<data.meta.node_ids.length; i++) {
			var th = $("<th node_id='"+data.meta.node_ids[i]+"'></th>")
			header2.append(th)
			th.osvc_nodename()
		}
		t.append(header2)

		var packages = {}
		var keys = []
		for (var i=0; i<data.data.length; i++) {
			var p = data.data[i]
			var key = p.pkg_name + "." + p.pkg_arch
			if (!(key in packages)) {
				packages[key] = {
					"pkg_name": p.pkg_name,
					"pkg_arch": p.pkg_arch,
					"pkg_type": p.pkg_type,
					"pkg_version": {}
				}
				keys.push(key)
			}
			packages[key].pkg_version[p.node_id] = p.pkg_version
		}

		for (var i=0; i<keys.length; i++) {
			var key = keys[i]
			var p = packages[key]
			var l = $("<tr class='diff_line'></tr>")
			l.append($("<td>"+p.pkg_name+"</td>"))
			l.append($("<td>"+p.pkg_arch+"</td>"))
			l.append($("<td>"+p.pkg_type+"</td>"))
			for (var j=0; j<data.meta.node_ids.length; j++) {
				var node_id = data.meta.node_ids[j]
				if (node_id in p.pkg_version) {
					l.append($("<td>"+p.pkg_version[node_id]+"</td>"))
				} else {
					l.append($("<td></td>"))
				}
			}
			t.append(l)
		}
		o.div.html(t)
		o.div.i18n()
		osvc_tools(o.div, {
			"link": o.link
		})
	}
	return o
}

function svc_pkgdiff(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	var t
	var d

	o.div.empty()
	o.div.addClass("p-3")
	osvc_tools(o.div, {
		"link": o.link
	})

	// pkgdiff at hv level
	t = $("<h3 data-i18n='diff.pkg_title_cluster'></h3>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	pkgdiff(d.attr("id"), {"svc_ids": o.options.svc_ids})

	// pkgdiff at encap level
	t = $("<h3 data-i18n='diff.pkg_title_encap'></h3>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	pkgdiff(d.attr("id"), {"svc_ids": o.options.svc_ids, "encap": "true"})

	o.div.i18n()
	return o
}


function servicediff(divid, options) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.options.compared = "svc_id"
	o.options.compared_title = "diff.services"
	o.options.blacklist = ["svc_config", "id"]

	o.options.get = function(callback, callback_error) {
		var data = {
			"meta": "0",
			"limit": "0",
			"filters": "svc_id ("+o.options.svc_ids.join(",")+")"
		}
		services_osvcgetrest("R_SERVICES", "", data, callback, callback_error)
	}
	generic_diff(divid, options)
}

function assetdiff(divid, options) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.options.compared = "nodename"
	o.options.compared_title = "diff.nodes"
	o.options.blacklist = ["id"]

	o.options.get = function(callback, callback_error) {
		var data = {
			"meta": "0",
			"limit": "0",
			"filters": "node_id ("+o.options.node_ids.join(",")+")"
		}
		services_osvcgetrest("R_NODES", "", data, callback, callback_error)
	}
	generic_diff(divid, options)
}

function generic_diff(divid, options) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	spinner_add(o.div, i18n.t("api.loading"))
	o.options.get(
		function(jd) {
			spinner_add(o.div, i18n.t("api.formatting"))
			if (jd.error) {
				o.div.html(services_error_fmt(jd))
				return
			}
			o.draw(jd.data)
		},
		function(xhr, stat, error) {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		}
	)

	o.draw = function(data) {
		if (data.length < 2) {
			o.div.html(i18n.t("diff.no_diff"))
			return
		}

		var t = $("<table class='table'></table>")

		// table header
		var header1 = $("<tr></tr>")
		header1.append($("<th></th>"))
		header1.append($("<th style='text-align:center' colspan="+data.length+" data-i18n='"+o.options.compared_title+"'></th>"))
		t.append(header1)

		var header2 = $("<tr></tr>")
		header2.append($("<th data-i18n='diff.property'></th>"))
		for (var i=0; i<data.length; i++) {
			var th = $("<th>"+data[i][o.options.compared]+"</th>")
			th.attr(o.options.compared, data[i][o.options.compared])
			header2.append(th)
			if (o.options.compared == "svc_id") {
				th.osvc_svcname()
			} else if (o.options.compared == "node_id") {
				th.osvc_nodename()
			}
		}
		t.append(header2)

		var keys = []
		for (prop in data[0]) {
			keys.push(prop)
		}
		keys = keys.sort()
		for (var j=0; j<keys.length; j++) {
			prop = keys[j]
			if (o.options.blacklist && (o.options.blacklist.indexOf(prop) >= 0)) {
				// discard blacklisted field
				continue
			}
			var ref = data[0][prop]
			if (ref == null) {
				ref = ""
			}
			for (var i=1; i<data.length; i++) {
				var val = data[i][prop]
				if (val == null) {
					val = ""
				}
				if (val != ref) {
					add_prop(prop)
					break
				}
			}
		}

		function add_prop(prop) {
			var l = $("<tr class='diff_line'></tr>")
			if (prop in colprops) {
				_prop = colprops[prop].title
				_class = "icon_fixed_width "+colprops[prop].img
			} else {
				_prop = prop
				_class = "icon_fixed_width"
			}
			l.append($("<td class='"+_class+"'>"+_prop+"</td>"))
			for (var i=0; i<data.length; i++) {
				var val = data[i][prop]
				if (typeof(val) === "undefined" || val == null) {
					val = ""
				}
				l.append($("<td>"+val+"</td>"))
			}
			t.append(l)
		}
		o.div.html(t)
		o.div.i18n()
	}
	return o
}

function nodediff(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	var t
	var d

	o.div.empty()
	osvc_tools(o.div, {
		"link": o.link
	})

	// asset diff
	t = $("<h2 data-i18n='diff.asset_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	assetdiff(d.attr("id"), {"node_ids": o.options.node_ids})

	// pkg diff
	t = $("<h2 data-i18n='diff.pkg_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	pkgdiff(d.attr("id"), {"node_ids": o.options.node_ids.join(",")})

	// comp diff
	t = $("<h2 data-i18n='diff.comp_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	sync_ajax('/init/compliance/ajax_compliance_nodediff?node='+o.options.node_ids.join(","), [], d.attr("id"), function(){})

	o.div.i18n()
	return o
}

function svcdiff(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	var t
	var d

	o.div.empty()
	osvc_tools(o.div, {
		"link": o.link
	})

	// asset diff
	t = $("<h2 data-i18n='diff.services_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	servicediff(d.attr("id"), {"svc_ids": o.options.svc_ids})

	// pkg diff
	t = $("<h2 data-i18n='diff.pkg_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	svc_pkgdiff(d.attr("id"), {"svc_ids": o.options.svc_ids.join(",")})

	// comp diff
	t = $("<h2 data-i18n='diff.comp_title'></h2>")
	d = $("<div></div>")
	d.uniqueId()
	o.div.append(t)
	o.div.append(d)
	sync_ajax('/init/compliance/ajax_compliance_svcdiff?node='+o.options.svc_ids.join(","), [], d.attr("id"), function(){})

	o.div.i18n()
	return o
}

