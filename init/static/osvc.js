//
// IE indexOf workaround
//
if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function(obj, start) {
    for (var i = (start || 0), j = this.length; i < j; i++) {
      if (this[i] === obj) { return i; }
    }
    return -1;
  }
}

//
// search tool
//
function bind_search_tool() {
  $(document).keydown(function(event) {
    if ( event.which == 27 ) {
      $("input:focus").blur()
      $("textarea:focus").blur()
      $(".white_float").hide()
      $(".white_float_input").hide()
      $(".right_click_menu").hide()
      return
    }
    if ($('input').is(":focus")) {
      return
    }
    if ($('textarea').is(":focus")) {
      return
    }
    searchbox = $(".search").find("input")
    if ( event.which == 83 ) {
      event.preventDefault();
      searchbox.focus()
    }
  })
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
            // websocket disabled for this table.
            // just remember we have queued change.
            osvc.tables[key].need_refresh = true
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
  e = $('#'+did)
  _invert_filter(e)
}

function table_invert_filter(id, did){
  e = $("#"+id).find('#'+did)
  _invert_filter(e)
}

function _invert_filter(e){
	var v = e.val()
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
		e.val(v)
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
		e.val(v)
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
    var t = osvc.tables[id]
    var c = col.split("_c_")[1]
    if (checked) {
      t.visible_columns.push(c)
    } else {
      t.visible_columns = t.visible_columns.filter(function(x){if (x!=c){return true}})
    }
    $("#table_"+id).find('[name='+col+']').each(function(){
         if (checked) {
             if ($(this).attr("cell") == '1') {
               _table_cell_decorator(id, this)
               table_refresh_column_filter(t, c)
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
             var t = osvc.tables[id]
             if (typeof t === 'undefined') { return }
             t.refresh_child_tables()
             t.on_change()
         }
    })
}
function table_restripe_lines(id) {
    var prev_spansum = ""
    var cls = ["cell1", "cell2"]
    var cl = "cell1"
    var i = 1
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

function table_format_input(t, c, val) {
  var s = "<td name='"+t.id+"_c_"+c+"'>"
  s += "<span class='clickable filter16'></span>"
  if (typeof(val) === "undefined") {
    val = ""
  }
  if (val == "**clear**") {
    val = ""
  }
  var n = val.length
  if ((n == 0) && (t.colprops[c].default_filter != "")) {
    val = t.colprops[c].default_filter
    n = val.length
  }
  if (n > 0) {
    if (n > 20) {
      _val = val.substring(0, 17)
    } else {
      _val = val
    }
    s += "<span class='clickable invert16'></span>"
    s += "<span class='clickable clear16'></span>"
    s += "<span title='"+val+"'>"+_val+"</span>"
  }
  s +=  "<div class='white_float_input'>"
  s +=   "<input name='fi' value='"+val+"' id='"+t.id+"_f_"+c+"'>"
  s +=   "<span class='clickable values_to_filter'></span>"
  s +=   "<br>"
  s +=   "<span id='"+t.id+"_fc_"+c+"'></span>"
  s +=  "</div>"
  s += "</td>"
  return s
}

function table_format_theader_slim(t, c, val) {
  if (typeof(val) === "undefined") {
    val = ""
  }
  if (val == "**clear**") {
    val = ""
  }
  var n = val.length
  if ((n == 0) && (t.colprops[c].default_filter != "")) {
    val = t.colprops[c].default_filter
    n = val.length
  }
  var cl = ""
  if ((val.length > 0) && (val != "**clear**")) {
    cl = " class='bgred'"
  }
  var s = "<td name='"+t.id+"_c_"+c+"'"+cl+">"
  return s
}

function table_refresh_column_filter(t, c, val) {
  if (typeof(val) === "undefined") {
    var e = $("#table_"+t.id).find("#"+t.id+"_f_"+c)
    val = e.val()
  }
  cell = $("#table_"+t.id).find("tr.sym_headers").find("td[name="+t.id+"_c_"+c+"]")
  cell.replaceWith(table_format_input(t, c, val))
  cell = $("#table_"+t.id).find("tr.theader_slim").find("td[name="+t.id+"_c_"+c+"]")
  cell.replaceWith(table_format_theader_slim(t, c, val))
}

function table_refresh_column_filters(t) {
  for (i=0; i<t.visible_columns.length; i++) {
    var c = t.visible_columns[i]
    t.refresh_column_filter(c)
  }
  t.bind_filter_input_events()
}

function table_format_header(t) {
  table_refresh_column_filters(t)
}

function table_cell_fmt(t, k, v) {
  var s = ""
  var cl = ""
  var n = t.id+"_c_"+k
  var classes = []
  if ((k == "extra") && (typeof(t.extrarow_class) !== 'undefined')) {
    classes.push(t.extrarow_class)
  }
  if ((k != "extra") && (t.visible_columns.indexOf(k) < 0)) {
    classes.push("hidden")
  }
  if (k in t.colprops) {
    classes = classes.concat(t.colprops[k]._class.split(" "))
    classes = classes.concat(t.colprops[k]._dataclass.split(" "))
  }
  if (classes.length > 0) {
    var cs = classes.join(' ').replace(/\s+$/, '')
    cl = " class='"+cs+"'"
  } 
  if (v == 'empty') {
    var text = ""
  } else {
    var text = v
  }
  s += "<td cell='1' name='"+n+"' v='"+v+"'"+cl+">"+text+"</td>"
  return s
}

function table_bind_checkboxes(t) {
  $("#table_"+t.id).find("[name="+t.id+"_ck]").each(function(){
    this.value = this.checked
    $(this).click(function(){this.value = this.checked})
  })
}

function table_data_to_lines(t, data) {
  var lines = ""
  for (var i=0; i<data.length; i++) {
    var line = ""
    if (t.checkboxes) {
      line += "<td><input value='"+data[i]['checked']+"' type='checkbox' id='"+t.id+"_ckid_"+data[i]['id']+"' name='"+t.id+"_ck'></td>"
    }
    if (t.extrarow) {
      var cols = ["extra"].concat(t.columns)
    } else {
      var cols = t.columns
    }
    for (var j=0; j<cols.length; j++) {
      var k = cols[j]
      var v = data[i]['cells'][j]
      line += table_cell_fmt(t, k, v)
    }
    lines += "<tr class='tl' spansum='"+data[i]['spansum']+"' cksum='"+data[i]['cksum']+"'>"+line+"</tr>"
  }
  return lines
}

function table_refresh(t) {
    if (!$("#"+t.id).is(":visible")) {
        return
    }
    if ($("#refresh_"+t.id).hasClass("spinner")) {
        t.need_refresh = true
        return
    } else {
        t.set_refresh_spin()
    }
    var query="table_id="+t.id
    query += '&'+t.id+"_page="+$("#"+t.id+"_page").val()
    for (c in t.colprops) {
      if (t.colprops[c].force_filter == "") {
        continue
      }
      query += "&"+encodeURIComponent(t.id+"_f_"+c)+"="+encodeURIComponent(t.colprops[c].force_filter)
    }
    query += "&visible_columns="+t.visible_columns.join(',')
    if (t.dataable) {
      var ajax_interface = "data"
    } else {
      var ajax_interface = "line"
    }
    $.ajax({
         type: "POST",
         url: t.ajax_url+"/"+ajax_interface,
         data: query,
         context: document.body,
         beforeSend: function(req){
         },
         success: function(msg){
             // disable DOM insert event trigger for perf
             t.need_refresh = false
             t.scroll_disable_dom()

             try {
                 var data = $.parseJSON(msg)
                 var format = data['format']
                 var pager = data['pager']
                 var lines = data['table_lines']
             } catch(e) {
                 $("#"+t.id).html(msg)
                 return
             }

             var msg = ""
             if (format == "json") {
               msg = table_data_to_lines(t, lines)
             } else {
               msg = lines
             }

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
                   new_line.addClass("tohighlight")
                   return
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
                   new_cell.addClass("tohighlight")
                 }
               })
             })

             // delete old lines
             tbody.children(".deleteme").remove()

             try {
               _table_pager(t.id, pager["page"], pager["perpage"], pager["start"], pager["end"], pager["total"])
             } catch(e) {}
             t.bind_checkboxes()
             t.bind_filter_selector()
             t.restripe_lines()
             t.hide_cells()
             t.decorate_cells()
             t.unset_refresh_spin()

             t.scroll_enable_dom()

             tbody.find(".tohighlight").removeClass("tohighlight").effect("highlight", 1000)

             t.refresh_child_tables()
             t.on_change()

             // clear mem refs
             cksum = null
             msg = null
             cell = null
             new_cell = null
             new_line = null
             old_line = null
             if (t.need_refresh) {
               $("#refresh_"+t.id).trigger("click")
             }
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
             t.need_refresh = false

             // disable DOM insert event trigger for perf
             t.scroll_disable_dom()

             try {
                 var data = $.parseJSON(msg)
                 var format = data['format']
                 var pager = data['pager']
                 var lines = data['table_lines']
             } catch(e) {}

             var msg = ""
             if (format == "json") {
               msg = table_data_to_lines(t, lines)
             } else {
               msg = lines
             }

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
             t.bind_checkboxes()
             t.bind_filter_selector()
             t.hide_cells()
             t.decorate_cells()

             $(".highlight").each(function(){
                $(this).removeClass("highlight")
                $(this).effect("highlight", 1000)
             })

             t.unset_refresh_spin()
             t.scroll_enable_dom()

             t.refresh_child_tables()
             t.on_change()

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
    var t = osvc.tables[id]

    // close dialogs
    $("#"+t.id).find(".white_float").hide()
    $("#"+t.id).find(".white_float_input").hide()

    var s = inputs.concat(additional_inputs).concat(getIdsByName(input_name))
    $("[name="+additional_input_name+"]").each(function(){s.push(this.id)});
    var query="table_id="+t.id
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
	   t.set_refresh_spin()
         },
         success: function(msg){
           if (!t.dataable) {
             $("#"+id).html(msg)
             $("#"+id).find("script").each(function(i){
               //eval($(this).text());
               $(this).remove();
             })
             t.on_change()
	     t.unset_refresh_spin()
           } else {
	     t.unset_refresh_spin()
             t.refresh()
           }
           t.refresh_child_tables()
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

function dashpie_sev(o) {
  var data = $.parseJSON(o.html())
  o.html("")
  o.height("300px")
  colors = {
    "4": "#2d2d2d",
    "3": "#660000",
    "2": "#990000",
    "1": "#ffa500",
    "0": "#009900"
  }
  c = []
  for (i=0;i<data.length;i++) {
      c.push(colors[data[i][0][data[i][0].length-1]])
  }
  options = {
      grid:{background:'transparent',borderColor:'transparent',shadow:false,drawBorder:false,shadowColor:'transparent'},
      seriesDefaults: {
        renderer: $.jqplot.PieRenderer,
        seriesColors: c,
        rendererOptions: {
          sliceMargin: 4,
          dataLabelPositionFactor: 0.7,
          startAngle: -90,
          dataLabels: 'value',
          showDataLabels: true
        }
      },
      legend: { show:false, location: 'e' }
    }
  $.jqplot(o.attr('id'), [data], options)
  o.bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
    dash_severity = data[seriesIndex][data[seriesIndex].length-1]
    $("#dashboard_f_dash_severity").val(dash_severity)
    filter_submit("dashboard", "dashboard_f_dash_severity", d)
  })
}

function plot_dashpie_sev(o) {
  $("#sev_chart").each(function(){
    dashpie_sev($(this))
  })
}

function savedonut(o) {
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var title = total
  o.html("")
  $.jqplot(o.attr('id'), d['data'],
    {
      grid:{background:'transparent',borderColor:'transparent',shadow:false,drawBorder:false,shadowColor:'transparent'},
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          showDataLabels: true
        }
      },
      title: { text: title }
    }
  )
  $('#'+o.attr('id')).bind('jqplotDataHighlight',
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('level: '+seriesIndex+', data: '+data[0]);
        }
  )
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight',
        function (ev) {
            $('#chart_info').html('-');
        }
  )
  } catch(e) {}
}

function plot_savedonuts() {
  $("[id^=chart_svc]").each(function(){
    savedonut($(this))
  })
  $("[id^=chart_ap]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("saves", "saves_f_save_app", d)
    })
  })
  $("[id^=chart_group]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("saves", "saves_f_save_group", d)
    })
  })
  $("[id^=chart_server]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      $("#saves_f_save_server").val(d)
      filter_submit("saves", "saves_f_save_server", d)
    })
  })
}

function diskdonut(o) {
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var backend_total = fancy_size_mb(d['backend_total'])
  var title = total + ' (' + backend_total + ')'
  o.html("")
  $.jqplot(o.attr('id'), d['data'],
    {
      grid:{background:'transparent',borderColor:'transparent',shadow:false,drawBorder:false,shadowColor:'transparent'},
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          showDataLabels: true
        }
      },
      title: { text: title }
    }
  );
  $('#'+o.attr('id')).bind('jqplotDataHighlight', 
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('level: '+seriesIndex+', data: '+data[0]);
        }
  );
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight', 
        function (ev) {
            $('#chart_info').html('-');
        }
  );
  } catch(e) {}
}

function plot_diskdonuts() {
  $("[id^=chart_svc]").each(function(){
    diskdonut($(this))
  })
  $("[id^=chart_ap]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("disks", "disks_f_app", d)
    })
  })
  $("[id^=chart_dg]").each(function(){
    diskdonut($(this))
  })
  $("[id^=chart_ar]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      filter_submit("disks", "disks_f_disk_arrayid", d)
    })
  })
}

function filter_submit(id,k,v){
  $("#"+k).val(v)
  window["ajax_submit_"+id]()
  osvc.tables[id].refresh_column_filters()
};

function table_bind_filter_input_events(t) {
  var inputs = $("#"+t.id).find("input[name=fi]")
  var url = t.ajax_url + "_col_values/"

  // refresh column filter cloud on keyup
  inputs.bind("keyup", function(event) {
    var input = $(this)
    if (!is_enter(event)) {
      var col = input.attr('id').split('_f_')[1]
      input.parents('tr.sym_headers').siblings("tr.theader_slim").find("[name='"+t.id+"_c_"+col+"']").removeClass("bgred").addClass("bgorange")
      clearTimeout(timer)
      timer = setTimeout(function validate(){
        var dest_id = input.siblings("[id^="+t.id+"_fc_]").attr("id")
        _url = url + col + "?" + input.attr('id') + "=" + encodeURIComponent(input.val())
        sync_ajax(_url, [], dest_id, function(){})
      }, 1000)
    }
  })

  // validate column filter on <enter> keypress
  inputs.bind("keypress", function(event) {
    if (is_enter(event)) {
      t.refresh_column_filters()
    }
    var fn = "ajax_enter_submit_"+t.id
    window[fn](event)
  })

  // open filter input on filter icon click
  inputs.parent().siblings(".filter16").bind("click", function(event) {
    var e = $(this).siblings(".white_float_input")
    e.toggle()
    if (e.is(":visible")) {
      keep_inside(e)
      register_pop_up(event, $(e))
      e.find("input").focus()
    }
  })

  // clear column filter click
  inputs.parent().siblings(".clear16").bind("click", function(event) {
    var k = $(this).parent().attr('name').replace("_c_", "_f_")
    filter_submit(t.id, k, "**clear**")
  })

  // invert column filter click
  inputs.parent().siblings(".invert16").bind("click", function(event) {
    var k = $(this).parent().attr('name').replace("_c_", "_f_")
    table_invert_filter(t.id, k)
    window["ajax_submit_"+t.id]()
    t.refresh_column_filters()
  })

  // values to column filter click
  inputs.siblings(".values_to_filter").bind("click", function(event) {
    var k = $(this).parent().find("input").attr('id')
    var ck = k.replace("_f_", "_fc_")
    var col = k.split("_f_")[1]
    function f() {
      values_to_filter(k, ck)
      window["ajax_submit_"+t.id]()
      t.refresh_column_filters()
    }
    _url = url + col + "?" + k + "=" + encodeURIComponent($("#"+k).val())
    sync_ajax(_url, [], ck, f)
  })
}

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
  try {
    var sel = window.getSelection().toString()
  } catch(e) {
    var sel = document.selection.createRange().text
  }
  if (sel.length == 0) {
    sel = v
  }
  _sel = sel
  $("#fsr"+id).show()
  var posx = 0
  var posy = 0
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
      $("#fsr"+id).hide()
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

function table_add_scrollers(t) {
  var s = ""
  s = "<div id='table_"+t.id+"_left' class='scroll_left'>&nbsp</div>"
  $("#table_"+t.id).before(s)
  s = "<div id='table_"+t.id+"_right' class='scroll_right'>&nbsp</div>"
  $("#table_"+t.id).after(s)
}

function table_add_filterbox(t) {
  var s = "<span id='fsr"+t.id+"' class='right_click_menu'>"
  s += "<table>"
  s +=  "<tr>"
  s +=   "<td id='fsrview' colspan=3></td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsrclear'>clear</td>"
  s +=   "<td id='fsrreset'>reset</td>"
  s +=   "<td id='fsrneg'>!</td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsrwildleft'>%..</td>"
  s +=   "<td id='fsrwildright'>..%</td>"
  s +=   "<td id='fsrwildboth'>%..%</td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsreq'>=</td>"
  s +=   "<td id='fsrandeq'>&=</td>"
  s +=   "<td id='fsroreq'>|=</td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsrsup'>></td>"
  s +=   "<td id='fsrandsup'>&></td>"
  s +=   "<td id='fsrorsup'>|></td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsrsinf'><</td>"
  s +=   "<td id='fsrandinf'>&<</td>"
  s +=   "<td id='fsrorinf'>|<</td>"
  s +=  "</tr>"
  s +=  "<tr>"
  s +=   "<td id='fsrempty'>empty</td>"
  s +=   "<td id='fsrandempty'>&empty</td>"
  s +=   "<td id='fsrorempty'>|empty</td>"
  s +=  "</tr>"
  s += "</table>"
  s += "</span>"
  $("#"+t.id).append(s)
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

//
// cell decorators
//
var action_img_h = {
  'checks': 'check16',
  'enable': 'check16',
  'disable': 'nok',
  'pushservices': 'svc',
  'pushpkg': 'pkg16',
  'pushpatch': 'pkg16',
  'reboot': 'action_restart_16',
  'shutdown': 'action_stop_16',
  'syncservices': 'action_sync_16',
  'updateservices': 'action16',
  'updatepkg': 'pkg16',
  'updatecomp': 'pkg16',
  'stop': 'action_stop_16',
  'stopapp': 'action_stop_16',
  'stopdisk': 'action_stop_16',
  'stopvg': 'action_stop_16',
  'stoploop': 'action_stop_16',
  'stopip': 'action_stop_16',
  'stopfs': 'action_stop_16',
  'umount': 'action_stop_16',
  'shutdown': 'action_stop_16',
  'boot': 'action_start_16',
  'start': 'action_start_16',
  'startstandby': 'action_start_16',
  'startapp': 'action_start_16',
  'startdisk': 'action_start_16',
  'startvg': 'action_start_16',
  'startloop': 'action_start_16',
  'startip': 'action_start_16',
  'startfs': 'action_start_16',
  'mount': 'action_start_16',
  'restart': 'action_restart_16',
  'provision': 'prov',
  'switch': 'action_restart_16',
  'freeze': 'frozen16',
  'thaw': 'frozen16',
  'syncall': 'action_sync_16',
  'syncnodes': 'action_sync_16',
  'syncdrp': 'action_sync_16',
  'syncfullsync': 'action_sync_16',
  'postsync': 'action_sync_16',
  'push': 'log16',
  'check': 'check16',
  'fixable': 'fixable16',
  'fix': 'comp16',
  'pushstats': 'spark16',
  'pushasset': 'node16',
  'stopcontainer': 'action_stop_16',
  'startcontainer': 'action_start_16',
  'stopapp': 'action_stop_16',
  'startapp': 'action_start_16',
  'prstop': 'action_stop_16',
  'prstart': 'action_start_16',
  'push': 'svc',
  'syncquiesce': 'action_sync_16',
  'syncresync': 'action_sync_16',
  'syncupdate': 'action_sync_16',
  'syncverify': 'action_sync_16',
  'toc': 'action_toc_16',
  'stonith': 'action_stonith_16',
  'switch': 'action_switch_16'
}


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

function cell_decorator_chk_instance(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var chk_type = line.children("[name$=_chk_type]").attr("v")
  if (chk_type == "mpath") {
    url = $(location).attr("origin") + "/init/disks/disks?disks_f_disk_id="+v+"&clear_filters=true"
    s = "<a class='hd16' href='"+url+"'>"+v+"</a>"
    $(e).html(s)
  }
}

function cell_decorator_chk_high(e) {
  var high = $(e).attr("v")
  var line = $(e).parent(".tl")
  var v = line.children("[name$=_chk_value]").attr("v")
  var cl = []
  v = parseInt(v)
  high = parseInt(high)
  if (v > high) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+high+"</span>")
}

function cell_decorator_chk_low(e) {
  var low = $(e).attr("v")
  var line = $(e).parent(".tl")
  var v = line.children("[name$=_chk_value]").attr("v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  if (v < low) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+low+"</span>")
}

function cell_decorator_chk_value(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var low = line.children("[name$=_chk_low]").attr("v")
  var high = line.children("[name$=_chk_high]").attr("v")
  var cl = []
  v = parseInt(v)
  low = parseInt(low)
  high = parseInt(high)
  if ((v > high) || (v < low)) {
    cl.push("highlight")
  }
  $(e).html("<span class='"+cl.join(" ")+"'>"+v+"</span>")
}

function cell_decorator_action_pid(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  var s = "<a>"+v+"</a>"
  $(e).html(s)
  $(e).bind('click', function(){
    var line = $(e).parent(".tl")
    var hostname = line.children("[name$=_hostname]").attr("v")
    var svcname = line.children("[name$=_svcname]").attr("v")
    var begin = line.children("[name$=_begin]").attr("v")
    var end = line.children("[name$=_end]").attr("v")

    var _begin = begin.replace(/ /, "T")
    var d = new Date(+new Date(_begin) - 1000*60*60*24)
    begin = print_date(d)

    var _end = end.replace(/ /, "T")
    var d = new Date(+new Date(_end) + 1000*60*60*24)
    end = print_date(d)

    url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_hostname="+hostname+"&actions_f_pid="+v+"&actions_f_begin=>"+begin+"&actions_f_end=<"+end+"&clear_filters=true"

    $(this).children("a").attr("href", url)
    $(this).children("a").click()
  })
}

function cell_decorator_action_status(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).html("<div class='spinner'></div>")
    return
  }
  cl = ["status_"+v.replace(' ', '_')]
  var line = $(e).parent(".tl")
  var ack = line.children("[name$=_ack]").attr("v")
  if (ack == 1) {
    cl.push("ack_1")
  }
  s = "<div class='"+cl.join(" ")+"'>"+v+"</diV>"
  $(e).html(s)
  if (ack != 1) {
    return
  }
  $(e).bind("mouseout", function(){
    ackpanel(event, false, "")
  })
  $(e).bind("mouseover", function(){
    var acked_date = line.children("[name$=_acked_date]").attr("v")
    var acked_by = line.children("[name$=_acked_by]").attr("v")
    var acked_comment = line.children("[name$=_acked_comment]").attr("v")
    s = "<div>"
    s += "<b>acked by </b>"+acked_by+"<br>"
    s += "<b> on </b>"+acked_date+"<br>"
    s += "<b>with comment:</b><br>"+acked_comment
    s += "</div>"
    ackpanel(event, true, s)
  })
}

function cell_decorator_action_end(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  } else if (v == "1000-01-01 00:00:00") {
    $(e).html("<span class='highlight'>timed out</span>")
    return
  }
  var line = $(e).parent(".tl")
  var id = line.children("[name$=_id]").attr("v")
  s = "<span class='highlight nowrap' id='spin_span_end_"+id+"'>"+v+"</span>"
}

function cell_decorator_action_log(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  s = "<pre>"+v+"</pre>"
  $(e).html(s)
}

function cell_decorator_action(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var status_log = line.children("[name$=status_log]").attr("v")
  cl = []
  if (status_log == "empty") {
    cl.push("metaaction")
  }
  action = v.split(/\s+/).pop()
  if (action in action_img_h) {
    cl.push(action_img_h[action])
  }
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_svc_action_err(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    $(e).empty()
    return
  }
  var line = $(e).parent(".tl")
  var svcname = line.children("[name$=mon_svcname]").attr("v")
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&clear_filters=true"
  s = "<a class='boxed_small bgred clickable' href='"+url+"'>"+v+"</a>"
  $(e).html(s)
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
  $(e).append("<div class='a nowrap'>"+v+"</div>")
  div = $(":first-child", e)
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
  $(e).append("<div class='a nowrap'>"+v+"</div>")
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
  $(e).html("<div class='boxed_small boxed_status boxed_status_"+c+"'>"+v+"</div>")
}

function cell_decorator_svcmon_links(e) {
  var line = $(e).parent(".tl")
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
  $(e).html(d)
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

function cell_decorator_dash_link_comp_tab(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  s = "<div class='comp16 clickable'></div>"
  $(e).html(s)
  if (svcname != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      url = $(location).attr("origin") + "/init/default/ajax_service?node="+svcname+"&tab=tab11&rowid="+id
      toggle_extra(url, id, e, 0)
    })
  } else if (nodename != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      url = $(location).attr("origin") + "/init/ajax_node/ajax_node?node="+nodename+"&tab=tab13&rowid="+id
      toggle_extra(url, id, e, 0)
    })
  }
}

function cell_decorator_dash_link_pkg_tab(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  s = "<div class='pkg16 clickable'></div>"
  $(e).html(s)
  if (svcname != "") {
    $(e).click(function(){
      table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
      span_id = $(e).parent(".tl").attr("spansum")
      id = table_id + "_x_" + span_id
      url = $(location).attr("origin") + "/init/default/ajax_service?node="+svcname+"&tab=tab10&rowid="+id
      toggle_extra(url, id, e, 0)
    })
  }
}

function cell_decorator_dash_link_feed_queue(e) {
  url = $(location).attr("origin") + "/init/feed_queue/feed_queue?feed_queue_f_created=<-15m&clear_filters=true"
  s = "<a class='action16 clickable' href='"+url+"'></a>"
  $(e).html(s)
}

function _cell_decorator_dash_link_actions(svcname) {
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_begin=>-7d&clear_filters=true"
  s = "<a class='action16 clickable' href='"+url+"'></a>"
  return s
}

function _cell_decorator_dash_link_action_error(svcname) {
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&clear_filters=true"
  s = "<a class='alert16 clickable' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_action_error(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_action_error(svcname)
  s += _cell_decorator_dash_link_actions(svcname)
  $(e).html(s)
}

function _cell_decorator_dash_link_svcmon(svcname) {
  url = $(location).attr("origin") + "/init/default/svcmon?svcmon_f_mon_svcname="+svcname+"&clear_filters=true"
  s = "<a class='svc clickable' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_svcmon(e) {
  var line = $(e).parent(".tl")
  var svcname = line.find("[name$=dash_svcname]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_svcmon(svcname)
  $(e).html(s)
}

function _cell_decorator_dash_link_node(nodename) {
  url = $(location).attr("origin") + "/init/nodes/nodes?nodes_f_nodename="+nodename+"&clear_filters=true"
  s = "<a class='node16 clickable' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_node(e) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_node(nodename)
  $(e).html(s)
}

function _cell_decorator_dash_link_checks(nodename) {
  url = $(location).attr("origin") + "/init/checks/checks?checks_f_chk_nodename="+nodename+"&clear_filters=true"
  s = "<a class='check16 clickable' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_checks(e) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  s += _cell_decorator_dash_link_checks(nodename)
  $(e).html(s)
}

function _cell_decorator_dash_link_mac_networks(mac) {
  url = $(location).attr("origin") + "/init/nodenetworks/nodenetworks?nodenetworks_f_mac="+mac+"&clear_filters=true"
  s = "<a class='net16 clickable' href='"+url+"'></a>"
  return s
}

function cell_decorator_dash_link_mac_duplicate(e) {
  var line = $(e).parent(".tl")
  var mac = line.find("[name$=dash_entry]").attr("v").split(" ")[1]
  var s = ""
  s += _cell_decorator_dash_link_mac_networks(mac)
  $(e).html(s)
}

function cell_decorator_dash_link_obsolescence(e, t) {
  var line = $(e).parent(".tl")
  var nodename = line.find("[name$=dash_nodename]").attr("v")
  var s = ""
  url = $(location).attr("origin") + "/init/obsolescence/obsolescence_config?obs_f_obs_type="+t+"&clear_filters=true"
  s = "<a class='"+t+"16 clickable' href='"+url+"'></a>"
  $(e).html(s)
}

function cell_decorator_dash_links(e) {
  var line = $(e).parent(".tl")
  var dash_type = line.find("[name$=dash_type]").attr("v")
  if (dash_type == "action errors") {
    cell_decorator_dash_link_action_error(e)
  } else if ((dash_type == "node warranty expired") ||
             (dash_type == "node without warranty end date") ||
             (dash_type == "node without asset information") ||
             (dash_type == "node close to warranty end") ||
             (dash_type == "node information not updated")) {
    cell_decorator_dash_link_node(e)
  } else if ((dash_type == "check out of bounds") ||
             (dash_type == "check value not updated")) {
    cell_decorator_dash_link_checks(e)
  } else if (dash_type == "mac duplicate") {
    cell_decorator_dash_link_mac_duplicate(e)
  } else if ((dash_type == "service available but degraded") ||
             (dash_type == "service status not updated") ||
             (dash_type == "service configuration not updated") ||
             (dash_type == "service frozen") ||
             (dash_type == "flex error") ||
             (dash_type == "service unavailable")) {
    cell_decorator_dash_link_svcmon(e)
  } else if (dash_type == "feed queue") {
    cell_decorator_dash_link_feed_queue(e)
  } else if (dash_type.indexOf("os obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "os")
  } else if (dash_type.indexOf("obsolescence") >= 0) {
    cell_decorator_dash_link_obsolescence(e, "hw")
  } else if (dash_type.indexOf("comp") == 0) {
    cell_decorator_dash_link_comp_tab(e)
  } else if (dash_type.indexOf("package") == 0) {
    cell_decorator_dash_link_pkg_tab(e)
  }
}

function cell_decorator_action_cron(e) {
  var v = $(e).attr("v")
  var l = []
  if (v == 1) {
      l.push("time16")
  }
  $(e).html("<div class='"+l.join(" ")+"'></div>")
}

function cell_decorator_dash_severity(e) {
  var v = $(e).attr("v")
  var l = []
  if (v == 0) {
      l.push("alertgreen")
  } else if (v == 1) {
      l.push("alertorange")
  } else if (v == 2) {
      l.push("alertred")
  } else if (v == 3) {
      l.push("alertdarkred")
  } else {
      l.push("alertblack")
  }
  $(e).html("<div class='"+l.join(" ")+"'>"+v+"</div>")
}

function cell_decorator_form_id(e) {
  var v = $(e).attr("v")
  var s = ""
  url = $(location).attr("origin") + "/init/forms/workflow?wfid="+v+"&clear_filters=true"
  s = "<a class='clickable' href='"+url+"'></a>"
  $(e).html(s)
}

function cell_decorator_run_log(e) {
  var v = $(e).attr("v")
  var s = "<pre>"+v.replace(/ERR:/g, "<span class='err'>ERR:</span>")+"</pre>"
  $(e).html(s)
}

function cell_decorator_run_status(e) {
  var v = $(e).attr("v")
  var s = ""
  var cl = ""
  var _v = ""
  if (v == 0) {
    cl = "check16"
  } else if (v == 1) {
    cl = "nok"
  } else if (v == 2) {
    cl = "na"
  } else if (v == -15) {
    cl = "kill16"
  } else {
    _v = v
  }
  $(e).html("<div class='"+cl+"'>"+_v+"</div>")
}

function cell_decorator_rset_md5(e) {
  var v = $(e).attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).click(function(){
    url = $(location).attr("origin") + "/init/compliance/ajax_rset_md5?rset_md5="+v
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(url, id, this, 0)
  })
}

function T(s) {
  return s
}

function cell_decorator_action_q_ret(e) {
  var v = $(e).attr("v")
  var cl = ["boxed_small"]
  if (v == 0) {
    cl.push("bggreen")
  } else {
    cl.push("bgred")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+v+"</div>"
  $(e).html(s)
}

function cell_decorator_action_q_status(e) {
  var v = $(e).attr("v")
  var st = ""
  var cl = ["boxed_small"]
  if (v == "T") {
    cl.push("bggreen")
    st = T("done")
  } else if (v == "R") {
    cl.push("bgred")
    st = T("running")
  } else if (v == "W") {
    st = T("waiting")
  } else if (v == "Q") {
    st = T("queued")
  } else if (v == "C") {
    cl.push("bgdarkred")
    st = T("cancelled")
  }
  var s = ""
  s = "<div class='"+cl.join(" ")+"'>"+st+"</div>"
  $(e).html(s)
}

function _outdated(s, max_age) {
  if (typeof s === 'undefined') {
    return true
  }
  s = s.replace(/ /, "T")
  var d = new Date(s)
  var now = new Date()
  delta = now - d
  if (delta > max_age*60000) {
    return true
  }
  return false
}

function status_outdated(line) {
  var s = line.children("[cell=1][name$=mon_updated]").attr("v")
  if (typeof s === 'undefined') {
    var s = line.children("[cell=1][name$=_updated]").attr("v")
  }
  return _outdated(s, 15)
}

function cell_decorator_date_no_age(e) {
  v = $(e).attr("v")
  if (typeof v === 'undefined') {
    return
  }
  s = v.split(" ")[0]
  $(e).html(s)
}

function cell_decorator_datetime_no_age(e) {
  $(e).addClass("nowrap")
}

function cell_decorator_datetime_status(e) {
  _cell_decorator_datetime(e, 15)
}

function cell_decorator_datetime_daily(e) {
  _cell_decorator_datetime(e, 60*24)
}

function cell_decorator_datetime_weekly(e) {
  _cell_decorator_datetime(e, 60*24*7)
}

function _cell_decorator_datetime(e, max_age) {
  s = $(e).attr("v")
  if (_outdated(s, max_age)) {
    var cl = " class='nowrap highlight'"
  } else {
    var cl = " class='nowrap'"
  }
  $(e).html("<div"+cl+">"+s+"</div>")
}

function cell_decorator_env(e) {
  if ($(e).attr("v") != "PRD") {
    return
  }
  s = "<div class='b'>PRD</div>"
  $(e).html(s)
}

function cell_decorator_svc_ha(e) {
  if ($(e).attr("v") != 1) {
    $(e).empty()
    return
  }
  s = "<div class='boxed_small'>HA</div>"
  $(e).html(s)
}

function cell_decorator_availstatus(e) {
  var line = $(e).parent(".tl")
  var mon_availstatus = $(e).attr("v")
  if (mon_availstatus=="") {
    return
  }
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
  $(e).html(s)
}

function cell_decorator_overallstatus(e) {
  var line = $(e).parent(".tl")
  var mon_overallstatus = $(e).attr("v")
  if (mon_overallstatus=="") {
    return
  }
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
  $(e).html(s)
}

cell_decorators = {
 "chk_instance": cell_decorator_chk_instance,
 "chk_value": cell_decorator_chk_value,
 "chk_low": cell_decorator_chk_low,
 "chk_high": cell_decorator_chk_high,
 "action": cell_decorator_action,
 "action_pid": cell_decorator_action_pid,
 "action_status": cell_decorator_action_status,
 "action_end": cell_decorator_action_end,
 "action_log": cell_decorator_action_log,
 "action_cron": cell_decorator_action_cron,
 "rset_md5": cell_decorator_rset_md5,
 "run_status": cell_decorator_run_status,
 "run_log": cell_decorator_run_log,
 "form_id": cell_decorator_form_id,
 "action_q_status": cell_decorator_action_q_status,
 "action_q_ret": cell_decorator_action_q_ret,
 "svcname": cell_decorator_svcname,
 "nodename": cell_decorator_nodename,
 "nodename_no_os": cell_decorator_nodename_no_os,
 "svc_action_err": cell_decorator_svc_action_err,
 "availstatus": cell_decorator_availstatus,
 "overallstatus": cell_decorator_overallstatus,
 "chk_type": cell_decorator_chk_type,
 "svcmon_links": cell_decorator_svcmon_links,
 "svc_ha": cell_decorator_svc_ha,
 "env": cell_decorator_env,
 "datetime_weekly": cell_decorator_datetime_weekly,
 "datetime_daily": cell_decorator_datetime_daily,
 "datetime_status": cell_decorator_datetime_status,
 "datetime_no_age": cell_decorator_datetime_no_age,
 "date_no_age": cell_decorator_date_no_age,
 "dash_severity": cell_decorator_dash_severity,
 "dash_links": cell_decorator_dash_links,
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
  $("#table_"+id).find("[cell=1]:visible").each(function(){
    _table_cell_decorator(id, this)
  })
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
  if (to_p.scrollLeft()+ww+1<tw) {
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
    if (this.value.match(/\s+/g)) {
      if (this.value.match(/^\(/)) {return}
      this.value = this.value.replace(/\s+/g, ',')
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
  var query = "set_col_table="+table
  query += "&set_col_field="+column
  query += "&set_col_value="+value
  var url = $(location).attr("origin") + "/init/ajax/ajax_set_user_prefs_column?"+query
  ajax(url, [], "set_col_dummy")
  var t = osvc.tables[id]
  t.format_header()
  t.refresh()
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

function table_init(opts) {
  var t = {
    'need_refresh': false,
    'id': opts['id'],
    'extrarow': opts['extrarow'],
    'extrarow_class': opts['extrarow_class'],
    'checkboxes': opts['checkboxes'],
    'ajax_url': opts['ajax_url'],
    'span': opts['span'],
    'columns': opts['columns'],
    'colprops': opts['colprops'],
    'visible_columns': opts['visible_columns'],
    'child_tables': opts['child_tables'],
    'dataable': opts['dataable'],
    'decorate_cells': function(){
      table_cell_decorator(opts['id'])
    },
    'hide_cells': function(){
      table_hide_cells(this)
    },
    'scroll': function(){
      table_scroll(opts['id'])
    },
    'bind_filter_reformat': function(){
      table_bind_filter_reformat(this)
    },
    'bind_filter_selector': function(){
      table_bind_filter_selector(this)
    },
    'bind_filter_input_events': function(){
      table_bind_filter_input_events(this)
    },
    'bind_refresh': function(){
      table_bind_refresh(this)
    },
    'bind_checkboxes': function(){
      table_bind_checkboxes(this)
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
      table_restripe_lines(opts['id'])
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
    'link': function(){
      table_link(this)
    },
    'add_scrollers': function(){
      table_add_scrollers(this)
    },
    'add_filterbox': function(){
      table_add_filterbox(this)
    },
    'refresh_column_filter': function(c, val){
      table_refresh_column_filter(this, c, val)
    },
    'refresh_column_filters': function(){
      table_refresh_column_filters(this)
    },
    'format_header': function(){
      table_format_header(this)
    },
    'on_change': function(){
      // placeholder to override after table_init()
    },
    'refresh_child_tables': function(){
      for (var i=0; i<this.child_tables.length; i++) {
        var id = this.child_tables[i]
        osvc.tables[id].refresh()
      }
    },
    'insert': function(data){
      table_insert(this, data)
    },
    'refresh': function(){
      table_refresh(this)
    }
  }
  osvc.tables[t.id] = t
  $("#"+t.id).find("select").parent().css("white-space", "nowrap")
  $("#"+t.id).find("select:visible").combobox()

  t.hide_cells()
  t.format_header()
  t.add_filterbox()
  t.add_scrollers()
  t.bind_filter_reformat()
  t.bind_refresh()
  t.bind_link()
  t.scroll_enable()

  if (t.dataable) {
    t.refresh()
  } else {
    t.bind_checkboxes()
    t.hide_cells()
    t.decorate_cells()
    t.bind_filter_selector()
    t.pager()
    t.restripe_lines()
  }
}

