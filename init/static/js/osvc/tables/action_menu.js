//
// install agent action menu entries definitions in the table object
//
function table_action_menu_init_data(t) {
  t.action_menu_req_max = 1000
  t.column_selectors = {
    "svcname": "td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]",
    "nodename": "td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]",
    "rid": "td[cell=1][name$=_rid]",
    "module": "td[cell=1][name$=_run_module]"
  }

  t.action_menu_data = [
    {
      "title": "action_menu.tools",
      "class": "spark16",
      "children": [
        {
          "selector": ["clicked", "checked"],
          "title": "action_menu.on_nodes",
          "foldable": true,
          "cols": ["nodename"],
          "condition": "nodename",
          "children": [
            {
              "title": "action_menu.node_diff",
              "class": "icon common16",
              "fn": "tool_nodediff",
              "min": 2
            },
            {
              "title": "action_menu.node_sysrep",
              "class": "icon log16",
              "fn": "tool_nodesysrep",
              "min": 1
            },
            {
              "title": "action_menu.node_sysrep_diff",
              "class": "icon common16",
              "fn": "tool_nodesysrepdiff",
              "min": 2
            },
            {
              "title": "action_menu.node_san_topo",
              "class": "icon hd16",
              "fn": "tool_nodesantopo",
              "min": 1
            },
            {
              "title": "action_menu.node_perf",
              "class": "icon spark16",
              "fn": "tool_grpprf",
              "min": 1
            }
          ]
        },
        {
          "selector": ["checked"],
          "title": "action_menu.on_services",
          "foldable": true,
          "cols": ["svcname"],
          "condition": "svcname",
          "children": [
            {
              "title": "action_menu.svc_diff",
              "class": "icon common16",
              "fn": "tool_svcdiff",
              "min": 2
            }
          ]
        },
        {
          "selector": ["clicked", "checked"],
          "title": "action_menu.on_nodes_and_services",
          "foldable": true,
          "cols": ["svcname", "nodename"],
          "condition": "svcname,nodename",
          "children": [
            {
              "title": "action_menu.topology",
              "class": "icon dia16",
              "fn": "tool_topo",
              "min": 1
            }
          ]
        }
      ]
    },
    {
      "title": "action_menu.data_actions",
      "class": "hd16",
      "children": [
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_services',
          "cols": ["svcname"],
          "condition": "svcname",
          "children": [
            {
              "title": "action_menu.delete",
              "class": "icon del16",
              "fn": "data_action_delete_svcs",
              "min": 1
            }
          ]
        },
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_services_instances',
          "cols": ["svcname", "nodename"],
          "condition": "svcname+nodename",
          "children": [
            {
              "title": "action_menu.delete",
              "class": "icon del16",
              "fn": "data_action_delete_svc_instances",
              "min": 1
            }
          ]
        }
      ]
    },
    {
      "title": "action_menu.agent_actions",
      "class": "action16",
      "children": [
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_nodes',
          "cols": ["nodename"],
          "condition": "nodename",
          "children": [
            {
              'title': 'Update node information',
              'class': 'icon node16',
              "min": 1,
              'action': 'pushasset'
            },
            {
              'title': 'Update disks information',
              'class': 'icon hd16',
              "min": 1,
              'action': 'pushdisks'
            },
            {
              'title': 'Update app information',
              'class': 'icon svc-c',
              "min": 1,
              'action': 'push_appinfo'
            },
            {
              'title': 'Update services information',
              'class': 'icon svc-c',
              "min": 1,
              'action': 'pushservices'
            },
            {
              'title': 'Update installed packages information',
              'class': 'icon pkg16',
              "min": 1,
              'action': 'pushpkg'
            },
            {
              'title': 'Update installed patches information',
              'class': 'icon pkg16',
              "min": 1,
              'action': 'pushpatch'
            },
            {
              'title': 'Update stats',
              'class': 'icon spark16',
              "min": 1,
              'action': 'pushstats'
            },
            {
              'title': 'Update check values',
              'class': 'icon ok',
              "min": 1,
              'action': 'checks'
            },
            {
              'title': 'Update sysreport',
              'class': 'icon log16',
              "min": 1,
              'action': 'sysreport'
            },
            {
              'title': 'Update compliance modules',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'updatecomp'
            },
            {
              'title': 'Update opensvc agent',
              'class': 'icon pkg16',
              "min": 1,
              'action': 'updatepkg'
            },
            {
              'title': 'Rotate root password',
              'class': 'icon key',
              "min": 1,
              'action': 'rotate root pw'
            },
            {
              'title': 'Rescan scsi hosts',
              'class': 'icon hd16',
              "min": 1,
              'action': 'scanscsi'
            },
            {
              'title': 'Reboot',
              'class': 'icon action_restart_16',
              "min": 1,
              'action': 'reboot'
            },
            {
              'title': 'Reboot schedule',
              'class': 'icon action_restart_16',
              "min": 1,
              'action': 'schedule_reboot'
            },
            {
              'title': 'Reboot unschedule',
              'class': 'icon action_restart_16',
              "min": 1,
              'action': 'unschedule_reboot'
            },
            {
              'title': 'Shutdown',
              'class': 'icon action_stop_16',
              "min": 1,
              'action': 'shutdown'
            },
            {
              'title': 'Wake On LAN',
              'class': 'icon action_start_16',
              "min": 1,
              'action': 'wol'
            },
            {
              'title': 'Compliance check',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'compliance_check',
              'params': ["module", "moduleset"]
            },
            {
              'title': 'Compliance fix',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'compliance_fix',
              'params': ["module", "moduleset"]
            },
            {
              'title': 'action_menu.provisioning',
              'class': 'icon prov',
              "min": 1,
              'fn': 'agent_action_provisioning'
            }
          ]
        },
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_services_instances',
          "cols": ["svcname", "nodename"],
          "condition": "svcname+nodename",
          "children": [
            {
              'title': 'Start',
              'class': 'icon action_start_16',
              "min": 1,
              'action': 'start'
            },
            {
              'title': 'Stop',
              'class': 'icon action_stop_16',
              "min": 1,
              'action': 'stop'
            },
            {
              'title': 'Restart',
              'class': 'icon action_restart_16',
              "min": 1,
              'action': 'restart'
            },
            {
              'title': 'Switch',
              'class': 'icon action_switch_16',
              "min": 1,
              'action': 'switch'
            },
            {
              'title': 'Sync all remotes',
              'class': 'icon action_sync_16',
              "min": 1,
              'action': 'syncall'
            },
            {
              'title': 'Sync peer remotes',
              'class': 'icon action_sync_16',
              "min": 1,
              'action': 'syncnodes'
            },
            {
              'title': 'Sync disaster recovery remotes',
              'class': 'icon action_sync_16',
              "min": 1,
              'action': 'syncdrp'
            },
            {
              'title': 'Enable',
              'class': 'icon ok',
              "min": 1,
              'action': 'enable'
            },
            {
              'title': 'Disable',
              'class': 'icon nok',
              "min": 1,
              'action': 'disable'
            },
            {
              'title': 'Thaw',
              'class': 'icon ok',
              "min": 1,
              'action': 'thaw'
            },
            {
              'title': 'Freeze',
              'class': 'icon nok',
              "min": 1,
              'action': 'freeze'
            },
            {
              'title': 'Compliance check',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'compliance_check',
              'params': ["module", "moduleset"]
            },
            {
              'title': 'Compliance fix',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'compliance_fix',
              'params': ["module", "moduleset"]
            }
          ]
        },
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_resources',
          "cols": ["svcname", "nodename", "rid"],
          "condition": "svcname+nodename+rid",
          "children": [
            {
              'title': 'Start',
              'class': 'icon action_start_16',
              "min": 1,
              'action': 'start'
            },
            {
              'title': 'Stop',
              'class': 'icon action_stop_16',
              "min": 1,
              'action': 'stop'
            },
            {
              'title': 'Restart',
              'class': 'icon action_restart_16',
              "min": 1,
              'action': 'restart'
            },
            {
              'title': 'Enable',
              'class': 'icon ok',
              "min": 1,
              'action': 'enable'
            },
            {
              'title': 'Disable',
              'class': 'icon nok',
              "min": 1,
              'action': 'disable'
            }
          ]
        },
        {
          "selector": ["clicked", "checked", "all"],
          "foldable": true,
          'title': 'action_menu.on_modules',
          "cols": ["svcname", "nodename", "module"],
          "condition": "svcname+nodename+module,nodename+module",
          "children": [
            {
              'title': 'Check',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'check'
            },
            {
              'title': 'Fix',
              'class': 'icon comp-c',
              "min": 1,
              'action': 'fix'
            }
          ]
        }
      ]
    }
  ]
}

//
// install handler for click events on the table checkbox column.
// only function called at table init.
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
// action menu formatter entry point
//
function table_action_menu(t, e){
  // drop the previous action menu
  $("#am_"+t.id).remove()

  // purge the caches
  t.action_menu_req_cache = null
  t.action_menu_data_cache = {}

  // create and position the popup at the mouse click
  var am = $("<div id='am_"+t.id+"' class='white_float action_menu stackable'></div>")
  var pos = get_pos(e)
  t.div.append(am)
  $("#am_"+t.id).css({"left": pos[0] + "px", "top": pos[1] + "px"})

  // format the data as menu
  var ul = $("<ul></ul>")
  for (var i=0; i<t.action_menu_data.length; i++) {
    var li = table_action_menu_format_section(t, e, t.action_menu_data[i])
    if (li.html().length == 0) {
      continue
    }
    ul.append(li)
  }

  // empty menu banner
  if (ul.html().length == 0) {
    am.append("<span class='alert16 icon'>"+i18n.t("action_menu.no_action")+"</span>")
    return
  }
  am.append(ul)

  // display actions only for the clicked section
  var folders = $("#am_"+t.id+" .action_menu_folder")
  folders.addClass("right16")
  folders.children("ul,.action_menu_selector").hide()
  folders.bind("click", function(e){
    e.stopPropagation()
    var v = $(this).children(".action_menu_selector").is(":visible")
    folders.removeClass("down16")
    folders.addClass("right16")
    folders.children("ul,.action_menu_selector").hide()
    if (!v) {
      var selector = $(this).children(".action_menu_selector")
      selector.show()
      var scope = selector.children(".action_menu_selector_selected").attr("scope")
      $(this).children("ul").hide()
      $(this).children("ul[scope="+scope+"]").show()
      $(this).removeClass("right16")
      $(this).addClass("down16")
    }
  })
  return
}

function table_action_menu_format_section(t, e, section) {
  var ul = $("<ul></ul>")
  for (var i=0; i<section.children.length; i++) {
    var li = table_action_menu_format_selector(t, e, section.children[i])
    if (li.html().length == 0) {
      continue
    }
    ul.append(li)
  }
  var content = $("<li></li>")
  if (ul.children().length == 0) {
    return content
  }
  var title = $("<h3 class='line'><span></span></h3>")
  title.children().text(i18n.t(section.title))
  content.append(title)
  content.append(ul)

  return content
}

//
// filter a dataset, removing elements not meeting conditions defined
// in the action menu data
//
function table_action_menu_condition_filter(t, condition, data) {
  var cond = []
  var or_cond = condition.split(",")
  for (var i=0; i<or_cond.length; i++) {
    cond.push(or_cond[i].split("+"))
  }
  var _data = []
  for (var i=0; i<data.length; i++) {
    for (var j=0; j<cond.length; j++) {
      var violation = false
      for (var k=0; k<cond[j].length; k++) {
        if (!(cond[j][k] in data[i])) {
          violation = true
          break
        }
      }
      if (!violation) {
        _data.push(data[i])
        break
      }
    }
  }
  return _data
}

function table_action_menu_get_cols_data_clicked(t, e, scope, selector) {
  var data = []
  var cell = $(e.target)
  var line = cell.parents(".tl").first()
  var d = {}
  for (var i=0; i<selector.cols.length; i++) {
    var c = selector.cols[i]
    var s = t.column_selectors[c]
    var val = line.find(s).first().attr("v")
    if ((typeof val === "undefined") || (val=="") || (val == "empty")) {
      continue
    }
    d[c] = val
  }
  data.push(d)
  return table_action_menu_condition_filter(t, selector.condition, data)
}

function table_action_menu_get_cols_data_checked(t, e, scope, selector) {
  var data = []
  var sigs = []
  t.div.find(".tl").each(function(){
    var ck = $(this).find("input[id^="+t.id+"_ckid_]").first()
    if ((ck.length == 0) || !ck.is(":checked")) {
      return
    }
    var d = {}
    var sig = ""
    for (var i=0; i<selector.cols.length; i++) {
      var c = selector.cols[i]
      var s = t.column_selectors[c]
      var val = $(this).find(s).first().attr("v")
      if ((typeof val === "undefined") || (val=="") || (val == "empty")) {
        sig += "-"
        continue
      }
      sig += val
      d[c] = val
    }
    if (sigs.indexOf(sig) < 0) {
      sigs.push(sig)
      data.push(d)
    }
  })
  return table_action_menu_condition_filter(t, selector.condition, data)
}

function table_action_menu_get_cols_data_all(t, e, scope, selector) {
  var data = []
  var cell = $(e.target)
  var line = cell.parents(".tl").first()
  var cols = []

  // fetch all columns meaningful for the action menu
  // so we can cache the result and avoid other requests
  if (t.action_menu_req_cache) {
    data = t.action_menu_req_cache
  } else {
    var reverse_col = {}
    for (var c in t.column_selectors) {
      var s = t.column_selectors[c]
      var name = line.find(s).first().attr("name")
      if (!name) {
        continue
      }
      var col = name.replace(/.*_c_/, "")
      cols.push(col)
      reverse_col[col] = c
    }
    if (cols.length == 0) {
      t.action_menu_req_cache = []
      return data
    }

    var sigs = []
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = cols.join(",")
    vars[t.id+"_page"] = 1
    vars[t.id+"_perpage"] = t.action_menu_req_max
    t.div.find("input[id^="+t.id+"_f_]").each(function(){
      vars[$(this).attr("id")] = $(this).val()
    })
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
             var _cols = ["extra"].concat(t.columns)
           } else {
             var _cols = t.columns
           }
           for (i=0; i<lines.length; i++) {
             var d = {}
             var sig = ""
             for (var j=0; j<cols.length; j++) {
               col = cols[j]
               idx = _cols.indexOf(col)
               var val = lines[i]["cells"][idx]
               d[reverse_col[col]] = val
               sig += "-"+val
             }
             if (sigs.indexOf(sig) < 0) {
               sigs.push(sig)
               data.push(d)
             }
           }
         }
    })
    t.action_menu_req_cache = data
  }

  // digest cached data for the selector
  var sigs = []
  var _data = []
  for (i=0; i<data.length; i++) {
    var d = {}
    var _d = data[i]
    var sig = ""
    for (var j=0; j<selector.cols.length; j++) {
      var col = selector.cols[j]
      if (!(col in _d)) {
        continue
      }
      var val = _d[col]
      d[col] = val
      sig += "-"+val
    }
    if (sigs.indexOf(sig) < 0) {
      sigs.push(sig)
      _data.push(d)
    }
  }
  return table_action_menu_condition_filter(t, selector.condition, _data)
}

function table_action_menu_get_cols_data(t, e, scope, selector) {
  if (scope == "clicked") {
    return table_action_menu_get_cols_data_clicked(t, e, scope, selector)
  } else if (scope == "checked") {
    return table_action_menu_get_cols_data_checked(t, e, scope, selector)
  } else if (scope == "all") {
    return table_action_menu_get_cols_data_all(t, e, scope, selector)
  }
  return []
}

function table_action_menu_format_selector(t, e, selector) {
  if (selector.title) {
    var title = $("<span></span>")
    title.text(i18n.t(selector.title))
  }
  var e_selector = $("<div class='action_menu_selector'></div>")
  var content = $("<li></li>")
  if (selector.foldable) {
    content.addClass("action_menu_folder")
  }

  for (var i=0; i<selector.selector.length; i++) {
    var scope = selector.selector[i]

    // compute selected cursor
    cache_id = ""
    for (var j=0; j<selector.cols.length; j++) {
      cache_id += '-'+selector.cols[j]
    }
    cache_id += '-'+scope
    if (cache_id in t.action_menu_data_cache) {
      var data = t.action_menu_data_cache[cache_id]
    } else {
      var data = table_action_menu_get_cols_data(t, e, scope, selector)
      t.action_menu_data_cache[cache_id] = data
    }

    // prepare action list for scope
    var ul = $("<ul></ul>")
    ul.attr("scope", scope)
    if (data.length > 0) {
      for (var j=0; j<selector.children.length; j++) {
        var leaf = selector.children[j]
        if (data.length < leaf.min) {
          continue
        }
        var li = table_action_menu_format_leaf(t, e, leaf)
        li.attr("cache_id", cache_id)
        li.bind("click", function(e) {
          e.stopPropagation()
          var fn = $(this).attr("fn")
          if (fn) {
            window[fn](t, e)
          } else {
            table_action_menu_agent_action(t, e)
          }
        })
        ul.append(li)
      }
    }

    // prepare the selector scope button
    var s = $("<div class='ellipsis'></div>")
    s.attr("scope", scope)

    // disable the scope if no data
    if (data.length == 0) {
      s.addClass("action_menu_selector_disabled")
    }

    // set as selected if not disabled and no other scope is already selected
    if ((e_selector.children(".action_menu_selector_selected").length == 0) && !s.hasClass("action_menu_selector_disabled")) {
      s.addClass("action_menu_selector_selected")
    }

    // set the span text
    if ((scope == "clicked") && (data.length > 0)) {
      var l = []
      for (var j=0; j<selector.cols.length; j++) {
        var c = selector.cols[j]
        if (c in data[0]) {
          l.push(data[0][c])
        }
      }
      s.text(l.join("-"))
      s.hover(function() {
        $(this).removeClass("ellipsis");
        var maxscroll = $(this).width();
        var speed = maxscroll * 15;
        $(this).animate({
          scrollLeft: maxscroll
        }, speed, "linear");
      }, function() {
        $(this).stop();
        $(this).addClass("ellipsis");
        $(this).animate({
          scrollLeft: 0
        }, 'slow');
      })
    } else if ((scope == "checked") || (scope == "all")) {
      var count = data.length
      var suffix = ""
      if (count == t.action_menu_req_max) {
        suffix = "+"
      }
      s.text(scope+" ("+count+suffix+")")
    } else {
      s.text(scope)
    }

    // add the action list and bind click handler if not disabled
    if ((ul.children().length > 0) && !s.hasClass("action_menu_selector_disabled")) {
      if (!s.hasClass("action_menu_selector_selected")) {
        ul.hide()
      }
      content.append(ul)
      s.addClass("clickable")
      s.bind("click", function(e) {
        e.stopPropagation()
        $(this).siblings().removeClass("action_menu_selector_selected")
        $(this).addClass("action_menu_selector_selected")
        var scope = $(this).attr("scope")
        $(this).parent().siblings("ul").hide()
        $(this).parent().siblings("ul[scope="+scope+"]").show()
      })
    } else {
      s.bind("click", function(e) {
        e.stopPropagation()
      })
    }

    e_selector.append(s)
  }
  if (content.children("ul").length > 0) {
    content.prepend(e_selector)
    if (selector.title) {
      content.prepend(title)
    }
  }

  return content
}

function table_action_menu_format_leaf(t, e, leaf) {
  var li = $("<li class='action_menu_leaf clickable'></li>")
  if (leaf.action) {
    try {
      var params = leaf.params.join(",")
    } catch(err) {
      var params = ""
    }
    li.attr("action", leaf.action)
    li.attr("params", params)
    //li.attr("scope", scope)
  }
  li.attr("fn", leaf.fn)
  li.addClass(leaf['class'])
  li.text(i18n.t(leaf.title))
  return li
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
    url: services_get_url() + "/init/compliance/call/json/comp_get_all_moduleset",
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
    url: services_get_url() + "/init/compliance/call/json/comp_get_all_module",
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
// Only leave the chosen leaf and its parents visible.
// Used by tools needing the space to pop addtional questions.
//
function table_action_menu_focus_on_leaf(t, entry) {
  // hide other choices
  entry.parent().parent().parent().parent().siblings().hide()
  entry.parent().parent().parent().siblings('ul').hide()
  entry.parent().parent().siblings('li').hide()
  entry.parent().siblings('ul').hide()

  // hide other actions in this selector scope
  entry.siblings().hide()
  entry.addClass("b")
  entry.unbind("click")
  entry.parent("ul").parent().unbind("click")
}

function table_action_menu_yes_no(t, msg, callback) {
   var e = $("<div style='margin-top:0.6em'></div>")
   var title = $("<div></div>")
   title.text(i18n.t(msg))
   var yes = $("<div class='ok float clickable' name='yes'>"+i18n.t("action_menu.yes")+"</div>")
   var no = $("<div class='nok float clickable' name='no'>"+i18n.t("action_menu.no")+"</div>")
   e.append(title)
   e.append(yes)
   e.append(no)
   e.append($("<br>"))
   yes.bind("click", function(e){
     $(this).unbind("click")
     $(this).removeClass("check16")
     $(this).addClass("spinner")
     callback(e)
   })
   no.bind("click", function(){
     $("#am_"+t.id).remove()
   })
   return e
}

//
// ask for a confirmation on first call, recurse once to do real stuff
// given a dataset, post each entry into the action_q
//
function table_action_menu_agent_action(t, e, confirmation) {
    var entry = $(e.target)
    var cache_id = entry.attr("cache_id")
    var action = entry.attr("action")

    if (!(confirmation==true)) {
      s = ""

      table_action_menu_focus_on_leaf(t, entry)

      // action parameters
      var params = entry.attr("params")
      if (typeof params !== "undefined") {
        params = params.split(",")
        for (var i=0; i<params.length; i++) {
          var param = params[i]
          try {
            s += t["action_menu_param_"+param]()
          } catch(err) {}
        }
      }

      var yes_no = table_action_menu_yes_no(t, 'action_menu.confirmation', function(){
        table_action_menu_agent_action(t, e, true)
      })
      $("<hr>").insertAfter(entry)
      yes_no.insertAfter(entry)
      return
    }

    // after confirmation
    var data = t.action_menu_data_cache[cache_id]
    for (var i=0; i<data.length; i++) {
      data[i]["action"] = action
    }

    // fetched checked options
    var params = {}
    $("#am_"+t.id).find("input[otype]:checked").each(function(){
      otype = $(this).attr("otype")
      oname = $(this).attr("oname")
      if (!(otype in params)) {
        params[otype] = []
      }
      params[otype].push(oname)
    })

    // add action parameters to each data entry
    for (otype in params) {
      if (params[otype].length > 0) {
        for (var i=0; i<data.length; i++) {
          data[i][otype] = params[otype].join(",")
        }
      }
    }

    // trigger the animation to highlight the action_q posting
    table_action_menu_click_animation(t)

    //services_osvcpostrest("R_ACTION_QUEUE", "", "", del_data, function(jd) {
    $.ajax({
      //async: false,
      type: "POST",
      url: services_get_url() + "/init/action_menu/call/json/json_action",
      data: {"data": JSON.stringify(data)},
      success: function(msg){
        table_action_menu_status(msg)
      }
    })
}




//
// tool: topo
//
function tool_topo(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var nodenames = new Array()
  for (i=0;i<data.length;i++) {
    nodenames.push(data[i]['nodename'])
  }
  var svcnames = new Array()
  for (i=0;i<data.length;i++) {
    svcnames.push(data[i]['svcname'])
  }
  topology("overlay", {
    "nodenames": nodenames,
    "svcnames": svcnames,
    "display": ["nodes", "services", "countries", "cities", "buildings", "rooms", "racks", "enclosures", "hvs", "hvpools", "hvvdcs"]
  })
  t.e_overlay.show()
}

//
// tool: nodesantopo
//
function tool_nodesantopo(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
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

//
// tool: nodesysrepdiff
//
function tool_nodesysrepdiff(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sysrepdiff("overlay", {"nodes": nodes.join(",")})
}

//
// tool: nodesysrep
//
function tool_nodesysrep(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sysrep("overlay", {"nodes": nodes.join(",")})
}

//
// tool: svcdiff
//
function tool_svcdiff(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['svcname'])
  }
  t.e_overlay.show()
  sync_ajax('/init/nodediff/ajax_svcdiff?node='+nodes.join(","), [], 'overlay', function(){})
}

//
// tool: nodediff
//
function tool_nodediff(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  t.e_overlay.show()
  sync_ajax('/init/nodediff/ajax_nodediff?node='+nodes.join(","), [], 'overlay', function(){})
}

//
// tool: grpprf
//
function tool_grpprf(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
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

//
// data action: delete services
//
function data_action_delete_svcs(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var del_data = new Array()
  for (i=0;i<data.length;i++) {
    del_data.push({'svc_name': data[i]['svcname']})
  }
  services_osvcdeleterest("R_SERVICES", "", "", del_data, function(jd) {
    if (jd.error && (jd.error.length > 0)) {
      $(".flash").show("blind").html(services_error_fmt(jd))
    }
    if (jd.info && (jd.info.length > 0)) {
      $(".flash").show("blind").html("<pre>"+jd.info+"</pre>")
    }
  },
  function(xhr, stat, error) {
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  })
}

//
// data action: delete service instances
//
function data_action_delete_svc_instances(t, e) {
  var entry = $(e.target)
  var cache_id = entry.attr("cache_id")
  var data = t.action_menu_data_cache[cache_id]
  var del_data = new Array()
  for (i=0;i<data.length;i++) {
    del_data.push({
      'mon_svcname': data[i]['svcname'],
      'mon_nodname': data[i]['nodename']
    })
  }
  services_osvcdeleterest("R_SERVICE_INSTANCES", "", "", del_data, function(jd) {
    if (jd.error && (jd.error.length > 0)) {
      $(".flash").show("blind").html(services_error_fmt(jd))
    }
    if (jd.info && (jd.info.length > 0)) {
      $(".flash").show("blind").html("<pre>"+jd.info+"</pre>")
    }
  },
  function(xhr, stat, error) {
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  })
}

//
// agent action: provisioning
//
function agent_action_provisioning(t, e) {
  var entry = $(e.target)

  table_action_menu_focus_on_leaf(t, entry)
  var div = $("<div class='template_selector'></div>")
  var title = $("<div data-i18n='action_menu.provisioning_selector_title'></div>").i18n()
  div.append($("<hr>"))
  div.append(title)
  div.insertAfter(entry)

  spinner_add(div)
  services_osvcgetrest("R_PROVISIONING_TEMPLATES", "", "", function(jd) {
    spinner_del(div)
    if (jd.error && (jd.error.length > 0)) {
      $(".flash").show("blind").html(services_error_fmt(jd))
    }
    if (jd.data.length == 0) {
      div.append($("<div data-i18n='action_menu.provisioning_selector_empty'></div>").i18n())
    }
    for (var i=0; i<jd.data.length; i++) {
      var d = jd.data[i]

      // populate the template selector
      var input = $("<input name='template_selector' type='radio'></input>")
      input.attr("tpl_id", d.id)
      input.uniqueId()
      var label = $("<label></label>")
      label.attr("for", input.attr("id"))
      var name = $("<div class='template_title'></div>").text(d.tpl_name)
      var comment = $("<div class='template_comment'></div>").text(d.tpl_comment)
      label.append(name)
      label.append(comment)
      div.append(input)
      div.append(label)

      // create the submit form
      tpl_form = $("<form></form>")
      tpl_form.hide()

      // get keys from the template command
      var keys = []
      var re = RegExp(/%\((\w+)\)s/g)
      do {
        var m = re.exec(d.tpl_command)
        if (m) {
          var key = m[1]
          if (keys.indexOf(key) < 0) {
            keys.push(key)
          }
        }
      } while (m)

      // for each key add a text input to the form
      for (var j=0; j<keys.length; j++) {
        var key = keys[j]
        if (key == "nodename") {
          continue
        }
        var line = $("<div class='template_form_line'></div>")
        var title = $("<div></div>")
        title.text(key)
        var input = $("<input class='oi'></input>")
        input.attr("key", key)
        line.append(title)
        line.append(input)
        tpl_form.append(line)
      }

      // keyup in the form inputs subst and beautifies the command
      // in the display_beautified div
      tpl_form.find("input").bind("keyup", function(ev) {
        var form = $(this).parents("form").first()
        var command = form.find("[name=command]").text()
        var display_beautified = form.find("[name=beautified]")
        form.find("input").each(function(){
          var val = $(this).val()
          var key = $(this).attr("key")
          var re = new RegExp("%\\(" + key + "\\)s", "g")
          if (val == "") {
            return
          }
          command = command.replace(re, "<span class=syntax_red>"+val+"</span>")
        })
        command = command.replace(/--provision/g, "<br>&nbsp;&nbsp;<span class=syntax_blue>--provision</span>")
        command = command.replace(/--resource/g, "<br>&nbsp;&nbsp;<span class=syntax_blue>--resource</span>")
        command = command.replace(/{/g, "{<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        command = command.replace(/\",/g, "\",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        command = command.replace(/}/g, "<br>&nbsp;&nbsp;&nbsp;&nbsp;}")
        command = command.replace(/%\(\w+\)s/g, function(x) {
          return "<span class=syntax_red>" + x + "</span>"
        })
        command = command.replace(/("\w+":)/g, function(x) {
          return "<span class=syntax_green>" + x + "</span>"
        })
        display_beautified.html("<tt>"+command+"</tt>")
      })

      // add a command display zone
      var display =$("<div name='command'><div>")
      display.text(d.tpl_command)
      display.hide()
      tpl_form.append(display)
      var display_beautified = $("<div class='template_beautified' name='beautified'><div>")
      tpl_form.append(display_beautified)

      // add submit/cancel buttons
      var yes_no = table_action_menu_yes_no(t, 'action_menu.provisioning_submit', function(e){
        var entry = $(e.target).parents(".template_selector").prev()
        var cache_id = entry.attr("cache_id")
        var data = t.action_menu_data_cache[cache_id]
        var form = $(e.target).parents("form").first()
        var tpl_id = $(e.target).parents(".template_selector").find("input[type=radio]:checked").attr("tpl_id")
        var input_data = {}
        var put_data = []
        form.find("input").each(function(){
          var val = $(this).val()
          var key = $(this).attr("key")
          input_data[key] = val
        })
        for (var i=0; i<data.length; i++) {
          var d = {}
          for (k in input_data) {
            d[k] = input_data[k]
          }
          d.nodename = data[i].nodename
          put_data.push(d)
        }

        // animate to highlight the enqueueing
        table_action_menu_click_animation(t)

        // put the provisioning action in queue
        services_osvcputrest("R_PROVISIONING_TEMPLATE", [tpl_id], "", put_data, function(jd) {
          if (jd.error && (jd.error.length > 0)) {
            $(".flash").show("blind").html(services_error_fmt(jd))
          }
          if (jd.info && (jd.info.length > 0)) {
            $(".flash").show("blind").html("<pre>"+jd.info+"</pre>")
          }
        },
        function(xhr, stat, error) {
          $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
        })
      })

      tpl_form.append(yes_no)
      div.append(tpl_form)

      // click on a label opens the associated form
      label.bind("click", function(ev) {
        $(this).parent().children("form").hide()
        $(this).next().show()
        $(this).next("form").find("input").first().focus()
      })
    }
  },
  function(xhr, stat, error) {
    spinner_del(div)
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  })

}
