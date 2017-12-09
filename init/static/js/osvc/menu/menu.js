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
		  "title" : "application",
		  "class" : "app16",
		  "id" : "view-app",
		  "link" : "/init/apps/apps",
		  "fn" : "table_apps"
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
		  "title" : "nodes hardware",
		  "class" : "hw16",
		  "id" : "view-nodes-hw",
		  "link" : "/init/nodes/nodes_hardware",
		  "fn" : "table_nodes_hardware"
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
		  "title" : "checks_defaults",
		  "class" : "check16",
		  "id" : "adm-chk-def",
		  "link" : "/init/checks/checks_defaults",
		  "fn" : "table_checks_defaults",
		  "secure" : ["Manager", "ChecksManager"]
		},
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
	"data_management": [
		{
			"title" : "add_app",
			"class" : "app16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-app",
			"fn" : "data_action_add_app",
			"link" : "/init/dm/index/data_action_add_app",
			"secure" : ["Manager", "AppManager"]
		},
		{
			"title" : "add_chart",
			"class" : "chart16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-chart",
			"fn" : "data_action_add_chart",
			"link" : "/init/dm/index/data_action_add_chart",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "add_contextual_thresholds",
			"class" : "check16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-contextual-thresholds",
			"fn" : "data_action_add_contextual_thresholds",
			"link" : "/init/dm/index/data_action_add_contextual_thresholds",
			"secure" : ["Manager", "ContextCheckManager"]
		},
		{
			"title" : "add_default_thresholds",
			"class" : "check16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-default-thresholds",
			"fn" : "data_action_add_default_thresholds",
			"link" : "/init/dm/index/data_action_add_default_thresholds",
			"secure" : ["Manager", "ChecksManager"]
		},
		{
			"title" : "add_dns_domain",
			"class" : "dns16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-dns-domain",
			"fn" : "data_action_add_dns_domain",
			"link" : "/init/dm/index/data_action_add_dns_domain",
			"secure" : ["Manager", "DnsManager"]
		},
		{
			"title" : "add_docker_registry",
			"class" : "docker_registry16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-docker-registry",
			"fn" : "data_action_add_docker_registry",
			"link" : "/init/dm/index/data_action_add_docker_registry",
			"secure" : ["Manager", "DockerRegistriesManager"]
		},
		{
			"title" : "add_filterset",
			"class" : "filter16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-filterset",
			"fn" : "data_action_add_filterset",
			"link" : "/init/dm/index/data_action_add_filterset",
			"secure" : ["Manager", "CompManager"]
		},
		{
			"title" : "add_form",
			"class" : "wf16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-form",
			"fn" : "data_action_add_form",
			"link" : "/init/dm/index/data_action_add_form",
			"secure" : ["Manager", "FormsManager"]
		},
		{
			"title" : "add_dns_record",
			"class" : "dns16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-dns-record",
			"fn" : "data_action_add_dns_record",
			"link" : "/init/dm/index/data_action_add_dns_record",
			"secure" : ["Manager", "DnsManager"]
		},
		{
			"title" : "add_group",
			"class" : "guys16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-group",
			"fn" : "data_action_add_group",
			"link" : "/init/dm/index/data_action_add_group",
			"secure" : ["Manager", "GroupManager"]
		},
		{
			"title" : "add_metric",
			"class" : "metric16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-metric",
			"fn" : "data_action_add_metric",
			"link" : "/init/dm/index/data_action_add_metric",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "add_network",
			"class" : "net16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-network",
			"fn" : "data_action_add_network",
			"link" : "/init/dm/index/data_action_add_network",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "add_network_segment",
			"class" : "net16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-network-segment",
			"fn" : "data_action_add_network_segment",
			"link" : "/init/dm/index/data_action_add_network_segment",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "add_node",
			"class" : "node16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-node",
			"fn" : "data_action_add_node",
			"link" : "/init/dm/index/data_action_add_node",
			"secure" : ["Manager", "NodeManager"]
		},
		{
			"title" : "add_prov_template",
			"class" : "prov",
			"stack" : "fa-plus-square",
			"id" : "dm-add-prov-template",
			"fn" : "data_action_add_prov_template",
			"link" : "/init/dm/index/data_action_add_prov_template",
			"secure" : ["Manager", "ProvisioningManager"]
		},
		{
			"title" : "add_quota",
			"class" : "quota16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-quota",
			"fn" : "data_action_add_quota",
			"link" : "/init/dm/index/data_action_add_quota",
			"secure" : ["Manager", "StorageManager"]
		},
		{
			"title" : "add_report",
			"class" : "report16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-report",
			"fn" : "data_action_add_report",
			"link" : "/init/dm/index/data_action_add_report",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "add_service",
			"class" : "svc",
			"stack" : "fa-plus-square",
			"id" : "dm-add-service",
			"fn" : "data_action_add_service",
			"link" : "/init/dm/index/data_action_add_service",
			"secure" : ["Manager", "NodeManager"]
		},
		{
			"title" : "add_tag",
			"class" : "tag16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-tag",
			"fn" : "data_action_add_tag",
			"link" : "/init/dm/index/data_action_add_tag",
			"secure" : ["Manager", "TagManager"]
		},
		{
			"title" : "add_user",
			"class" : "guy16",
			"stack" : "fa-plus-square",
			"id" : "dm-add-user",
			"fn" : "data_action_add_user",
			"link" : "/init/dm/index/data_action_add_user",
			"secure" : ["Manager", "UserManager"]
		},
		{
			"title" : "del_contextual_thresholds",
			"class" : "check16",
			"stack" : "fa-minus-square",
			"id" : "dm-del-contextual-thresholds",
			"fn" : "data_action_delete_contextual_thresholds",
			"link" : "/init/dm/index/data_action_delete_contextual_thresholds",
			"secure" : ["Manager", "ContextCheckManager"]
		},
		{
			"title" : "del_groups",
			"class" : "guys16",
			"stack" : "fa-minus-square",
			"id" : "dm-del-groups",
			"fn" : "data_action_del_groups",
			"link" : "/init/dm/index/data_action_del_groups",
			"secure" : ["Manager", "GroupManager"]
		},
		{
			"title" : "free_gids",
			"class" : "guys16",
			"stack" : "fa-search-plus",
			"id" : "dm-free-gids",
			"fn" : "tool_free_gids",
			"link" : "/init/dm/index/tool_free_gids"
		},
		{
			"title" : "free_uids",
			"class" : "guy16",
			"stack" : "fa-search-plus",
			"id" : "dm-free-uids",
			"fn" : "tool_free_uids",
			"link" : "/init/dm/index/tool_free_uids"
		},
		{
			"title" : "import_compliance_design",
			"class" : "comp16",
			"stack" : "fa-upload",
			"id" : "dm-import-compliance-design",
			"fn" : "data_action_import_compliance_design",
			"link" : "/init/dm/index/data_action_import_compliance_design",
			"secure" : ["Manager", "CompManager"]
		},
		{
			"title" : "import_report",
			"class" : "report16",
			"stack" : "fa-upload",
			"id" : "dm-import-report",
			"fn" : "data_action_import_report",
			"link" : "/init/dm/index/data_action_import_report",
			"secure" : ["Manager", "ReportsManager"]
		},
		{
			"title" : "refresh_obsolescence",
			"class" : "obs16",
			"stack" : "fa-refresh",
			"id" : "dm-refresh-obsolescence",
			"fn" : "data_action_obs_refresh",
			"link" : "/init/dm/index/data_action_obs_refresh",
			"secure" : ["Manager", "ObsManager"]
		},
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
		o.div.addClass("clickable")
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

		// compute the number of org groups the user is member of.
		// exclude Everybody.
		var ref_count = 0
		for (var i=0; i<_groups.length; i++) {
			var g = _groups[i]
			if (g.role == "Everybody") {
				continue
			}
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
		o.div.on("click", function (event) {
			if ($(event.target).is(".menu_section") || $(event.target).parents(".menu_section").length > 0) {
				return
			}
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
			o.open()
		} else {
			o.close()
		}
	}

	o.open = function() {
		if (o.menu_div.is(':visible')) {
			return
		}
		$(".header").find(".menu").slideUp()
		o.menu_div.stop().slideDown(function(){
			osvc.search.e_search_input.val("").focus()
			osvc.search.filter_menu()
			osvc.body_scroll.disable()
			osvc.search.set_placeholder()
		})
	}

	o.close = function() {
		if (!o.menu_div.is(':visible')) {
			return
		}
		o.menu_div.stop().slideUp(function(){
			osvc.body_scroll.enable()
			osvc.search.set_placeholder()
		})
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
				o.close()
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

	if (entry.stack) {
		var stack = "<i class='fa "+entry.stack+"'></i>"
	} else {
		var stack = ""
	}
	var cl = entry.class
	if (cl != "") {
		div_entry += "<div class='menu_icon " + cl + "'>" + stack + "</div>";
	} else {
		div_entry += "<div class='menu_icon'>" + entry.label +  "</div>";
	}
	div_entry += "<div>";
	div_entry += "<div class='menu_title'>" + titre + "</div>";
	div_entry += "<div class='menu_subtitle'>" + text + "</div>";

	div_entry +="</div></div></div>";
	return div_entry;
}


