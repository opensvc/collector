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
    "R_GETSYSREP" : "rest/api/sysreport/timeline",
    "R_GETSYSREPNODEDIFF" : "rest/api/sysreport/nodediff",
    "R_GETNODESSYS" : "rest/api/nodes/%1/sysreport",
    "R_GETNODESSYSREPTIMEDIFF" : "rest/api/nodes/%1/sysreport/timediff",
    "R_GETNODESSYSCID" : "rest/api/nodes/%1/sysreport/%2",
    "R_GETNODESSYSCIDTREE" : "rest/api/nodes/%1/sysreport/%2/tree",
    "R_GETNODESSYSCIDOID" : "rest/api/nodes/%1/sysreport/%2/tree/%3",
    "R_GETSYSREPSECPAT" : "rest/api/sysreport/secure_patterns",
    "R_POSTSYSREPSECPAT" : "rest/api/sysreport/secure_patterns",
    "R_DELSYSREPSECPAT" : "rest/api/sysreport/secure_patterns/%1",
    "R_GETSYSREPADMINALLOW" : "rest/api/sysreport/authorizations",
    "R_POSTSYSREPADMINALLOW" : "rest/api/sysreport/authorizations",
    "R_DELSYSREPADMINALLOW" : "rest/api/sysreport/authorizations/%1",
    "G_GETFILTERSET" : "rest/api/filtersets",
    "G_GETUSERSELF" : "/rest/api/users/self",
    "G_GETUSERSGROUPS" : "/rest/api/groups",
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

function services_osvcpost(service, data, callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url))
    {
        console.log(service + " uri undefined")
        return
    }
    var req = $.ajax(
    {
        type: "POST",
        url: url,
        data: data,
        success: callback
    })
}

function services_osvcgetrest(service, uri, params, callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url)) {
        console.log(service + " uri undefined")
        return
    }
    for(i=0;i<uri.length;i++) {
        url = url.replace("%"+(i+1), uri[i])
    }
    if (Object.keys(params).length > 0) {
        url += "?"
        for (key in params) {
            url += encodeURIComponent(key) + "=" + encodeURIComponent(params[key]) + "&";
        }
        url = url.replace(/&$/, "");
    }
    var req = $.getJSON(url, callback)
}

function services_osvcpostrest(service, param, callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url))
    {
        console.log(service + " uri undefined")
        return
    }
    var req = $.post(url,param)
    .done( callback )
    .fail( function(xhr, textStatus, errorThrown) {
        callback(xhr.responseText);
    });
}

function services_osvcdeleterest(service, param, callback)
{
    url = services_getaccessurl(service)
    if (is_blank(url))
    {
        console.log(service + " uri undefined")
        return
    }
    for(i=0;i<param.length;i++)
        url = url.replace("%"+(i+1),param[i])
    var req = $.ajax(
    {
        type: "DELETE",
        url: url,
        success: callback
    });
}

function services_feed_self_and_group()
{
    services_osvcgetrest("G_GETUSERSELF", "", "", function(dataself)
    {
        _self = dataself.data[0];
        services_osvcgetrest("G_GETUSERSGROUPS", "", {"meta": "false", "limit": "0"}, function(datagroup)
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

function services_ismemberof(group, callback)
{
    return waitfor(function(){return (_groups.length > 0)}, true, 500, 20, function() {
        var result = $.grep(_groups, function(g) {
            return g.role === group;
        });
        if (result.length > 0) {
            callback();
        }
    });
}
