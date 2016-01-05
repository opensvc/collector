function search_get_menu(fk)
{
  var menu = {
    "users": {
        "tab" : 'user_tabs("__rowid__", {"user_id": "__id__", "fullname": "__fullname__"})',
        "title": "__fullname__ <__email__>",
        "menu_entry_id": "adm-usr",
        "class": "guy16 fa-2x search-section-icon",
        "subclass" : "meta_username clickable",
        "links" : [
          {
            "title": "users",
            "menu_entry_id": "adm-usr",
            "class" : "guys16",
            "link" : "/init/users/users?clear_filters=true&users_f_fullname=__fullname__"
          },
          {
            "title": "logs",
            "menu_entry_id": "adm-log",
            "class" : "log16",
            "link" : "/init/log/log?clear_filters=true&log_f_log_user=__fullname__"
          },
          {
            "title": "apps",
            "menu_entry_id": "adm-app",
            "class" : "svc",
            "link" : "/init/apps/apps?clear_filters=true&apps_f_responsibles=%__fullname__%"
          }
        ]
    },
    "safe_files": {
        "title": "__name__ (__uuid__)",
        "menu_entry_id": "view-safe",
        "class": "pkg16 fa-2x search-section-icon",
        "subclass" : "meta_file",
        "links" : []
    },
    "disks": {
        "title": "__disk_id__",
        "menu_entry_id": "view-disks",
        "class": "hd16 fa-2x search-section-icon",
        "subclass" : "meta_app",
        "links" : [
          {
            "title": "disk_info",
            "menu_entry_id": "view-disks",
            "class" : "hd16",
            "link" : "/init/disks/disks?clear_filters=true&disks_f_disk_id=__disk_id__"
          }
        ]
    },
    "apps": {
        "title": "__app__",
        "tab" : 'app_tabs("__rowid__", {"app_name": "__app__"})',
        "menu_entry_id": "view-dummy",
        "class": "svc fa-2x search-section-icon",
        "subclass" : "meta_app clickable",
        "links" : [
          {
            "title": "nodes",
            "menu_entry_id": "view-nodes",
            "class" : "hw16",
            "link" : "/init/nodes/nodes?clear_filters=true&nodes_f_project=__app__"
          },
          {
            "title": "status",
            "menu_entry_id": "view-service-instances",
            "class" : "svc",
            "link" : "/init/default/svcmon?clear_filters=true&svcmon_f_svc_app=__app__"
          },
          {
            "title": "disk_info",
            "menu_entry_id": "view-disks",
            "class" : "hd16",
            "link" : "/init/disks/disks?clear_filters=true&disks_f_app=__app__"
          },
          {
            "title": "availability",
            "menu_entry_id": "stat-avail",
            "class" : "avail16",
            "link" : "/init/svcmon_log/svcmon_log?clear_filters=true&svcmon_log_f_svc_app=__app__"
          },
          {
            "title": "app",
            "menu_entry_id": "adm-app",
            "class" : "svc",
            "link" : "/init/apps/apps?clear_filters=true&apps_f_app=__app__"
          }
        ]
    },
    "ips": {
        "title": "__addr__@__nodename__",
        "menu_entry_id": "view-node-net",
        "class": "net16 fa-2x search-section-icon",
        "subclass" : "meta_username",
        "links" : [
          {
            "title": "nodes",
            "menu_entry_id": "view-nodes",
            "class" : "hw16",
            "link" : "/init/nodes/nodes?clear_filters=true&nodes_f_nodename=__nodename__"
          },
          {
            "title": "dashboard",
            "menu_entry_id": "view-dashboard",
            "class" : "alert16",
            "link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_nodename=__nodename__"
          },
          {
            "title": "services",
            "menu_entry_id": "view-services",
            "class" : "svc",
            "link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_nodname=__nodename__"
          },
          {
            "title": "resources",
            "menu_entry_id": "view-resources",
            "class" : "svc",
            "link" : "/init/resmon/resmon?clear_filters=true&resmon_f_nodename=__nodename__"
          },
          {
            "title": "appinfo",
            "menu_entry_id": "view-appinfo",
            "class" : "svc",
            "link" : "/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_nodename=__nodename__"
          },
          {
            "title": "action",
            "menu_entry_id": "view-actions",
            "class" : "action16",
            "link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_hostname=__nodename__"
          },
          {
            "title": "checks",
            "menu_entry_id": "view-checks",
            "class" : "check16",
            "link" : "/init/checks/checks?clear_filters=true&checks_f_chk_nodename=__nodename__"
          },
          {
            "title": "packages",
            "menu_entry_id": "view-pkg",
            "class" : "pkg16",
            "link" : "/init/packages/packages?clear_filters=true&packages_f_nodename=__nodename__"
          },
          {
            "title": "network",
            "menu_entry_id": "view-net",
            "class" : "net16",
            "link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_nodename=__nodename__"
          },
          {
            "title": "san",
            "menu_entry_id": "view-san",
            "class" : "net16",
            "link" : "/init/nodesan/nodesan?clear_filters=true&nodesan_f_nodename=__nodename__"
          },
          {
            "title": "disks",
            "menu_entry_id": "view-disks",
            "class" : "hd16",
            "link" : "/init/disks/disks?clear_filters=true&disks_f_disk_nodename=__nodename__"
          },
          {
            "title": "saves",
            "menu_entry_id": "view-saves",
            "class" : "cd16",
            "link" : "/init/saves/saves?clear_filters=true&saves_f_save_nodename=__nodename__"
          },
          {
            "title": "compliance_status",
            "menu_entry_id": "comp-status",
            "class" : "comp16",
            "link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_nodename=__nodename__"
          },
          {
            "title": "compliance_log",
            "menu_entry_id": "comp-log",
            "class" : "log16",
            "link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_nodename=__nodename__"
          },
          {
            "title": "logs",
            "menu_entry_id": "adm-log",
            "class" : "log16",
            "link" : "/init/log/log?clear_filters=true&log_f_log_nodename=__nodename__"
          }
        ],
        "special_header_links" : [
          {
            "title": "nodes_net",
            "menu_entry_id": "view-node-net",
            "class" : "hw16",
            "link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_addr=__addr__"
          }
        ]
    },
    "groups": {
        "tab" : 'group_tabs("__rowid__", {"group_id": "__id__", "group_name": "__role__"})',
        "title": "__role__",
        "menu_entry_id": "adm-usr",
        "class": "guys16 fa-2x search-section-icon",
        "subclass" : "meta_username clickable",
        "links" : [
          {
            "title": "nodes",
            "menu_entry_id": "view-nodes",
            "class" : "hw16",
            "link" : "/init/nodes/nodes?clear_filters=true&nodes_f_team_responsible=__role__"
          },
          {
            "title": "apps",
            "menu_entry_id": "adm-app",
            "class" : "svc",
            "link" : "/init/apps/apps?clear_filters=true&apps_f_roles=__role__"
          },
          {
            "title": "checks",
            "menu_entry_id": "view-checks",
            "class" : "check16",
            "link" : "/init/checks/checks?clear_filters=true&checks_f_team_responsible=__role__"
          },
          {
            "title": "compliance_status",
            "menu_entry_id": "comp-status",
            "class" : "comp16",
            "link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_team_responsible=__role__"
          }
        ]
    },
    "services": {
        "tab" : 'service_tabs("__rowid__", {"svcname": "__svc_name__"})',
        "title": "__svc_name__",
        "menu_entry_id": "view-services",
        "class": "svc fa-2x search-section-icon",
        "subclass" : "meta_svcname clickable",
        "links" : [
          {
            "title": "dashboard",
            "menu_entry_id": "view-dashboard",
            "class" : "alert16",
            "link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_svcname=__svc_name__"
          },
          {
            "title": "status",
            "menu_entry_id": "view-service-instances",
            "class" : "alert16",
            "link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_svcname=__svc_name__"
          },
          {
            "title": "resources",
            "menu_entry_id": "view-resources",
            "class" : "svc",
            "link" : "/init/resmon/resmon?clear_filters=true&resmon_f_svcname=__svc_name__"
          },
          {
            "title": "appinfo",
            "menu_entry_id": "view-appinfo",
            "class" : "alert16",
            "link" : "/init/dashboard/index?clear_/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_svcname=__svc_name__"
          },
          {
            "title": "action",
            "menu_entry_id": "view-actions",
            "class" : "action16",
            "link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_svcname=__svc_name__"
          },
          {
            "title": "checks",
            "menu_entry_id": "view-checks",
            "class" : "check16",
            "link" : "/init/checks/checks?clear_filters=true&checks_f_chk_svcname=__svc_name__"
          },
          {
            "title": "disks",
            "menu_entry_id": "view-disks",
            "class" : "hd16",
            "link" : "/init/disks/disks?clear_filters=true&disks_f_disk_svcname=__svc_name__"
          },
          {
            "title": "saves",
            "menu_entry_id": "view-saves",
            "class" : "cd16",
            "link" : "/init/saves/saves?clear_filters=true&saves_f_save_svcname=__svc_name__"
          },
          {
            "title": "compliance_status",
            "menu_entry_id": "comp-status",
            "class" : "comp16",
            "link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_svcname=__svc_name__"
          },
          {
            "title": "compliance_log",
            "menu_entry_id": "comp-log",
            "class" : "log16",
            "link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_svcname=__svc_name__"
          },
          {
            "title": "availability",
            "menu_entry_id": "stat-avail",
            "class" : "avail16",
            "link" : "/init/svcmon_log/svcmon_log?clear_filters=true&svcmon_log_f_svc_name=__svc_name__"
          },
          {
            "title": "logs",
            "menu_entry_id": "adm-log",
            "class" : "log16",
            "link" : "/init/log/log?clear_filters=true&log_f_log_svcname=__svc_name__"
          }
        ]
    },
    "nodes": {
        "tab" : 'node_tabs("__rowid__", {"nodename": "__nodename__"})',
        "title": "__nodename__",
        "menu_entry_id": "view-nodes",
        "class": "node16 fa-2x search-section-icon",
        "subclass" : "meta_nodename clickable",
        "links" : [
          {
            "title": "nodes",
            "menu_entry_id": "view-nodes",
            "class" : "hw16",
            "link" : "/init/nodes/nodes?clear_filters=true&nodes_f_nodename=__nodename__"
          },
          {
            "title": "dashboard",
            "menu_entry_id": "view-dashboard",
            "class" : "alert16",
            "link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_nodename=__nodename__"
          },
          {
            "title": "services",
            "menu_entry_id": "view-service-instances",
            "class" : "svc",
            "link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_nodname=__nodename__"
          },
          {
            "title": "resources",
            "menu_entry_id": "view-resources",
            "class" : "svc",
            "link" : "/init/resmon/resmon?clear_filters=true&resmon_f_nodename=__nodename__"
          },
          {
            "title": "appinfo",
            "menu_entry_id": "view-appinfo",
            "class" : "svc",
            "link" : "/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_nodename=__nodename__"
          },
          {
            "title": "actions",
            "menu_entry_id": "view-actions",
            "class" : "action16",
            "link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_hostname=__nodename__"
          },
          {
            "title": "checks",
            "menu_entry_id": "view-checks",
            "class" : "check16",
            "link" : "/init/checks/checks?clear_filters=true&checks_f_chk_nodename=__nodename__"
          },
          {
            "title": "packages",
            "menu_entry_id": "view-pkg",
            "class" : "pkg16",
            "link" : "/init/packages/packages?clear_filters=true&packages_f_nodename=__nodename__"
          },
          {
            "title": "network",
            "menu_entry_id": "view-net",
            "class" : "net16",
            "link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_nodename=__nodename__"
          },
          {
            "title": "san",
            "menu_entry_id": "view-san",
            "class" : "net16",
            "link" : "/init/nodesan/nodesan?clear_filters=true&nodesan_f_nodename=__nodename__"
          },
          {
            "title": "disks",
            "menu_entry_id": "view-disks",
            "class" : "hd16",
            "link" : "/init/disks/disks?clear_filters=true&disks_f_disk_nodename=__nodename__"
          },
          {
            "title": "compliance_status",
            "menu_entry_id": "comp-status",
            "class" : "comp16",
            "link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_nodename=__nodename__"
          },
          {
            "title": "compliance_log",
            "menu_entry_id": "comp-log",
            "class" : "log16",
            "link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_nodename=__nodename__"
          },
          {
            "title": "logs",
            "menu_entry_id": "adm-log",
            "class" : "log16",
            "link" : "/init/log/log?clear_filters=true&log_f_log_nodename=__nodename__"
          }
        ]
    },
    "filtersets": {
        "tab" : "/init/compliance/json_tree_action?operation=show&obj_type=filterset&obj_id=__id__",
        "title": "__fset_name__",
        "menu_entry_id": "adm-filters",
        "class": "filter16 fa-2x search-section-icon",
        "subclass" : "meta_username clickable",
        "links" : [
          {
            "title": "designer",
            "menu_entry_id": "comp-designer",
            "class" : "wf16",
            "link" : "/init/compliance/comp_admin?obj_filter=__fset_name__"
          }
        ]
    },
    "vms": {
        "tab" : 'node_tabs("__rowid__", {"nodename": "__mon_vmname__"})',
        "title": "__mon_vmname__",
        "menu_entry_id": "view-nodes",
        "class": "hv16 fa-2x search-section-icon",
        "subclass" : "meta_nodename",
        "links" : [
          {
            "title": "status",
            "menu_entry_id": "view-service-instances",
            "class" : "svc",
            "link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_vmname=__mon_vmname__"
          }
        ]
    }
  }
  return menu[fk];
}

function search_build_result_row(label, first, res, count) {
  var section_data = search_get_menu(label)

  // init result row, set icon cell
  var row_group = $("<div></div>")
  var row = $("<tr></tr>")
  row_group.append(row)
  var cell_icon = $("<td></td>")
  cell_icon.addClass(section_data.class)
  row.append(cell_icon)

  // title cell
  cell_result = $("<td></td>")
  p_title = $("<p></p>")
  cell_result.append(p_title)
  row.append(cell_result)

  if (first==1) {
    // first header with %___%
    var title = "%"+ $('#search_input').val() +"%";
    p_title.text(title)
  } else {
    // substitute key in the title format
    var title = section_data.title
    for (key in res) {
      title = title.replace("__"+key+"__", res[key])
      p_title.text(title)
    }
    p_title.addClass(section_data.subclass)

    var tab = section_data.tab
    if (tab) {
      // create a div to host the result tab
      tab_tr = $("<tr></tr>")
      tab_td = $("<td colspan='2'></td>")
      tab_div = $("<div class='stackable searchtab hidden'></div>")
      tab_tr.append(tab_td)
      tab_td.append(tab_div)
      tab_div.uniqueId()
      row_group.append(tab_tr)

      // mangle extra id to satisfy tabs code constraints
      var rowid = tab_div.attr("id").replace(/[ \/\.-]/g, '_')
      tab_div.attr("id", rowid)

      // substitute the keys in the defined tab action
      tab = tab.replace("__rowid__", rowid)
      for (key in res) {
        tab = tab.replace("__"+key+"__", res[key])
      }

      if (tab[0] == "/") {
        // tab action: load ajax content
        var url = services_get_url() + tab
        var fn = "sync_ajax('"+url+"', [], '"+rowid+"', function() {})"
      } else {
        // tab action: execute a function
        var fn = tab
      }
      fn = '$("#'+ rowid + '").show();' + fn
      p_title.attr("onclick", fn)
    }
  }

  // add links to views
  if (first==1 && section_data.special_header_links != undefined) {
    // special condition for first element if present
    links = section_data.special_header_links
  } else {
    links = section_data.links
  }

  for(j=0; j<links.length; j++) {
    var link_data = links[j]
    if (osvc.hidden_menu_entries.indexOf(link_data.menu_entry_id) >= 0) {
      continue
    }
    var url = link_data.link
    for (key in res) {
      url = url.replace("__"+key+"__", res[key])
    }
    // leftover (the first==1 case)
    url = url.replace(/__\w+__/, title)

    var a_link = $("<a class='search-link'></a>")
    a_link.addClass(link_data.class)
    a_link.attr("href", url)
    a_link.attr("target", "_blank")
    a_link.text(i18n.t("search.menu_link."+ link_data.title))
    cell_result.append(a_link)
  }
  return row_group.children()
}

function search_build_result_view(label, resultset) {
  var section_data = search_get_menu(label)
  if (osvc.hidden_menu_entries.indexOf(section_data.menu_entry_id) >= 0) {
    return
  }
  var section_div = $("<div class='menu_section'></div>")
  section_div.attr("id", label)
  section_div.text(i18n.t("search.menu_header.title_"+label) + " (" + resultset.total +")")
  var table = $("<table id='search_result_table' style='width:100%'></table>")
  section_div.append(table)

  // Init global row
  table.append(search_build_result_row(label, 1, ""))

  for (i=0; i<resultset.data.length; i++) {
    table.append(search_build_result_row(label, 0, resultset.data[i], i))
  }
  return section_div;
}

function search_search() {
  var count=0;
  var search_query = $('#search_input').val();

  if (search_query == "") {
    return
  }

  $("#search_div").removeClass("searchidle");
  $("#search_div").addClass("searching");

  $("#search_result").empty();

  services_osvcgetrest("R_SEARCH", "", {"substring" : search_query}, function(jd) {
      var result = jd.data;
      for (d in result) {
        if (result[d].data.length>0 && search_get_menu(d) !== undefined) {
          response = search_build_result_view(d, result[d]);
          $("#search_result").append(response);
          count += result[d].data.length;
        }
      }

      if (count == 0) {
        var div = "<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>";
        $("#search_result").append(div);
      } else if (count == 1) {
        $('#search_result_table tr:first').remove();
        var td = $('#search_title_click0');
        td.trigger("click");
      }

      if (!$("#search_result").is(':visible')) {
        toggle('search_result');
      }
      $("#search_div").removeClass("searching");
      $("#search_div").addClass("searchidle");
      search_highlight($("#search_result"), search_query)
  });
}

function search_router(o, delay) {
  var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
  if (menu.is(":visible")) {
    filter_menu(null);
  } else if ($(".header [name=fset_selector_entries]").is(":visible")) {
    filter_fset_selector(null);
  } else {
    // close the search result panel if no search keyword
    if ($("#search_input").val() == "") {
      $("#search_result").hide("fold")
    } else {
      clearTimeout(o.timer);
      o.timer = setTimeout(search_search, delay);
    }
  }
}

function search(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)

  o.init = function init() {
    return search_init(o)
  }
  o.router = function router(delay) {
    return search_router(o, delay)
  }
  o.div.load("/init/static/views/search.html", function() {
    o.init()
  })

  return o
}

function search_init(o)
{
  o.timer = null

  o.div.i18n()
  o.e_search_div = $("#search_div")
  o.e_search_input = $("#search_input")

  o.e_search_div.on("keyup",function (event) {
    if (event.keyCode == 13) {
      o.router(0);
    }
  });
  o.e_search_input.on("keyup",function (event) {
    if (event.keyCode != 27) {
      o.router(1000);
    }
  });
}


function filter_menu(event) {
  var menu = $("#menu_menu");
  var text = $(".search").find("input").val();

  var reg = new RegExp(text, "i");
  menu.find(".menu_entry").each(function(){
    if ($(this).text().match(reg)) {
      $(this).show()
      $(this).parents(".menu_section").first().show()
    } else {
      $(this).hide()
    }
  })
  menu.find(".menu_section").each(function(){
    if ($(this).children("a").text().match(reg)) {
      $(this).find(".menu_entry").show()
      $(this).show()
    }
    n = $(this).find(".menu_entry:visible").length
    if (n == 0) {
      $(this).hide()
    }
  })
  var entries = menu.find(".menu_entry:visible")
  if (is_enter(event)) {
    if (menu.is(":visible") && (entries.length == 1)) {
      entries.effect("highlight")
      window.location = entries.attr("link");
    }
  }
  if (entries.length==0) {
    menu.append("<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>")
  } else {
    menu.find(".meta_not_found").remove()
  }
  search_highlight(menu, text)
}

function filter_fset_selector(event) {
  var div = $(".header [name=fset_selector_entries]")
  if (!div.is("[ready]")) {
    var timer = setTimeout(function(){filter_fset_selector(event)}, 500)
    return
  }
  var text = $(".search").find("input").val()
  var reg = new RegExp(text, "i");
  div.find(".menu_entry").each(function(){
    if ($(this).find("[name=title]").text().match(reg)) {
      $(this).show()
    } else {
      $(this).hide()
    }
  })
  var entries = div.find(".menu_entry:visible")
  if (entries.length==0) {
    div.append("<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>")
  } else {
    div.find(".meta_not_found").remove()
  }
  search_highlight(div, text)
}

function search_highlight(e, s) {
  // keep track of original texts
  if (e.children("[name=orig]").length == 0) {
    var cache = $("<div name='orig'></div>")
    cache.css({"display": "none"})
    e.find("*").each(function() {
      var clone = $(this).clone()
      clone.children().remove()
      if (clone.text().match(/^$/)) {
        return
      }
      var cache_entry = $("<div></div>")
      cache_entry.uniqueId()
      var id = cache_entry.attr("id")
      $(this).attr("highlight_id", id)
      cache_entry.html(clone.html())
      cache.append(cache_entry)
    })
    e.append(cache)
  }

  var regexp = new RegExp(s, 'ig');

  e.children("[name=orig]").children().each(function(){
    // restore orig
    var id = $(this).attr("id")
    var tgt = e.find("[highlight_id="+id+"]")
    tgt.find("[name=highlighted]").remove()
    var children = tgt.children().detach()

    tgt.empty()
    tgt.text($(this).text())

    if ((s != "") && $(this).text().match(regexp)) {
      var highlighted = $("<span name='highlighted'></span>")
      highlighted.html($(this).text().replace("<", "&lt;").replace(">", "&gt;").replace(regexp, function(x) {
        return '<span class="highlight_light">' + x + '</span>'
      }))
      tgt.text("")
      tgt.prepend(highlighted)
    }
    tgt.append(children)
  })
}
