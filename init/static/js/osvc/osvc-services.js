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
    "R_APP_RESPONSIBLES" : "rest/api/apps/%1/responsibles",
    "R_SEARCH" : "rest/api/search",
    "R_SYSREPORT_TIMELINE" : "rest/api/sysreport/timeline",
    "R_SYSREPORT_NODEDIFF" : "rest/api/sysreport/nodediff",
    "R_NODE" : "rest/api/nodes/%1",
    "R_NODE_UUID" : "rest/api/nodes/%1/uuid",
    "R_NODE_ROOT_PASSWORD" : "rest/api/nodes/%1/root_password",
    "R_NODE_SYSREPORT" : "rest/api/nodes/%1/sysreport",
    "R_NODE_SYSREPORT_TIMEDIFF" : "rest/api/nodes/%1/sysreport/timediff",
    "R_NODE_SYSREPORT_CID" : "rest/api/nodes/%1/sysreport/%2",
    "R_NODE_SYSREPORT_CID_TREE" : "rest/api/nodes/%1/sysreport/%2/tree",
    "R_NODE_SYSREPORT_CID_TREE_OID" : "rest/api/nodes/%1/sysreport/%2/tree/%3",
    "R_PACKAGES_DIFF" : "rest/api/packages/diff",
    "R_SYSREPORT_SECURE_PATTERNS" : "rest/api/sysreport/secure_patterns",
    "R_SYSREPORT_SECURE_PATTERN" : "rest/api/sysreport/secure_patterns/%1",
    "R_SYSREPORT_AUTHORIZATIONS" : "rest/api/sysreport/authorizations",
    "R_SYSREPORT_AUTHORIZATION" : "rest/api/sysreport/authorizations/%1",
    "R_FILTERSETS" : "rest/api/filtersets",
    "R_USERS_SELF" : "/rest/api/users/self",
    "R_USER_APPS" : "/rest/api/users/%1/apps",
    "R_USER_GROUPS" : "/rest/api/users/%1/groups",
    "R_GROUPS" : "/rest/api/groups",
    "R_NODE_TAGS" : "/rest/api/nodes/%1/tags",
    "R_NODE_CANDIDATE_TAGS" : "/rest/api/nodes/%1/candidate_tags",
    "R_SERVICE" : "/rest/api/services/%1",
    "R_SERVICES" : "/rest/api/services",
    "R_SERVICE_ACTIONS" : "/rest/api/services/%1/actions",
    "R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS" : "/rest/api/services/%1/actions_unacknowledged_errors",
    "R_SERVICE_INSTANCES" : "/rest/api/service_instances",
    "R_SERVICE_NODES" : "/rest/api/services/%1/nodes",
    "R_SERVICE_TAGS" : "/rest/api/services/%1/tags",
    "R_SERVICE_CANDIDATE_TAGS" : "/rest/api/services/%1/candidate_tags",
    "R_TAGS" : "/rest/api/tags",
    "R_TAG_NODE" : "/rest/api/tags/%1/nodes/%2",
    "R_TAG_SERVICE" : "/rest/api/tags/%1/services/%2",
    "R_WIKI" : "rest/api/wiki/%1",
    "R_WIKIS" : "rest/api/wiki",
    "R_IPS" : "rest/api/nodes/%1/ips",
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
    if (Object.keys(params).length > 0) {
        url += "?"
        for (key in params) {
            url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
        }
        url = url.replace(/&$/, "");
    }
    var req = $.ajax(
    {
        type: "POST",
        url: url,
        data: data,
        error: error_callback,
        success: callback
    })
}

function services_encodes_json_param(params)
{
    var url="";
    if (params.length >0)
    {
        for (i=0;i<params.length;i++)
        {
            for (key in params[i]) {
                        url += encodeURIComponent(key) + "=" + encodeURIComponent(params[i][key]) + "&";
                    }
        }
        url = url.replace(/&$/, "");
    }
    else if (Object.keys(params).length > 0) {
        for (key in params) {
            url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
        }
        url = url.replace(/&$/, "");
    }
    return url;
}

function services_osvcgetrest(service, uri, params, callback, error_callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url)) {
        console.log(service + " uri undefined")
        return
    }
    for(i=0; i<uri.length; i++) {
        url = url.replace("%"+(i+1), uri[i])
    }
    
    var parameters = services_encodes_json_param(params);
    if (parameters != "")
        url += "?" + parameters;

    var req = $.ajax(
    {
        type: "GET",
        url: url,
        dataType: "json",
        error: error_callback,
        success: callback,
    });

}

function services_osvcdeleterest(service, uri, callback, error_callback)
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
    var req = $.ajax(
    {
        type: "DELETE",
        url: url,
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
        });
    });
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
    e = $("<span class='alert16'></span>")
    e.text(i18n.t("ajax.error"))
    p = $("<pre></pre>")
    p.text("status: " + stat + "\nerror: " + error)
    p.css({
      "padding": "5px",
      "padding-left": "20px",
    })
    e.append(p)
    return e
}

function services_error_fmt(data) {
    e = $("<span class='alert16'></span>")
    e.text(i18n.t("api.error"))
    p = $("<pre></pre>")
    p.text(data.error)
    p.css({
      "padding": "5px",
      "padding-left": "20px",
    })
    e.append(p)
    return e
}

