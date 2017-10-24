// used by some table definitions and the fset designer
objcols = {
	"node": [
		'assetname',
		'fqdn',
		'serial',
		'model',
		'bios_version',
		'sp_version',
		'asset_env',
		'role',
		'status',
		'type',
		'sec_zone',
		'tz',
		'loc_country',
		'loc_zip',
		'loc_city',
		'loc_addr',
		'loc_building',
		'loc_floor',
		'loc_room',
		'loc_rack',
		'enclosure',
		'enclosureslot',
		'hvvdc',
		'hvpool',
		'hv',
		'os_name',
		'os_release',
		'os_vendor',
		'os_arch',
		'os_kernel',
		'os_concat',
		'cpu_dies',
		'cpu_cores',
		'cpu_threads',
		'cpu_model',
		'cpu_freq',
		'mem_banks',
		'mem_slots',
		'mem_bytes',
		'listener_port',
		'version',
		'action_type',
		'collector',
		'connect_to',
		'node_env',
		'team_responsible',
		'team_integ',
		'app_team_ops',
		'team_support',
		'app',
		'app_domain',
		'last_comm',
		'last_boot',
		'power_supply_nb',
		'power_cabinet1',
		'power_cabinet2',
		'power_protect',
		'power_protect_breaker',
		'power_breaker1',
		'power_breaker2',
		'warranty_end',
		'maintenance_end',
		'os_obs_warn_date',
		'os_obs_alert_date',
		'hw_obs_warn_date',
		'hw_obs_alert_date'
	],
	"service": [
		'svc_status',
		'svc_availstatus',
		'svc_frozen',
		'svc_provisioned',
		'svc_placement',
		'svc_app',
		'svc_env',
		'svc_ha',
		'svc_topology',
		'svc_flex_min_nodes',
		'svc_flex_max_nodes',
		'svc_flex_cpu_low_threshold',
		'svc_flex_cpu_high_threshold',
		'svc_drptype',
		'svc_autostart',
		'svc_nodes',
		'svc_drpnode',
		'svc_drpnodes',
		'svc_comment',
		'svc_created',
		'svc_status_updated'
	],
	"service_instance": [
		'mon_vmtype',
		'mon_vmname',
		'mon_vcpus',
		'mon_vmem',
		'mon_guestos',
		'mon_availstatus',
		'mon_overallstatus',
		'mon_frozen',
		'mon_containerstatus',
		'mon_ipstatus',
		'mon_fsstatus',
		'mon_diskstatus',
		'mon_sharestatus',
		'mon_syncstatus',
		'mon_appstatus',
		'mon_hbstatus',
		'mon_updated'
	],
	"resource": [
		'id',
		'vmname',
		'rid',
		'res_type',
		'res_status',
		'res_desc',
		'res_log',
		'res_monitor',
		'res_disable',
		'res_optional',
		'updated'
	],
	'app': [
		'id',
		'app',
		'app_domain',
		'app_team_ops',
		'publications',
		'responsibles'
	]
}

colprops = {
	"registry_id": {
		"field": "id",
		"table": "docker_registries",
		"img": "key",
		"title": "Registry id"
	},
	"registry_service": {
		"_class": "docker_registry",
		"field": "service",
		"table": "docker_registries",
		"img": "docker_registry16",
		"title": "Registry service"
	},
	"registry_updated": {
		"field": "updated",
		"table": "docker_registries",
		"_class": "datetime_status",
		"img": "time16",
		"title": "Registry updated"
	},
	"registry_created": {
		"field": "created",
		"table": "docker_registries",
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Registry created"
	},
	"repository_id": {
		"field": "id",
		"table": "docker_repositories",
		"img": "key",
		"title": "Repository id"
	},
	"repository_name": {
		"_class": "docker_repository",
		"field": "repository",
		"table": "docker_repositories",
		"img": "docker_repository16",
		"title": "Repository name"
	},
	"repository_stars": {
		"field": "stars",
		"table": "docker_repositories",
		"img": "fa-star",
		"title": "Repository stars"
	},
	"repository_official": {
		"_class": "boolean",
		"field": "official",
		"table": "docker_repositories",
		"img": "docker_repository16",
		"title": "Repository official"
	},
	"repository_automated": {
		"_class": "boolean",
		"field": "automated",
		"table": "docker_repositories",
		"img": "docker_repository16",
		"title": "Repository automated"
	},
	"repository_updated": {
		"field": "updated",
		"table": "docker_repositories",
		"_class": "datetime_status",
		"img": "time16",
		"title": "Repository updated"
	},
	"repository_created": {
		"field": "created",
		"table": "docker_repositories",
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Repository created"
	},
	"safe_name": {
		"img": "safe16",
		"title": "Name"
	},
	"uuid": {
		"_class": "safe_file",
		"img": "safe16",
		"title": "Unique id"
	},
	"size": {
		"_class": "numeric size_b",
		"img": "safe16",
		"title": "Size"
	},
	"md5": {
		"_dataclass": "pre",
		"img": "safe16",
		"title": "Checksum"
	},
	"uploader": {
		"img": "key",
		"title": "Uploader user id"
	},
	"uploader_name": {
		"img": "guy16",
		"title": "Uploader user name"
	},
	"uploaded_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Uploaded on"
	},
	"uploaded_from": {
		"img": "ip16",
		"title": "Uploaded from"
	},
	"quota_org_group": {
		"img": "quota16",
		"title": "quota_org_group"
	},
	"quota_app": {
		"img": "quota16",
		"title": "quota_app"
	},
	"account": {
		"img": "guy16",
		"title": "Account"
	},
	"ack": {
		"img": "action16",
		"title": "Ack"
	},
	"acked_by": {
		"img": "guy16",
		"title": "Acked by"
	},
	"acked_comment": {
		"img": "action16",
		"title": "Ack comment"
	},
	"acked_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Ack date"
	},
	"action": {
		"_class": "action",
		"img": "action16",
		"title": "Action"
	},
	"action_type": {
		"img": "svc",
		"title": "Action type"
	},
	"addr": {
		"img": "net16",
		"title": "Ip Address"
	},
	"addr_type": {
		"img": "net16",
		"title": "Ip Address Type"
	},
	"addr_updated": {
		"_class": "datetime_no_age",
		"img": "net16",
		"title": "Address Update"
	},
	"app": {
		"_class": "app",
		"img": "app16",
		"title": "App"
	},
	"app_domain": {
		"img": "app16",
		"title": "App domain"
	},
	"app_id": {
		"img": "key",
		"title": "App Id"
	},
	"res_key": {
		"_class": "resinfo_key",
		"img": "svc",
		"title": "Key"
	},
	"app_team_ops": {
		"img": "guys16",
		"title": "Ops team"
	},
	"res_value": {
		"_class": "resinfo_value",
		"img": "svc",
		"title": "Value"
	},
	"array_cache": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array Cache"
	},
	"array_firmware": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array Firmware"
	},
	"array_id": {
		"img": "hd16",
		"title": "Array Id"
	},
	"array_level": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array Level"
	},
	"array_model": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array Model"
	},
	"array_name": {
		"_class": "disk_array",
		"img": "hd16",
		"title": "Array"
	},
	"array_updated": {
		"_class": "datetime_no_age",
		"_dataclass": "bluer",
		"img": "time16",
		"title": "Array Updated"
	},
	"assetname": {
		"img": "node16",
		"title": "Asset name"
	},
	"asset_status": {
		"img": "node16",
		"title": "Status"
	},
	"autofix": {
		"_class": "boolean",
		"img": "actionred16",
		"title": "Autofix"
	},
	"begin": {
		"_class": "_network",
		"img": "net16",
		"title": "Ip range begin"
	},
	"broadcast": {
		"_class": "_network",
		"img": "net16",
		"title": "Broadcast"
	},
	"chain": {
		"img": "comp16",
		"title": "Chain"
	},
	"chain_len": {
		"img": "comp16",
		"title": "Chain length"
	},
	"change_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last change"
	},
	"changed": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last change"
	},
	"chart": {
		"_class": "saves_charts",
		"img": "chart16",
		"title": "Chart"
	},
	"chart_name": {
		"_class": "chart_name",
		"img": "chart16",
		"title": "Name"
	},
	"chart_yaml": {
		"_class": "yaml",
		"img": "log16",
		"title": "Definition"
	},
	"chk_prio": {
		"img": "fa-sort",
		"title": "Priority"
	},
	"chk_created": {
		"img": "check16",
		"title": "Created"
	},
	"chk_err": {
		"img": "check16",
		"title": "Error"
	},
	"chk_high": {
		"_class": "chk_high",
		"img": "fa-step-forward",
		"title": "High threshold"
	},
	"chk_inst": {
		"_class": "chk_inst",
		"img": "check16",
		"title": "Instance"
	},
	"chk_instance": {
		"_class": "chk_instance",
		"img": "check16",
		"title": "Instance"
	},
	"chk_low": {
		"_class": "chk_low",
		"img": "fa-step-backward",
		"title": "Low threshold"
	},
	"chk_nodename": {
		"_class": "nodename",
		"img": "node16",
		"title": "Nodename"
	},
	"chk_svcname": {
		"_class": "svcname",
		"img": "check16",
		"title": "Service"
	},
	"chk_threshold_provider": {
		"img": "check16",
		"title": "Threshold provider"
	},
	"chk_type": {
		"_class": "chk_type",
		"img": "check16",
		"title": "Type"
	},
	"chk_updated": {
		"_class": "datetime_daily",
		"img": "check16",
		"title": "Last check update"
	},
	"chk_value": {
		"_class": "chk_value",
		"img": "check16",
		"title": "Value"
	},
	"command": {
		"_class": "action_q_ret",
		"img": "action16",
		"title": "Command"
	},
	"comment": {
		"_class": "_network",
		"img": "net16",
		"title": "Comment"
	},
	"tz": {
		"img": "loc",
		"title": "Timezone"
	},
	"connect_to": {
		"img": "net16",
		"title": "Connect to"
	},
	"content": {
		"img": "dns16",
		"title": "Content"
	},
	"cpu_cores": {
		"img": "cpu16",
		"title": "CPU cores"
	},
	"cpu_dies": {
		"img": "cpu16",
		"title": "CPU dies"
	},
	"cpu_freq": {
		"_class": "cpu_freq",
		"img": "cpu16",
		"title": "CPU freq"
	},
	"cpu_model": {
		"img": "cpu16",
		"title": "CPU model"
	},
	"cpu_threads": {
		"img": "cpu16",
		"title": "CPU threads"
	},
	"cpu_vendor": {
		"img": "cpu16",
		"title": "CPU vendor"
	},
	"create_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Created on"
	},
	"created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Attach date"
	},
	"creator": {
		"img": "guy16",
		"title": "Creator"
	},
	"cron": {
		"_class": "action_cron",
		"img": "action16",
		"title": "Scheduled"
	},
	"current_cksum": {
		"img": "db16",
		"title": "Current csum"
	},
	"dash_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Begin date"
	},
	"dash_dict": {
		"img": "alert16",
		"title": "Dictionary"
	},
	"dash_entry": {
		"_class": "dash_entry",
		"filter_redirect": "dash_dict",
		"img": "alert16",
		"title": "Alert"
	},
	"dash_env": {
		"_class": "env",
		"img": "node_env16",
		"title": "Env"
	},
	"dash_fmt": {
		"img": "alert16",
		"title": "Format"
	},
	"dash_links": {
		"_class": "dash_links",
		"img": "dashlink16",
		"title": "Links"
	},
	"dash_md5": {
		"img": "alert16",
		"title": "Signature"
	},
	"dash_severity": {
		"_class": "dash_severity",
		"img": "alert16",
		"title": "Severity"
	},
	"dash_type": {
		"_class": "alert_type",
		"img": "alert16",
		"title": "Type"
	},
	"dash_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last update"
	},
	"date_dequeued": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Dequeued"
	},
	"date_queued": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Queued"
	},
	"description": {
		"img": "edit16",
		"title": "Description"
	},
	"dg_free": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Free"
	},
	"dg_id": {
		"img": "hd16",
		"title": "Array Disk Group Id"
	},
	"dg_name": {
		"_class": "disk_array_dg",
		"img": "hd16",
		"title": "Array Disk Group"
	},
	"dg_reservable": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Reservable"
	},
	"dg_reserved": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Reserved"
	},
	"dg_size": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Size"
	},
	"dg_used": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Used"
	},
	"disk_alloc": {
		"_class": "numeric size_mb",
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Disk Allocation"
	},
	"disk_arrayid": {
		"_class": "disk_array",
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array Id"
	},
	"disk_created": {
		"_dataclass": "bluer",
		"img": "time16",
		"title": "Storage Created"
	},
	"disk_devid": {
		"_dataclass": "pre bluer",
		"img": "hd16",
		"title": "Array device Id"
	},
	"disk_dg": {
		"img": "hd16",
		"title": "System disk group"
	},
	"disk_group": {
		"_class": "disk_array_dg",
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Array disk group"
	},
	"disk_id": {
		"_class": "disk_id",
		"_dataclass": "pre bluer",
		"img": "hd16",
		"title": "Disk Id"
	},
	"disk_level": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Level"
	},
	"disk_local": {
		"_class": "boolean",
		"img": "hd16",
		"title": "Disk Local"
	},
	"disk_model": {
		"img": "hd16",
		"title": "Disk Model"
	},
	"disk_name": {
		"_dataclass": "pre bluer",
		"img": "hd16",
		"title": "Disk Name"
	},
	"disk_nodename": {
		"_class": "nodename",
		"img": "node16",
		"title": "Nodename"
	},
	"disk_raid": {
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Raid"
	},
	"disk_region": {
		"_dataclass": "pre",
		"img": "hd16",
		"title": "Disk Region"
	},
	"disk_size": {
		"_class": "numeric size_mb",
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "Disk Size"
	},
	"disk_svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"disk_updated": {
		"_dataclass": "datetime_daily bluer",
		"img": "time16",
		"title": "Storage Updated"
	},
	"disk_used": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Disk Used"
	},
	"disk_vendor": {
		"img": "hd16",
		"title": "Disk Vendor"
	},
	"domain_id": {
		"img": "dns16",
		"title": "Domain Id"
	},
	"email": {
		"img": "guy16",
		"title": "Email"
	},
	"encap": {
		"_class": "boolean",
		"img": "svc",
		"title": "Encap"
	},
	"encap_fset_id": {
		"img": "key",
		"title": "Encap filterset id"
	},
	"encap_fset_name": {
		"_class": "fset_name",
		"img": "filter16",
		"title": "Encap filterset"
	},
	"encap_rset": {
		"img": "comp16",
		"title": "Encapsulated ruleset"
	},
	"encap_rset_id": {
		"img": "comp16",
		"title": "Encapsulated ruleset id"
	},
	"enclosure": {
		"img": "loc",
		"title": "Enclosure"
	},
	"enclosureslot": {
		"img": "loc",
		"title": "Enclosure Slot"
	},
	"end": {
		"_class": "_network",
		"img": "net16",
		"title": "Ip range end"
	},
	"asset_env": {
		"_class": "env",
		"img": "node_env16",
		"title": "Asset env"
	},
	"err": {
		"_class": "svc_action_err",
		"img": "action16",
		"title": "Action errors"
	},
	"f_author": {
		"img": "guy16",
		"title": "Author"
	},
	"f_field": {
		"_class": "db_column_name",
		"img": "filter16",
		"title": "Field"
	},
	"f_id": {
		"img": "key",
		"title": "Filter id"
	},
	"f_log_op": {
		"img": "filter16",
		"title": "Operator"
	},
	"f_op": {
		"img": "filter16",
		"title": "Operator"
	},
	"f_order": {
		"img": "filter16",
		"title": "Ordering"
	},
	"f_table": {
		"_class": "db_table_name",
		"img": "filter16",
		"title": "Table"
	},
	"f_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Updated"
	},
	"f_value": {
		"img": "filter16",
		"title": "Value"
	},
	"flag_deprecated": {
		"_class": "boolean",
		"img": "net16",
		"title": "Flag, deprecated"
	},
	"form_author": {
		"img": "guy16",
		"title": "Author"
	},
	"form_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Created on"
	},
	"form_folder": {
		"img": "hd16",
		"title": "Folder"
	},
	"form_head_id": {
		"_class": "form_id",
		"img": "wf16",
		"title": "Head form id"
	},
	"form_id": {
		"_class": "form_id",
		"img": "wf16",
		"title": "Request form id"
	},
	"form_name": {
		"img": "wf16",
		"title": "Name"
	},
	"safe_team_publication": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team publication"
	},
	"safe_team_responsible": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team responsible"
	},
	"form_team_publication": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team publication"
	},
	"form_team_responsible": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team responsible"
	},
	"form_type": {
		"img": "edit16",
		"title": "Type"
	},
	"form_yaml": {
		"_class": "yaml",
		"img": "action16",
		"title": "Definition"
	},
	"fqdn": {
		"img": "node16",
		"title": "Fqdn"
	},
	"fset_author": {
		"img": "guy16",
		"title": "Fset author"
	},
	"fset_id": {
		"img": "key",
		"title": "Filterset id"
	},
	"fset_name": {
		"_class": "fset_name",
		"img": "filter16",
		"title": "Filterset"
	},
	"fset_stats": {
		"_class": "boolean",
		"img": "chart16",
		"title": "Compute stats"
	},
	"fset_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Fset updated"
	},
	"fullname": {
		"_class": "username",
		"img": "guy16",
		"title": "Full name"
	},
	"gateway": {
		"_class": "_network",
		"img": "net16",
		"title": "Gateway"
	},
	"group_id": {
		"_class": "gid",
		"img": "guys16",
		"title": "Group id"
	},
	"group_id_count": {
		"img": "guys16",
		"title": "Group count"
	},
	"group_name": {
		"img": "guys16",
		"title": "Group name"
	},
	"groups": {
		"_class": "groups",
		"img": "guys16",
		"title": "Groups"
	},
	"hba_id": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Hba Id"
	},
	"hba_type": {
		"img": "hd16",
		"title": "Hba type"
	},
	"hostname": {
		"_class": "nodename",
		"img": "node16",
		"title": "Node name"
	},
	"hv": {
		"img": "hv16",
		"title": "Hypervisor"
	},
	"hvpool": {
		"img": "hv16",
		"title": "Hypervisor pool"
	},
	"hvvdc": {
		"img": "hv16",
		"title": "Virtual datacenter"
	},
	"hw_obs_alert_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "Hardware obsolescence alert date"
	},
	"hw_obs_warn_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "Hardware obsolescence warning date"
	},
	"id": {
		"img": "key",
		"title": "Id"
	},
	"intf": {
		"img": "net16",
		"title": "Interface"
	},
	"last": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last events"
	},
	"last_assignee": {
		"img": "guy16",
		"title": "Last assignee"
	},
	"last_comm": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last comm"
	},
	"last_boot": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last boot"
	},
	"last_check": {
		"_class": "datetime_daily",
		"img": "time16",
		"title": "Last Check"
	},
	"last_cksum": {
		"img": "db16",
		"title": "Last csum"
	},
	"last_form_id": {
		"_class": "form_id",
		"img": "wf16",
		"title": "Last form id"
	},
	"last_form_name": {
		"img": "wf16",
		"title": "Last form name"
	},
	"last_update": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last updated"
	},
	"listener_port": {
		"img": "svc",
		"title": "Listener port"
	},
	"loc_addr": {
		"img": "loc",
		"title": "Address"
	},
	"loc_building": {
		"img": "loc",
		"title": "Building"
	},
	"loc_city": {
		"img": "loc",
		"title": "City"
	},
	"loc_country": {
		"img": "loc",
		"title": "Country"
	},
	"loc_floor": {
		"img": "loc",
		"title": "Floor"
	},
	"loc_rack": {
		"img": "loc",
		"title": "Rack"
	},
	"loc_room": {
		"img": "loc",
		"title": "Room"
	},
	"loc_zip": {
		"img": "loc",
		"title": "ZIP"
	},
	"lock_filter": {
		"_class": "boolean",
		"img": "attach16",
		"title": "Lock filterset"
	},
	"log_action": {
		"img": "action16",
		"title": "Action"
	},
	"log_date": {
		"_class": "datetime_no_age",
		"default_filter": ">-1d",
		"img": "time16",
		"title": "Date"
	},
	"log_dict": {
		"img": "log16",
		"title": "Dictionary"
	},
	"log_email_sent": {
		"img": "log16",
		"title": "Sent via email"
	},
	"log_entry_id": {
		"img": "log16",
		"title": "Entry id"
	},
	"log_evt": {
		"_class": "log_event",
		"filter_redirect": "log_dict",
		"img": "log16",
		"title": "Event"
	},
	"log_fmt": {
		"img": "log16",
		"title": "Format"
	},
	"log_gtalk_sent": {
		"img": "log16",
		"title": "Sent via gtalk"
	},
	"log_icons": {
		"_class": "log_icons",
		"img": "action16",
		"title": "Icons"
	},
	"log_level": {
		"_class": "log_level",
		"img": "action16",
		"title": "Severity"
	},
	"log_nodename": {
		"_class": "nodename",
		"img": "node16",
		"title": "Node"
	},
	"log_svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"log_user": {
		"_class": "username",
		"img": "guy16",
		"title": "User"
	},
	"mac": {
		"img": "net16",
		"title": "Mac Address"
	},
	"mailto": {
		"img": "guy16",
		"title": "Responsibles emails"
	},
	"maintenance_end": {
		"_class": "date_future",
		"img": "time16",
		"title": "Maintenance end"
	},
	"manager": {
		"_class": "users_role",
		"img": "guy16",
		"title": "Role"
	},
	"mask": {
		"img": "net16",
		"title": "Netmask"
	},
	"master": {
		"img": "dns16",
		"title": "Master"
	},
	"mem_banks": {
		"img": "mem16",
		"title": "Memory banks"
	},
	"mem_bytes": {
		"_class": "numeric size_mb",
		"img": "mem16",
		"title": "Memory"
	},
	"mem_slots": {
		"img": "mem16",
		"title": "Memory slots"
	},
	"metric_author": {
		"img": "guy16",
		"title": "Author"
	},
	"metric_col_instance_index": {
		"img": "action16",
		"title": "Instance column index"
	},
	"metric_col_instance_label": {
		"img": "action16",
		"title": "Instance label"
	},
	"metric_col_value_index": {
		"img": "action16",
		"title": "Value column index"
	},
	"metric_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Created on"
	},
	"metric_name": {
		"_class": "metric_name",
		"img": "prov",
		"title": "Name"
	},
	"metric_sql": {
		"_class": "sql",
		"img": "action16",
		"title": "SQL request"
	},
	"metric_historize": {
		"_class": "boolean",
		"img": "action16",
		"title": "Historize"
	},
	"mod_log": {
		"_class": "comp_mod_log",
		"img": "complog",
		"title": "History"
	},
	"mod_name": {
		"img": "mod16",
		"title": "Module"
	},
	"mode": {
		"img": "repl16",
		"title": "Mode"
	},
	"model": {
		"img": "node16",
		"title": "Model"
	},
	"modset_id": {
		"img": "key",
		"title": "Moduleset id"
	},
	"modset_mod_author": {
		"img": "guy16",
		"title": "Author"
	},
	"modset_mod_name": {
		"img": "action16",
		"title": "Module"
	},
	"modset_mod_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Updated"
	},
	"modset_name": {
		"_class": "modset_name",
		"img": "action16",
		"title": "Moduleset"
	},
	"mon_appstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "App status"
	},
	"mon_availstatus": {
		"_class": "availstatus",
		"img": "svcinstance",
		"title": "Availability status"
	},
	"mon_changed": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Last status change"
	},
	"mon_containerpath": {
		"img": "svcinstance",
		"title": "Container path"
	},
	"mon_containerstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Container status"
	},
	"mon_diskstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Disk status"
	},
	"mon_frozen": {
		"img": "svcinstance",
		"title": "Frozen"
	},
	"mon_fsstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Fs status"
	},
	"mon_guestos": {
		"img": "svcinstance",
		"title": "Guest OS"
	},
	"mon_hbstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Hb status"
	},
	"mon_ipstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Ip status"
	},
	"mon_overallstatus": {
		"_class": "overallstatus",
		"img": "svcinstance",
		"title": "Status"
	},
	"mon_sharestatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Share status"
	},
	"mon_svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"mon_svctype": {
		"_class": "env",
		"img": "svc_env16",
		"title": "Service type"
	},
	"mon_syncstatus": {
		"_class": "status",
		"img": "svcinstance",
		"title": "Sync status"
	},
	"mon_updated": {
		"_class": "datetime_status",
		"img": "time16",
		"title": "Last status update"
	},
	"mon_vcpus": {
		"img": "svcinstance",
		"title": "Vcpus"
	},
	"mon_vmem": {
		"img": "svcinstance",
		"title": "Vmem"
	},
	"mon_vmname": {
		"_class": "nodename_no_os",
		"img": "node16",
		"title": "Container name"
	},
	"mon_vmtype": {
		"img": "svcinstance",
		"title": "Container type"
	},
	"na": {
		"_class": "numeric",
		"img": "compstatus",
		"title": "N/A"
	},
	"name": {
		"_class": "_network",
		"img": "net16",
		"title": "Name"
	},
	"need_resync": {
		"img": "repl16",
		"title": "Need resync"
	},
	"seg_id": {
		"img": "key",
		"title": "Segment Id"
	},
	"seg_type": {
		"img": "segment16",
		"title": "Segment Type"
	},
	"seg_begin": {
		"img": "segment16",
		"title": "Segment Begin"
	},
	"seg_end": {
		"img": "segment16",
		"title": "Segment End"
	},
	"net_begin": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Ip range begin"
	},
	"net_broadcast": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Broadcast"
	},
	"net_comment": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Comment"
	},
	"net_end": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Ip range end"
	},
	"net_gateway": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Gateway"
	},
	"net_id": {
		"img": "net16",
		"title": "Net Id"
	},
	"net_name": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Name"
	},
	"net_netmask": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Netmask"
	},
	"net_network": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net Network"
	},
	"net_pvid": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net VLAN id"
	},
	"net_team_responsible": {
		"_dataclass": "bluer",
		"img": "guys16",
		"title": "Net Team Responsible"
	},
	"netmask": {
		"_class": "_network",
		"img": "net16",
		"title": "Netmask"
	},
	"network": {
		"_class": "_network",
		"img": "net16",
		"title": "Network"
	},
	"node_log": {
		"_class": "comp_node_log",
		"img": "complog",
		"title": "History"
	},
	"node_name": {
		"_class": "nodename",
		"img": "node16",
		"title": "Node"
	},
	"node_updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"field": "updated",
		"title": "Last node update"
	},
	"nodename": {
		"_class": "nodename",
		"img": "node16",
		"title": "Node"
	},
	"nok": {
		"_class": "numeric",
		"img": "compstatus",
		"title": "Not Ok"
	},
	"notified_serial": {
		"img": "dns16",
		"title": "Notified Serial"
	},
	"obs": {
		"_class": "numeric",
		"img": "compstatus",
		"title": "Obsolete"
	},
	"obs_alert_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "Alert date"
	},
	"obs_count": {
		"_class": "obs_count",
		"img": "obs16",
		"title": "Count"
	},
	"obs_name": {
		"img": "obs16",
		"title": "Name"
	},
	"obs_type": {
		"_class": "obs_type",
		"img": "obs16",
		"title": "Type"
	},
	"obs_warn_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "Warn date"
	},
	"ok": {
		"_class": "numeric",
		"img": "compstatus",
		"title": "Ok"
	},
	"os_arch": {
		"img": "os16",
		"title": "OS arch"
	},
	"os_concat": {
		"img": "os16",
		"title": "OS full name"
	},
	"os_kernel": {
		"img": "os16",
		"title": "OS kernel"
	},
	"os_name": {
		"_class": "os_name",
		"img": "os16",
		"title": "OS name"
	},
	"os_obs_alert_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "OS obsolescence alert date"
	},
	"os_obs_warn_date": {
		"_class": "date_future",
		"img": "time16",
		"title": "OS obsolescence warning date"
	},
	"os_release": {
		"img": "os16",
		"title": "OS release"
	},
	"os_vendor": {
		"img": "os16",
		"title": "OS vendor"
	},
	"patch_install_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Install date"
	},
	"patch_num": {
		"img": "pkg16",
		"title": "Patchnum"
	},
	"patch_rev": {
		"img": "pkg16",
		"title": "Patchrev"
	},
	"patch_updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"title": "Updated"
	},
	"pct": {
		"_class": "pct",
		"img": "compstatus",
		"title": "Percent"
	},
	"phone_work": {
		"_class": "nowrap",
		"img": "guy16",
		"title": "Work desk phone"
	},
	"pid": {
		"_class": "action_pid",
		"img": "action16",
		"title": "Pid"
	},
	"pkg_arch": {
		"img": "pkg16",
		"title": "Arch"
	},
	"pkg_install_date": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Install date"
	},
	"pkg_name": {
		"img": "pkg16",
		"title": "Package"
	},
	"node_app": {
		"_class": "app",
		"img": "app16",
		"title": "Node App"
	},
	"node_id": {
		"img": "node16",
		"title": "Node Id"
	},
	"svc_id": {
		"img": "svc",
		"title": "Service Id"
	},
	"pkg_sig": {
		"_dataclass": "pre",
		"img": "pkg16",
		"title": "Signature"
	},
	"pkg_type": {
		"img": "pkg16",
		"title": "Type"
	},
	"pkg_updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"title": "Updated"
	},
	"pkg_version": {
		"_class": "nowrap",
		"img": "pkg16",
		"title": "Version"
	},
	"power_breaker1": {
		"img": "pwr",
		"title": "Power breaker #1"
	},
	"power_breaker2": {
		"img": "pwr",
		"title": "Power breaker #2"
	},
	"power_cabinet1": {
		"img": "pwr",
		"title": "Power cabinet #1"
	},
	"power_cabinet2": {
		"img": "pwr",
		"title": "Power cabinet #2"
	},
	"power_protect": {
		"img": "pwr",
		"title": "Power protector"
	},
	"power_protect_breaker": {
		"img": "pwr",
		"title": "Power protector breaker"
	},
	"power_supply_nb": {
		"img": "pwr",
		"title": "Power supply number"
	},
	"primary_group": {
		"_class": "groups",
		"img": "guys16",
		"title": "Primary group"
	},
	"prio": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Net priority"
	},
	"pvid": {
		"_class": "_network",
		"img": "net16",
		"title": "VLAN id"
	},
	"quota": {
		"_class": "quota numeric size_mb",
		"img": "hd16",
		"title": "Quota"
	},
	"quota_used": {
		"_class": "numeric size_mb",
		"img": "hd16",
		"title": "Quota Used"
	},
	"remote": {
		"img": "node16",
		"title": "Remote"
	},
	"report_name": {
		"_class": "report_name",
		"img": "report16",
		"title": "Name"
	},
	"report_yaml": {
		"_class": "yaml",
		"img": "log16",
		"title": "Definition"
	},
	"res_desc": {
		"img": "resource",
		"title": "Description"
	},
	"res_disable": {
		"_class": "boolean",
		"img": "resource",
		"title": "Disable"
	},
	"res_log": {
		"_class": "res_log",
		"img": "resource",
		"title": "Log"
	},
	"res_monitor": {
		"_class": "boolean",
		"img": "resource",
		"title": "Monitor"
	},
	"res_optional": {
		"_class": "boolean",
		"img": "resource",
		"title": "Optional"
	},
	"res_type": {
		"_class": "res_stype",
		"img": "resource",
		"title": "Type"
	},
	"res_status": {
		"_class": "status",
		"img": "resource",
		"title": "Status"
	},
	"publications": {
		"_class": "groups",
		"img": "guys16",
		"title": "Publications"
	},
	"responsibles": {
		"_class": "groups",
		"img": "guys16",
		"title": "Responsibles"
	},
	"ret": {
		"_class": "action_q_ret",
		"img": "action16",
		"title": "Return code"
	},
	"rid": {
		"img": "resource",
		"title": "Resource id"
	},
	"role": {
		"img": "node16",
		"title": "Role"
	},
	"roles": {
		"_class": "groups",
		"img": "guys16",
		"title": "Sysresp teams"
	},
	"rset_md5": {
		"_dataclass": "nowrap pre rset_md5",
		"img": "comp16",
		"title": "Ruleset md5"
	},
	"ruleset_id": {
		"img": "comp16",
		"title": "Ruleset id"
	},
	"ruleset_name": {
		"_class": "ruleset_name",
		"img": "comp16",
		"title": "Ruleset"
	},
	"ruleset_public": {
		"_class": "boolean",
		"img": "comp16",
		"title": "Ruleset public"
	},
	"ruleset_type": {
		"img": "comp16",
		"title": "Ruleset type"
	},
	"run_action": {
		"img": "mod16",
		"title": "Action"
	},
	"run_date": {
		"_class": "datetime_weekly",
		"img": "time16",
		"title": "Run date"
	},
	"run_log": {
		"_class": "status_run_log",
		"img": "complog",
		"title": "Log"
	},
	"run_status": {
		"_class": "status_run_status",
		"img": "compstatus",
		"title": "Status"
	},
	"run_module": {
		"img": "mod16",
		"title": "Module"
	},
	"run_status_log": {
		"_class": "comp_log",
		"img": "complog",
		"title": "History"
	},
	"run_svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"save_app": {
		"img": "app16",
		"title": "App"
	},
	"save_date": {
		"_class": "datetime_no_age",
		"default_filter": ">-1d",
		"img": "time16",
		"title": "Date"
	},
	"save_group": {
		"img": "save16",
		"title": "Group"
	},
	"save_id": {
		"img": "save16",
		"title": "Id"
	},
	"save_level": {
		"img": "save16",
		"title": "Level"
	},
	"save_name": {
		"img": "save16",
		"title": "Name"
	},
	"save_nodename": {
		"_class": "nodename",
		"img": "node16",
		"title": "Nodename"
	},
	"save_retention": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Retention"
	},
	"save_server": {
		"_class": "nodename_no_os",
		"img": "node16",
		"title": "Server"
	},
	"save_size": {
		"_class": "size_b",
		"img": "save16",
		"title": "Size"
	},
	"save_svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"save_volume": {
		"img": "save16",
		"title": "Volume"
	},
	"sec_zone": {
		"img": "fw16",
		"title": "Security zone"
	},
	"serial": {
		"img": "node16",
		"title": "Serial"
	},
	"bios_version": {
		"img": "node16",
		"title": "Bios Version"
	},
	"sp_version": {
		"img": "node16",
		"title": "SP Version"
	},
	"sig_provider": {
		"img": "pkg16",
		"title": "Signature provider"
	},
	"status": {
		"img": "node16",
		"title": "Status"
	},
	"status_log": {
		"_class": "action_log",
		"img": "action16",
		"title": "Log"
	},
	"stderr": {
		"_dataclass": "pre",
		"img": "action16",
		"title": "Stderr"
	},
	"stdout": {
		"_dataclass": "pre",
		"img": "action16",
		"title": "Stdout"
	},
	"steps": {
		"img": "wf16",
		"title": "Steps"
	},
	"svc_app": {
		"_class": "app",
		"img": "app16",
		"title": "App"
	},
	"svc_autostart": {
		"_class": "svc_autostart",
		"img": "svc",
		"title": "Primary node"
	},
	"svc_availstatus": {
		"_class": "status",
		"img": "svc",
		"title": "Service availability status"
	},
	"svc_topology": {
		"img": "svc",
		"title": "Topology"
	},
	"svc_comment": {
		"img": "svc",
		"title": "Comment"
	},
	"svc_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Service creation date"
	},
	"svc_drpnode": {
		"img": "node16",
		"title": "DRP node"
	},
	"svc_drpnodes": {
		"img": "svc",
		"title": "DRP nodes"
	},
	"svc_drptype": {
		"img": "svc",
		"title": "DRP type"
	},
	"svc_config_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Config file updated"
	},
	"svc_config": {
		"img": "svc",
		"title": "Config file"
	},
	"svc_flex_cpu_high_threshold": {
		"img": "chart16",
		"title": "Flex cpu high threshold"
	},
	"svc_flex_cpu_low_threshold": {
		"img": "chart16",
		"title": "Flex cpu low threshold"
	},
	"svc_flex_max_nodes": {
		"img": "svc",
		"title": "Flex max nodes"
	},
	"svc_flex_min_nodes": {
		"img": "svc",
		"title": "Flex min nodes"
	},
	"svc_ha": {
		"_class": "svc_ha",
		"img": "svc",
		"title": "HA"
	},
	"svc_hostid": {
		"img": "svc",
		"title": "Host id"
	},
	"svc_log": {
		"_class": "comp_svc_log",
		"img": "complog",
		"title": "History"
	},
	"svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"svc_nodes": {
		"img": "node16",
		"title": "Nodes"
	},
	"svc_status": {
		"_class": "status",
		"img": "svc",
		"title": "Service overall status"
	},
	"svc_frozen": {
		"_class": "frozen",
		"img": "svc",
		"title": "Service frozen"
	},
	"svc_placement": {
		"img": "svc",
		"title": "Service placement"
	},
	"svc_provisioned": {
		"img": "svc",
		"title": "Service provisioned"
	},
	"svc_status_updated": {
		"_class": "datetime_status",
		"img": "time16",
		"title": "Status updated"
	},
	"svc_env": {
		"_class": "env",
		"img": "svc_env16",
		"title": "Service env"
	},
	"node_env": {
		"_class": "env",
		"img": "node_env16",
		"title": "Node env"
	},
	"svc_updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"field": "updated",
		"title": "Config updated"
	},
	"svc_wave": {
		"img": "svc",
		"title": "Drp wave"
	},
	"svcdisk_id": {
		"_class": "disk_array",
		"_dataclass": "bluer",
		"img": "hd16",
		"title": "System Disk Id"
	},
	"svcdisk_updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"title": "System Updated"
	},
	"svcname": {
		"_class": "svcname",
		"img": "svc",
		"title": "Service"
	},
	"sw_fabric": {
		"img": "net16",
		"title": "Switch Fabric"
	},
	"sw_index": {
		"img": "net16",
		"title": "Port Index"
	},
	"sw_name": {
		"img": "net16",
		"title": "Switch Name"
	},
	"sw_port": {
		"img": "net16",
		"title": "Port"
	},
	"sw_portname": {
		"img": "net16",
		"title": "Port Name"
	},
	"sw_portnego": {
		"_class": "boolean",
		"img": "net16",
		"title": "Port Nego"
	},
	"sw_portspeed": {
		"img": "net16",
		"title": "Port Speed"
	},
	"sw_portstate": {
		"img": "net16",
		"title": "Port State"
	},
	"sw_porttype": {
		"img": "net16",
		"title": "Port Type"
	},
	"sw_rname": {
		"img": "net16",
		"title": "Remote Name"
	},
	"sw_rportname": {
		"img": "net16",
		"title": "Remote Port Name"
	},
	"sw_slot": {
		"img": "net16",
		"title": "Slot"
	},
	"sw_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Updated"
	},
	"table_name": {
		"img": "db16",
		"title": "Table"
	},
	"table_schema": {
		"img": "db16",
		"title": "Database"
	},
	"table_updated": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Updated"
	},
	"tag_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Tag created"
	},
	"tag_exclude": {
		"_class": "tag_exclude",
		"img": "tag16",
		"title": "Tag exclude"
	},
	"tag_id": {
		"img": "tag16",
		"title": "Tag id"
	},
	"tag_name": {
		"_class": "tag_name",
		"img": "tag16",
		"title": "Tag name"
	},
	"team_integ": {
		"_class": "groups",
		"img": "guys16",
		"title": "Integrator"
	},
	"team_responsible": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team responsible"
	},
	"team_support": {
		"_class": "groups",
		"img": "guys16",
		"title": "Support"
	},
	"teams_publication": {
		"_class": "groups",
		"img": "guys16",
		"title": "Teams publication"
	},
	"teams_responsible": {
		"_class": "groups",
		"img": "guys16",
		"title": "Teams responsible"
	},
	"tgt_id": {
		"_dataclass": "bluer",
		"img": "net16",
		"title": "Target Id"
	},
	"time": {
		"img": "time16",
		"title": "Duration"
	},
	"total": {
		"_class": "numeric",
		"img": "compstatus",
		"title": "Total"
	},
	"tpl_author": {
		"img": "guy16",
		"title": "Author"
	},
	"tpl_definition": {
		"_class": "tpl_definition",
		"img": "action16",
		"title": "Definition"
	},
	"tpl_comment": {
		"img": "edit16",
		"title": "Comment"
	},
	"tpl_created": {
		"_class": "datetime_no_age",
		"img": "time16",
		"title": "Created on"
	},
	"tpl_name": {
		"_class": "prov_template",
		"img": "prov",
		"title": "Name"
	},
	"tpl_team_responsible": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team responsible"
	},
	"tpl_team_publication": {
		"_class": "groups",
		"img": "guys16",
		"title": "Team publication"
	},
	"ttl": {
		"img": "dns16",
		"title": "Time to Live"
	},
	"type": {
		"img": "node16",
		"title": "Type"
	},
	"updated": {
		"_class": "datetime_daily",
		"img": "time16",
		"title": "Updated"
	},
	"user_id": {
		"_class": "uid",
		"img": "guy16",
		"title": "User id"
	},
	"user_id_count": {
		"img": "guy16",
		"title": "User count"
	},
	"user_name": {
		"img": "guy16",
		"title": "User name"
	},
	"username": {
		"_class": "username",
		"img": "guy16",
		"title": "User name"
	},
	"var_author": {
		"img": "guy16",
		"title": "Author"
	},
	"var_class": {
		"_class": "var_class",
		"img": "wf16",
		"title": "Class"
	},
	"var_name": {
		"_class": "var_name",
		"img": "comp16",
		"title": "Variable"
	},
	"var_updated": {
		"_class": "datetime_no_age",
		"img": "comp16",
		"title": "Updated"
	},
	"var_value": {
		"_class": "rule_value",
		"img": "comp16",
		"title": "Value"
	},
	"version": {
		"_class": "nowrap",
		"img": "svc",
		"title": "Agent version"
	},
	"collector": {
		"img": "svc",
		"title": "Collector"
	},
	"vmname": {
		"_class": "nodename_no_os",
		"img": "node16",
		"title": "Container name"
	},
	"warranty_end": {
		"_class": "date_future",
		"img": "time16",
		"title": "Warranty end"
	}
}
