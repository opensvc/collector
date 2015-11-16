

function menu_search_key()
{
	var menu = 
	{
		"Views" : 
		[
			{ 
			  "title" : "Dashboard",
			  "class" : "alert16",
			  "text" : "Current issues on nodes and services",
			  "link" : "/dashboard/index" },
			{ 
			  "title" : "Services",
			  "class" : "svc",
			  "text" : "Services information and status",
			  "link" : "/init/services/services" },
			{ 
			  "title" : "Services Instances",
			  "class" : "svc",
			  "text" : "Service instances status",
			  "link" : "/init/default/svcmon" },
			{ 
			  "title" : "Resources",
			  "class" : "svc",
			  "class" : "Service resources status",
			  "link" : "/init/resmon/resmon" },
			{ 
			  "title" : "App Info",
			  "class" : "svc",
			  "text" : "Service 'app' resources key:val store",
			  "link" : "/init/appinfo/appinfo" },
			{ 
			  "title" : "Nodes",
			  "class" : "node16",
			  "text" : "Technical and organizational info",
			  "link" : "/init/nodes/nodes" },
			{ 
			  "title" : "Tag Attachments",
			  "class" : "fa-tags",
			  "text" : "Tags attached to nodes and services",
			  "link" : "/init/tags/tagattach" },
			{ 
			  "title" : "Actions",
			  "class" : "actions",
			  "text" : "Service actions log",
			  "link" : "/init/svcactions/svcactions" },
			{ 
			  "title" : "Checks",
			  "class" : "check16",
			  "text" : "Nodes health monitoring",
			  "link" : "/init/checks/checks" },
			{ 
			  "title" : "Packages",
			  "class" : "pkg16",
			  "text" : "All packages installed on nodes",
			  "link" : "/init/packages/packages" },
			{ 
			  "title" : "Patches",
			  "class" : "patch",
			  "text" : "All patches installed on nodes",
			  "link" : "/init/patches/patches" },
			{ 
			  "title" : "Networks",
			  "class" : "net16",
			  "text" : "Known subnets, gateways, vlans, ...",
			  "link" : "/init/networks/networks" },
			{ 
			  "title" : "Node Networks",
			  "class" : "net16",
			  "text" : "Node ips with their network information",
			  "link" : "/init/nodenetworks/nodenetworks" },
			{ 
			  "title" : "Node SAN",
			  "class" : "net16",
			  "text" : "Node SAN ports with their fabric information",
			  "link" : "/init/nodesan/nodesan" },
			{ 
			  "title" : "SAN switches",
			  "class" : "net16",
			  "text" : "Ports id, state, remote ports",
			  "link" : "/init/sanswitches/sanswitches" },
			{ 
			  "title" : "Domain Name Service",
			  "class" : "net16",
			  "text" : "Internal dns zones and records",
			  "link" : "/init/dns/dns" },
			{ 
			  "title" : "Saves",
			  "class" : "save16",
			  "text" : "Backup servers aggregated index",
			  "link" : "/init/saves/saves" },
			{ 
			  "title" : "Disks",
			  "class" : "hd16",
			  "text" : "All known disks with their array information",
			  "link" : "/init/disks/disks" },
		],
		"Compliance" : 
		[
			{ 
			  "title" : "Status",
			  "class" : "check16",
			  "text" : "Nodes and service last configuration checks",
			  "link" : "/init/compliance/comp_status" },
			{ 
			  "title" : "Log",
			  "class" : "log16",
			  "text" : "All configuration checks and fixes",
			  "link" : "/init/compliance/comp_log" },
			{ 
			  "title" : "Modulesets",
			  "class" : "actions",
			  "text" : "Search-optimized modules grouping view",
			  "link" : "/init/compliance/comp_modules" },
			{ 
			  "title" : "Status",
			  "class" : "comp16",
			  "text" : "Search-optimized target configurations view",
			  "link" : "/init/compliance/comp_rules" },
			{ 
			  "title" : "Designer",
			  "class" : "wf16",
			  "text" : "Creation-optimized configuration targets tool",
			  "link" : "/init/compliance/comp_admin?obj_filter=opensvc" },
			{ 
			  "title" : "Node rulesets",
			  "class" : "node16",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_rulesets_nodes_attachment" },
			{ 
			  "title" : "Service rulesets",
			  "class" : "svc",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_rulesets_services_attachment" },
			{ 
			  "title" : "Service modulesets",
			  "class" : "svc",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_modulesets_services" },
			{ 
			  "title" : "Node modulesets",
			  "class" : "node16",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_modulesets_nodes" },
		],
		"Statistic" : 
		[
			{ 
			  "title" : "Reports",
			  "class" : "spark16",
			  "text" : "User-defined reports",
			  "link" : "/init/charts/reports" },
			{ 
			  "title" : "Site",
			  "class" : "spark16",
			  "text" : "Pre-defined site report",
			  "link" : "/init/stats/stats" },
			{ 
			  "title" : "Compare",
			  "class" : "spark16",
			  "text" : "Compare node and service subsets evolution",
			  "link" : "/init/stats/compare" },
			{ 
			  "title" : "Os lifecycle",
			  "class" : "spark16",
			  "text" : "Operating systems dispatch evolution",
			  "link" : "/init/lifecycle/lifecycle_os" },
			{ 
			  "title" : "Availability",
			  "class" : "avail16",
			  "text" : "Service outage timelines",
			  "link" : "/init/svcmon_log/svcmon_log" },
			{ 
			  "title" : "Node rulesets",
			  "class" : "node16",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_rulesets_nodes_attachment" },
			{ 
			  "title" : "Service rulesets",
			  "class" : "svc",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_rulesets_services_attachment" },
			{ 
			  "title" : "Service modulesets",
			  "class" : "svc",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_modulesets_services" },
			{ 
			  "title" : "Node modulesets",
			  "class" : "node16",
			  "text" : "Mass attach and detach tool",
			  "link" : "/init/compliance/comp_modulesets_nodes" },
		],
		"Requests" : 
		[
			{ 
			  "title" : "New request",
			  "class" : "wf16",
			  "text" : "Start a new workflow or orchestration",
			  "link" : "/init/forms/forms" },
			{ 
			  "title" : "Assigned to my team",
			  "class" : "wf16",
			  "text" : "Workflows waiting for action from my team",
			  "link" : "/init/forms/workflows_assigned_to_me" },
			{ 
			  "title" : "Pending tiers action",
			  "class" : "wf16",
			  "text" : "Workflows started by my team waiting action from a tier",
			  "link" : "/init/forms/workflows_pending_tiers_action" },
			{ 
			  "title" : "All requests",
			  "class" : "wf16",
			  "text" : "Workflow and orchestration history",
			  "link" : "/init/forms/workflows" },
		],
		"Administration" : 
		[
			{ 
			  "title" : "Users",
			  "class" : "guys16",
			  "text" : "Users and group administration",
			  "link" : "/init/users/users",
			  "secure" : ["Manager"] },
			{ 
			  "title" : "Log",
			  "class" : "log16",
			  "text" : "Collector events log",
			  "link" : "/init/log/log" },
			{ 
			  "title" : "Obsolescence setup",
			  "class" : "obs16",
			  "text" : "Set server models and os releases obsolescence dates",
			  "link" : "/init/obsolescence/obsolescence_config" },
			{ 
			  "title" : "Applications",
			  "class" : "svc",
			  "text" : "Application codes assigned to nodes and services",
			  "link" : "/init/apps/apps" },
			{ 
			  "title" : "Drplan",
			  "class" : "drp16",
			  "text" : "Designer for disaster recovery plans",
			  "link" : "/init/drplan/drplan" },
			{ 
			  "title" : "Batchs",
			  "class" : "actions",
			  "text" : "Collector janitoring batchs",
			  "link" : "/init/batchs/batchs",
			  "secure" : ["Manager"] },
			{ 
			  "title" : "Billing",
			  "class" : "bill16",
			  "text" : "Licensing tokens count and dispatch",
			  "link" : "/init/billing/billing",
			  "secure" : ["Manager"] },
			{ 
			  "title" : "Applications",
			  "class" : "svc",
			  "text" : "Create service provisioning templates",
			  "link" : "/init/apps/apps" },
			{ 
			  "title" : "Provisioning",
			  "class" : "prov",
			  "text" : "Create service provisioning templates",
			  "link" : "/init/provisioning/prov_admin",
			  "secure" : ["Manager","ProvManager"] },
			{ 
			  "title" : "Filters",
			  "class" : "filter16",
			  "text" : "Create new filtersets",
			  "link" : "/init/compliance/comp_filters" },
			{ 
			  "title" : "Forms",
			  "class" : "wf16",
			  "text" : "SeDesign new workflows and orchestrations",
			  "link" : "/init/forms/forms_admin" },
			{ 
			  "title" : "Metrics",
			  "class" : "spark16",
			  "text" : "Design sql requests to embed in charts",
			  "link" : "/init/charts/metrics_admin" },
			{ 
			  "title" : "Charts",
			  "class" : "spark16",
			  "text" : "Design charts to embed in reports",
			  "link" : "/init/charts/charts_admin" },
			{ 
			  "title" : "Reports",
			  "class" : "spark16",
			  "text" : "Design custom reports",
			  "link" : "/init/charts/reports_admin" },
			{ 
			  "title" : "Tags",
			  "class" : "fa-tags",
			  "text" : "Manage tag properties",
			  "link" : "/init/tags/tags" },
		],
		"Shortcuts" :
		[
			{ 
			  "title" : "Filter selector",
			  "class" : "",
			  "label" : "f",
			  "text" : "Switch the filter applied to all displayed data",
			  "link" : "" },
			{ 
			  "title" : "Link",
			  "class" : "",
			  "label" : "l",
			  "text" : "Show url to share your filters",
			  "link" : "" },
			{ 
			  "title" : "Navigation",
			  "class" : "",
			  "label" : "n",
			  "text" : "Open the navigation menu",
			  "link" : "" },
			{ 
			  "title" : "Search",
			  "class" : "",
			  "label" : "s",
			  "text" : "Focus the global search tool",
			  "link" : "" },
			{ 
			  "title" : "Unfocus",
			  "class" : "",
			  "label" : "ESC",
			  "text" : "Close pop-ups and menus",
			  "link" : "" },
			{ 
			  "title" : "Rest API",
			  "class" : "api",
			  "label" : "",
			  "text" : "Documentation",
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

  o.div.i18n()
  o.menu_div = $("#menu_menu");
  o.menu_clickable = $("#menu_top");

  menu_load_config(o);

  //Binding
  o.menu_clickable.on("click",function (event) {
  	menu_clicked(o);
  });
}

function menu_create_entry(o, entry)
{
	if (entry.secure !== undefined)
	{
		var sectest=0;
		services_ismemberof(entry.secure, function () {
			sectest = 1;
		});
		if (sectest==0) return;
	}

	var div_entry = "<div id='"+ entry.title.replace(" ","_") +"' class='menu_entry' link='" + entry.link + "'>";

	div_entry += "<div class='menu_box'>";

	var cl = entry.class;
	if (cl != "")
		div_entry += "<div class='menu_icon " + entry.class +  "'></div>";
	else
		div_entry += "<div class='menu_icon'>" + entry.label +  "</div>";
	div_entry += "<div>";
	div_entry += "<div class='menu_title'>" + entry.title + "</div>";
	div_entry += "<div class='menu_subtitle'>" + entry.text + "</div>";

	div_entry +="</div></div></div>";
	return div_entry;
}

function menu_bind_sub_link(o, section)
{
	for(i=0;i<section.length;i++)
	{
		$("#"+section[i].title.replace(" ","_")).on("click",function (event) {
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
			history.pushState({}, "", href)
	  	});
	}
}

function menu_create_section(o, title, section)
{
	var div_section = "<div id='menu_section' class='menu_section' style='display: block;'><a>";
	div_section += title + "</a><div>";

	for (i=0;i<section.length;i++)
	{
		div_section += menu_create_entry(o,section[i]);
	}

	div_section += "</div></div>";
	return div_section;
}

function menu_load_config(o)
{
	for (d in menu_search_key())
	{
		var result = menu_create_section(o, d, menu_search_key()[d]);
		o.menu_div.append(result);
		menu_bind_sub_link(o, menu_search_key()[d]);
	}
}

function menu_clicked(o)
{
	o.menu_div.toggle("fold", function()
	{
		filter_menu();
		$("#search_input").focus();
	});
}