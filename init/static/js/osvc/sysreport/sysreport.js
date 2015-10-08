// SysReport JS Script
// MD 08062015

function sysreport_onchangeBeginEndDate(event,nodes)
{
    url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysrep"
    dest = $("[name=sysrep_top]")
    if (is_enter(event))
    {
        $.ajax(
        {
            type: "POST",
            url: url,
            data: 
            {
                nodes: nodes,
                end: dest.find("[name=end]").val(),
                begin: dest.find("[name=begin]").val(),
                path: dest.find("[name=filter]").val()
            },
            success: function(msg)
            {
                dest.html(msg)
            }
        })
    }
}

function show_dateTimePicker(item)
{
    $(item).toggle();
    $(item).siblings().toggle().children("input").focus();
    $(item).datetimepicker({dateFormat: "yy-mm-dd"});
}
