// IE indexOf workaround
if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function(obj, start) {
    for (var i = (start || 0), j = this.length; i < j; i++) {
      if (this[i] === obj) { return i; }
    }
    return -1;
  }
}

//
// websockets
//
var wsh = {}
var last_events = []

function ws_duplicate_event(uid) {
    if (last_events.indexOf(uid) >= 0) {
        return true
    }
    last_events.push(uid)
    if (last_events.length > 10) {
        last_events = last_events.slice(0, 10)
    }
    return false
}

function ws_switch(e) {
    try {
        data = eval('('+e.data+')')
    } catch(ex) {
        return
    }
    if (ws_duplicate_event(data['uuid'])) {
        return
    }
    data = data['data']
    for (i=0; i<data.length; i++) {
        ws_switch_one(data[i])
    }
}

function ws_switch_one(data) {
    if (!("event" in data)) {
        return
    }
    for (key in wsh) {
        if (!$("#wsswitch_"+key).prop('checked')) {
            // websocket disable for this table
            return
        }
        ws_action_switch = wsh[key]
        ws_action_switch(data)
    }
}

web2py_websocket("wss://"+window.location.hostname+"/realtime/generic", ws_switch)

function print_date(d) {
  var day = d.getDate()
  var month = d.getMonth()+1
  var year = d.getFullYear()
  var hours = d.getHours()
  var minutes = d.getMinutes()
  if (month<10) { month = "0"+month }
  if (day<10) { day = "0"+day }
  if (hours<10) { hours = "0"+hours }
  if (minutes<10) { minutes = "0"+minutes }
  var ds = year+"-"+month+"-"+day+" "+hours+":"+minutes
  return ds
}

function values_to_filter(iid, did){
	l = []
	var reg = new RegExp("[ ]+$", "g");
	$("#"+did).contents().find("a").each(function(){
                s = this.text
      		s = s.replace(reg, "")
		if (s == "None") {s = "empty"}
		l.push(s)
	})
        v = '(' + l.join(",") + ')'
	$("#"+iid).val(v)
}
function invert_filter(did){
	var v = $('#'+did).val()
	var reg = new RegExp("[|]+", "g");
	var l = v.split(reg);
        if (l.length > 1) {
		for (var i=0; i<l.length; i++) {
			if (l[i][0] == '!') {
				l[i] = l[i].substr(1)
			} else {
				l[i] = '!'+l[i]
			}
		}
		v = l.join("&")
		$('#'+did).val(v)
		return
	} else {
		var reg = new RegExp("[&]+", "g");
		var l = v.split(reg);
		for (var i=0; i<l.length; i++) {
			if (l[i][0] == '!') {
				l[i] = l[i].substr(1)
			} else {
				l[i] = '!'+l[i]
			}
		}
		v = l.join("|")
		$('#'+did).val(v)
		return
	}
}
function toggle_vis(name){
	_toggle_vis(name,'table-row')
}

function toggle_vis_block(name){
	_toggle_vis(name,'block')
}

function _toggle_vis(name, mode){
	$("[name="+name+"]").each(function(){
		if ($(this).is(":visible")) {
			$(this).hide()
		} else {
			$(this).show()
			$(this).children("select").combobox()
		}
	})
}

function checkEnter(e) {
  submit_form_on_enter(e, document.svcform)
}

function submit_form_on_enter(e, form) {
  var characterCode
  if(e && e.which) {
    e = e
    characterCode = e.which
  }else{
//    e = event
    characterCode = e.keyCode
  }
  if(characterCode == 13) {
    form.submit()
    return false
  }else{
    return true
  }
}

function is_enter(e) {
  var characterCode
  if(e && e.which) {
    e = e
    characterCode = e.which
  }else{
    characterCode = e.keyCode
  }
  if(characterCode == 13) {
    return true
  }else{
    return false
  }
}

function select_all(checked, aform) {
  var elem = aform.elements;
  for(var i = 0; i < elem.length; i++) {
    if (elem[i].type == 'checkbox' && elem[i].disabled == false && elem[i].name.match(/^check_/)) {
      elem[i].checked = checked
    }
  }
}

function dumpProps(obj, parent) {
   // Go through all the properties of the passed-in object
   for (var i in obj) {
      // if a parent (2nd parameter) was passed in, then use that to
      // build the message. Message includes i (the object's property name)
      // then the object's property value on a new line
      if (parent) { var msg = parent + "." + i + "\n" + obj[i]; } else { var msg = i + "\n" + obj[i]; }
      // Display the message. If the user clicks "OK", then continue. If they
      // click "CANCEL" then quit this level of recursion
      if (!confirm(msg)) { return; }
      // If this property (i) is an object, then recursively process the object
      if (typeof obj[i] == "object") {
         if (parent) { dumpProps(obj[i], parent + "." + i); } else { dumpProps(obj[i], i); }
      }
   }
}

function show_eid(id) {
  if ((navigator.appName == 'Netscape')||(navigator.appName == 'Opera')) {
    document.getElementById(id).style['display']='table-row'
  } else {
    document.getElementById(id).style['display']='block'
  }
}

function hide_eid(id) {
  document.getElementById(id).style['display']='none'
}

function toggle_filter_value_input() {
  id = document.getElementById('addfilter').value
  id = 'addfilter_opt'+id
  if (document.getElementById(id).title == '') {
    hide_eid('tr_filtervalue')
  } else {
    show_eid('tr_filtervalue')
    document.getElementById('filtervalue').focus()
  }
}

//
// table class js functions
//
var timer;
function check_toggle_vis(id, checked, col){
    $("#table_"+id).find('[name='+col+']').each(function(){
         if (checked) {
             if ($(this).attr("cell") == '1') {
               _table_cell_decorator(id, this)
             }
             $(this).fadeIn('slow')
         } else {
             $(this).fadeOut('slow')
         }
    })
}
function show_result(e, url, id){
    clearTimeout(timer)
    timer=setTimeout(function validate(){
        sync_ajax(url, ['search'], id, function(){
            if ($('#'+id).html().length == 0){
                $('#'+id).hide()
            } else {
                $('#'+id).show()
                $('#'+id).css("left", $('body').width())
                keep_inside($('#'+id))
                register_pop_up(e, document.getElementById(id))
            }
        })
    }, 800)
}
function keep_inside(box){
    box_off_l = $(box).offset().left
    box_pos_l = $(box).position().left
    box_w = $(box).width()
    doc_w = $('body').width()
    if ((box_off_l+box_w+20)>doc_w) {
        if (box_off_l != box_pos_l) {
            over = doc_w-(box_off_l+box_w+20)
            $(box).css("left", over+'px')
        } else {
            new_l = doc_w - box_w - 20
            if (new_l < 0) {
		$(box).css("width", box_w + new_l)
		$(box).css("overflow-x", "auto")
		new_l = 0
	    }
            $(box).css("left", new_l+'px')
        }
    }
}
function click_toggle_vis(e, name, mode){
    $("[name="+name+"]").each(function () {
        if ($(this).css("display") == 'none' || $(this).css("display") == "") {
            $(this).show()
            keep_inside($(this))
            register_pop_up(e, $(this))
            $(this).find("select:visible").combobox()
        } else {
            $(this).hide()
        }
        $(this).find('input[type=text],textarea,select').filter(':visible:first').focus()
    })
}
function register_pop_up(e, box){
    if (e) {
        // IE event does not support stopPropagation
        if (!e.stopPropagation) {return}
        e.stopPropagation()
    }
    $(document).click(function(e) {
        e = e || event
        var target = e.target || e.srcElement
        if (target.id.match(/^ui-id/)) {
		// combox box click
		return
	}
        try {
            boxtop = box.get(0)
        } catch(e) {
            return
        }
        do {
            if (boxtop == target) {
                // click inside
                return
            }
            target = target.parentNode
        } while(target)
        box.hide()
    })
}
function check_all(name, checked){
    c = document.getElementsByName(name);
    for(i = 0; i < c.length; i++) {
        if (c[i].type == 'checkbox' && c[i].disabled == false) {
            c[i].checked = checked
            c[i].value = checked
        }
    }
}
function getIdsByName(names){
    ids = []
    for (j = 0; j < names.length; j++) {
        $("[name="+names[j]+"]").each(function(){
            ids.push($(this).attr('id'))
        })
    }
    return ids
}
function sparkl(url, id) {
    if (!$("#"+id).is(":visible")) {
        return
    }
    chartoptions = {type: 'tristate'};
    $.getJSON(url, function(data) {
        $(document.getElementById(id)).sparkline(data, chartoptions);
    });
}
function comp_status_plot(url, id) {
    if (!$("#"+id).is(":visible")) {
        return
    }
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	$.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                drawGridlines: false,
                borderWidth: 0,
                shadow: false,
                background: 'rgba(0,0,0,0)'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadow: false
            },
	    series: [
                {
                    label: 'ok',
                    color: 'lightgreen'
                },
                {
                    label: 'errors',
                    color: 'red'
                },
                {
                    label: 'n/a',
                    color: 'gray'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {
                        formatString:'%s',
                        showMark:false,
                        showGridline: false,
                        fontSize:'7pt'
                    },
                    ticks: data[0],
                    padMax: 0
		}, 
		yaxis: {
		    min: 0, 
		    tickOptions:{
                        showLabel: false,
                        size: 0,
                        formatString:'%d'
                    }
		}
	    }
	});
    });
}
function avail_plot(id, data) {
    $.jqplot.config.enablePlugins = true;
        document.getElementById(id).style['height'] = '50px'
	$.jqplot(id, data, {
            width: 300,
            height: 50,
            cursor: {
                zoom:true,
                showTooltip:true
            },
            highlighter: {
                show: false
            },
	    grid: {
                drawGridlines: false,
                borderWidth: 0,
                shadow: false,
                background: 'rgba(0,0,0,0)'
            },
	    seriesDefaults: {
                breakOnNull : true,
                breakOnNull: true,
                fill: false
            },
	    series: [
                {
                    label: 'down',
                    color: 'red'
                },
                {
                    label: 'down acked',
                    color: 'gray'
                },
                {
                    label: 'ack',
                    markerOptions:{style:'filledDiamond'}
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer, 
		    tickOptions: {
                        fontSize:'7pt',
		        formatString:'%#m/%#d %R'
                    }
		}, 
		yaxis: {
		    min: 0.8, 
		    max: 1.2, 
		    tickOptions:{
                        showLabel: false,
                        size: 0,
                        formatString:'%d'
                    }
		}
	    }
	})
}
function ajax_changed(url1, last, f) {
    $.ajax({
         type: "POST",
         url: url1,
         data: "",
         success: function(msg){
             if (parseInt(msg) < last) {
                 f()
             }
         }
    })
}
function sync_ajax(url, inputs, id, f) {
    s = inputs
    var query=""
    for (i=0; i<s.length; i++) {
        if (i > 0) {query=query+"&"}
        e = $("#"+s[i])
        if (e.is('select')) {
           val = e.find(":selected").val()
        } else {
           val = e.val()
        }
        query=query+encodeURIComponent(s[i])+"="+encodeURIComponent(val);
    }
    $.ajax({
         type: "POST",
         url: url,
         data: query,
         context: document.body,
         success: function(msg){
             $("#"+id).html(msg)
             $("#"+id).find("script").each(function(i){
               //eval($(this).text());
               $(this).remove();
             });
             f()
             $("#"+id).parents(".white_float").each(function(){keep_inside(this)})
         }
    })
}
function table_restripe_lines(id) {
    prev_spansum = ""
    cls = ["cell1", "cell2"]
    i = 1
    $("#table_"+id).children().children(".tl").each(function(){
       spansum = $(this).attr("spansum")
       if (spansum != prev_spansum) {
           prev_spansum = spansum
           cl = cls[i]
           i = 1 - i
       }
       if ($(this).hasClass(cl)) {
           return
       }
       $(this).removeClass(cls[i]).addClass(cl)
    })
}

function table_trim_lines(t) {
    perpage = parseInt($("#table_"+t.id).attr("perpage")) + 2
    lines = $("#table_"+t.id).children("tbody").children()
    if (lines.length <= perpage) {
        return
    }
    for (i=perpage; i<lines.length; i++) {
        $(lines[i]).remove()
    }
    lines = null
}

function sort_table(id) {
    keys = $("#table_"+id).attr("order").split(",")
    table_lines = $("#table_"+id).children("tbody").children(".tl")
    for (i=0; i<table_lines.length-1; i++) {
        line1 = $(table_lines[i])
        line_moved = false
        for (j=i+1; j<table_lines.length; j++) {
            if (line_moved) {
                break
            }
            line2 = $(table_lines[j])
            eq = 0
            for (k=0; k<keys.length; k++) {
                key = keys[k]
                if (key.charAt(0) == "~") {
                    asc = false
                    key = key.slice(1, key.length)
                } else {
                    asc = true
                }
                cname = id+"_c_"+key
                v1 = line1.find("[name="+cname+"]").attr("v")
                v2 = line2.find("[name="+cname+"]").attr("v")
                //if (i==0) {alert(v1+" "+ v2 + " " + asc )}
                if (v1 == v2) {
                    eq += 1
                    if (eq == keys.length) {
                        // all values equal, don't move the line
                        line_moved = true
                    }
                    continue
                }
                try {
                    v1 = parseFloat(v1)
                    v2 = parseFloat(v2)
                    cmp = (v1 < v2)
                } catch(e) {
                    cmp = (v1.localeCompare(v2) < 0)
                }
                if (asc && cmp) {
                    if (j > i+1) {
                        line1.insertAfter(line2)
                    }
                    line_moved = true
                    break
                } else if ((!asc) && (!cmp)) {
                    if (j > i+1) {
                        //line1.insertAfter(line2)
                    }
                    line_moved = true
                    break
                } else if (asc && (!cmp)) {
                    // no need to compare more keys, the line should be lower than j
                    break
                } else if ((!asc) && cmp) {
                    // no need to compare more keys, the line should be lower than j
                    break
                }
            }
        }
        if (!line_moved && (i<table_lines.length-1)) {
            line1.insertAfter(line2)
        }
    }
    keys = null
    table_lines = null
    line1 = null
    line2 = null
    v1 = null
    v2 = null
    asc = null
    cmp = null
}

function table_refresh(t) {
    if ($("#refresh_"+t.id).hasClass("spinner")) {
        return
    }
    var query = t.id+"_page="+$("#"+t.id+"_page").val()
    $.ajax({
         type: "POST",
         url: t.ajax_url+"/line",
         data: query,
         context: document.body,
         beforeSend: function(req){
             t.set_refresh_spin()
         },
         success: function(msg){
             // disable DOM insert event trigger for perf
             t.scroll_disable_dom()

             try {
                 var data = $.parseJSON(msg)
                 var pager = data['pager']
                 var msg = data['table_lines']
             } catch(e) {}

             // strip the topmost table marks
             msg = msg.replace(/^.table.|.\/table.$/g, '')

             // mark old lines for deletion
             $("#table_"+t.id).find(".tl").addClass("deleteme")

             // insert new lines
             $("#table_"+t.id).children("tbody").first().append(msg)

             tbody = $("#table_"+t.id).children("tbody")
             tbody.children(".tl").each(function(){
               if ($(this).hasClass("deleteme")) {
                   return
               }
               new_line = $(this)
               cksum = $(this).attr("cksum")
               old_line = tbody.children(".deleteme[cksum="+cksum+"]")
               if (old_line.length == 0) {
                   new_line.effect("highlight", 1000)
               }
               old_line.each(function(){
                 j = 0
                 for (i=0; i<$(this).children().length; i++) {
                   new_cell = $(":nth-child("+i+")", new_line)
                   if (!new_cell.is(":visible")) {
                     continue
                   }
                   cell = $(":nth-child("+i+")", this)
                   if (cell.attr("v") == new_cell.attr("v")) {
                     continue
                   }
                   new_cell.effect("highlight", 1000)
                 }
               })
             })

             // delete old lines
             tbody.children(".deleteme").remove()

             try {
               _table_pager(t.id, pager["page"], pager["perpage"], pager["start"], pager["end"], pager["total"])
             } catch(e) {}
             t.bind_filter_selector()
             t.restripe_lines()
             t.hide_cells()
             t.decorate_cells()
             t.unset_refresh_spin()

             t.scroll_enable_dom()

             // clear mem refs
             cksum = null
             msg = null
             cell = null
             new_cell = null
             new_line = null
             old_line = null
         }
    })
}

function table_insert(t, data) {
    var query="volatile_filters=true"
    for (i=0; i<data.length; i++) {
        try {
            key=data[i]["key"]
            val=data[i]["val"]
            op=data[i]["op"]
            query=query+"&"+encodeURIComponent(t.id+"_f_"+key)+op+encodeURIComponent(val)
        } catch(e) {
            return
        }
    }
    $.ajax({
         type: "POST",
         url: t.ajax_url+"/line",
         data: query,
         context: document.body,
         beforeSend: function(req){
             t.set_refresh_spin()
         },
         success: function(msg){

             // disable DOM insert event trigger for perf
             t.scroll_disable_dom()

             try {
                 var data = $.parseJSON(msg)
                 var pager = data['pager']
                 var msg = data['table_lines']
             } catch(e) {}

             // strip the topmost table marks
             msg = msg.replace(/^.table.|.\/table.$/g, '')

             // replace already displayed lines
             modified = []

             n_new_lines = 0

             $(msg).each(function(){
               n_new_lines += 1
               new_line = $(this)
               cksum = $(this).attr("cksum")
               $("#table_"+t.id).find("[cksum="+cksum+"]").each(function(){
                 $(this).before(new_line)
                 for (i=1; i<$(this).children().length+1; i++) {
                   cell = $(":nth-child("+i+")", this)
                   if (!cell.is(":visible")) {
                     continue
                   }
                   new_cell = $(":nth-child("+i+")", new_line)
                   if (cell.attr("v") == new_cell.attr("v")) {
                     continue
                   }
                   new_cell.addClass("highlight")
                 }
                 $(this).remove()
                 modified.push(cksum)
               })
             })

             // insert new lines
             first_line = $("#table_"+t.id).find(".tl").first()
             first_line.before(msg)
             if (msg.length > 0) {
                 // remove "no data" lines
                 $("#table_"+t.id).find(".nodataline").remove()
             }

             new_line = first_line.prev(".tl")
             while (new_line.length > 0) {
                 if (modified.indexOf(new_line.attr("cksum"))>=0) {
                     // remove lines already changed in-place
                     new_line = new_line.prev()
                     new_line.next().remove()
                     continue
                 }
                 // highlight new lines
                 new_line.addClass("highlight")
                 new_line = new_line.prev(".tl")
             }
             n_new_lines -= modified.length
             pager_total = $("#table_"+t.id).attr("pager_total")
             pager_total = parseInt(pager_total) + n_new_lines
             $("#table_"+t.id).attr("pager_total", pager_total)

             t.pager()
             t.trim_lines()
             t.restripe_lines()
             t.bind_filter_selector()
             t.hide_cells()
             t.decorate_cells()

             $(".highlight").each(function(){
                $(this).removeClass("highlight")
                $(this).effect("highlight", 1000)
             })

             t.unset_refresh_spin()
             t.scroll_enable_dom()

             // clear mem refs
             cksum = null
             msg = null
             cell = null
             new_cell = null
             new_line = null
             b = null
             modified = null
         }
    })
}

function table_ajax_submit(url, id, inputs, additional_inputs, input_name, additional_input_name) {
    var s = inputs.concat(additional_inputs).concat(getIdsByName(input_name))
    $("[name="+additional_input_name+"]").each(function(){s.push(this.id)});
    var query=""
    for (i=0; i<s.length; i++) {
        if (i > 0) {query=query+"&"}
        try {
            query=query+encodeURIComponent(s[i])+"="+encodeURIComponent(document.getElementById(s[i]).value);
        } catch(e) {}
    }
    $.ajax({
         type: "POST",
         url: url,
         data: query,
         context: document.body,
         beforeSend: function(req){
	     $("#refresh_"+id).toggleClass("spinner")
         },
         success: function(msg){
             $("#"+id).html(msg)
             $("#"+id).find("script").each(function(i){
               //eval($(this).text());
               $(this).remove();
             });
         }
    })
}
function toggle_extra(url, id, e, ncols) {
    line=$(e).parents(".tl")
    if (ncols==0) {
        ncols = line.children("[cell=1]").length
    }
    if (line.next().children("#"+id).attr("id")!=id) {
        line.after("<tr><td id="+id+" colspan="+ncols+" style='display:none'></td></tr>")
        $("#"+id).toggleClass("spinner")
    }
    if ($('#'+id).css("display") == 'none') {
        $('#'+id).show()
        sync_ajax(url, [], id, function(){$("#"+id).removeClass("spinner")})
    } else {
        $('#'+id).hide()
    }
}
function checked_services() {
    d = new Array()
    $("[name=svcmon_ck]").each(function(){
        if (this.type == 'checkbox' && this.disabled == false && this.checked) {
            d.push($(this).parents('tr').children("[name=svcmon_c_mon_svcname]").attr('v'))
        }
    })
    return d.join(",");
}
function checked_nodes() {
    l = document.getElementsByName('nodes_ck');
    d = new Array()
    for(i=0; i<l.length; i++) {
        if (l[i].type == 'checkbox' && l[i].disabled == false && l[i].checked) {
            d.push(l[i].id.replace("nodes_ckid_",""));
        }
    }
    return d.join(",");
}
function plot_height(id, data) {
    h = Math.max(100+data.length*30, 200)+'px'
    document.getElementById(id).style['height'] = h
}
function plot_width_x(id, data) {
    h = Math.max(100+data.length*40, 200)+'px'
    document.getElementById(id).style['width'] = h
}
function plot_width(id, data) {
    w = 12
    for (i=0; i<data.length; i++) {
        w = Math.max(w, data[i].length)
    }
    w -= 12
    iw = $('#'+id).width()
    $('#'+id).width(iw+w*5+'px')
}

function stats_avg_cpu_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id, data[0])
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average cpu utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'usr'},
                {label: 'nice'},
                {label: 'sys'},
                {label: 'iowait'},
                {label: 'steal'},
                {label: 'irq'},
                {label: 'soft'},
                {label: 'guest'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString:'%.2f %%', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_swp_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "MB")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height(id, data[0])
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average swap utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'free'},
                {label: 'used'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit'], angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_mem_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "MB")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height(id, data[0])
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average memory utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'free'},
                {label: 'cache'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit'], angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_block_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }

        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height('tps_'+id, data[0])
        $('#tps_'+id).width('450px')
	p = $.jqplot('tps_'+id, [data[1][0], data[1][1]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average io/s'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit']+'io/s', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#tps_'+id), p)

        max = 0
        for (i=0; i<data[1][2].length; i++) {
            max = Math.max(max, data[1][2][i][0]+data[1][3][i][0])
        }
        d = best_unit_mb(max, "KB")
        for (i=0; i<data[1][2].length; i++) {
            data[1][2][i][0] /= d['div']
            data[1][3][i][0] /= d['div']
        }

        plot_height('bps_'+id, data[0])
        $('#bps_'+id).width('450px')
	p = $.jqplot('bps_'+id, [data[1][2], data[1][3]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average block devices bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#bps_'+id), p)
    });
}
function stats_disk_for_svc(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }

        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
        }

        plot_height(id, data[0])
        $('#'+id).width('450px')
	p = $.jqplot(id, [data[1][0]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Disk size per service'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:10
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'SAN disk size'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_proc_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id+'_runq_sz', data[0])
        $('#'+id+'_runq_sz').width('450px')
	p = $.jqplot(id+'_runq_sz', [data[1][0]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average run queue size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'runq sz'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id+'_runq_sz'), p)

        plot_height(id+'_plist_sz', data[0])
        $('#'+id+'_plist_sz').width('450px')
	p = $.jqplot(id+'_plist_sz', [data[1][1]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average process list size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'plist sz'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
		    tickOptions:{formatString:'%i'}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	});
        _jqplot_extra($('#'+id+'_plist_sz'), p)
    });
}
function dash_history(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                rendererOptions: {
                    barDirection:'vertical',
                    barPadding: 6,
                    barMargin:10
                },
                shadowAngle: 135
            },
            series: [
                { label: 'alerts' },
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString:'%i'}
                }
            }
        });
        _jqplot_extra($('#'+id), p)
    });
}
function comp_history(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                { label: 'ok' },
                { label: 'nok' },
                { label: 'na' }
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString:'%i'}
                }
            }
        });
        _jqplot_extra($('#'+id), p)
    });
}
function stat_day(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        $('#'+id+'_err').height('300px')
        $('#'+id+'_err').width('300px')
	p = $.jqplot(id+'_err', [data[2]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
		    label: 'err',
                    markerOptions: {size: 2},
		    color: 'red'
		}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_err'), p)

        $('#'+id+'_apps').height('300px')
        $('#'+id+'_apps').width('300px')
	p = $.jqplot(id+'_apps', [data[11]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
		    label: 'apps',
                    markerOptions: {size: 2}
		}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_apps'), p)

        $('#'+id+'_nb_vcpu').height('300px')
        $('#'+id+'_nb_vcpu').width('300px')
	p = $.jqplot(id+'_nb_vcpu', [data[20]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'vcpu',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nb_vcpu'), p)

        $('#'+id+'_nb_vmem').height('300px')
        $('#'+id+'_nb_vmem').width('300px')

        max = 0
        for (i=0; i<data[21].length; i++) {
            max = Math.max(max, data[21][i][1])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[21].length; i++) {
            data[21][i][1] /= d['div']
        }

	p = $.jqplot(id+'_nb_vmem', [data[21]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'vmem',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nb_vmem'), p)

        $('#'+id+'_disk').height('300px')
        $('#'+id+'_disk').width('300px')

        max = 0
        for (i=0; i<data[5].length; i++) {
            max = Math.max(max, data[5][i][1]+data[31][i][1])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[5].length; i++) {
            data[5][i][1] /= d['div']
            data[31][i][1] /= d['div']
        }

	p = $.jqplot(id+'_disk', [data[5], data[31]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'SAN disk size',
                    breakOnNull: true
                },
                {
                    label: 'DAS disk size',
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_disk'), p)

        $('#'+id+'_nodes_ram').height('300px')
        $('#'+id+'_nodes_ram').width('300px')

        max = 0
        for (i=0; i<data[6].length; i++) {
            max = Math.max(max, data[6][i][1])
        }
        d = best_unit_mb(max*1024)
        for (i=0; i<data[6].length; i++) {
            data[6][i][1] *= 1024
            data[6][i][1] /= d['div']
        }

	p = $.jqplot(id+'_nodes_ram', [data[6]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'ram size',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes_ram'), p)

        $('#'+id+'_nodes_core').height('300px')
        $('#'+id+'_nodes_core').width('300px')
	p = $.jqplot(id+'_nodes_core', [data[7]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'cores',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes_core'), p)

        $('#'+id+'_accounts').height('300px')
        $('#'+id+'_accounts').width('300px')
	p = $.jqplot(id+'_accounts', [data[12]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    markerOptions: {size: 2},
		    label: 'accounts'
		}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_accounts'), p)

        $('#'+id+'_resp_accounts').height('300px')
        $('#'+id+'_resp_accounts').width('300px')
	p = $.jqplot(id+'_resp_accounts', [data[22]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    markerOptions: {size: 2},
		    label: 'sys responsible accounts'
		}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_resp_accounts'), p)

        $('#'+id+'_actions').height('300px')
        $('#'+id+'_actions').width('300px')
	p = $.jqplot(id+'_actions', [data[4],  data[3], data[2]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'ok',
                    color: 'lightgreen'
                },
                {
                    label: 'warn',
                    color: 'orange'
                },
                {
                    label: 'error',
                    color: 'red'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_actions'), p)

        $('#'+id+'_nodes').height('300px')
        $('#'+id+'_nodes').width('300px')
	p = $.jqplot(id+'_nodes', [data[17],  data[14]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'PRD nodes'
                },
                {
                    label: 'other nodes'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes'), p)

        $('#'+id+'_virt_nodes').height('300px')
        $('#'+id+'_virt_nodes').width('300px')
	p = $.jqplot(id+'_virt_nodes', [data[23],  data[24]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'virtual nodes'
                },
                {
                    label: 'physical nodes'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		},
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_virt_nodes'), p)

        $('#'+id+'_svc_type').height('300px')
        $('#'+id+'_svc_type').width('300px')
	p = $.jqplot(id+'_svc_type', [data[15],  data[0]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {label: 'PRD svc'},
                {label: 'other svc'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_type'), p)

        $('#'+id+'_svc_cluster').height('300px')
        $('#'+id+'_svc_cluster').width('300px')
	p = $.jqplot(id+'_svc_cluster', [data[16],  data[18]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    seriesDefaults: {
                breakOnNull: true,
                fill: true
            },
	    series: [
                {label: 'clustered svc'},
                {label: 'not clustered svc'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_cluster'), p)

        $('#'+id+'_svc_drp').height('300px')
        $('#'+id+'_svc_drp').width('300px')
	p = $.jqplot(id+'_svc_drp', [data[13],  data[19]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'svc with drp'
                },
                {
                    label: 'svc without drp'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_drp'), p)
    });
}
function stat_compare_day(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        labels = new Array()
        for (i=0; i<data[0].length; i++){
            labels.push({'label': data[0][i]})
        }
        $('#'+id+'_svc').height('300px')
        $('#'+id+'_svc').width('300px')
	p = $.jqplot(id+'_svc', data[1][25], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc'), p)

        $('#'+id+'_nodes').height('300px')
        $('#'+id+'_nodes').width('300px')
	p = $.jqplot(id+'_nodes', data[1][26], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes'), p)

        $('#'+id+'_nodes_virt_ratio').height('300px')
        $('#'+id+'_nodes_virt_ratio').width('300px')
	p = $.jqplot(id+'_nodes_virt_ratio', data[1][27], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes_virt_ratio'), p)

        $('#'+id+'_svc_prd_ratio').height('300px')
        $('#'+id+'_svc_prd_ratio').width('300px')
	p = $.jqplot(id+'_svc_prd_ratio', data[1][28], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_prd_ratio'), p)

        $('#'+id+'_svc_drp_ratio').height('300px')
        $('#'+id+'_svc_drp_ratio').width('300px')
	p = $.jqplot(id+'_svc_drp_ratio', data[1][29], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_drp_ratio'), p)

        $('#'+id+'_svc_clu_ratio').height('300px')
        $('#'+id+'_svc_clu_ratio').width('300px')
	p = $.jqplot(id+'_svc_clu_ratio', data[1][30], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svc_clu_ratio'), p)
    });
}
function stats_cpu(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Cpu usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                markerOptions: {size: 2},
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                breakOnNull : true,
                shadowWidth: 2
            },
	    series: [
                { label: 'usr' },
                { label: 'nice' },
                { label: 'sys' },
                { label: 'iowait' },
                { label: 'steal' },
                { label: 'irq' },
                { label: 'soft' },
                { label: 'guest' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_proc(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id+'_runq_sz', [data[0]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Run queue size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'runq_sz' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_runq_sz'), p)

	p = $.jqplot(id+'_plist_sz', [data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Process list size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'plist_sz' }
            ],
	    axes: {
		xaxis: {
                    min: data[1][0][0],
                    max: data[1][data[1].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_plist_sz'), p)

	p = $.jqplot(id+'_loadavg', [data[2],data[3],data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Load average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'loadavg 1\'' },
                { label: 'loadavg 5\'' },
                { label: 'loadavg 15\'' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_loadavg'), p)
    });
}
function stats_svc_cpu(url, id) {
    stats_svc(url, id, "cpu usage", "%")
}
function stats_svc_mem(url, id) {
    stats_svc(url, id, "mem usage", "%")
}
function stats_svc_nproc(url, id) {
    stats_svc(url, id, "nproc", "")
}
function stats_svc_rss(url, id) {
    stats_svc(url, id, "rss")
}
function stats_svc_swap(url, id) {
    stats_svc(url, id, "swap")
}
function stats_svc_pg(url, id) {
    stats_svc(url, id, "paging")
}
function stats_svc_avgpg(url, id) {
    stats_svc(url, id, "average paging")
}
function stats_svc_at(url, id) {
    stats_svc(url, id, "at")
}
function stats_svc_avgat(url, id) {
    stats_svc(url, id, "average at")
}
function stats_svc_cap(url, id) {
    stats_svc(url, id, "mem cap")
}
function stats_svc_cap_cpu(url, id) {
    stats_svc(url, id, "cpu cap", "")
}
function stats_svc(url, id, title, unit) {
    if(typeof(unit)==='undefined') {
        unit = "MB"
    }

    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data.length < 2) { return }
        if (data[1].length == 0) { return }
        if (data[1][0].length < 2) { return }
        svcnames = data[0]
        series = []
        for (i=0; i<svcnames.length; i++) {
            series.push({ label: svcnames[i] })
        }

        max = 0

        for (i=0; i<data[1].length; i++) {
          for (j=0; j<data[1][i].length; j++) {
            max = Math.max(max, data[1][i][j][1])
          }
        }
        d = best_unit_mb(max, unit)
        for (i=0; i<data[1].length; i++) {
          for (j=0; j<data[1][i].length; j++) {
            data[1][i][j][1] /= d['div']
          }
        }

	p = $.jqplot(id, data[1], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: title
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[2],
                    max: data[3],
		    renderer: $.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_mem(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {

        max = 0
        for (i=0; i<data[1].length; i++) {
            max = Math.max(max, (data[1][i][1]+data[3][i][1]+data[4][i][1]+data[7][i][1]+data[0][i][1])/1024)
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']*1024
            data[3][i][1] /= d['div']*1024
            data[4][i][1] /= d['div']*1024
            data[7][i][1] /= d['div']*1024
            data[0][i][1] /= d['div']*1024
        }

	p = $.jqplot(id+'_u', [data[1], data[3], data[4], data[7], data[0]], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Memory usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used' },
                { label: 'used, buffer' },
                { label: 'used, cache' },
                { label: 'used, sys' },
                { label: 'free' }
            ],
	    axes: {
		xaxis: {
                    min: data[1][0][0],
                    max: data[1][data[1].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_u'), p)

	p = $.jqplot(id+'_pct', [data[2],data[6]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Memory usage percent'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used/mem' },
                { label: 'promised/(mem+swap)' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct'), p)

    });
}
function stats_swap(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {

        max = 0
        for (i=0; i<data[1].length; i++) {
            max = Math.max(max, (data[1][i][1]+data[3][i][1]+data[0][i][1])/1024)
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']*1024
            data[3][i][1] /= d['div']*1024
            data[0][i][1] /= d['div']*1024
        }

	p = $.jqplot(id+'_u', [data[1], data[3], data[0]], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Swap usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used' },
                { label: 'used, cached' },
                { label: 'free' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_u'), p)

	p = $.jqplot(id+'_pct', [data[2],data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Swap usage percent'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used/total' },
                { label: 'cached/used' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct'), p)
    });
}
function stats_block(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data[0].length; i++) {
            max = Math.max(max, (data[0][i][1]))
            max = Math.max(max, (data[1][i][1]))
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']
            data[0][i][1] /= d['div']
        }

	p = $.jqplot(id+'_tps', [data[0],data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device transactions'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'read' },
                { label: 'write' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'io/s'},
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_tps'), p)

        max = 0
        for (i=0; i<data[2].length; i++) {
            max = Math.max(max, (data[2][i][1]))
            max = Math.max(max, (data[3][i][1]))
        }
        d = best_unit_mb(max, 'KB')
        for (i=0; i<data[2].length; i++) {
            data[2][i][1] /= d['div']
            data[3][i][1] /= d['div']
        }

	p = $.jqplot(id+'_bps', [data[2],data[3]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'read' },
                { label: 'write' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'},
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_bps'), p)
    });
}
function stats_trend_mem(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Memory usage trend<br>high/low/average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer, 
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'mem usage KB' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {formatString:'%s'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_trend_cpu(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Cpu usage trend<br>high/low/average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer, 
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'cpu usage %' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {formatString:'%s'}
		}, 
		yaxis: {
		    min: 0,
		    max: 100,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_blockdev(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]
        data = _data['time']['secps']['data']
        labels = _data['time']['secps']['labels']
        max_secps = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_secps = Math.max(max_secps, Math.abs(data[i][j][1]))
          }
        }
        d_secps = best_unit_mb(max_secps, '')
        max_secps /= d_secps['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_secps['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_secps_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Block device bandwidth'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_secps['fmt']+' '+d_secps['unit']+'sect/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_secps_time'), p)

        data = _data['time']['pct_util']['data']
        labels = _data['time']['pct_util']['labels']
        max_pct_util = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_pct_util = Math.max(max_pct_util, Math.abs(data[i][j][1]))
          }
        }
        d_pct_util = best_unit_mb(max_pct_util, '')
        max_pct_util /= d_pct_util['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_pct_util['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_pct_util_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device utilization'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_pct_util['fmt']+' '+d_pct_util['unit']+'%'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct_util_time'), p)

        data = _data['time']['tps']['data']
        labels = _data['time']['tps']['labels']
        max_tps = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_tps = Math.max(max_tps, Math.abs(data[i][j][1]))
          }
        }
        d_tps = best_unit_mb(max_tps, '')
        max_tps /= d_tps['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_tps['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_tps_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device transactions'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_tps['fmt']+' '+d_tps['unit']+'io/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_tps_time'), p)

        data = _data['time']['await']['data']
        labels = _data['time']['await']['labels']
        max_await = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_await = Math.max(max_await, Math.abs(data[i][j][1]))
          }
        }
        d_await = best_unit_mb(max_await, 'ms')
        max_await /= d_await['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_await['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_await_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device wait time'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_await['fmt']+' '+d_await['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_await_time'), p)

        data = _data['time']['svctm']['data']
        labels = _data['time']['svctm']['labels']
        max_svctm = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_svctm = Math.max(max_svctm, Math.abs(data[i][j][1]))
          }
        }
        d_svctm = best_unit_mb(max_svctm, 'ms')
        max_svctm /= d_svctm['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_svctm['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_svctm_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device service time'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_svctm['fmt']+' '+d_svctm['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svctm_time'), p)

        data = _data['time']['avgrq_sz']['data']
        labels = _data['time']['avgrq_sz']['labels']
        max_avgrq_sz = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_avgrq_sz = Math.max(max_avgrq_sz, Math.abs(data[i][j][1]))
          }
        }
        d_avgrq_sz = best_unit_mb(max_avgrq_sz, '')
        max_avgrq_sz /= d_avgrq_sz['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_avgrq_sz['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_avgrq_sz_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device request size'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_avgrq_sz['fmt']+' '+d_avgrq_sz['unit']+'sectors'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_avgrq_sz_time'), p)

        data = _data['avg']
        for (i=0; i<data[1].length; i++) {
          data[1][i][1] /= d_tps['div']
          data[1][i][2] /= d_tps['div']
          data[1][i][3] /= d_tps['div']
        }
        plot_width_x(id+'_tps', data[0])
	p = $.jqplot(id+'_tps', [data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device transactions<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'io/s' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_tps['fmt']+' '+d_tps['unit']+'io/s'},
		    max: max_tps,
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_tps'), p)

        for (i=0; i<data[2].length; i++) {
          data[2][i][1] /= d_avgrq_sz['div']
          data[2][i][2] /= d_avgrq_sz['div']
          data[2][i][3] /= d_avgrq_sz['div']
        }
        plot_width_x(id+'_avgrq_sz', data[0])
	p = $.jqplot(id+'_avgrq_sz', [data[2]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device request size<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'rq sz (sectors)' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_avgrq_sz,
                    tickOptions:{formatString: d_avgrq_sz['fmt']+' '+d_avgrq_sz['unit']+'sectors'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_avgrq_sz'), p)

        for (i=0; i<data[3].length; i++) {
          data[3][i][1] /= d_await['div']
          data[3][i][2] /= d_await['div']
          data[3][i][3] /= d_await['div']
        }
        plot_width_x(id+'_await', data[0])
	p = $.jqplot(id+'_await', [data[3]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device wait time<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'wait' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_await,
                    tickOptions:{formatString: d_await['fmt']+' '+d_await['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_await'), p)

        for (i=0; i<data[4].length; i++) {
          data[4][i][1] /= d_svctm['div']
          data[4][i][2] /= d_svctm['div']
          data[4][i][3] /= d_svctm['div']
        }
        plot_width_x(id+'_svctm', data[0])
	p = $.jqplot(id+'_svctm', [data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device service time<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'svc time' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_svctm,
                    tickOptions:{formatString: d_svctm['fmt']+' '+d_svctm['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_svctm'), p)

        for (i=0; i<data[5].length; i++) {
          data[5][i][1] /= d_pct_util['div']
          data[5][i][2] /= d_pct_util['div']
          data[5][i][3] /= d_pct_util['div']
        }
        plot_width_x(id+'_pct_util', data[0])
	p = $.jqplot(id+'_pct_util', [data[5]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device utilization<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'util (%)' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_pct_util['fmt']+' '+d_pct_util['unit']+'%'},
                    max: max_pct_util,
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct_util'), p)

        for (i=0; i<data[6][0].length; i++) {
          data[6][0][i] /= d_secps['div']
          data[6][1][i] /= d_secps['div']
        }
        plot_width_x(id+'_secps', data[0])
	p = $.jqplot(id+'_secps', data[6], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Block device bandwidth<br>average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d_secps['fmt']+' '+d_secps['unit']+'sect/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_secps'), p)

        plot_width_x(id+'_tm', data[7])
	p = $.jqplot(id+'_tm', data[8], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Hard/Soft times<br>average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'hard (msec)'},
                {label: 'soft (msec)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_tm'), p)
    });
}
function stats_netdev_err(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        errps = _data[0]
        collps = _data[1]
        dropps = _data[2]
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]

        labels = errps[0]
        data = errps[1]
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_errps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device errors/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_errps'), p)

        labels = collps[0]
        data = collps[1]
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_collps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device collisions/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_collps'), p)

        labels = dropps[0]
        data = dropps[1]
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_dropps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device drops/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_dropps'), p)
    });
}
function stats_netdev_avg(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        plot_width_x(id+'_kBps', data[0])
	p = $.jqplot(id+'_kBps', data[1], {
	    stackSeries: false,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Net device bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'avg rcv (kB/s)'},
                {label: 'avg send (kB/s)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_kBps'), p)

        plot_width_x(id+'_pckps', data[0])
	p = $.jqplot(id+'_pckps', data[2], {
	    stackSeries: false,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Net device packet rate'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'avg rcv (pck/s)'},
                {label: 'avg send (pck/s)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pckps'), p)
    });
}
function stats_netdev(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        bw = _data[0]
        pk = _data[1]
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]

        labels = bw[0]
        data = bw[1]
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, 'KB')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            if (data[i][j][1] == null) {continue}
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_kBps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device bandwidth'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_kBps'), p)

        labels = pk[0]
        data = pk[1]
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            if (data[i][j][1] == null) {continue}
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_pckps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device packets/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pckps'), p)
    });
}
function fancy_size_mb(size) {
    if (size<1024) {
        unit = 'MB'
        _size = size
    } else if (size<1048576) {
        unit = 'GB'
        _size = size / 1024
    } else {
        unit = 'TB'
        _size = size / 1048576
    }
    if (_size>=100) {
        _size = Math.round(_size)
    } else if (_size>=10) {
        _size = Math.round(_size*10)/10
    } else {
        _size = Math.round(_size*100)/100
    }
    return _size + ' ' + unit
}
function best_unit_mb(max, iunit) {
    if (typeof(iunit)==='undefined') {
        iunit = "MB"
    }
    if (iunit.length == 2) {
        unit = iunit[iunit.length-1]
    } else {
        unit = ""
    }
    if (unit == 'B') {
        mul = 1024
    } else {
        mul = 1000
    }

    if (iunit.length < 1) {
        idiv = 1
    } else if (iunit[0] == 'K') {
        idiv = mul
    } else if (iunit[0] == 'm') {
        idiv =  1/mul
    } else if (iunit[0] == 'M') {
        idiv = mul*mul
    } else if (iunit[0] == 'u') {
        idiv =  1/mul/mul
    } else if (iunit[0] == 'G') {
        idiv = mul*mul*mul
    } else if (iunit[0] == 'p') {
        idiv =  1/mul/mul/mul
    } else if (iunit[0] == 'T') {
        idiv = mul*mul*mul*mul
    } else if (iunit[0] == 'P') {
        idiv = mul*mul*mul*mul*mul
    } else {
        idiv = 1
    }
    max *= idiv

    if (unit == 's' && max<1/mul/mul) {
        unit = 'p'+unit
        div = 1/mul/mul/mul
    } else if (unit == 's' && max<1/mul) {
        unit = 'u'+unit
        div = 1/mul/mul
    } else if (unit == 's' && max<1) {
        unit = 'm'+unit
        div = 1/mul
    } else if (max<mul) {
        unit = ''+unit
        div = 1
    } else if (max<mul*mul) {
        unit = 'K'+unit
        div = mul
    } else if (max<mul*mul*mul) {
        unit = 'M'+unit
        div = mul*mul
    } else if (max<mul*mul*mul*mul) {
        unit = 'G'+unit
        div = mul*mul*mul
    } else if (max<mul*mul*mul*mul*mul) {
        unit = 'T'+unit
        div = mul*mul*mul*mul
    } else {
        unit = 'P'+unit
        div = mul*mul*mul*mul*mul
    }
    max /= div

    if (max >= 100) {
        fmt = '%i'
    } else if (max >= 10) {
        fmt = '%.1f'
    } else {
        fmt = '%.2f'
    }
    return {'unit': unit, 'div': div/idiv, 'fmt': fmt}
}
function stats_fs(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        labels = new Array()
        for (i=0;i<data[0].length;i++){
            labels.push({'label': data[0][i]})
        }
        h = labels.length
        h = Math.max(38*h, 300)
        $('#'+id+'_u').height(h+'px')
        //plot_width_x(id+'_u', data[0])
	p = $.jqplot(id+'_u', data[1], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Fs usage %'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
                    min: data[1][0][0][0],
                    max: data[1][0][data[1][0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    max: 100,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
  	});
        _jqplot_extra($('#'+id+'_u'), p)
    });
}
function stat_os(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        $("#"+id).width("600px")
        //plot_width(id, data[0])
        labels = new Array()
        for (i=0;i<data[0].length;i++){
            labels.push({'label': data[0][i]})
        }
        h = labels.length
        h = Math.max(24*h, 300)
        $('#'+id).height(h+'px')
        if (id == 'stat_os_name') {
             title = ''
        } else {
             title = id.replace('stat_os_','')
        }
	p = $.jqplot(id, data[1], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: title
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'ne',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer, 
		    tickOptions:{formatString:'%F'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}
function ackpanel(e, show, s){
    if (e.pageX || e.pageY) {
        posx = e.pageX;
        posy = e.pageY;
    }
    else if (e.clientX || e.clientY) {
        posx = e.clientX + document.body.scrollLeft
             + document.documentElement.scrollLeft;
        posy = e.clientY + document.body.scrollTop
             + document.documentElement.scrollTop;
    }
    if (show) {
        $("#ackpanel").css({"left": posx + "px", "top": posy + "px"});
        $("#ackpanel").show();
    } else {
        $("#ackpanel").hide();
    }
    $("#ackpanel").html(s)
}
function refresh_action(url, id){
    spintimer=setTimeout(function validate(){ajax(url, [], 'spin_span_'+id)}, 3000);
}
function click_action_queue(url) {
    $("#action_queue").toggle('fast')
    if ($("#action_queue").is(":visible")) {
        ajax(url, [], 'action_queue')
    }
}
function refresh_plot(url, rowid, id) {
    sync_ajax(url,['begin_'+rowid, 'end_'+rowid], id, function(){})
}
function toggle_plot(url, rowid, id) {
    if ($("#"+id).is(":visible")) {
        $("#"+id).hide()
        $("#refresh_"+id).hide()
        $("#close_"+id).hide()
    } else {
        $("#"+id).show()
        $("#refresh_"+id).show()
        $("#close_"+id).show()
        refresh_plot(url, rowid, id)
    }
}
function stats_appinfo(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max, "")
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, {
            cursor:{zoom:true},
            stackSeries: true,
            legend: {
                show: false
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_disk_array(url, id) {
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                {label: 'used'},
                {label: 'free'},
                {label: 'reserved', fill: false, disableStack: true},
                {label: 'reservable', fill: false, disableStack: true}
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_disk_app(url, id) {
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                {label: 'used'},
                {label: 'quota'}
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	});
        _jqplot_extra($('#'+id), p)
    });
}
function charts_plot(url, id) {
    $.jqplot.config.enablePlugins = true
    $.getJSON(url, function(dd) {
        data = dd['data']
        instances = dd['instances']
        options = dd['options']
        stackSeries = options['stack']
        series = []
        unit = ""
        if (instances.length>1) {
	    legend = {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{
                  numberRows: 7,
                  numberColumns: instances.length/7
                },
                show: true,
                placement: "outside",
                location: 'e'
            }
	} else {
	    legend = {
		show: false
	    }
	}
        for (i=0; i<instances.length; i++) {
            serie = {
              'label': instances[i]['label'],
              'shadow': instances[i]['shadow'],
              'fill': instances[i]['fill']
            }
	    series.push(serie)
            unit = instances[i]['unit']
	}
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max, unit)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, {
	    stackSeries: stackSeries,
            cursor:{zoom:true, showTooltip:false},
            legend: legend,
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: series,
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	});
        _jqplot_extra($('#'+id), p)
    });
}
function obsplot(o) {
  var data = $.parseJSON(o.html())
  o.html("")
  if (data[0].length < 1) {
    return
  }
  options = {
	    cursor: {
                show: true,
                zoom: true
            },
            highlighter: {
                show: true
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            series: [
                {label: 'delta', renderer: $.jqplot.BarRenderer,
                 rendererOptions: {
                  barWidth: 10
                 }
                },
                {label: 'sigma'},
                {label: 'today', color: 'red', showMarker: false},
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b\n%Y'}
                },
                yaxis: {
                    min: 0,
                    max: data[2][1][1],
                    tickOptions:{formatString:'%i'}
                }
            }
  }
  p = $.jqplot(o.attr('id'), data, options)
  _jqplot_extra(o, p)
}

function jqplot_img(){
    if (!$.jqplot.use_excanvas) {
        $('div.jqplot-target').each(function(){
            _jqplot_img(this)
        })
    }
}

function _jqplot_extra(e, p){
	_jqplot_resize(e, p);
	_jqplot_img(e);
}

function _jqplot_resize(e, p){
	e.parent().resizable({delay:20});
	e.parent().bind('resize', function(event, ui) {
          e.width('100%');
          e.height('90%');
	  p.replot( { resetAxes: false } );
	});
}

function _jqplot_img(e){
            var outerDiv = $(document.createElement('div'));
            var header = $(document.createElement('div'));
            var div = $(document.createElement('div'));

            outerDiv.append(header);
            outerDiv.append(div);

            outerDiv.addClass('jqplot-image-container');
            header.addClass('jqplot-image-container-header');
            div.addClass('jqplot-image-container-content');

            header.html('Right Click to Save Image As...');

            var close = $(document.createElement('a'));
            close.addClass('jqplot-image-container-close');
            close.html('Close');
            close.click(function() {
                $(this).parents('div.jqplot-image-container').hide(500);
            })
            header.append(close);

            $(e).after(outerDiv);
            outerDiv.hide();

            outerDiv = header = div = close = null;

            if (!$.jqplot._noToImageButton) {
                var btn = $(document.createElement('button'));
                btn.text('View Plot Image');
                btn.addClass('jqplot-image-button');
                btn.bind('click', {chart: $(e)}, function(evt) {
                    var imgelem = evt.data.chart.jqplotToImageElem();
                    var div = $(e).nextAll('div.jqplot-image-container').first();
                    div.children('div.jqplot-image-container-content').empty();
                    div.children('div.jqplot-image-container-content').append(imgelem);
                    div.show(500);
                    div = null;
                });

                $(e).after(btn);
                btn.after('<br />');
                btn = null;
            }
}

function filter_submit(id,k,v){
  $("#"+k).val(v)
  window["ajax_submit_"+id]()
};

function table_bind_filter_selector(t) {
  $("#table_"+t.id).each(function(){
    $(this).bind("mouseup", function(event) {
      cell = $(event.target)
      if (typeof cell.attr("v") === 'undefined') {
        cell = cell.parents("[cell=1]").first()
      }
      filter_selector(t.id, event, cell.attr('name'), cell.attr('v'))
    })
    $(this).bind("contextmenu", function() {
      return false
    })
    $(this).bind("click", function() {
      $("#fsr"+t.id).hide()
    })
  })
}

function filter_selector(id,e,k,v){
  if(e.button != 2) {
    return
  }
  $("#fsr"+id).each(function() {
    $(this)[0].oncontextmenu = function() {
      return false;
    }
  });
  var sel = window.getSelection().toString()
  if (sel.length == 0) {
    sel = v
  }
  _sel = sel
  $("#fsr"+id).show()
  if (e.pageX || e.pageY) {
      posx = e.pageX;
      posy = e.pageY;
  }
  else if (e.clientX || e.clientY) {
      posx = e.clientX + document.body.scrollLeft
           + document.documentElement.scrollLeft;
      posy = e.clientY + document.body.scrollTop
           + document.documentElement.scrollTop;
  }
  $("#fsr"+id).find(".bgred").each(function(){
    $(this).removeClass("bgred")
  })
  function getsel(){
    __sel = _sel
    if ($("#fsr"+id).find("#fsrwildboth").hasClass("bgred")) {
      __sel = '%' + __sel + '%'
    } else
    if ($("#fsr"+id).find("#fsrwildleft").hasClass("bgred")) {
      __sel = '%' + __sel
    } else
    if ($("#fsr"+id).find("#fsrwildright").hasClass("bgred")) {
      __sel = __sel + '%'
    }
    if ($("#fsr"+id).find("#fsrneg").hasClass("bgred")) {
      __sel = '!' + __sel
    }
    return __sel
  }
  $("#fsr"+id).css({"left": posx + "px", "top": posy + "px"})
  $("#fsr"+id).find("#fsrview").each(function(){
    $(this).text($("[name="+k+"]").find("input").val())
    $(this).unbind()
    $(this).bind("dblclick", function(){
      sel = $(this).text()
      $(".sym_headers").find("[name="+k+"]").find("input").val(sel)
      filter_submit(id,k,sel)
    })
    $(this).bind("click", function(){
      sel = $(this).text()
      cur = sel
      $(this).removeClass("highlight")
      $(this).addClass("b")
      $(".sym_headers").find("[name="+k+"]").find("input").val(sel)
      $(".theader_slim").find("[name="+k+"]").each(function(){
        $(this).removeClass("bgred")
        $(this).addClass("bgorange")
      })
    })
  })
  $("#fsr"+id).find("#fsrreset").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text("")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrclear").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text("**clear**")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrneg").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+id).find("#fsrwildboth").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+id).find("#fsrwildleft").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+id).find("#fsrwildright").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+id).find("#fsreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(sel)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrandeq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      cur =  $(".sym_headers").find("[name="+k+"]").find("input").val()
      val = cur + '&' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsroreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      cur =  $(".sym_headers").find("[name="+k+"]").find("input").val()
      val = cur + '|' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '>' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrandsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&>' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrorsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|>' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '<' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrandinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&<' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrorinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|<' + sel
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($("#fsr"+id).find("#fsrneg").hasClass("bgred")) {
        val = '!empty'
      } else {
        val = 'empty'
      }
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrandempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr"+id).find("#fsrneg").hasClass("bgred")) {
        val = val + '&!empty'
      } else {
        val = val + '&empty'
      }
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+id).find("#fsrorempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr"+id).find("#fsrneg").hasClass("bgred")) {
        val = val + '|!empty'
      } else {
        val = val + '|empty'
      }
      $("#fsr"+id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
};

//
// Table link url popup
//
function get_view_url() {
  var url = $(location).attr('href')
  if (url.indexOf('?')>0) {
    url=url.substring(0, url.indexOf('?'))
  }
  return url
}

function table_link(t){
  var url = get_view_url()
  var re = /#$/;
  url = url.replace(re, "")+"?";
  args = "clear_filters=true&discard_filters=true&dbfilter="+$("#avs"+t.id).val()
  $("#"+t.id).find("[name=fi]").each(function(){
    if ($(this).val().length==0) {
      return
    }
    args=args+'&'+$(this).attr('id')+"="+encodeURIComponent($(this).val())
  })
  alert(url+args)
}

//
// cell decorators
//

var os_class_h = {
  'darwin': 'os_darwin',
  'linux': 'os_linux',
  'hp-ux': 'os_hpux',
  'osf1': 'os_tru64',
  'opensolaris': 'os_opensolaris',
  'solaris': 'os_solaris',
  'sunos': 'os_solaris',
  'freebsd': 'os_freebsd',
  'aix': 'os_aix',
  'windows': 'os_win',
  'vmware': 'os_vmware'
}

function cell_decorator_nodename(e) {
  _cell_decorator_nodename(e, true)
}

function cell_decorator_nodename_no_os(e) {
  _cell_decorator_nodename(e, false)
}

function _cell_decorator_nodename(e, os_icon) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  if (os_icon) {
    try {
      os_cell = $(e).parent().children(".os_name")
      os_c = os_class_h[os_cell.attr("v").toLowerCase()]
      div.addClass(os_c)
    } catch(e) {}
  }
  try {
    svc_autostart_cell = $(e).parent().children(".svc_autostart")
    if (svc_autostart_cell.attr("v") == v) {
      div.addClass("b")
    }
  } catch(e) {}
  $(e).click(function(){
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/ajax_node/ajax_node?node="+v+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_svcname(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).click(function(){
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/default/ajax_service?node="+v+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_status(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    v = "undef"
  }
  var c = v
  var line = $(e).parent(".tl")
  if (status_outdated(line)) {
    c = "undef"
  }
  c = c.replace(' ', '_')
  $(e).empty()
  $(e).append("<div class='boxed_small boxed_status boxed_status_"+c+"'>"+v+"</div>")
}

function cell_span(id, e) {
  try {
    var s = $(e).attr("name").split("_c_")[1]
  } catch(e) {
    return false
  }
  if (osvc.tables[id].span.indexOf(s) < 0) {
    return false
  }
  var line = $(e).parent(".tl")
  var span_id = line.attr("spansum")
  var prev_span_id = line.prev().attr("spansum")
  if (span_id == prev_span_id) {
    return true
  }
  return false
}

function cell_decorator_svcmon_links(e) {
  $(e).empty()
  var mon_svcname = line.children("[name$=mon_svcname]").attr("v")
  var query = "clear_filters=true&actions_f_svcname="+mon_svcname
  query += "&actions_f_status_log=empty"
  query += "&actions_f_begin="+encodeURIComponent(">-1d")
  url = $(location).attr("origin") + "/init/svcactions/svcactions?"+query
  var d = "<a class='clickable action16' href="+url+">&nbsp</a>"

  var mon_frozen = line.children("[name$=mon_frozen]").attr("v")
  if (mon_frozen == "1") {
    d += "<span class='frozen16'>&nbsp</span>"
  }
  $(e).append(d)
}

function cell_decorator_chk_type(e) {
  var v = $(e).attr("v")
  if (v=="") {
    return
  }
  $(e).empty()
  $(e).append("<div>"+v+"</div>")
  div = $(":first-child", e)
  div.addClass("a")
  div.addClass("nowrap")
  $(e).click(function(){
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/checks/ajax_chk_type_defaults/"+v
    toggle_extra(url, id, e, 0)
  })
}

function status_outdated(line) {
  var s = line.children("[cell=1][name$=mon_updated]").attr("v")
  if (typeof s === 'undefined') {
    var s = line.children("[cell=1][name$=_updated]").attr("v")
  }
  if (typeof s === 'undefined') {
    return true
  }
  s = s.replace(/ /, "T")
  var d = new Date(s)
  var now = new Date()
  delta = now - d
  if (delta > 15*60000) {
    return true
  }
  return false
}

function cell_decorator_availstatus(e) {
  var line = $(e).parent(".tl")
  var mon_availstatus = $(e).attr("v")
  if (mon_availstatus=="") {
    return
  }
  $(e).empty()
  var mon_containerstatus = line.children("[name$=mon_containerstatus]").attr("v")
  var mon_ipstatus = line.children("[name$=mon_ipstatus]").attr("v")
  var mon_fsstatus = line.children("[name$=mon_fsstatus]").attr("v")
  var mon_diskstatus = line.children("[name$=mon_diskstatus]").attr("v")
  var mon_sharestatus = line.children("[name$=mon_sharestatus]").attr("v")
  var mon_appstatus = line.children("[name$=mon_appstatus]").attr("v")

  if (status_outdated(line)) {
    var cl_availstatus = "status_undef"
    var cl_containerstatus = "status_undef"
    var cl_ipstatus = "status_undef"
    var cl_fsstatus = "status_undef"
    var cl_diskstatus = "status_undef"
    var cl_sharestatus = "status_undef"
    var cl_appstatus = "status_undef"
  } else {
    var cl_availstatus = mon_availstatus.replace(/ /g, '_')
    var cl_containerstatus = mon_containerstatus.replace(/ /g, '_')
    var cl_ipstatus = mon_ipstatus.replace(/ /g, '_')
    var cl_fsstatus = mon_fsstatus.replace(/ /g, '_')
    var cl_diskstatus = mon_diskstatus.replace(/ /g, '_')
    var cl_sharestatus = mon_sharestatus.replace(/ /g, '_')
    var cl_appstatus = mon_appstatus.replace(/ /g, '_')
  }
  var s = "<table>"
  s += "<tr>"
  s += "<td colspan=6 class=\"aggstatus status_" + cl_availstatus + "\">" + mon_availstatus + "</td>"
  s += "</tr>"
  s += "<tr>"
  s += "<td class=status_" + cl_containerstatus + ">vm</td>"
  s += "<td class=status_" + cl_ipstatus + ">ip</td>"
  s += "<td class=status_" + cl_fsstatus + ">fs</td>"
  s += "<td class=status_" + cl_diskstatus + ">dg</td>"
  s += "<td class=status_" + cl_sharestatus + ">share</td>"
  s += "<td class=status_" + cl_appstatus + ">app</td>"
  s += "</tr>"
  s += "</table>"
  $(e).append(s)
}

function cell_decorator_overallstatus(e) {
  var line = $(e).parent(".tl")
  var mon_overallstatus = $(e).attr("v")
  if (mon_overallstatus=="") {
    return
  }
  $(e).empty()
  var mon_containerstatus = line.children("[name$=mon_containerstatus]").attr("v")
  var mon_availstatus = line.children("[name$=mon_availstatus]").attr("v")
  var mon_hbstatus = line.children("[name$=mon_hbstatus]").attr("v")
  var mon_syncstatus = line.children("[name$=mon_syncstatus]").attr("v")

  if (status_outdated(line)) {
    var cl_overallstatus = "status_undef"
    var cl_availstatus = "status_undef"
    var cl_syncstatus = "status_undef"
    var cl_hbstatus = "status_undef"
  } else {
    var cl_overallstatus = mon_overallstatus.replace(/ /g, '_')
    var cl_availstatus = mon_availstatus.replace(/ /g, '_')
    var cl_syncstatus = mon_syncstatus.replace(/ /g, '_')
    var cl_hbstatus = mon_hbstatus.replace(/ /g, '_')
  }

  var s = "<table>"
  s += "<tr>"
  s += "<td colspan=3 class=\"aggstatus status_" + cl_overallstatus + "\">" + mon_overallstatus + "</td>"
  s += "</tr>"
  s += "<tr>"
  s += "<td class=status_" + cl_availstatus + ">avail</td>"
  s += "<td class=status_" + cl_hbstatus + ">hb</td>"
  s += "<td class=status_" + cl_syncstatus + ">sync</td>"
  s += "</tr>"
  s += "</table>"
  $(e).append(s)
}

cell_decorators = {
 "svcname": cell_decorator_svcname,
 "nodename": cell_decorator_nodename,
 "nodename_no_os": cell_decorator_nodename_no_os,
 "availstatus": cell_decorator_availstatus,
 "overallstatus": cell_decorator_overallstatus,
 "chk_type": cell_decorator_chk_type,
 "svcmon_links": cell_decorator_svcmon_links,
 "status": cell_decorator_status
}

function _table_cell_decorator(id, cell) {
  if (cell_span(id, cell)) {
    $(cell).empty()
    return
  }
  var cl = $(cell).attr('class')
  if (!cl) {
    return
  }
  cl = cl.split(/\s+/)
  for (i=0; i<cl.length; i++) {
    c = cl[i]
    if (!(c in cell_decorators)) {
      continue
    }
    cell_decorators[c](cell)
  }
}

function table_cell_decorator(id) {
  for (var c in cell_decorators) {
    if (!cell_decorators.hasOwnProperty(c)) {
      continue
    }
    //var start = new Date().getTime()
    $("#table_"+id).find("[cell=1]."+c+":visible").each(function(){
      if (cell_span(id, this)) {
        $(this).empty()
        return
      }
      try {
        cell_decorators[c](this)
      } catch(e) {}
    })
    //var end = new Date().getTime()
    //var time = end - start
    //alert(c+": "+time)
  }
}


//
// table pager
//
function _table_pager(id, p_page, p_perpage, p_start, p_end, p_total) {
  pager = $("#"+id).find(".pager")
  p_page = parseInt(p_page)
  p_start = parseInt(p_start)
  p_end = parseInt(p_end)
  p_total = parseInt(p_total)

  if ((p_total > 0) && (p_end > p_total)) {
    p_end = p_total
  }
  var s_total = ""
  if (p_total > 0) {
    s_total = "/" + p_total
  }

  // perpage selector
  var l = [20, 50, 100, 500]
  var selector = "<div name='pager_perpage' class='white_float' style='max-width:50%;display:none;text-align:right;'>"
  for (i=0; i<l.length; i++) {
     v = l[i]
     if (v == p_perpage) {
       c = " current_page"
     } else {
       c = ""
     }
     selector += "<span name='perpage_val' class='clickable"+c+"'>"+v+"</span><br>"
  }
  selector += "</div>"

  // main pager
  var d = ""
  if (p_total == 0) {
    d += "No records found matching filters"
  } else {
    if (p_page > 1) {
      d += "<span name='pager_left'><< </span>"
    }
    d += "<span name='pager_center'>"+(p_start+1)+"-"+p_end+s_total+"</span>"
    if ((p_total < 0) || ((p_page * p_perpage) < p_total)) {
      d += "<span name='pager_right'> >></span>"
    }
  }
  d += selector

  pager.empty()
  pager.append(d)
  pager.children("span").each(function () {
    $(this).addClass('current_page clickable')
  })
  pager.children("[name=pager_right]").click(function(){
    filter_submit(id, id+"_page", p_page+1)   
  })
  pager.children("[name=pager_left]").click(function(){
    filter_submit(id, id+"_page", p_page-1)   
  })
  pager.children("[name=pager_center]").click(function(){
    $(this).parent().children("[name=pager_perpage]").toggle()
  })
  pager.find("[name=perpage_val]").click(function(){
    filter_submit(id, id+"_perpage", parseInt($(this).text()))   
  })
}

function table_pager(t) {
  var te = $("#table_"+t.id)
  p_page = te.attr("pager_page")
  p_perpage = te.attr("pager_perpage")
  p_start = te.attr("pager_start")
  p_end = te.attr("pager_end")
  p_total = te.attr("pager_total")
  _table_pager(t.id, p_page, p_perpage, p_start, p_end, p_total)
}

//
// table horizontal scroll
//
function table_scroll(t){
  to=$("#table_"+t.id)
  to_p=to.parent()
  ww=$(window).width()
  tw=to.width()
  if (ww>=tw) {
    $("#table_"+t.id+"_left").hide()
    $("#table_"+t.id+"_right").hide()
    return
  }
  if (to_p.scrollLeft()>0) {
    $("#table_"+t.id+"_left").show()
    $("#table_"+t.id+"_left").height(to.height())
  } else {
    $("#table_"+t.id+"_left").hide()
  }
  if (to_p.scrollLeft()+ww<tw) {
    $("#table_"+t.id+"_right").show()
    $("#table_"+t.id+"_right").height(to.height())
    $("#table_"+t.id+"_right").css({'top': to.position().top})
  } else {
    $("#table_"+t.id+"_right").hide()
  }
}

function table_scroll_enable(t) {
  $("#table_"+t.id+"_left").click(function(){
    $("#table_"+t.id).parent().animate({'scrollLeft': '-='+$(window).width()}, 500)
  })
  $("#table_"+t.id+"_right").click(function(){
    $("#table_"+t.id).parent().animate({'scrollLeft': '+='+$(window).width()}, 500)
  })
  $("#table_"+t.id).parent().scroll(function(){
    table_scroll(t)
  })
  $(window).resize(function(){
    table_scroll(t)
  })
  $(".down16,.right16").click(function() {
    table_scroll(t)
  })
  t.scroll_enable_dom()
}

function table_scroll_enable_dom(t) {
  $(window).bind("DOMNodeInserted", table_scroll(t))
  table_scroll(t)
}
function table_scroll_disable_dom(t) {
  $(window).unbind("DOMNodeInserted", table_scroll(t))
}

function table_bind_link(t) {
  $("#link_"+t.id).bind("click", function(){
    t.link()
  })
  $(this).bind("keypress", function(event) {
    if ($('input').is(":focus")) { return }
    if ($('textarea').is(":focus")) { return }
    if ( event.which == 108 ) {
      //event.preventDefault()
      t.link()
    }
  })
}

function table_bind_refresh(t) {
  $("#refresh_"+t.id).bind("click", function(){
    t.refresh()
  })
  $(this).bind("keypress", function(event) {
    if ($('input').is(":focus")) { return }
    if ($('textarea').is(":focus")) { return }
    if ( event.which == 114 ) {
      //event.preventDefault()
      t.refresh()
    }
  })
}

function table_bind_filter_reformat(t) {
  $("#table_"+t.id).find("input").each(function(){
   attr = $(this).attr('id')
   if ( typeof(attr) == 'undefined' || attr == false ) {
     return
   }
   if ( ! attr.match(/nodename/gi) && 
        ! attr.match(/svcname/gi) && 
        ! attr.match(/assetname/gi) && 
        ! attr.match(/mon_nodname/gi) && 
        ! attr.match(/disk_nodename/gi) && 
        ! attr.match(/disk_id/gi) && 
        ! attr.match(/disk_svcname/gi) && 
        ! attr.match(/save_nodename/gi) && 
        ! attr.match(/save_svcname/gi)
      ) {return}
   $(this).bind("change keyup input", function(){
    if (this.value.match(/ /g)) {
      if (this.value.match(/^\(/)) {return}
      this.value = this.value.replace(/ /g, ',')
      if (!this.value.match(/^\(/)) {
        this.value = '(' + this.value
      }
      if (!this.value.match(/\)$/)) {
        this.value = this.value + ')'
      }
    }
   })
  })
}

function table_hide_cells(t) {
  for (i=0; i<t.columns.length; i++) {
    var c = t.columns[i]
    if (t.visible_columns.indexOf(c) >= 0) {
      continue
    }
    n = t.id + "_c_" + c
    $("#table_"+t.id).find("[name="+n+"]").hide()
  }
}

function table_toggle_column(id, column, table) {
  var fid = id + '_f_' + column
  var cname = id + '_c_' + column
  var ccname = id + '_cc_' + column
  var value = $("[name="+ccname+"]").is(":checked")

  if ($("#"+fid) && $("#"+fid).val().length>0) {
    $("[name="+ccname+"]").checked = true
    return
  }

  check_toggle_vis(id, value, cname);
  table_scroll(id);
  var query = "set_col_table="+table
  query += "&set_col_field="+column
  query += "&set_col_value="+value
  var url = $(location).attr("origin") + "/init/ajax/ajax_set_user_prefs_column?"+query
  ajax(url, [], "set_col_dummy")
}

function table_unset_refresh_spin(t) {
  $("#refresh_"+t.id).removeClass("spinner")
}

function table_set_refresh_spin(t) {
  $("#refresh_"+t.id).addClass("spinner")
}


var osvc = {
 'tables': {}
}

function table_init(id, ajax_url, columns, visible_columns) {
  var t = {
    'id': id,
    'ajax_url': ajax_url,
    'span': $("#table_"+id).attr("span").split(","),
    'columns': columns,
    'visible_columns': visible_columns,
    'decorate_cells': function(){
      table_cell_decorator(id)
    },
    'hide_cells': function(){
      table_hide_cells(this)
    },
    'scroll': function(){
      table_scroll(id)
    },
    'bind_filter_reformat': function(){
      table_bind_filter_reformat(this)
    },
    'bind_filter_selector': function(){
      table_bind_filter_selector(this)
    },
    'bind_refresh': function(){
      table_bind_refresh(this)
    },
    'bind_link': function(){
      table_bind_link(this)
    },
    'pager': function(){
      table_pager(this)
    },
    'trim_lines': function(){
      table_trim_lines(this)
    },
    'restripe_lines': function(){
      table_restripe_lines(id)
    },
    'scroll_enable': function(){
      table_scroll_enable(this)
    },
    'scroll_enable_dom': function(){
      table_scroll_enable_dom(this)
    },
    'scroll_disable_dom': function(){
      table_scroll_disable_dom(this)
    },
    'set_refresh_spin': function(){
      table_set_refresh_spin(this)
    },
    'unset_refresh_spin': function(){
      table_unset_refresh_spin(this)
    },
    'insert': function(data){
      table_insert(this, data)
    },
    'link': function(){
      table_link(this)
    },
    'refresh': function(){
      table_refresh(this)
    }
  }
  osvc.tables[id] = t
  $("#"+id).find("select").parent().css("white-space", "nowrap")
  $("#"+id).find("select:visible").combobox()

  t.bind_filter_reformat()
  t.bind_refresh()
  t.bind_link()

  t.hide_cells()
  t.decorate_cells()
  t.bind_filter_selector()
  t.pager()
  t.restripe_lines()
  t.scroll_enable()
}

