// OpenSvc Services JS Script
// MD 09062015

var services_access_uri = {
    "S_SYSREP" : "ajax_sysreport/ajax_sysrep",
    "S_SYSREPDIFF" : "ajax_sysreport/ajax_sysrepdiff",
    "S_SYSREPCOMMIT" : "ajax_sysreport/ajax_sysreport_commit",
    "S_SYSREPADMIN" : "ajax_sysreport/ajax_sysreport_admin",
    "S_SYSREPSHOWFILE" : "ajax_sysreport/ajax_sysreport_show_file"
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

function services_osvcpost(service,data,callback)
{
    url = services_getaccessurl(service)
    if (is_blank(service_uri))
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
