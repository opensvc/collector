// OpenSvc Services JS Script
// MD 09062015

// Global JS Static self
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
    "R_ACTIONS" : "rest/api/actions",
    "R_ALERT_EVENT" : "rest/api/alert_event",
    "R_API" : "rest/api",
    "R_APP_RESPONSIBLES" : "rest/api/apps/%1/responsibles",
    "R_CHECKS" : "rest/api/checks/live",
    "R_CHECKS_SETTINGS" : "rest/api/checks/settings",
    "R_CHECKS_CONTEXTUAL_SETTINGS" : "rest/api/checks/contextual_settings",
    "R_COMPLIANCE_MODULESETS" : "rest/api/compliance/modulesets",
    "R_COMPLIANCE_MODULESETS_NODES" : "rest/api/compliance/modulesets_nodes",
    "R_COMPLIANCE_MODULESETS_SERVICES" : "rest/api/compliance/modulesets_services",
    "R_COMPLIANCE_RULESET_EXPORT" : "rest/api/compliance/rulesets/%1/export",
    "R_COMPLIANCE_RULESET_USAGE" : "rest/api/compliance/rulesets/%1/usage",
    "R_COMPLIANCE_RULESETS" : "rest/api/compliance/rulesets",
    "R_COMPLIANCE_RULESETS_NODES" : "rest/api/compliance/rulesets_nodes",
    "R_COMPLIANCE_RULESETS_SERVICES" : "rest/api/compliance/rulesets_services",
    "R_COMPLIANCE_RULESET_VARIABLE" : "rest/api/compliance/rulesets/%1/variables/%2",
    "R_COMPLIANCE_STATUS" : "rest/api/compliance/status",
    "R_FILTERSETS" : "rest/api/filtersets",
    "R_FORM" : "rest/api/forms/%1",
    "R_FORM_PUBLICATIONS" : "rest/api/forms/%1/publications",
    "R_FORM_RESPONSIBLES" : "rest/api/forms/%1/responsibles",
    "R_FORMS" : "rest/api/forms",
    "R_FORMS_REVISION" : "rest/api/forms_revisions/%1",
    "R_FORMS_REVISIONS" : "rest/api/forms_revisions",
    "R_FORMS_PUBLICATIONS" : "rest/api/forms_publications",
    "R_FORMS_RESPONSIBLES" : "rest/api/forms_responsibles",
    "R_GROUPS" : "rest/api/groups",
    "R_GROUP" : "rest/api/groups/%1",
    "R_GROUP_USERS" : "rest/api/groups/%1/users",
    "R_GROUP_APPS" : "rest/api/groups/%1/apps",
    "R_GROUP_SERVICES" : "rest/api/groups/%1/services",
    "R_GROUP_HIDDEN_MENU_ENTRIES" : "rest/api/groups/%1/hidden_menu_entries",
    "R_IPS" : "rest/api/nodes/%1/ips",
    "R_NETWORK" : "rest/api/networks/%1",
    "R_NETWORKS" : "rest/api/networks",
    "R_NETWORK_SEGMENTS" : "rest/api/networks/%1/segments",
    "R_NETWORK_SEGMENT" : "rest/api/networks/%1/segments/%2",
    "R_NETWORK_SEGMENT_RESPONSIBLES" : "rest/api/networks/%1/segments/%2/responsibles",
    "R_NODE" : "rest/api/nodes/%1",
    "R_NODES" : "rest/api/nodes",
    "R_NODE_AM_I_RESPONSIBLE" : "rest/api/nodes/%1/am_i_responsible",
    "R_NODE_CANDIDATE_TAGS" : "rest/api/nodes/%1/candidate_tags",
    "R_NODE_TAGS" : "rest/api/nodes/%1/tags",
    "R_NODE_ROOT_PASSWORD" : "rest/api/nodes/%1/root_password",
    "R_NODE_SYSREPORT" : "rest/api/nodes/%1/sysreport",
    "R_NODE_SYSREPORT_TIMEDIFF" : "rest/api/nodes/%1/sysreport/timediff",
    "R_NODE_SYSREPORT_CID" : "rest/api/nodes/%1/sysreport/%2",
    "R_NODE_SYSREPORT_CID_TREE" : "rest/api/nodes/%1/sysreport/%2/tree",
    "R_NODE_SYSREPORT_CID_TREE_OID" : "rest/api/nodes/%1/sysreport/%2/tree/%3",
    "R_NODE_UUID" : "rest/api/nodes/%1/uuid",
    "R_PACKAGES_DIFF" : "rest/api/packages/diff",
    "R_PROVISIONING_TEMPLATES" : "rest/api/provisioning_templates",
    "R_PROVISIONING_TEMPLATE" : "rest/api/provisioning_templates/%1",
    "R_SCHEDULER_STATS" : "rest/api/scheduler/stats",
    "R_SEARCH" : "rest/api/search",
    "R_SERVICE" : "rest/api/services/%1",
    "R_SERVICE_AM_I_RESPONSIBLE" : "rest/api/services/%1/am_i_responsible",
    "R_SERVICES" : "rest/api/services",
    "R_SERVICES_ACTIONS" : "rest/api/services_actions",
    "R_SERVICE_ACTIONS" : "rest/api/services/%1/actions",
    "R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS" : "rest/api/services/%1/actions_unacknowledged_errors",
    "R_SERVICE_INSTANCES" : "rest/api/service_instances",
    "R_SERVICE_NODES" : "rest/api/services/%1/nodes",
    "R_SERVICE_TAGS" : "rest/api/services/%1/tags",
    "R_SERVICE_CANDIDATE_TAGS" : "rest/api/services/%1/candidate_tags",
    "R_STORE_FORMS" : "rest/api/forms_store",
    "R_STORE_FORM" : "rest/api/forms_store/%1",
    "R_SYSREPORT_TIMELINE" : "rest/api/sysreport/timeline",
    "R_SYSREPORT_NODEDIFF" : "rest/api/sysreport/nodediff",
    "R_SYSREPORT_SECURE_PATTERNS" : "rest/api/sysreport/secure_patterns",
    "R_SYSREPORT_SECURE_PATTERN" : "rest/api/sysreport/secure_patterns/%1",
    "R_SYSREPORT_AUTHORIZATIONS" : "rest/api/sysreport/authorizations",
    "R_SYSREPORT_AUTHORIZATION" : "rest/api/sysreport/authorizations/%1",
    "R_TAGS" : "rest/api/tags",
    "R_TAG_NODE" : "rest/api/tags/%1/nodes/%2",
    "R_TAG_SERVICE" : "rest/api/tags/%1/services/%2",
    "R_TAGS_NODES" : "rest/api/tags/nodes",
    "R_TAGS_SERVICES" : "rest/api/tags/services",
    "R_USERS" : "rest/api/users",
    "R_USERS_SELF" : "rest/api/users/self",
    "R_USERS_SELF_FILTERSET" : "rest/api/users/self/filterset",
    "R_USERS_SELF_FILTERSET_ONE" : "rest/api/users/self/filterset/%1",
    "R_USERS_SELF_TABLE_SETTINGS" : "rest/api/users/self/table_settings",
    "R_USERS_SELF_TABLE_FILTERS" : "rest/api/users/self/table_filters",
    "R_USERS_SELF_TABLE_FILTERS_LOAD_BOOKMARK" : "rest/api/users/self/table_filters/load_bookmark",
    "R_USERS_SELF_TABLE_FILTERS_SAVE_BOOKMARK" : "rest/api/users/self/table_filters/save_bookmark",
    "R_USER_PRIMARY_GROUP" : "rest/api/users/%1/primary_group",
    "R_USER_PRIMARY_GROUP_SET" : "rest/api/users/%1/primary_group/%2",
    "R_USER" : "rest/api/users/%1",
    "R_USER_DETAILS" : "rest/api/users/%1/details",
    "R_USER_DOMAINS" : "rest/api/users/%1/domains",
    "R_USER_APPS" : "rest/api/users/%1/apps",
    "R_USER_FILTERSET" : "rest/api/users/%1/filterset",
    "R_USER_FILTERSET_SET" : "rest/api/users/%1/filterset/%2",
    "R_USER_GROUP" : "rest/api/users/%1/groups/%2",
    "R_USER_GROUPS" : "rest/api/users/%1/groups",
    "R_USER_HIDDEN_MENU_ENTRIES" : "rest/api/users/%1/hidden_menu_entries",
    "R_USERS_GROUPS" : "rest/api/users_groups",
    "R_WIKI" : "rest/api/wiki/%1",
    "R_WIKIS" : "rest/api/wiki",
    "R_IPS" : "rest/api/nodes/%1/ips",
    "R_ALERT_EVENT" : "rest/api/alert_event",
    "R_GET_REPORTS" : "rest/api/reports",
    "R_GET_REPORT" : "rest/api/reports/%1",
    "R_GET_REPORT_METRIC" : "rest/api/reports/metrics/%1",
    "R_GET_REPORT_METRIC_SAMPLES" : "rest/api/reports/metrics/%1/samples",
    "R_GET_REPORT_CHART" : "rest/api/reports/charts/%1",
    "R_GET_REPORT_CHART_SAMPLES" : "rest/api/reports/charts/%1/samples",
    "R_LINKS" : "rest/api/links",
    "R_LINK" : "rest/api/links/%1",
    "R_TAG" : "rest/api/tags/%1",
    "R_WORKFLOW" : "rest/api/workflows/%1",
    "R_WORKFLOWS" : "rest/api/workflows"
}

function services_getaccessurl(service)
{
    base_path = "/init/"
    service_uri = services_access_uri[service]
    if (is_blank(service_uri))
    {
        return
    }
    base_path +=service_uri
    return base_path
}

function services_osvcputrest(service, uri, params, data, callback, error_callback)
{
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
        url = url.replace("%"+(i+1), uri[i])
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
      content_type = "application/json"
    }
    var xhr = $.ajax(
    {
        type: "PUT",
        url: url,
        contentType: content_type,
        data: data,
        error: error_callback,
        success: callback
    })
    return xhr
}

function services_osvcpostrest(service, uri, params, data, callback, error_callback)
{
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
        url = url.replace("%"+(i+1), uri[i])
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
      content_type = "application/json"
    }
    var xhr = $.ajax(
    {
        type: "POST",
        url: url,
        contentType: content_type,
        data: data,
        error: function(xhr, stat, error) {
          console.log(error)
          if (error == "UNAUTHORIZED") {
            app_load_href("/init/default/user/login")
          }
          if (error_callback) {
            error_callback(xhr, stat, error)
	  }
        },
        success: callback
    })
    return xhr
}

function services_osvcgetrest(service, uri, params, callback, error_callback, async)
{
    if (service.match(/^\/init\/rest/)) {
      var url = service
    } else {
      var url = services_getaccessurl(service)
    }
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
        url = url.replace("%"+(i+1), uri[i])
    }

    if (async === undefined || async == null) async=true;
    
    var xhr = $.ajax(
    {
        type: "GET",
        url: url,
        data: params,
        async : async,
        dataType: "json",
        error: function(xhr, stat, error) {
          console.log(error)
          if (error == "UNAUTHORIZED") {
            app_load_href("/init/default/user/login")
          }
          if (error_callback) {
            error_callback(xhr, stat, error)
	  }
        },
        success: callback,
    });
    return xhr
}

function services_osvcdeleterest(service, uri, params, data, callback, error_callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url))
    {
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
        url = url.replace("%"+(i+1), uri[i])
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
      content_type = "application/json"
    }
    var xhr = $.ajax(
    {
        type: "DELETE",
        url: url,
        contentType: content_type,
        data: data,
        error: error_callback,
        success: callback,
    });
    return xhr
}

function services_feed_self_and_group() {
    services_osvcgetrest("R_USERS_SELF", "", "", function(dataself) {
        _self = dataself.data[0]
        services_osvcgetrest("R_USER_GROUPS", [_self.id], {"meta": "false", "limit": "0"}, function(datagroup) {
            _groups = datagroup.data;
            osvc.user_groups_loaded.resolve(true)
        })
    })
}

function waitfor(test, expectedValue, msec, count, callback) {
    while (test() !== expectedValue) {
        count++;
        setTimeout(function() {
            return waitfor(test, expectedValue, msec, count, callback);
        }, msec);
        return;
    }
    callback();
}

function services_ismemberof(groups)
{
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
    var e = $("<span><span class='alert16 err fa-2x'></span><span data-i18n='ajax.error'></span></span>")
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
    var e = $("<span><span class='alert16 err fa-2x'></span><span data-i18n='api.error'></span></span>")
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
    var e = $("<span><span class='alert16 fa-2x'></span><span data-i18n='api.info'></span></span>")
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

function services_get_url()
{
    return window.location.protocol +"//" + window.location.host;
}

