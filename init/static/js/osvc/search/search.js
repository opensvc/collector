//MD
//20102015

function search_get_menu(fk)
{
  var menu = {
    "users": {
        "tab" : "1",
        "keys": [ {"key" : "fullname"} ], 
        "class": "s_guys48",
        "subclass" : "meta_username clickable",
        "link" : [
          { "user" : [ {"class" : "guy16"},{"link" : "/init/users/users?clear_filters=true&users_f_fullname="} ] },
          { "logs" : [ {"class" : "guy16"},{"link" : "/init/log/log?clear_filters=true&log_f_log_user="} ] },
          { "apps" : [ {"class" : "guy16"},{"link" : "/init/apps/apps?clear_filters=true&apps_f_responsibles="} ] },
           ],
    }, 
    "safe_files": {
        "tab" : "0",
        "keys": [ {"key" : "files_id"} ], 
        "class": "s_guys48",
        "subclass" : "meta_username",
        "link" : [],
    },  
    "disks": {
        "tab" : "0",
        "keys": [ {"key" : "disk_id"} ], 
        "class": "s_disk48",
        "subclass" : "meta_app",
        "link" : [
          { "disk info" : [ {"class" : "hd16"},{"link" : "/init/disks/disks?clear_filters=true&disks_f_disk_id="} ] },
        ],
    }, 
    "apps": {
        "tab" : "0",
        "keys": [ {"key" : "app"} ], 
        "class": "s_svc48",
        "subclass" : "",
        "link" : [
         { "nodes" : [ {"class" : "hw16"},{"link" : "/init/nodes/nodes?clear_filters=true&nodes_f_project="} ] },
         { "status" : [ {"class" : "svc"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_svc_app="} ] },
         { "disk_info" : [ {"class" : "hd16"},{"link" : "/init/disks/disks?clear_filters=true&disks_f_app="} ] },
         { "availability" : [ {"class" : "avail16"},{"link" : "/init/svcmon_log/svcmon_log?clear_filters=true&svcmon_log_f_svc_app="} ] },
         { "app" : [ {"class" : "svc"},{"link" : "/init/apps/apps?clear_filters=true&apps_f_app="} ] },
        ],
    },  
    "ips": {
        "tab" : "0",
        "keys": [ {"key" : "addr"},{"key" : "nodename"} ], 
        "class": "s_net48",
        "subclass" : "meta_username",
        "link" : [
          { "nodes" : [ {"class" : "hw16"},{"link" : "/init/nodes/nodes?clear_filters=true&nodes_f_nodename="} ] },
          { "dashboard" : [ {"class" : "alert16"},{"link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_nodename="} ] },
          { "services" : [ {"class" : "svc"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_nodname="} ] },
          { "resources" : [ {"class" : "svc"},{"link" : "/init/resmon/resmon?clear_filters=true&resmon_f_nodename="} ] },
          { "appinfo" : [ {"class" : "svc"},{"link" : "/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_nodename="} ] },
          { "action" : [ {"class" : "action16"},{"link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_hostname="} ] },
          { "checks" : [ {"class" : "check16"},{"link" : "/init/checks/checks?clear_filters=true&checks_f_chk_nodename="} ] },
          { "packages" : [ {"class" : "pkg16"},{"link" : "/init/packages/packages?clear_filters=true&packages_f_nodename="} ] },
          { "network" : [ {"class" : "net16"},{"link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_nodename="} ] },
          { "san" : [ {"class" : "net16"},{"link" : "/init/nodesan/nodesan?clear_filters=true&nodesan_f_nodename="} ] },
          { "disks" : [ {"class" : "hd16"},{"link" : "/init/disks/disks?clear_filters=true&disks_f_disk_nodename="} ] },
          { "saves" : [ {"class" : "cd16"},{"link" : "/init/saves/saves?clear_filters=true&saves_f_save_nodename="} ] },
          { "compliance_status" : [ {"class" : "comp16"},{"link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_nodename="} ] },
          { "compliance_log" : [ {"class" : "log16"},{"link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_nodename="} ] },
          { "logs" : [ {"class" : "log16"},{"link" : "/init/log/log?clear_filters=true&log_f_log_nodename="} ] },
        ],
        "special_header_link" : [
          { "nodes_net" : [ {"class" : "hw16"},{"link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_addr="} ] },
        ],
        "key_separator" : "@",
        "link_value" : "nodename",
    },   
    "groups": {
        "tab" : "1",
        "keys": [ {"key" : "role"} ], 
        "class": "s_guys48",
        "subclass" : "meta_username clickable",
        "link" : [
          { "nodes" : [ {"class" : "hw16"},{"link" : "/init/nodes/nodes?clear_filters=true&nodes_f_team_responsible="} ] },
          { "apps" : [ {"class" : "svc"},{"link" : "/init/apps/apps?clear_filters=true&apps_f_roles="} ] },
          { "checks" : [ {"class" : "check16"},{"link" : "/init/checks/checks?clear_filters=true&checks_f_team_responsible="} ] },
          { "compliance_status" : [ {"class" : "comp16"},{"link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_team_responsible="} ] },
        ],
    },   
    "services": {
        "tab" : "1",
        "keys": [ {"key" : "svc_name"} ], 
        "class": "s_svc48",
        "subclass" : "meta_svcname clickable",
        "link" : [
          { "dashboard" : [ {"class" : "alert16"},{"link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_svcname="} ] },
          { "status" : [ {"class" : "alert16"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_svcname="} ] },
          { "resources" : [ {"class" : "svc"},{"link" : "/init/resmon/resmon?clear_filters=true&resmon_f_svcname="} ] },
          { "appinfo" : [ {"class" : "alert16"},{"link" : "/init/dashboard/index?clear_/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_svcname="} ] },
          { "action" : [ {"class" : "action16"},{"link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_svcname="} ] },
          { "checks" : [ {"class" : "check16"},{"link" : "/init/checks/checks?clear_filters=true&checks_f_chk_svcname="} ] },
          { "disks" : [ {"class" : "hd16"},{"link" : "/init/disks/disks?clear_filters=true&disks_f_disk_svcname="} ] },
          { "saves" : [ {"class" : "cd16"},{"link" : "/init/saves/saves?clear_filters=true&saves_f_save_svcname="} ] },
          { "compliance_status" : [ {"class" : "comp16"},{"link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_svcname="} ] },
          { "compliance_log" : [ {"class" : "log16"},{"link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_svcname="} ] },
          { "availability" : [ {"class" : "avail16"},{"link" : "/init/svcmon_log/svcmon_log?clear_filters=true&svcmon_log_f_svc_name="} ] },
          { "logs" : [ {"class" : "log16"},{"link" : "/init/log/log?clear_filters=true&log_f_log_svcname=atomic71.opensvc.com="} ] },
        ],
    },    
    "nodes": {
        "tab" : "1",
        "keys": [ {"key" : "nodename"} ], 
        "class": "s_node48",
        "subclass" : "meta_nodename clickable",
        "link" : [          
          { "nodes" : [ {"class" : "hw16"},{"link" : "/init/nodes/nodes?clear_filters=true&nodes_f_nodename="} ] },
          { "dashboard" : [ {"class" : "alert16"},{"link" : "/init/dashboard/index?clear_filters=true&dashboard_f_dash_nodename="} ] },
          { "services" : [ {"class" : "svc"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_nodname="} ] },
          { "resources" : [ {"class" : "svc"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_nodname="} ] },
          { "appinfo" : [ {"class" : "svc"},{"link" : "/init/appinfo/appinfo?clear_filters=true&appinfo_f_app_nodename="} ] },
          { "action" : [ {"class" : "action16"},{"link" : "/init/svcactions/svcactions?clear_filters=true&actions_f_hostname="} ] },
          { "checks" : [ {"class" : "check16"},{"link" : "/init/checks/checks?clear_filters=true&checks_f_chk_nodename="} ] },
          { "packages" : [ {"class" : "pkg16"},{"link" : "/init/packages/packages?clear_filters=true&packages_f_nodename="} ] },
          { "network" : [ {"class" : "net16"},{"link" : "/init/nodenetworks/nodenetworks?clear_filters=true&nodenetworks_f_nodename="} ] },
          { "san" : [ {"class" : "net16"},{"link" : "/init/nodesan/nodesan?clear_filters=true&nodesan_f_nodename="} ] },
          { "disks" : [ {"class" : "hd16"},{"link" : "/init/disks/disks?clear_filters=true&disks_f_disk_nodename="} ] },
          { "compliance_status" : [ {"class" : "comp16"},{"link" : "/init/compliance/comp_status?clear_filters=true&cs0_f_run_nodename="} ] },
          { "compliance_log" : [ {"class" : "log16"},{"link" : "/init/compliance/comp_log?clear_filters=true&comp_log_f_run_nodename="} ] },
          { "logs" : [ {"class" : "log16"},{"link" : "/init/log/log?clear_filters=true&log_f_log_nodename="} ] },
        ],
    },   
    "filtersets": {
        "tab" : "1",
        "keys": [ {"key" : "fset_name"} ], 
        "class": "s_filter48",
        "subclass" : "meta_username clickable",
        "link" : [
          { "designer" : [ {"class" : "wf16"},{"link" : "/init/compliance/comp_admin?obj_filter="} ] },
          { "availability" : [ {"class" : "avail16"},{"link" : "/init/svcmon_log/svcmon_log?clear_filters=true&svcmon_log_f_mon_vmname="} ] },
        ],
    },   
    "vms": {
        "tab" : "0",
        "keys": [ {"key" : "mon_vmname"} ], 
        "class": "s_disk48",
        "subclass" : "meta_nodename",
        "link" : [
          { "status" : [ {"class" : "svc"},{"link" : "/init/default/svcmon?clear_filters=true&svcmon_f_mon_vmname="} ] },
          { "filterset" : [ {"class" : "filter16"},{"link" : "/init/compliance/comp_filters?clear_filters=true&ajax_comp_filtersets_f_fset_name="} ] },
        ],
    },   
  }
  return menu[fk];
}

function search_build_result_row(label, first, res)
{
  var title ="";
  var link_value ="";
  var row = "<tr><td " + "class='" + search_get_menu(label).class + "' ></td>";
  // Title construction
  if (first==1) // first header with %___%
    {
      title = "%"+ $('#search_input').val() +"%";
      row += "<td><p class='highlight_light'>%" + $('#search_input').val() + "%</p>";
    }
  else 
    {
      for (ki=0;ki<search_get_menu(label).keys.length;ki++)
      {
        if (ki>=1) title += " " + search_get_menu(label).key_separator + " ";
        title += res[search_get_menu(label).keys[ki].key];
        // Handle special link variable
        if (search_get_menu(label).link_value != undefined && 
          search_get_menu(label).link_value == search_get_menu(label).keys[ki].key)
          link_value = res[search_get_menu(label).keys[ki].key];
      }

      row += "<td><p class='" + search_get_menu(label).subclass + "' ";
      if (search_get_menu(label).tab == "1") 
        row += "id='search_title_click' onclick=\"search_show_tab(this,'" + label + "', '"+ link_value +"')\""; 
      row += ">" + title + "</p>";
    }

  if (link_value=="") link_value=title;  

  // Link construction : special condition for first element if present
  if (first==1  && search_get_menu(label).special_header_link != undefined)
    link = search_get_menu(label).special_header_link;
  else
    link = search_get_menu(label).link;

  for(j=0;j<link.length;j++)
  {
    for (l in link[j])
      row += "<a class='" + link[j][l][0].class + "' href='"+ link[j][l][1].link + link_value + "'>"+ i18n.t("search.menu_link."+ l) +"</a>";
  }
  row +="</td></tr>";
  return row;
}

function search_build_result_view(label, resultset)
{
  var section_div = "<div id='" + label + "' class='menu_section'>" +  i18n.t("search.menu_header.title_"+label) +
  " (" + resultset.total +")";
  var table = "<table id='search_result_table'>"

  // Init global row
  table += search_build_result_row(label,1,"");

  for (i=0;i<resultset.data.length;i++)
  {
    table += search_build_result_row(label,0,resultset.data[i]);
    table += "<tr><td name='extra' colspan='2'></td></tr>";
  }

  section_div += table;
  section_div += "</table></div>";
  return section_div;
}

function search_search()
{
  var count=0;
  var search_query = $('#search_input').val();
  if (search_query == "") return;

  $("#search_div").removeClass("searchidle");
  $("#search_div").addClass("searching");

  $("#search_result").empty();

  //var param = "substring="+search_query;
  services_osvcgetrest("R_SEARCH","",{"substring" : search_query}, function(jd) {
      var result = jd.data;
      for (d in result)
      {
        if (result[d].data.length>0)
        {
          response = search_build_result_view(d,result[d]);
          $("#search_result").append(response);
          count += result[d].data.length;
        }
      }

      if (count==0)
      {
        var div = "<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>";
        $("#search_result").append(div);
      }
      else if (count==1)
      {
        $('#search_result_table tr:first').remove();
        var td = $('#search_title_click');
        td.trigger("click");
      }

      if (!$("#search_result").is(':visible')) toggle('search_result');
      $("#search_div").removeClass("searching");
      $("#search_div").addClass("searchidle");
  });
}

function search_routing(delay)
{
  var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
  if (menu.is(":visible")) 
  {
    filter_menu();
  } 
  else {
    clearTimeout(timer);
    timer = setTimeout(search_search,delay);
  }
}

function search_init()
{
  var timer;

  $('#search_div').on("keyup",function (event) {
    if (event.keyCode == 13) 
      search_routing(0);
  });

  $("#search_input").on("keyup",function (event) {
    if (event.keyCode !=27)
    {
      search_routing(1000);
    }
  });
}

function search_show_tab(item, tab, param)
{
  var value = $(item).text();
  var _id = "sextra_" + value.replace(/[ \.-]/g, '_');
  var d = "<div id='" + _id + "' class='searchtab hidden'></div>";
  $(item).parents('table').first().find("[name=extra]").html(d);
  if (tab=="users")
    var _url = $(location).attr("origin") + "/init/ajax_user/ajax_user?username=" + value + "&rowid=" + _id;
  else if (tab=="services")
    var _url = $(location).attr("origin") + "/init/default/ajax_service?node="+value+"&rowid="+_id;
  else if (tab=="nodes")
    var _url = $(location).attr("origin") + "/init/ajax_node/ajax_node?node="+value+"&rowid="+_id;
  else if (tab=="groups")
    var _url = $(location).attr("origin") + "/init/ajax_group/ajax_group?groupname="+value+"&rowid="+_id;
  else if (tab=="filtersets")
    var _url = $(location).attr("origin") + "/init/compliance/json_tree_action?operation=show&obj_type=filterset&obj_id="+value;
  sync_ajax(_url, [], _id, function() {});
  $("#" + _id).show();
}

function filter_menu() {
  var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu")
  var text = searchbox = $(".search").find("input").val()
  var reg = new RegExp(text, "i");
  menu.find(".menu_entry").each(function(){
    if (($(this).parents(".menu_section").children("a").text().match(reg)) || ($(this).text().match(reg))) {
      $(this).show()
      $(this).parents(".menu_section").first().show()
    } else {
      $(this).hide()
    }
  })
  menu.find(".menu_section").each(function(){
    n = $(this).find(".menu_entry:visible").length
    if (n == 0) {
      $(this).hide()
    }
  })
  var entries = menu.find(".menu_entry:visible")
  if (is_enter(event)) {
    if (menu.is(":visible") && (entries.length == 1)) {
      entries.effect("highlight")
      window.location = entries.children("a").attr("href")
    }
  }
  if (entries.length==0) {
    menu.append("<div class='menu_entry meta_not_found'><a><div class='question48'>"+T("No menu entry found matching filter")+"</div></a></div>")
  } else {
    menu.find(".meta_not_found").remove()
  }
}
