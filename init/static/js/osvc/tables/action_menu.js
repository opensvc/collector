//
// install agent action menu entries definitions in the table object
//
var am_node_agent_leafs = [
	{
		'title': 'Update node information',
		'class': 'node16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'pushasset'
	},
	{
		'title': 'Update disks information',
		'class': 'hd16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'pushdisks'
	},
	{
		'title': 'Update app information',
		'class': 'svc',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'push_resinfo'
	},
	{
		'title': 'Update services information',
		'class': 'svc',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'push_services'
	},
	{
		'title': 'Update installed packages information',
		'class': 'pkg16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'pushpkg'
	},
	{
		'title': 'Update installed patches information',
		'class': 'pkg16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'pushpatch'
	},
	{
		'title': 'Update stats',
		'class': 'chart16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'pushstats'
	},
	{
		'title': 'Update check values',
		'class': 'ok',
		"privileges": ["Manager", "NodeManager", "NodeExec", "CheckExec"],
		"min": 1,
		'action': 'checks'
	},
	{
		'title': 'Update sysreport',
		'class': 'log16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'sysreport'
	},
	{
		'title': 'Update compliance modules',
		'class': 'comp16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'updatecomp'
	},
	{
		'title': 'Update opensvc agent',
		'class': 'pkg16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'updatepkg'
	},
	{
		'title': 'Rotate root password',
		'class': 'key',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'rotate root pw'
	},
	{
		'title': 'Rescan scsi hosts',
		'class': 'hd16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'scanscsi'
	},
	{
		'title': 'Reboot',
		'class': 'action_restart_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'reboot'
	},
	{
		'title': 'Reboot schedule',
		'class': 'action_restart_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'schedule_reboot'
	},
	{
		'title': 'Reboot unschedule',
		'class': 'action_restart_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'unschedule_reboot'
	},
	{
		'title': 'Shutdown',
		'class': 'action_stop_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'shutdown'
	},
	{
		'title': 'Wake On LAN',
		'class': 'action_start_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'wol'
	},
	{
		'title': 'Compliance check',
		'class': 'comp16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'compliance_check',
		'params': ["module", "moduleset"]
	},
	{
		'title': 'Compliance fix',
		'class': 'comp16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'compliance_fix',
		'params': ["module", "moduleset"]
	},
	{
		'title': 'action_menu.provisioning',
		'class': 'prov',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'fn': 'agent_action_provisioning'
	}
]

var am_svc_agent_leafs = [
	{
		'title': 'Start',
		'class': 'action_start_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'start'
	},
	{
		'title': 'Stop',
		'class': 'action_stop_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'stop'
	},
	{
		'title': 'Giveback',
		'class': 'action_switch_16',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'giveback'
	},
	{
		'title': 'Abort',
		'class': 'icon fa-ban',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'abort'
	},
	{
		'title': 'Clear',
		'class': 'icon fa-eraser',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'clear'
	},
	{
		'title': 'Freeze',
		'class': 'icon fa-snowflake icon-blue',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'freeze'
	},
	{
		'title': 'Thaw',
		'class': 'icon fa-snowflake icon-gray',
		"privileges": ["Manager", "NodeManager", "NodeExec"],
		"min": 1,
		'action': 'thaw'
	}
]

function table_action_menu_init_data(t) {
	t.action_menu_req_max = 1000
	t.column_selectors = {
		"svc_id": ".cell[col=svc_id]",
		"node_id": ".cell[col=node_id]",
		"rid": ".cell[col=rid]",
		"module": ".cell[col=run_module]",
		"vmname": ".cell[col=vmname]",
		"action": ".cell[col=action]",
		"id": ".cell[col=id]",
		"net_id": ".cell[col=net_id]",
		"seg_id": ".cell[col=seg_id]",
		"fset_id": ".cell[col=fset_id]",
		"encap_fset_id": ".cell[col=encap_fset_id]",
		"f_id": ".cell[col=f_id]",
		"email": ".cell[col=email]",
		"tag_id": ".cell[col=tag_id]",
		"ruleset_id": ".cell[col=ruleset_id]",
		"modset_id": ".cell[col=modset_id]",
		"slave": ".cell[col=encap]",
		"command": ".cell[col=command]",
		"registry_id": ".cell[col=registry_id]",
		"repository_id": ".cell[col=repository_id]",
		"chk_type": ".cell[col=chk_type]",
		"chk_instance": ".cell[col=chk_instance]"
	}

	t.action_menu_data = [
		// section: tools
		{
			"title": "action_menu.tools",
			//"class": "chart16",
			"children": [
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_nodes",
					"clicked_decorator": function(e, data){
						e.osvc_nodename()
					},
					"class": "node16",
					"foldable": true,
					"cols": ["node_id"],
					"condition": "node_id",
					"children": [
						{
							"title": "action_menu.node_diff",
							"class": "common16",
							"fn": "tool_nodediff",
							"min": 2,
							"max": 10
						},
						{
							"title": "action_menu.node_sysrep",
							"class": "log16",
							"fn": "tool_nodesysrep",
							"min": 1,
							"max": 10
						},
						{
							"title": "action_menu.node_sysrep_diff",
							"class": "common16",
							"fn": "tool_nodesysrepdiff",
							"min": 2,
							"max": 10
						},
						{
							"title": "action_menu.node_san_topo",
							"class": "hd16",
							"fn": "tool_nodesantopo",
							"min": 1,
							"max": 50
						},
						{
							"title": "action_menu.node_perf",
							"class": "chart16",
							"fn": "tool_grpprf",
							"min": 1,
							"max": 20
						},
						{
							"title": "action_menu.obsolescence",
							"class": "chart16",
							"fn": "tool_obsolescence",
							"min": 2
						}
					]
				},
				{
					"selector": ["checked"],
					"title": "action_menu.on_services",
					"clicked_decorator": function(e, data){
						e.osvc_svcname()
					},
					"class": "svc",
					"foldable": true,
					"cols": ["svc_id"],
					"condition": "svc_id",
					"children": [
						{
							"title": "action_menu.svc_diff",
							"class": "common16",
							"fn": "tool_svcdiff",
							"min": 2
						},
						{
							"title": "action_menu.services_status_log",
							"class": "avail16",
							"fn": "tool_services_status_log",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked"],
					"title": "action_menu.on_nodes_and_services",
					"clicked_decorator": clicked_decorator_nodes_and_services,
					"class": "svc",
					"foldable": true,
					"cols": ["svc_id", "node_id"],
					"condition": "svc_id,node_id",
					"children": [
						{
							"title": "action_menu.topology",
							"class": "dia16",
							"fn": "tool_topo",
							"min": 1
						}
					]
				}
			]
		},
		// section: data actions
		{
			"title": "action_menu.data_actions",
			"children": [
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_filters',
					"class": "filter16",
					"table": ["filters"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_filters",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_filtersets',
					"clicked_decorator": function(e, data){
						e.osvc_filtersetname()
					},
					"class": "filter16",
					"table": ["filtersets"],
					"cols": ["fset_id"],
					"condition": "fset_id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_filtersets",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.attach_filters",
							"class": "attach16",
							"fn": "data_action_attach_filters",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.attach_filtersets",
							"class": "attach16",
							"fn": "data_action_attach_filtersets",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_encap_filters',
					"class": "filter16",
					"table": ["filtersets"],
					"cols": ["fset_id", "f_id"],
					"condition": "fset_id+f_id",
					"children": [
						{
							"title": "action_menu.detach_filters",
							"class": "detach16",
							"fn": "data_action_detach_filters",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_operator",
							"class": "edit16",
							"fn": "data_action_filters_set_operator",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_order",
							"class": "edit16",
							"fn": "data_action_filters_set_order",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_encap_filtersets',
					"class": "filter16",
					"table": ["filtersets"],
					"cols": ["fset_id", "encap_fset_id"],
					"condition": "fset_id+encap_fset_id",
					"children": [
						{
							"title": "action_menu.detach_filtersets",
							"class": "detach16",
							"fn": "data_action_detach_filtersets",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_operator",
							"class": "edit16",
							"fn": "data_action_filtersets_set_operator",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_order",
							"class": "edit16",
							"fn": "data_action_filtersets_set_order",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_metrics',
					"clicked_decorator": function(e, data){
						e.osvc_metricname()
					},
					"class": osvc.icons.metric,
					"table": ["metrics"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_metrics",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_metrics_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_metrics_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_charts',
					"clicked_decorator": function(e, data){
						e.osvc_chartname()
					},
					"class": osvc.icons.chart,
					"table": ["charts"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_charts",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_charts_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_charts_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_charts_responsible",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_charts_responsible",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_reports',
					"clicked_decorator": function(e, data){
						e.osvc_reportname()
					},
					"class": osvc.icons.report,
					"table": ["reports"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_reports",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_reports_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_reports_publication",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_reports_responsible",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_reports_responsible",
							"privileges": ["Manager", "ReportsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_prov_templates',
					"clicked_decorator": function(e, data){
						e.osvc_prov_templatename()
					},
					"class": "prov",
					"table": ["templates"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_prov_templates",
							"privileges": ["Manager", "ProvisioningManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_prov_templates_publication",
							"privileges": ["Manager", "ProvisioningManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_prov_templates_publication",
							"privileges": ["Manager", "ProvisioningManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_prov_templates_responsible",
							"privileges": ["Manager", "ProvisioningManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_prov_templates_responsible",
							"privileges": ["Manager", "ProvisioningManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_obsolescence_settings',
					"clicked_decorator": function(e, data){
						e.osvc_obsolescencename()
					},
					"class": "check16",
					"table": ["obsolescence"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.set_warn_date",
							"class": "edit16",
							"fn": "data_action_obs_set_warn_date",
							"privileges": ["Manager", "ObsManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_alert_date",
							"class": "edit16",
							"fn": "data_action_obs_set_alert_date",
							"privileges": ["Manager", "ObsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_obs_del",
							"privileges": ["Manager", "ObsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_quotas',
					"class": "quota16",
					"table": ["quota"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_quotas",
							"privileges": ["Manager", "StorageManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_apps',
					"clicked_decorator": function(e, data){
						e.osvc_appname()
					},
					"class": "app16",
					"table": ["apps"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_apps",
							"privileges": ["Manager", "AppManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_app_publication",
							"privileges": ["Manager", "AppManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_app_publication",
							"privileges": ["Manager", "AppManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_app_responsible",
							"privileges": ["Manager", "AppManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_app_responsible",
							"privileges": ["Manager", "AppManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_compliance_status",
					"class": "comp16",
					"foldable": true,
					"cols": ["id", "module"],
					"condition": "id+module",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_compliance_status",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_node_ips",
					"clicked_decorator": clicked_decorator_node_ips,
					"class": "net16",
					"table": ["nodenetworks"],
					"foldable": true,
					"cols": ["id", "node_id"],
					"condition": "id+node_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_node_ips",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_dns_domains',
					"clicked_decorator": function(e, data){
						e.osvc_dns_domainname()
					},
					"class": "dns16",
					"table": ["dns_domains"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_dns_domains",
							"privileges": ["Manager", "DnsManager"],
							"min": 1
						},
						{
							"title": "action_menu.sync_dns_domains",
							"class": "net16",
							"fn": "data_action_sync_dns_domains",
							"privileges": ["Manager", "DnsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_dns_records',
					"clicked_decorator": function(e, data){
						e.osvc_dns_recordname()
					},
					"class": "dns16",
					"table": ["dns_records"],
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_dns_records",
							"privileges": ["Manager", "DnsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_networks",
					"clicked_decorator": function(e, data){
						e.osvc_netname()
					},
					"class": "net16",
					"table": ["networks"],
					"foldable": true,
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_networks",
							"privileges": ["Manager", "NetworkManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_network_segments",
					"clicked_decorator": clicked_decorator_network_segment,
					"class": "segment16",
					"table": ["network_segments"],
					"foldable": true,
					"cols": ["net_id", "seg_id"],
					"condition": "net_id+seg_id",
					"children": [
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_networks_segments_responsible",
							"privileges": ["Manager", "NetworkManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_networks_segments_responsible",
							"privileges": ["Manager", "NetworkManager"],
							"min": 1
						},
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_networks_segments",
							"privileges": ["Manager", "NetworkManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_modulesets",
					"clicked_decorator": function(e, data){
						e.osvc_modulesetname()
					},
					"class": "modset16",
					"foldable": true,
					"cols": ["modset_id"],
					"condition": "modset_id",
					"children": [
						{
							"title": "action_menu.del_moduleset",
							"class": "del16",
							"fn": "data_action_del_modulesets",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_moduleset_publication",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_moduleset_publication",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_moduleset_responsible",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_moduleset_responsible",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_rulesets",
					"clicked_decorator": function(e, data){
						e.osvc_rulesetname()
					},
					"class": "rset16",
					"foldable": true,
					"cols": ["ruleset_id"],
					"condition": "ruleset_id",
					"children": [
						{
							"title": "action_menu.del_ruleset",
							"class": "del16",
							"fn": "data_action_del_rulesets",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_ruleset_publication",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_ruleset_publication",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_ruleset_responsible",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_ruleset_responsible",
							"privileges": ["Manager", "CompManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_safe_files",
					"clicked_decorator": function(e, data){
						e.osvc_safe()
					},
					"class": "safe16",
					"table": ["safe"],
					"foldable": true,
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_safe_publication",
							"privileges": ["Manager", "SafeUploader"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_safe_publication",
							"privileges": ["Manager", "SafeUploader"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_safe_responsible",
							"privileges": ["Manager", "SafeUploader"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_safe_responsible",
							"privileges": ["Manager", "SafeUploader"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_forms",
					"clicked_decorator": function(e, data){
						e.osvc_formname()
					},
					"class": "wf16",
					"table": ["forms"],
					"foldable": true,
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.del_form",
							"class": "del16",
							"fn": "data_action_del_form",
							"privileges": ["Manager", "FormsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_publication",
							"class": "add16",
							"fn": "data_action_add_form_publication",
							"privileges": ["Manager", "FormsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_publication",
							"class": "del16",
							"fn": "data_action_del_form_publication",
							"privileges": ["Manager", "FormsManager"],
							"min": 1
						},
						{
							"title": "action_menu.add_responsible",
							"class": "add16",
							"fn": "data_action_add_form_responsible",
							"privileges": ["Manager", "FormsManager"],
							"min": 1
						},
						{
							"title": "action_menu.del_responsible",
							"class": "del16",
							"fn": "data_action_del_form_responsible",
							"privileges": ["Manager", "FormsManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_nodes',
					"clicked_decorator": function(e, data){
						e.osvc_nodename()
					},
					"class": "node16",
					"cols": ["node_id"],
					"condition": "node_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_nodes",
							"privileges": ["Manager", "NodeManager"],
							"min": 1
						},
						{
							"title": "action_menu.tag_attach",
							"class": "tag16",
							"fn": "data_action_nodes_tags_attach",
							"privileges": ["Manager", "NodeManager"],
							"min": 1
						},
						{
							"title": "action_menu.modset_attach",
							"class": "modset16",
							"fn": "data_action_nodes_modsets_attach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.modset_detach",
							"class": "modset16",
							"fn": "data_action_nodes_modsets_detach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.ruleset_attach",
							"class": "comp16",
							"fn": "data_action_nodes_rulesets_attach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.ruleset_detach",
							"class": "comp16",
							"fn": "data_action_nodes_rulesets_detach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_check_defaults',
					"class": "check16",
					"cols": ["id"],
					"condition": "id",
					"table": ["checks_defaults"],
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_default_thresholds",
							"privileges": ["Manager", "ChecksManager"],
							"min": 1
						},
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_check_instances',
					"class": "check16",
					"cols": ["node_id", "svc_id", "chk_type", "chk_instance"],
					"condition": "node_id+chk_type+chk_instance,node_id+svc_id+chk_type+chk_instance",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_chk_instance_delete",
							"privileges": ["Manager", "CheckExec"],
							"min": 1
						},
						{
							"title": "action_menu.reset_thresholds",
							"class": "fa-undo",
							"fn": "data_action_chk_instance_reset_thresholds",
							"privileges": ["Manager", "CheckExec"],
							"min": 1
						},
						{
							"title": "action_menu.set_low_threshold",
							"class": "fa-angle-down",
							"fn": "data_action_chk_instance_set_low_threshold",
							"privileges": ["Manager", "CheckExec"],
							"min": 1
						},
						{
							"title": "action_menu.set_high_threshold",
							"class": "fa-angle-up",
							"fn": "data_action_chk_instance_set_high_threshold",
							"privileges": ["Manager", "CheckExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_nodes_modulesets',
					"class": "modset16",
					"cols": ["node_id", "modset_id"],
					"condition": "node_id+modset_id",
					"children": [
						{
							"title": "action_menu.modset_detach",
							"class": "del16",
							"fn": "data_action_nodes_modsets_detach_no_selector",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_queued_actions',
					"class": "actions",
					"cols": ["id", "command"],
					"condition": "id+command",
					"children": [
						{
							"title": "action_menu.cancel",
							"class": "del16",
							"fn": "data_action_action_queue_cancel",
							"privileges": ["Manager", "NodeExec", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.redo",
							"class": "refresh16",
							"fn": "data_action_action_queue_redo",
							"privileges": ["Manager", "NodeExec", "CompExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_nodes_rulesets',
					"class": "comp16",
					"cols": ["node_id", "ruleset_id"],
					"condition": "node_id+ruleset_id",
					"children": [
						{
							"title": "action_menu.ruleset_detach",
							"class": "del16",
							"fn": "data_action_nodes_rulesets_detach_no_selector",
							"privileges": ["Manager", "NodeManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_nodes_tags',
					"class": "tag16",
					"cols": ["node_id", "tag_id"],
					"condition": "node_id+tag_id",
					"children": [
						{
							"title": "action_menu.nodes_tags_detach",
							"class": "del16",
							"fn": "data_action_nodes_tags_detach",
							"privileges": ["Manager", "NodeManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services',
					"clicked_decorator": function(e, data){
						e.osvc_svcname()
					},
					"class": "svc",
					"cols": ["svc_id", "slave"],
					"condition": "svc_id+slave,svc_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_svcs",
							"min": 1
						},
						{
							"title": "action_menu.tag_attach",
							"class": "tag16",
							"fn": "data_action_services_tags_attach",
							"min": 1
						},
						{
							"title": "action_menu.modset_attach",
							"class": "modset16",
							"fn": "data_action_services_modsets_attach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.modset_detach",
							"class": "modset16",
							"fn": "data_action_services_modsets_detach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.ruleset_attach",
							"class": "comp16",
							"fn": "data_action_services_rulesets_attach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						},
						{
							"title": "action_menu.ruleset_detach",
							"class": "comp16",
							"fn": "data_action_services_rulesets_detach",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services_instances',
					"clicked_decorator": clicked_decorator_service_instance,
					"table": ["service_instances"],
					"class": "svcinstance",
					"cols": ["id", "node_id", "svc_id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_svc_instances",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					"table": ["resmon"],
					'title': 'action_menu.on_resources',
					"clicked_decorator": clicked_decorator_resource,
					"class": "resource",
					"cols": ["id"],
					"condition": "id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_resources",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_service_actions',
					"clicked_decorator": clicked_decorator_action,
					"class": "actions",
					"cols": ["id", "action", "ack", "svc_id"],
					"condition": "id+action",
					"children": [
						{
							"title": "action_menu.ack",
							"class": "check16",
							"fn": "data_action_ack_actions",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services_tags',
					"class": "tag16",
					"cols": ["svc_id", "tag_id"],
					"condition": "svc_id+tag_id",
					"children": [
						{
							"title": "action_menu.services_tags_detach",
							"class": "del16",
							"fn": "data_action_services_tags_detach",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services_modulesets',
					"clicked_decorator": clicked_decorator_service_moduleset,
					"class": "modset16",
					"cols": ["svc_id", "modset_id", "slave"],
					"condition": "svc_id+modset_id+slave",
					"children": [
						{
							"title": "action_menu.modset_detach",
							"class": "del16",
							"fn": "data_action_services_modsets_detach_no_selector",
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services_rulesets',
					"class": "rset16",
					"cols": ["svc_id", "ruleset_id", "slave"],
					"condition": "svc_id+ruleset_id+slave",
					"children": [
						{
							"title": "action_menu.ruleset_detach",
							"class": "del16",
							"fn": "data_action_services_rulesets_detach_no_selector",
							"privileges": ["Manager", "CompExec"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_tags',
					"class": "tag16",
					"table": ["tags"],
					"cols": ["tag_id"],
					"condition": "tag_id",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_tag",
							"privileges": ["Manager", "TagManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_users",
					"class": "guy16",
					"foldable": true,
					"cols": ["id", "email"],
					"condition": "id+email",
					"children": [
						{
							"title": "action_menu.del",
							"class": "del16",
							"fn": "data_action_del_user",
							"privileges": ["Manager", "UserManager"],
							"min": 1
						},
						{
							"title": "action_menu.attach_groups",
							"class": "attach16",
							"fn": "data_action_user_attach_groups",
							"privileges": ["Manager", "GroupManager"],
							"min": 1
						},
						{
							"title": "action_menu.detach_groups",
							"class": "detach16",
							"fn": "data_action_user_detach_groups",
							"privileges": ["Manager", "GroupManager"],
							"min": 1
						},
						{
							"title": "action_menu.attach_privileges",
							"class": "attach16",
							"fn": "data_action_user_attach_privileges",
							"privileges": ["Manager", "GroupManager"],
							"min": 1
						},
						{
							"title": "action_menu.detach_privileges",
							"class": "detach16",
							"fn": "data_action_user_detach_privileges",
							"privileges": ["Manager", "GroupManager"],
							"min": 1
						},
						{
							"title": "action_menu.lock_filterset",
							"class": "fa-lock",
							"fn": "data_action_user_lock_filterset",
							"privileges": ["Manager", "UserManager", "SelfManager"],
							"min": 1
						},
						{
							"title": "action_menu.unlock_filterset",
							"class": "fa-unlock",
							"fn": "data_action_user_unlock_filterset",
							"privileges": ["Manager", "UserManager", "SelfManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_filterset",
							"class": "filter16",
							"fn": "data_action_user_set_filterset",
							"privileges": ["Manager", "UserManager", "SelfManager"],
							"min": 1
						},
						{
							"title": "action_menu.set_primary_group",
							"class": "guys16",
							"fn": "data_action_user_set_primary_group",
							"privileges": ["Manager", "UserManager", "SelfManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_docker_tags",
					"clicked_decorator": clicked_decorator_docker,
					"class": "dockertags16",
					"foldable": true,
					"cols": ["registry_id", "tag_id", "repository_id"],
					"condition": "registry_id+tag_id+repository_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_docker_tags",
							"privileges": ["Manager", "DockerRegistriesManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_docker_repositories",
					"clicked_decorator": clicked_decorator_docker,
					"class": "docker_repository16",
					"foldable": true,
					"cols": ["repository_id"],
					"condition": "repository_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_docker_repositories",
							"privileges": ["Manager", "DockerRegistriesManager"],
							"min": 1
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"title": "action_menu.on_docker_registries",
					"clicked_decorator": function(e, data){
						e.osvc_docker_registryname()
					},
					"class": "docker_registry16",
					"foldable": true,
					"cols": ["registry_id"],
					"condition": "registry_id",
					"children": [
						{
							"title": "action_menu.delete",
							"class": "del16",
							"fn": "data_action_delete_docker_registries",
							"privileges": ["Manager", "DockerRegistriesManager"],
							"min": 1
						}
					]
				}
			]
		},
		// section: agent actions
		{
			"title": "action_menu.agent_actions",
			//"class": "action16",
			"children": [
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_nodes',
					"clicked_decorator": function(e, data){
						e.osvc_nodename()
					},
					"class": "node16",
					"cols": ["node_id"],
					"condition": "node_id",
					"children": am_node_agent_leafs
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services',
					"clicked_decorator": function(e, data){
						e.osvc_svcname()
					},
					"class": "svc",
					"cols": ["svc_id"],
					"condition": "svc_id",
					"children": am_svc_agent_leafs
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_services_instances',
					"clicked_decorator": clicked_decorator_service_instance,
					"class": "svcinstance",
					"cols": ["svc_id", "node_id"],
					"condition": "svc_id+node_id",
					"children": [
						{
							'title': 'Push',
							'class': 'fa-upload',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'push'
						},
						{
							'title': 'Pull',
							'class': 'fa-download',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'pull'
						},
						{
							'title': 'Start',
							'class': 'action_start_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'start'
						},
						{
							'title': 'Stop',
							'class': 'action_stop_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'stop'
						},
						{
							'title': 'Restart',
							'class': 'action_restart_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'restart'
						},
						{
							'title': 'Takeover',
							'class': 'action_switch_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'takeover'
						},
						{
							'title': 'Giveback',
							'class': 'action_switch_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'giveback'
						},
						{
							'title': 'Switch',
							'class': 'action_switch_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'switch'
						},
						{
							'title': 'Run',
							'class': 'fa-play icon-green',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'switch'
						},
						{
							'title': 'Sync all remotes',
							'class': 'action_sync_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'syncall'
						},
						{
							'title': 'Sync peer remotes',
							'class': 'action_sync_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'syncnodes'
						},
						{
							'title': 'Sync disaster recovery remotes',
							'class': 'action_sync_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'syncdrp'
						},
						{
							'title': 'Abort',
							'class': 'icon fa-ban',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'abort'
						},
						{
							'title': 'Clear',
							'class': 'icon fa-eraser',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'clear'
						},
						{
							'title': 'Enable',
							'class': 'ok',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'enable'
						},
						{
							'title': 'Disable',
							'class': 'nok',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'disable'
						},
						{
							'title': 'Thaw',
							'class': 'icon fa-snowflake icon-gray',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'thaw'
						},
						{
							'title': 'Freeze',
							'class': 'icon fa-snowflake icon-blue',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'freeze'
						},
						{
							'title': 'Compliance check',
							'class': 'comp16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'compliance_check',
							'params': ["module", "moduleset"]
						},
						{
							'title': 'Compliance fix',
							'class': 'comp16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
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
					"clicked_decorator": clicked_decorator_resource,
					"class": "resource",
					"cols": ["svc_id", "node_id", "vmname", "rid"],
					"condition": "svc_id+node_id+vmname+rid,svc_id+node_id+rid",
					"children": [
						{
							'title': 'Start',
							'class': 'action_start_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'start'
						},
						{
							'title': 'Stop',
							'class': 'action_stop_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'stop'
						},
						{
							'title': 'Restart',
							'class': 'action_restart_16',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'restart'
						},
						{
							'title': 'Enable',
							'class': 'ok',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'enable'
						},
						{
							'title': 'Disable',
							'class': 'nok',
							"privileges": ["Manager", "NodeManager", "NodeExec"],
							"min": 1,
							'action': 'disable'
						}
					]
				},
				{
					"selector": ["clicked", "checked", "all"],
					"foldable": true,
					'title': 'action_menu.on_modules',
					"class": "mod16",
					"cols": ["svc_id", "node_id", "module"],
					"condition": "svc_id+node_id+module,node_id+module",
					"children": [
						{
							'title': 'Check',
							'class': 'comp16',
							"privileges": ["Manager", "NodeManager", "NodeExec", "CompExec"],
							"min": 1,
							'action': 'check'
						},
						{
							'title': 'Fix',
							'class': 'comp16',
							"privileges": ["Manager", "NodeManager", "NodeExec", "CompExec"],
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
// animation to highlight a post in the action_q
//
function table_action_menu_click_animation(t) {
	dest = $(".header").find(".action_q_widget")
	dest.effect("highlight")
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

		var yes_no = table_action_menu_yes_no('action_menu.confirmation', function(){
			table_action_menu_agent_action(t, e, true)
		})
		yes_no.insertAfter(entry)
		if (s.length > 0) {
			$(s).insertAfter(entry)
		}
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

	//services_osvcputrest("R_ACTIONS", "", "", del_data, function(jd) {
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
// tool: free uids
//
function tool_free_uids(divid) {
	var parent_div = $("#"+divid)
	var div = data_management_div({"title": "menu.data_management.free_uids.title"})
	parent_div.empty().append(div)
	var title = $("<div></div>")
	var input = $("<input class='oi' id='uid_start'>")
	var area = $("<div style='padding-top:1em' class='pre'></div>")
	area.uniqueId()
	title.text(i18n.t("action_menu.user_id_range_start"))
	div.append(title)
	div.append(input)
	div.append(area)
	input.bind("keyup", function(event) {
		if (!is_enter(event)) {
			return
		}
		sync_ajax("/init/nodes/ajax_free_uids", ["uid_start"], area.attr("id"), function(){})
	})
}

//
// tool: free gids
//
function tool_free_gids(divid) {
	var parent_div = $("#"+divid)
	var div = data_management_div({"title": "menu.data_management.free_gids.title"})
	parent_div.empty().append(div)
	var title = $("<div></div>")
	var input = $("<input class='oi' id='gid_start'>")
	var area = $("<div style='padding-top:1em' class='pre'></div>")
	area.uniqueId()
	title.text(i18n.t("action_menu.user_id_range_start"))
	div.append(title)
	div.append(input)
	div.append(area)
	input.bind("keyup", function(event) {
		if (!is_enter(event)) {
			return
		}
		sync_ajax("/init/nodes/ajax_free_gids", ["gid_start"], area.attr("id"), function(){})
	})
}

//
// tool: topo
//
function tool_topo(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var node_ids = new Array()
	for (i=0;i<data.length;i++) {
		node_ids.push(data[i]['node_id'])
	}
	var svc_ids = new Array()
	for (i=0;i<data.length;i++) {
		svc_ids.push(data[i]['svc_id'])
	}
	osvc.flash.show({
		id: "topo-"+node_ids.join("")+svc_ids.join(""),
		cl: "icon dia16",
		text: i18n.t("action_menu.topology"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div><div>")
			$("#"+id).html(d)
			d.uniqueId()
			topology(d.attr("id"), {
				"node_ids": node_ids,
				"svc_ids": svc_ids,
				"display": ["nodes", "services", "countries", "cities", "buildings", "rooms", "racks", "enclosures", "hvs", "hvpools", "hvvdcs"]
			})
		}
	})
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
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "nodesantopo-"+nodes.join(""),
		cl: "icon hd16",
		text: i18n.t("action_menu.node_san_topo"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div style='padding:1em;overflow-y:auto'><div>")
			$("#"+id).html(d)
			d.uniqueId()
			sync_ajax('/init/ajax_node/ajax_nodes_stor?nodes='+nodes.join(","), [], d.attr("id"), function(){})
		}
	})
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
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "sysrepdiff-"+nodes.join(""),
		cl: "icon common16",
		text: i18n.t("action_menu.node_sysrep_diff"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div><div>")
			$("#"+id).html(d)
			d.uniqueId()
			sysrepdiff(d.attr("id"), {"nodes": nodes})
		}
	})
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
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "sysrep-"+nodes.join(""),
		cl: "icon log16",
		text: i18n.t("action_menu.node_sysrep"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div><div>")
			$("#"+id).html(d)
			d.uniqueId()
			sysrep(d.attr("id"), {"nodes": nodes})
		}
	})
}

//
// tool: svcdiff
//
function tool_svcdiff(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var svc_ids = new Array()
	for (i=0;i<data.length;i++) {
		svc_ids.push(data[i]['svc_id'])
	}
	osvc.flash.show({
		id: "svcdiff-"+svc_ids.join(""),
		cl: "icon common16",
		text: i18n.t("action_menu.svc_diff"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div style='padding:1em;overflow-y:auto'><div>")
			$("#"+id).html(d)
			d.uniqueId()
			svcdiff(d.attr("id"), {"svc_ids": svc_ids})
		}
	})
}

//
// tool: svc status log
//
function tool_services_status_log(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var services = new Array()
	for (i=0;i<data.length;i++) {
		services.push(data[i]['svc_id'])
	}
	osvc.flash.show({
		id: "services_status_log-"+services.join(""),
		cl: "icon avail16",
		text: i18n.t("action_menu.services_status_log"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div style='padding:1em;overflow-y:auto'><div>")
			$("#"+id).html(d)
			d.uniqueId()
			services_status_log(d.attr("id"), {"services": services})
		}
	})
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
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "nodediff-"+nodes.join(""),
		cl: "icon common16",
		text: i18n.t("action_menu.node_diff"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div style='padding:1em;overflow-y:auto'><div>")
			$("#"+id).html(d)
			d.uniqueId()
			nodediff(d.attr("id"), {"node_ids": nodes})
		}
	})
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
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "grpprf-"+nodes.join(""),
		cl: "icon chart16",
		text: i18n.t("action_menu.node_perf"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div style='padding:1em;overflow-y:auto'><div>")
			$("#"+id).html(d)
			d.uniqueId()
			node_stats(d.attr("id"), {
				"node_id": nodes,
				"view": "/init/static/views/nodes_stats.html",
				"controller": "/init/stats",
			})
		}
	})
}

//
// tool: obsolescence
//
function tool_obsolescence(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	if (data.length==0) {
		return ""
	}
	var nodes = new Array()
	for (i=0;i<data.length;i++) {
		nodes.push(data[i]['node_id'])
	}
	osvc.flash.show({
		id: "obsolescence-"+nodes.join(""),
		cl: "icon obs16",
		text: i18n.t("action_menu.obsolescence"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div><div>")
			$("#"+id).html(d)
			d.uniqueId()
			$.ajax({
				type: "POST",
				url: services_get_url() + "/init/nodes/ajax_obs_agg",
				data: {"nodes": nodes},
				success: function(msg){
					d.html(msg)
				}
			})
		}
	})
}

//
// data action: attach user privilege
//
function data_action_user_attach_privileges(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_USERS_GROUPS",
		"selector": generic_selector_privilege_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"user_id": data["id"]
			}
		}
	})
}

//
// data action: detach user privilege
//
function data_action_user_detach_privileges(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_USERS_GROUPS",
		"selector": generic_selector_privilege_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"user_id": data["id"]
			}
		}
	})
}

//
// data action: attach user groups
//
function data_action_user_attach_groups(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_USERS_GROUPS",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"user_id": data["id"]
			}
		}
	})
}

//
// data action: detach user groups
//
function data_action_user_detach_groups(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_USERS_GROUPS",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"user_id": data["id"]
			}
		}
	})
}

//
// data action: set user primary group
//
function data_action_user_set_primary_group(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	table_action_menu_focus_on_leaf(t, entry)

	// form elements
	var div = $("<div style='padding:0.5em'></div>")
	var label_group_id = $("<div data-i18n='action_menu.group_name'></div>")
	var input_group_id = $("<input id='group_id' class='oi'>")
	var yes_no = table_action_menu_yes_no('action_menu.submit', function(e){
		var _data = []
		div.empty()
		for (i=0;i<data.length;i++) {
			services_osvcpostrest("R_USER_PRIMARY_GROUP_SET", [data[i]['id'], input_group_id.attr("group_id")], "", "", function(jd) {
				if (rest_error(jd)) {
					div.html(services_error_fmt(jd))
				}
				if (jd.info && (jd.info.length > 0)) {
					div.append("<pre>"+jd.info+"</pre>")
				}
			},
			function(xhr, stat, error) {
				div.html(services_ajax_error_fmt(xhr, stat, error))
			})
		}
	})

	// groups autocomplete
	var groups = []
	services_osvcgetrest("R_GROUPS", "", {"limit": "0", "meta": "0", "orderby": "role", "filters": ["privilege F"]}, function(jd) {
		for (var i=0; i<jd.data.length; i++) {
			groups.push({
				"id": jd.data[i].id,
				"label": jd.data[i].role
			})
		}
	})
	input_group_id.autocomplete({
		source: groups,
		minLength: 0,
		focus: function(event, ui) {
			input_group_id.attr("group_id", ui.item.id)
		},
		select: function(event, ui) {
			input_group_id.attr("group_id", ui.item.id)
		}
	})

	// assemble the form elements
	div.append(label_group_id)
	div.append(input_group_id)
	div.append(yes_no)
	div.i18n()
	div.insertAfter(entry)
}

//
// data action: set user filterset
//
function data_action_user_set_filterset(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	table_action_menu_focus_on_leaf(t, entry)

	// form elements
	var div = $("<div style='padding:0.5em'></div>")
	var label_fset_id = $("<div data-i18n='col.Filterset'></div>")
	var input_fset_id = $("<input id='fset_id' class='oi'>")
	var yes_no = table_action_menu_yes_no('action_menu.submit', function(e){
		var _data = []
		div.empty()
		for (i=0;i<data.length;i++) {
			services_osvcpostrest("R_USER_FILTERSET_SET", [data[i]['id'], input_fset_id.attr("fset_id")], "", "", function(jd) {
				if (rest_error(jd)) {
					  div.html(services_error_fmt(jd))
				}
				if (jd.info && (jd.info.length > 0)) {
					  div.append("<pre>"+jd.info+"</pre>")
				}
			},
			function(xhr, stat, error) {
				div.html(services_ajax_error_fmt(xhr, stat, error))
			})
		}
	})

	// fset autocomplete
	var fsets = []
	services_osvcgetrest("R_FILTERSETS", "", {"limit": "0", "meta": "0", "orderby": "fset_name"}, function(jd) {
		for (var i=0; i<jd.data.length; i++) {
			fsets.push({
				"id": jd.data[i].id,
				"label": jd.data[i].fset_name
			})
		}
	})
	input_fset_id.autocomplete({
		source: fsets,
		minLength: 0,
		focus: function(event, ui) {
			input_fset_id.attr("fset_id", ui.item.id)
		},
		select: function(event, ui) {
			input_fset_id.attr("fset_id", ui.item.id)
		}
	})

	// assemble the form elements
	div.append(label_fset_id)
	div.append(input_fset_id)
	div.append(yes_no)
	div.i18n()
	div.insertAfter(entry)
}

//
// data action: add dns domain
//
function data_action_add_dns_domain(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_dns_domain.title",
		"request_service": "R_DNS_DOMAINS",
		"properties_tab": function(divid, data) {
			dns_domain_properties(divid, {"domain_id": data.id})
		},
		"createable_message": "action_menu.domain_createable",
		"inputs": [
			{
				"title": "action_menu.domain_name",
				"key": "name"
			}
		]
	})
}

function data_management_div(options) {
	var child_div = $("<div class='p-3'><div>")
	if (options.title) {
		var title = $("<h2></h2>").text(i18n.t(options.title))
		child_div.append(title)
	}
	return child_div
}

function data_action_generic_add(divid, options) {
	var div = $("#"+divid)
	var child_div = data_management_div(options)
	div.empty().append(child_div)

	// minimal create information
	for (var i=0; i<options.inputs.length; i++) {
		var input_data = options.inputs[i]
		var line = $("<div class='template_form_line'></div>")
		var title = $("<div></div>")
		title.text(i18n.t(input_data.title))
		var input = $("<input class='oi'></input>")
		input.attr("id", input_data.key)
		input.attr("placeholder", input_data.placeholder)
		line.append(title)
		line.append(input)
		child_div.append(line)
	}
	var info = $("<div></div>")
	info.uniqueId()
	info.css({"margin": "0.8em 0 0.8em 0"})
	child_div.append(info)
	child_div.find("div.template_form_line input").first().focus()

	var timer = null
	var xhr = null

	child_div.find("div.template_form_line input").bind("keyup", keyup_trigger)

	function keyup_trigger(e) {
		if (is_special_key(e)) {
			return
		}
		clearTimeout(timer)
		if (is_enter(e)) {
			if ($(this).val() == "") {
				return
			}
			var data = {}
			child_div.find("div.template_form_line input").each(function(){
				data[$(this).attr("id")] = $(this).val()
			})
			info.empty()
			spinner_add(info)
			xhr  = services_osvcpostrest(options.request_service, options.request_parameters, "", data, function(jd) {
				spinner_del(info)
				if (rest_error(jd)) {
					info.html(services_error_fmt(jd))
					return
				}
				// display the properties tab to set more properties
				options.properties_tab(info.attr("id"), jd.data[0])
			},
			function(xhr, stat, error) {
				info.html(services_ajax_error_fmt(xhr, stat, error))
			})
		} else {
			timer = setTimeout(function(){
				info.empty()
				if (xhr) {
					xhr.abort()
				}
				var data = {"filters": []}
				var inputs = child_div.find("div.template_form_line input")
				for (var i=0; i<inputs.length; i++) {
					var key = $(inputs[i]).attr("id")
					if (options.exist_check_keys && options.exist_check_keys.indexOf(key) < 0) {
						continue
					}
					var val = $(inputs[i]).val()
					if (!val || val.match(/^\s*$/)) {
						return
					}
					data.filters.push(key + " " + val)
				}
				spinner_add(info)
				services_osvcgetrest(options.request_service, "", data, function(jd) {
					xhr = null
					spinner_del(info)
					if (rest_error(jd)) {
						info.html(services_error_fmt(jd))
					}
					if (jd.data.length == 0) {
						info.text(i18n.t(options.createable_message))
						return
					}

					// display the properties tab
					options.properties_tab(info.attr("id"), jd.data[0])
				},
				function(xhr, stat, error) {
					info.html(services_ajax_error_fmt(xhr, stat, error))
				})
			}, 500)
		}
	}
}

//
// data action: delete dns domains
//
function data_action_del_dns_domains(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_DNS_DOMAINS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: sync dns domains
//
function data_action_sync_dns_domains(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var div = $("<div></div>")
	var info = $("<div></div>")
	div.append(info)
	div.insertAfter(entry)

	for (i=0; i<data.length; i++) {
		services_osvcputrest("R_DNS_DOMAIN_SYNC", [data[i]['id']], "", "", function(jd) {
			if (rest_error(jd)) {
				info.append("<pre>"+jd.error+"</pre>")
			}
			if (jd.info && (jd.info.length > 0)) {
				info.append("<pre>"+jd.info+"</pre>")
			}
		},
		function(xhr, stat, error) {
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}
}

//
// data action: delete dns records
//
function data_action_del_dns_records(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_DNS_RECORDS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add dns record
//
function data_action_add_dns_record(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_dns_record.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div.attr("id"), {"form_name": "internal_add_dns_record"})
}

//
// data action: add network segment
//
function data_action_add_network_segment(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_network_segment.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div.attr("id"), {"form_name": "internal_add_network_segment"})
}

//
// data action: add app publications
//
function data_action_add_app_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/apps_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"app_id": data["id"]
			}
		}
	})
}

//
// data action: del app publications
//
function data_action_del_app_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/apps_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"app_id": data["id"]
			}
		}
	})
}

//
// data action: add app responsibles
//
function data_action_add_app_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_APPS_RESPONSIBLES",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"app_id": data["id"]
			}
		}
	})
}

//
// data action: del app responsible
//
function data_action_del_app_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_APPS_RESPONSIBLES",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"app_id": data["id"]
			}
		}
	})
}

//
// data action: delete app
//
function data_action_del_apps(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_APPS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add app
//
function data_action_add_app(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_app.title",
		"request_service": "R_APPS",
		"properties_tab": function(divid, data) {
			app_properties(divid, {"app_id": data.id})
		},
		"createable_message": "action_menu.app_createable",
		"inputs": [
			{
				"title": "action_menu.app_name",
				"key": "app"
			}
		]
	})
}

//
// data action: lock user filterset
//
function data_action_user_lock_filterset(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var _data = new Array()
	for (i=0;i<data.length;i++) {
		_data.push({
			'id': data[i]['id'],
			'lock_filter': true
		})
	}
	services_osvcpostrest("R_USERS", "", "", _data, function(jd) {
		if (rest_error(jd)) {
			osvc.flash.error(services_error_fmt(jd))
		}
		if (jd.info && (jd.info.length > 0)) {
			osvc.flash.info(services_info_fmt(jd))
		}
	},
	function(xhr, stat, error) {
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})
}

//
// data action: unlock user filterset
//
function data_action_user_unlock_filterset(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var _data = new Array()
	for (i=0;i<data.length;i++) {
		_data.push({
			'id': data[i]['id'],
			'lock_filter': false
		})
	}
	services_osvcpostrest("R_USERS", "", "", _data, function(jd) {
		if (rest_error(jd)) {
			osvc.flash.error(services_error_fmt(jd))
		}
		if (jd.info && (jd.info.length > 0)) {
			osvc.flash.info(services_info_fmt(jd))
		}
	},
	function(xhr, stat, error) {
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})
}

//
// data action: delete user
//
function data_action_del_user(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_USERS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete group
//
function data_action_del_group(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_GROUPS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: del groups
//
function data_action_del_groups(divid) {
	var div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.del_groups.title"
	})
	div.empty().append(child_div)
	_data_action_generic_selector(child_div, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_GROUPS",
		"selector": generic_selector_org_groups,
		"selector_options": {
			"exclude": ["Everybody"]
		},
		"no_lines": true,
		"request_data_entry": function(selected) {
			return {
				"id": selected
			}
		}
	})
}

//
// data action: add group
//
function data_action_add_group(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_group.title",
		"request_service": "R_GROUPS",
		"properties_tab": function(divid, data) {
			group_properties(divid, {"group_id": data.id})
		},
		"createable_message": "action_menu.group_createable",
		"inputs": [
			{
				"title": "action_menu.group_name",
				"key": "role"
			}
		]
	})
}

//
// data action: add user
//
function data_action_add_user(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_user.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div, {"form_name": "internal_add_user"})
}

//
// data action: add node
//
function data_action_add_node(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_node.title",
		"request_service": "R_NODES",
		"properties_tab": function(divid, data) {
			node_properties(divid, {"node_id": data.node_id})
		},
		"createable_message": "action_menu.node_createable",
		"inputs": [
			{
				"title": "action_menu.nodename",
				"key": "nodename"
			}
		]
	})
}

//
// data action: add service
//
function data_action_add_service(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_service.title",
		"request_service": "R_SERVICES",
		"properties_tab": function(divid, data) {
			service_tabs(divid, {
				"svc_id": data.svc_id,
				"show_tabs": ["node_tabs.properties", "service_tabs.env"],
			})
		},
		"createable_message": "action_menu.service_createable",
		"exist_check_keys": ["svcname"],
		"inputs": [
			{
				"title": "col.Service",
				"key": "svcname"
			}
		]
	})
}

//
// data action: set low threshold
//
function data_action_chk_instance_set_low_threshold(t, e) {
	data_action_chk_instance_set_threshold(t, e, "low")
}

function data_action_chk_instance_set_high_threshold(t, e) {
	data_action_chk_instance_set_threshold(t, e, "high")
}

function data_action_chk_instance_set_threshold(t, e, threshold) {
	var entry = $(e.target)
	table_action_menu_focus_on_leaf(t, entry)
	//entry.next("[name=tool]").remove()
	var div = $("<div name='tool' style='padding:0.5em'></div>")
	var input = $("<input class='oi'>")
	div.append(input)
	div.insertAfter(entry)
	input.focus()

	// result
	var result = $("<div></div>")
	result.css({"width": entry.width(), "padding": "0.3em"})
	result.insertAfter(div)

	input.bind("keyup", function(event) {
		if (!is_enter(event)) {
			return
		}
		var cache_id = entry.attr("cache_id")
		var data = t.action_menu_data_cache[cache_id]
		var _data = new Array()
		for (i=0;i<data.length;i++) {
			var d = {
				'node_id': data[i]['node_id'],
				'svc_id': data[i]['svc_id'],
				'chk_type': data[i]['chk_type'],
				'chk_instance': data[i]['chk_instance'],
			}
			if (threshold == "low") {
				d['chk_low'] = $(this).val()
			} else if (threshold == "high") {
				d['chk_high'] = $(this).val()
			} else {
				continue
			}
			_data.push(d)
		}
		result.empty()
		xhr  = services_osvcpostrest("R_CHECKS_SETTINGS", "", "", _data, function(jd) {
			if (rest_error(jd)) {
				result.html(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				result.html(services_info_fmt(jd))
			}
		},
		function(xhr, stat, error) {
			result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	})
}

//
// data action: delete check instances
//
function data_action_chk_instance_reset_thresholds(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_CHECKS_SETTINGS",
		"request_data_entry": function(data) {
			return {
				'node_id': data['node_id'],
				'svc_id': data['svc_id'],
				'chk_type': data['chk_type'],
				'chk_instance': data['chk_instance']
			}
		}
	})
}

//
// data action: delete check instances
//
function data_action_chk_instance_delete(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_CHECKS",
		"request_data_entry": function(data) {
			return {
				'node_id': data['node_id'],
				'svc_id': data['svc_id'],
				'chk_type': data['chk_type'],
				'chk_instance': data['chk_instance']
			}
		}
	})
}

//
// data action: add contextual threshold
//
function data_action_add_contextual_thresholds(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_contextual_thresholds.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div, {"form_name": "internal_add_contextual_thresholds"})
}

//
// data action: delete contextual threshold
//
function data_action_delete_contextual_thresholds(divid) {
	var div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.del_contextual_thresholds.title"
	})
	div.empty().append(child_div)
	_data_action_generic_selector(child_div, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_CHECKS_CONTEXTUAL_SETTINGS",
		"selector": generic_selector_checks_contextual_settings,
		"request_data_entry": function(selected, data) {
			return {
				"id": selected
			}
		}
	})
}

//
// data action: add default threshold
//
function data_action_add_default_thresholds(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_default_thresholds.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div, {"form_name": "internal_add_default_thresholds"})
}

//
// data action: delete default threshold
//
function data_action_delete_default_thresholds(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/checks/defaults",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}


//
// data action: cancel queued actions
//
function data_action_action_queue_cancel(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var _data = new Array()
	for (i=0;i<data.length;i++) {
		_data.push({
			'id': data[i]['id'],
			'status': 'C'
		})
	}
	services_osvcpostrest("R_ACTIONS", "", "", _data, function(jd) {
		if (rest_error(jd)) {
			osvc.flash.error(services_error_fmt(jd))
		}
		if (jd.info && (jd.info.length > 0)) {
			osvc.flash.info(services_info_fmt(jd))
		}
		t.refresh_menu_data_cache(entry, e)
	},
	function(xhr, stat, error) {
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})
}

//
// data action: redo queued actions
//
function data_action_action_queue_redo(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var _data = new Array()
	for (i=0;i<data.length;i++) {
		_data.push({
			'id': data[i]['id'],
			'status': 'W'
		})
	}
	services_osvcpostrest("R_ACTIONS", "", "", _data, function(jd) {
		if (rest_error(jd)) {
			osvc.flash.error(services_error_fmt(jd))
		}
		if (jd.info && (jd.info.length > 0)) {
			osvc.flash.info(services_info_fmt(jd))
		}
		t.refresh_menu_data_cache(entry, e)
	},
	function(xhr, stat, error) {
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})
}

//
// data action: delete docker registries
//
function data_action_delete_docker_registries(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/docker/registries",
		"request_data_entry": function(data) {
			return {
				'id': data['registry_id']
			}
		}
	})
}

//
// data action: delete docker tags
//
function data_action_delete_docker_repositories(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/docker/repositories",
		"request_data_entry": function(data) {
			return {
				'id': data['repository_id']
			}
		}
	})
}

//
// data action: delete docker tags
//
function data_action_delete_docker_tags(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/docker/tags",
		"request_data_entry": function(data) {
			return {
				'id': data['tag_id']
			}
		}
	})
}

//
// data action: delete nodes
//
function data_action_delete_nodes(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_NODES",
		"request_data_entry": function(data) {
			return {
				'node_id': data['node_id']
			}
		}
	})
}

//
// data action: delete services
//
function data_action_delete_svcs(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_SERVICES",
		"request_data_entry": function(data) {
			return {
				'svc_id': data['svc_id']
			}
		}
	})
}

//
// data action: delete compliance status
//
function data_action_delete_compliance_status(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_COMPLIANCE_STATUS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add network
//
function data_action_add_network(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_network.title",
		"request_service": "R_NETWORKS",
		"properties_tab": function(divid, data) {
			network_properties(divid, {"network_id": data.id})
		},
		"createable_message": "action_menu.net_createable",
		"inputs": [
			{
				"title": "action_menu.network",
				"key": "network",
				"placeholder": "192.168.0.0"
			},
			{
				"title": "action_menu.netmask",
				"key": "netmask",
				"placeholder": "24"
			}
		]
	})
}

//
// data action: add networks_segments responsibles
//
function data_action_add_networks_segments_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/networks/segments_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"seg_id": data["seg_id"],
				"net_id": data["net_id"]
			}
		}
	})
}

//
// data action: del networks_segments responsible
//
function data_action_del_networks_segments_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/networks/segments_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"seg_id": data["seg_id"],
				"net_id": data["net_id"]
			}
		}
	})
}

//
// data action: delete networks segments
//
function data_action_delete_networks_segments(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/networks/segments",
		"request_data_entry": function(data) {
			return {
				'net_id': data['net_id'],
				'seg_id': data['seg_id']
			}
		}
	})
}

//
// data action: delete networks
//
function data_action_delete_networks(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_NETWORKS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete service instances
//
function data_action_delete_svc_instances(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_SERVICE_INSTANCES",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete service resources
//
function data_action_delete_resources(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/resources",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete node ips
//
function data_action_delete_node_ips(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/ips",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: acknowledge action
//
function data_action_ack_actions(t, e) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var scope = entry.attr("scope")
	var selector = $.data(entry[0], "selector")
	var data = t.action_menu_data_cache[cache_id]
	var post_data = new Array()

	table_action_menu_focus_on_leaf(t, entry)

	// comment textarea
	var form = $("<form></form>")
	var c = $("<textarea class='oi' style='width:100%;height:8em'></textarea>")
	c.uniqueId()
	var label = $("<div data-i18n='action_menu.ack_comment'></div>")
	form.append(label)
	form.append(c)
	c.bind("click", function(event) {
		event.stopPropagation()
	})
	table_action_menu_focus_on_leaf(t, entry)
	var yes_no = table_action_menu_yes_no('action_menu.submit', function(e){
		var comment = $(e.target).parents("form").first().find("textarea").val()
		for (i=0;i<data.length;i++) {
			if (data[i].ack) {
				// avoid acknowledgeing already acknowledged actions
				continue
			}
			post_data.push({
				'id': data[i]['id'],
				'ack': 1,
				'acked_comment': comment
			})
		}
		result.empty()
		services_osvcpostrest("R_SERVICES_ACTIONS", "", "", post_data, function(jd) {
			if (rest_error(jd)) {
				result.html(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				result.html(services_info_fmt(jd))
			}
			t.refresh_menu_data_cache(entry, e)
		},
		function(xhr, stat, error) {
			result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	})
	form.append(yes_no)
	form.insertAfter(entry)

	// result
	var result = $("<div></div>")
	result.css({"width": entry.width(), "padding": "0.3em"})
	result.insertAfter(form)

	c.focus()
}

function data_action_import(divid, options) {
	var parent_div = $("#"+divid)
	var div = data_management_div({"title": options.title})
	parent_div.empty().append(div)

	var line = $("<div class='template_form_line'></div>")
	var title = $("<div></div>")
	title.text(i18n.t("action_menu.json_data"))
	var input = $("<textarea style='min-width:30em;height:30em' class='oi'>")
	var button = $("<button class='button_div icon fa-upload'></button>")
	button.text(i18n.t("action_menu.submit"))
	input.css({"margin": "1em 0"})
	input.attr("id", "data")
	line.append(title)
	line.append(input)
	div.append(line)
	div.append(button)
	input.focus()

	var info = $("<div></div>")
	info.uniqueId()
	info.css({"margin": "0.8em 0 0.8em 0"})
	div.append(info)
	div.find("div.template_form_line input").first().focus()

	var timer = null
	var xhr = null

	button.click(function(e) {
		var data = JSON.parse(input.val())
		info.empty()
		spinner_add(info)
		xhr  = services_osvcpostrest(options.url, "", "", data, function(jd) {
			spinner_del(info)
			info.empty()
			if (rest_error(jd)) {
				info.append(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				info.append(services_info_fmt(jd))
			}
		},
		function(xhr, stat, error) {
			info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	})
}

//
// data action: import report
//
function data_action_import_report(divid) {
	data_action_import(divid, {
		url: "/reports/import",
		title: "menu.data_management.import_report.title"
	})
}

//
// data action: import compliance design
//
function data_action_import_compliance_design(divid) {
	data_action_import(divid, {
		url: "/compliance/import",
		title: "menu.data_management.import_compliance_design.title"
	})
}

//
// data action: add report
//
function data_action_add_report(t, e) {
	data_action_generic_add(t, {
		"title": "menu.data_management.add_report.title",
		"request_service": "/reports",
		"properties_tab": function(divid, data) {
			report_tabs(divid, {"report_id": data.id, "report_name": data.report_name})
		},
		"createable_message": "action_menu.report_createable",
		"inputs": [
			{
				"title": "report_properties.report_name",
				"key": "report_name"
			}
		]
	})
}

//
// data action: delete reports
//
function data_action_del_reports(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/reports",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add reports responsibles
//
function data_action_add_reports_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/reports_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"report_id": data["id"]
			}
		}
	})
}

//
// data action: del reports responsible
//
function data_action_del_reports_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/reports_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"report_id": data["id"]
			}
		}
	})
}

//
// data action: add reports publications
//
function data_action_add_reports_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/reports_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"report_id": data["id"]
			}
		}
	})
}

//
// data action: del reports publications
//
function data_action_del_reports_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/reports_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"report_id": data["id"]
			}
		}
	})
}


//
// data action: add chart
//
function data_action_add_chart(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_chart.title",
		"request_service": "/reports/charts",
		"properties_tab": function(divid, data) {
			chart_tabs(divid, {"chart_id": data.id, "chart_name": data.chart_name})
		},
		"createable_message": "action_menu.chart_createable",
		"inputs": [
			{
				"title": "chart_properties.chart_name",
				"key": "chart_name"
			}
		]
	})
}

//
// data action: add charts responsibles
//
function data_action_add_charts_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/reports/charts_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"chart_id": data["id"]
			}
		}
	})
}

//
// data action: del charts responsible
//
function data_action_del_charts_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/reports/charts_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"chart_id": data["id"]
			}
		}
	})
}

//
// data action: add charts publications
//
function data_action_add_charts_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/reports/charts_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"chart_id": data["id"]
			}
		}
	})
}

//
// data action: del charts publications
//
function data_action_del_charts_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/reports/charts_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"chart_id": data["id"]
			}
		}
	})
}

//
// data action: delete filters
//
function data_action_del_filters(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/filters",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete filtersets
//
function data_action_del_filtersets(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/filtersets",
		"request_data_entry": function(data) {
			return {
				'id': data['fset_id']
			}
		}
	})
}

//
// data action: add filterset
//
function data_action_add_filterset(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_filterset.title",
		"request_service": "/filtersets",
		"properties_tab": function(divid, data) {
			filterset_tabs(divid, {"fset_name": data.fset_name})
		},
		"createable_message": "action_menu.fset_createable",
		"inputs": [
			{
				"title": "fset_properties.name",
				"key": "fset_name"
			}
		]
	})
}

//
// data action: add docker registry
//
function data_action_add_docker_registry(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_docker_registry.title",
		"request_service": "/docker/registries",
		"properties_tab": function(divid, data) {
			docker_registry_tabs(divid, {"registry_service": data.service})
		},
		"createable_message": "action_menu.docker_registry_createable",
		"inputs": [
			{
				"title": "docker_properties.service",
				"key": "service"
			}
		]
	})
}

//
// data action: set fitlersets operator
//
function data_action_filtersets_set_operator(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filtersets",
		"selector": generic_selector_operator,
		"request_data_entry": function(selected, data) {
			return {
				"parent_fset_id": data.fset_id,
				"child_fset_id": data.encap_fset_id,
				"f_log_op": selected
			}
		}
	})
}

//
// data action: set filtersets order
//
function data_action_filtersets_set_order(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filtersets",
		"selector": generic_selector_order,
		"request_data_entry": function(selected, data) {
			return {
				"parent_fset_id": data.fset_id,
				"child_fset_id": data.encap_fset_id,
				"f_order": selected
			}
		}
	})
}

//
// data action: set fitlers operator
//
function data_action_filters_set_operator(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filters",
		"selector": generic_selector_operator,
		"request_data_entry": function(selected, data) {
			return {
				"fset_id": data.fset_id,
				"f_id": data.f_id,
				"f_log_op": selected
			}
		}
	})
}

//
// data action: set filters order
//
function data_action_filters_set_order(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filters",
		"selector": generic_selector_order,
		"request_data_entry": function(selected, data) {
			return {
				"fset_id": data.fset_id,
				"f_id": data.f_id,
				"f_order": selected
			}
		}
	})
}

//
// data action: attach filtersets to filtersets
//
function data_action_attach_filtersets(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filtersets",
		"selector": generic_selector_filtersets,
		"request_data_entry": function(selected, data) {
			return {
				"parent_fset_id": data.fset_id,
				"child_fset_id": selected
			}
		}
	})
}

//
// data action: attach filters to filtersets
//
function data_action_attach_filters(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/filtersets_filters",
		"selector": generic_selector_filters,
		"request_data_entry": function(selected, data) {
			return {
				"fset_id": data.fset_id,
				"f_id": selected
			}
		}
	})
}

//
// data action: detach filtersets from filtersets
//
function data_action_detach_filtersets(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/filtersets_filtersets",
		"request_data_entry": function(data) {
			return {
				'parent_fset_id': data['fset_id'],
				'child_fset_id': data['encap_fset_id']
			}
		}
	})
}

//
// data action: detach filters from filtersets
//
function data_action_detach_filters(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/filtersets_filters",
		"request_data_entry": function(data) {
			return {
				'fset_id': data['fset_id'],
				'f_id': data['f_id']
			}
		}
	})
}


//
// data action: delete charts
//
function data_action_del_charts(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/reports/charts",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add metric
//
function data_action_add_metric(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_metric.title",
		"request_service": "/reports/metrics",
		"properties_tab": function(divid, data) {
			metric_tabs(divid, {"metric_id": data.id, "metric_name": data.metric_name})
		},
		"createable_message": "action_menu.metric_createable",
		"inputs": [
			{
				"title": "metric_properties.metric_name",
				"key": "metric_name"
			}
		]
	})
}

//
// data action: add metrics publications
//
function data_action_add_metrics_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/reports/metrics_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"metric_id": data["id"]
			}
		}
	})
}

//
// data action: del metrics publications
//
function data_action_del_metrics_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/reports/metrics_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"metric_id": data["id"]
			}
		}
	})
}


//
// data action: delete metrics
//
function data_action_del_metrics(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/reports/metrics",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete tag
//
function data_action_del_tag(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_TAGS",
		"request_data_entry": function(data) {
			return {
				'tag_id': data['tag_id']
			}
		}
	})
}

//
// data action: add tag
//
function data_action_add_tag(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_tag.title",
		"request_service": "R_TAGS",
		"properties_tab": function(divid, data) {
			$("#"+divid).html(i18n.t("action_menu.tag_not_createable"))
		},
		"createable_message": "action_menu.tag_createable",
		"inputs": [
			{
				"title": "action_menu.tag_name",
				"key": "tag_name"
			}
		]
	})
}

//
// data action: add form
//
function data_action_add_form(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_form.title",
		"request_service": "R_FORMS",
		"properties_tab": function(divid, data) {
			form_tabs(divid, {"form_id": data.id, "form_name": data.form_name})
		},
		"createable_message": "action_menu.form_createable",
		"inputs": [
			{
				"title": "action_menu.form_name",
				"key": "form_name"
			}
		]
	})
}

//
// data action: delete modulesets
//
function data_action_del_modulesets(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/compliance/modulesets",
		"request_data_entry": function(data) {
			return {
				'id': data['modset_id']
			}
		}
	})
}

//
// data action: add moduleset publication
//
function data_action_add_moduleset_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/compliance/modulesets_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"modset_id": data["modset_id"]
			}
		}
	})
}

//
// data action: del moduleset publication
//
function data_action_del_moduleset_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/compliance/modulesets_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"modset_id": data["modset_id"]
			}
		}
	})
}

//
// data action: add moduleset responsibles
//
function data_action_add_moduleset_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/compliance/modulesets_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"modset_id": data["modset_id"]
			}
		}
	})
}

//
// data action: del moduleset responsible
//
function data_action_del_moduleset_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/compliance/modulesets_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"modset_id": data["modset_id"]
			}
		}
	})
}

//
// data action: delete rulesets
//
function data_action_del_rulesets(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/compliance/rulesets",
		"request_data_entry": function(data) {
			return {
				'id': data['ruleset_id']
			}
		}
	})
}

//
// data action: add ruleset publication
//
function data_action_add_ruleset_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/compliance/rulesets_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"ruleset_id": data["ruleset_id"]
			}
		}
	})
}

//
// data action: del ruleset publication
//
function data_action_del_ruleset_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/compliance/rulesets_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"ruleset_id": data["ruleset_id"]
			}
		}
	})
}

//
// data action: add ruleset responsibles
//
function data_action_add_ruleset_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/compliance/rulesets_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"ruleset_id": data["ruleset_id"]
			}
		}
	})
}

//
// data action: del ruleset responsible
//
function data_action_del_ruleset_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/compliance/rulesets_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"ruleset_id": data["ruleset_id"]
			}
		}
	})
}

//
// data action: delete forms
//
function data_action_del_form(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_FORMS",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add form publication
//
function data_action_add_form_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_FORMS_PUBLICATIONS",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"form_id": data["id"]
			}
		}
	})
}

//
// data action: del form publication
//
function data_action_del_form_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_FORMS_PUBLICATIONS",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"form_id": data["id"]
			}
		}
	})
}

//
// data action: add form responsibles
//
function data_action_add_form_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_FORMS_RESPONSIBLES",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"form_id": data["id"]
			}
		}
	})
}

//
// data action: del form responsible
//
function data_action_del_form_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_FORMS_RESPONSIBLES",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"form_id": data["id"]
			}
		}
	})
}

//
// data action: add safe file publication
//
function data_action_add_safe_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/safe/files_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"file_id": data["id"]
			}
		}
	})
}

//
// data action: del safe file publication
//
function data_action_del_safe_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/safe/files_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"file_id": data["id"]
			}
		}
	})
}

//
// data action: add safe file responsibles
//
function data_action_add_safe_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/safe/files_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"file_id": data["id"]
			}
		}
	})
}

//
// data action: del safe file responsible
//
function data_action_del_safe_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/safe/files_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"file_id": data["id"]
			}
		}
	})
}

//
// data action: attach tags to services
//
function data_action_services_tags_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_TAGS_SERVICES",
		"selector": generic_selector_tags,
		"request_data_entry": function(selected, data) {
			return {
				"tag_id": selected,
				"svc_id": data["svc_id"]
			}
		}
	})
}

//
// data action: attach tags to nodes
//
function data_action_nodes_tags_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_TAGS_NODES",
		"selector": generic_selector_tags,
		"request_data_entry": function(selected, data) {
			return {
				"tag_id": selected,
				"node_id": data["node_id"]
			}
		}
	})
}

//
// data action: detach nodes tags
//
function data_action_nodes_tags_detach(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_TAGS_NODES",
		"request_data_entry": function(data) {
			return {
				'tag_id': data['tag_id'],
				'node_id': data['node_id']
			}
		}
	})
}

//
// data action: detach services tags
//
function data_action_services_tags_detach(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_TAGS_SERVICES",
		"request_data_entry": function(data) {
			return {
				'tag_id': data['tag_id'],
				'svc_id': data['svc_id']
			}
		}
	})
}

//
// data action: detach nodes modulesets
//
function data_action_nodes_modsets_detach_no_selector(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_MODULESETS_NODES",
		"request_data_entry": function(data) {
			return {
				'modset_id': data['modset_id'],
				'node_id': data['node_id']
			}
		}
	})
}

//
// data action: detach services modulesets
//
function data_action_services_modsets_detach_no_selector(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_MODULESETS_SERVICES",
		"request_data_entry": function(data) {
			return {
				'modset_id': data['modset_id'],
				'svc_id': data['svc_id'],
				'slave': data['slave']
			}
		}
	})
}

//
// data action: detach nodes rulesets
//
function data_action_nodes_rulesets_detach_no_selector(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_RULESETS_NODES",
		"request_data_entry": function(data) {
			return {
				'ruleset_id': data['ruleset_id'],
				'node_id': data['node_id']
			}
		}
	})
}

//
// data action: detach services rulesets
//
function data_action_services_rulesets_detach_no_selector(t, e) {
	data_action_generic(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_RULESETS_SERVICES",
		"request_data_entry": function(data) {
			return {
				'ruleset_id': data['ruleset_id'],
				'svc_id': data['svc_id'],
				'slave': data['slave']
			}
		}
	})
}

//
// data action: attach modsets to nodes
//
function data_action_nodes_modsets_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_COMPLIANCE_MODULESETS_NODES",
		"selector": generic_selector_modsets,
		"request_data_entry": function(selected, data) {
			return {
				"modset_id": selected,
				"node_id": data["node_id"]
			}
		}
	})
}

//
// data action: attach modsets to services
//
function data_action_services_modsets_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_COMPLIANCE_MODULESETS_SERVICES",
		"selector": generic_selector_modsets,
		"request_data_entry": function(selected, data) {
			return {
				"modset_id": selected,
				"svc_id": data["svc_id"],
				"slave": data["slave"]
			}
		}
	})
}

//
// data action: attach rulesets to nodes
//
function data_action_nodes_rulesets_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_COMPLIANCE_RULESETS_NODES",
		"selector": generic_selector_rulesets,
		"request_data_entry": function(selected, data) {
			return {
				"ruleset_id": selected,
				"node_id": data["node_id"]
			}
		}
	})
}

//
// data action: attach rulesets to services
//
function data_action_services_rulesets_attach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "R_COMPLIANCE_RULESETS_SERVICES",
		"selector": generic_selector_rulesets,
		"request_data_entry": function(selected, data) {
			return {
				"ruleset_id": selected,
				"svc_id": data["svc_id"],
				"slave": data["slave"]
			}
		}
	})
}

//
// data action: detach modsets from nodes
//
function data_action_nodes_modsets_detach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_MODULESETS_NODES",
		"selector": generic_selector_modsets,
		"request_data_entry": function(selected, data) {
			return {
				"modset_id": selected,
				"node_id": data["node_id"]
			}
		}
	})
}

//
// data action: detach modsets from services
//
function data_action_services_modsets_detach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_MODULESETS_SERVICES",
		"selector": generic_selector_modsets,
		"request_data_entry": function(selected, data) {
			return {
				"modset_id": selected,
				"svc_id": data["svc_id"],
				"slave": data["slave"]
			}
		}
	})
}

//
// data action: detach rulesets from nodes
//
function data_action_nodes_rulesets_detach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_RULESETS_NODES",
		"selector": generic_selector_rulesets,
		"request_data_entry": function(selected, data) {
			return {
				"ruleset_id": selected,
				"node_id": data["node_id"]
			}
		}
	})
}

//
// data action: detach rulesets from services
//
function data_action_services_rulesets_detach(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "R_COMPLIANCE_RULESETS_SERVICES",
		"selector": generic_selector_rulesets,
		"request_data_entry": function(selected, data) {
			return {
				"ruleset_id": selected,
				"svc_id": data["svc_id"],
				"slave": data["slave"]
			}
		}
	})
}

//
// customizable data action tool
//
function data_action_generic(t, e, options) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]
	var request_data = new Array()
	table_action_menu_focus_on_leaf(t, entry)

	// result
	var result = $("<div></div>")
	result.css({"width": entry.width(), "padding": "0.3em"})
	result.insertAfter(entry)

	for (i=0;i<data.length;i++) {
		request_data.push(options.request_data_entry(data[i]))
	}

	if (options.confirmation) {
		var yes_no = table_action_menu_yes_no('action_menu.submit', function(event){
			do_action(event)
		})
		yes_no.insertAfter(result)
	} else {
		do_action(e)
	}

	function do_action(e) {
		options.requestor(options.request_service, options.request_parameters, "", request_data, function(jd) {
			if (rest_error(jd)) {
				result.html(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				result.html(services_info_fmt(jd))
			}
			t.refresh_menu_data_cache(entry, e)
		},
		function(xhr, stat, error) {
			result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}
}

//
// customizable data delete action tool
//
function data_action_generic_delete(t, e, options) {
	options.requestor = services_osvcdeleterest
	options.confirmation = true
	data_action_generic(t, e, options)
}

//
// customizable selector based data action
//
function data_action_generic_selector(t, e, options) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	table_action_menu_focus_on_leaf(t, entry)
	options.data = t.action_menu_data_cache[cache_id]
	options.callback = function(){
		t.refresh_menu_data_cache(entry, e)
	}
	// form
	var form = $("<form></form>")
	form.css({"width": "100%", "padding": "0.3em"})
	form.insertAfter(entry)
	_data_action_generic_selector(form, options)
}

function _data_action_generic_selector(form, options) {
	var request_data = new Array()

	// selector
	var selector_div = $("<div></div>")
	selector_div.uniqueId()
	form.append(selector_div)
	var selector_instance = options.selector(selector_div.attr("id"), options.selector_options)
	var yes_no = table_action_menu_yes_no('action_menu.submit', function(e){
		if (options.no_lines || !options.data) {
			var selected = selector_instance.get_selected()
			for (j=0;j<selected.length;j++) {
				request_data.push(options.request_data_entry(selected[j]))
			}
		} else {
			var selected = selector_instance.get_selected()
			for (i=0;i<options.data.length;i++) {
				for (j=0;j<selected.length;j++) {
					request_data.push(options.request_data_entry(selected[j], options.data[i]))
				}
			}
		}
		options.requestor(options.request_service, "", "", request_data, function(jd) {
			if (rest_error(jd)) {
				form.html(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				form.html(services_info_fmt(jd))
			}
			if (options.callback) {
				options.callback()
			}
		},
		function(xhr, stat, error) {
			form.html(services_ajax_error_fmt(xhr, stat, error))
		})
	})
	form.append(yes_no)
	return form
}

//
// agent actions
//

//
// agent action: provisioning
//
function agent_action_provisioning(t, e) {
	var entry = $(e.target)

	table_action_menu_focus_on_leaf(t, entry)
	var div = $("<div class='template_selector'></div>")
	var title = $("<div data-i18n='action_menu.provisioning_selector_title'></div>").i18n()
	div.append(title)
	div.insertAfter(entry)

	spinner_add(div)
	services_osvcgetrest("R_PROVISIONING_TEMPLATES", "", "", function(jd) {
		spinner_del(div)
		if (rest_error(jd)) {
			osvc.flash.error(services_error_fmt(jd))
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

			// display the beautified template definition
			var display_beautified = $("<div class='template_beautified' name='beautified'><div>")
			display_beautified.html(decorator_tpl_definition(d.tpl_definition))
			tpl_form.append(display_beautified)
			tpl_form.append("<br>")

			// get keys from the template definition
			var keys = {"svcname": ""}
			var lines = d.tpl_definition.split("\n")
			var inb = false
			for (var j=0; j<lines.length; j++) {
				var line = lines[j].trim()
				if (line == "[env]") {
					inb = true
					continue
				}
				if (!inb) {
					continue
				}
				if (line.match(/^\s*\[.+\]\s*$/)) {
					if (line == "[env]") {
						continue
					}
					inb = false
					continue
				}

				var k = line.indexOf("=")
				if (k < 0) {
					continue
				}
				var key = line.slice(0, k).trim()
				if (key == "") {
					continue
				}
				var val = line.slice(k+1, line.length).trim()
				keys[key] = val
			}

			// for each key add a text input to the form
			for (key in keys) {
				var val = keys[key]
				var line = $("<div class='template_form_line'></div>")
				var title = $("<div></div>")
				title.text(key)
				var input = $("<input class='oi'></input>")
				input.attr("key", key)
				input.val(val)
				line.append(title)
				line.append(input)
				tpl_form.append(line)
			}

			// add submit/cancel buttons
			var yes_no = table_action_menu_yes_no('action_menu.provisioning_submit', function(e){
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
					d.node_id = data[i].node_id
					put_data.push(d)
				}

				// animate to highlight the enqueueing
				table_action_menu_click_animation(t)

				// put the provisioning action in queue
				services_osvcputrest("R_PROVISIONING_TEMPLATE", [tpl_id], "", put_data, function(jd) {
					if (rest_error(jd)) {
						osvc.flash.error(services_error_fmt(jd))
					}
					if (jd.info && (jd.info.length > 0)) {
						osvc.flash.info(services_info_fmt(jd))
					}
				},
				function(xhr, stat, error) {
					osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
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
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})

}

//
// data action: delete quotas
//
function data_action_del_quotas(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "R_ARRAY_DISKGROUP_QUOTAS",
		"request_parameters": [0, 0],
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add quota
//
function data_action_add_quota(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.add_quota.title"
	})
	div.empty().append(child_div)
	var form_div = $("<div></div>")
	form_div.uniqueId()
	child_div.append(form_div)
	form(form_div.attr("id"), {"form_name": "internal_add_quota"})
}

//
// data action: refresh obsolescence list and alerts
//
function data_action_obs_refresh(divid) {
	div = $("#"+divid)
	var child_div = data_management_div({
		"title": "menu.data_management.refresh_obsolescence.title"
	})
	div.empty().append(child_div)
	services_osvcputrest("/obsolescence/refresh", "", "", "", function(jd) {
		if (rest_error(jd)) {
			child_div.append(services_error_fmt(jd))
		}
		if (jd.info && (jd.info.length > 0)) {
			child_div.append(services_info_fmt(jd))
		}
	},
	function(xhr, stat, error) {
		child_div.append(services_ajax_error_fmt(xhr, stat, error))
	})
}

//
// data action: delete obsolescence settings
//
function data_action_obs_del(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/obsolescence/settings",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: delete obsolescence settings
//
function data_action_obs_set_warn_date(t, e) {
	return data_action_obs_set(t, e, {
		"label": "col.Warn date",
		"key": "obs_warn_date",
	})
}

function data_action_obs_set_alert_date(t, e) {
	return data_action_obs_set(t, e, {
		"label": "col.Alert date",
		"key": "obs_alert_date",
	})
}

function data_action_obs_set(t, e, options) {
	var entry = $(e.target)
	var cache_id = entry.attr("cache_id")
	var data = t.action_menu_data_cache[cache_id]

	// create and focus tool area
	table_action_menu_focus_on_leaf(t, entry)
	var div = $("<div></div>")
	div.uniqueId()
	div.insertAfter(entry)

	// minimal create information
	var line = $("<div class='template_form_line'></div>")
	var title = $("<div></div>")
	title.text(i18n.t(options.label))
	var input = $("<input class='oi'></input>")
	input.uniqueId()
	input.datetimepicker({dateFormat:'yy-mm-dd'})
	var info = $("<div></div>")
	info.uniqueId()
	info.css({"margin": "0.8em 0 0.8em 0"})
	line.append(title)
	line.append(input)
	div.append(line)
	div.append(info)
	input.focus()

	input.bind("keyup", function(e) {
		if (!is_enter(e)) {
			return
		}
		var _data = new Array()
		for (i=0;i<data.length;i++) {
			var d = {
				'id': data[i]['id'],
			}
			d[options.key] = input.val()
			_data.push(d)
		}
		info.empty()
		spinner_add(info)
		services_osvcpostrest("/obsolescence/settings", "", "", _data, function(jd) {
			spinner_del(info)
			if (rest_error(jd)) {
				info.html(services_error_fmt(jd))
			}
			if (jd.info && (jd.info.length > 0)) {
				info.html(services_info_fmt(jd))
			}
			t.refresh_menu_data_cache(entry, e)
		},
		function(xhr, stat, error) {
			info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	})
}

//
// data action: add prov template
//
function data_action_add_prov_template(divid) {
	data_action_generic_add(divid, {
		"title": "menu.data_management.add_prov_template.title",
		"request_service": "/provisioning_templates",
		"properties_tab": function(divid, data) {
			prov_template_tabs(divid, {"tpl_id": data.id, "tpl_name": data.tpl_name})
		},
		"createable_message": "action_menu.tpl_createable",
		"inputs": [
			{
				"title": "action_menu.tpl_name",
				"key": "tpl_name"
			}
		]
	})
}

//
// data action: delete prov templates
//
function data_action_del_prov_templates(t, e) {
	data_action_generic_delete(t, e, {
		"request_service": "/provisioning_templates",
		"request_data_entry": function(data) {
			return {
				'id': data['id']
			}
		}
	})
}

//
// data action: add provisioning templates responsibles
//
function data_action_add_prov_templates_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/provisioning_templates_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"tpl_id": data["id"]
			}
		}
	})
}

//
// data action: del provisioning templates responsible
//
function data_action_del_prov_templates_responsible(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/provisioning_templates_responsibles",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"tpl_id": data["id"]
			}
		}
	})
}

//
// data action: add provisioning templates publications
//
function data_action_add_prov_templates_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcpostrest,
		"request_service": "/provisioning_templates_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"tpl_id": data["id"]
			}
		}
	})
}

//
// data action: del provisioning templates publications
//
function data_action_del_prov_templates_publication(t, e) {
	data_action_generic_selector(t, e, {
		"requestor": services_osvcdeleterest,
		"request_service": "/provisioning_templates_publications",
		"selector": generic_selector_org_groups,
		"request_data_entry": function(selected, data) {
			return {
				"group_id": selected,
				"tpl_id": data["id"]
			}
		}
	})
}

//
// Selector clicked decorators
//
clicked_decorator_service_instance = function(e, data) {
	var s = $("<span><span svc_id='"+data.svc_id+"'></span> @ <span node_id='"+data.node_id+"'></span></span>")
	e.html(s)
	s.children("[node_id]").osvc_nodename()
	s.children("[svc_id]").osvc_svcname()
}

clicked_decorator_nodes_and_services = function(e, data) {
	var s = $("<span><span svc_id='"+data.svc_id+"'></span></span>")
	if (typeof(data.node_id) != "undefined") {
		s.append(" @ <span node_id='"+data.node_id+"'></span>")
	}
	e.html(s)
	s.children("[svc_id]").osvc_svcname()
	s.children("[node_id]").osvc_nodename()
}

clicked_decorator_resource = function(e, data) {
	if (!data.id) {
		var s = $("<span><span svc_id='"+data.svc_id+"'></span> @ <span node_id='"+data.node_id+"'></span><span rid='"+data.rid+"'></span></span>")
		e.html(s)
		s.children("[svc_id]").osvc_svcname()
		s.children("[node_id]").osvc_nodename()
		s.children("[rid]").osvc_resourcename()
	} else {
		var s = $("<span><span id='"+data.id+"'></span></span>")
		e.html(s)
		s.children("[id]").osvc_resourcename()
	}
}

clicked_decorator_service_moduleset = function(e, data) {
	var s = $("<span><span svc_id='"+data.svc_id+"'></span><span modset_id='"+data.modset_id+"'></span></span>")
	e.html(s)
	s.children("[svc_id]").osvc_svcname()
	s.children("[modset_id]").osvc_modulesetname()
}

clicked_decorator_action = function(e, data) {
	var s = $("<span><span action='"+data.action+"'></span> @ <span svc_id='"+data.svc_id+"'></span></span>")
	e.html(s)
	s.children("[action]").osvc_svcaction_name()
	s.children("[svc_id]").osvc_svcname()
}

clicked_decorator_network_segment = function(e, data) {
	var s = $("<span><span class='segment16 icon_fixed_width'>"+data.seg_id+"</span> in <span net_id='"+data.net_id+"'></span></span>")
	e.html(s)
	s.children("[net_id]").osvc_netname()
}

clicked_decorator_node_ips = function(e, data) {
	var s = $("<span><span id='"+data.id+"'></span> @ <span node_id='"+data.node_id+"'></span></span>")
	e.html(s)
	s.children("[node_id]").osvc_nodename()
	s.children("[id]").osvc_ip()
}

clicked_decorator_docker = function(e, data) {
	if (data.tag_id) {
		var s = $("<span><span tag_id='"+data.tag_id+"'></span> @ <span repository_id='"+data.repository_id+"'></span></span>")
		e.html(s)
		s.children("[repository_id]").osvc_docker_repositoryname()
		s.children("[tag_id]").osvc_docker_tagname()
	} else {
		var s = $("<span><span repository_id='"+data.repository_id+"'></span></span>")
		e.html(s)
		s.children("[repository_id]").osvc_docker_repositoryname()
	}
	
}

