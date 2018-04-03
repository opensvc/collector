//
// dns domains
//
function dns_domain_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.dns
	o.options.icon = "dns16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		services_osvcgetrest("R_DNS_DOMAIN", [o.options.domain_id], {"meta": "0"}, function(jd) {
			o.data = jd.data[0]
			o._load()
		})
	})

	o._load = function() {
		var title = o.data.name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "dns_domain_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			dns_domain_properties(divid, o.options)
		}

		// tab records
		i = o.register_tab({
			"title": "dns_domain_tabs.records",
			"title_class": "icon dns16"
		})
		o.tabs[i].callback = function(divid) {
			table_dns_records_domain_id(divid, o.options.domain_id)
		}
		o.set_tab(o.options.tab)
	}

	return o
}

function dns_domain_properties(divid, options) {
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
		o.info_id = o.div.find("#id")
		o.info_name = o.div.find("#name")
		o.info_type = o.div.find("#type")
		o.info_account = o.div.find("#account")
		o.info_last_check = o.div.find("#last_check")
		o.info_notified_serial = o.div.find("#notified_serial")
		o.info_master = o.div.find("#master")

		o.load_dns_domain()
	}

	o.load_dns_domain = function() {
		services_osvcgetrest("R_DNS_DOMAIN", [o.options.domain_id], "", function(jd) {
			o._load_dns_domain(jd.data[0])
		})
	}

	o._load_dns_domain = function(data) {
		o.info_id.html(data.id)
		o.info_name.html(data.name)
		o.info_type.html(data.type)
		o.info_account.html(data.account)
		o.info_last_check.html(data.last_check)
		o.info_notified_serial.html(data.notified_serial)
		o.info_master.html(data.master)

		var am_data = [
			{
				"title": "action_menu.data_actions",
				"children": [
					{
						"selector": ["tab"],
						"foldable": false,
						"cols": [],
						"children": [
							{
								"title": "action_menu.del",
								"class": "del16",
								"fn": "data_action_del_dns_domains",
								"privileges": ["Manager", "DnsManager"]
							},
							{
								"title": "action_menu.sync_dns_domains",
								"class": "net16",
								"fn": "data_action_sync_dns_domains",
								"privileges": ["Manager", "DnsManager"]
							}

						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"id": data.id},
			"am_data": am_data
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["DnsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("R_DNS_DOMAIN", [o.options.domain_id], "", data, callback, error_callback)
			}
		})
		tab_properties_generic_autocomplete({
			"div": o.info_type,
			"privileges": ["DnsManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("R_DNS_DOMAIN", [data.id], "", _data, callback, error_callback)
			},
			"get": function(callback) {
				var opts = ["NATIVE", "MASTER", "SLAVE"]
				callback(opts)
			}
		})
	}

	o.div.load("/init/static/views/dns_domain_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

