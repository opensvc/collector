

function menu_search_key()
{
	var menu =
	{
		"views" :
		[
			{
			  "title" : "dashboard",
			  "class" : "alert16",
			  "id" : "view-dashboard",
			  "link" : "/init/dashboard/index" },
			{
			  "title" : "services",
			  "class" : "svc",
			  "id" : "view-services",
			  "link" : "/init/services/services" },
			{
			  "title" : "services_instances",
			  "class" : "svc",
			  "id" : "view-service-instances",
			  "link" : "/init/default/svcmon" },
			{
			  "title" : "resources",
			  "class" : "svc",
			  "id" : "view-resources",
			  "link" : "/init/resmon/resmon" },
			{
			  "title" : "app_info",
			  "class" : "svc",
			  "id" : "view-appinfo",
			  "link" : "/init/appinfo/appinfo" },
			{
			  "title" : "nodes",
			  "class" : "node16",
			  "id" : "view-nodes",
			  "link" : "/init/nodes/nodes" },
			{
			  "title" : "tag_attachments",
			  "class" : "fa-tags",
			  "id" : "view-tagattach",
			  "link" : "/init/tags/tagattach" },
			{
			  "title" : "actions",
			  "class" : "actions",
			  "id" : "view-actions",
			  "link" : "/init/svcactions/svcactions" },
			{
			  "title" : "checks",
			  "class" : "check16",
			  "id" : "view-checks",
			  "link" : "/init/checks/checks" },
			{
			  "title" : "packages",
			  "class" : "pkg16",
			  "id" : "view-pkg",
			  "link" : "/init/packages/packages" },
			{
			  "title" : "patches",
			  "class" : "patch",
			  "id" : "view-patch",
			  "link" : "/init/patches/patches" },
			{
			  "title" : "networks",
			  "class" : "net16",
			  "id" : "view-net",
			  "link" : "/init/networks/networks" },
			{
			  "title" : "node_networks",
			  "class" : "net16",
			  "id" : "view-node-net",
			  "link" : "/init/nodenetworks/nodenetworks" },
			{
			  "title" : "node_san",
			  "class" : "net16",
			  "id" : "view-node-san",
			  "link" : "/init/nodesan/nodesan" },
			{
			  "title" : "san_switches",
			  "class" : "net16",
			  "id" : "view-san",
			  "link" : "/init/sanswitches/sanswitches" },
			{
			  "title" : "dns",
			  "class" : "net16",
			  "id" : "view-dns",
			  "link" : "/init/dns/dns" },
			{
			  "title" : "saves",
			  "class" : "save16",
			  "id" : "view-saves",
			  "link" : "/init/saves/saves" },
			{
			  "title" : "disks",
			  "class" : "hd16",
			  "id" : "view-disks",
			  "link" : "/init/disks/disks" },
		],
		"compliance" :
		[
			{
			  "title" : "statut",
			  "class" : "check16",
			  "id" : "comp-status",
			  "link" : "/init/compliance/comp_status" },
			{
			  "title" : "log",
			  "class" : "log16",
			  "id" : "comp-log",
			  "link" : "/init/compliance/comp_log" },
			{
			  "title" : "modulesets",
			  "class" : "actions",
			  "id" : "comp-modsets",
			  "link" : "/init/compliance/comp_modules" },
			{
			  "title" : "rulesets",
			  "class" : "comp16",
			  "id" : "comp-rsets",
			  "link" : "/init/compliance/comp_rules" },
			{
			  "title" : "designer",
			  "class" : "wf16",
			  "id" : "comp-designer",
			  "link" : "/init/compliance/comp_admin?obj_filter=opensvc" },
			{
			  "title" : "nrulesets",
			  "class" : "node16",
			  "id" : "comp-node-rset",
			  "link" : "/init/compliance/comp_rulesets_nodes_attachment" },
			{
			  "title" : "node_modulesets",
			  "class" : "node16",
			  "id" : "comp-node-modset",
			  "link" : "/init/compliance/comp_modulesets_nodes" },
			{
			  "title" : "srulesets",
			  "class" : "svc",
			  "id" : "comp-svc-rset",
			  "link" : "/init/compliance/comp_rulesets_services_attachment" },
			{
			  "title" : "service_modulesets",
			  "class" : "svc",
			  "id" : "comp-svc-modset",
			  "link" : "/init/compliance/comp_modulesets_services" },
		],
		"statistic" :
		[
			{
			  "title" : "reports",
			  "class" : "spark16",
			  "id" : "stat-reports",
			  "link" : "/init/charts/reports" },
			{
			  "title" : "site",
			  "class" : "spark16",
			  "id" : "stat-site",
			  "link" : "/init/stats/stats" },
			{
			  "title" : "compare",
			  "class" : "spark16",
			  "id" : "stat-compare",
			  "link" : "/init/stats/compare" },
			{
			  "title" : "os_lc",
			  "class" : "spark16",
			  "id" : "stat-os-lifecycle",
			  "link" : "/init/lifecycle/lifecycle_os" },
			{
			  "title" : "availability",
			  "class" : "avail16",
			  "id" : "stat-avail",
			  "link" : "/init/svcmon_log/svcmon_log" },
		],
		"requests" :
		[
			{
			  "title" : "new_request",
			  "class" : "wf16",
			  "id" : "req-new",
			  "link" : "/init/forms/forms" },
			{
			  "title" : "a_t_m_t",
			  "class" : "wf16",
			  "id" : "req-pending-my",
			  "link" : "/init/forms/workflows_assigned_to_me" },
			{
			  "title" : "p_t_a",
			  "class" : "wf16",
			  "id" : "req-pending-tiers",
			  "link" : "/init/forms/workflows_pending_tiers_action" },
			{
			  "title" : "all_requests",
			  "class" : "wf16",
			  "id" : "req-all",
			  "link" : "/init/forms/workflows" },
		],
		"administration" :
		[
			{
			  "title" : "users",
			  "class" : "guys16",
			  "id" : "adm-usr",
			  "link" : "/init/users/users",
			  "secure" : ["Manager"] },
			{
			  "title" : "log",
			  "class" : "log16",
			  "id" : "adm-log",
			  "link" : "/init/log/log" },
			{
			  "title" : "o_setup",
			  "class" : "obs16",
			  "id" : "adm-obs",
			  "link" : "/init/obsolescence/obsolescence_config" },
			{
			  "title" : "application",
			  "class" : "svc",
			  "id" : "adm-app",
			  "link" : "/init/apps/apps" },
			{
			  "title" : "drpplan",
			  "class" : "drp16",
			  "id" : "adm-drp",
			  "link" : "/init/drplan/drplan" },
			{
			  "title" : "batchs",
			  "class" : "actions",
			  "id" : "adm-batch",
			  "link" : "/init/batchs/batchs",
			  "secure" : ["Manager"] },
			{
			  "title" : "billing",
			  "class" : "bill16",
			  "id" : "adm-bill",
			  "link" : "/init/billing/billing",
			  "secure" : ["Manager"] },
			{
			  "title" : "prov",
			  "class" : "prov",
			  "id" : "adm-prov",
			  "link" : "/init/provisioning/prov_admin",
			  "secure" : ["Manager","ProvManager"] },
			{
			  "title" : "filters",
			  "class" : "filter16",
			  "link" : "/init/compliance/comp_filters" },
			{
			  "title" : "forms",
			  "class" : "wf16",
			  "id" : "adm-forms",
			  "link" : "/init/forms/forms_admin" },
			{
			  "title" : "metrics",
			  "class" : "spark16",
			  "id" : "adm-metrics",
			  "link" : "/init/charts/metrics_admin" },
			{
			  "title" : "charts",
			  "class" : "spark16",
			  "id" : "adm-charts",
			  "link" : "/init/charts/charts_admin" },
			{
			  "title" : "reports",
			  "class" : "spark16",
			  "id" : "adm-reports",
			  "link" : "/init/charts/reports_admin" },
			{
			  "title" : "tags",
			  "class" : "fa-tags",
			  "id" : "adm-tags",
			  "link" : "/init/tags/tags" },
		],
		"shortcuts" :
		[
			{
			  "title" : "filter_sel",
			  "class" : "",
			  "id" : "key-f",
			  "label" : "f",
			  "link" : "" },
			{
			  "title" : "link",
			  "class" : "",
			  "id" : "key-l",
			  "label" : "l",
			  "link" : "" },
			{
			  "title" : "nav",
			  "class" : "",
			  "id" : "key-n",
			  "label" : "n",
			  "link" : "" },
			{
			  "title" : "refresh",
			  "class" : "",
			  "id" : "key-r",
			  "label" : "r",
			  "link" : "" },
			{
			  "title" : "search",
			  "class" : "",
			  "id" : "key-s",
			  "label" : "s",
			  "link" : "" },
			{
			  "title" : "unfocus",
			  "class" : "",
			  "id" : "key-esc",
			  "label" : "ESC",
			  "link" : "" },
			{
			  "title" : "rest_api",
			  "class" : "api",
			  "label" : "",
			  "id" : "help-api",
			  "link" : "/init/rest/doc" }
		],
	}
	return menu;
}

function menu(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)

  o.init = function() {
    return menu_init(o)
  }

  o.clicked = function() {
    return menu_clicked(o);
  }

  o.div.load("/init/static/views/menu.html", function() {
    params = {
      "stats": "menu_entry",
      "props": "menu_entry",
      "limit": "0"
    }
    services_osvcgetrest("R_USER_HIDDEN_MENU_ENTRIES", ["self"], params, function(jd) {
      /*
	{
	    "data": {
		"menu_entry": {
		    "key-s": 1, 
		    "key-r": 1, 
		    "key-esc": 1, 
		    "key-l": 3
		}
	    }
	}
      */
      if (jd.error && (jd.error.length > 0)) {
        $(".flash").show("blind").html(services_error_fmt(jd))
      }
      o.hidden = []
      var ref_count = 0
      for (var i=0; i<_groups.length; i++) {
        var g = _groups[i]
        if (g.role.indexOf("user_") == 0) {
          continue
        }
        if (g.privilege == true) {
          continue
        }
        ref_count++
      }
      for (key in jd.data.menu_entry) {
        if (jd.data.menu_entry[key] == ref_count) {
          o.hidden.push(key)
        }
      }
      console.log("hidden menu entries:", o.hidden)
      o.init()
    })
  })

  return o
}

function menu_init(o)
{
  var timer;

  o.menu_div = $("#menu_menu");
  o.menu_clickable = $("#menu_top > ul");

  menu_load_config(o);

  //Binding
  o.menu_clickable.on("click", function (event) {
    o.clicked();
  });
}

function menu_create_entry(o, section, entry)
{
	if (o.hidden.indexOf(entry.id) >= 0) {
		return
	}
	if (entry.secure && !services_ismemberof(entry.secure)) {
		return
	}
	return menu_create_entry_s(section, entry)
}
function menu_create_entry_s(section, entry)
{
	var titre = i18n.t("menu."+section+ "." + entry.title +".title");
	var text = i18n.t("menu."+section+ "." + entry.title +".text");

	var div_entry = "<div id='menu_" + section + "_" + entry.title + "' class='menu_entry clickable' link='" + entry.link + "'>";

	div_entry += "<div class='menu_box'>";

	var cl = entry.class;
	if (cl != "")
		div_entry += "<div class='menu_icon " + entry.class +  "'></div>";
	else
		div_entry += "<div class='menu_icon'>" + entry.label +  "</div>";
	div_entry += "<div>";
	div_entry += "<div class='menu_title'>" + titre + "</div>";
	div_entry += "<div class='menu_subtitle'>" + text + "</div>";

	div_entry +="</div></div></div>";
	return div_entry;
}

function menu_bind_sub_link(o, title)
{
        var section = menu_search_key()[title]
	for(i=0;i<section.length;i++)
	{
		$("#menu_"+title+"_"+section[i].title).on("click",function (event) {
	  		event.preventDefault()
			var href = $(this).attr("link");
			if (!href) {
			  return
			}
			if (event.ctrlKey) {
			  window.open(href, "_blank")
			  return
			}
			o.menu_div.hide("fold");
			$("#search_input").val("").blur()
			app_load_href(href)

			// update browser url and history
			if (!_badIE) history.pushState({}, "", href)
	  	});
	}
}

function menu_create_section(o, title)
{
        var section = menu_search_key()[title]
	var div_section = "<div id='menu_section' class='menu_section' style='display: block;'><a>";
	div_section += i18n.t("menu."+title+".title") + "</a><div>";

	for (i=0;i<section.length;i++)
	{
		var s = menu_create_entry(o,title, section[i]);
                if (!s) {
                  continue
                }
		div_section += s
	}

	div_section += "</div></div>";
	return div_section;
}

function menu_load_config(o)
{
	for (d in menu_search_key())
	{
		var result = menu_create_section(o, d);
		o.menu_div.append(result);
		menu_bind_sub_link(o, d);
	}
}

function menu_clicked(o)
{
	if (!o.menu_div.is(":visible")) {
		o.menu_div.stop().show("fold", function(){filter_menu()})
		$("#search_input").val("").focus();
	} else {
		o.menu_div.stop().hide("fold")
	}
}
