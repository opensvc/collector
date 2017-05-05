//
// cell decorators
//

var db_tables = {
	"packages": {
		"cl": "pkg16",
		"hide": false,
		"name": "packages",
		"title": "packages"
	},
	"v_tags": {
		"cl": "tag16",
		"hide": false,
		"name": "v_tags",
		"title": "tags"
	},
	"v_comp_moduleset_attachments": {
		"cl": "modset16",
		"hide": false,
		"name": "v_comp_moduleset_attachments",
		"title": "moduleset attachments"
	},
	"svcmon": {
		"cl": "svc",
		"hide": false,
		"name": "svcmon",
		"title": "service status"
	},
	"services": {
		"cl": "svc",
		"hide": false,
		"name": "services",
		"title": "services"
	},
	"diskinfo": {
		"cl": "hd16",
		"hide": false,
		"name": "diskinfo",
		"title": "disks"
	},
	"svcdisks": {
		"cl": "hd16",
		"hide": false,
		"name": "svcdisks",
		"title": "svcdisks"
	},
	"nodes": {
		"cl": "node16",
		"hide": false,
		"name": "nodes",
		"title": "nodes"
	},
	"apps": {
		"cl": "svc",
		"hide": false,
		"name": "apps",
		"title": "apps"
	},
	"resmon": {
		"cl": "action16",
		"hide": false,
		"name": "resmon",
		"title": "resources"
	},
	"node_hba": {
		"cl": "node16",
		"hide": false,
		"name": "node_hba",
		"title": "node host bus adapaters"
	}
}


var action_img_h = {
	'checks': 'check16',
	'enable': 'check16',
	'disable': 'nok',
	'pushservices': 'svc',
	'pushpkg': 'pkg16',
	'pushpatch': 'pkg16',
	'reboot': 'action_restart_16',
	'shutdown': 'action_stop_16',
	'syncservices': 'action_sync_16',
	'sync_services': 'action_sync_16',
	'updateservices': 'action16',
	'updatepkg': 'pkg16',
	'updatecomp': 'pkg16',
	'stop': 'action_stop_16',
	'stopapp': 'action_stop_16',
	'stopdisk': 'action_stop_16',
	'stopvg': 'action_stop_16',
	'stoploop': 'action_stop_16',
	'stopip': 'action_stop_16',
	'stopfs': 'action_stop_16',
	'umount': 'action_stop_16',
	'shutdown': 'action_stop_16',
	'boot': 'action_start_16',
	'pull': 'csv',
	'start': 'action_start_16',
	'startstandby': 'action_start_16',
	'startapp': 'action_start_16',
	'startdisk': 'action_start_16',
	'startvg': 'action_start_16',
	'startloop': 'action_start_16',
	'startip': 'action_start_16',
	'startfs': 'action_start_16',
	'mount': 'action_start_16',
	'restart': 'action_restart_16',
	'provision': 'prov',
	'switch': 'action_switch_16',
	'freeze': 'frozen16',
	'thaw': 'frozen16',
	'sync_all': 'action_sync_16',
	'sync_nodes': 'action_sync_16',
	'sync_drp': 'action_sync_16',
	'syncall': 'action_sync_16',
	'syncnodes': 'action_sync_16',
	'syncdrp': 'action_sync_16',
	'syncfullsync': 'action_sync_16',
	'postsync': 'action_sync_16',
	'push': 'log16',
	'check': 'check16',
	'fixable': 'fixable16',
	'fix': 'comp16',
	'pushstats': 'chart16',
	'pushasset': 'node16',
	'stopcontainer': 'action_stop_16',
	'startcontainer': 'action_start_16',
	'stopapp': 'action_stop_16',
	'startapp': 'action_start_16',
	'prstop': 'action_stop_16',
	'prstart': 'action_start_16',
	'push': 'svc',
	'syncquiesce': 'action_sync_16',
	'syncresync': 'action_sync_16',
	'syncupdate': 'action_sync_16',
	'syncverify': 'action_sync_16',
	'toc': 'action_toc_16',
	'stonith': 'action_stonith_16',
	'switch': 'action_switch_16'
}


var os_class_h = {
	'darwin': 'os_darwin',
	'linux': 'os_linux',
	'hp-ux': 'os_hpux',
	'osf1': 'os_tru64',
	'opensolaris': 'os_opensolaris',
	'solaris': 'os_solaris',
	'sunos': 'os_solaris',
	'freebsd': 'os_freebsd',
	'aix': 'os_aix',
	'windows': 'os_win',
	'vmware': 'os_vmware'
}

var img_h = {
	'responsible': 'guys16',
	'publication': 'guys16',
	'form': 'wf16',
	'ack': 'check16',
	'action': 'action16',
	'action_queue': 'action16',
	'add': 'add16',
	'apps': 'svc',
	'attach': 'attach16',
	'auth': 'lock',
	'change': 'edit16',
	'check': 'check16',
	'checks': 'check16',
	'compliance': 'comp16',
	'contextual_settings': 'filter16',
	'delete': 'del16',
	'detach': 'detach16',
	'dns': 'dns16',
	'filterset': 'filter16',
	'filter': 'filter16',
	'group': 'guys16',
	'link': 'link16',
	'message': 'im',
	'moduleset': 'action16',
	'module': 'action16',
	'networks': 'net16',
	'node': 'node16',
	'password': 'lock',
	'rename': 'edit16',
	'service': 'svc',
	'status': 'fa-status',
	'status': 'fa-status',
	'table_settings': 'settings',
	'table_filters': 'filter16',
	'update': 'edit16',
	'user': 'guy16',
	'users': 'guys16',
	'tag': 'tag16'
}

function cell_decorator_var_class(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			text: v,
			cl: "icon wf16",
			bgcolor: osvc.colors.form,
			fn: function(id){form_tabs(id, {"form_name": v})}
		})
	})
}

function cell_decorator_var_name(e, line) {
	var v = $.data(e[0], "v")
	var var_id = $.data(line.children("[col=id]")[0], "v")
	var rset_id = $.data(line.children("[col=ruleset_id]")[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			text: v,
			cl: "icon comp16",
			bgcolor: osvc.colors.comp,
			fn: function(id){variable_tabs(id, {"ruleset_id": rset_id, "variable_id": var_id, "variable_name": v})}
		})
	})
}

function cell_decorator_log_icons(e, line) {
	var action = $.data(line.children("[col=log_action]")[0], "v")
	var l = action.split(".")
	var span = $("<span></span>")
	span.attr("title", action).tooltipster()
	for (var i=0; i<l.length; i++) {
		var w = l[i]
		if (!(w in img_h)) {
			continue
		}
		var cl = img_h[w]
		var icon = $("<span class='iconlist'></span>")
		icon.addClass(cl+" icon")
		span.append(icon)
	}
	e.html(span)
}

function cell_decorator_boolean(e, line) {
	var v = $.data(e[0], "v")
	true_vals = [1, "1", "T", "True", "true", true]
	if (typeof v === "undefined") {
		var cl = ""
	} else if (true_vals.indexOf(v) >= 0) {
		var cl = "fa toggle-on"
	} else {
		var cl = "fa toggle-off"
	}
	s = $("<span class='"+cl+"' title='"+v+"'></span>").tooltipster()
	e.html(s)
}

function cell_decorator_app(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			id: "app-"+v,
			cl: "icon app16",
			text: v,
			bgcolor: osvc.colors.app,
			fn: function(id){app_tabs(id, {"app_name": v})}
		})
	})
}

function cell_decorator_dns_domain(e, line) {
	var v = $.data(e[0], "v")
	var domain_id = $.data(line.children("[col=id]")[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			text: v,
			cl: "icon dns16",
			bgcolor: osvc.colors.dns,
			fn: function(id){dns_domain_tabs(id, {"domain_id": domain_id, "domain_name": v})}
		})
	})
}

function cell_decorator_dns_record(e, line) {
	var v = $.data(e[0], "v")
	var record_id =  $.data(line.children("[col=id]")[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			text: v,
			cl: "icon dns16",
			bgcolor: osvc.colors.dns,
			fn: function(id){dns_record_tabs(id, {"record_id": record_id, "record_name": v})}
		})
	})
}

function cell_decorator_disk_array_dg(e, line) {
	var v = $.data(e[0], "v")
	e.addClass("corner-top").empty()
	v.split(", ").forEach(function(v) {
		$("<div class='clickable link pl-1 pr-1'>"+v+"</div>")
		.on("click", function(){
			var array_name = $.data(line.children("[col=array_name],[col=disk_arrayid]")[0], "v")
			osvc.flash.show({
				id: "dg-"+v,
				text: v,
				cl: "icon diskgroup",
				bgcolor: osvc.colors.disk,
				fn: function(id){
					diskgroup_tabs(id, {"array_name": array_name, "dg_name": v})
				}
			})
		})
		.appendTo(e)
	})
}


function cell_decorator_disk_id(e, line) {
	var v = $.data(e[0], "v")
	e
	.attr("disk_id", v)
	.addClass("corner-top")
	.osvc_disk({"tag": false, "event": "click"})
}

function cell_decorator_disk_array(e, line) {
	var v = $.data(e[0], "v")
	e
	.addClass("corner-top")
	.osvc_array({"tag": false, "event": "click"})
}

function cell_decorator_quota(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner")
	.on("click", function(){
		var quota_id = $.data(line.children("[col=id]")[0], "v")
		var id = toggle_extraline(e)
		quota_tabs(id, {"quota_id": quota_id})
	})
}

function cell_decorator_prov_template(e, line) {
	var v = $.data(e[0], "v")
	var tpl_id = $.data(line.children("[col=id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_prov_template({"tag": false, "event": "click", "tpl_id": tpl_id})
}

function cell_decorator_fset_name(e, line) {
	var v = $.data(e[0], "v")
		if (v == "empty") {
		return
	}
	e
	.addClass("corner-top")
	.osvc_filterset({"tag": false, "event": "click"})
}

function cell_decorator_modset_name(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			id: "modset-"+v,
			text: v, 
			cl: "icon modset16",
			bgcolor: osvc.colors.comp,
			fn: function(id){moduleset_tabs(id, {"modset_name": v})}
		})
	})
}

function cell_decorator_ruleset_name(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			id: "rset-"+v,
			text: v, 
			cl: "icon rset16",
			bgcolor: osvc.colors.comp,
			fn: function(id){ruleset_tabs(id, {"ruleset_name": v})}
		})
	})
}

function cell_decorator_report_name(e, line) {
	var v = $.data(e[0], "v")
	var report_id = $.data(line.children("[col=id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_report({"tag": false, "event": "click", "report_id": report_id, "report_name": v})
}

function cell_decorator_chart_name(e, line) {
	var v = $.data(e[0], "v")
	var chart_id = $.data(line.children("[col=id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_chart({"tag": false, "event": "click", "chart_id": chart_id, "chart_name": v})
}

function cell_decorator_metric_name(e, line) {
	var v = $.data(e[0], "v")
	var metric_id = $.data(line.children("[col=id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_metric({"tag": false, "event": "click", "metric_id": metric_id, "metric_name": v})
}

function cell_decorator_form_name(e, line) {
	var v = $.data(e[0], "v")
	var form_id = $.data(line.children("[col=id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_form({"tag": false, "event": "click", "form_id": form_id, "form_name": v})
}

function cell_decorator_docker_repository(e, line) {
	var v = $.data(e[0], "v")
	var repository_id = $.data(line.children("[col=repository_id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_docker_repository({"tag": false, "event": "click", "repository_id": repository_id, "repository_name": v})
}

function cell_decorator_docker_registry(e, line) {
	var v = $.data(e[0], "v")
	var registry_id = $.data(line.children("[col=registry_id]")[0], "v")
	e
	.addClass("corner-top")
	.osvc_docker_registry({"tag": false, "event": "click", "registry_id": registry_id, "registry_service": v})
}

function cell_decorator_network(e, line) {
	var v = $.data(e[0], "v")
	var name = $.data(line.children("[col=name]")[0], "v")
	e
	.html("<span class='clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		var net_id = $.data(line.children("[col=id],[col=net_id]")[0], "v")
		osvc.flash.show({
			id: "net-"+net_id,
			text: name, 
			cl: "icon net16",
			bgcolor: osvc.colors.net,
			fn: function(id){network_tabs(id, {"network_id": net_id})}
		})
	})
}

function cell_decorator_chk_instance(e, line) {
	var v = $.data(e[0], "v")
	var chk_type = $.data(line.children("[col=chk_type]")[0], "v")
	if (chk_type == "mpath") {
		var disk_id = $.data(line.children("[col=chk_instance]")[0], "v")
		var s = "<a class='icon hd16 nowrap'>"+v+"</a>"
		e
		.html(s)
		.addClass("corner")
		.on("click", function(){
			var id = toggle_extratable(e)
			var req = {}
			req[id+"_f_disk_id"] = disk_id
			table_disks(id, {"id": id, "request_vars": req, "volatile_filters": true})
		})
	}
}

function cell_decorator_chk_high(e, line) {
	var high = $.data(e[0], "v")
	try {
		var err = $.data(line.children("[col=chk_err]")[0], "v")
	} catch(e) {
		return
	}
	var cl = []
	err = parseInt(err)
	if (err == 2) {
		cl.push("highlight")
	}
	e.html("<span class='"+cl.join(" ")+"'>"+high+"</span>")
}

function cell_decorator_chk_low(e, line) {
	var low = $.data(e[0], "v")
	try {
		var err = $.data(line.children("[col=chk_err]")[0], "v")
	} catch(e) {
		return
	}
	var cl = []
	err = parseInt(err)
	if (err == 1) {
		cl.push("highlight")
	}
	e.html("<span class='"+cl.join(" ")+"'>"+low+"</span>")
}

function cell_decorator_chk_value(e, line) {
	var v = $.data(e[0], "v")
	var low = $.data(line.children("[col=chk_low]")[0], "v")
	var high = $.data(line.children("[col=chk_high]")[0], "v")
	var cl = []
	v = parseInt(v)
	low = parseInt(low)
	high = parseInt(high)
	if ((v > high) || (v < low)) {
		cl.push("highlight")
	}
	e.html("<span class='"+cl.join(" ")+"'>"+v+"</span>")
}

function cell_decorator_action_pid(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		e.empty()
		return
	}
	var s = "<a>"+v+"</a>"
	e
	.html(s)
	.on('click', function(){
		var node_id = $.data(line.children("[col=node_id]")[0], "v")
		var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
		var begin = $.data(line.children("[col=begin]")[0], "v")
		var end = $.data(line.children("[col=end]")[0], "v")

		var _begin = begin.replace(/ /, "T")
		var d = new Date(+new Date(_begin) - 1000*60*60*24)
		begin = print_date(d)

		var _end = end.replace(/ /, "T")
		var d = new Date(+new Date(_end) + 1000*60*60*24)
		end = print_date(d)

		url = services_get_url() + "/init/svcactions/svcactions?actions_f_svc_id="+svc_id+"&actions_f_node_id="+node_id+"&actions_f_pid="+v+"&actions_f_begin=>"+begin+"&actions_f_end=<"+end+"&volatile_filters=true"

		$(this).children("a").attr("href", url)
		$(this).children("a").attr("target", "_blank")
		//$(this).children("a").click()
	})
}

function cell_decorator_action_status(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		e.html("<div class='icon spinner'></div>")
		return
	}
	cl = ["status_"+v.replace(' ', '_')]
	var ack = $.data(line.children("[col=ack]")[0], "v")
	if (ack == 1) {
		cl.push("ack_1")
	}
	s = "<div class='"+cl.join(" ")+"'>"+v+"</diV>"
	e.html(s)
	if (ack != 1) {
		return
	}
	var acked_date = $.data(line.children("[col=acked_date]")[0], "v")
	var acked_by = $.data(line.children("[col=acked_by]")[0], "v")
	var acked_comment = $.data(line.children("[col=acked_comment]")[0], "v")
	s = "<div>"
	s += "<b>acked by </b>"+acked_by+"<br>"
	s += "<b> on </b>"+acked_date+"<br>"
	s += "<b>with comment:</b><br>"+acked_comment
	s += "</div>"
	e.children().attr("title",  s).tooltipster({contentAsHTML: true})
}

function cell_decorator_action_end(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		e.empty()
		return
	} else if (v == "1000-01-01 00:00:00") {
		e.html("<span class='highlight'>timed out</span>")
		return
	}
	var id = $.data(line.children("[col=id]")[0], "v")
	s = "<span class='highlight nowrap' id='spin_span_end_"+id+"'>"+v+"</span>"
}

function cell_decorator_action_log(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		e.empty()
		return
	}
	s = "<pre>"+v+"</pre>"
	e.html(s)
}

function cell_decorator_db_table_name(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		return
	}
	var s = $("<span class='nowrap'>"+v+"</span>")
	if (v in db_tables) {
		s.text(db_tables[v].title)
		s.addClass("icon "+db_tables[v].cl)
	}
	e.html(s)
}

function cell_decorator_db_column_name(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		return
	}
	var s = $("<span class='nowrap'>"+v+"</span>")
	if (v in colprops) {
		s.text(colprops[v].title)
		s.addClass("icon "+colprops[v].img)
	}
	e.html(s)
}

function cell_decorator_action(e, line) {
	var v = $.data(e[0], "v")
	var status_log = $.data(line.children("[col=status_log]")[0], "v")
	cl = []
	if (status_log == "empty") {
		cl.push("metaaction")
	}
	action = v.split(/\s+/).pop()
	if (action in action_img_h) {
		cl.push(action_img_h[action])
	}
	s = "<div class='icon "+cl.join(" ")+"'>"+v+"</div>"
	e.html(s)
}

function cell_decorator_docker_tag_digest(e, line) {
	var v = $.data(e[0], "v")
	if ((v == "empty") || (v == "")) {
		e.empty()
		return
	}
	s = $("<a class='icon resource'>"+v+"</a>")
	e.addClass("corner")
	s.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var id = toggle_extratable(e)
		table_resinfo(id, {
			"volatile_filters": true,
			"request_vars": {
				"resinfo_f_res_value": v
			}
		})
	})
	e.html(s)
}

function cell_decorator_svc_action_err(e, line) {
	var v = $.data(e[0], "v")
	if (v == "empty") {
		e.empty()
		return
	}
	s = $("<a class='icon action16 icon-red clickable'>"+v+"</a>")
	s.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
		var id = toggle_extratable(e)
		table_actions(id, {
			"volatile_filters": true,
			"hide_cols": ["svc_id"],
			"request_vars": {
				"actions_f_svc_id": svc_id,
				"actions_f_status": "err",
				"actions_f_ack": "!1|empty",
				"actions_f_begin": ">-300d"
			}
		})
	})
	e.html(s)
}

function cell_decorator_obs_type(e, line) {
	var v = $.data(e[0], "v")
	if ((v=="") || (v=="empty")) {
		return
	}
	div = $("<div class='nowrap'>"+v+"</div>")
	e.html(div)
	if (v == "os") {
		div.addClass("icon os16")
	} else if (v == "hw") {
		div.addClass("icon hw16")
	}
}

function cell_decorator_nodename(e, line) {
	_cell_decorator_nodename(e, true, line)
}

function cell_decorator_nodename_no_os(e, line) {
	_cell_decorator_nodename(e, false, line)
}

function _cell_decorator_nodename(e, os_icon, line) {
	var v = $.data(e[0], "v")
	var node_id = $.data(line.children("[col=node_id]")[0], "v")
	if ((v=="") || (v=="empty")) {
		return
	}
	var div = $("<div class='a nowrap trunc20'>"+v+"</div>")
	if (os_icon) {
		try {
			var os_name = $.data(line.children("[col=os_name]")[0], "v")
			os_c = os_class_h[os_name.toLowerCase()]
			div.addClass(os_c)
		} catch(e) {}
	}
	try {
		svc_autostart_cell = e.parent().children(".svc_autostart")[0]
		if ($.data(svc_autostart_cell, "v") == v) {
			div.addClass("b")
		}
	} catch(err) {}
	e
	.html(div)
	.addClass("corner-top")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		osvc.flash.show({
			id: "node-"+node_id,
			text: v,
			cl: "icon node16",
			bgcolor: osvc.colors.node,
			fn: function(id){node_tabs(id, {"node_id": node_id})}
		})
	})
}

function cell_decorator_groups(e, line) {
	var v = $.data(e[0], "v")
	if ((v=="") || (v=="empty")) {
		return
	}
	l = v.split(', ')
	s = ""
	for (i=0; i<l.length; i++) {
		g = l[i]
		s += "<span>"+g+"</span> "
	}
	e
	.addClass("corner-top")
	.html(s)
	.children().osvc_org_group({
		"event": "click",
		"tag": false,
		"show_icon": false
	})
}

function cell_decorator_user_id(e, line) {
	var v = $.data(e[0], "v")
	if ((v=="") || (v=="empty")) {
		return
	}
	var fullname = $.data(line.children("[col=fullname]")[0], "v")
	e
	.addClass("corner-top")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		osvc.flash.show({
			id: "user-"+fullname,
			text: v, 
			cl: "icon guy16",
			bgcolor: osvc.colors.user,
			fn: function(id){user_tabs(id, {"user_id": v, "fullname": fullname})}
		})
	})
}

function cell_decorator_username(e, line) {
	var v = $.data(e[0], "v")
	if ((v=="") || (v=="empty")) {
		return
	}
	e
	.addClass("corner-top")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var table_id = e.parents("table").attr("id").replace(/^table_/, '')
		var data = {"fullname": v}
		if (table_id.match(/^users/)) {
			var user_id = $.data(line.children("[col=id]")[0], "v")
			data["user_id"] = user_id
			flash_id = "user-" + user_id
		} else {
			flash_id = "user-" + v
		}
		osvc.flash.show({
			id: flash_id,
			text: v, 
			cl: "icon guy16",
			bgcolor: osvc.colors.user,
			fn: function(id){user_tabs(id, data)}
		})
	})
}

function cell_decorator_safe_file(e, line) {
	var uuid = $.data(e[0], "v")
	if ((uuid=="") || (uuid=="empty")) {
		return
	}
	e
	.html("<div class='a nowrap trunc20'>"+uuid+"</div>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
                        text: uuid,
                        cl: "icon safe16",
                        bgcolor: osvc.colors.comp,
                        fn: function(id){safe_file_tabs(id, {"uuid": uuid})}
                })
	})
}

function cell_decorator_svcname(e, line) {
	var v = $.data(e[0], "v")
	var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
	if ((svc_id=="") || (svc_id=="empty")) {
		return
	}
	e
	.html("<div class='a nowrap trunc20'>"+v+"</div>")
	.addClass("corner-top")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		osvc.flash.show({
			id: "svc-"+svc_id,
			text: v,
			cl: "icon svc",
			bgcolor: osvc.colors.svc,
			fn: function(id){service_tabs(id, {"svc_id": svc_id})}
		})
	})
}

function cell_decorator_res_log(e, line) {
	var v = $.data(e[0], "v")
	e.css({"white-space": "pre"})
	var s = v
		.replace(/info: /g, "<span style='width:5em' class='mr-2 btn btn-sm btn-info'>info</span>")
		.replace(/warn: /g, "<span style='width:5em' class='mr-2 btn btn-sm btn-warning'>warn</span>")
		.replace(/err: /g, "<span style='width:5em' class='mr-2 btn btn-sm btn-danger'>err</span>")
	e.html(s)
}

function cell_decorator_log_event(e, line) {
	var d = $.data(line.children("[col=log_dict]")[0], "v")
	var fmt = $.data(line.children("[col=log_fmt]")[0], "v")
	if (!d || (d.length == 0)) {
		e.html(fmt)
		return
	}
	try {
		d = $.parseJSON(d)
	} catch(err) {
		e.html(i18n.t("decorators.corrupted_log"))
		return
	}
	for (key in d) {
		var re = RegExp("%\\("+key+"\\)[sd]", "g")
		fmt = fmt.replace(re, "<b>"+d[key]+"</b>")
	}
	e.html(fmt)
}

function cell_decorator_log_level(e, line) {
	var v = $.data(e[0], "v")
	var t = {
		"warning": "icon-orange",
		"info": "icon-green",
		"error": "icon-red",
	}
	if (v in t) {
		var cl = t[v]
	} else {
		var cl = ""
	}
	e.addClass(cl)
}

function cell_decorator_status(e, line) {
	var v = $.data(e[0], "v")
	if ((v=="") || (v=="empty")) {
		v = "undef"
	}
	var c = v
	if (status_outdated(line)) {
		c = "undef"
	}
	var t = {
		"warn": "orange",
		"up": "green",
		"stdby up": "green",
		"down": "red",
		"stdby down": "red",
		"undef": "gray",
		"n/a": "gray"
	}
	e.html("<div class='nowrap icon-"+t[c]+"'>"+v+"</div>")
}

function cell_decorator_dns_records_type(e, line) {
	var v = $.data(e[0], "v")
	var cl = ["boxed_small"]
	if ((v == "A") || (v == "PTR")) {
		cl.push("bgblack")
	} else if (v == "CNAME") {
		cl.push("bggreen")
	} else {
		cl.push("bgred")
	}
	e.html("<div class='"+cl.join(" ")+"'>"+v+"</div>")
}

function cell_decorator_svcmon_link_frozen(e, line) {
	var mon_frozen = $.data(line.children("[col=mon_frozen]")[0], "v")
	if (mon_frozen == "1") {
		var s = $("<span class='icon frozen16'>&nbsp</span>")
	} else {
		var s = null
	}
	return s
}

function cell_decorator_svcmon_links(e, line) {
	e.html(
		cell_decorator_svcmon_link_frozen(e, line)
	)
}

function cell_decorator_comp_log(e, line) {
	var module = $.data(line.find("[col=run_module]")[0], "v")
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	var node_id = $.data(line.find("[col=node_id]")[0], "v")
	var div = $("<div class='icon chart16'></div>")
	div
	.addClass("a")
	.addClass("nowrap")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var id = toggle_extraline(e)
		comp_log(id, {"module": module, "svc_id": svc_id, "node_id": node_id})
	})
}

function cell_decorator_comp_mod_log(e, line) {
	var modname = $.data(line.find("[col=mod_name]")[0], "v")
	var div = $("<div class='a nowrap icon chart16'></div>")
	div
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var table_id = e.parents("table").attr("id").replace(/^table_/, '')
		var span_id = e.parent(".tl").attr("spansum")
		var id = table_id + "_x_" + span_id
		var url = services_get_url() + "/init/compliance/ajax_mod_history?modname="+modname+"&rowid="+id
		toggle_extra(url, id, e, 0)
	})
}

function cell_decorator_comp_node_log(e, line) {
	var node_id = $.data(line.find("[col=node_id]")[0], "v")
	var div = $("<div class='icon chart16 a nowrap'></div>")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var table_id = e.parents("table").attr("id").replace(/^table_/, '')
		var span_id = e.parent(".tl").attr("spansum")
		var id = table_id + "_x_" + span_id
		var url = services_get_url() + "/init/compliance/ajax_node_history?node_id="+node_id+"&rowid="+id
		toggle_extra(url, id, e, 0)
	})
}

function cell_decorator_comp_svc_log(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	var div = $("<div class='icon chart16 a nowrap'></div>")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var table_id = e.parents("table").attr("id").replace(/^table_/, '')
		var span_id = e.parent(".tl").attr("spansum")
		var id = table_id + "_x_" + span_id
		var url = services_get_url() + "/init/compliance/ajax_svc_history?svc_id="+svc_id+"&rowid="+id
		toggle_extra(url, id, e, 0)
	})
}

function cell_decorator_uid(e, line) {
	var v = $.data(e[0], "v")
	if (v == "") {
		return
	}
	var div = $("<div class='a nowrap'>"+v+"</div>")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var url = services_get_url() + "/init/nodes/ajax_uid_dispatch?user_id="+v
		toggle_extra(url, null, e, 0)
	})
}

function cell_decorator_gid(e, line) {
	var v = $.data(e[0], "v")
	if (v == "") {
		return
	}
	var div = $("<div class='a nowrap'>"+v+"</div>")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var url = services_get_url() + "/init/nodes/ajax_gid_dispatch?group_id="+v
		toggle_extra(url, null, e, 0)
	})
}

function cell_decorator_chk_type(e, line) {
	var v = $.data(e[0], "v")
	if (v == "") {
		return
	}
	var div = $("<div class='a nowrap'>"+v+"</div>")
	e
	.html(div)
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var id = toggle_extratable(e)
		table_checks_defaults_type(id, v)
	})
}

function cell_decorator_dash_link_comp_svcdiff(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	s = "<div class='icon comp16 clickable'></div>"
	e
	.html(s)
	.addClass("corner")
	e.on("click", function(){
		var id = toggle_extraline(e)
		t = $("<h2 data-i18n='diff.comp_title'></h2>")
		d = $("<div></div>")
		d.uniqueId()
		$("#"+id).append(t)
		$("#"+id).append(d)
		sync_ajax('/init/compliance/ajax_compliance_svcdiff?node='+svc_id, [], d.attr("id"), function(){})
	})
}

function cell_decorator_dash_link_comp_tab(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	var node_id = $.data(line.find("[col=node_id]")[0], "v")
	s = "<div class='icon comp16 clickable'></div>"
	e
	.html(s)
	.addClass("corner")
	if (svc_id != "") {
		e.on("click", function(){
			var id = toggle_extraline(e)
			service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.compliance"})
		})
	} else if (node_id != "") {
		e.on("click", function(){
			var id = toggle_extraline(e)
			node_tabs(id, {"node_id": node_id, "tab": "node_tabs.compliance"})
		})
	}
}

function cell_decorator_dash_link_pkg_tab(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	e
	.html("<div class='icon pkg16 clickable'></div>")
	.addClass("corner")
	if (svc_id != "") {
		e.on("click", function(){
			var id = toggle_extraline(e)
			service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.pkgdiff"})
		})
	}
}

function cell_decorator_dash_link_feed_queue(e, line) {
	e.html("<a class='icon action16' href=''></a>")
}

function _cell_decorator_dash_link_actions(svc_id, e) {
	s = $("<a class='icon action16 clickable'></a>")
	s.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var id = toggle_extratable(e)
		table_actions(id, {
			"volatile_filters": true,
			"hide_cols": ["svc_id"],
			"request_vars": {
				"actions_f_svc_id": svc_id,
				"actions_f_begin": ">-7d"
			}
		})
	})
	return s
}

function cell_decorator_obs_count(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<a class='icon node16 clickable'>"+v+"</a>")
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var obs_name = $.data(line.find("[col=obs_name]")[0], "v")
		var obs_type = $.data(line.find("[col=obs_type]")[0], "v")
		var options = {
			"volatile_filters": true,
			"request_vars": {}
		}
		if (obs_type == "hw") {
			options.request_vars.nodes_f_model = obs_name
		} else {
			options.request_vars.nodes_f_os_concat = obs_name
		}
		var id = toggle_extratable(e)
		table_nodes(id, options)
	})
}

function _cell_decorator_dash_link_action_error(svc_id, e) {
	s = $("<a class='icon alert16 clickable'></a>")
	s.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var id = toggle_extratable(e)
		table_actions(id, {
			"volatile_filters": true,
			"hide_cols": ["svc_id"],
			"request_vars": {
				"actions_f_svc_id": svc_id,
				"actions_f_status": "err",
				"actions_f_ack": "!1|empty",
				"actions_f_begin": ">-30d"
			}
		})
	})
	return s
}

function cell_decorator_dash_link_action_error(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	e
	.append(_cell_decorator_dash_link_action_error(svc_id, e))
	.append(_cell_decorator_dash_link_actions(svc_id, e))
}

function cell_decorator_dash_link_svcmon(e, line) {
	var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
	e
	.html("<div class='icon svc clickable'></div>")
	.addClass("corner")
	if (svc_id != "") {
		e.on("click", function(){
			var id = toggle_extraline(e)
			service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.status"})
		})
	}
}

function cell_decorator_dash_link_node(e, line) {
	var node_id = $.data(line.find("[col=node_id]")[0], "v")
	e
	.html("<div class='icon node16 clickable'></div>")
	.addClass("corner")
	if (node_id != "") {
		e.on("click", function(){
			var id = toggle_extraline(e)
			node_tabs(id, {"node_id": node_id, "tab": "node_tabs.properties"})
		})
	}
}

function cell_decorator_dash_link_checks(e, line) {
	var node_id = $.data(line.find("[col=node_id]")[0], "v")
	e
	.html("<div class='icon check16 clickable'></div>")
	.addClass("corner")
	if (node_id != "") {
		e.on("click", function(){
			var id = toggle_extratable(e)
			var req = {}
			req[id+"_f_node_id"] = node_id
			req[id+"_f_chk_err"] = ">0"
			table_checks(id, {
				"id": id,
				"request_vars": req,
				"hide_cols": ["node_id"],
				"volatile_filters": true
			})
		})
	}
}

function _cell_decorator_dash_link_mac_networks(mac) {
	url = services_get_url() + "/init/nodenetworks/nodenetworks?nodenetworks_f_mac="+mac+"&volatile_filters=true"
	s = "<a class='icon net16 clickable' target='_blank' href='"+url+"'></a>"
	return s
}

function cell_decorator_dash_link_mac_duplicate(e, line) {
	try {
		var mac = $.parseJSON($.data(line.find("[col=dash_dict]")[0], "v")).mac
	} catch(err) {
		console.log(err)
		return
	}
	e.html(_cell_decorator_dash_link_mac_networks(mac))
}

function cell_decorator_dash_link_obsolescence(e, line) {
	s = $("<a class='icon obs16 clickable'></a>")
	s.on("click", function(){
		if (get_selected() != "") {
			return
		}
		try {
			var name = $.parseJSON($.data(line.find("[col=dash_dict]")[0], "v")).o
		} catch(err) {
			console.log(err)
			return
		}
		var id = toggle_extratable(e)
		table_obsolescence(id, {
			"volatile_filters": true,
			"request_vars": {
				"obs_f_obs_name": name
			}
		})
	})
	e
	.html(s)
	.addClass("corner")
}

function cell_decorator_dash_links(e, line) {
	var dash_type = $.data(line.find("[col=dash_type]")[0], "v")
	if (dash_type == "action errors") {
		cell_decorator_dash_link_action_error(e, line)
	} else if ((dash_type == "node warranty expired") ||
		   (dash_type == "node without warranty end date") ||
		   (dash_type == "node without asset information") ||
		   (dash_type == "node close to warranty end") ||
		   (dash_type == "node information not updated")) {
		cell_decorator_dash_link_node(e, line)
	} else if ((dash_type == "check out of bounds") ||
		   (dash_type == "check value not updated")) {
		cell_decorator_dash_link_checks(e, line)
	} else if (dash_type == "mac duplicate") {
		cell_decorator_dash_link_mac_duplicate(e)
	} else if ((dash_type == "service available but degraded") ||
		   (dash_type == "service status not updated") ||
		   (dash_type == "service configuration not updated") ||
		   (dash_type == "service frozen") ||
		   (dash_type == "flex error") ||
		   (dash_type == "service unavailable")) {
		cell_decorator_dash_link_svcmon(e, line)
	} else if (dash_type == "feed queue") {
		cell_decorator_dash_link_feed_queue(e, line)
	} else if (dash_type.indexOf("os obsolescence") >= 0) {
		cell_decorator_dash_link_obsolescence(e, line)
	} else if (dash_type.indexOf("obsolescence") >= 0) {
		cell_decorator_dash_link_obsolescence(e, line)
	} else if (dash_type.indexOf("comp") == 0) {
		cell_decorator_dash_link_comp_svcdiff(e, line)
	} else if (dash_type.indexOf("package") == 0) {
		cell_decorator_dash_link_pkg_tab(e, line)
	}
}

function cell_decorator_action_cron(e, line) {
	var v = $.data(e[0], "v")
	var l = []
	if (v == 1) {
		l.push("icon time16")
	}
	e.html("<div class='"+l.join(" ")+"'></div>")
}

function cell_decorator_dash_severity(e, line) {
	var v = $.data(e[0], "v")
	if (v == 0) {
		cl = "icon-green"
		text = "info"
	} else if (v == 1) {
		cl = "icon-orange"
		text = "warning"
	} else if (v == 2) {
		cl = "icon-lightred"
		text = "error"
	} else if (v == 3) {
		cl = "icon-red"
		text = "critical"
	} else {
		cl = "icon-black"
		text = "alert"
	}
	e.text(text).addClass(cl)
}

function cell_decorator_form_id(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<span class='icon wf16 nowrap clickable'>"+v+"</span>")
	.addClass("corner-top")
	.on("click", function(){
		osvc.flash.show({
			id: "wf-"+v,
			cl: "icon wf16",
			text: v,
			bgcolor: osvc.colors.form,
			fn: function(id){workflow_tabs(id, {"form_id": v, "tab": "workflow_tabs.steps"})}
		})
	})
}

function cell_decorator_log_run_log(e, line) {
	cell_decorator_run_log(e, line, comp_log_tabs)
}
function cell_decorator_log_run_status(e, line) {
	cell_decorator_run_status(e, line, comp_log_tabs)
}
function cell_decorator_status_run_log(e, line) {
	cell_decorator_run_log(e, line, comp_status_tabs)
}
function cell_decorator_status_run_status(e, line) {
	cell_decorator_run_status(e, line, comp_status_tabs)
}

function cell_decorator_run_log(e, line, fn) {
	var v = $.data(e[0], "v")
	if (typeof v === "undefined") {
		var s = ""
	} else {
		var s = "<pre>"+v.replace(/ERR:/g, "<span class='err'>ERR:</span>")+"</pre>"
	}
	e.html(s)
	if (line != undefined) {
		e.addClass("corner-top")
		.on("click", function(){
			var log_id = $.data(line.children("[col=id]")[0], "v")
			osvc.flash.show({
				id: "complog-"+log_id,
				cl: "icon log16",
				text: log_id,
				bgcolor: osvc.colors.comp,
				fn: function(id){fn(id, {"id": log_id})}
			})
		})
	}
}

function cell_decorator_run_status(e, line, fn) {
	var v = $.data(e[0], "v")
	var s = ""
	var cl = ""
	var _v = ""
	if (v == 0) {
		cl = "ok"
	} else if (v == 1) {
		cl = "nok"
	} else if (v == 2) {
		cl = "na"
	} else if (v == -15) {
		cl = "kill16"
	} else {
		_v = v
	}
	e.html("<div class='icon "+cl+"'>"+_v+"</div>")
	if (line != undefined) {
		e.addClass("corner-top")
		.on("click", function(){
			var log_id = $.data(line.children("[col=id]")[0], "v")
			osvc.flash.show({
				id: "complog-"+log_id,
				cl: "icon log16",
				text: log_id,
				bgcolor: osvc.colors.comp,
				fn: function(id){fn(id, {"id": log_id})}
			})
		})
	}

}

function cell_decorator_tag_exclude(e, line) {
	generic_prop_updater(e, line, {
		"privileges": ["Manager", "TagManager"],
		"url": "/tags/%1",
		"prop": "tag_exclude",
		"id_prop": "tag_id",
	})
}

//
// options:
//  privileges: list of priv groups, one of which being required
//  url: the rest api url to post on
//  prop: the rest api url property to post an update on
//
function generic_prop_updater(e, line, options) {
	if (!options) {
		return
	}
	if (!options.privileges) {
		options.privileges = ["Manager"]
	}
	if (!options.id_prop) {
		options.id_prop = "id"
	}
	var v = $.data(e[0], "v")
	if (v == "empty") {
		v = ""
	}
	e.html(v)
	if (services_ismemberof(options.privileges)) {
		e.addClass("editable editable-placeholder")
		e.on("click", function(event){
			event.stopPropagation()
			e.removeClass("editable editable-placeholder")
			var i = $("<input class='oi tag_exclude'></input>")
			i.on("blur", function() {
				$(this).parent().html(v).addClass("editable editable-placeholder")
			})
			var _v = $.data(this, "v")
			if (_v == "empty") {
				_v = ""
			}
			i.val(_v)
			i.on("keyup", function(event){
				if (!is_enter(event)) {
					return
				}
				var line_id = $.data($(this).parents(".tl").find("[col="+options.id_prop+"]")[0], "v")
				var data = {}
				data[options.prop] = $(this).val()
				var _i = $(this)
				services_osvcpostrest(options.url, [line_id], "", data, function(jd) {
					if (jd.error && (jd.error.length > 0)) {
						osvc.flash.error(services_error_fmt(jd))
						return
					}
					_i.parent().html(data[options.prop]).addClass("editable editable-placeholder")
				},
				function(xhr, stat, error) {
					osvc.flash.info(services_ajax_error_fmt(xhr, stat, error))
				})
			})
			e.html(i)
			i.focus()
		})
	}
}

function cell_decorator_dash_entry(e, line) {
	var d = $.data(line.children("[col=dash_dict]")[0], "v")
	var fmt = $.data(line.children("[col=dash_fmt]")[0], "v")
	if (d && d.length>0) {
		try {
			d = $.parseJSON(d)
			for (key in d) {
				var re = RegExp("%\\("+key+"\\)[sd]", "g")
				fmt = fmt.replace(re, "<b>"+d[key]+"</b>")
			}
		} catch(err) {
			e.html(i18n.t("decorators.corrupted_log"))
			return
		}
	}
	e
	.html(fmt)
	.addClass("clickable corner")
	.on("click", function(){
		var options = {
			"node_id": $.data(line.children("[col=node_id]")[0], "v"),
			"svc_id": $.data(line.children("[col=svc_id]")[0], "v"),
			"dash_md5": $.data(line.children("[col=dash_md5]")[0], "v"),
			"dash_created": $.data(line.children("[col=dash_created]")[0], "v")
		}
		var id = toggle_extraline(e)
		alert_info(id, options)
	})
}

function cell_decorator_rset_md5(e, line) {
	var v = $.data(e[0], "v")
	e
	.html("<div class='clickable'>"+v+"</div>")
	.addClass("corner")
	.on("click", function(){
		if (get_selected() != "") {
			return
		}
		var url = services_get_url() + "/init/compliance/ajax_rset_md5?rset_md5="+v
		toggle_extra(url, null, this, 0)
	})
}

function cell_decorator_action_q_ret(e, line) {
	var v = $.data(e[0], "v")
	var cl = []
	if (typeof v == "number") {
		cl = ["boxed_small"]
		v = v.toString()
		if (v == 0) {
			cl.push("bggreen")
		} else {
			cl.push("bgred")
		}
	}
	var actionq_id = $.data(line.children("[col=id]")[0], "v")
	e.addClass("corner-top").html("<div class='"+cl.join(" ")+"'>"+v+"</div>")
	.on("click", function(){
		osvc.flash.show({
			text: actionq_id,
			cl: "icon action16",
			bgcolor: osvc.colors.action,
			id: "ret-"+actionq_id,
			fn: function(id){
				actionq_tabs(id, {"actionq_id": actionq_id, "retcode": v})
			}
		})
	})
}

function cell_decorator_action_q_status(e, line) {
	var v = $.data(e[0], "v")
	var st = ""
	var cl = ["boxed_small"]
	if (v == "T") {
		cl.push("bggreen")
		st = i18n.t("decorators.done")
	} else if (v == "R") {
		cl.push("bgred")
		st = i18n.t("decorators.running")
	} else if (v == "W") {
		st = i18n.t("decorators.waiting")
	} else if (v == "Q") {
		st = i18n.t("decorators.queued")
	} else if (v == "C") {
		cl.push("bgdarkred")
		st = i18n.t("decorators.cancelled")
	}
	e.html("<div class='"+cl.join(" ")+"'>"+st+"</div>")
}

function cell_decorator_env(e, line) {
	if ($.data(e[0], "v") != "PRD") {
		return
	}
	e.addClass("icon-red")
}

function cell_decorator_svc_ha(e, line) {
	if ($.data(e[0], "v") != 1) {
		e.empty()
		return
	}
	e.html("<div class='boxed_small'>HA</div>")
}

function cell_decorator_size_mb(e, line) {
	v = $.data(e[0], "v")
	if (v == "empty") {
		return
	}
	e.html("<div class='nowrap'>"+fancy_size_mb(v)+"</div>")
}

function cell_decorator_size_kb(e, line) {
	v = $.data(e[0], "v")
	if (v == "empty") {
		return
	}
	e.html("<div class='nowrap'>"+fancy_size_b(v*1024)+"</div>")
}

function cell_decorator_size_b(e, line) {
	v = $.data(e[0], "v")
	if (v == "empty") {
		return
	}
	e.html("<div class='nowrap'>"+fancy_size_b(v)+"</div>")
}

function cell_decorator_availstatus(e, line) {
	var mon_availstatus = $.data(e[0], "v")
	if (mon_availstatus=="") {
		return
	}
	var mon_containerstatus = $.data(line.children("[col=mon_containerstatus]")[0], "v")
	var mon_ipstatus = $.data(line.children("[col=mon_ipstatus]")[0], "v")
	var mon_fsstatus = $.data(line.children("[col=mon_fsstatus]")[0], "v")
	var mon_diskstatus = $.data(line.children("[col=mon_diskstatus]")[0], "v")
	var mon_sharestatus = $.data(line.children("[col=mon_sharestatus]")[0], "v")
	var mon_appstatus = $.data(line.children("[col=mon_appstatus]")[0], "v")

	if (status_outdated(line)) {
		var cl_availstatus = "status_undef"
		var cl_containerstatus = "status_undef"
		var cl_ipstatus = "status_undef"
		var cl_fsstatus = "status_undef"
		var cl_diskstatus = "status_undef"
		var cl_sharestatus = "status_undef"
		var cl_appstatus = "status_undef"
	} else {
		var cl_availstatus = mon_availstatus.replace(/ /g, '_')
		var cl_containerstatus = mon_containerstatus.replace(/ /g, '_')
		var cl_ipstatus = mon_ipstatus.replace(/ /g, '_')
		var cl_fsstatus = mon_fsstatus.replace(/ /g, '_')
		var cl_diskstatus = mon_diskstatus.replace(/ /g, '_')
		var cl_sharestatus = mon_sharestatus.replace(/ /g, '_')
		var cl_appstatus = mon_appstatus.replace(/ /g, '_')
	}
	var s = "<table>"
	s += "<tr>"
	s += "<td colspan=6 class=\"aggstatus status_" + cl_availstatus + "\">" + mon_availstatus + "</td>"
	s += "</tr>"
	s += "<tr>"
	s += "<td class=status_" + cl_containerstatus + ">vm</td>"
	s += "<td class=status_" + cl_ipstatus + ">ip</td>"
	s += "<td class=status_" + cl_fsstatus + ">fs</td>"
	s += "<td class=status_" + cl_diskstatus + ">dg</td>"
	s += "<td class=status_" + cl_sharestatus + ">share</td>"
	s += "<td class=status_" + cl_appstatus + ">app</td>"
	s += "</tr>"
	s += "</table>"
	e.html(s)
}

function cell_decorator_rsetvars(e, line) {
	var s = $.data(e[0], "v")
	e.html("<pre>"+s.replace(/\|/g, "\n")+"</pre>")
}

function cell_decorator_overallstatus(e, line) {
	var mon_overallstatus = $.data(e[0], "v")
	if (mon_overallstatus=="") {
		return
	}
	var mon_containerstatus = $.data(line.children("[col=mon_containerstatus]")[0], "v")
	var mon_availstatus = $.data(line.children("[col=mon_availstatus]")[0], "v")
	var mon_hbstatus = $.data(line.children("[col=mon_hbstatus]")[0], "v")
	var mon_syncstatus = $.data(line.children("[col=mon_syncstatus]")[0], "v")

	if (status_outdated(line)) {
		var cl_overallstatus = "status_undef"
		var cl_availstatus = "status_undef"
		var cl_syncstatus = "status_undef"
		var cl_hbstatus = "status_undef"
	} else {
		var cl_overallstatus = mon_overallstatus.replace(/ /g, '_')
		var cl_availstatus = mon_availstatus.replace(/ /g, '_')
		var cl_syncstatus = mon_syncstatus.replace(/ /g, '_')
		var cl_hbstatus = mon_hbstatus.replace(/ /g, '_')
	}

	var s = "<table>"
	s += "<tr>"
	s += "<td colspan=3 class=\"aggstatus status_" + cl_overallstatus + "\">" + mon_overallstatus + "</td>"
	s += "</tr>"
	s += "<tr>"
	s += "<td class=status_" + cl_availstatus + ">avail</td>"
	s += "<td class=status_" + cl_hbstatus + ">hb</td>"
	s += "<td class=status_" + cl_syncstatus + ">sync</td>"
	s += "</tr>"
	s += "</table>"
	e.html(s)
}

function cell_decorator_sql(e, line) {
	var s = $.data(e[0], "v")
	var _e = $("<pre></pre>")
	s = s.replace(/(SELECT|FROM|GROUP BY|WHERE)/gi, function(x) {
		return '<span class=syntax_red>'+x+'</span>'
	})
	s = s.replace(/(COUNT|DATE_SUB|SUM|MAX|MIN|CEIL|FLOOR|AVG|CONCAT|GROUP_CONCAT)/gi, function(x) {
		return '<span class=syntax_green>'+x+'</span>'
	})
	s = s.replace(/([\"\']\w*[\"\'])/gi, function(x) {
		return '<span class=syntax_blue>'+x+'</span>'
	})
	s = s.replace(/(%%\w+%%)/gi, function(x) {
		return '<span class=syntax_blue>'+x+'</span>'
	})
	_e.html(s)
	e.html(_e)
}

function cell_decorator_alert_type(e, line) {
	var s = $.data(e[0], "v")
	e.html(i18n.t("alert_type."+s))
}

function cell_decorator_tpl_definition(e, line) {
	var s = $.data(e[0], "v")
	_e = decorator_tpl_definition(s)
	e.html(_e)
}

function decorator_tpl_definition(s) {
	var _e = $("<pre></pre>")
	// sections
	s = s.replace(/(\[[#:\w]+\])/gi, function(x) {
		return '<span class=syntax_red>'+x+'</span>'
	})
	// env references
	s = s.replace(/({env\.\w+})/gi, function(x) {
		return '<span class="b syntax_green">'+x+'</span>'
	})
	// references
	s = s.replace(/({[\.\w]+})/gi, function(x) {
		return '<span class=syntax_green>'+x+'</span>'
	})
	// options
	s = s.replace(/\n\s*(\w+\s*=)/gi, function(x) {
		return '<span class=syntax_blue>'+x+'</span>'
	})
	_e.html(s)
	return _e
}

function cell_decorator_yaml(e, line) {
	var s = $.data(e[0], "v")
	var _e = $("<pre></pre>")
	s = s.replace(/Id:\s*(\w+)/gi, function(x) {
		return '<span class=syntax_red>'+x+'</span>'
	})
	s = s.replace(/(#\w+)/gi, function(x) {
		return '<span class=syntax_red>'+x+'</span>'
	})
	s = s.replace(/(\w+:)/gi, function(x) {
		return '<span class=syntax_green>'+x+'</span>'
	})
	_e.html(s)
	e.html(_e)
}

function cell_decorator_resinfo_key(e, line) {
	var s = $.data(e[0], "v")
	var _e = $("<div class='boxed_small'></div>")
	_e.text(s)
	if (s == "Error") {
		_e.addClass("bgred")
	} else {
		_e.addClass("bgblack")
	}
	e.html(_e)
}

function cell_decorator_resinfo_value(e, line) {
	var s = $.data(e[0], "v")
	var _e = $("<span></span>")
	_e.text(s)
	if (is_numeric(s)) {
		_e.addClass("icon chart16")
		e
		.addClass("corner clickable")
		.on("click", function() {
			var span_id = line.attr("spansum")
			var table_id = e.parents("table").attr("id").replace(/^table_/, '')
			var id = table_id + "_x_" + span_id
			var params = "svc_id="+encodeURIComponent($.data(line.children("[col=svc_id]")[0], "v"))
			params += "&node_id="+encodeURIComponent($.data(line.children("[col=node_id]")[0], "v"))
			params += "&rid="+encodeURIComponent($.data(line.children("[col=rid]")[0], "v"))
			params += "&key="+encodeURIComponent($.data(line.children("[col=res_key]")[0], "v"))
			params += "&rowid="+encodeURIComponent(id)
			var url = services_get_url() + "/init/resinfo/ajax_resinfo_log?" + params
			toggle_extra(url, id, e, 0)
		})
	}
	e.html(_e)
}

function cell_decorator_saves_charts(e, line) {
	var v = $.data(e[0], "v")
	var data = $.parseJSON(v)
	e.empty()
	if (data.chart_svc.data && data.chart_svc.data[0].length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_svc'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.services"))
		plot_div.text(JSON.stringify(data.chart_svc))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_ap.data && data.chart_ap.data[0].length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_ap'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.apps"))
		plot_div.text(JSON.stringify(data.chart_ap))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_group.data && data.chart_group.data[0].length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_group'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.groups"))
		plot_div.text(JSON.stringify(data.chart_group))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_server.data && data.chart_server.data[0].length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_server'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.servers"))
		plot_div.text(JSON.stringify(data.chart_server))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	e.append("<div class='spacer'></div>")
	e.append("<div id='chart_info'>-</div>")
	plot_savedonuts()
}

function cell_decorator_disks_charts(e, line) {
	var v = $.data(e[0], "v")
	var data = $.parseJSON(v)
	e.empty()
	if (data.chart_svc.data && data.chart_svc.data.length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_svc'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.services"))
		plot_div.text(JSON.stringify(data.chart_svc))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_ap.data && data.chart_ap.data.length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_ap'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.apps"))
		plot_div.text(JSON.stringify(data.chart_ap))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_dg.data && data.chart_dg.data.length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_dg'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.diskgroups"))
		plot_div.text(JSON.stringify(data.chart_dg))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	if (data.chart_ar.data && data.chart_ar.data.length > 0) {
		var div = $("<div style='float:left;width:500px'></div>")
		var plot_div = $("<div id='chart_ar'></div>")
		var title = $("<h3></h3>")
		title.text(i18n.t("decorators.charts.arrays"))
		plot_div.text(JSON.stringify(data.chart_ar))
		div.append(title)
		div.append(plot_div)
		e.append(div)
	}
	e.append("<div class='spacer'></div>")
	e.append("<div id='chart_info'>-</div>")
	plot_diskdonuts()
}

function cell_decorator_users_role(e, line) {
	var s = $.data(e[0], "v")
	e.empty()
	if (s == 1) {
		e.addClass("icon admin")
	} else {
		e.addClass("icon guy16")
	}
}

function cell_decorator_rule_value(e, line) {
	var var_id = $.data(line.children("[col=id]")[0], "v")
	var rset_id = $.data(line.children("[col=ruleset_id]")[0], "v")
	var var_class = $.data(line.children("[col=var_class]")[0], "v")
	var encap = $.data(line.children("[col=encap_rset]")[0], "v")
	if (encap != "") {
		var disable_edit = true
	} else {
		var disable_edit = false
	}
	try {
		var data = $.parseJSON($.data(e[0], "v"))
	} catch(err) {
		var data = $.data(e[0], "v")
	}
	form(e, {
		"data": data,
		"var_id": var_id,
		"rset_id": rset_id,
		"display_mode": true,
		"digest": true,
		"form_name": var_class,
		"disable_edit": disable_edit
	})
}

function cell_decorator_chk_def_high(e, line) {
	generic_prop_updater(e, line, {
		"privileges": ["Manager", "CheckManager"],
		"url": "/checks/defaults/%1",
		"prop": "chk_high",
	})
}

function cell_decorator_chk_def_low(e, line) {
	generic_prop_updater(e, line, {
		"privileges": ["Manager", "CheckManager"],
		"url": "/checks/defaults/%1",
		"prop": "chk_low",
	})
}

function cell_decorator_chk_def_prio(e, line) {
	generic_prop_updater(e, line, {
		"privileges": ["Manager", "CheckManager"],
		"url": "/checks/defaults/%1",
		"prop": "chk_prio",
	})
}

function cell_decorator_chk_def_inst(e, line) {
	generic_prop_updater(e, line, {
		"privileges": ["Manager", "CheckManager"],
		"url": "/checks/defaults/%1",
		"prop": "chk_inst",
	})
}

$.extend(true, cell_decorators, {
	"yaml": cell_decorator_yaml,
	"sql": cell_decorator_sql,
	"rsetvars": cell_decorator_rsetvars,
	"dash_entry": cell_decorator_dash_entry,
	"disk_array_dg": cell_decorator_disk_array_dg,
	"disk_array": cell_decorator_disk_array,
	"disk_id": cell_decorator_disk_id,
	"size_mb": cell_decorator_size_mb,
	"size_kb": cell_decorator_size_kb,
	"size_b": cell_decorator_size_b,
	"chk_instance": cell_decorator_chk_instance,
	"chk_value": cell_decorator_chk_value,
	"chk_low": cell_decorator_chk_low,
	"chk_high": cell_decorator_chk_high,
	"chk_def_high": cell_decorator_chk_def_high,
	"chk_def_low": cell_decorator_chk_def_low,
	"chk_def_prio": cell_decorator_chk_def_prio,
	"chk_def_inst": cell_decorator_chk_def_inst,
	"db_table_name": cell_decorator_db_table_name,
	"db_column_name": cell_decorator_db_column_name,
	"action": cell_decorator_action,
	"action_pid": cell_decorator_action_pid,
	"action_status": cell_decorator_action_status,
	"action_end": cell_decorator_action_end,
	"action_log": cell_decorator_action_log,
	"action_cron": cell_decorator_action_cron,
	"rset_md5": cell_decorator_rset_md5,
	"status_run_status": cell_decorator_status_run_status,
	"status_run_log": cell_decorator_status_run_log,
	"log_run_status": cell_decorator_log_run_status,
	"log_run_log": cell_decorator_log_run_log,
	"form_id": cell_decorator_form_id,
	"action_q_status": cell_decorator_action_q_status,
	"action_q_ret": cell_decorator_action_q_ret,
	"svcname": cell_decorator_svcname,
	"user_id": cell_decorator_user_id,
	"username": cell_decorator_username,
	"groups": cell_decorator_groups,
	"safe_file": cell_decorator_safe_file,
	"nodename": cell_decorator_nodename,
	"nodename_no_os": cell_decorator_nodename_no_os,
	"svc_action_err": cell_decorator_svc_action_err,
	"docker_tag_digest": cell_decorator_docker_tag_digest,
	"availstatus": cell_decorator_availstatus,
	"overallstatus": cell_decorator_overallstatus,
	"chk_type": cell_decorator_chk_type,
	"svcmon_links": cell_decorator_svcmon_links,
	"svc_ha": cell_decorator_svc_ha,
	"env": cell_decorator_env,
	"dash_severity": cell_decorator_dash_severity,
	"dash_links": cell_decorator_dash_links,
	"report_name": cell_decorator_report_name,
	"chart_name": cell_decorator_chart_name,
	"metric_name": cell_decorator_metric_name,
	"dns_records_type": cell_decorator_dns_records_type,
	"tag_exclude": cell_decorator_tag_exclude,
	"docker_repository": cell_decorator_docker_repository,
	"docker_registry": cell_decorator_docker_registry,
	"form_name": cell_decorator_form_name,
	"quota": cell_decorator_quota,
	"dns_record": cell_decorator_dns_record,
	"dns_domain": cell_decorator_dns_domain,
	"_network": cell_decorator_network,
	"boolean": cell_decorator_boolean,
	"status": cell_decorator_status,
	"users_role": cell_decorator_users_role,
	"alert_type": cell_decorator_alert_type,
	"resinfo_key": cell_decorator_resinfo_key,
	"resinfo_value": cell_decorator_resinfo_value,
	"log_icons": cell_decorator_log_icons,
	"var_class": cell_decorator_var_class,
	"var_name": cell_decorator_var_name,
	"app": cell_decorator_app,
	"obs_type": cell_decorator_obs_type,
	"obs_count": cell_decorator_obs_count,
	"uid": cell_decorator_uid,
	"gid": cell_decorator_gid,
	"tpl_definition": cell_decorator_tpl_definition,
	"prov_template": cell_decorator_prov_template,
	"fset_name": cell_decorator_fset_name,
	"disks_charts": cell_decorator_disks_charts,
	"saves_charts": cell_decorator_saves_charts,
	"comp_log": cell_decorator_comp_log,
	"comp_mod_log": cell_decorator_comp_mod_log,
	"comp_node_log": cell_decorator_comp_node_log,
	"comp_svc_log": cell_decorator_comp_svc_log,
	"modset_name": cell_decorator_modset_name,
	"log_level": cell_decorator_log_level,
	"log_event": cell_decorator_log_event,
	"res_log": cell_decorator_res_log,
	"ruleset_name": cell_decorator_ruleset_name,
	"rule_value": cell_decorator_rule_value
})


