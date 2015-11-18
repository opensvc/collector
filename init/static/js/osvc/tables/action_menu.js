//
// install agent action menu entries definitions in the table object
//
function table_action_menu_init_data(t) {
   t.action_menu = {
    "nodes": [
      {'title': 'Update node information', 'class': 'icon node16', 'action': 'pushasset'},
      {'title': 'Update disks information', 'class': 'icon hd16', 'action': 'pushdisks'},
      {'title': 'Update app information', 'class': 'icon svc-c', 'action': 'push_appinfo'},
      {'title': 'Update services information', 'class': 'icon svc-c', 'action': 'pushservices'},
      {'title': 'Update installed packages information', 'class': 'icon pkg16', 'action': 'pushpkg'},
      {'title': 'Update installed patches information', 'class': 'icon pkg16', 'action': 'pushpatch'},
      {'title': 'Update stats', 'class': 'icon spark16', 'action': 'pushstats'},
      {'title': 'Update check values', 'class': 'icon ok', 'action': 'checks'},
      {'title': 'Update sysreport', 'class': 'icon log16', 'action': 'sysreport'},
      {'title': 'Update compliance modules', 'class': 'icon comp-c', 'action': 'updatecomp'},
      {'title': 'Update opensvc agent', 'class': 'icon pkg16', 'action': 'updatepkg'},
      {'title': 'Rotate root password', 'class': 'icon key', 'action': 'rotate root pw'},
      {'title': 'Rescan scsi hosts', 'class': 'icon hd16', 'action': 'scanscsi'},
      {'title': 'Reboot', 'class': 'icon action_restart_16', 'action': 'reboot'},
      {'title': 'Reboot schedule', 'class': 'icon action_restart_16', 'action': 'schedule_reboot'},
      {'title': 'Reboot unschedule', 'class': 'icon action_restart_16', 'action': 'unschedule_reboot'},
      {'title': 'Shutdown', 'class': 'icon action_stop_16', 'action': 'shutdown'},
      {'title': 'Wake On LAN', 'class': 'icon action_start_16', 'action': 'wol'},
      {'title': 'Compliance check', 'class': 'icon comp-c', 'action': 'compliance_check', 'params': ["module", "moduleset"]},
      {'title': 'Compliance fix', 'class': 'icon comp-c', 'action': 'compliance_fix', 'params': ["module", "moduleset"]}
    ],
    "services": [
      {'title': 'Start', 'class': 'icon action_start_16', 'action': 'start'},
      {'title': 'Stop', 'class': 'icon action_stop_16', 'action': 'stop'},
      {'title': 'Restart', 'class': 'icon action_restart_16', 'action': 'restart'},
      {'title': 'Switch', 'class': 'icon action_switch_16', 'action': 'switch'},
      {'title': 'Sync all remotes', 'class': 'icon action_sync_16', 'action': 'syncall'},
      {'title': 'Sync peer remotes', 'class': 'icon action_sync_16', 'action': 'syncnodes'},
      {'title': 'Sync disaster recovery remotes', 'class': 'icon action_sync_16', 'action': 'syncdrp'},
      {'title': 'Enable', 'class': 'icon ok', 'action': 'enable'},
      {'title': 'Disable', 'class': 'icon nok', 'action': 'disable'},
      {'title': 'Thaw', 'class': 'icon ok', 'action': 'thaw'},
      {'title': 'Freeze', 'class': 'icon nok', 'action': 'freeze'},
      {'title': 'Compliance check', 'class': 'icon comp-c', 'action': 'compliance_check', 'params': ["module", "moduleset"]},
      {'title': 'Compliance fix', 'class': 'icon comp-c', 'action': 'compliance_fix', 'params': ["module", "moduleset"]}
    ],
    "resources": [
      {'title': 'Start', 'class': 'icon action_start_16', 'action': 'start'},
      {'title': 'Stop', 'class': 'icon action_stop_16', 'action': 'stop'},
      {'title': 'Restart', 'class': 'icon action_restart_16', 'action': 'restart'},
      {'title': 'Enable', 'class': 'icon ok', 'action': 'enable'},
      {'title': 'Disable', 'class': 'icon nok', 'action': 'disable'}
    ],
    "modules": [
      {'title': 'Check', 'class': 'icon comp-c', 'action': 'check'},
      {'title': 'Fix', 'class': 'icon comp-c', 'action': 'fix'}
    ]
  }
}

//
// install handler for click events on the table checkbox column
// only function called at table init
//
function table_bind_action_menu(t) {
  table_action_menu_init_data(t)

  $("#table_"+t.id).find("[name="+t.id+"_tools]").each(function(){
    $(this).bind("mouseup", function(event) {
      if (event.button == 2) {
        // right-click => open the action menu
        table_action_menu(t, event)
      } else {
        // left-click => close the action menu, the menu and the filter box
        $("#fsr"+t.id).hide()
        $(".menu").hide("fold")
        $(".action_menu").hide()
      }
    })
  })
}

//
// format action submit result as a flash message
//
function table_action_menu_status(msg){
  var s = "accepted: "+msg.accepted+", rejected: "+msg.rejected
  if (msg.factorized>0) {
    s = "factorized: "+msg.factorized+", "+s
  }
  $(".flash").html(s).show("blind")
}

//
// animation to highlight a post in the action_q
//
function table_action_menu_click_animation(t) {
  var src = $("#am_"+t.id)
  var dest = $(".header").find("[href$=action_queue]")
  var destp = dest.position()
  src.animate({
   top: destp.top,
   left: destp.left,
   opacity: "toggle",
   height: ["toggle", "swing"],
   width: ["toggle", "swing"]
  }, 1500, function(){dest.parent().effect("highlight")})
}

//
// helper to populate the checkbox list of modulesets for compliance check/fix actions
//
function table_action_menu_param_moduleset(t) {
  var s = ""
  $.ajax({
    async: false,
    type: "POST",
    url: $(location).attr("origin") + "/init/compliance/call/json/comp_get_all_moduleset",
    data: "",
    success: function(data){
      for (var i=0; i<data.length; i++) {
        var e = data[i]
        s += "<div><input type=checkbox otype='moduleset' oid="+e[0]+" oname='"+e[1]+"'>"+e[1]+"</div>"
      }
    }
  })
  return "<p class='clickable b' onclick='$(this).next().toggle()'>--moduleset</p><div class='panselector10 hidden'>"+s+"</div>"
}

//
// helper to populate the checkbox list of modules for compliance check/fix actions
//
function table_action_menu_param_module(t) {
  var s = ""
  $.ajax({
    async: false,
    type: "POST",
    url: $(location).attr("origin") + "/init/compliance/call/json/comp_get_all_module",
    data: "",
    success: function(data){
      for (var i=0; i<data.length; i++) {
        var e = data[i]
        s += "<div><input type=checkbox otype='module' oid="+e[0]+" oname='"+e[1]+"'>"+e[1]+"</div>"
      }
    }
  })
  return "<p class='clickable b' onclick='$(this).next().toggle()'>--module</p><div class='panselector10 hidden'>"+s+"</div>"
}

//
// ask for a confirmation on first call, recurse once to do real stuff
// given a dataset, post each entry into the action_q
//
function table_action_menu_post_data(t, data, confirmation) {
    action = data[0]['action']
    if (!(confirmation==true)) {
      s = ""
      $("#am_"+t.id).find("li.right").remove()
      $("#am_"+t.id).find("li[action="+action+"]").each(function(){
        $(this).addClass("b")
        $(this).unbind("click")
        $(this).siblings().remove()
        $(this).parent("ul").parent().unbind("click")

        // action parameters
        var params = $(this).attr("params")
        if (typeof params !== "undefined") {
          params = params.split(",")
          for (var i=0; i<params.length; i++) {
            var param = params[i]
            try {
              s += t["action_menu_param_"+param]()
            } catch(err) {}
          }
        }
      })
      s += "<hr>"
      s += "<div>"+i18n.t("action_menu.confirmation")+"</div><br>"
      s += "<div class='check16 float clickable' name='yes'>"+i18n.t("action_menu.yes")+"</div>"
      s += "<div class='nok float clickable' name='no'>"+i18n.t("action_menu.no")+"</div>"
      $("#am_"+t.id).find("ul").last().append(s)
      $("#am_"+t.id).find("[name=yes]").bind("click", function(){
        $(this).unbind("click")
        $(this).removeClass("check16")
        $(this).addClass("spinner")
        table_action_menu_post_data(t, data, true)
      })
      $("#am_"+t.id).find("[name=no]").bind("click", function(){$("#am_"+t.id).remove()})
      return
    }
    var params = {}
    $("#am_"+t.id).find("input[otype]:checked").each(function(){
      otype = $(this).attr("otype")
      oname = $(this).attr("oname")
      if (!(otype in params)) {
        params[otype] = []
      }
      params[otype].push(oname)
    })
    for (otype in params) {
      if (params[otype].length > 0) {
        for (var i=0; i<data.length; i++) {
          data[i][otype] = params[otype].join(",")
        }
      }
    }
    table_action_menu_click_animation(t)
    $.ajax({
      //async: false,
      type: "POST",
      url: $(location).attr("origin") + "/init/action_menu/call/json/json_action",
      data: {"data": JSON.stringify(data)},
      success: function(msg){
        table_action_menu_status(msg)
      }
    })
}

//
// action menu formatter entry point
//
function table_action_menu(t, e){
  // drop the previous action menu
  $("#am_"+t.id).remove()

  if (typeof t.action_menu === "undefined") {
    return
  }
  $(".right_click_menu").hide()

  var s = ""

  // format the tools menu
  var tm = ""
  tm += table_tools_menu_nodes(t)
  tm += table_tools_menu_svcs(t)
  tm += tool_topo(t)
  if (tm != "") {
    s += "<h3 class='line'><span>"+i18n.t("action_menu.tools")+"</span></h3>"
    s += tm
  }

  // format the data action menu
  var dm = ""
  dm += table_data_action_menu_svc(t, e)
  dm += table_data_action_menu_svcs(t)
  dm += table_data_action_menu_svcs_all(t, e)
  if (dm != "") {
    s += "<h3 class='line'><span>"+i18n.t("action_menu.data_actions")+"</span></h3>"
    s += dm
  }

  // format the agent action menu
  var am = ""
  if ("nodes" in t.action_menu) {
    am += table_action_menu_node(t, e)
    am += table_action_menu_nodes(t)
    am += table_action_menu_nodes_all(t, e)
  }
  if ("services" in t.action_menu) {
    am += table_action_menu_svc(t, e)
    am += table_action_menu_svcs(t)
    am += table_action_menu_svcs_all(t, e)
  }
  if ("resources" in t.action_menu) {
    am += table_action_menu_resource(t, e)
    am += table_action_menu_resources(t)
    am += table_action_menu_resources_all(t, e)
  }
  if ("modules" in t.action_menu) {
    am += table_action_menu_module(t, e)
    am += table_action_menu_modules(t)
    am += table_action_menu_modules_all(t, e)
  }
  if (am != "") {
      s += "<h3 class='line'><span>"+i18n.t("action_menu.agent_actions")+"</span></h3>"
      s += am
  }

  if (s == "") {
    return
  }
  s = "<div id='am_"+t.id+"' class='white_float action_menu stackable'><ul>"+s+"</ul></div>"

  // position the popup at the mouse click
  var pos = get_pos(e)
  t.div.append(s)
  $("#am_"+t.id).css({"left": pos[0] + "px", "top": pos[1] + "px"})

  // bind action click triggers
  $("#am_"+t.id).find("[scope=module]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_module_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=modules]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_modules_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=modules_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_modules_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resource]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resource_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resources]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resources_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resources_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resources_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svc]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svc_instance_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svcs]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svcs_instances_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svcs_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svcs_instances_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=node]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_node_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=nodes]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_nodes_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=nodes_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_nodes_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })

  // display actions only for the clicked section
  var sections = $("#am_"+t.id).children("ul").children("li")
  sections.addClass("right")
  sections.children("ul").hide()
  sections.bind("click", function(){
    var v = $(this).children("ul").is(":visible")
    sections.removeClass("down")
    sections.addClass("right")
    sections.children("ul").hide()
    if (!v) {
      $(this).children("ul").show()
      $(this).removeClass("right")
      $(this).addClass("down")
    }
  })
}


//
// data selectors: node
//
function table_action_menu_get_nodes_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var nodenames = []
    lines.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodname],td[cell=1][name$=hostname]").each(function(){
      nodename = $(this).attr("v")
      var d = {'nodename': nodename, 'action': action}
      if (nodenames.indexOf(nodename) < 0) {
        nodenames.push(nodename)
        data.push({'nodename': nodename, 'action': action})
      }
    })
    return data
}

function table_action_menu_get_node_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'action': action}]
    return data
}

function table_action_menu_get_nodes_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var name = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var col = name.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = col
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idx = cols.indexOf(col)
           var sigs = []
           for (i=0; i<lines.length; i++) {
             var sig = lines[i]["cells"][idx]
             if (sigs.indexOf(sig) >= 0) { continue }
             sigs.push(sig)
             data.push({nodename: lines[i]["cells"][idx], action: action})
           }
         }
    })
    return data
}

//
// data selectors: service
//
function table_action_menu_get_svcs_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        return []
      }
      var i = svcname
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push({"svcname": svcname, "action": action})
      }
    })
    return data
}

function table_action_menu_get_svc_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return []
    }
    var data = [{'svcname': svcname, 'action': action}]
    return data
}

function table_action_menu_get_svcs_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var colsvc = svcname.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colsvc
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxsvc = cols.indexOf(colsvc)
           var sigs = []
           for (i=0; i<lines.length; i++) {
             var sig = lines[i]["cells"][idxsvc]
             if (sigs.indexOf(sig) >= 0) { continue }
             sigs.push(sig)
             data.push({svcname: lines[i]["cells"][idxsvc], action: action})
           }
         }
    })
    return data
}

//
// data selectors: service instances
//
function table_action_menu_get_svcs_instances_data_with_node(t, action) {
    var d = table_action_menu_get_svcs_instances_data(t, action)
    var n = []
    for (i=0; i<d.length; i++) {
        if (d[i]["nodename"] != "") {
            n.push(d[i])
        }
    }
    return n
}

function table_action_menu_get_svcs_instances_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        nodename = ""
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        return []
      }
      var i = nodename+"--"+svcname
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push({"nodename": nodename, "svcname": svcname, "action": action})
      }
    })
    return data
}

function table_action_menu_get_svc_instance_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'svcname': svcname, 'action': action}]
    return data
}

function table_action_menu_get_svcs_instances_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           var sigs = []
           for (i=0; i<lines.length; i++) {
             var sig = lines[i]["cells"][idxnode]+"--"+lines[i]["cells"][idxsvc]
             if (sigs.indexOf(sig) >= 0) { continue }
             sigs.push(sig)
             data.push({nodename: lines[i]["cells"][idxnode], svcname: lines[i]["cells"][idxsvc], action: action})
           }
         }
    })
    return data
}

//
// data selector: module
//
function table_action_menu_get_modules_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        return
      }
      var module = $(this).find("td[cell=1][name$=_run_module]").attr("v")
      if ((typeof module === "undefined")||(module=="")) {
        return
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        var i = nodename+"--"+svcname+"--"+module
        d = {"nodename": nodename, "module": module, "action": action}
      } else {
        var i = nodename+"--"+module
        d = {"nodename": nodename, "svcname": svcname, "module": module, "action": action}
      }
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push(d)
      }
    })
    return data
}

function table_action_menu_get_module_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var module = line.find("td[cell=1][name$=_run_module]").first().attr("v")
    if ((typeof module === "undefined")||(module=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'module': module, 'action': action}]
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return data
    }
    data[0]['svcname'] = svcname
    return data
}

function table_action_menu_get_modules_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var module = line.find("td[cell=1][name$=_run_module]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var colmodule = module.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc+","+colmodule
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           idxmodule = cols.indexOf(colmodule)
           for (i=0; i<lines.length; i++) {
             data.push({
               nodename: lines[i]["cells"][idxnode],
               svcname: lines[i]["cells"][idxsvc],
               module: lines[i]["cells"][idxmodule],
               action: action
             })
           }
         }
    })
    return data
}

//
// data selector: resource
//
function table_action_menu_get_resources_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        return
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        return
      }
      var rid = $(this).find("td[cell=1][name$=_rid]").attr("v")
      if ((typeof rid === "undefined")||(rid=="")) {
        return
      }
      var i = nodename+"--"+svcname+"--"+rid
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push({"nodename": nodename, "svcname": svcname, "rid": rid, "action": action})
      }
    })
    return data
}

function table_action_menu_get_resource_data(t, e, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return []
    }
    var rid = line.find("td[cell=1][name$=_rid]").first().attr("v")
    if ((typeof rid === "undefined")||(rid=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'svcname': svcname, 'rid': rid, 'action': action}]
    return data
}

function table_action_menu_get_resources_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var rid = line.find("td[cell=1][name$=_rid]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var colrid = rid.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc+","+rid
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           idxrid = cols.indexOf(colrid)
           for (i=0; i<lines.length; i++) {
             data.push({
               nodename: lines[i]["cells"][idxnode],
               svcname: lines[i]["cells"][idxsvc],
               rid: lines[i]["cells"][idxrid],
               action: action
             })
           }
         }
    })
    return data
}

//
// data actions menu: services
//
function table_data_action_menu_svcs_all(t, e){
  var data = table_action_menu_get_svc_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.data_actions_on_all_services")+"</li>"
  return s
}

function table_data_action_menu_svc(t, e){
  var data = table_action_menu_get_svc_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.data_actions_on_service", data[0])+"</li>"
  return s
}

function table_data_action_menu_svcs(t){
  var data = table_action_menu_get_svcs_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.data_actions_on_selected_services")+" (<b>"+data.length+"</b>)"+"</li>"
  return s
}

//
// agent actions menu: modules
//
function table_action_menu_modules_all(t, e){
  var data = table_action_menu_get_module_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_all_modules")+table_action_menu_module_entries(t, "modules_all")+"</li>"
  return s
}

function table_action_menu_module(t, e){
  var data = table_action_menu_get_module_data(t, e)
  if (data.length==0) {
    return ""
  }
  if ('svcname' in data[0]) {
    var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_module_on_service_on_node", data[0])+table_action_menu_module_entries(t, "module")+"</li>"
  } else {
    var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_module_on_node", data[0])+table_action_menu_module_entries(t, "module")+"</li>"
  }
  return s
}

function table_action_menu_modules(t){
  var data = table_action_menu_get_modules_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_selected_modules")+" (<b>"+data.length+"</b>)"+table_action_menu_module_entries(t, "modules")+"</li>"
  return s
}

//
// agent actions menu: resources
//
function table_action_menu_resources_all(t, e){
  var data = table_action_menu_get_resource_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_all_resources")+table_action_menu_resource_entries(t, "resources_all")+"</li>"
  return s
}

function table_action_menu_resource(t, e){
  var data = table_action_menu_get_resource_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_resource_on_service_on_node", data[0])+table_action_menu_resource_entries(t, "resource")+"</li>"
  return s
}

function table_action_menu_resources(t){
  var data = table_action_menu_get_resources_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_selected_resource")+" (<b>"+data.length+"</b>)"+table_action_menu_resource_entries(t, "resources")+"</li>"
  return s
}

//
// agent actions menu: services instances
//
function table_action_menu_svcs_all(t, e){
  var data = table_action_menu_get_svc_instance_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_all_services_instances")+table_action_menu_svc_entries(t, "svcs_all")+"</li>"
  return s
}

function table_action_menu_svc(t, e){
  var data = table_action_menu_get_svc_instance_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_services_instances_on_node", data[0])+table_action_menu_svc_entries(t, "svc")+"</li>"
  return s
}

function table_action_menu_svcs(t){
  var data = table_action_menu_get_svcs_instances_data_with_node(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_selected_services_instances")+" (<b>"+data.length+"</b>)"+table_action_menu_svc_entries(t, "svcs")+"</li>"
  return s
}

//
// agent actions menu: nodes
//
function table_action_menu_nodes_all(t, e){
  var data = table_action_menu_get_node_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_all_nodes")+table_action_menu_node_entries(t, "nodes_all")+"</li>"
  return s
}

function table_action_menu_node(t, e){
  var data = table_action_menu_get_node_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_node")+" <b>"+data[0]['nodename']+"</b>"+table_action_menu_node_entries(t, "node")+"</li>"
  return s
}

function table_action_menu_nodes(t){
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_selected_nodes")+" (<b>"+data.length+"</b>)"+table_action_menu_node_entries(t, "nodes")+"</li>"
  return s
}


//
// tool: topo
//
function trigger_tool_topo(tid) {
  var t = osvc.tables[tid]
  var datasvc = table_action_menu_get_svcs_data(t)
  var datanode = table_action_menu_get_nodes_data(t)
  if (datasvc.length+datanode.length==0) {
    return ""
  }
  var nodenames = new Array()
  for (i=0;i<datanode.length;i++) {
    nodenames.push(datanode[i]['nodename'])
  }
  var svcnames = new Array()
  for (i=0;i<datasvc.length;i++) {
    svcnames.push(datasvc[i]['svcname'])
  }
  topology("overlay", {
    "nodenames": nodenames,
    "svcnames": svcnames,
    "display": ["nodes", "services", "countries", "cities", "buildings", "rooms", "racks", "enclosures", "hvs", "hvpools", "hvvdcs"]
  })
  t.e_overlay.show()
}

function tool_topo(t) {
  var datasvc = table_action_menu_get_svcs_data(t)
  var datanode = table_action_menu_get_nodes_data(t)
  if (datasvc.length+datanode.length==0) {
    return ""
  }
  return "<div class='clickable icon dia16' onclick='trigger_tool_topo(\""+t.id+"\")'>"+i18n.t("action_menu.topology")+"</div>"
}

//
// tool: nodesantopo
//
function trigger_tool_nodesantopo(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sync_ajax('/init/ajax_node/ajax_nodes_stor?nodes='+nodes.join(","), [], 'overlay', function(){})
}

function tool_nodesantopo(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon hd16' onclick='trigger_tool_nodesantopo(\""+t.id+"\")'>"+i18n.t("action_menu.node_san_topo")+"</div>"
}

//
// tool: nodesysrepdiff
//
function trigger_tool_nodesysrepdiff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length<2) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sysrepdiff("overlay", {"nodes": nodes.join(",")})
}

function tool_nodesysrepdiff(t, data) {
  if (data.length<2) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_nodesysrepdiff(\""+t.id+"\")'>"+i18n.t("action_menu.node_sysrep_diff")+"</div>"
}

//
// tool: nodesysrep
//
function trigger_tool_nodesysrep(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sysrep("overlay", {"nodes": nodes.join(",")})
}

function tool_nodesysrep(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon log16' onclick='trigger_tool_nodesysrep(\""+t.id+"\")'>"+i18n.t("action_menu.node_sysrep")+"</div>"
}

//
// tool: svcdiff
//
function trigger_tool_svcdiff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_svcs_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['svcname'])
  }
  t.e_overlay.show()
  sync_ajax('/init/nodediff/ajax_svcdiff?node='+nodes.join(","), [], 'overlay', function(){})
}

function tool_svcdiff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_svcdiff(\""+t.id+"\")'>"+i18n.t("action_menu.svc_diff")+"</div>"
}

//
// tool: nodediff
//
function trigger_tool_nodediff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sync_ajax('/init/nodediff/ajax_nodediff?node='+nodes.join(","), [], 'overlay', function(){})
}

function tool_nodediff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_nodediff(\""+t.id+"\")'>"+i18n.t("action_menu.node_diff")+"</div>"
}

//
// tool: grpprf
//
function trigger_tool_grpprf(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sync_ajax('/init/nodes/ajax_grpprf?node='+nodes.join(","), [], 'overlay', function(){})
}

function tool_grpprf(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon spark16' onclick='trigger_tool_grpprf(\""+t.id+"\")'>"+i18n.t("action_menu.node_perf")+"</div>"
}

//
// data action: delete services
//
function trigger_data_action_delete_services() {
  console.log("delete")
}

function tool_data_action_delete_services(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<li class='clickable icon del16' onclick='trigger_tool_data_action_delete_services()'>"+i18n.t("action_menu.delete")+"</div>"
}


//
// tools wrapper: nodes
//
function table_tools_menu_nodes(t){
  var data = table_action_menu_get_nodes_data(t)
  var s = ""
  s += tool_nodediff(t, data)
  s += tool_nodesysrep(t, data)
  s += tool_nodesysrepdiff(t, data)
  s += tool_nodesantopo(t, data)
  s += tool_grpprf(t, data)
  return s
}

//
// tools wrapper: services
//
function table_tools_menu_svcs(t){
  var data = table_action_menu_get_svcs_data(t)
  var s = ""
  s += tool_svcdiff(t, data)
  return s
}

//
// data actions wrapper: services
//
function table_data_actions_menu_svcs(t){
  var data = table_action_menu_get_svcs_data(t)
  var s = ""
  s += data_action_delete_services(t, data)
  return s
}

//
// agent actions wrappers
//
function table_action_menu_module_entries(t, scope){
  return table_action_menu_single_entries(t, "modules", scope)
}

function table_action_menu_resource_entries(t, scope){
  return table_action_menu_single_entries(t, "resources", scope)
}

function table_action_menu_svc_entries(t, scope){
  return table_action_menu_single_entries(t, "services", scope)
}

function table_action_menu_node_entries(t, scope){
  return table_action_menu_single_entries(t, "nodes", scope)
}

function table_action_menu_single_entries(t, action_menu_key, scope){
  s = "<ul>"
  for (i=0; i<t.action_menu[action_menu_key].length; i++) {
    var e = t.action_menu[action_menu_key][i]
    try {
      var params = " params='"+e.params.join(",")+"'"
    } catch(err) {
      var params = ""
    }
    s += "<li class='clickable "+e['class']+"' action='"+e.action+"' scope='"+scope+"'"+params+">"+e.title+"</li>"
  }
  s += "</ul>"
  return s
}


