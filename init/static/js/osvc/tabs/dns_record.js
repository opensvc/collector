//
// dns records
//
function dns_record_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.dns
	o.options.icon = "dns16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		services_osvcgetrest("R_DNS_RECORD", [o.options.record_id], {"meta": "0"}, function(jd) {
			o.data = jd.data[0]
			o._load()
		})
	})

	o._load = function() {
		var title = o.data.name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "dns_record_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			dns_record_properties(divid, o.options)
		}

		if ((typeof(o.data.type) === "string") && (o.data.type.length > 0) && (o.data.type[0] == "A")) {
			// tab alerts
			i = o.register_tab({
				"title": "dns_record_tabs.nodes",
				"title_class": "icon node16"
			})
			o.tabs[i].callback = function(divid) {
				table_nodenetworks_addr(divid, o.data.content)
			}
		}

		o.set_tab(o.options.tab)
	}

	return o
}

function dns_record_properties(divid, options) {
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
		o.info_id = o.div.find("#id")
		o.info_name = o.div.find("#name")
		o.info_type = o.div.find("#type")
		o.info_content = o.div.find("#content")
		o.info_prio = o.div.find("#prio")
		o.info_ttl = o.div.find("#ttl")
		o.info_domain = o.div.find("#domain")
		o.info_change_date = o.div.find("#change_date")
		o.info_nodes = o.div.find("#nodes")
		o.load_dns_record()
	}

	o.load_dns_record = function() {
		services_osvcgetrest("R_DNS_RECORD", [o.options.record_id], "", function(jd) {
			o._load_dns_record(jd.data[0])
		})
	}

	o._load_dns_record = function(data) {
		o.info_id.html(data.id)
		o.info_name.html(data.name)
		o.info_type.html(data.type)
		o.info_content.html(data.content)
		o.info_prio.html(data.prio)
		o.info_ttl.html(data.ttl)
		o.info_change_date.html(data.change_date)
		osvc_tools(o.div, {
			"link": o.link
		})

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
								"fn": "data_action_del_dns_records",
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

		services_osvcgetrest("R_DNS_DOMAIN", [data.domain_id], "", function(jd) {
			o.info_domain.html(jd.data[0].name)
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["DnsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("R_DNS_RECORD", [o.options.record_id], "", data, callback, error_callback)
			}
		})
		tab_properties_generic_autocomplete({
			"div": o.info_domain,
			"privileges": ["FormsManager", "Manager"],
			"value_key": "domain_id",
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("R_DNS_RECORD", [data.id], "", _data, callback, error_callback)
			},
			"get": function(callback) {
				services_osvcgetrest("R_DNS_DOMAINS", "", "", function(jd) {
					var opts = []
					for (var i=0; i<jd.data.length; i++) {
						opts.push({
							"label": jd.data[i].name,
							"value": jd.data[i].id
						})
					}
					callback(opts)
				})
			}
		})
		tab_properties_generic_autocomplete({
			"div": o.info_type,
			"privileges": ["FormsManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("R_DNS_RECORD", [data.id], "", _data, callback, error_callback)
			},
			"get": function(callback) {
				var opts = [
					"A",
					"AAAA",
					"A6",
					"CNAME",
					"DNAME",
					"DNSKEY",
					"DS",
					"HINFO",
					"ISDN",
					"KEY",
					"LOC",
					"MX",
					"NAPTR",
					"NS",
					"NSEC",
					"PTR",
					"SOA",
					"SRV",
					"TXT"
				]
				callback(opts)
			}
		})
	}

	o.div.load("/init/static/views/dns_record_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

