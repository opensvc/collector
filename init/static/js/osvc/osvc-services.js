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
    "R_ALERT_EVENT" : "rest/api/alert_event",
    "R_APP_RESPONSIBLES" : "rest/api/apps/%1/responsibles",
    "R_FILTERSETS" : "rest/api/filtersets",
    "R_GROUPS" : "rest/api/groups",
    "R_IPS" : "rest/api/nodes/%1/ips",
    "R_NODE" : "rest/api/nodes/%1",
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
    "R_SEARCH" : "rest/api/search",
    "R_SERVICE" : "rest/api/services/%1",
    "R_SERVICE_AM_I_RESPONSIBLE" : "rest/api/services/%1/am_i_responsible",
    "R_SERVICES" : "rest/api/services",
    "R_SERVICE_ACTIONS" : "rest/api/services/%1/actions",
    "R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS" : "rest/api/services/%1/actions_unacknowledged_errors",
    "R_SERVICE_INSTANCES" : "rest/api/service_instances",
    "R_SERVICE_NODES" : "rest/api/services/%1/nodes",
    "R_SERVICE_TAGS" : "rest/api/services/%1/tags",
    "R_SERVICE_CANDIDATE_TAGS" : "rest/api/services/%1/candidate_tags",
    "R_SYSREPORT_TIMELINE" : "rest/api/sysreport/timeline",
    "R_SYSREPORT_NODEDIFF" : "rest/api/sysreport/nodediff",
    "R_SYSREPORT_SECURE_PATTERNS" : "rest/api/sysreport/secure_patterns",
    "R_SYSREPORT_SECURE_PATTERN" : "rest/api/sysreport/secure_patterns/%1",
    "R_SYSREPORT_AUTHORIZATIONS" : "rest/api/sysreport/authorizations",
    "R_SYSREPORT_AUTHORIZATION" : "rest/api/sysreport/authorizations/%1",
    "R_TAGS" : "rest/api/tags",
    "R_TAG_NODE" : "rest/api/tags/%1/nodes/%2",
    "R_TAG_SERVICE" : "rest/api/tags/%1/services/%2",
    "R_USERS_SELF" : "rest/api/users/self",
    "R_USERS_SELF_FILTERSET" : "rest/api/users/self/filterset",
    "R_USERS_SELF_FILTERSET_ONE" : "rest/api/users/self/filterset/%1",
    "R_USERS_SELF_TABLE_SETTINGS" : "rest/api/users/self/table_settings",
    "R_USERS_SELF_TABLE_FILTERS" : "rest/api/users/self/table_filters",
    "R_USERS_SELF_TABLE_FILTERS_LOAD_BOOKMARK" : "rest/api/users/self/table_filters/load_bookmark",
    "R_USERS_SELF_TABLE_FILTERS_SAVE_BOOKMARK" : "rest/api/users/self/table_filters/save_bookmark",
    "R_USER" : "rest/api/users/%1",
    "R_USER_DOMAINS" : "rest/api/users/%1/domains",
    "R_USER_APPS" : "rest/api/users/%1/apps",
    "R_USER_GROUPS" : "rest/api/users/%1/groups",
    "R_WIKI" : "rest/api/wiki/%1",
    "R_WIKIS" : "rest/api/wiki",
    "R_LINKS" : "rest/api/links",
    "R_LINK" : "rest/api/links/%1"
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

function services_osvcpostrest(service, uri, params, data, callback, error_callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url)) {
        console.log(service + " uri undefined")
        return
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
    var req = $.ajax(
    {
        type: "POST",
        url: url,
        contentType: content_type,
        data: data,
        error: error_callback,
        success: callback
    })
}

function services_osvcgetrest(service, uri, params, callback, error_callback, async)
{
    url = services_getaccessurl(service)
    if (is_blank(url)) {
        console.log(service + " uri undefined")
        return
    }
    for(i=0; i<uri.length; i++) {
        url = url.replace("%"+(i+1), uri[i])
    }

    if (async === undefined || async == null) async=true;
    
    var req = $.ajax(
    {
        type: "GET",
        url: url,
        data: params,
        async : async,
        dataType: "json",
        error: error_callback,
        success: callback,
    });

}

function services_osvcdeleterest(service, uri, params, data, callback, error_callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url))
    {
        console.log(service + " uri undefined")
        return
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
    var req = $.ajax(
    {
        type: "DELETE",
        url: url,
        contentType: content_type,
        data: data,
        error: error_callback,
        success: callback,
    });
}

function services_feed_self_and_group()
{
    services_osvcgetrest("R_USERS_SELF", "", "", function(dataself)
    {
        _self = dataself.data[0];
        services_osvcgetrest("R_USER_GROUPS", [_self.id], {"meta": "false", "limit": "0"}, function(datagroup)
        {
            _groups = datagroup.data;
        }, null, false);
    }, null, false);
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

function services_ismemberof(groups, callback)
{
    if (typeof groups === "string") {
      groups = [groups]
    }
    return waitfor(function(){return (_groups.length > 0)}, true, 500, 20, function() {
        var result = $.grep(_groups, function(g) {
            if (groups.indexOf(g.role) < 0) {
                return false;
            }
            return true;
        });
        if (result.length > 0) {
            callback();
        }
    });
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
    var e = $("<span><span class='alert16 err fa-2x'></span><span data-i18n='api.error'></span></span>")
    e.i18n()
    var p = $("<pre></pre>")
    p.text(data.error)
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
