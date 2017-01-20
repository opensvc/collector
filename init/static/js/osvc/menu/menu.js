var menu_data = {
	"views": [
		{
		  "title" : "dashboard",
		  "class" : "alert16",
		  "id" : "view-dashboard",
		  "link" : "/init/dashboard/index",
		  "fn" : "table_dashboard"
		},
		{
		  "title" : "services",
		  "class" : "svc",
		  "id" : "view-services",
		  "link" : "/init/services/services",
		  "fn" : "table_services"
		},
		{
		  "title" : "services_instances",
		  "class" : "svcinstance",
		  "id" : "view-service-instances",
		  "link" : "/init/default/svcmon",
		  "fn" : "table_service_instances"
		},
		{
		  "title" : "resources",
		  "class" : "resource",
		  "id" : "view-resources",
		  "link" : "/init/resmon/resmon",
		  "fn" : "table_resources"
		},
		{
		  "title" : "res_info",
		  "class" : "resource",
		  "id" : "view-resinfo",
		  "link" : "/init/resinfo/resinfo",
		  "fn" : "table_resinfo"
		},
		{
		  "title" : "nodes",
		  "class" : "node16",
		  "id" : "view-nodes",
		  "link" : "/init/nodes/nodes",
		  "fn" : "view_nodes"
		},
		{
		  "title" : "tag_attachments",
		  "class" : "fa-tags",
		  "id" : "view-tagattach",
		  "link" : "/init/tags/tagattach",
		  "fn" : "table_tagattach"
		},
		{
		  "title" : "actions",
		  "class" : "actions",
		  "id" : "view-actions",
		  "link" : "/init/svcactions/svcactions",
		  "fn" : "table_actions"
		},
		{
		  "title" : "actions_queue",
		  "class" : "actions",
		  "id" : "view-actions-queue",
		  "link" : "/init/action_queue/action_queue",
		  "fn" : "table_action_queue"
		},
		{
		  "title" : "checks",
		  "class" : "check16",
		  "id" : "view-checks",
		  "link" : "/init/checks/checks",
		  "fn" : "table_checks"
		},
		{
		  "title" : "packages",
		  "class" : "pkg16",
		  "id" : "view-pkg",
		  "link" : "/init/packages/packages",
		  "fn" : "table_packages"
		},
		{
		  "title" : "patches",
		  "class" : "patch",
		  "id" : "view-patch",
		  "link" : "/init/patches/patches",
		  "fn" : "table_patches"
		},
		{
		  "title" : "networks",
		  "class" : "net16",
		  "id" : "view-net",
		  "link" : "/init/networks/networks",
		  "fn" : "table_networks"
		},
		{
		  "title" : "node_networks",
		  "class" : "net16",
		  "id" : "view-node-net",
		  "link" : "/init/nodenetworks/nodenetworks",
		  "fn" : "table_nodenetworks"
		},
		{
		  "title" : "node_san",
		  "class" : "net16",
		  "id" : "view-node-san",
		  "link" : "/init/nodesan/nodesan",
		  "fn" : "table_nodesan"
		},
		{
		  "title" : "san_switches",
		  "class" : "net16",
		  "id" : "view-san",
		  "link" : "/init/sanswitches/sanswitches",
		  "fn" : "table_sanswitches"
		},
		{
		  "title" : "dns",
		  "class" : "dns16",
		  "id" : "view-dns",
		  "link" : "/init/dns/dns"
		},
		{
		  "title" : "docker",
		  "class" : "docker_registry16",
		  "id" : "view-docker",
		  "link" : "/init/registry/registries"
		},
		{
		  "title" : "saves",
		  "class" : "save16",
		  "id" : "view-saves",
		  "link" : "/init/saves/saves",
		  "fn" : "view_saves"
		},
		{
		  "title" : "disks",
		  "class" : "hd16",
		  "id" : "view-disks",
		  "link" : "/init/disks/disks"
		},
		{
		  "title" : "disks_quotas",
		  "class" : "quota16",
		  "id" : "view-disks-quotas",
		  "link" : "/init/disks/quota"
		}
	],
	"compliance": [
		{
		  "title" : "statut",
		  "class" : "compstatus",
		  "id" : "comp-status",
		  "link" : "/init/compliance/comp_status",
		  "fn" : "view_comp_status"
		},
		{
		  "title" : "log",
		  "class" : "complog",
		  "id" : "comp-log",
		  "link" : "/init/compliance/comp_log",
		  "fn" : "table_comp_log"
		},
		{
		  "title" : "modulesets",
		  "class" : "modset16",
		  "id" : "comp-modsets",
		  "link" : "/init/compliance/comp_modules",
		  "fn" : "table_comp_modules"
		},
		{
		  "title" : "rulesets",
		  "class" : "comp16",
		  "id" : "comp-rsets",
		  "link" : "/init/compliance/comp_rules",
		  "fn" : "table_comp_rules"
		},
		{
		  "title" : "designer",
		  "class" : "designer16",
		  "id" : "comp-designer",
		  "link" : "/init/compliance/comp_admin"
		},
		{
		  "title" : "safe",
		  "class" : "safe16",
		  "id" : "comp-safe",
		  "link" : "/init/safe/safe",
		  "fn" : "table_safe"
		},
		{
		  "title" : "nrulesets",
		  "class" : "node16",
		  "id" : "comp-node-rset",
		  "link" : "/init/compliance/comp_rulesets_nodes",
		  "fn" : "table_comp_rulesets_nodes"
		},
		{
		  "title" : "node_modulesets",
		  "class" : "node16",
		  "id" : "comp-node-modset",
		  "link" : "/init/compliance/comp_modulesets_nodes",
		  "fn" : "table_comp_modulesets_nodes"
		},
		{
		  "title" : "srulesets",
		  "class" : "svc",
		  "id" : "comp-svc-rset",
		  "link" : "/init/compliance/comp_rulesets_services",
		  "fn" : "table_comp_rulesets_services"
		},
		{
		  "title" : "service_modulesets",
		  "class" : "svc",
		  "id" : "comp-svc-modset",
		  "link" : "/init/compliance/comp_modulesets_services",
		  "fn" : "table_comp_modulesets_services"
		},
	],
	"statistic": [
		{
		  "title" : "reports",
		  "class" : "report16",
		  "id" : "stat-reports",
		  "link" : "/init/charts/reports",
		  "fn" : "reports"
		},
		{
		  "title" : "scheduler_stats",
		  "class" : "chart16",
		  "id" : "stat-scheduler",
		  "link" : "/init/stats/scheduler_stats",
                  "fn": "scheduler_stats"
		}
	],
	"requests": [
		{
		  "title" : "new_request",
		  "class" : "wf16",
		  "id" : "req-new",
		  "link" : "/init/forms/forms",
		  "fn" : "requests"
		},
		{
		  "title" : "a_t_m_t",
		  "class" : "wf16",
		  "id" : "req-pending-my",
		  "link" : "/init/forms/workflows_assigned_to_me",
		  "fn" : "table_workflows_assigned_to_me"
		},
		{
		  "title" : "p_t_a",
		  "class" : "wf16",
		  "id" : "req-pending-tiers",
		  "link" : "/init/forms/workflows_pending_tiers_action",
		  "fn" : "table_workflows_assigned_to_tiers"
		},
		{
		  "title" : "all_requests",
		  "class" : "wf16",
		  "id" : "req-all",
		  "link" : "/init/forms/workflows",
		  "fn" : "table_workflows"
		},
	],
	"administration": [
		{
		  "title" : "users",
		  "class" : "guys16",
		  "id" : "adm-usr",
		  "link" : "/init/users/users",
		  "fn" : "table_users",
		  "secure" : ["Manager", "UserManager"]
		},
		{
		  "title" : "log",
		  "class" : "log16",
		  "id" : "adm-log",
		  "link" : "/init/log/log",
		  "fn" : "table_log"
		},
		{
		  "title" : "o_setup",
		  "class" : "obs16",
		  "id" : "adm-obs",
		  "link" : "/init/obsolescence/obsolescence_config",
		  "fn" : "table_obsolescence"
		},
		{
		  "title" : "application",
		  "class" : "app16",
		  "id" : "adm-app",
		  "link" : "/init/apps/apps",
		  "fn" : "table_apps"
		},
		{
		  "title" : "batchs",
		  "class" : "batchs16",
		  "id" : "adm-batchs",
		  "link" : "/init/batchs/batchs",
		  "secure" : ["Manager"]
		},
		{
		  "title" : "billing",
		  "class" : "bill16",
		  "id" : "adm-bill",
		  "link" : "/init/billing/billing",
		  "secure" : ["Manager"]
		},
		{
		  "title" : "prov",
		  "class" : "prov",
		  "id" : "adm-prov",
		  "link" : "/init/provisioning/prov_admin",
		  "fn" : "table_prov_templates",
		  "secure" : ["Manager","ProvisioningManager"]
		},
		{
		  "title" : "filters",
		  "class" : "filter16",
		  "id" : "adm-filters",
		  "link" : "/init/filtersets/filters",
		  "fn" : "table_filters",
		},
		{
		  "title" : "filtersets",
		  "class" : "filter16",
		  "id" : "adm-filtersets",
		  "link" : "/init/filtersets/filtersets",
		  "fn" : "table_filtersets",
		},
		{
		  "title" : "forms",
		  "class" : "wf16",
		  "id" : "adm-forms",
		  "link" : "/init/forms/forms_admin",
                  "fn": "table_forms"
		},
		{
		  "title" : "metrics",
		  "class" : "metric16",
		  "id" : "adm-metrics",
		  "link" : "/init/charts/metrics_admin",
                  "fn": "table_metrics"
		},
		{
		  "title" : "charts",
		  "class" : "chart16",
		  "id" : "adm-charts",
		  "link" : "/init/charts/charts_admin",
                  "fn": "table_charts"
		},
		{
		  "title" : "reports",
		  "class" : "report16",
		  "id" : "adm-reports",
		  "link" : "/init/charts/reports_admin",
		  "fn" : "table_reports"
		},
		{
		  "title" : "tags",
		  "class" : "fa-tags",
		  "id" : "adm-tags",
		  "link" : "/init/tags/tags",
                  "fn": "table_tags"
		},
		{
		  "title" : "replication",
		  "class" : "repl16",
		  "id" : "adm-replication",
		  "link" : "/init/replication/repl_admin",
                  "fn": "table_replication"
		}
	],
	"shortcuts": [
		{
		  "title" : "filter_sel",
		  "class" : "",
		  "id" : "key-f",
		  "label" : "f",
		  "link" : ""
		},
		{
		  "title" : "nav",
		  "class" : "",
		  "id" : "key-n",
		  "label" : "n",
		  "link" : ""
		},
		{
		  "title" : "refresh",
		  "class" : "",
		  "id" : "key-r",
		  "label" : "r",
		  "link" : ""
		},
		{
		  "title" : "search",
		  "class" : "",
		  "id" : "key-s",
		  "label" : "s",
		  "link" : ""
		},
		{
		  "title" : "unfocus",
		  "class" : "",
		  "id" : "key-esc",
		  "label" : "ESC",
		  "link" : ""
		},
		{
		  "title" : "rest_api",
		  "class" : "api",
		  "label" : "",
		  "id" : "help-api",
		  "link" : "/init/rest/doc"
		}
	]
}

function menu(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.set_title = function(title) {
		o.menu_clickable.text(title)
	}

	o.set_title_from_href = function() {
		for (d in menu_data) {
			var section = menu_data[d]
			for (i=0; i<section.length; i++) {
				var entry = section[i]
				if (entry.link == window.location.pathname) {
					var title = i18n.t("menu."+d+ "." + entry.title +".title")
					o.set_title(title)
				}
			}
		}
	}

	o.load_sections = function() {
		for (d in menu_data) {
			var result = o.create_section(d)
			o.menu_div.append(result)
			o.bind_sub_link(d)
		}
	}


	o.div.load("/init/static/views/menu.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		$.when(osvc.user_loaded).then(function(){
			o.store_data(osvc.hidden_menu_entries_stats)
			o.init()
		})
	})

	o.store_data = function(data) {
		/*
		{
		    "data": {
			"menu_entry": {
			    "key-s": 1,
			    "key-r": 1,
			    "key-esc": 1
			}
		    }
		}
		*/
		osvc.hidden_menu_entries = []
		var ref_count = 0
		for (var i=0; i<_groups.length; i++) {
			var g = _groups[i]
			if (g.privilege == true) {
				continue
			}
			ref_count++
		}
		for (key in data.menu_entry) {
			if (data.menu_entry[key] == ref_count) {
				osvc.hidden_menu_entries.push(key)
			}
		}
		console.log("hidden menu entries:", osvc.hidden_menu_entries)
	}


	o.init = function() {
		var timer;

		o.menu_div = o.div.find("#menu_menu")
		o.menu_clickable = o.div.find("#menu_top > .header_logo > a").first()

		o.load_sections(o)
		o.set_title_from_href()

		//Binding
		o.menu_clickable.on("click", function (event) {
			o.clicked()
		});
	}

	o.create_entry = function (section, entry) {
		if (osvc.hidden_menu_entries.indexOf(entry.id) >= 0) {
			return
		}
		if (entry.secure && !services_ismemberof(entry.secure)) {
			return
		}
		return menu_create_entry_s(section, entry)
	}

	o.create_section = function(title) {
		var section = menu_data[title]
		var div_section = "<div id='menu_section' class='menu_section' style='display: block;'><a>"
		div_section += i18n.t("menu."+title+".title") + "</a><div>"

		for (i=0; i<section.length; i++) {
			var s = o.create_entry(title, section[i])
			if (!s) {
				continue
			}
			div_section += s
		}

		div_section += "</div></div>"
		return div_section
	}

	o.clicked = function() {
		if (!o.menu_div.is(":visible")) {
			$(".header").find(".menu").slideUp()
			o.menu_div.stop().slideDown(function(){
				osvc.search.filter_menu()
			})
			osvc.search.e_search_input.val("").focus()
		} else {
			o.menu_div.stop().slideUp()
		}
	}

	o.bind_sub_link = function(title) {
		var section = menu_data[title]
		for (i=0; i<section.length; i++) {
			$("#menu_"+title+"_"+section[i].title).on("click", function (event) {
				event.preventDefault()
				var title = $(this).find(".menu_title").text()
				var href = $(this).attr("link");
				var fn = $(this).attr("fn");
				if (!href) {
				  return
				}
				if (event.ctrlKey) {
				  window.open(href, "_blank")
				  return
				}
				o.set_title(title)
				o.menu_div.slideUp();
				osvc.search.e_search_input.val("").blur()
				app_load_href(href, fn)
			})
		}
	}

	return o
}

function menu_create_entry_s(section, entry)
{
	var titre = i18n.t("menu."+section+ "." + entry.title +".title");
	var text = i18n.t("menu."+section+ "." + entry.title +".text");

	var div_entry = "<div id='menu_" + section + "_" + entry.title + "' class='menu_entry clickable' link='" + entry.link + "' fn='" + entry.fn + "'>";

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


