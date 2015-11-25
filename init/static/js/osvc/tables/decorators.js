//
// cell decorators
//

var db_tables = {
  "v_tags": {
    "cl": "tag16",
    "hide": false,
    "name": "v_tags",
    "title": "tags"
  },
  "v_comp_moduleset_attachments": {
    "cl": "modset16",
    "hide": false,
    "name": "v_comp_moduleset_attachments",
    "title": "moduleset attachments"
  },
  "svcmon": {
    "cl": "svc",
    "hide": false,
    "name": "svcmon",
    "title": "service status"
  },
  "services": {
    "cl": "svc",
    "hide": false,
    "name": "services",
    "title": "services"
  },
  "b_disk_app": {
    "cl": "hd16",
    "hide": false,
    "name": "b_disk_app",
    "title": "disks"
  },
  "nodes": {
    "cl": "node16",
    "hide": false,
    "name": "nodes",
    "title": "nodes"
  },
  "apps": {
    "cl": "svc",
    "hide": false,
    "name": "apps",
    "title": "apps"
  },
  "resmon": {
    "cl": "action16",
    "hide": false,
    "name": "resmon",
    "title": "resources"
  },
  "node_hba": {
    "cl": "node16",
    "hide": false,
    "name": "node_hba",
    "title": "node host bus adapaters"
  }
}

var db_columns = {
  "loc_city": {
    "field": "loc_city",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "City",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_svcname": {
    "field": "mon_svcname",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service",
    "_class": "svcname",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_envdate": {
    "field": "svc_envdate",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Env file date",
    "_class": "",
    "table": "v_svcmon",
    "default_filter": ""
  },
  "mon_containerstatus": {
    "field": "mon_containerstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Container status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "cpu_dies": {
    "field": "cpu_dies",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU dies",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "assetname": {
    "field": "assetname",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Asset name",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "loc_country": {
    "field": "loc_country",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Country",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "cpu_vendor": {
    "field": "cpu_vendor",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU vendor",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_diskstatus": {
    "field": "mon_diskstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Disk status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "loc_building": {
    "field": "loc_building",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Building",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "team_responsible": {
    "field": "team_responsible",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guys16",
    "_dataclass": "",
    "title": "Team responsible",
    "_class": "groups",
    "table": "v_nodes",
    "default_filter": ""
  },
  "cpu_cores": {
    "field": "cpu_cores",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU cores",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "loc_rack": {
    "field": "loc_rack",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Rack",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "res_desc": {
    "field": "res_desc",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Description",
    "_class": "",
    "table": "",
    "default_filter": ""
  },
  "cpu_model": {
    "field": "cpu_model",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU model",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_devid": {
    "field": "disk_devid",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Array device Id",
    "_class": "pre",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "svc_flex_min_nodes": {
    "field": "svc_flex_min_nodes",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Flex min nodes",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "cpu_threads": {
    "field": "cpu_threads",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU threads",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_wave": {
    "field": "svc_wave",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Drp wave",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "disk_nodename": {
    "field": "disk_nodename",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hw16",
    "_dataclass": "",
    "title": "Nodename",
    "_class": "nodename",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "svc_containertype": {
    "field": "svc_containertype",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service mode",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "svc_ha": {
    "field": "svc_ha",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "HA",
    "_class": "svc_ha",
    "table": "v_services",
    "default_filter": ""
  },
  "svc_created": {
    "field": "svc_created",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Service creation date",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "mon_fsstatus": {
    "field": "mon_fsstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Fs status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "action_type": {
    "field": "action_type",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Action type",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_updated": {
    "field": "mon_updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last status update",
    "_class": "datetime_daily",
    "table": "svcmon",
    "default_filter": ""
  },
  "hw_obs_warn_date": {
    "field": "hw_obs_warn_date",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Hardware obsolescence warning date",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "power_breaker2": {
    "field": "power_breaker2",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power breaker #2",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "status": {
    "field": "status",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Status",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_vmem": {
    "field": "mon_vmem",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Vmem",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "mem_bytes": {
    "field": "mem_bytes",
    "filter_redirect": "",
    "force_filter": "",
    "img": "mem16",
    "_dataclass": "",
    "title": "Memory",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "power_protect_breaker": {
    "field": "power_protect_breaker",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power protector breaker",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "hvpool": {
    "field": "hvpool",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hv16",
    "_dataclass": "",
    "title": "Hypervisor pool",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_overallstatus": {
    "field": "mon_overallstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Status",
    "_class": "overallstatus",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_flex_cpu_high_threshold": {
    "field": "svc_flex_cpu_high_threshold",
    "filter_redirect": "",
    "force_filter": "",
    "img": "spark16",
    "_dataclass": "",
    "title": "Flex cpu high threshold",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "team_support": {
    "field": "team_support",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guys16",
    "_dataclass": "",
    "title": "Support",
    "_class": "groups",
    "table": "v_nodes",
    "default_filter": ""
  },
  "host_mode": {
    "field": "host_mode",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Host Mode",
    "_class": "env",
    "table": "v_nodes",
    "default_filter": ""
  },
  "enclosure": {
    "field": "enclosure",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Enclosure",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "responsibles": {
    "field": "responsibles",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guy16",
    "_dataclass": "",
    "title": "Responsibles",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "mon_vmtype": {
    "field": "mon_vmtype",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Container type",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "disk_vendor": {
    "field": "disk_vendor",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Disk Vendor",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "svc_cluster_type": {
    "field": "svc_cluster_type",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Cluster type",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "array_model": {
    "field": "array_model",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Array Model",
    "_class": "",
    "table": "stor_array",
    "default_filter": ""
  },
  "svc_autostart": {
    "field": "svc_autostart",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Primary node",
    "_class": "svc_autostart",
    "table": "v_services",
    "default_filter": ""
  },
  "mon_sharestatus": {
    "field": "mon_sharestatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Share status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "version": {
    "field": "version",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Agent version",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svcdisk_updated": {
    "field": "svcdisk_updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "System Updated",
    "_class": "datetime_daily",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "mem_slots": {
    "field": "mem_slots",
    "filter_redirect": "",
    "force_filter": "",
    "img": "mem16",
    "_dataclass": "",
    "title": "Memory slots",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_updated": {
    "field": "disk_updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "datetime_daily bluer",
    "title": "Storage Updated",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "os_obs_alert_date": {
    "field": "os_obs_alert_date",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "OS obsolescence alert date",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "warranty_end": {
    "field": "warranty_end",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Warranty end",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "last_boot": {
    "field": "last_boot",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last boot",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_guestos": {
    "field": "mon_guestos",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Guest OS",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "mon_svctype": {
    "field": "mon_svctype",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service type",
    "_class": "env",
    "table": "svcmon",
    "default_filter": ""
  },
  "loc_addr": {
    "field": "loc_addr",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Address",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "changed": {
    "field": "changed",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last change",
    "_class": "datetime_no_age",
    "table": "",
    "default_filter": ""
  },
  "modset_name": {
    "field": "modset_name",
    "filter_redirect": "",
    "force_filter": "",
    "img": "modset16",
    "_dataclass": "",
    "title": "Moduleset name",
    "_class": "",
    "table": "v_comp_moduleset_attachments",
    "default_filter": ""
  },
  "power_breaker1": {
    "field": "power_breaker1",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power breaker #1",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_hbstatus": {
    "field": "mon_hbstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Hb status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_drpnode": {
    "field": "svc_drpnode",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "DRP node",
    "_class": "nodename_no_os",
    "table": "v_services",
    "default_filter": ""
  },
  "hvvdc": {
    "field": "hvvdc",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hv16",
    "_dataclass": "",
    "title": "Virtual datacenter",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_raid": {
    "field": "disk_raid",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Raid",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "disk_used": {
    "field": "disk_used",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Disk Used",
    "_class": "numeric size_mb",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "svc_updated": {
    "field": "updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last service update",
    "_class": "datetime_daily",
    "table": "v_services",
    "default_filter": ""
  },
  "svcdisk_id": {
    "field": "svcdisk_id",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "System Disk Id",
    "_class": "disk_array",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "sec_zone": {
    "field": "sec_zone",
    "filter_redirect": "",
    "force_filter": "",
    "img": "fw16",
    "_dataclass": "",
    "title": "Security zone",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_app": {
    "field": "svc_app",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "App",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "app": {
    "field": "app",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Application code",
    "_class": "",
    "table": "apps",
    "default_filter": ""
  },
  "power_cabinet1": {
    "field": "power_cabinet1",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power cabinet #1",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "power_cabinet2": {
    "field": "power_cabinet2",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power cabinet #2",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_vcpus": {
    "field": "mon_vcpus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Vcpus",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_status": {
    "field": "svc_status",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service overall status",
    "_class": "status",
    "table": "v_services",
    "default_filter": ""
  },
  "disk_arrayid": {
    "field": "disk_arrayid",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Array Id",
    "_class": "disk_array",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "os_vendor": {
    "field": "os_vendor",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS vendor",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mailto": {
    "field": "mailto",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guy16",
    "_dataclass": "",
    "title": "Responsibles emails",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "svc_flex_cpu_low_threshold": {
    "field": "svc_flex_cpu_low_threshold",
    "filter_redirect": "",
    "force_filter": "",
    "img": "spark16",
    "_dataclass": "",
    "title": "Flex cpu low threshold",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "cpu_freq": {
    "field": "cpu_freq",
    "filter_redirect": "",
    "force_filter": "",
    "img": "cpu16",
    "_dataclass": "",
    "title": "CPU freq",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mem_banks": {
    "field": "mem_banks",
    "filter_redirect": "",
    "force_filter": "",
    "img": "mem16",
    "_dataclass": "",
    "title": "Memory banks",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "res_log": {
    "field": "res_log",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Log",
    "_class": "",
    "table": "",
    "default_filter": ""
  },
  "disk_id": {
    "field": "disk_id",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Disk Id",
    "_class": "pre",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "type": {
    "field": "type",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Type",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "enclosureslot": {
    "field": "enclosureslot",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Enclosure Slot",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_type": {
    "field": "svc_type",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service type",
    "_class": "env",
    "table": "v_services",
    "default_filter": ""
  },
  "svc_envfile": {
    "field": "svc_envfile",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Env file",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "hba_type": {
    "field": "hba_type",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Hba type",
    "_class": "",
    "table": "node_hba",
    "default_filter": ""
  },
  "hv": {
    "field": "hv",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hv16",
    "_dataclass": "",
    "title": "Hypervisor",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_vmname": {
    "field": "mon_vmname",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Container name",
    "_class": "nodename_no_os",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_availstatus": {
    "field": "svc_availstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service availability status",
    "_class": "status",
    "table": "v_services",
    "default_filter": ""
  },
  "disk_level": {
    "field": "disk_level",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Level",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "svc_drptype": {
    "field": "svc_drptype",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "DRP type",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "os_concat": {
    "field": "os_concat",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS full name",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_status_updated": {
    "field": "svc_status_updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Status updated",
    "_class": "datetime_status",
    "table": "services",
    "default_filter": ""
  },
  "disk_name": {
    "field": "disk_name",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Disk Name",
    "_class": "pre",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "listener_port": {
    "field": "listener_port",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Listener port",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "environnement": {
    "field": "environnement",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Env",
    "_class": "env",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_nodname": {
    "field": "mon_nodname",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Node",
    "_class": "nodename",
    "table": "svcmon",
    "default_filter": ""
  },
  "svc_drpnodes": {
    "field": "svc_drpnodes",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "DRP nodes",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "svc_nodes": {
    "field": "svc_nodes",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Nodes",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "err": {
    "field": "err",
    "filter_redirect": "",
    "force_filter": "",
    "img": "action16",
    "_dataclass": "",
    "title": "Action errors",
    "_class": "svc_action_err",
    "table": "v_svcmon",
    "default_filter": ""
  },
  "os_obs_warn_date": {
    "field": "os_obs_warn_date",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "OS obsolescence warning date",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_name": {
    "field": "svc_name",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service",
    "_class": "svcname",
    "table": "v_services",
    "default_filter": ""
  },
  "disk_created": {
    "field": "disk_created",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "bluer",
    "title": "Storage Created",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "loc_room": {
    "field": "loc_room",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Room",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "project": {
    "field": "project",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Project",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "loc_floor": {
    "field": "loc_floor",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "Floor",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_availstatus": {
    "field": "mon_availstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Availability status",
    "_class": "availstatus",
    "table": "svcmon",
    "default_filter": ""
  },
  "app_team_ops": {
    "field": "app_team_ops",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guys16",
    "_dataclass": "",
    "title": "Ops team",
    "_class": "",
    "table": "apps",
    "default_filter": ""
  },
  "disk_dg": {
    "field": "disk_dg",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "System disk group",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "os_kernel": {
    "field": "os_kernel",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS kernel",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "updated": {
    "field": "updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Updated",
    "_class": "datetime_status",
    "table": "",
    "default_filter": ""
  },
  "fqdn": {
    "field": "fqdn",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Fqdn",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_svcname": {
    "field": "disk_svcname",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Service",
    "_class": "svcname",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "mon_frozen": {
    "field": "mon_frozen",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Frozen",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "mon_containerpath": {
    "field": "mon_containerpath",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Container path",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "mon_ipstatus": {
    "field": "mon_ipstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Ip status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "id": {
    "field": "id",
    "filter_redirect": "",
    "force_filter": "",
    "img": "columns",
    "_dataclass": "",
    "title": "Id",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_hostid": {
    "field": "svc_hostid",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Host id",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "disk_model": {
    "field": "disk_model",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Disk Model",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "os_arch": {
    "field": "os_arch",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS arch",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "node_updated": {
    "field": "node_updated",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last node update",
    "_class": "datetime_daily",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_comment": {
    "field": "svc_comment",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Comment",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "role": {
    "field": "role",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Role",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "team_integ": {
    "field": "team_integ",
    "filter_redirect": "",
    "force_filter": "",
    "img": "guys16",
    "_dataclass": "",
    "title": "Integrator",
    "_class": "groups",
    "table": "v_nodes",
    "default_filter": ""
  },
  "power_supply_nb": {
    "field": "power_supply_nb",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power supply number",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "svc_flex_max_nodes": {
    "field": "svc_flex_max_nodes",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Flex max nodes",
    "_class": "",
    "table": "v_services",
    "default_filter": ""
  },
  "res_status": {
    "field": "res_status",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Status",
    "_class": "status",
    "table": "",
    "default_filter": ""
  },
  "rid": {
    "field": "rid",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Resource id",
    "_class": "",
    "table": "resmon",
    "default_filter": ""
  },
  "maintenance_end": {
    "field": "maintenance_end",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Maintenance end",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "loc_zip": {
    "field": "loc_zip",
    "filter_redirect": "",
    "force_filter": "",
    "img": "loc",
    "_dataclass": "",
    "title": "ZIP",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "app_domain": {
    "field": "app_domain",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "App domain",
    "_class": "",
    "table": "apps",
    "default_filter": ""
  },
  "os_name": {
    "field": "os_name",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS name",
    "_class": "os_name",
    "table": "v_nodes",
    "default_filter": ""
  },
  "nodename": {
    "field": "nodename",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hw16",
    "_dataclass": "",
    "title": "Nodename",
    "_class": "nodename",
    "table": "node_hba",
    "default_filter": ""
  },
  "power_protect": {
    "field": "power_protect",
    "filter_redirect": "",
    "force_filter": "",
    "img": "pwr",
    "_dataclass": "",
    "title": "Power protector",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_appstatus": {
    "field": "mon_appstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "App status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "mon_changed": {
    "field": "mon_changed",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Last status change",
    "_class": "",
    "table": "svcmon",
    "default_filter": ""
  },
  "disk_local": {
    "field": "disk_local",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Disk Local",
    "_class": "",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "disk_group": {
    "field": "disk_group",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Array disk group",
    "_class": "disk_array_dg",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "serial": {
    "field": "serial",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Serial",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "hw_obs_alert_date": {
    "field": "hw_obs_alert_date",
    "filter_redirect": "",
    "force_filter": "",
    "img": "time16",
    "_dataclass": "",
    "title": "Hardware obsolescence alert date",
    "_class": "date_future",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_size": {
    "field": "disk_size",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Disk Size",
    "_class": "numeric size_mb",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "disk_alloc": {
    "field": "disk_alloc",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "bluer",
    "title": "Disk Allocation",
    "_class": "numeric size_mb",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "description": {
    "field": "description",
    "filter_redirect": "",
    "force_filter": "",
    "img": "edit16",
    "_dataclass": "",
    "title": "Description",
    "_class": "",
    "table": "apps",
    "default_filter": ""
  },
  "tag_name": {
    "field": "tag_name",
    "filter_redirect": "",
    "force_filter": "",
    "img": "tag16",
    "_dataclass": "",
    "title": "Tag name",
    "_class": "",
    "table": "v_tags",
    "default_filter": ""
  },
  "os_release": {
    "field": "os_release",
    "filter_redirect": "",
    "force_filter": "",
    "img": "os16",
    "_dataclass": "",
    "title": "OS release",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "mon_syncstatus": {
    "field": "mon_syncstatus",
    "filter_redirect": "",
    "force_filter": "",
    "img": "svc",
    "_dataclass": "",
    "title": "Sync status",
    "_class": "status",
    "table": "svcmon",
    "default_filter": ""
  },
  "model": {
    "field": "model",
    "filter_redirect": "",
    "force_filter": "",
    "img": "node16",
    "_dataclass": "",
    "title": "Model",
    "_class": "",
    "table": "v_nodes",
    "default_filter": ""
  },
  "disk_region": {
    "field": "disk_region",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Disk Region",
    "_class": "pre",
    "table": "b_disk_app",
    "default_filter": ""
  },
  "hba_id": {
    "field": "hba_id",
    "filter_redirect": "",
    "force_filter": "",
    "img": "hd16",
    "_dataclass": "",
    "title": "Hba id",
    "_class": "",
    "table": "node_hba",
    "default_filter": ""
  }
}

var action_img_h = {
  'checks': 'check16',
  'enable': 'check16',
  'disable': 'nok',
  'pushservices': 'svc',
  'pushpkg': 'pkg16',
  'pushpatch': 'pkg16',
  'reboot': 'action_restart_16',
  'shutdown': 'action_stop_16',
  'syncservices': 'action_sync_16',
  'sync_services': 'action_sync_16',
  'updateservices': 'action16',
  'updatepkg': 'pkg16',
  'updatecomp': 'pkg16',
  'stop': 'action_stop_16',
  'stopapp': 'action_stop_16',
  'stopdisk': 'action_stop_16',
  'stopvg': 'action_stop_16',
  'stoploop': 'action_stop_16',
  'stopip': 'action_stop_16',
  'stopfs': 'action_stop_16',
  'umount': 'action_stop_16',
  'shutdown': 'action_stop_16',
  'boot': 'action_start_16',
  'start': 'action_start_16',
  'startstandby': 'action_start_16',
  'startapp': 'action_start_16',
  'startdisk': 'action_start_16',
  'startvg': 'action_start_16',
  'startloop': 'action_start_16',
  'startip': 'action_start_16',
  'startfs': 'action_start_16',
  'mount': 'action_start_16',
  'restart': 'action_restart_16',
  'provision': 'prov',
  'switch': 'action_switch_16',
  'freeze': 'frozen16',
  'thaw': 'frozen16',
  'sync_all': 'action_sync_16',
  'sync_nodes': 'action_sync_16',
  'sync_drp': 'action_sync_16',
  'syncall': 'action_sync_16',
  'syncnodes': 'action_sync_16',
  'syncdrp': 'action_sync_16',
  'syncfullsync': 'action_sync_16',
  'postsync': 'action_sync_16',
  'push': 'log16',
  'check': 'check16',
  'fixable': 'fixable16',
  'fix': 'comp16',
  'pushstats': 'spark16',
  'pushasset': 'node16',
  'stopcontainer': 'action_stop_16',
  'startcontainer': 'action_start_16',
  'stopapp': 'action_stop_16',
  'startapp': 'action_start_16',
  'prstop': 'action_stop_16',
  'prstart': 'action_start_16',
  'push': 'svc',
  'syncquiesce': 'action_sync_16',
  'syncresync': 'action_sync_16',
  'syncupdate': 'action_sync_16',
  'syncverify': 'action_sync_16',
  'toc': 'action_toc_16',
  'stonith': 'action_stonith_16',
  'switch': 'action_switch_16'
}


var os_class_h = {
  'darwin': 'os_darwin',
  'linux': 'os_linux',
  'hp-ux': 'os_hpux',
  'osf1': 'os_tru64',
  'opensolaris': 'os_opensolaris',
  'solaris': 'os_solaris',
  'sunos': 'os_solaris',
  'freebsd': 'os_freebsd',
  'aix': 'os_aix',
  'windows': 'os_win',
  'vmware': 'os_vmware'
}

function cell_decorator_boolean(e) {
  var v = $(e).attr("v")
  true_vals = [1, "1", "T", "True", "true", true]
  if (typeof v === "undefined") {
    var cl = ""
  } else if (true_vals.indexOf(v) >= 0) {
    var cl = "toggle-on"
  } else {
    var cl = "toggle-off"
  }
  s = "<span class='"+cl+"' title='"+v+"'></span>"
  $(e).html(s)
}

function cell_decorator_network(e) {
  var v = $(e).attr("v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var net_id = line.children("[name$=_c_id]").attr("v")
    url = services_get_url() + "/init/networks/segments/"+net_id
    toggle_extra(url, net_id, $(this), 0)
  })
}

function cell_decorator_chk_instance(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var chk_type = line.children("[name$=_chk_type]").attr("v")
  if (chk_type == "mpath") {
    url = services_get_url() + "/init/disks/disks?disks_f_disk_id="+v+"&volatile_filters=true"
    s = "<a class='hd16' href='"+url+"' target='_blank'>"+v+"</a>"
    $(e).html(s)
  }
}

function cell_decorator_chk_high(e) {
  var high = $(e).attr("v")
  var line = $(e).parent(".tl")
  var v = line.children("[name$=_chk_value]").attr("v")
  var cl = []
  v = parseInt(v)
  high = parseInt(high)
  if (v > high) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+high+"</span>")
}

function cell_decorator_chk_low(e) {
  var low = $(e).attr("v")
  var line = $(e).parent(".tl")
  var v = line.children("[name$=_chk_value]").attr("v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  if (v < low) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+low+"</span>")
}

function cell_decorator_chk_value(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var low = line.children("[name$=_chk_low]").attr("v")
  var high = line.children("[name$=_chk_high]").attr("v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  high = parseInt(high)
  if ((v > high) || (v < low)) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+v+"</span>")
}

function cell_decorator_action_pid(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  var s = "<a>"+v+"</a>"
  $(e).html(s)
  $(e).bind('click', function(){
    var line = $(e).parent(".tl")
    var hostname = line.children("[name$=_hostname]").attr("v")
    var svcname = line.children("[name$=_svcname]").attr("v")
    var begin = line.children("[name$=_begin]").attr("v")
    var end = line.children("[name$=_end]").attr("v")

    var _begin = begin.replace(/ /, "T")
    var d = new Date(+new Date(_begin) - 1000*60*60*24)
    begin = print_date(d)

    var _end = end.replace(/ /, "T")
    var d = new Date(+new Date(_end) + 1000*60*60*24)
    end = print_date(d)

    url = services_get_url() + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_hostname="+hostname+"&actions_f_pid="+v+"&actions_f_begin=>"+begin+"&actions_f_end=<"+end+"&volatile_filters=true"

    $(this).children("a").attr("href", url)
    $(this).children("a").attr("target", "_blank")
    //$(this).children("a").click()
  })
}

function cell_decorator_action_status(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).html("<div class='spinner'></div>")
    return
  }
  cl = ["status_"+v.replace(' ', '_')]
  var line = $(e).parent(".tl")
  var ack = line.children("[name$=_ack]").attr("v")
  if (ack == 1) {
    cl.push("ack_1")
  }
  s = "<div class='"+cl.join(" ")+"'>"+v+"</diV>"
  $(e).html(s)
  if (ack != 1) {
    return
  }
  $(e).bind("mouseout", function(){
    ackpanel(event, false, "")
  })
  $(e).bind("mouseover", function(){
    var acked_date = line.children("[name$=_acked_date]").attr("v")
    var acked_by = line.children("[name$=_acked_by]").attr("v")
    var acked_comment = line.children("[name$=_acked_comment]").attr("v")
    s = "<div>"
    s += "<b>acked by </b>"+acked_by+"<br>"
    s += "<b> on </b>"+acked_date+"<br>"
    s += "<b>with comment:</b><br>"+acked_comment
    s += "</div>"
    ackpanel(event, true, s)
  })
}

function cell_decorator_action_end(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  } else if (v == "1000-01-01 00:00:00") {
    $(e).html("<span class='highlight'>timed out</span>")
    return
  }
  var line = $(e).parent(".tl")
  var id = line.children("[name$=_id]").attr("v")
  s = "<span class='highlight nowrap' id='spin_span_end_"+id+"'>"+v+"</span>"
}

function cell_decorator_action_log(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  s = "<pre>"+v+"</pre>"
  $(e).html(s)
}

function cell_decorator_db_table_name(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var s = $("<span class='nowrap'>"+v+"</span>")
  if (v in db_tables) {
    s.text(db_tables[v].title)
    s.addClass(db_tables[v].cl)
  }
  $(e).html(s)
}

function cell_decorator_db_column_name(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var s = $("<span class='nowrap'>"+v+"</span>")
  if (v in db_columns) {
    s.text(db_columns[v].title)
    s.addClass(db_columns[v].img)
  }
  $(e).html(s)
}

function cell_decorator_action(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var status_log = line.children("[name$=status_log]").attr("v")
  cl = []
  if (status_log == "empty") {
    cl.push("metaaction")
  }
  action = v.split(/\s+/).pop()
  if (action in action_img_h) {
    cl.push(action_img_h[action])
  }
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_svc_action_err(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  var line = $(e).parent(".tl")
  var svcname = line.children("[name$=mon_svcname]").attr("v")
  url = services_get_url() + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&volatile_filters=true"
  s = "<a class='action16 icon-red clickable' href='"+url+"' target='_blank'>"+v+"</a>"
  $(e).html(s)
}

function cell_decorator_nodename(e) {
  _cell_decorator_nodename(e, true)
}

function cell_decorator_nodename_no_os(e) {
  _cell_decorator_nodename(e, false)
}

function _cell_decorator_nodename(e, os_icon) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div class='a nowrap'>"+v+"</div>")
  $(e).addClass("corner")
  div = $(":first-child", e)
  if (os_icon) {
    try {
      os_cell = $(e).parent().children(".os_name")
      os_c = os_class_h[os_cell.attr("v").toLowerCase()]
      div.addClass(os_c)
    } catch(e) {}
  }
  try {
    svc_autostart_cell = $(e).parent().children(".svc_autostart")
    if (svc_autostart_cell.attr("v") == v) {
      div.addClass("b")
    }
  } catch(e) {}
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(null, id, e, 0)
    node_tabs(id, {"nodename": v})
  })
}

function cell_decorator_groups(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).addClass("corner")
  l = v.split(', ')
  s = ""
  for (i=0; i<l.length; i++) {
    g = l[i]
    s += "<span>"+g+"</span>"
  }
  $(e).html(s)
  table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
  span_id = $(e).parent(".tl").attr("spansum")
  id = table_id + "_x_" + span_id
  $(e).children().each(function(){
    $(this).click(function(){
      if (get_selected() != "") {return}
      g = $(this).text()
      url = services_get_url() + "/init/ajax_group/ajax_group?groupname="+encodeURIComponent(g)+"&rowid="+id
      toggle_extra(url, id, e, 0)
    })
  })
}

function cell_decorator_username(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  var line = $(e).parent(".tl")
  var user_id = line.children("[name$=_c_id]").attr("v")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/ajax_user/ajax_user?user_id="+encodeURIComponent(user_id)+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_svcname(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div class='a nowrap'>"+v+"</div>")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(null, id, e, 0)
    service_tabs(id, {"svcname": v})
  })
}

function cell_decorator_status(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    v = "undef"
  }
  var c = v
  var line = $(e).parent(".tl")
  if (status_outdated(line)) {
    c = "undef"
  }
  t = {
    "warn": "orange",
    "up": "green",
    "stdby up": "green",
    "down": "red",
    "stdby down": "red",
    "undef": "gray",
    "n/a": "gray",
  }
  $(e).html("<div class='svc nowrap icon-"+t[c]+"'></div>")
}

function cell_decorator_reports_links(e) {
  $(e).empty()
  $(e).addClass("corner nowrap")

  var line = $(e).parent(".tl")
  var id = line.children("[name$=_c_id]").attr("v")
  var query = "report_id="+id
  url = services_get_url() + "/init/charts/reports_editor?"+query
  var d = "<a class='clickable edit16' target='_blank' href="+url+"></a>"
  $(e).append(d)

  // test chart
  var d = $("<span></span>")
  $(d).addClass("clickable action16")
  $(d).click(function(){
    var table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    var span_id = $(e).parent(".tl").attr("spansum")
    var id = table_id + "_x_" + span_id
    var report_id = $(this).parents(".tl").first().children("[name$=_c_id]").attr("v")
    //url = services_get_url() + "/init/charts/ajax_report_test?report_id="+report_id
    //toggle_extra(url, id, e, 0)
    $(e).parent(".tl").after("<tr><td id='"+id+"' colspan='4'></td></tr>");
    var options = {"report_id" : report_id};
    reports_single(id,options);
  })
  $(e).append(d)
}

function cell_decorator_charts_links(e) {
  $(e).empty()
  $(e).addClass("corner nowrap")

  // editor
  var line = $(e).parent(".tl")
  var id = line.children("[name$=_c_id]").attr("v")
  var query = "chart_id="+id
  url = services_get_url() + "/init/charts/charts_editor?"+query
  var d = "<a class='clickable edit16' target='_blank' href="+url+"></a>"
  $(e).append(d)

  // test chart
  var d = $("<span></span>")
  $(d).addClass("clickable action16")
  $(d).click(function(){
    var table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    var span_id = $(e).parent(".tl").attr("spansum")
    var id = table_id + "_x_" + span_id
    var chart_id = $(this).parents(".tl").first().children("[name$=_c_id]").attr("v")
    url = services_get_url() + "/init/charts/ajax_chart_test?chart_id="+chart_id
    toggle_extra(url, id, e, 0)
  })
  $(e).append(d)
}

function cell_decorator_metrics_links(e) {
  $(e).empty()
  $(e).addClass("corner nowrap")

  // editor
  var line = $(e).parent(".tl")
  var id = line.children("[name$=_c_id]").attr("v")
  var query = "metric_id="+id
  url = services_get_url() + "/init/charts/metrics_editor?"+query
  var d = "<a class='clickable edit16' target='_blank' href="+url+"></a>"
  $(e).append(d)

  // test metric
  var d = $("<span></span>")
  $(d).addClass("clickable action16")
  $(d).click(function(){
    var table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    var span_id = $(e).parent(".tl").attr("spansum")
    var id = table_id + "_x_" + span_id
    var metric_id = $(this).parents(".tl").first().children("[name$=_c_id]").attr("v")
    url = services_get_url() + "/init/charts/ajax_metric_test?metric_id="+metric_id
    toggle_extra(url, id, e, 0)
  })
  $(e).append(d)
}

function cell_decorator_dns_records_type(e) {
  var v = $(e).attr("v")
  var cl = ["boxed_small"]
  if ((v == "A") || (v == "PTR")) {
    cl.push("bgblack")
  } else if (v == "CNAME") {
    cl.push("bggreen")
  } else {
    cl.push("bgred")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_dns_records_links(e) {
  $(e).empty()
  var line = $(e).parent(".tl")
  var record_id = line.children("[name$=_c_id]").attr("v")

  var query = "record_id="+record_id
  var query = query + "&_next="+window.location
  url = services_get_url() + "/init/dns/record_edit?"+query
  var d = $("<a class='clickable icon edit16' target='_blank' href="+url+"></a>")
  $(e).append(d)
}

function cell_decorator_dns_domains_links(e) {
  $(e).empty()
  var line = $(e).parent(".tl")
  var domain_id = line.children("[name$=_c_id]").attr("v")

  var query = "domain_id="+domain_id
  var query = query + "&_next="+window.location
  url = services_get_url() + "/init/dns/domain_edit?"+query
  var d = $("<a class='clickable icon edit16' target='_blank' href="+url+"></a>")
  $(e).append(d)

  var query = "domain_id="+domain_id
  var query = query + "&_next="+window.location
  url = services_get_url() + "/init/dns/domain_sync?"+query
  var d = $("<a class='clickable icon action_sync_16' target='_blank' href="+url+"></a>")
  $(e).append(d)
}

function cell_decorator_forms_links(e) {
  var line = $(e).parent(".tl")
  var form_id = line.children("[name$=_c_id]").attr("v")
  var query = "form_id="+form_id
  url = services_get_url() + "/init/forms/forms_editor?"+query
  var d = "<a class='clickable edit16' target='_blank' href="+url+"></a>"
  $(e).html(d)
}

function cell_decorator_svcmon_links(e) {
  var line = $(e).parent(".tl")
  var mon_svcname = line.children("[name$=mon_svcname]").attr("v")
  var query = "volatile_filters=true&actions_f_svcname="+mon_svcname
  query += "&actions_f_status_log=empty"
  query += "&actions_f_begin="+encodeURIComponent(">-1d")
  url = services_get_url() + "/init/svcactions/svcactions?"+query
  var d = "<a class='clickable action16' target='_blank' href="+url+"></a>"

  var mon_frozen = line.children("[name$=mon_frozen]").attr("v")
  if (mon_frozen == "1") {
    d += "<span class='frozen16'>&nbsp</span>"
  }
  $(e).html(d)
}

function cell_decorator_chk_type(e) {
  var v = $(e).attr("v")
  if (v=="") {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/checks/ajax_chk_type_defaults/"+v
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_dash_link_comp_tab(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  s = "<div class='comp16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (svcname != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      toggle_extra(null, id, e, 0)
      service_tabs(id, {"svcname": svcname, "tab": "service_tabs.compliance"})
    })
  } else if (nodename != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      toggle_extra(null, id, e, 0)
      node_tabs(id, {"nodename": nodename, "tab": "node_tabs.compliance"})
    })
  }
}

function cell_decorator_dash_link_pkg_tab(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  s = "<div class='pkg16 clickable'></div>"
  $(e).html(s)
  $(e).addClass("corner")
  if (svcname != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      toggle_extra(null, id, e, 0)
      service_tabs(id, {"svcname": svcname, "tab": "service_tabs.pkgdiff"})
    })
  }
}

function cell_decorator_dash_link_feed_queue(e) {
  s = "<a class='action16' href=''></a>"
  $(e).html(s)
}

function _cell_decorator_dash_link_actions(svcname) {
  url = services_get_url() + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_begin=>-7d&volatile_filters=true"
  s = "<a class='action16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function _cell_decorator_dash_link_action_error(svcname) {
  url = services_get_url() + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&volatile_filters=true"
  s = "<a class='alert16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_action_error(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_action_error(svcname)
  s += _cell_decorator_dash_link_actions(svcname)
  $(e).html(s)
}

function _cell_decorator_dash_link_svcmon(svcname) {
  url = services_get_url() + "/init/default/svcmon?svcmon_f_mon_svcname="+svcname+"&volatile_filters=true"
  s = "<a class='svc clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_svcmon(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_svcmon(svcname)
  $(e).html(s)
}

function _cell_decorator_dash_link_node(nodename) {
  url = services_get_url() + "/init/nodes/nodes?nodes_f_nodename="+nodename+"&volatile_filters=true"
  s = "<a class='node16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_node(e) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_node(nodename)
  $(e).html(s)
}

function _cell_decorator_dash_link_checks(nodename) {
  url = services_get_url() + "/init/checks/checks?checks_f_chk_nodename="+nodename+"&volatile_filters=true"
  s = "<a class='check16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_checks(e) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_checks(nodename)
  $(e).html(s)
}

function _cell_decorator_dash_link_mac_networks(mac) {
  url = services_get_url() + "/init/nodenetworks/nodenetworks?nodenetworks_f_mac="+mac+"&volatile_filters=true"
  s = "<a class='net16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_mac_duplicate(e) {
  var line = $(e).parent(".tl")
  var mac = line.find("[name$=dash_entry]").attr("v").split(" ")[1]
  var s = ""
  s += _cell_decorator_dash_link_mac_networks(mac)
  $(e).html(s)
}

function cell_decorator_dash_link_obsolescence(e, t) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  url = services_get_url() + "/init/obsolescence/obsolescence_config?obs_f_obs_type="+t+"&volatile_filters=true"
  s = "<a class='"+t+"16 clickable' target='_blank' href='"+url+"'></a>"
  $(e).html(s)
}

function cell_decorator_dash_links(e) {
  var line = $(e).parent(".tl")
  var dash_type = line.find("[name$=dash_type]").attr("v")
  if (dash_type == "action errors") {
    cell_decorator_dash_link_action_error(e)
  } else if ((dash_type == "node warranty expired") ||
             (dash_type == "node without warranty end date") ||
             (dash_type == "node without asset information") ||
             (dash_type == "node close to warranty end") ||
             (dash_type == "node information not updated")) {
    cell_decorator_dash_link_node(e)
  } else if ((dash_type == "check out of bounds") ||
             (dash_type == "check value not updated")) {
    cell_decorator_dash_link_checks(e)
  } else if (dash_type == "mac duplicate") {
    cell_decorator_dash_link_mac_duplicate(e)
  } else if ((dash_type == "service available but degraded") ||
             (dash_type == "service status not updated") ||
             (dash_type == "service configuration not updated") ||
             (dash_type == "service frozen") ||
             (dash_type == "flex error") ||
             (dash_type == "service unavailable")) {
    cell_decorator_dash_link_svcmon(e)
  } else if (dash_type == "feed queue") {
    cell_decorator_dash_link_feed_queue(e)
  } else if (dash_type.indexOf("os obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "os")
  } else if (dash_type.indexOf("obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "hw")
  } else if (dash_type.indexOf("comp") == 0) {
    cell_decorator_dash_link_comp_tab(e)
  } else if (dash_type.indexOf("package") == 0) {
    cell_decorator_dash_link_pkg_tab(e)
  }
}

function cell_decorator_action_cron(e) {
  var v = $(e).attr("v")
  var l = []
  if (v == 1) {
      l.push("time16")
  }
  $(e).html("<div class='"+l.join(" ")+"'></div>")
}

function cell_decorator_dash_severity(e) {
  var v = $(e).attr("v")
  var l = []
  if (v == 0) {
      l.push("alertgreen")
  } else if (v == 1) {
      l.push("alertorange")
  } else if (v == 2) {
      l.push("alertred")
  } else if (v == 3) {
      l.push("alertdarkred")
  } else {
      l.push("alertblack")
  }
  $(e).html("<div class='"+l.join(" ")+"' title='"+v+"'></div>")
}

function cell_decorator_form_id(e) {
  var v = $(e).attr("v")
  var s = ""
  url = services_get_url() + "/init/forms/workflow?wfid="+v+"&volatile_filters=true"
  s = "<a class='wf16 icon nowrap clickable' target='_blank' href='"+url+"'>"+v+"</a>"
  $(e).html(s)
}

function cell_decorator_run_log(e) {
  var v = $(e).attr("v")
  if (typeof v === "undefined") {
    var s = ""
  } else {
    var s = "<pre>"+v.replace(/ERR:/g, "<span class='err'>ERR:</span>")+"</pre>"
  }
  $(e).html(s)
}

function cell_decorator_run_status(e) {
  var v = $(e).attr("v")
  var s = ""
  var cl = ""
  var _v = ""
  if (v == 0) {
    cl = "check16"
  } else if (v == 1) {
    cl = "nok"
  } else if (v == 2) {
    cl = "na"
  } else if (v == -15) {
    cl = "kill16"
  } else {
    _v = v
  }
  $(e).html("<div class='"+cl+"'>"+_v+"</div>")
}

function cell_decorator_disk_array(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var line = $(e).parent(".tl")
  var model = line.find("[name$=_array_model]").attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/disks/ajax_array?array="+v+"&rowid="+id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_disk_array_dg(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    array = line.find("[name$=_disk_arrayid],[name$=_array_name]").attr("v")
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    url = services_get_url() + "/init/disks/ajax_array_dg?array="+array+"&dg="+v+"&rowid="+id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_tag_exclude(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    v = ""
  }
  $(e).html(v)
  $(window).bind("click", function() {
    $("input.tag_exclude").parent().html(v)
  })
  $(e).bind("click", function(){
    event.stopPropagation()
    i = $("<input class='tag_exclude'></input>")
    var _v = $(this).attr("v")
    if (_v == "empty") {
      _v = ""
    }
    i.val(_v)
    i.bind("keyup", function(){
      if (!is_enter(event)) {
        return
      }
      var url = services_get_url() + "/init/tags/call/json/tag_exclude"
      var data = {
        "tag_exclude": $(this).val(),
        "tag_id": $(this).parents(".tl").find("[name=tags_c_id]").attr("v")
      }
      var _i = $(this)
      $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
          _i.parent().html(data.tag_exclude)
        }
      })
    })
    $(e).empty().append(i)
    i.focus()
  })
}

function cell_decorator_dash_entry(e) {
  var v = $(e).attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    var nodename = line.children("[name$=dash_nodename]").attr("v")
    var svcname = line.children("[name$=dash_svcname]").attr("v")
    var dash_md5 = line.children("[name$=dash_md5]").attr("v")
    var dash_created = line.children("[name$=dash_created]").attr("v")
    var rowid = line.attr("cksum")
    url = services_get_url() + "/init/dashboard/ajax_alert_events?dash_nodename="+nodename+"&dash_svcname="+svcname+"&dash_md5="+dash_md5+"&dash_created="+dash_created+"&rowid="+rowid
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_rset_md5(e) {
  var v = $(e).attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = services_get_url() + "/init/compliance/ajax_rset_md5?rset_md5="+v
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_action_q_ret(e) {
  var v = $(e).attr("v")
  var cl = ["boxed_small"]
  if (v == 0) {
    cl.push("bggreen")
  } else {
    cl.push("bgred")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_action_q_status(e) {
  var v = $(e).attr("v")
  var st = ""
  var cl = ["boxed_small"]
  if (v == "T") {
    cl.push("bggreen")
    st = i18n.t("decorators.done")
  } else if (v == "R") {
    cl.push("bgred")
    st = i18n.t("decorators.running")
  } else if (v == "W") {
    st = i18n.t("decorators.waiting")
  } else if (v == "Q") {
    st = i18n.t("decorators.queued")
  } else if (v == "C") {
    cl.push("bgdarkred")
    st = i18n.t("decorators.cancelled")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+st+"</div>"
  $(e).html(s)
}

function datetime_age(s) {
  // return age in minutes
  if (typeof s === 'undefined') {
    return
  }
  if (s == 'empty') {
    return
  }
  s = s.replace(/ /, "T")
  var d = new Date(s)
  var now = new Date()
  delta = now.getTime() - d.getTime() - now.getTimezoneOffset() * 60000
  return delta / 60000
}

function _outdated(s, max_age) {
  delta = datetime_age(s)
  if (!delta) {
    return true
  }
  if (delta > max_age) {
    return true
  }
  return false
}

function status_outdated(line) {
  var s = line.children("[cell=1][name$=mon_updated]").attr("v")
  if (typeof s === 'undefined') {
    var s = line.children("[cell=1][name$=status_updated]").attr("v")
  }
  if (typeof s === 'undefined') {
    var s = line.children("[cell=1][name$=_updated]").attr("v")
  }
  return _outdated(s, 15)
}

function cell_decorator_date_no_age(e) {
  v = $(e).attr("v")
  if (typeof v === 'undefined') {
    return
  }
  s = v.split(" ")[0]
  $(e).html(s)
}

function cell_decorator_datetime_no_age(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_date_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_status(e) {
  $(e).attr("max_age", 15)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_daily(e) {
  $(e).attr("max_age", 1440)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_weekly(e) {
  $(e).attr("max_age", 10080)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime(e) {
  var s = $(e).attr("v")
  var max_age = $(e).attr("max_age")
  var delta = datetime_age(s)

  if (!delta) {
    $(e).html()
    return
  }

  if (delta > 0) {
    var prefix = "-"
  } else {
    var prefix = ""
    delta = -delta
  }

  var hour = 60
  var day = 1440
  var week = 10080
  var month = 43200
  var year = 524520

  if (delta < hour) {
    var cl = "minute icon"
    var text = prefix + i18n.t("table.minute", {"count": Math.floor(delta)})
    var color = "#000000"
  } else if (delta < day) {
    var cl = "hour icon"
    var text = prefix + i18n.t("table.hour", {"count": Math.floor(delta/hour)})
    var color = "#181818"
  } else if (delta < week) {
    var cl = "day icon "
    var text = prefix + i18n.t("table.day", {"count": Math.floor(delta/day)})
    var color = "#333333"
  } else if (delta < month) {
    var cl = "week icon "
    var text = prefix + i18n.t("table.week", {"count": Math.floor(delta/week)})
    var color = "#333333"
  } else if (delta < year) {
    var cl = "month icon"
    var text = prefix + i18n.t("table.month", {"count": Math.floor(delta/month)})
    var color = "#484848"
  } else {
    var cl = "year icon"
    var text = prefix + i18n.t("table.year", {"count": Math.floor(delta/year)})
    var color = "#666666"
  }

  if ($(e).text() == text) {
    return
  }
  cl += " nowrap"

  if (max_age && (delta > max_age)) {
    cl += " icon-red"
  }
  $(e).html("<div class='"+cl+"' style='color:"+color+"' title='"+s+"'>"+text+"</div>")
}

function cell_decorator_date(e) {
  cell_decorator_datetime(e)
  s = $(e).attr("v")
  $(e).text(s.split(" ")[0])
}

function cell_decorator_env(e) {
  if ($(e).attr("v") != "PRD") {
    return
  }
  s = "<div class='b'>PRD</div>"
  $(e).html(s)
}

function cell_decorator_svc_ha(e) {
  if ($(e).attr("v") != 1) {
    $(e).empty()
    return
  }
  s = "<div class='boxed_small'>HA</div>"
  $(e).html(s)
}

function cell_decorator_size_mb(e) {
  v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_mb(v)+"</div>"
  $(e).html(s)
}

function cell_decorator_size_b(e) {
  v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_b(v)+"</div>"
  $(e).html(s)
}

function cell_decorator_availstatus(e) {
  var line = $(e).parent(".tl")
  var mon_availstatus = $(e).attr("v")
  if (mon_availstatus=="") {
    return
  }
  var mon_containerstatus = line.children("[name$=mon_containerstatus]").attr("v")
  var mon_ipstatus = line.children("[name$=mon_ipstatus]").attr("v")
  var mon_fsstatus = line.children("[name$=mon_fsstatus]").attr("v")
  var mon_diskstatus = line.children("[name$=mon_diskstatus]").attr("v")
  var mon_sharestatus = line.children("[name$=mon_sharestatus]").attr("v")
  var mon_appstatus = line.children("[name$=mon_appstatus]").attr("v")

  if (status_outdated(line)) {
    var cl_availstatus = "status_undef"
    var cl_containerstatus = "status_undef"
    var cl_ipstatus = "status_undef"
    var cl_fsstatus = "status_undef"
    var cl_diskstatus = "status_undef"
    var cl_sharestatus = "status_undef"
    var cl_appstatus = "status_undef"
  } else {
    var cl_availstatus = mon_availstatus.replace(/ /g, '_')
    var cl_containerstatus = mon_containerstatus.replace(/ /g, '_')
    var cl_ipstatus = mon_ipstatus.replace(/ /g, '_')
    var cl_fsstatus = mon_fsstatus.replace(/ /g, '_')
    var cl_diskstatus = mon_diskstatus.replace(/ /g, '_')
    var cl_sharestatus = mon_sharestatus.replace(/ /g, '_')
    var cl_appstatus = mon_appstatus.replace(/ /g, '_')
  }
  var s = "<table>"
  s += "<tr>"
  s += "<td colspan=6 class=\"aggstatus status_" + cl_availstatus + "\">" + mon_availstatus + "</td>"
  s += "</tr>"
  s += "<tr>"
  s += "<td class=status_" + cl_containerstatus + ">vm</td>"
  s += "<td class=status_" + cl_ipstatus + ">ip</td>"
  s += "<td class=status_" + cl_fsstatus + ">fs</td>"
  s += "<td class=status_" + cl_diskstatus + ">dg</td>"
  s += "<td class=status_" + cl_sharestatus + ">share</td>"
  s += "<td class=status_" + cl_appstatus + ">app</td>"
  s += "</tr>"
  s += "</table>"
  $(e).html(s)
}

function cell_decorator_rsetvars(e) {
  var s = $(e).attr("v")
  $(e).html("<pre>"+s.replace(/\|/g, "\n")+"</pre>")
}

function cell_decorator_overallstatus(e) {
  var line = $(e).parent(".tl")
  var mon_overallstatus = $(e).attr("v")
  if (mon_overallstatus=="") {
    return
  }
  var mon_containerstatus = line.children("[name$=mon_containerstatus]").attr("v")
  var mon_availstatus = line.children("[name$=mon_availstatus]").attr("v")
  var mon_hbstatus = line.children("[name$=mon_hbstatus]").attr("v")
  var mon_syncstatus = line.children("[name$=mon_syncstatus]").attr("v")

  if (status_outdated(line)) {
    var cl_overallstatus = "status_undef"
    var cl_availstatus = "status_undef"
    var cl_syncstatus = "status_undef"
    var cl_hbstatus = "status_undef"
  } else {
    var cl_overallstatus = mon_overallstatus.replace(/ /g, '_')
    var cl_availstatus = mon_availstatus.replace(/ /g, '_')
    var cl_syncstatus = mon_syncstatus.replace(/ /g, '_')
    var cl_hbstatus = mon_hbstatus.replace(/ /g, '_')
  }

  var s = "<table>"
  s += "<tr>"
  s += "<td colspan=3 class=\"aggstatus status_" + cl_overallstatus + "\">" + mon_overallstatus + "</td>"
  s += "</tr>"
  s += "<tr>"
  s += "<td class=status_" + cl_availstatus + ">avail</td>"
  s += "<td class=status_" + cl_hbstatus + ">hb</td>"
  s += "<td class=status_" + cl_syncstatus + ">sync</td>"
  s += "</tr>"
  s += "</table>"
  $(e).html(s)
}

function cell_decorator_sql(e) {
  var s = $(e).attr("v")
  var _e = $("<pre></pre>")
  s = s.replace(/(SELECT|FROM|GROUP BY|WHERE)/gi, function(x) {
    return '<span class=syntax_red>'+x+'</span>'
  })
  s = s.replace(/(COUNT|DATE_SUB|SUM|MAX|MIN|CEIL|FLOOR|AVG|CONCAT|GROUP_CONCAT)/gi, function(x) {
    return '<span class=syntax_green>'+x+'</span>'
  })
  s = s.replace(/([\"\']\w*[\"\'])/gi, function(x) {
    return '<span class=syntax_blue>'+x+'</span>'
  })
  s = s.replace(/(%%\w+%%)/gi, function(x) {
    return '<span class=syntax_blue>'+x+'</span>'
  })
  _e.html(s)
  $(e).html(_e)
}

function cell_decorator_yaml(e) {
  var s = $(e).attr("v")
  var _e = $("<pre></pre>")
  s = s.replace(/Id:\s*(\w+)/gi, function(x) {
    return '<span class=syntax_red>'+x+'</span>'
  })
  s = s.replace(/(#\w+)/gi, function(x) {
    return '<span class=syntax_red>'+x+'</span>'
  })
  s = s.replace(/(\w+:)/gi, function(x) {
    return '<span class=syntax_green>'+x+'</span>'
  })
  _e.html(s)
  $(e).html(_e)
}

function cell_decorator_appinfo_key(e) {
  var s = $(e).attr("v")
  var _e = $("<div class='boxed_small'></div>")
  _e.text(s)
  if (s == "Error") {
    _e.addClass("bgred")
  } else {
    _e.addClass("bgblack")
  }
  $(e).html(_e)
}

function cell_decorator_appinfo_value(e) {
  var s = $(e).attr("v")
  var _e = $("<span></span>")
  _e.text(s)
  if (is_numeric(s)) {
    _e.addClass("spark16")
    $(e).addClass("corner clickable")
    $(e).bind("click", function() {
      var line = $(e).parent(".tl")
      var span_id = line.attr("spansum")
      var table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      var id = table_id + "_x_" + span_id
      var params = "svcname="+encodeURIComponent(line.children("[name$=_c_app_svcname]").attr("v"))
      params += "&nodename="+encodeURIComponent(line.children("[name$=_c_app_nodename]").attr("v"))
      params += "&launcher="+encodeURIComponent(line.children("[name$=_c_app_launcher]").attr("v"))
      params += "&key="+encodeURIComponent(line.children("[name$=_c_app_key]").attr("v"))
      params += "&rowid="+encodeURIComponent(id)
      var url = services_get_url() + "/init/appinfo/ajax_appinfo_log?" + params
 
      toggle_extra(url, id, e, 0)
    })
  }
  $(e).html(_e)
}

function cell_decorator_users_role(e) {
  var s = $(e).attr("v")
  $(e).empty()
  if (s == 1) {
    $(e).addClass("admin")
  } else {
    $(e).addClass("guy16")
  }
}

function cell_decorator_users_domain(e) {
  var s = $(e).attr("v")
  if (s == "empty") {
    s = ""
  }
  var span = $("<span class='clickable'></span>")
  var input = $("<input class='hidden oi'></input>")
  var line = $(e).parent(".tl")
  var user_id = line.children("[name$=_c_id]").attr("v")

  if (services_ismemberof(["Manager", "UserManager"])) {
    $(e).hover(
      function() {
        span.addClass("editable")
      },
      function() {
        span.removeClass("editable")
      }
    )
  }
  span.bind("click", function() {
    span.hide()
    input.show()
    input.focus()
    input.select()
  })
  input.bind("blur", function(event) {
    span.show()
    input.hide()
  })
  input.bind("keyup", function(event) {
    if (!is_enter(event)) {
      return
    }
    data = {
      "domains": $(this).val()
    }
    services_osvcpostrest("R_USER_DOMAINS", [user_id], "", data, function(jd) {
      if (!jd.data) {
        span.html(services_error_fmt(jd))
        span.show()
        input.hide()
        return
      }
      span.text(input.val())
      span.show()
      input.hide()
    },
    function(xhr, stat, error) {
      span.html(services_ajax_error_fmt(xhr, stat, error))
      span.show()
      input.hide()
    })
  })

  span.text(s)
  input.val(s)
  $(e).empty()
  $(e).append(span)
  $(e).append(input)
}

cell_decorators = {
 "yaml": cell_decorator_yaml,
 "sql": cell_decorator_sql,
 "rsetvars": cell_decorator_rsetvars,
 "dash_entry": cell_decorator_dash_entry,
 "disk_array_dg": cell_decorator_disk_array_dg,
 "disk_array": cell_decorator_disk_array,
 "size_mb": cell_decorator_size_mb,
 "size_b": cell_decorator_size_b,
 "chk_instance": cell_decorator_chk_instance,
 "chk_value": cell_decorator_chk_value,
 "chk_low": cell_decorator_chk_low,
 "chk_high": cell_decorator_chk_high,
 "db_table_name": cell_decorator_db_table_name,
 "db_column_name": cell_decorator_db_column_name,
 "action": cell_decorator_action,
 "action_pid": cell_decorator_action_pid,
 "action_status": cell_decorator_action_status,
 "action_end": cell_decorator_action_end,
 "action_log": cell_decorator_action_log,
 "action_cron": cell_decorator_action_cron,
 "rset_md5": cell_decorator_rset_md5,
 "run_status": cell_decorator_run_status,
 "run_log": cell_decorator_run_log,
 "form_id": cell_decorator_form_id,
 "action_q_status": cell_decorator_action_q_status,
 "action_q_ret": cell_decorator_action_q_ret,
 "svcname": cell_decorator_svcname,
 "username": cell_decorator_username,
 "groups": cell_decorator_groups,
 "nodename": cell_decorator_nodename,
 "nodename_no_os": cell_decorator_nodename_no_os,
 "svc_action_err": cell_decorator_svc_action_err,
 "availstatus": cell_decorator_availstatus,
 "overallstatus": cell_decorator_overallstatus,
 "chk_type": cell_decorator_chk_type,
 "svcmon_links": cell_decorator_svcmon_links,
 "forms_links": cell_decorator_forms_links,
 "svc_ha": cell_decorator_svc_ha,
 "env": cell_decorator_env,
 "date_future": cell_decorator_date_future,
 "datetime_future": cell_decorator_datetime_future,
 "datetime_weekly": cell_decorator_datetime_weekly,
 "datetime_daily": cell_decorator_datetime_daily,
 "datetime_status": cell_decorator_datetime_status,
 "datetime_no_age": cell_decorator_datetime_no_age,
 "date_no_age": cell_decorator_date_no_age,
 "dash_severity": cell_decorator_dash_severity,
 "dash_links": cell_decorator_dash_links,
 "metrics_links": cell_decorator_metrics_links,
 "charts_links": cell_decorator_charts_links,
 "reports_links": cell_decorator_reports_links,
 "dns_domains_links": cell_decorator_dns_domains_links,
 "dns_records_links": cell_decorator_dns_records_links,
 "dns_records_type": cell_decorator_dns_records_type,
 "tag_exclude": cell_decorator_tag_exclude,
 "_network": cell_decorator_network,
 "boolean": cell_decorator_boolean,
 "status": cell_decorator_status,
 "users_domain": cell_decorator_users_domain,
 "users_role": cell_decorator_users_role,
 "appinfo_key": cell_decorator_appinfo_key,
 "appinfo_value": cell_decorator_appinfo_value
}


