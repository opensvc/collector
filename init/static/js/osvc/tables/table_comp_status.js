function table_comp_module_status(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "cms",
		'name': "comp_module_status",
		'caller': "table_comp_module_status",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_mod_status',
		'span': ['mod_name'],
		'columns': ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'mod_log'],
		'default_columns': ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'mod_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_node_status(divid, options) {
	var defaults = {
		'id': "cns",
		'divid': divid,
		'caller': "table_comp_node_status",
		'name': "comp_node_status",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_node_status',
		'span': ['node_name'],
		'columns': ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'node_log'],
		'default_columns': ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'node_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_service_status(divid, options) {
	var defaults = {
		'divid': divid,
		'name': "comp_service_status",
		'caller': "table_comp_service_status",
		'id': "css",
		'checkboxes': false,
		'ajax_url': '/init/compliance/ajax_comp_svc_status',
		'span': ['svc_name'],
		'columns': ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'svc_log'],
		'default_columns': ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'svc_log'],
		'parent_tables': ['cs0']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_comp_status(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "cs0",
		'name': "comp_status",
		'caller': "table_comp_status",
		'ajax_url': '/init/compliance/ajax_comp_status',
		'span': ['run_nodename', 'run_svcname', 'run_module'],
		'force_cols': ['id', 'os_name'],
		'columns': ['id', 'run_date', 'run_nodename', 'run_svcname', 'run_module', 'run_status', 'run_status_log', 'rset_md5', 'run_log', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
		'default_columns': ["run_date", "run_module", "run_nodename", "run_status", "run_svcname"],
		'child_tables': ['cms', 'cns', 'css'],
		'wsable': true,
		'events': ['comp_status_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function comp_status_agg(divid, options) {
	var t = options.table
	var data = {
	  "table_id": t.id
	}
	for (c in t.colprops) {
		var current = $("#"+t.id+"_f_"+c).val()
		if ((current != "") && (typeof current !== 'undefined')) {
			data[t.id+"_f_"+c] = current
		} else if (t.colprops[c].force_filter != "") {
			data[t.id+"_f_"+c] = t.colprops[c].force_filter
		}
	}
	$.getJSON("/init/compliance/call/json/json_comp_status_agg", data, function(data) {
			var total = data.ok + data.nok + data.obs + data.na
			if (total == 0) {
				var p_ok = 0
				var p_nok = 0
				var p_obs = 0
				var p_na = 0
				var fp_ok = "0%"
				var fp_nok = "0%"
				var fp_obs = "0%"
				var fp_na = "0%"
			} else {
				var fp_ok = 100 * data.ok / total
				var fp_nok = 100 * data.nok / total
				var fp_obs = 100 * data.obs / total
				var fp_na = 100 * data.na / total
				var p_ok = fp_ok.toFixed(0) + "%"
				var p_nok = fp_nok.toFixed(0) + "%"
				var p_obs = fp_obs.toFixed(0) + "%"
				var p_na = fp_na.toFixed(0) + "%"
				var fp_ok = fp_ok.toFixed(1) + "%"
				var fp_nok = fp_nok.toFixed(1) + "%"
				var fp_obs = fp_obs.toFixed(1) + "%"
				var fp_na = fp_na.toFixed(1) + "%"
			}
			var d1 = $("<div style='margin:auto;text-align:center;width:100%'></div>")
			var d2 = $("<div style='text-align:left;margin:2px auto;background:#FF7863;overflow:hidden'></div>")
			var d3 = $("<div></div>")

			var div_obs = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#15367A'></div>")
			div_obs.css({"max-width": p_obs, "width": p_obs})
			var div_ok = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#3aaa50'></div>")
			div_ok.css({"max-width": p_ok, "width": p_ok})
			var div_na = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#acacac'></div>")
			div_na.css({"max-width": p_na, "width": p_na})

			var span_obs = $("<span style='color:#15367A;padding:3px'></span>")
			span_obs.text(data.obs + " (" + fp_obs + ") " + i18n.t("views.comp_status.obs"))
			var span_ok = $("<span style='color:#3aaa50;padding:3px'></span>")
			span_ok.text(data.ok + " (" + fp_ok + ") " + i18n.t("views.comp_status.ok"))
			var span_na = $("<span style='color:#acacac;padding:3px'></span>")
			span_na.text(data.na + " (" + fp_na + ") " + i18n.t("views.comp_status.na"))
			var span_nok = $("<span style='color:#FF7863;padding:3px'></span>")
			span_nok.text(data.nok + " (" + fp_nok + ") " + i18n.t("views.comp_status.nok"))

			d1.append(d2)
			d1.append(d3)
                        d2.append(div_obs)
                        d2.append(div_ok)
                        d2.append(div_na)
                        d3.append(span_obs)
                        d3.append(span_ok)
                        d3.append(span_na)
                        d3.append(span_nok)
			$("#"+divid).html(d1)
	})
}

function view_comp_status(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/comp_status.html", function() {
		$(this).i18n()
		var t = table_comp_status("cs0", options)
		t.options.on_change = function() {
			comp_status_agg("agg", {"table": t})
		}
		$("#cms_a").bind("click", function() {
			if (!$("#cms").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cms").show()
				table_comp_module_status("cms", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cms").hide()
			}
		})
		$("#cns_a").bind("click", function() {
			if (!$("#cns").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cns").show()
				table_comp_node_status("cns", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cns").hide()
			}
		})
		$("#css_a").bind("click", function() {
			if (!$("#css").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#css").show()
				table_comp_service_status("css", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#css").hide()
			}
		})
	})

}

function comp_status_log_on_hover(t) {
	t.div.find("[name$=_c_run_status]").hover(
	function() {
		line = $(this).parents("tr")
		var s = line.children("[name$=_c_run_status]")
		var e = line.children("[name$=_c_run_log]")
		var pos = s.position()
		e.width($(window).width()*0.8)
		e.css({"left": pos.left - e.width() - 10 + "px", "top": pos.top+s.parent().height() + "px"})
		e.addClass("white_float")
		cell_decorator_run_log(e)
		e.show()
	},
	function() {
		$(this).parents("tr").children("[name$=_c_run_log]").hide()
	})
}

function table_comp_status_node(divid, nodename) {
	var id = "cs_node_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_run_nodename"
	var request_vars = {}
	request_vars[f] = nodename

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_node",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_svcname', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}

function table_comp_status_svc(divid, svcname) {
	var id = "cs_svc_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_run_svcname"
	var request_vars = {}
	request_vars[f] = svcname

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_svc",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_nodename', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}


