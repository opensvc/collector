//
// array
//
function disk_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.disk
	o.options.icon = "hd16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		var title = o.options.disk_id
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon hd16"
		})
		o.tabs[i].callback = function(divid) {
			disk_properties(divid, {"disk_id": o.options.disk_id})
		}

		// tab disks
		i = o.register_tab({
			"title": "table.name.disks",
			"title_class": "icon hd16"
		})
		o.tabs[i].callback = function(divid) {
			table_disks_disk(divid, o.options.disk_id)
		}

		o.set_tab(o.options.tab)
	})

	return o
}


function disk_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_disk_id = o.div.find("#disk_id")
		o.info_disk_vendor = o.div.find("#disk_vendor")
		o.info_disk_model = o.div.find("#disk_model")
		o.info_size = o.div.find("#size")
		o.info_array_name = o.div.find("#array_name")
		o.info_array_dg = o.div.find("#array_dg")
		o.info_disk_name = o.div.find("#disk_name")
		o.info_disk_devid = o.div.find("#disk_devid")
		o.info_disk_raid = o.div.find("#disk_raid")
		o.info_disk_size = o.div.find("#disk_size")
		o.info_disk_alloc = o.div.find("#disk_alloc")
		o.info_nodes = o.div.find("#nodes")
		o.info_services = o.div.find("#services")
		o.info_apps = o.div.find("#apps")
		o.info_nodes_title = o.div.find("#nodes_title")
		o.info_services_title = o.div.find("#services_title")
		o.info_apps_title = o.div.find("#apps_title")
		o.info_disk_updated = o.div.find("#disk_updated")
		o.info_svcdisks_updated = o.div.find("#svcdisks_updated")
		o.load_disk()
	}

	o.load_disk = function() {
		services_osvcgetrest("/disks/%1", [o.options.disk_id], {"props": "nodes.nodename,nodes.app,services.svcname,services.svc_app,svcdisks.node_id,svcdisks.svc_id,diskinfo.disk_id,svcdisks.disk_model,svcdisks.disk_vendor,stor_array.array_name,diskinfo.disk_group,diskinfo.disk_name,diskinfo.disk_devid,diskinfo.disk_raid,svcdisks.disk_size,diskinfo.disk_size,diskinfo.disk_alloc,stor_array.array_updated,svcdisks.disk_updated"}, function(jd) {
			o.data = jd.data[0]
			o.data_nodes = []
			o.data_services = []
			o.data_apps = []
			o.data_apps_flat = []
			for (var i=0; i<jd.data.length; i++) {
				if (jd.data[i].svcdisks.node_id) {
					o.data_nodes.push({
						"nodename": jd.data[i].nodes.nodename,
						"node_id": jd.data[i].svcdisks.node_id,
					})
				}
				if (jd.data[i].svcdisks.svc_id) {
					o.data_services.push({
						"svcname": jd.data[i].services.svcname,
						"svc_id": jd.data[i].svcdisks.svc_id,
					})
				}
				var app = jd.data[i].services.svc_app
				if (app && o.data_apps_flat.indexOf(app) < 0) {
					o.data_apps_flat.push(app)
					o.data_apps.push({
						"app": app,
					})
				}
				app = jd.data[i].nodes.app
				if (app && o.data_apps_flat.indexOf(app) < 0) {
					o.data_apps_flat.push(app)
					o.data_apps.push({
						"app": app,
					})
				}
			}
			o._load_disk()
		})
	}

	o._load_disk = function() {
		o.info_disk_id.html(o.data.diskinfo.disk_id)
		o.info_disk_model.html(o.data.svcdisks.disk_model)
		o.info_disk_vendor.html(o.data.svcdisks.disk_vendor)
		o.info_array_name.html(o.data.stor_array.array_name)
		o.info_array_dg.html(o.data.diskinfo.disk_group)
		o.info_disk_name.html(o.data.diskinfo.disk_name)
		o.info_disk_devid.html(o.data.diskinfo.disk_devid)
		o.info_disk_raid.html(o.data.diskinfo.disk_raid)
		$.data(o.info_size[0], "v", o.data.svcdisks.disk_size)
		cell_decorator_size_mb(o.info_size)
		$.data(o.info_disk_size[0], "v", o.data.diskinfo.disk_size)
		cell_decorator_size_mb(o.info_disk_size)
		$.data(o.info_disk_alloc[0], "v", o.data.diskinfo.disk_alloc)
		cell_decorator_size_mb(o.info_disk_alloc)
		o.info_disk_updated.html(osvc_date_from_collector(o.data.stor_array.array_updated))
		o.info_svcdisks_updated.html(osvc_date_from_collector(o.data.svcdisks.disk_updated))

		o.info_array_name.attr("array_id", o.data.stor_array.array_name)
		o.info_array_name.osvc_array()

		o.info_array_dg.attr("array_name", o.data.stor_array.array_name)
		o.info_array_dg.attr("dg_name", o.data.diskinfo.disk_group)
		o.info_array_dg.osvc_diskgroup()

		tab_properties_generic_list({
			"data": o.data_nodes,
			"key": "nodename",
			"item_class": "icon node16",
			"id": "node_id",
			"flash_id_prefix": "node",
			"title": "disk_properties.nodes",
			"bgcolor": osvc.colors.node,
			"e_title": o.info_nodes_title,
			"e_list": o.info_nodes,
			"lowercase": true,
			"ondblclick": function(divid, data) {
				node_tabs(divid, {"node_id": data.id})
			}
		})
		tab_properties_generic_list({
			"data": o.data_services,
			"key": "svcname",
			"item_class": "icon svc",
			"id": "svc_id",
			"flash_id_prefix": "svc",
			"title": "disk_properties.services",
			"bgcolor": osvc.colors.svc,
			"e_title": o.info_services_title,
			"e_list": o.info_services,
			"lowercase": true,
			"ondblclick": function(divid, data) {
				service_tabs(divid, {"svc_id": data.id})
			}
		})
		tab_properties_generic_list({
			"data": o.data_apps,
			"key": "app",
			"item_class": "icon app16",
			"id": "app",
			"flash_id_prefix": "app",
			"title": "disk_properties.apps",
			"bgcolor": osvc.colors.app,
			"e_title": o.info_apps_title,
			"e_list": o.info_apps,
			"lowercase": true,
			"ondblclick": function(divid, data) {
				app_tabs(divid, {"app_name": data.id})
			}
		})

	}

	o.div.load("/init/static/views/disk_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

