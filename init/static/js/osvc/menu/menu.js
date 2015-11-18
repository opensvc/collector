

function menu_search_key()
{
	var menu =
	{
		"views" :
		[
			{
			  "title" : "dashboard",
			  "class" : "alert16",
			  "link" : "/init/dashboard/index" },
			{
			  "title" : "services",
			  "class" : "svc",
			  "link" : "/init/services/services" },
			{
			  "title" : "services_instances",
			  "class" : "svc",
			  "link" : "/init/default/svcmon" },
			{
			  "title" : "resources",
			  "class" : "svc",
			  "link" : "/init/resmon/resmon" },
			{
			  "title" : "app_info",
			  "class" : "svc",
			  "link" : "/init/appinfo/appinfo" },
			{
			  "title" : "nodes",
			  "class" : "node16",
			  "link" : "/init/nodes/nodes" },
			{
			  "title" : "tag_attachments",
			  "class" : "fa-tags",
			  "link" : "/init/tags/tagattach" },
			{
			  "title" : "actions",
			  "class" : "actions",
			  "link" : "/init/svcactions/svcactions" },
			{
			  "title" : "checks",
			  "class" : "check16",
			  "link" : "/init/checks/checks" },
			{
			  "title" : "packages",
			  "class" : "pkg16",
			  "link" : "/init/packages/packages" },
			{
			  "title" : "patches",
			  "class" : "patch",
			  "link" : "/init/patches/patches" },
			{
			  "title" : "networks",
			  "class" : "net16",
			  "link" : "/init/networks/networks" },
			{
			  "title" : "node_networks",
			  "class" : "net16",
			  "link" : "/init/nodenetworks/nodenetworks" },
			{
			  "title" : "node_san",
			  "class" : "net16",
			  "link" : "/init/nodesan/nodesan" },
			{
			  "title" : "san_switches",
			  "class" : "net16",
			  "link" : "/init/sanswitches/sanswitches" },
			{
			  "title" : "dns",
			  "class" : "net16",
			  "link" : "/init/dns/dns" },
			{
			  "title" : "saves",
			  "class" : "save16",
			  "link" : "/init/saves/saves" },
			{
			  "title" : "disks",
			  "class" : "hd16",
			  "link" : "/init/disks/disks" },
		],
		"compliance" :
		[
			{
			  "title" : "statut",
			  "class" : "check16",
			  "link" : "/init/compliance/comp_status" },
			{
			  "title" : "log",
			  "class" : "log16",
			  "link" : "/init/compliance/comp_log" },
			{
			  "title" : "modulesets",
			  "class" : "actions",
			  "link" : "/init/compliance/comp_modules" },
			{
			  "title" : "rulesets",
			  "class" : "comp16",
			  "link" : "/init/compliance/comp_rules" },
			{
			  "title" : "designer",
			  "class" : "wf16",
			  "link" : "/init/compliance/comp_admin?obj_filter=opensvc" },
			{
			  "title" : "nrulesets",
			  "class" : "node16",
			  "link" : "/init/compliance/comp_rulesets_nodes_attachment" },
			{
			  "title" : "node_modulesets",
			  "class" : "node16",
			  "link" : "/init/compliance/comp_modulesets_nodes" },
			{
			  "title" : "srulesets",
			  "class" : "svc",
			  "link" : "/init/compliance/comp_rulesets_services_attachment" },
			{
			  "title" : "service_modulesets",
			  "class" : "svc",
			  "link" : "/init/compliance/comp_modulesets_services" },
		],
		"statistic" :
		[
			{
			  "title" : "reports",
			  "class" : "spark16",
			  "link" : "/init/charts/reports" },
			{
			  "title" : "site",
			  "class" : "spark16",
			  "link" : "/init/stats/stats" },
			{
			  "title" : "compare",
			  "class" : "spark16",
			  "link" : "/init/stats/compare" },
			{
			  "title" : "os_lc",
			  "class" : "spark16",
			  "link" : "/init/lifecycle/lifecycle_os" },
			{
			  "title" : "availability",
			  "class" : "avail16",
			  "link" : "/init/svcmon_log/svcmon_log" },
		],
		"requests" :
		[
			{
			  "title" : "new_request",
			  "class" : "wf16",
			  "link" : "/init/forms/forms" },
			{
			  "title" : "a_t_m_t",
			  "class" : "wf16",
			  "link" : "/init/forms/workflows_assigned_to_me" },
			{
			  "title" : "p_t_a",
			  "class" : "wf16",
			  "link" : "/init/forms/workflows_pending_tiers_action" },
			{
			  "title" : "all_requests",
			  "class" : "wf16",
			  "link" : "/init/forms/workflows" },
		],
		"administration" :
		[
			{
			  "title" : "users",
			  "class" : "guys16",
			  "link" : "/init/users/users",
			  "secure" : ["Manager"] },
			{
			  "title" : "log",
			  "class" : "log16",
			  "link" : "/init/log/log" },
			{
			  "title" : "o_setup",
			  "class" : "obs16",
			  "link" : "/init/obsolescence/obsolescence_config" },
			{
			  "title" : "application",
			  "class" : "svc",
			  "link" : "/init/apps/apps" },
			{
			  "title" : "drpplan",
			  "class" : "drp16",
			  "link" : "/init/drplan/drplan" },
			{
			  "title" : "batchs",
			  "class" : "actions",
			  "link" : "/init/batchs/batchs",
			  "secure" : ["Manager"] },
			{
			  "title" : "billing",
			  "class" : "bill16",
			  "link" : "/init/billing/billing",
			  "secure" : ["Manager"] },
			{
			  "title" : "prov",
			  "class" : "prov",
			  "link" : "/init/provisioning/prov_admin",
			  "secure" : ["Manager","ProvManager"] },
			{
			  "title" : "filters",
			  "class" : "filter16",
			  "link" : "/init/compliance/comp_filters" },
			{
			  "title" : "forms",
			  "class" : "wf16",
			  "link" : "/init/forms/forms_admin" },
			{
			  "title" : "metrics",
			  "class" : "spark16",
			  "link" : "/init/charts/metrics_admin" },
			{
			  "title" : "charts",
			  "class" : "spark16",
			  "link" : "/init/charts/charts_admin" },
			{
			  "title" : "reports",
			  "class" : "spark16",
			  "link" : "/init/charts/reports_admin" },
			{
			  "title" : "tags",
			  "class" : "fa-tags",
			  "link" : "/init/tags/tags" },
		],
		"shortcuts" :
		[
			{
			  "title" : "filter_sel",
			  "class" : "",
			  "label" : "f",
			  "link" : "" },
			{
			  "title" : "link",
			  "class" : "",
			  "label" : "l",
			  "link" : "" },
			{
			  "title" : "nav",
			  "class" : "",
			  "label" : "n",
			  "link" : "" },
			{
			  "title" : "refresh",
			  "class" : "",
			  "label" : "r",
			  "link" : "" },
			{
			  "title" : "search",
			  "class" : "",
			  "label" : "s",
			  "link" : "" },
			{
			  "title" : "unfocus",
			  "class" : "",
			  "label" : "ESC",
			  "link" : "" },
			{
			  "title" : "rest_api",
			  "class" : "api",
			  "label" : "",
			  "link" : "/init/rest/doc" }
		],
	}
	return menu;
}

function menu(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)

  o.init = function init() {
    return menu_init(o)
  }

  o.menu_clicked = function menu_clicked() {
  	return menu_clicked(o);
  }

  o.div.load("/init/static/views/menu.html", function() {
    o.init()
  })

  return o
}

function menu_init(o)
{
  var timer;

  o.menu_div = $("#menu_menu");
  o.menu_clickable = $("#menu_top");

  menu_load_config(o);

  //Binding
  o.menu_clickable.on("click",function (event) {
  	menu_clicked(o);
  });
}

function menu_create_entry(o, title, entry)
{
	if (entry.secure !== undefined)
	{
		var sectest=0;
		services_ismemberof(entry.secure, function () {
			sectest = 1;
		});
		if (sectest==0) return;
	}

	var titre = i18n.t("menu."+title+ "." + entry.title +".title");
	var text = i18n.t("menu."+title+ "." + entry.title +".text");

	var div_entry = "<div id='menu_" + title + "_" + entry.title + "' class='menu_entry clickable' link='" + entry.link + "'>";

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
			$("menu_menu").hide("fold");
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
		div_section += menu_create_entry(o,title, section[i]);
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
	o.menu_div.toggle("fold", function()
	{
		$("#search_input").focus();
	});
}
