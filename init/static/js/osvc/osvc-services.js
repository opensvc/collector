var _self;
var _groups = [];
var services_access_uri = {
	"S_SYSREP" : "ajax_sysreport/ajax_sysrep",
	"S_SYSREPVIEW" : "ajax_sysreport/sysrep",
	"S_SYSREPDIFFVIEW" : "ajax_sysreport/sysrepdiff",
	"S_SYSREPDIFF" : "ajax_sysreport/ajax_sysrepdiff",
	"S_SYSREPCOMMIT" : "ajax_sysreport/ajax_sysreport_commit",
	"S_SYSREPADMIN" : "ajax_sysreport/ajax_sysreport_admin",
	"S_SYSREPSHOWFILE" : "ajax_sysreport/ajax_sysreport_show_file",
	"R_ACTIONS" : "/actions",
	"R_ALERT_EVENT" : "/alert_event",
	"R_API" : "/",
	"R_APP" : "/apps/%1",
	"R_APPS" : "/apps",
	"R_APP_AM_I_RESPONSIBLE" : "/apps/%1/am_i_responsible",
	"R_APP_RESPONSIBLES" : "/apps/%1/responsibles",
	"R_APP_RESPONSIBLE" : "/apps/%1/responsibles/%2",
	"R_APP_PUBLICATION" : "/apps/%1/publications/%2",
	"R_APP_SERVICES" : "/apps/%1/services",
	"R_APP_NODES" : "/apps/%1/nodes",
	"R_APPS_RESPONSIBLES" : "/apps_responsibles",
	"R_ARRAY" : "/arrays/%1",
	"R_ARRAY_DISKGROUP" : "/arrays/%1/diskgroups/%2",
	"R_ARRAY_DISKGROUP_QUOTA" : "/arrays/%1/diskgroups/%2/quotas/%3",
	"R_ARRAY_DISKGROUP_QUOTAS" : "/arrays/%1/diskgroups/%2/quotas",
	"R_CHECKS" : "/checks/live",
	"R_CHECKS_SETTINGS" : "/checks/settings",
	"R_CHECKS_CONTEXTUAL_SETTINGS" : "/checks/contextual_settings",
	"R_COMPLIANCE_MODULESETS" : "/compliance/modulesets",
	"R_COMPLIANCE_MODULESETS_NODES" : "/compliance/modulesets_nodes",
	"R_COMPLIANCE_MODULESETS_SERVICES" : "/compliance/modulesets_services",
	"R_COMPLIANCE_RULESET_EXPORT" : "/compliance/rulesets/%1/export",
	"R_COMPLIANCE_RULESET_USAGE" : "/compliance/rulesets/%1/usage",
	"R_COMPLIANCE_RULESETS" : "/compliance/rulesets",
	"R_COMPLIANCE_RULESETS_NODES" : "/compliance/rulesets_nodes",
	"R_COMPLIANCE_RULESETS_SERVICES" : "/compliance/rulesets_services",
	"R_COMPLIANCE_RULESET_VARIABLE" : "/compliance/rulesets/%1/variables/%2",
	"R_COMPLIANCE_STATUS" : "/compliance/status",
	"R_DNS_RECORD" : "/dns/records/%1",
	"R_DNS_RECORDS" : "/dns/records",
	"R_DNS_DOMAIN" : "/dns/domains/%1",
	"R_DNS_DOMAIN_SYNC" : "/dns/domains/%1/sync",
	"R_DNS_DOMAINS" : "/dns/domains",
	"R_FILTERSETS" : "/filtersets",
	"R_FILTERSET" : "/filtersets/%1",
	"R_FORM" : "/forms/%1",
	"R_FORM_PUBLICATION" : "/forms/%1/publications/%2",
	"R_FORM_RESPONSIBLE" : "/forms/%1/responsibles/%2",
	"R_FORM_PUBLICATIONS" : "/forms/%1/publications",
	"R_FORM_RESPONSIBLES" : "/forms/%1/responsibles",
	"R_FORM_AM_I_RESPONSIBLE" : "/forms/%1/am_i_responsible",
	"R_FORMS" : "/forms",
	"R_FORMS_REVISION" : "/forms_revisions/%1",
	"R_FORMS_REVISIONS" : "/forms_revisions",
	"R_FORMS_PUBLICATIONS" : "/forms_publications",
	"R_FORMS_RESPONSIBLES" : "/forms_responsibles",
	"R_GROUPS" : "/groups",
	"R_GROUP" : "/groups/%1",
	"R_GROUP_USERS" : "/groups/%1/users",
	"R_GROUP_APPS" : "/groups/%1/apps",
	"R_GROUP_SERVICES" : "/groups/%1/services",
	"R_GROUP_HIDDEN_MENU_ENTRIES" : "/groups/%1/hidden_menu_entries",
	"R_IPS" : "/nodes/%1/ips",
	"R_NETWORK" : "/networks/%1",
	"R_NETWORKS" : "/networks",
	"R_NETWORK_SEGMENTS" : "/networks/%1/segments",
	"R_NETWORK_SEGMENT" : "/networks/%1/segments/%2",
	"R_NETWORK_SEGMENT_RESPONSIBLES" : "/networks/%1/segments/%2/responsibles",
	"R_NODE" : "/nodes/%1",
	"R_NODES" : "/nodes",
	"R_NODE_AM_I_RESPONSIBLE" : "/nodes/%1/am_i_responsible",
	"R_NODE_CANDIDATE_TAGS" : "/nodes/%1/candidate_tags",
	"R_NODE_TAGS" : "/nodes/%1/tags",
	"R_NODE_ROOT_PASSWORD" : "/nodes/%1/root_password",
	"R_NODE_SYSREPORT" : "/nodes/%1/sysreport",
	"R_NODE_SYSREPORT_TIMEDIFF" : "/nodes/%1/sysreport/timediff",
	"R_NODE_SYSREPORT_CID" : "/nodes/%1/sysreport/%2",
	"R_NODE_SYSREPORT_CID_TREE" : "/nodes/%1/sysreport/%2/tree",
	"R_NODE_SYSREPORT_CID_TREE_OID" : "/nodes/%1/sysreport/%2/tree/%3",
	"R_NODE_UUID" : "/nodes/%1/uuid",
	"R_PACKAGES_DIFF" : "/packages/diff",
	"R_PROVISIONING_TEMPLATES" : "/provisioning_templates",
	"R_PROVISIONING_TEMPLATE" : "/provisioning_templates/%1",
	"R_SCHEDULER_STATS" : "/scheduler/stats",
	"R_SEARCH" : "/search",
	"R_SERVICE" : "/services/%1",
	"R_SERVICE_AM_I_RESPONSIBLE" : "/services/%1/am_i_responsible",
	"R_SERVICES" : "/services",
	"R_SERVICES_ACTIONS" : "/services_actions",
	"R_SERVICE_ACTIONS" : "/services/%1/actions",
	"R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS" : "/services/%1/actions_unacknowledged_errors",
	"R_SERVICE_INSTANCES" : "/services_instances",
	"R_SERVICE_NODES" : "/services/%1/nodes",
	"R_SERVICE_TAGS" : "/services/%1/tags",
	"R_SERVICE_CANDIDATE_TAGS" : "/services/%1/candidate_tags",
	"R_STORE_FORMS" : "/forms_store",
	"R_STORE_FORM" : "/forms_store/%1",
	"R_SYSREPORT_TIMELINE" : "/sysreport/timeline",
	"R_SYSREPORT_NODEDIFF" : "/sysreport/nodediff",
	"R_SYSREPORT_SECURE_PATTERNS" : "/sysreport/secure_patterns",
	"R_SYSREPORT_SECURE_PATTERN" : "/sysreport/secure_patterns/%1",
	"R_SYSREPORT_AUTHORIZATIONS" : "/sysreport/authorizations",
	"R_SYSREPORT_AUTHORIZATION" : "/sysreport/authorizations/%1",
	"R_TAGS" : "/tags",
	"R_TAG_NODE" : "/tags/%1/nodes/%2",
	"R_TAG_SERVICE" : "/tags/%1/services/%2",
	"R_TAGS_NODES" : "/tags/nodes",
	"R_TAGS_SERVICES" : "/tags/services",
	"R_USERS" : "/users",
	"R_USERS_SELF" : "/users/self",
	"R_USERS_SELF_FILTERSET" : "/users/self/filterset",
	"R_USERS_SELF_FILTERSET_ONE" : "/users/self/filterset/%1",
	"R_USER_PRIMARY_GROUP" : "/users/%1/primary_group",
	"R_USER_PRIMARY_GROUP_SET" : "/users/%1/primary_group/%2",
	"R_USER" : "/users/%1",
	"R_USER_DETAILS" : "/users/%1/details",
	"R_USER_APPS_RESPONSIBLE" : "/users/%1/apps/responsible",
	"R_USER_APPS_PUBLICATION" : "/users/%1/apps/publication",
	"R_USER_FILTERSET" : "/users/%1/filterset",
	"R_USER_FILTERSET_SET" : "/users/%1/filterset/%2",
	"R_USER_GROUP" : "/users/%1/groups/%2",
	"R_USER_GROUPS" : "/users/%1/groups",
	"R_USER_HIDDEN_MENU_ENTRIES" : "/users/%1/hidden_menu_entries",
	"R_USERS_GROUPS" : "/users_groups",
	"R_WIKI" : "/wiki/%1",
	"R_WIKIS" : "/wiki",
	"R_IPS" : "/nodes/%1/ips",
	"R_ALERT_EVENT" : "/alert_event",
	"R_GET_REPORTS" : "/reports",
	"R_GET_REPORT" : "/reports/%1/definition",
	"R_GET_REPORT_METRIC" : "/reports/metrics/%1",
	"R_GET_REPORT_METRIC_SAMPLES" : "/reports/metrics/%1/samples",
	"R_GET_REPORT_CHART" : "/reports/charts/%1",
	"R_GET_REPORT_CHART_SAMPLES" : "/reports/charts/%1/samples",
	"R_LINKS" : "/links",
	"R_LINK" : "/links/%1",
	"R_TAG" : "/tags/%1",
	"R_WORKFLOW" : "/workflows/%1",
	"R_WORKFLOWS" : "/workflows"
}

function encode_uri_key(key) {
	try {
		key = key.replace("/", "(slash)")
	} catch(e) {}
	return key
}

function services_getaccessurl(service) {
	var base_path = "/"+osvc.app+"/rest/api"
	if (service.match(/^S_/)) {
		service_uri = services_access_uri[service]
		if (is_blank(service_uri)) {
			return
		}
		return "/"+osvc.app+"/" + service_uri
	} else if (service.match(/^R_/)) {
		service_uri = services_access_uri[service]
		if (is_blank(service_uri)) {
			return
		}
		return base_path + service_uri
	} else if (service.indexOf(base_path) == 0) {
		return service
	} else if (service.match(/^\//)) {
		return base_path + service
	}
}

function services_osvcputrest(service, uri, params, data, callback, error_callback, async) {
	url = services_getaccessurl(service)
	if (is_blank(url)) {
		console.log(service + " uri undefined")
		return
	}
	if (!uri) {
		uri = []
	}
	if (!params) {
		params = {}
	}
	for(var i=0; i<uri.length; i++) {
		url = url.replace("%"+(i+1), encode_uri_key(uri[i]))
	}

	var isobj=0;
	try {
		var t = Object.keys(params);
		isobj=1;
	}
	catch (e){;}

	if ((isobj==1) && (t.length > 0)) {
		url += "?"
		for (key in t) {
			url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
		}
		url = url.replace(/&$/, "");
	}
	var content_type = "application/x-www-form-urlencoded"
	if (Object.prototype.toString.call(data) === '[object Array]') {
		data = JSON.stringify(data)
		content_type = "application/json; charset=utf-8"
	}

	if (async === undefined || async == null) async=true;

	var xhr = $.ajax({
		type: "PUT",
		async: async,
		url: url,
		contentType: content_type,
		data: data,
		error: error_callback,
		success: callback
	})
	return xhr
}

function services_osvcpostrest(service, uri, params, data, callback, error_callback, async) {
	url = services_getaccessurl(service)
	if (is_blank(url)) {
		console.log(service + " uri undefined")
		return
	}
	if (!uri) {
		uri = []
	}
	if (!params) {
		params = {}
	}
	for(var i=0; i<uri.length; i++) {
		url = url.replace("%"+(i+1), encode_uri_key(uri[i]))
	}

	var isobj = 0
	try {
		var t = Object.keys(params);
		isobj = 1
	} catch (e){}

	if ((isobj==1) && (t.length > 0)) {
		url += "?"
		for (key in t) {
			url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
		}
		url = url.replace(/&$/, "");
	}
	var content_type = "application/x-www-form-urlencoded"
	var data_type = null
	try {
		data = JSON.stringify(data)
		content_type = "application/json; charset=utf-8"
		data_type = "json"
	} catch(err) {}

	if (async === undefined || async == null) async=true;

	var xhr = $.ajax({
		type: "POST",
		url: url,
		async: async,
		dataType: data_type,
		contentType: content_type,
		data: data,
		error: function(xhr, stat, error) {
			console.log(error)
			if (error == "UNAUTHORIZED") {
				app_load_href("/"+osvc.app+"/default/user/login")
			}
			if (error_callback) {
				error_callback(xhr, stat, error)
			}
		},
		success: callback
	})
	return xhr
}

function services_osvcgetrest(service, uri, params, callback, error_callback, async) {
	var url = services_getaccessurl(service)
	if (is_blank(url)) {
		console.log(service + " uri undefined")
		return
	}
	if (!uri) {
		uri = []
	}
	if (!params) {
		params = {}
	}
	for(i=0; i<uri.length; i++) {
		url = url.replace("%"+(i+1), encode_uri_key(uri[i]))
	}

	if (async === undefined || async == null) async=true;

	var xhr = $.ajax({
		type: "GET",
		url: url,
		data: params,
		async : async,
		dataType: "json",
		error: function(xhr, stat, error) {
			console.log(error)
			if (error == "UNAUTHORIZED") {
				app_load_href("/"+osvc.app+"/default/user/login")
			}
			if (error_callback) {
				error_callback(xhr, stat, error)
			}
		},
		success: callback
	})
	return xhr
}

function services_osvcdeleterest(service, uri, params, data, callback, error_callback, async) {
	url = services_getaccessurl(service)
	if (is_blank(url)) {
		console.log(service + " uri undefined")
		return
	}
	if (!uri) {
		uri = []
	}
	if (!params) {
		params = {}
	}
	for(i=0; i<uri.length; i++) {
		url = url.replace("%"+(i+1), encode_uri_key(uri[i]))
	}

	var isobj=0;
	try {
		var t = Object.keys(params);
		isobj=1;
	}
	catch (e){}

	if ((isobj==1) && (t.length > 0)) {
		url += "?"
		for (key in t) {
			url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
		}
		url = url.replace(/&$/, "");
	}

	var content_type = "application/x-www-form-urlencoded"
	if (Object.prototype.toString.call(data) === '[object Array]') {
		data = JSON.stringify(data)
		content_type = "application/json; charset=utf-8"
	}
	if (async === undefined || async == null) async=true;
	var xhr = $.ajax({
		type: "DELETE",
		async: async,
		url: url,
		contentType: content_type,
		data: data,
		error: error_callback,
		success: callback
	})
	return xhr
}

function load_user() {
	services_osvcgetrest("/users/self/dump", "", "", function(jd) {
		_self = jd.user[0]
		_groups = jd.groups
		osvc.code_rev = jd.code_rev
		osvc.server_timezone = jd.server_timezone
		osvc.client_timezone = moment.tz.guess()
		osvc.user_prefs = user_prefs(jd.prefs)
		osvc.hidden_menu_entries_stats = jd.hidden_menu_entries_stats
		osvc.filterset = jd.filterset
		osvc.user_loaded.resolve(true)
	})
}

function services_ismemberof(groups) {
	if (typeof groups === "string") {
		groups = [groups]
	}
	var result = $.grep(_groups, function(g) {
		if (groups.indexOf(g.role) < 0) {
			return false;
		}
			return true;
	})
	if (result.length > 0) {
		return true
	}
	return false
}

function services_ajax_error_fmt(xhr, stat, error) {
	var e = $("<span><span class='icon alert16 err fa-2x'></span><span data-i18n='ajax.error'></span></span>")
	e.i18n()
	var p = $("<pre></pre>")
	p.text("status: " + stat + "\nerror: " + error)
	p.css({
		"padding": "5px",
		"padding-left": "20px",
	})
	e.append(p)
	return e
}

function services_error_fmt(data) {
	if (!data.error) {
		return
	}
	var e = $("<span><span class='icon alert16 err fa-2x'></span><span data-i18n='api.error'></span></span>")
	e.i18n()
	var p = $("<pre></pre>")
	if (typeof data.error === "string") {
		p.text(data.error)
	} else {
		p.text(data.error.join("\n"))
	}
	p.css({
		"padding": "2em 0 0 0",
	})
	e.append(p)
	return e
}

function services_info_fmt(data) {
	if (!data.info) {
		return
	}
	var e = $("<span><span class='fa fa-info-circle fa-2x icon-green icon'></span><span data-i18n='api.info'></span></span>")
	e.i18n()
	var p = $("<pre></pre>")
	if (typeof data.info === "string") {
		p.text(data.info)
	} else {
		p.text(data.info.join("\n"))
	}
	p.css({
		"padding": "2em 0 0 0",
	})
	e.append(p)
	return e
}

function services_get_url() {
	return window.location.protocol +"//" + window.location.host;
}

