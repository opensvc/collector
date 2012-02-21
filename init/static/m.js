function format_filters(d) {
        fset_id = d[0]
        s = ""
	if (fset_id == 0) {
		selected = "selected"
	} else {
		selected = ""
	}
	s += "<option value=0 "+selected+">none</option>"
        for (id in d[1]) {
                data = d[1][id]
                if (data['id'] == fset_id) {
                        selected = "selected"
                } else {
                        selected = ""
                }
                s += "<option value="+data['id']+" "+selected+">"+data['fset_name']+"</option>"
        }
        return s
}

function init_filters(event, data) {
        $.getJSON("{{=URL(r=request, f='call/json/json_filters')}}", function(data) {
                e = format_filters(data)
                $("#filters").append(e).selectmenu('refresh')
        });
        $('#filters').change('select', select_filter)
}

function select_filter(event, data) {
        $.getJSON("{{=URL(r=request, f='call/json/json_set_filter')}}/"+$(this).attr('value'), function(data) {
		location.reload()
        });
}

function format_service(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li><a rel='external' href='{{=URL(r=request, f='svc')}}/"+data[i]+"'>" + data[i] + "</a></li>"
	}
        return s
}

function format_node(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li><a rel='external' href='{{=URL(r=request, f='node')}}/"+data[i]+"'>" + data[i] + "</a></li>"
	}
        return s
}

function format_alert(d) {
        s =  "<div style='display:table;width:100%'>"
        s +=  "<div style='display:table-row'>"
        s +=  "<div class='sev sev"+d['dash_severity']+"'>&nbsp;</div>"
        s +=  "<div style='display:table-cell;padding-left:1em;vertical-align:middle'>"
        s +=   "<div class='ui-li-aside ui-li-desc'>"+d['dash_created']+"</div>"
        s +=   "<div>"+d['dash_type']+"</div>"
        s +=   "<div>"+d['body']+"</div>"
        if (d['dash_svcname'].length > 0 || d['dash_nodename'].length > 0) {
                s += "<div data-type='vertical' data-role='controlgroup'>"
                if (d['dash_svcname'].length > 0) {
                        s += "<a rel='external' href='{{=URL(r=request, f='svc')}}/"+d['dash_svcname']+"' data-role='button'>"+d['dash_svcname']+"</a>"
                }
                if (d['dash_nodename'].length > 0) {
                        s += "<a rel='external' href='{{=URL(r=request, f='node')}}/"+d['dash_nodename']+"' data-role='button'>"+d['dash_nodename']+"</a>"
                }
                s += "</div>"
        }
        s +=  "</div>"
        s += "</div>"
        s += "</div>"
        return s
}

function format_alerts(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li>" + format_alert(data[i]) + "</li>"
	}
	return s
}

action_img_h = {
    'checks': 'check16.png',
    'pushservices': 'svc.png',
    'pushpkg': 'pkg16.png',
    'pushpatch': 'pkg16.png',
    'reboot': 'action_restart_16.png',
    'shutdown': 'action_stop_16.png',
    'syncservices': 'action_sync_16.png',
    'updateservices': 'action16.png',
    'stop': 'action_stop_16.png',
    'stopapp': 'action_stop_16.png',
    'stopdisk': 'action_stop_16.png',
    'stoploop': 'action_stop_16.png',
    'stopip': 'action_stop_16.png',
    'umount': 'action_stop_16.png',
    'shutdown': 'action_stop_16.png',
    'boot': 'action_start_16.png',
    'start': 'action_start_16.png',
    'startstandby': 'action_start_16.png',
    'startapp': 'action_start_16.png',
    'startdisk': 'action_start_16.png',
    'startloop': 'action_start_16.png',
    'startip': 'action_start_16.png',
    'mount': 'action_start_16.png',
    'restart': 'action_restart_16.png',
    'provision': 'prov.png',
    'switch': 'action_restart_16.png',
    'freeze': 'frozen16.png',
    'thaw': 'frozen16.png',
    'syncall': 'action_sync_16.png',
    'syncnodes': 'action_sync_16.png',
    'syncdrp': 'action_sync_16.png',
    'syncfullsync': 'action_sync_16.png',
    'postsync': 'action_sync_16.png',
    'push': 'log16.png',
    'check': 'check16.png',
    'fixable': 'fixable16.png',
    'fix': 'comp16.png',
    'pushstats': 'spark16.png',
    'pushasset': 'node16.png',
    'stopcontainer': 'action_stop_16.png',
    'startcontainer': 'action_start_16.png',
    'stopapp': 'action_stop_16.png',
    'startapp': 'action_start_16.png',
    'prstop': 'action_stop_16.png',
    'prstart': 'action_start_16.png',
    'push': 'svc.png',
    'syncquiesce': 'action_sync_16.png',
    'syncresync': 'action_sync_16.png',
    'syncupdate': 'action_sync_16.png',
    'syncverify': 'action_sync_16.png',
    'toc': 'action_toc_16.png',
    'stonith': 'action_stonith_16.png',
    'switch': 'action_switch_16.png'
}

function format_action(d) {
	url = "{{=URL(r=request, c='static', f='foo')}}"
        s =  "<div style='display:table;width:100%'>"
        s +=  "<div style='display:table-row'>"
        s +=   "<div class='sev sev"+d['status']+"'>&nbsp;</div>"
        s +=   "<div style='display:table-cell;padding-left:1em;vertical-align:middle'>"
        s +=    "<div class='ui-li-aside ui-li-desc'>"+d['begin']+"</div>"
        s +=    "<div>pid: "+d['pid']+"</div>"
	if (d['ack'] == 1) {
		s += "<div>Acked by: "+d['acked_by']+"</div>"
		s += "<div>Acked on: "+d['acked_date']+"</div>"
		s += "<div>Comment:</div>"
		s += "<div>"+d['acked_comment']+"</div>"
	}
        s +=    "<div data-type='vertical' data-role='controlgroup'>"
        s +=     "<a data-role='button' rel='external' data-rel='dialog' href={{=URL(r=request, f='show_action')}}/"+d['id']+">"
        s +=      "<img width='12px' src='"+url.replace("foo", action_img_h[d['action']])+"'>"
        if (d['cron'] == 1) {
		s += "<img width='12px' style='padding-left:6px' src='{{=URL(r=request, c='static', f='time16.png')}}'>"
	}
        s +=      "<span style='padding-left:6px'>"+d['action']+"</span>"
	s +=     "</a>"
	s +=     "<a rel='external' href='{{=URL(r=request, f='svc')}}/"+d['svcname']+"' data-role='button'>"+d['svcname']+"</a>"
	s +=     "<a rel='external' href='{{=URL(r=request, f='node')}}/"+d['hostname']+"' data-role='button'>"+d['hostname']+"</a>"
	s +=    "</div>"
	s +=   "</div>"
        s +=  "</div>"
        s += "</div>"
        return s
}

function format_actions(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li>" + format_action(data[i]) + "</li>"
	}
	return s
}

function format_show_action(d) {
        s =  "<div style='display:table;width:100%'>"
        s +=  "<div style='display:table-row'>"
        s +=   "<div class='sev sev"+d['status']+"'>&nbsp;</div>"
        s +=   "<div style='display:table-cell;padding-left:1em;vertical-align:middle'>"
        s +=    "<div class='ui-li-aside ui-li-desc'>"
        s +=     "<div><strong>"+d['hostname']+"."+d['svcname']+"."+d['action']+"</strong></div>"
        s +=     "<div>"+d['begin']+"</div>"
        s +=    "</div>"
        s +=   "<div>&nbsp;</div>"
        s +=   "<code>"+d['status_log'].replace(/\n/g, "<br\>")+"</code>"
        s +=  "</div>"
        s += "</div>"
        return s
}

function format_show_actions(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li>" + format_show_action(data[i]) + "</li>"
	}
	return s
}

function format_compliance_li(d) {
        s =  ""
        s += "<div style='display:table;width:100%'>"
        s +=  "<div style='display:table-row'>"
        s +=   "<div class='sev comp_status_"+d['run_status']+"'>&nbsp;</div>"
        s +=   "<div style='display:table-cell;padding-left:1em;vertical-align:middle'>"
        s +=    "<div class='ui-li-aside ui-li-desc'>"
        s +=     "<div>"+d['run_date']+"</div>"
        s +=    "</div>"
        s +=   "<strong>"+d['run_module']+"</strong>"
        s +=  "</div>"
        s += "</div>"
        return s
}

function format_compliance(data) {
	s = ""
	for (i=0; i<data.length; i++) {
		s += "<li>" + format_compliance_li(data[i]) + "</li>"
	}
	return s
}

