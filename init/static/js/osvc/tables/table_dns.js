table_dns_records_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/dns/ajax_dns_records',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'domain_id', 'name', 'type', 'content', 'ttl', 'prio', 'change_date'],
     'colprops': {'name': {'field': 'name', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Name', '_class': 'dns_record', 'table': 'records', 'display': 1, 'default_filter': ''}, 'prio': {'field': 'prio', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Priority', '_class': '', 'table': 'records', 'display': 1, 'default_filter': ''}, 'domain_id': {'field': 'domain_id', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Domain Id', '_class': '', 'table': 'records', 'display': 1, 'default_filter': ''}, 'content': {'field': 'content', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Content', '_class': '', 'table': 'records', 'display': 1, 'default_filter': ''}, 'ttl': {'field': 'ttl', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Time to Live', '_class': '', 'table': 'records', 'display': 1, 'default_filter': ''}, 'change_date': {'field': 'change_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last change', '_class': '', 'table': 'records', 'display': 0, 'default_filter': ''}, 'type': {'field': 'type', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Type', '_class': 'dns_records_type', 'table': 'records', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Record Id', '_class': '', 'table': 'records', 'display': 0, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': false,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': true,
     'pageable': true,
     'on_change': false,
     'events': ['pdns_records_change'],
     'request_vars': {}
}

function table_dns_records(divid, options) {
  var _options = {"id": "dnsr"}
  $.extend(true, _options, table_dns_records_defaults, options)
  _options.divid = divid
  _options.caller = "table_dns_records"
  table_init(_options)
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

table_dns_domains_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/dns/ajax_dns_domains',
     'span': ['id'],
     'force_cols': ['id'],
     'columns': ['id', 'name', 'master', 'last_check', 'type', 'notified_serial', 'account'],
     'colprops': {'account': {'field': 'account', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Account', '_class': '', 'table': 'domains', 'display': 0, 'default_filter': ''}, 'name': {'field': 'name', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Name', '_class': 'dns_domain', 'table': 'domains', 'display': 1, 'default_filter': ''}, 'last_check': {'field': 'last_check', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last Check', '_class': '', 'table': 'domains', 'display': 0, 'default_filter': ''}, 'notified_serial': {'field': 'notified_serial', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Notified Serial', '_class': '', 'table': 'domains', 'display': 1, 'default_filter': ''}, 'master': {'field': 'master', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Master', '_class': '', 'table': 'domains', 'display': 0, 'default_filter': ''}, 'type': {'field': 'type', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Type', '_class': '', 'table': 'domains', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'dns16', '_dataclass': '', 'title': 'Domain Id', '_class': '', 'table': 'domains', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': false,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': true,
     'pageable': true,
     'on_change': false,
     'events': ['pdns_domains_change'],
     'request_vars': {}
}

function table_dns_domains(divid, options) {
  var _options = {"id": "dnsd"}
  $.extend(true, _options, table_dns_domains_defaults, options)
  _options.divid = divid
  _options.caller = "table_dns_domains"
  table_init(_options)
}

function view_dns(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/dns.html", function() {
		$(this).i18n()
		table_dns_domains("dnsddiv", options)
		table_dns_records("dnsrdiv", options)
	})
}

