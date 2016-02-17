function table_dns_records(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "dnsr",
		'caller': "table_dns_records",
		'name': "dns_records",
		'ajax_url': '/init/dns/ajax_dns_records',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'domain_id', 'name', 'type', 'content', 'ttl', 'prio', 'change_date'],
		'default_columns': ['domain_id', 'name', 'type', 'content', 'ttl', 'prio'],
		'colprops': {
			"name": {
				"_class": "dns_record",
				"_dataclass": "",
				"img": "dns16",
				"title": "Name"
			},
			"prio": {
				"_class": "",
				"_dataclass": "",
				"img": "dns16",
				"title": "Priority"
			},
			"type": {
				"_class": "dns_records_type",
				"_dataclass": "",
				"img": "dns16",
				"title": "Type"
			}
		},
		'wsable': true,
		'events': ['pdns_records_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_dns_records_domain_id(divid, domain_id) {
	var id = "dnsr_" + domain_id
	var f = id+"_f_domain_id"
	var request_vars = {}
	request_vars[f] = domain_id
	table_dns_records(divid, {
		"id": id,
		"caller": "table_dns_records_domain_id",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
	})
}

function table_dns_domains(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_dns_domains",
		'id': "dnsd",
		'name': "dns_domains",
		'ajax_url': '/init/dns/ajax_dns_domains',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'name', 'master', 'last_check', 'type', 'notified_serial', 'account'],
		'default_columns': ['name', 'master', 'type', 'notified_serial'],
		"colprops": {
			"name": {
				"_class": "dns_domain",
				"_dataclass": "",
				"img": "dns16",
				"title": "Name"
			},
			"type": {
				"_class": "",
				"_dataclass": "",
				"img": "dns16",
				"title": "Type"
			}
		},
		'wsable': true,
		'events': ['pdns_domains_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_dns(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/dns.html", function() {
		$(this).i18n()
		table_dns_domains("dnsddiv", options)
		table_dns_records("dnsrdiv", options)
	})
}

