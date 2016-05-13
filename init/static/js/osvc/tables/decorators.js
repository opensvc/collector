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
  'pushstats': 'spark16',
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

function cell_decorator_log_icons(e) {
  var line = $(e).parent(".tl")
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
  $(e).html(span)
}

function cell_decorator_boolean(e) {
  var v = $.data(e, "v")
  true_vals = [1, "1", "T", "True", "true", true]
  if (typeof v === "undefined") {
    var cl = ""
  } else if (true_vals.indexOf(v) >= 0) {
    var cl = "fa toggle-on"
  } else {
    var cl = "fa toggle-off"
  }
  s = $("<span class='"+cl+"' title='"+v+"'></span>").tooltipster()
  $(e).html(s)
}

function cell_decorator_pct(e) {
  var v = $.data(e, "v")
  d = _cell_decorator_pct(v)
  $(e).html(d)
}

function _cell_decorator_pct(v) {
  var dl = $("<div><div>")
  var dr = $("<div><div>")
  var dp = $("<div><div>")
  var d = $("<div><div>")
  dl.css({
    "font-size": "0px",
    "line-height": "0px",
    "height": "4px",
    "min-width": "0%",
    "max-width": v+"%",
    "width": v+"%",
    "background": "#A6FF80"
  })
  dr.css({
    "text-align": "left",
    "margin": "2px auto",
    "background": "#FF7863",
    "overflow": "hidden"
  })
  dp.css({
    "margin": "auto",
    "text-align": "center",
    "width": "100%"
  })
  dp.text(v+"%")
  dr.append(dl)
  d.append([dr, dp])
  return d
}

function cell_decorator_app(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extraline(e)
    app_tabs(id, {"app_name": v})
  })
}

function cell_decorator_dns_domain(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var domain_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    dns_domain_tabs(id, {"domain_id": domain_id, "domain_name": v})
  })
}

function cell_decorator_dns_record(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var record_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    dns_record_tabs(id, {"record_id": record_id, "record_name": v})
  })
}

function cell_decorator_disk_array_dg(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var array_name = $.data(line.children("[col=array_name],[col=disk_arrayid]")[0], "v")
    var id = toggle_extraline(e)
    diskgroup_tabs(id, {"array_name": array_name, "dg_name": v})
  })
}

function cell_decorator_disk_array(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extraline(e)
    array_tabs(id, {"array_name": v})
  })
}

function cell_decorator_quota(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var quota_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    quota_tabs(id, {"quota_id": quota_id})
  })
}

function cell_decorator_prov_template(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var tpl_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    prov_template_tabs(id, {"tpl_id": tpl_id, "tpl_name": v})
  })
}

function cell_decorator_fset_name(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    return
  }
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extraline(e)
    filterset_tabs(id, {"fset_name": v})
  })
}

function cell_decorator_modset_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extraline(e)
    moduleset_tabs(id, {"modset_name": v})
  })
}

function cell_decorator_ruleset_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extraline(e)
    ruleset_tabs(id, {"ruleset_name": v})
  })
}

function cell_decorator_report_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var report_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    report_tabs(id, {"report_id": report_id, "report_name": v})
  })
}

function cell_decorator_chart_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var chart_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    chart_tabs(id, {"chart_id": chart_id, "chart_name": v})
  })
}

function cell_decorator_metric_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var metric_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    metric_tabs(id, {"metric_id": metric_id, "metric_name": v})
  })
}

function cell_decorator_form_name(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var form_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    form_tabs(id, {"form_id": form_id, "form_name": v})
  })
}

function cell_decorator_network(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var net_id = $.data(line.children("[col=id]")[0], "v")
    var id = toggle_extraline(e)
    network_tabs(id, {"network_id": net_id})
  })
}

function cell_decorator_chk_instance(e) {
  var v = $.data(e, "v")
  var line = $(e).parent(".tl")
  var chk_type = $.data(line.children("[col=chk_type]")[0], "v")
  if (chk_type == "mpath") {
    var disk_id = $.data(line.children("[col=chk_instance]")[0], "v")
    s = "<div class='icon check16 clickable'></div>"
    $(e).html(s)
    $(e).addClass("corner")
    $(e).click(function(){
      var id = toggle_extratable(e)
      var req = {}
      req[id+"_f_disk_id"] = disk_id
      table_disks(id, {"id": id, "request_vars": req, "volatile_filters": true})
    })
    s = "<a class='icon hd16 nowrap'>"+v+"</a>"
    $(e).html(s)
  }
}

function cell_decorator_chk_high(e) {
  var high = $.data(e, "v")
  var line = $(e).parent(".tl")
  var v = $.data(line.children("[col=chk_value]")[0], "v")
  var cl = []
  v = parseInt(v)
  high = parseInt(high)
  if (v > high) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+high+"</span>")
}

function cell_decorator_chk_low(e) {
  var low = $.data(e, "v")
  var line = $(e).parent(".tl")
  var v = $.data(line.children("[col=chk_value]")[0], "v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  if (v < low) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+low+"</span>")
}

function cell_decorator_chk_value(e) {
  var v = $.data(e, "v")
  var line = $(e).parent(".tl")
  var low = $.data(line.children("[col=chk_low]")[0], "v")
  var high = $.data(line.children("[col=chk_high]")[0], "v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  high = parseInt(high)
  if ((v > high) || (v < low)) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+v+"</span>")
}

function cell_decorator_action_pid(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  var s = "<a>"+v+"</a>"
  $(e).html(s)
  $(e).bind('click', function(){
    var line = $(e).parent(".tl")
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

function ackpanel(e, show, s){
    var panel = $("#ackpanel")
    if (panel.length == 0) {
      panel = $("<div id='ackpanel' class='ackpanel'></div>")
      $("#layout").append(panel)
    }
    var pos = get_pos(e)
    if (show) {
        panel.css({"left": pos[0] + "px", "top": pos[1] + "px"});
        panel.show();
    } else {
        panel.hide();
    }
    panel.html(s)
}

function cell_decorator_action_status(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    $(e).html("<div class='icon spinner'></div>")
    return
  }
  cl = ["status_"+v.replace(' ', '_')]
  var line = $(e).parent(".tl")
  var ack = $.data(line.children("[col=ack]")[0], "v")
  if (ack == 1) {
    cl.push("ack_1")
  }
  s = "<div class='"+cl.join(" ")+"'>"+v+"</diV>"
  $(e).html(s)
  if (ack != 1) {
    return
  }
  $(e).bind("mouseout", function(){
    ackpanel(event, false, "")
  })
  $(e).bind("mouseover", function(){
    var acked_date = $.data(line.children("[col=acked_date]")[0], "v")
    var acked_by = $.data(line.children("[col=acked_by]")[0], "v")
    var acked_comment = $.data(line.children("[col=acked_comment]")[0], "v")
    s = "<div>"
    s += "<b>acked by </b>"+acked_by+"<br>"
    s += "<b> on </b>"+acked_date+"<br>"
    s += "<b>with comment:</b><br>"+acked_comment
    s += "</div>"
    ackpanel(event, true, s)
  })
}

function cell_decorator_action_end(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    $(e).empty()
    return
  } else if (v == "1000-01-01 00:00:00") {
    $(e).html("<span class='highlight'>timed out</span>")
    return
  }
  var line = $(e).parent(".tl")
  var id = $.data(line.children("[col=id]")[0], "v")
  s = "<span class='highlight nowrap' id='spin_span_end_"+id+"'>"+v+"</span>"
}

function cell_decorator_action_log(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  s = "<pre>"+v+"</pre>"
  $(e).html(s)
}

function cell_decorator_db_table_name(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    return
  }
  var s = $("<span class='nowrap'>"+v+"</span>")
  if (v in db_tables) {
    s.text(db_tables[v].title)
    s.addClass("icon "+db_tables[v].cl)
  }
  $(e).html(s)
}

function cell_decorator_db_column_name(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    return
  }
  var s = $("<span class='nowrap'>"+v+"</span>")
  if (v in colprops) {
    s.text(colprops[v].title)
    s.addClass("icon "+colprops[v].img)
  }
  $(e).html(s)
}

function cell_decorator_action(e) {
  var v = $.data(e, "v")
  var line = $(e).parent(".tl")
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
  $(e).html(s)
}

function cell_decorator_svc_action_err(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  s = $("<a class='icon action16 icon-red clickable'>"+v+"</a>")
  s.click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
    var id = toggle_extratable(e)
    table_actions(id, {
	"volatile_filters": true,
	"request_vars": {
		"actions_f_svc_id": svc_id,
		"actions_f_status": "err",
		"actions_f_ack": "!1|empty",
		"actions_f_begin": ">-300d"
	}
    })
  })
  $(e).html(s)
}

function cell_decorator_nodename(e) {
  _cell_decorator_nodename(e, true)
}

function cell_decorator_nodename_no_os(e) {
  _cell_decorator_nodename(e, false)
}

function cell_decorator_obs_type(e) {
  var v = $.data(e, "v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  div = $("<div class='nowrap'>"+v+"</div>")
  $(e).append(div)
  if (v == "os") {
      div.addClass("icon os16")
  } else if (v == "hw") {
      div.addClass("icon hw16")
  }
}

function _cell_decorator_nodename(e, os_icon) {
  var v = $.data(e, "v")
  var line = $(e).parent(".tl")
  var node_id = $.data(line.children("[col=node_id]")[0], "v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div class='a nowrap trunc20'>"+v+"</div>")
  $(e).addClass("corner")
  div = $(":first-child", e)
  if (os_icon) {
    try {
      os_cell = $(e).parent().children(".os_name")[0]
      os_c = os_class_h[$.data(os_cell, "v").toLowerCase()]
      div.addClass(os_c)
    } catch(e) {}
  }
  try {
    svc_autostart_cell = $(e).parent().children(".svc_autostart")[0]
    if ($.data(svc_autostart_cell, "v") == v) {
      div.addClass("b")
    }
  } catch(e) {}
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    node_tabs(id, {"nodename": v, "node_id": node_id})
  })
}

function cell_decorator_groups(e) {
  var v = $.data(e, "v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).addClass("corner")
  l = v.split(', ')
  s = ""
  for (i=0; i<l.length; i++) {
    g = l[i]
    s += "<span>"+g+"</span>"
  }
  $(e).html(s)
  $(e).children().each(function(){
    $(this).click(function(){
      if (get_selected() != "") {return}
      g = $(this).text()
      var id = toggle_extraline(e)
      group_tabs(id, {"group_name": g})
    })
  })
}

function cell_decorator_user_id(e) {
  var v = $.data(e, "v")
  if ((v=="") || (v=="empty")) {
    return
  }
  var line = $(e).parent(".tl")
  var fullname = $.data(line.children("[col=fullname]")[0], "v")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    user_tabs(id, {"user_id": v, "fullname": fullname})
  })
}

function cell_decorator_username(e) {
  var v = $.data(e, "v")
  if ((v=="") || (v=="empty")) {
    return
  }
  var line = $(e).parent(".tl")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    user_tabs(id, {"fullname": v})
  })
}

function cell_decorator_safe_file(e) {
  var uuid = $.data(e, "v")
  if ((uuid=="") || (uuid=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div class='a nowrap trunc20'>"+uuid+"</div>")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    safe_file_tabs(id, {"uuid": uuid})
  })
}

function cell_decorator_svcname(e) {
  var v = $.data(e, "v")
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
  if ((svc_id=="") || (svc_id=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div class='a nowrap trunc20'>"+v+"</div>")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    service_tabs(id, {"svc_id": svc_id})
  })
}

function cell_decorator_log_event(e) {
  var line = $(e).parent(".tl")
  var d = $.data(line.children("[col=log_dict]")[0], "v")
  var fmt = $.data(line.children("[col=log_fmt]")[0], "v")
  if (!d || d.length==0) {
    $(e).html(fmt)
    return
  }
  try {
    d = $.parseJSON(d)
  } catch(err) {
    $(e).html(i18n.t("decorators.corrupted_log"))
    return
  }
  for (key in d) {
    var re = RegExp("%\\("+key+"\\)[sd]", "g")
    fmt = fmt.replace(re, "<b>"+d[key]+"</b>")
  }
  $(e).html(fmt)
}

function cell_decorator_log_level(e) {
  var v = $.data(e, "v")
  t = {
    "warning": "boxed_small bgorange",
    "info": "boxed_small bggreen",
    "error": "boxed_small bgred",
  }
  if (v in t) {
    var cl = t[v]
  } else {
    var cl = "boxed_small bgblack"
  }
  $(e).html("<div class='"+cl+"'>"+v+"</div>")
}

function cell_decorator_status(e) {
  var v = $.data(e, "v")
  if ((v=="") || (v=="empty")) {
    v = "undef"
  }
  var c = v
  var line = $(e).parent(".tl")
  if (status_outdated(line)) {
    c = "undef"
  }
  t = {
    "warn": "orange",
    "up": "green",
    "stdby up": "green",
    "down": "red",
    "stdby down": "red",
    "undef": "gray",
    "n/a": "gray"
  }
  $(e).html("<div class='icon status_icon nowrap icon-"+t[c]+"'>"+v+"</div>")
}

function cell_decorator_dns_records_type(e) {
  var v = $.data(e, "v")
  var cl = ["boxed_small"]
  if ((v == "A") || (v == "PTR")) {
    cl.push("bgblack")
  } else if (v == "CNAME") {
    cl.push("bggreen")
  } else {
    cl.push("bgred")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_svcmon_link_frozen(e) {
  var line = $(e).parent(".tl")
  var mon_frozen = $.data(line.children("[col=mon_frozen]")[0], "v")
  if (mon_frozen == "1") {
    var s = $("<span class='icon frozen16'>&nbsp</span>")
  } else {
    var s = null
  }
  return s
}

function cell_decorator_svcmon_links(e) {
  $(e).html(
    cell_decorator_svcmon_link_frozen(e)
  )
}

function cell_decorator_comp_log(e) {
  var line = $(e).parent(".tl")
  var module = $.data(line.find("[col=run_module]")[0], "v")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  var node_id = $.data(line.find("[col=node_id]")[0], "v")
  $(e).empty()
  $(e).append("<div class='icon spark16'></div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extraline(e)
    comp_log(id, {"module": module, "svc_id": svc_id, "node_id": node_id})
  })
}

function cell_decorator_comp_mod_log(e) {
  var line = $(e).parent(".tl")
  var modname = $.data(line.find("[col=mod_name]")[0], "v")
  $(e).empty()
  $(e).append("<div class='icon spark16'></div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/compliance/ajax_mod_history?modname="+modname+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_comp_node_log(e) {
  var line = $(e).parent(".tl")
  var node_id = $.data(line.find("[col=node_id]")[0], "v")
  $(e).empty()
  $(e).append("<div class='icon spark16'></div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/compliance/ajax_node_history?node_id="+node_id+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_comp_svc_log(e) {
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  $(e).empty()
  $(e).append("<div class='icon spark16'></div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/compliance/ajax_svc_history?svc_id="+svc_id+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_uid(e) {
  var v = $.data(e, "v")
  if (v=="") {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = services_get_url() + "/init/nodes/ajax_uid_dispatch?user_id="+v
    toggle_extra(url, null, e, 0)
  })
}

function cell_decorator_gid(e) {
  var v = $.data(e, "v")
  if (v=="") {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = services_get_url() + "/init/nodes/ajax_gid_dispatch?group_id="+v
    toggle_extra(url, null, e, 0)
  })
}

function cell_decorator_chk_type(e) {
  var v = $.data(e, "v")
  if (v=="") {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = services_get_url() + "/init/checks/ajax_chk_type_defaults/"+v
    toggle_extra(url, null, e, 0)
  })
}

function cell_decorator_dash_link_comp_tab(e) {
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  var node_id = $.data(line.find("[col=node_id]")[0], "v")
  s = "<div class='icon comp16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (svc_id != "") {
    $(e).click(function(){
      var id = toggle_extraline(e)
      service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.compliance"})
    })
  } else if (node_id != "") {
    $(e).click(function(){
      var id = toggle_extraline(e)
      node_tabs(id, {"node_id": node_id, "tab": "node_tabs.compliance"})
    })
  }
}

function cell_decorator_dash_link_pkg_tab(e) {
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  s = "<div class='icon pkg16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (svc_id != "") {
    $(e).click(function(){
      var id = toggle_extraline(e)
      service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.pkgdiff"})
    })
  }
}

function cell_decorator_dash_link_feed_queue(e) {
  s = "<a class='icon action16' href=''></a>"
  $(e).html(s)
}

function _cell_decorator_dash_link_actions(svc_id, e) {
  s = $("<a class='icon action16 clickable'></a>")
  s.click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extratable(e)
    table_actions(id, {
	"volatile_filters": true,
	"request_vars": {
		"actions_f_svc_id": svc_id,
		"actions_f_begin": ">-7d"
	}
    })
  })
  return s
}

function cell_decorator_obs_count(e) {
  var v = $.data(e, "v")
  $(e).addClass("corner")
  s = $("<a class='icon node16 clickable'>"+v+"</a>")
  $(e).empty().append(s)
  s.click(function(){
    if (get_selected() != "") {return}
    var line = $(this).parents(".tl").first()
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
  s.click(function(){
    if (get_selected() != "") {return}
    var id = toggle_extratable(e)
    table_actions(id, {
	"volatile_filters": true,
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

function cell_decorator_dash_link_action_error(e) {
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  $(e).append(_cell_decorator_dash_link_action_error(svc_id, e))
  $(e).append(_cell_decorator_dash_link_actions(svc_id, e))
}

function cell_decorator_dash_link_svcmon(e) {
  var line = $(e).parent(".tl")
  var svc_id = $.data(line.find("[col=svc_id]")[0], "v")
  s = "<div class='icon svc clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (svc_id != "") {
    $(e).click(function(){
      var id = toggle_extraline(e)
      service_tabs(id, {"svc_id": svc_id, "tab": "service_tabs.status"})
    })
  }
}

function cell_decorator_dash_link_node(e) {
  var line = $(e).parent(".tl")
  var node_id = $.data(line.find("[col=node_id]")[0], "v")
  s = "<div class='icon node16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (node_id != "") {
    $(e).click(function(){
      var id = toggle_extraline(e)
      node_tabs(id, {"node_id": node_id, "tab": "node_tabs.properties"})
    })
  }
}

function cell_decorator_dash_link_checks(e) {
  var line = $(e).parent(".tl")
  var node_id = $.data(line.find("[col=node_id]")[0], "v")
  s = "<div class='icon check16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (node_id != "") {
    $(e).click(function(){
      var id = toggle_extratable(e)
      var req = {}
      req[id+"_f_node_id"] = node_id
      req[id+"_f_chk_err"] = ">0"
      table_checks(id, {"id": id, "request_vars": req, "volatile_filters": true})
    })
  }
}

function _cell_decorator_dash_link_mac_networks(mac) {
  url = services_get_url() + "/init/nodenetworks/nodenetworks?nodenetworks_f_mac="+mac+"&volatile_filters=true"
  s = "<a class='icon net16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_mac_duplicate(e) {
  var line = $(e).parent(".tl")
  try {
    var mac = $.parseJSON($.data(line.find("[col=dash_dict]")[0], "v")).mac
  } catch(err) {
    console.log(err)
    return
  }
  var s = ""
  s += _cell_decorator_dash_link_mac_networks(mac)
  $(e).html(s)
}

function cell_decorator_dash_link_obsolescence(e, t) {
  $(e).empty().addClass("corner")
  s = $("<a class='icon obs16 clickable'></a>")
  s.click(function(){
    if (get_selected() != "") {return}
    var line = $(this).parents(".tl").first()
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
  $(e).append(s)
}

function cell_decorator_dash_links(e) {
  var line = $(e).parent(".tl")
  var dash_type = $.data(line.find("[col=dash_type]")[0], "v")
  if (dash_type == "action errors") {
    cell_decorator_dash_link_action_error(e)
  } else if ((dash_type == "node warranty expired") ||
             (dash_type == "node without warranty end date") ||
             (dash_type == "node without asset information") ||
             (dash_type == "node close to warranty end") ||
             (dash_type == "node information not updated")) {
    cell_decorator_dash_link_node(e)
  } else if ((dash_type == "check out of bounds") ||
             (dash_type == "check value not updated")) {
    cell_decorator_dash_link_checks(e)
  } else if (dash_type == "mac duplicate") {
    cell_decorator_dash_link_mac_duplicate(e)
  } else if ((dash_type == "service available but degraded") ||
             (dash_type == "service status not updated") ||
             (dash_type == "service configuration not updated") ||
             (dash_type == "service frozen") ||
             (dash_type == "flex error") ||
             (dash_type == "service unavailable")) {
    cell_decorator_dash_link_svcmon(e)
  } else if (dash_type == "feed queue") {
    cell_decorator_dash_link_feed_queue(e)
  } else if (dash_type.indexOf("os obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "os")
  } else if (dash_type.indexOf("obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "hw")
  } else if (dash_type.indexOf("comp") == 0) {
    cell_decorator_dash_link_comp_tab(e)
  } else if (dash_type.indexOf("package") == 0) {
    cell_decorator_dash_link_pkg_tab(e)
  }
}

function cell_decorator_action_cron(e) {
  var v = $.data(e, "v")
  var l = []
  if (v == 1) {
      l.push("time16")
  }
  $(e).html("<div class='"+l.join(" ")+"'></div>")
}

function cell_decorator_dash_severity(e) {
  var v = $.data(e, "v")
  var l = []
  if (v == 0) {
      l.push("alertgreen")
  } else if (v == 1) {
      l.push("alertorange")
  } else if (v == 2) {
      l.push("alertred")
  } else if (v == 3) {
      l.push("alertdarkred")
  } else {
      l.push("alertblack")
  }
  var content = $("<div class='icon "+l.join(" ")+"' title='"+v+"'></div>").tooltipster()
  $(e).html(content)
}

function cell_decorator_form_id(e) {
  var v = $.data(e, "v")
  $(e).html("<span class='icon wf16 nowrap clickable'>"+v+"</span>")
  $(e).addClass("corner")
  $(e).click(function(){
    var id = toggle_extratable(e)
    workflow(id, {"form_id": v})
  })
}

function cell_decorator_run_log(e) {
  var v = $.data(e, "v")
  if (typeof v === "undefined") {
    var s = ""
  } else {
    var s = "<pre>"+v.replace(/ERR:/g, "<span class='err'>ERR:</span>")+"</pre>"
  }
  $(e).html(s)
}

function cell_decorator_run_status(e) {
  var v = $.data(e, "v")
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
  $(e).html("<div class='icon "+cl+"'>"+_v+"</div>")
}

function cell_decorator_tag_exclude(e) {
  var v = $.data(e, "v")
  if (v == "empty") {
    v = ""
  }
  $(e).html(v)
  $(window).bind("click", function() {
    $("input.tag_exclude").parent().html(v)
  })
  if (services_ismemberof(["Manager", "TagManager"])) {
    $(e).bind("click", function(event){
      event.stopPropagation()
      i = $("<input class='oi tag_exclude'></input>")
      var _v = $.data(this, "v")
      if (_v == "empty") {
        _v = ""
      }
      i.val(_v)
      i.bind("keyup", function(event){
        if (!is_enter(event)) {
          return
        }
        var tag_id = $.data($(this).parents(".tl").find("[col=id]")[0], "v")
        var data = {
          "tag_exclude": $(this).val(),
        }
        var _i = $(this)
        services_osvcpostrest("R_TAG", [tag_id], "", data, function(jd) {
          if (jd.error && (jd.error.length > 0)) {
            $(".flash").show("blind").html(services_error_fmt(jd))
            return
          }
          _i.parent().html(data.tag_exclude)
        },
        function(xhr, stat, error) {
          $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
        })
      })
      $(e).empty().append(i)
      i.focus()
    })
  }
}

function cell_decorator_dash_entry(e) {
  var line = $(e).parent(".tl")
  var d = $.data(line.children("[col=dash_dict]")[0], "v")
  var fmt = $.data(line.children("[col=dash_fmt]")[0], "v")
  if (!d || d.length==0) {
    $(e).html(fmt)
    return
  }
  try {
    d = $.parseJSON(d)
  } catch(err) {
    $(e).html(i18n.t("decorators.corrupted_log"))
    return
  }
  for (key in d) {
    var re = RegExp("%\\("+key+"\\)[sd]", "g")
    fmt = fmt.replace(re, "<b>"+d[key]+"</b>")
  }
  $(e).html(fmt)
  $(e).addClass("clickable corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    var node_id = $.data(line.children("[col=node_id]")[0], "v")
    var svc_id = $.data(line.children("[col=svc_id]")[0], "v")
    var dash_md5 = $.data(line.children("[col=dash_md5]")[0], "v")
    var dash_created = $.data(line.children("[col=dash_created]")[0], "v")
    var rowid = line.attr("cksum")
    url = services_get_url() + "/init/dashboard/ajax_alert_events?node_id="+node_id+"&svc_id="+svc_id+"&dash_md5="+dash_md5+"&dash_created="+dash_created+"&rowid="+rowid
    toggle_extra(url, null, this, 0)
  })
}

function cell_decorator_rset_md5(e) {
  var v = $.data(e, "v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = services_get_url() + "/init/compliance/ajax_rset_md5?rset_md5="+v
    toggle_extra(url, null, this, 0)
  })
}

function cell_decorator_action_q_ret(e) {
  var v = $.data(e, "v")
  var cl = ["boxed_small"]
  if (v == 0) {
    cl.push("bggreen")
  } else {
    cl.push("bgred")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_action_q_status(e) {
  var v = $.data(e, "v")
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
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+st+"</div>"
  $(e).html(s)
}

function datetime_age(s) {
  // return age in minutes
  if (typeof s === 'undefined') {
    return
  }
  if (!s || (s == 'empty')) {
    return
  }
  var d = moment.tz(s, osvc.server_timezone)
  var now = moment()
  var delta = (now -d)/60000
  return delta
}

function _outdated(s, max_age) {
  delta = datetime_age(s)
  if (!delta) {
    return true
  }
  if (delta > max_age) {
    return true
  }
  return false
}

function status_outdated(line) {
  var l = line.children("[cell=1][col=mon_updated]")
  if (l.length == 0) {
    l = line.children("[cell=1][col=svc_status_updated]")
  }
  if (l.length == 0) {
    l = line.children("[cell=1][col=status_updated]")
  }
  if (l.length == 0) {
    l = line.children("[cell=1][col$=updated]")
  }
  if (l.length == 0) {
    return true
  }
  var s = $.data(l[0], "v")
  return _outdated(s, 15)
}

function cell_decorator_date_no_age(e) {
  v = $.data(e, "v")
  if (typeof v === 'undefined') {
    return
  }
  s = v.split(" ")[0]
  $(e).html(s)
}

function cell_decorator_datetime_no_age(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_date_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_status(e) {
  $(e).attr("max_age", 15)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_daily(e) {
  $(e).attr("max_age", 1440)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_weekly(e) {
  $(e).attr("max_age", 10080)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime(e) {
  var s = $.data(e, "v")
  var max_age = $(e).attr("max_age")
  var delta = datetime_age(s)

  if (!delta) {
    $(e).html()
    return
  }
  var content = delta_format(delta, s, max_age)
  if ($(e).text() == content.text()) {
    return
  }
  $(e).html(content)
}

function delta_format(delta, s, max_age) {
  if (delta > 0) {
    var prefix = "-"
    var round = Math.ceil
  } else {
    var prefix = ""
    delta = -delta
    var round = Math.floor
  }

  var hour = 60
  var day = 1440
  var week = 10080
  var month = 43200
  var year = 524520

  if (delta < hour) {
    var cl = "minute icon"
    var text = prefix + i18n.t("table.minute", {"count": round(delta)})
    var color = "#000000"
  } else if (delta < day) {
    var cl = "hour icon"
    var text = prefix + i18n.t("table.hour", {"count": round(delta/hour)})
    var color = "#181818"
  } else if (delta < week) {
    var cl = "day icon "
    var text = prefix + i18n.t("table.day", {"count": round(delta/day)})
    var color = "#333333"
  } else if (delta < month) {
    var cl = "week icon "
    var text = prefix + i18n.t("table.week", {"count": round(delta/week)})
    var color = "#333333"
  } else if (delta < year) {
    var cl = "month icon"
    var text = prefix + i18n.t("table.month", {"count": round(delta/month)})
    var color = "#484848"
  } else {
    var cl = "year icon"
    var text = prefix + i18n.t("table.year", {"count": round(delta/year)})
    var color = "#666666"
  }

  cl += " nowrap"

  if (max_age && (delta > max_age)) {
    cl += " icon-red"
  }

  if (!s) {
    s = ""
  }

  return $("<div class='"+cl+"' style='color:"+color+"' title='"+s+"'>"+text+"</div>").tooltipster()
}

function cell_decorator_date(e) {
  cell_decorator_datetime(e)
  s = $.data(e, "v")
  $(e).text(s.split(" ")[0])
}

function cell_decorator_env(e) {
  if ($.data(e, "v") != "PRD") {
    return
  }
  $(e).addClass("highlight")
}

function cell_decorator_svc_ha(e) {
  if ($.data(e, "v") != 1) {
    $(e).empty()
    return
  }
  s = "<div class='boxed_small'>HA</div>"
  $(e).html(s)
}

function cell_decorator_size_mb(e) {
  v = $.data(e, "v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_mb(v)+"</div>"
  $(e).html(s)
}

function cell_decorator_size_b(e) {
  v = $.data(e, "v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_b(v)+"</div>"
  $(e).html(s)
}

function cell_decorator_availstatus(e) {
  var line = $(e).parent(".tl")
  var mon_availstatus = $.data(e, "v")
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
  $(e).html(s)
}

function cell_decorator_rsetvars(e) {
  var s = $.data(e, "v")
  $(e).html("<pre>"+s.replace(/\|/g, "\n")+"</pre>")
}

function cell_decorator_overallstatus(e) {
  var line = $(e).parent(".tl")
  var mon_overallstatus = $.data(e, "v")
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
  $(e).html(s)
}

function cell_decorator_sql(e) {
  var s = $.data(e, "v")
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
  $(e).html(_e)
}

function cell_decorator_alert_type(e) {
  var s = $.data(e, "v")
  $(e).html(i18n.t("alert_type."+s))
}

function cell_decorator_tpl_command(e) {
  var s = $.data(e, "v")
  var _e = $("<pre></pre>")
  s = s.replace(/--provision/g, "<br><span class=syntax_blue>  --provision</span>")
  s = s.replace(/--resource/g, "<br><span class=syntax_blue>  --resource</span>")
  s = s.replace(/{/g, "{<br>      ")
  s = s.replace(/\",/g, "\",<br>     ")
  s = s.replace(/}/g, "<br>    }")
  s = s.replace(/(\(\w+\)s)/gi, function(x) {
    return '<span class=syntax_red>'+x+'</span>'
  })
  s = s.replace(/("\w+":)/gi, function(x) {
    return '<span class=syntax_green>'+x+'</span>'
  })
  _e.html(s)
  $(e).html(_e)
}

function cell_decorator_yaml(e) {
  var s = $.data(e, "v")
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
  $(e).html(_e)
}

function cell_decorator_resinfo_key(e) {
  var s = $.data(e, "v")
  var _e = $("<div class='boxed_small'></div>")
  _e.text(s)
  if (s == "Error") {
    _e.addClass("bgred")
  } else {
    _e.addClass("bgblack")
  }
  $(e).html(_e)
}

function cell_decorator_resinfo_value(e) {
  var s = $.data(e, "v")
  var _e = $("<span></span>")
  _e.text(s)
  if (is_numeric(s)) {
    _e.addClass("icon spark16")
    $(e).addClass("corner clickable")
    $(e).bind("click", function() {
      var line = $(e).parent(".tl")
      var span_id = line.attr("spansum")
      var table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
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
  $(e).html(_e)
}

function cell_decorator_saves_charts(e) {
  var v = $.data(e, "v")
  var data = $.parseJSON(v)
  $(e).empty()
  if (data.chart_svc.data && data.chart_svc.data[0].length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_svc'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.services"))
    plot_div.text(JSON.stringify(data.chart_svc))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_ap.data && data.chart_ap.data[0].length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_ap'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.apps"))
    plot_div.text(JSON.stringify(data.chart_ap))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_group.data && data.chart_group.data[0].length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_group'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.groups"))
    plot_div.text(JSON.stringify(data.chart_group))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_server.data && data.chart_server.data[0].length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_server'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.servers"))
    plot_div.text(JSON.stringify(data.chart_server))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  $(e).append("<div class='spacer'></div>")
  $(e).append("<div id='chart_info'>-</div>")
  plot_savedonuts()
}

function cell_decorator_disks_charts(e) {
  var v = $.data(e, "v")
  var data = $.parseJSON(v)
  $(e).empty()
  if (data.chart_svc.data && data.chart_svc.data.length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_svc'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.services"))
    plot_div.text(JSON.stringify(data.chart_svc))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_ap.data && data.chart_ap.data.length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_ap'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.apps"))
    plot_div.text(JSON.stringify(data.chart_ap))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_dg.data && data.chart_dg.data.length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_dg'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.diskgroups"))
    plot_div.text(JSON.stringify(data.chart_dg))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  if (data.chart_ar.data && data.chart_ar.data.length > 0) {
    var div = $("<div style='float:left;width:500px'></div>")
    var plot_div = $("<div id='chart_ar'></div>")
    var title = $("<h3></h3>")
    title.text(i18n.t("decorators.charts.arrays"))
    plot_div.text(JSON.stringify(data.chart_ar))
    div.append(title)
    div.append(plot_div)
    $(e).append(div)
  }
  $(e).append("<div class='spacer'></div>")
  $(e).append("<div id='chart_info'>-</div>")
  plot_diskdonuts()
}

function cell_decorator_users_role(e) {
  var s = $.data(e, "v")
  $(e).empty()
  if (s == 1) {
    $(e).addClass("admin")
  } else {
    $(e).addClass("guy16")
  }
}

function cell_decorator_rule_value(e) {
  var line = $(e).parent(".tl")
  $(e).uniqueId()
  var id = $(e).attr("id")
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
    var data = $.parseJSON($.data(e, "v"))
  } catch(err) {
    var data = $.data(e, "v")
  }
  form($(e), {
    "data": data,
    "var_id": var_id,
    "rset_id": rset_id,
    "display_mode": true,
    "digest": true,
    "form_name": var_class,
    "disable_edit": disable_edit
  })
}

cell_decorators = {
 "yaml": cell_decorator_yaml,
 "sql": cell_decorator_sql,
 "rsetvars": cell_decorator_rsetvars,
 "dash_entry": cell_decorator_dash_entry,
 "disk_array_dg": cell_decorator_disk_array_dg,
 "disk_array": cell_decorator_disk_array,
 "size_mb": cell_decorator_size_mb,
 "size_b": cell_decorator_size_b,
 "chk_instance": cell_decorator_chk_instance,
 "chk_value": cell_decorator_chk_value,
 "chk_low": cell_decorator_chk_low,
 "chk_high": cell_decorator_chk_high,
 "db_table_name": cell_decorator_db_table_name,
 "db_column_name": cell_decorator_db_column_name,
 "action": cell_decorator_action,
 "action_pid": cell_decorator_action_pid,
 "action_status": cell_decorator_action_status,
 "action_end": cell_decorator_action_end,
 "action_log": cell_decorator_action_log,
 "action_cron": cell_decorator_action_cron,
 "rset_md5": cell_decorator_rset_md5,
 "run_status": cell_decorator_run_status,
 "run_log": cell_decorator_run_log,
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
 "availstatus": cell_decorator_availstatus,
 "overallstatus": cell_decorator_overallstatus,
 "chk_type": cell_decorator_chk_type,
 "svcmon_links": cell_decorator_svcmon_links,
 "svc_ha": cell_decorator_svc_ha,
 "env": cell_decorator_env,
 "date_future": cell_decorator_date_future,
 "datetime_future": cell_decorator_datetime_future,
 "datetime_weekly": cell_decorator_datetime_weekly,
 "datetime_daily": cell_decorator_datetime_daily,
 "datetime_status": cell_decorator_datetime_status,
 "datetime_no_age": cell_decorator_datetime_no_age,
 "date_no_age": cell_decorator_date_no_age,
 "dash_severity": cell_decorator_dash_severity,
 "dash_links": cell_decorator_dash_links,
 "report_name": cell_decorator_report_name,
 "chart_name": cell_decorator_chart_name,
 "metric_name": cell_decorator_metric_name,
 "dns_records_type": cell_decorator_dns_records_type,
 "tag_exclude": cell_decorator_tag_exclude,
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
 "app": cell_decorator_app,
 "obs_type": cell_decorator_obs_type,
 "obs_count": cell_decorator_obs_count,
 "uid": cell_decorator_uid,
 "gid": cell_decorator_gid,
 "pct": cell_decorator_pct,
 "tpl_command": cell_decorator_tpl_command,
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
 "ruleset_name": cell_decorator_ruleset_name,
 "rule_value": cell_decorator_rule_value
}


