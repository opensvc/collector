$(document).on('click', function(event){
  if(event.which == 2){
    event.preventDefault()
  }
}).on('contextmenu', function(event){
  if ($(event.target).is("canvas")){return}
  event.preventDefault()
})

// Handle pop up exit
$(document).keydown(function(event) {
    if ( event.which == 27 ) {
      $("input:focus").blur()
      $("textarea:focus").blur()
      $("#overlay").empty()
      $(".white_float").hide()
      $(".white_float_input").hide()
      $(".right_click_menu").hide()
      $(".extraline").remove()
      $(".menu").hide("fold")
      $(".menu").find("[id^=sextra]").remove()
      return
    }

    if ($('input').is(":focus")) {
      return
    }
    if ($('textarea').is(":focus")) {
      return
    }

   if (event.which == 83) // s for search
   {
      if (!$('#search_input').is(":focus")) 
        {
          event.preventDefault();
          $('#search_input').val('');
        }
      $('#search_input').focus();
   }
   else if ( event.which == 78 ) { // n for menu, siwth the search functionnality to filter only menu
    if (!$('#search_input').is(":focus")) 
      {
        event.preventDefault();
        $(".header").find(".menu16").parents("ul").first().siblings(".menu").show("fold");
        $('#search_input').val('');
        $('#search_input').focus();
      }
    }
  else if ( event.which == 9 ) // init menu key navigation
  {
    var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
    var entries = menu.find(".menu_entry:visible");
    $(entries[0]).addClass("menu_selected");
  }
  else if ((event.which == 37)||(event.which == 38)) { // Left/Up key function
    var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
    event.preventDefault();
    var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
    var entries = menu.find(".menu_entry:visible");
    var i = 0;
    var prev;
    entries.each(function(){
      i += 1;
      if ($(this).hasClass("menu_selected")) {
        if (i==1) { return; }
        menu.find(".menu_entry").removeClass("menu_selected");
        $(prev).addClass("menu_selected");
        return;
      }
      prev = this;
    });
  }
  else if ((event.which == 39)||(event.which == 40)) { // Right/down function
    var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
    event.preventDefault();
    var entries = menu.find(".menu_entry:visible");
    var i = 0;
    var found = false;
    entries.each(function(){
      i += 1;
      if ($(this).hasClass("menu_selected")) {
        if (i==entries.length) { return; }
        found = true;
        return;
      }
      if (found) {
        menu.find(".menu_entry").removeClass("menu_selected");
        $(this).addClass("menu_selected");
        found = false;
        return;
      }
    });
  }
  else if (is_enter(event)) { // validation in menu function
    var menu = $(".header").find(".menu16").parents("ul").first().siblings(".menu");
    menu.find(".menu_selected:visible").each(function(){
      event.preventDefault();;
      $(this).effect("highlight");
      window.location = $(this).children("a").attr("href");
    })
  }
});

//
// user group tool
//
function bind_user_groups() {
  $("[name=user_group_check]").bind("click", function(){
    var data = {
     'user_id': $(this).attr("user_id"),
     'group_id': $(this).attr("group_id"),
     'membership': $(this).is(":checked")
    }
    var url = $(location).attr("origin") + "/init/ajax_user/call/json/set_user_group"
    $.ajax({
         type: "POST",
         url: url,
         data: data,
         success: function(msg){
         }
    })
  })
}

//
// group hiddenn menu entries tool
//
function bind_group_hidden_menu_entries() {
  $("[name=group_hidden_menu_entry_check]").bind("click", function(){
    var data = {
     'group_id': $(this).attr("group_id"),
     'menu_entry': $(this).attr("menu_entry"),
     'hidden': $(this).is(":checked")
    }
    var url = $(location).attr("origin") + "/init/ajax_group/call/json/set_group_hidden_menu_entry"
    $.ajax({
         type: "POST",
         url: url,
         data: data,
         success: function(msg){
         }
    })
  })
}

//
// tabs
//
function bind_tabs(id, callbacks, active_id) {
  $("#"+id).find('.closetab').click(function () {
    $("#"+id).remove()
  })
  $("#"+id).find('[id^=litab]').click(function () {
    var _id = $(this).attr('id')
    var did = _id.slice(2, _id.length)
    $("#"+id).find('div[id^=tab]').hide()
    $(this).siblings('[id^=litab]').removeClass('tab_active')
    $("#"+id).find('#'+did).show()
    $(this).show().addClass('tab_active')
    if (_id in callbacks) {
      callbacks[_id]()
      delete callbacks[_id]
    }
  })
  $("#"+id).find('#'+active_id).trigger("click")
}



//
// topo
//
function draw_topo(id, data, display) {
  var i=0
  url = $(location).attr("origin") + "/init/topo/call/json/json_topo_data"
  if ("svcnames" in data) {
    if (i==0) {url += '?'}
    else if (i==1) {url += '&'}
    i += 1
    url += "svcnames="+encodeURIComponent(data["svcnames"])
  }
  if ("nodenames" in data) {
    if (i==0) {url += '?'}
    else if (i>0) {url += '&'}
    i += 1
    url += "nodenames="+encodeURIComponent(data["nodenames"])
  }
  if (typeof display !== 'undefined') {
    if (i==0) {url += '?'}
    else if (i>0) {url += '&'}
    i += 1
    url += "display="+encodeURIComponent(display.join(","))
  }
  if ($("#"+id).parents(".overlay").length == 0) {
      _height = $(window).height()-$(".header").outerHeight()-16
      $("#"+id).height(_height)
  }
  $.getJSON(url, function(_data){
    var eid = document.getElementById(id)
    var options = {
      physics: {
        barnesHut: {
          //enabled: true,
          gravitationalConstant: -2500,
          centralGravity: 1,
          springLength: 95,
          springConstant: 0.1,
          damping: 0.5
        }
      },
      clickToUse: false,
      height: _height+'px',
      nodes: {
        size: 32,
        font: {
          face: "arial",
          size: 12
        }
      },
      edges: {
        font: {
          face: "arial",
          size: 12
        }
      }
    }
    var network = new vis.Network(eid, _data, options)
  })
}

function init_topo(id, data, display) {
  $("#"+id).parent().find("input:submit").bind("click", function(){
    var display = []
    $(this).parent().find("input:checked").each(function () {
      display.push($(this).attr("name"))
    })
    draw_topo(id, data, display)
  })
  draw_topo(id, data, display)
}

//
// startup sequence diagram
//
function draw_startup(id, data) {
  var i=0
  url = $(location).attr("origin") + "/init/topo/call/json/json_startup_data"
  if ("svcnames" in data) {
    if (i==0) {url += '?'}
    else if (i==1) {url += '&'}
    i += 1
    url += "svcnames="+encodeURIComponent(data["svcnames"])
  }
  if ("nodenames" in data) {
    if (i==0) {url += '?'}
    else if (i==1) {url += '&'}
    i += 1
    url += "nodenames="+encodeURIComponent(data["nodenames"])
  }
  if ($("#"+id).parents(".overlay").length == 0) {
      _height = $(window).height()-$(".header").outerHeight()-16
      $("#"+id).height(_height)
  }
  $.getJSON(url, function(_data){
    var eid = document.getElementById(id)
    var options = {
      interaction: {
        hover: true
      },
      physics: {
        barnesHut: {
          enabled: true,
          gravitationalConstant: -2500,
          centralGravity: 1,
          springLength: 95,
          springConstant: 0.1,
          damping: 0.5
        }
      },
      clickToUse: false,
      height: _height+'px',
      nodes: {
        size: 32,
        font: {
          face: "arial",
          size: 12
        }
      },
      edges: {
        font: {
          face: "arial",
          size: 12
        }
      }
    }
    var network = new vis.Network(eid, _data, options)
  })
}

function init_startup(id, data) {
  $("#"+id).parent().find("input:submit").bind("click", function(){
    var nodenames = []
    $(this).parent().find("input:checked").each(function () {
      nodenames.push($(this).attr("name"))
    })
    data["nodenames"] = nodenames
    draw_startup(id, data)
  })
  draw_startup(id, data)
}


//
//
//
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
             if (f) {
               f()
             }
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
      _val = val.substring(0, 17)+"..."
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
    if (t.volatile_filters == "") {
      cl = " class='bgred'"
    } else {
      cl = " class='bgblack'"
    }
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

function table_add_filtered_to_visible_columns(t) {
  $("#table_"+t.id).find("[id^="+t.id+"_f_]").each(function(){
    var s = $(this).attr("id")
    var col = s.split("_f_")[1]
    var ckcc = t.id+"_cc_"+col
    var val = $(this).val()
    if (val === "") {
      $("#"+t.id).find("[name="+ckcc+"]").removeAttr("disabled")
      return
    }
    $("#"+t.id).find("[name="+ckcc+"]").attr("disabled", "true")
    if (t.visible_columns.indexOf(col) >= 0) {
      return
    }
    t.visible_columns.push(col)
  })
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

function table_bind_persistent_filter(t) {
  $("#avs"+t.id).bind("change", function() {
    var v = $(this).find("option:selected").val()
    var url = $(location).attr("origin") + "/init/ajax/ajax_select_filter/"+v
    $.ajax({
         type: "POST",
         url: url,
         data: "",
         success: function(msg){
           for (tid in osvc.tables) {
             osvc.tables[tid].refresh()
           }
         }
    })
  })
}

function table_data_to_lines(t, data) {
  var lines = ""
  for (var i=0; i<data.length; i++) {
    var line = ""
    if (t.checkboxes) {
      line += "<td name='"+t.id+"_tools' class='tools'><input value='"+data[i]['checked']+"' type='checkbox' id='"+t.id+"_ckid_"+data[i]['id']+"' name='"+t.id+"_ck'></td>"
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
    lines += "<tr class='tl h' spansum='"+data[i]['spansum']+"' cksum='"+data[i]['cksum']+"'>"+line+"</tr>"
  }
  return lines
}

function table_refresh(t) {
    if ($("#"+t.id).length > 0 && !$("#"+t.id).is(":visible")) {
        return
    }
    if ($("#refresh_"+t.id).length > 0 && $("#refresh_"+t.id).hasClass("spinner")) {
        t.need_refresh = true
        return
    } else {
        t.set_refresh_spin()
    }

    // move open tabs to overlay to preserve what was in use
    if ($("#"+t.id).find(".extraline").children("td").children("table").length > 0) {
      $("#overlay").empty().hide()
      $("#"+t.id).find(".extraline").children("td").children("table").parent().each(function() {
        var e = $("<div></div>")
        e.attr("id", $(this).attr("id"))
        e.append($(this).children())
        $("#overlay").append(e)
      })
      $("#overlay").hide().show("scale")
    }

    var data = {
      "table_id": t.id,
      "visible_columns": t.visible_columns.join(',')
    }
    if (t.volatile_filters != "") {
      data["volatile_filters"] = true
    }
    data[t.id+"_page"] = $("#"+t.id+"_page").val()
    for (c in t.colprops) {
      var current = $("#"+t.id+"_f_"+c).val()
      if ((current != "") && (typeof current !== 'undefined')) {
        data[t.id+"_f_"+c] = current
      } else if (t.colprops[c].force_filter != "") {
        data[t.id+"_f_"+c] = t.colprops[c].force_filter
      }
    }
    if (t.dataable) {
      var ajax_interface = "data"
    } else {
      var ajax_interface = "line"
    }
    $.ajax({
         type: "POST",
         url: t.ajax_url+"/"+ajax_interface,
         data: data,
         context: document.body,
         beforeSend: function(req){
             $("#"+t.id).find(".nodataline>td").text(T("Loading data"))
         },
         success: function(msg){
             // disable DOM insert event trigger for perf
             t.need_refresh = false
             t.scroll_disable_dom()
             $("#table_"+t.id).children().children("tr.extraline").remove()

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

             // detach old lines
             var old_lines = $("<tbody></tbody>").append($("#table_"+t.id).children("tbody").children(".tl").detach())

             // insert new lines
             tbody = $("#table_"+t.id).children("tbody")
             tbody.append(msg)

             tbody.children(".tl").each(function(){
               var new_line = $(this)
               var cksum = new_line.attr("cksum")
               var old_line = $("[cksum="+cksum+"]", old_lines)
               if (old_line.length == 0) {
                   // this is a new line : highlight
                   new_line.addClass("tohighlight")
                   return
               } else if (old_line.length > 1) {
                   //alert("The table key is not unique. Please contact the editor.")
                   return
               }
               for (i=0; i<old_line.children().length; i++) {
                 var new_cell = $(":nth-child("+i+")", new_line)
                 if (!new_cell.is(":visible")) {
                   continue
                 }
                 var old_cell = $(":nth-child("+i+")", old_line)
                 if (old_cell.attr("v") == new_cell.attr("v")) {
                   continue
                 }
                 new_cell.addClass("tohighlight")
               }
             })

             old_lines.remove()

             // clear mem refs
             cksum = null
             msg = null
             new_cell = null
             old_cell = null
             new_line = null
             old_line = null
             old_lines = null

             try {
               _table_pager(t.id, pager["page"], pager["perpage"], pager["start"], pager["end"], pager["total"])
             } catch(e) {}
             t.add_filtered_to_visible_columns()
             t.bind_checkboxes()
             t.bind_filter_selector()
             t.bind_action_menu()
             t.restripe_lines()
             t.hide_cells()
             t.decorate_cells()
             t.unset_refresh_spin()
             t.relocate_extra_rows()

             t.scroll_enable_dom()

             tbody.find(".tohighlight").removeClass("tohighlight").effect("highlight", 1000)

             t.refresh_child_tables()
             t.on_change()

             if (t.need_refresh) {
               $("#refresh_"+t.id).trigger("click")
             }
         }
    })
}

function table_insert(t, data) {
    var query="volatile_filters="+t.volatile_filters
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
             t.bind_action_menu()
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

function table_ajax_submit(url, id, additional_inputs, input_name, additional_input_name) {
    var t = osvc.tables[id]

    // close dialogs
    $("#"+t.id).find(".white_float").hide()
    $("#"+t.id).find(".white_float_input").hide()

    var inputs = ['tableid', id+"_page", id+"_perpage"]
    var s = inputs.concat(additional_inputs).concat(getIdsByName(input_name))
    $("#"+t.id).find("[name="+additional_input_name+"]").each(function(){s.push(this.id)})
    $("#"+t.id).find("input[id^="+t.id+"_f_]").each(function(){s.push(this.id)})
    var query="table_id="+t.id
    for (i=0; i<s.length; i++) {
        if (i > 0) {query=query+"&"}
        try {
            query=query+encodeURIComponent(s[i])+"="+encodeURIComponent(document.getElementById(s[i]).value);
        } catch(e) {}
    }
    if (t.volatile_filters != "") {
      query += "&volatile_filters=true"
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
    var toolbar = ""
    line.children("td.tools").each(function(){
      toolbar = "<td class='tools'></td>"
    })
    if (line.next().children("#"+id).attr("id")==id) {
        line.next().remove()
    }
    line.after("<tr class='extraline'>"+toolbar+"<td id="+id+" colspan="+ncols+"></td></tr>")
    $("#"+id).toggleClass("spinner")
    sync_ajax(url, [], id, function(){
      $("#"+id).removeClass("spinner")
      $("#"+id).children().each(function(){$(this).width($(window).width()-$(this).children().position().left-20)})
    })
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

function ackpanel(e, show, s){
    var pos = get_pos(e)
    if (show) {
        $("#ackpanel").css({"left": pos[0] + "px", "top": pos[1] + "px"});
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

function filter_submit(id,k,v){
  $("#"+k).val(v)
  window["ajax_submit_"+id]()
  osvc.tables[id].refresh_column_filters()
};

function table_insert_bookmark(t, bookmark) {
  s = "<p><a name='bookmark' class='bookmark16'>"+bookmark+"</a><a style='float:right' class='del16'></a></p>"
  $('#'+t.id).find("[name^=bookmark].white_float").children("span").append(s)
  t.bind_bookmark()
}

function table_bind_bookmark(t) {
  $('[name=bookmarks'+t.id+']').find(".del16").bind("click", function() {
    var bookmark = $(this).siblings("[name=bookmark]").text()
    var url = $(location).attr("origin") + "/init/ajax/del_bookmark"
    var query = "table_id="+t.id+"&bookmark="+encodeURIComponent(bookmark)
    var line = $(this).parents("p").first()
    $.ajax({
         type: "POST",
         url: url,
         data: query,
         success: function(msg){
           line.remove()
           $(".white_float").hide()
           $(".white_float_input").hide()
         }
    })
  })
  $('[name=bookmarks'+t.id+']').find("[name=bookmark]").bind("click", function() {
    var bookmark = $(this).text()
    var url = $(location).attr("origin") + "/init/ajax/load_bookmark"
    var query = "table_id="+t.id+"&bookmark="+encodeURIComponent(bookmark)
    $.ajax({
         type: "POST",
         url: url,
         data: query,
         success: function(msg){
           var l = $.parseJSON(msg)
           for (var i=0; i<t.columns.length; i++) {
             var k = t.id + "_f_" + t.columns[i]
             $("#"+k).val("")
           }
           for (var i=0; i<l.length; i++) {
             var data = l[i]
             var k = t.id + "_f_" + data['col_name'].split('.')[1]
             var v = data['col_filter']
             $("#"+k).val(v)
           }
           $(".white_float").hide()
           $(".white_float_input").hide()
           t.format_header()
           t.refresh()
         }
    })
  })
  $('[name=bookmarks'+t.id+']').find("[id^=bookmark_name_input]").bind("keyup", function(event) {
    if (!is_enter(event)) {
      return
    }
    var url = $(location).attr("origin") + "/init/ajax/save_bookmark"
    var bookmark = $(this).val()
    var query = "table_id="+t.id+"&bookmark="+encodeURIComponent(bookmark)
    $.ajax({
         type: "POST",
         url: url,
         data: query,
         success: function(msg){
           t.insert_bookmark(bookmark)
           $(".white_float").hide()
           $(".white_float_input").hide()
         }
    })
  })
}

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
        var data = {}
        for (c in t.colprops) {
          var current = $("#"+t.id+"_f_"+c).val()
          if ((current != "") && (typeof current !== 'undefined')) {
            data[t.id+"_f_"+c] = current
          } else if (t.colprops[c].force_filter != "") {
            data[t.id+"_f_"+c] = t.colprops[c].force_filter
          }
        }
        if (t.volatile_filters != "") {
          data["volatile_filters"] = true
        }
        data[input.attr('id')] = input.val()
        var dest = input.siblings("[id^="+t.id+"_fc_]")
        _url = url + col
        $.ajax({
         type: "POST",
         url: _url,
         data: data,
         context: document.body,
         success: function(msg){
           dest.html(msg)
         }
        })
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
    _url = url + col
    sync_ajax(_url, [k], ck, f)
  })
  t.bind_filter_reformat()
}

function table_bind_action_menu(t) {
  $("#table_"+t.id).find("[name="+t.id+"_tools]").each(function(){
    $(this).bind("mouseup", function(event) {
      table_action_menu(t, event)
    })
    $(this).bind("click", function() {
      $("#fsr"+t.id).hide()
      $(".menu").hide("fold")
    })
  })
}

function table_bind_filter_selector(t) {
  $("#table_"+t.id).find("[cell=1]").each(function(){
    $(this).bind("mouseup", function(event) {
      cell = $(event.target)
      if (typeof cell.attr("v") === 'undefined') {
        cell = cell.parents("[cell=1]").first()
      }
      filter_selector(t.id, event, cell.attr('name'), cell.attr('v'))
    })
    $(this).bind("click", function() {
      $("#fsr"+t.id).hide()
      $("#am_"+t.id).remove()
      $(".menu").hide("fold")
    })
  })
}

function table_action_menu_click_animation(t) {
  var src = $("#am_"+t.id)
  var dest = $(".header").find("[href$=action_queue]")
  var destp = dest.position()
  src.animate({
   top: destp.top,
   left: destp.left,
   opacity: "toggle",
   height: ["toggle", "swing"],
   width: ["toggle", "swing"]
  }, 1500, function(){dest.parent().effect("highlight")})
}

function table_action_menu_param_moduleset(t) {
  var s = ""
  $.ajax({
    async: false,
    type: "POST",
    url: $(location).attr("origin") + "/init/compliance/call/json/comp_get_all_moduleset",
    data: "",
    success: function(data){
      for (var i=0; i<data.length; i++) {
        var e = data[i]
        s += "<div><input type=checkbox otype='moduleset' oid="+e[0]+" oname='"+e[1]+"'>"+e[1]+"</div>"
      }
    }
  })
  return "<p class='clickable b' onclick='$(this).next().toggle()'>--moduleset</p><div class='panselector10 hidden'>"+s+"</div>"
}

function table_action_menu_param_module(t) {
  var s = ""
  $.ajax({
    async: false,
    type: "POST",
    url: $(location).attr("origin") + "/init/compliance/call/json/comp_get_all_module",
    data: "",
    success: function(data){
      for (var i=0; i<data.length; i++) {
        var e = data[i]
        s += "<div><input type=checkbox otype='module' oid="+e[0]+" oname='"+e[1]+"'>"+e[1]+"</div>"
      }
    }
  })
  return "<p class='clickable b' onclick='$(this).next().toggle()'>--module</p><div class='panselector10 hidden'>"+s+"</div>"
}

function table_action_menu_post_data(t, data, confirmation) {
    action = data[0]['action']
    if (!(confirmation==true)) {
      s = ""
      $("#am_"+t.id).find("li.right").remove()
      $("#am_"+t.id).find("li[action="+action+"]").each(function(){
        $(this).addClass("b")
        $(this).unbind("click")
        $(this).siblings().remove()
        $(this).parent("ul").parent().unbind("click")

        // action parameters
        var params = $(this).attr("params")
        if (typeof params !== "undefined") {
          params = params.split(",")
          for (var i=0; i<params.length; i++) {
            var param = params[i]
            try {
              s += t["action_menu_param_"+param]()
            } catch(err) {}
          }
        }
      })
      s += "<hr>"
      s += "<div>"+T("Are you sure ?")+"</div><br>"
      s += "<div class='check16 float clickable' name='yes'>"+T("Yes")+"</div>"
      s += "<div class='nok float clickable' name='no'>"+T("No")+"</div>"
      $("#am_"+t.id).find("ul").last().append(s)
      $("#am_"+t.id).find("[name=yes]").bind("click", function(){
        $(this).unbind("click")
        $(this).removeClass("check16")
        $(this).addClass("spinner")
        table_action_menu_post_data(t, data, true)
      })
      $("#am_"+t.id).find("[name=no]").bind("click", function(){$("#am_"+t.id).remove()})
      return
    }
    var params = {}
    $("#am_"+t.id).find("input[otype]:checked").each(function(){
      otype = $(this).attr("otype")
      oname = $(this).attr("oname")
      if (!(otype in params)) {
        params[otype] = []
      }
      params[otype].push(oname)
    })
    for (otype in params) {
      if (params[otype].length > 0) {
        for (var i=0; i<data.length; i++) {
          data[i][otype] = params[otype].join(",")
        }
      }
    }
    table_action_menu_click_animation(t)
    $.ajax({
      //async: false,
      type: "POST",
      url: $(location).attr("origin") + "/init/action_menu/call/json/json_action",
      data: {"data": JSON.stringify(data)},
      success: function(msg){
        menu_action_status(msg)
      }
    })
}

function table_action_menu(t, e){
  // drop the previous action menu
  $("#am_"+t.id).remove()
  if(e.button != 2) {
    return
  }
  if (typeof t.action_menu === "undefined") {
    return
  }
  $(".right_click_menu").hide()

  var s = ""

  // format the tools menu
  var tm = ""
  if ("nodes" in t.action_menu) {
    tm += table_tools_menu_nodes(t)
  }
  if ("services" in t.action_menu) {
    tm += table_tools_menu_svcs(t)
  }
  if (("nodes" in t.action_menu) || ("services" in t.action_menu)) {
    tm += tool_topo(t)
  }
  if (tm != "") {
    s += "<h3 class='line'><span>"+T("Tools")+"</span></h3>" + s
    s += tm
  }

  // format the action menu
  var am = ""
  if ("nodes" in t.action_menu) {
    am += table_action_menu_node(t, e)
    am += table_action_menu_nodes(t)
    am += table_action_menu_nodes_all(t, e)
  }
  if ("services" in t.action_menu) {
    am += table_action_menu_svc(t, e)
    am += table_action_menu_svcs(t)
    am += table_action_menu_svcs_all(t, e)
  }
  if ("resources" in t.action_menu) {
    am += table_action_menu_resource(t, e)
    am += table_action_menu_resources(t)
    am += table_action_menu_resources_all(t, e)
  }
  if ("modules" in t.action_menu) {
    am += table_action_menu_module(t, e)
    am += table_action_menu_modules(t)
    am += table_action_menu_modules_all(t, e)
  }
  if (am != "") {
      s += "<h3 class='line'><span>"+T("Actions")+"</span></h3>"
      s += am
  }

  if (s == "") {
    return
  }
  s = "<div id='am_"+t.id+"' class='white_float action_menu'><ul>"+s+"</ul></div>"

  // position the popup at the mouse click
  var pos = get_pos(e)
  $("#"+t.id).append(s)
  $("#am_"+t.id).css({"left": pos[0] + "px", "top": pos[1] + "px"})

  // bind action click triggers
  $("#am_"+t.id).find("[scope=module]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_module_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=modules]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_modules_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=modules_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_modules_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resource]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resource_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resources]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resources_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=resources_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_resources_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svc]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svc_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svcs]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svcs_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=svcs_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_svcs_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=node]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_node_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=nodes]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_nodes_data(t, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })
  $("#am_"+t.id).find("[scope=nodes_all]").bind("click", function(){
    var action = $(this).attr("action")
    var data = table_action_menu_get_nodes_all_data(t, e, action)
    if (data.length==0) {
      return
    }
    table_action_menu_post_data(t, data)
  })

  // display actions only for the clicked section
  var sections = $("#am_"+t.id).children("ul").children("li")
  sections.addClass("right")
  sections.children("ul").hide()
  sections.bind("click", function(){
    var v = $(this).children("ul").is(":visible")
    sections.removeClass("down")
    sections.addClass("right")
    sections.children("ul").hide()
    if (!v) {
      $(this).children("ul").show()
      $(this).removeClass("right")
      $(this).addClass("down")
    }
  })
}

function table_action_menu_get_nodes_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var name = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var col = name.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = col
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idx = cols.indexOf(col)
           var sigs = []
           for (i=0; i<lines.length; i++) {
             var sig = lines[i]["cells"][idx]
             if (sigs.indexOf(sig) >= 0) { continue }
             sigs.push(sig)
             data.push({nodename: lines[i]["cells"][idx], action: action})
           }
         }
    })
    return data
}

function table_action_menu_get_svcs_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           var sigs = []
           for (i=0; i<lines.length; i++) {
             var sig = lines[i]["cells"][idxnode]+"--"+lines[i]["cells"][idxsvc]
             if (sigs.indexOf(sig) >= 0) { continue }
             sigs.push(sig)
             data.push({nodename: lines[i]["cells"][idxnode], svcname: lines[i]["cells"][idxsvc], action: action})
           }
         }
    })
    return data
}

function table_action_menu_get_resources_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var rid = line.find("td[cell=1][name$=_rid]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var colrid = rid.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc+","+rid
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           idxrid = cols.indexOf(colrid)
           for (i=0; i<lines.length; i++) {
             data.push({
               nodename: lines[i]["cells"][idxnode],
               svcname: lines[i]["cells"][idxsvc],
               rid: lines[i]["cells"][idxrid],
               action: action
             })
           }
         }
    })
    return data
}

function table_action_menu_get_modules_all_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("name")
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").first().attr("name")
    var module = line.find("td[cell=1][name$=_run_module]").first().attr("name")
    var colnode = nodename.replace(/.*_c_/, "")
    var colsvc = svcname.replace(/.*_c_/, "")
    var colmodule = module.replace(/.*_c_/, "")
    var url = t.ajax_url+"/data"
    var vars = {}
    vars["table_id"] = t.id
    vars["visible_columns"] = colnode+","+colsvc+","+colmodule
    vars[t.id+"_page"] = 0
    var data = []
    $.ajax({
         async: false,
         type: "POST",
         url: url,
         data: vars,
         success: function(msg){
           try {
             var _data = $.parseJSON(msg)
             var lines = _data['table_lines']
           } catch(e) {
             return []
           }
           if (t.extrarow) {
             var cols = ["extra"].concat(t.columns)
           } else {
             var cols = t.columns
           }
           idxnode = cols.indexOf(colnode)
           idxsvc = cols.indexOf(colsvc)
           idxmodule = cols.indexOf(colmodule)
           for (i=0; i<lines.length; i++) {
             data.push({
               nodename: lines[i]["cells"][idxnode],
               svcname: lines[i]["cells"][idxsvc],
               module: lines[i]["cells"][idxmodule],
               action: action
             })
           }
         }
    })
    return data
}

function table_action_menu_get_nodes_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var nodenames = []
    lines.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodname],td[cell=1][name$=hostname]").each(function(){
      nodename = $(this).attr("v")
      var d = {'nodename': nodename, 'action': action}
      if (nodenames.indexOf(nodename) < 0) {
        nodenames.push(nodename)
        data.push({'nodename': nodename, 'action': action})
      }
    })
    return data
}

function table_action_menu_get_node_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'action': action}]
    return data
}

function table_action_menu_get_svcs_data_with_node(t, action) {
    var d = table_action_menu_get_svcs_data(t, action)
    var n = []
    for (i=0; i<d.length; i++) {
        if (d[i]["nodename"] != "") {
            n.push(d[i])
        }
    }
    return n
}

function table_action_menu_get_svcs_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=disk_nodename],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        nodename = ""
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name],td[cell=1][name$=disk_svcname]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        return []
      }
      var i = nodename+"--"+svcname
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push({"nodename": nodename, "svcname": svcname, "action": action})
      }
    })
    return data
}

function table_action_menu_get_svc_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'svcname': svcname, 'action': action}]
    return data
}

function table_action_menu_get_modules_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        return
      }
      var module = $(this).find("td[cell=1][name$=_run_module]").attr("v")
      if ((typeof module === "undefined")||(module=="")) {
        return
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        var i = nodename+"--"+svcname+"--"+module
        d = {"nodename": nodename, "module": module, "action": action}
      } else {
        var i = nodename+"--"+module
        d = {"nodename": nodename, "svcname": svcname, "module": module, "action": action}
      }
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push(d)
      }
    })
    return data
}

function table_action_menu_get_module_data(t, e, action) {
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var module = line.find("td[cell=1][name$=_run_module]").first().attr("v")
    if ((typeof module === "undefined")||(module=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'module': module, 'action': action}]
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return data
    }
    data[0]['svcname'] = svcname
    return data
}

function table_action_menu_get_resources_data(t, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var data = []
    var index = []
    lines.each(function(){
      var nodename = $(this).find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").attr("v")
      if ((typeof nodename === "undefined")||(nodename=="")) {
        return
      }
      var svcname = $(this).find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").attr("v")
      if ((typeof svcname === "undefined")||(svcname=="")) {
        return
      }
      var rid = $(this).find("td[cell=1][name$=_rid]").attr("v")
      if ((typeof rid === "undefined")||(rid=="")) {
        return
      }
      var i = nodename+"--"+svcname+"--"+rid
      if (index.indexOf(i)<0) {
        index.push(i)
        data.push({"nodename": nodename, "svcname": svcname, "rid": rid, "action": action})
      }
    })
    return data
}

function table_action_menu_get_resource_data(t, e, action) {
    var lines = $("[id^="+t.id+"_ckid_]:checked").parent().parent()
    var cell = $(e.target)
    var line = cell.parents(".tl").first()
    var nodename = line.find("td[cell=1][name$=nodename],td[cell=1][name$=mon_nodname],td[cell=1][name$=hostname]").first().attr("v")
    if ((typeof nodename === "undefined")||(nodename=="")) {
      return []
    }
    var svcname = line.find("td[cell=1][name$=svcname],td[cell=1][name$=svc_name]").first().attr("v")
    if ((typeof svcname === "undefined")||(svcname=="")) {
      return []
    }
    var rid = line.find("td[cell=1][name$=_rid]").first().attr("v")
    if ((typeof rid === "undefined")||(rid=="")) {
      return []
    }
    var data = [{'nodename': nodename, 'svcname': svcname, 'rid': rid, 'action': action}]
    return data
}

function menu_action_status(msg){
  var s = "accepted: "+msg.accepted+", rejected: "+msg.rejected
  if (msg.factorized>0) {
    s = "factorized: "+msg.factorized+", "+s
  }
  $(".flash").html(s).slideDown().effect("fade", 5000)
}

function table_action_menu_modules_all(t, e){
  var data = table_action_menu_get_module_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on all modules")+table_action_menu_module_entries(t, "modules_all")+"</li>"
  return s
}

function table_action_menu_module(t, e){
  var data = table_action_menu_get_module_data(t, e)
  if (data.length==0) {
    return ""
  }
  if ('svcname' in data[0]) {
    var s = "<li class='clickable'>"+T("Actions on module <b>{{module}}</b> on <b>{{svcname}}</b> service instance on node <b>{{nodename}}</b>", data[0])+table_action_menu_module_entries(t, "module")+"</li>"
  } else {
    var s = "<li class='clickable'>"+T("Actions on module <b>{{module}}</b> on node <b>{{nodename}}</b>", data[0])+table_action_menu_module_entries(t, "module")+"</li>"
  }
  return s
}

function table_action_menu_modules(t){
  var data = table_action_menu_get_modules_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on selected modules")+" (<b>"+data.length+"</b>)"+table_action_menu_module_entries(t, "modules")+"</li>"
  return s
}

function table_action_menu_resources_all(t, e){
  var data = table_action_menu_get_resource_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on all resources")+table_action_menu_resource_entries(t, "resources_all")+"</li>"
  return s
}

function table_action_menu_resource(t, e){
  var data = table_action_menu_get_resource_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on resource <b>{{rid}}</b> of <b>{{svcname}}</b> service instance on node <b>{{nodename}}</b>", data[0])+table_action_menu_resource_entries(t, "resource")+"</li>"
  return s
}

function table_action_menu_resources(t){
  var data = table_action_menu_get_resources_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on selected resources")+" (<b>"+data.length+"</b>)"+table_action_menu_resource_entries(t, "resources")+"</li>"
  return s
}

function table_action_menu_svcs_all(t, e){
  var data = table_action_menu_get_svc_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on all service instances")+table_action_menu_svc_entries(t, "svcs_all")+"</li>"
  return s
}

function table_action_menu_svc(t, e){
  var data = table_action_menu_get_svc_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on <b>{{svcname}}</b> service instance on node <b>{{nodename}}</b>", data[0])+table_action_menu_svc_entries(t, "svc")+"</li>"
  return s
}

function table_action_menu_svcs(t){
  var data = table_action_menu_get_svcs_data_with_node(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on selected service instances")+" (<b>"+data.length+"</b>)"+table_action_menu_svc_entries(t, "svcs")+"</li>"
  return s
}

function table_action_menu_nodes_all(t, e){
  var data = table_action_menu_get_node_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on all nodes")+table_action_menu_node_entries(t, "nodes_all")+"</li>"
  return s
}

function table_action_menu_node(t, e){
  var data = table_action_menu_get_node_data(t, e)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on node")+" <b>"+data[0]['nodename']+"</b>"+table_action_menu_node_entries(t, "node")+"</li>"
  return s
}

function create_overlay() {
  e = $("#overlay")
  if (e.length == 0) {
    $("body").append("<div class='white_float hidden' id='overlay'></div>")
  }
  $(window).resize(function(){
    resize_overlay()
    resize_extralines()
  })
  $("#overlay").bind("DOMSubtreeModified", function(){
    resize_overlay()
  })
}

function resize_overlay() {
  _resize_overlay()
  e.find("img").one("load", function(){_resize_overlay()})
}

function _resize_overlay() {
  e = $("#overlay")
  if (e.is(":empty")) {
    e.hide()
    return
  }
  e.show()
  e.css({
   'overflow': 'auto',
   'position': 'fixed',
   'height': $(window).height()-60,
   'width': $(window).width()-60,
   'top': ($(window).height()-e.height())/2,
   'left': ($(window).width()-e.width())/2
  })
}

function resize_extralines() {
  $(".extraline>td>table").each(function(){$(this).width($(window).width()-$(this).children().position().left-20)})
}

function trigger_tool_topo(tid) {
  var t = osvc.tables[tid]
  var datasvc = table_action_menu_get_svcs_data(t)
  var datanode = table_action_menu_get_nodes_data(t)
  if (datasvc.length+datanode.length==0) {
    return ""
  }
  var nodenames = new Array()
  for (i=0;i<datanode.length;i++) {
    nodenames.push(datanode[i]['nodename'])
  }
  var svcnames = new Array()
  for (i=0;i<datasvc.length;i++) {
    svcnames.push(datasvc[i]['svcname'])
  }
  url = '/init/topo/ajax_topo?display=nodes,services,countries,cities,buildings,rooms,racks,enclosures,hvs,hvpools,hvvdcs'
  url += '&svcnames=('+svcnames.join(",")+")"
  url += '&nodenames=('+nodenames.join(",")+")"
  sync_ajax(url, [], 'overlay', function(){})
}

function trigger_tool_nodesantopo(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  sync_ajax('/init/ajax_node/ajax_nodes_stor?nodes='+nodes.join(","), [], 'overlay', function(){})
}

function trigger_tool_nodesysrepdiff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length<2) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  sysrepdiff("overlay", {"nodes": nodes.join(",")})
  $("#overlay").width($("#overlay").css("max-width"))
}

function trigger_tool_nodesysrep(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  sysrep("overlay", {"nodes": nodes.join(",")})
  $("#overlay").width($("#overlay").css("max-width"))
}

function trigger_tool_svcdiff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_svcs_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['svcname'])
  }
  sync_ajax('/init/nodediff/ajax_svcdiff?node='+nodes.join(","), [], 'overlay', function(){})
}

function trigger_tool_nodediff(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  sync_ajax('/init/nodediff/ajax_nodediff?node='+nodes.join(","), [], 'overlay', function(){})
}

function trigger_tool_grpprf(tid) {
  var t = osvc.tables[tid]
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var nodes = new Array()
  for (i=0;i<data.length;i++) {
    nodes.push(data[i]['nodename'])
  }
  sync_ajax('/init/nodes/ajax_grpprf?node='+nodes.join(","), [], 'overlay', function(){})
}

function tool_nodediff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable common16' onclick='trigger_tool_nodediff(\""+t.id+"\")'>"+T("Nodes differences")+"</div>"
}

function tool_nodesantopo(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable hd16' onclick='trigger_tool_nodesantopo(\""+t.id+"\")'>"+T("Nodes SAN topology")+"</div>"
}

function tool_nodesysrepdiff(t, data) {
  if (data.length<2) {
    return ""
  }
  return "<div class='clickable common16' onclick='trigger_tool_nodesysrepdiff(\""+t.id+"\")'>"+T("Nodes sysreport differences")+"</div>"
}

function tool_nodesysrep(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable log16' onclick='trigger_tool_nodesysrep(\""+t.id+"\")'>"+T("Nodes sysreport")+"</div>"
}

function tool_grpprf(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable spark16' onclick='trigger_tool_grpprf(\""+t.id+"\")'>"+T("Nodes performance")+"</div>"
}

function tool_svcdiff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable common16' onclick='trigger_tool_svcdiff(\""+t.id+"\")'>"+T("Services differences")+"</div>"
}

function tool_topo(t) {
  var datasvc = table_action_menu_get_svcs_data(t)
  var datanode = table_action_menu_get_nodes_data(t)
  if (datasvc.length+datanode.length==0) {
    return ""
  }
  return "<div class='clickable dia16' onclick='trigger_tool_topo(\""+t.id+"\")'>"+T("Topology")+"</div>"
}

function table_tools_menu_nodes(t){
  var data = table_action_menu_get_nodes_data(t)
  var s = ""
  s += tool_nodediff(t, data)
  s += tool_nodesysrep(t, data)
  s += tool_nodesysrepdiff(t, data)
  s += tool_nodesantopo(t, data)
  s += tool_grpprf(t, data)
  return s
}

function table_tools_menu_svcs(t){
  var data = table_action_menu_get_svcs_data(t)
  var s = ""
  s += tool_svcdiff(t, data)
  return s
}

function table_action_menu_nodes(t){
  var data = table_action_menu_get_nodes_data(t)
  if (data.length==0) {
    return ""
  }
  var s = "<li class='clickable'>"+T("Actions on selected nodes")+" (<b>"+data.length+"</b>)"+table_action_menu_node_entries(t, "nodes")+"</li>"
  return s
}

function table_action_menu_module_entries(t, scope){
  return table_action_menu_single_entries(t, "modules", scope)
}

function table_action_menu_resource_entries(t, scope){
  return table_action_menu_single_entries(t, "resources", scope)
}

function table_action_menu_svc_entries(t, scope){
  return table_action_menu_single_entries(t, "services", scope)
}

function table_action_menu_node_entries(t, scope){
  return table_action_menu_single_entries(t, "nodes", scope)
}

function table_action_menu_single_entries(t, action_menu_key, scope){
  s = "<ul>"
  for (i=0; i<t.action_menu[action_menu_key].length; i++) {
    var e = t.action_menu[action_menu_key][i]
    try {
      var params = " params='"+e.params.join(",")+"'"
    } catch(err) {
      var params = ""
    }
    s += "<li class='clickable "+e['class']+"' action='"+e.action+"' scope='"+scope+"'"+params+">"+e.title+"</li>"
  }
  s += "</ul>"
  return s
}

function get_pos(e) {
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
  return [posx, posy]
}

function get_selected() {
    if (window.getSelection) {
        return window.getSelection().toString();
    } else if (document.getSelection) {
        return document.getSelection().toString();
    } else {
        var selection = document.selection && document.selection.createRange();
        if (selection.text) {
            return selection.text.toString();
        }
        return "";
    }
    return "";
}

function filter_selector(id,e,k,v){
  if(e.button != 2) {
    return
  }
  $("#am_"+id).remove()
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
  var pos = get_pos(e)
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
  $("#fsr"+id).css({"left": pos[0] + "px", "top": pos[1] + "px"})
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
  if ($("#link_val_"+t.id).is(":visible")) {
    $("#link_val_"+t.id).hide()
    return
  }
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
  $("#link_val_"+t.id).children("textarea").val(url+args).attr("readonly", "on").select()
  $("#link_val_"+t.id).show()
  $("#link_val_"+t.id).children("textarea").select()
  keep_inside($("#link_val_"+t.id))
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

function cell_decorator_network(e) {
  var v = $(e).attr("v")
  $(e).html("<span class='clickable'>"+v+"</span>")
  $(e).click(function(){
    var line = $(this).parent(".tl")
    var net_id = line.children("[name$=_c_id]").attr("v")
    url = $(location).attr("origin") + "/init/networks/segments/"+net_id
    toggle_extra(url, net_id, $(this), 0)
  })
}

function cell_decorator_chk_instance(e) {
  var v = $(e).attr("v")
  var line = $(e).parent(".tl")
  var chk_type = line.children("[name$=_chk_type]").attr("v")
  if (chk_type == "mpath") {
    url = $(location).attr("origin") + "/init/disks/disks?disks_f_disk_id="+v+"&volatile_filters=true"
    s = "<a class='hd16' href='"+url+"' target='_blank'>"+v+"</a>"
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

    url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_hostname="+hostname+"&actions_f_pid="+v+"&actions_f_begin=>"+begin+"&actions_f_end=<"+end+"&volatile_filters=true"

    $(this).children("a").attr("href", url)
    $(this).children("a").attr("target", "_blank")
    //$(this).children("a").click()
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
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&volatile_filters=true"
  s = "<a class='boxed_small bgred clickable' href='"+url+"' target='_blank'>"+v+"</a>"
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
  $(e).addClass("corner")
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
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/ajax_node/ajax_node?node="+v+"&rowid="+id
    toggle_extra(url, id, e, 0)
  })
}

function cell_decorator_groups(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).addClass("corner")
  l = v.split(', ')
  s = ""
  for (i=0; i<l.length; i++) {
    g = l[i]
    s += "<span>"+g+"</span>"
  }
  $(e).html(s)
  table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
  span_id = $(e).parent(".tl").attr("spansum")
  id = table_id + "_x_" + span_id
  $(e).children().each(function(){
    $(this).click(function(){
      if (get_selected() != "") {return}
      g = $(this).text()
      url = $(location).attr("origin") + "/init/ajax_group/ajax_group?groupname="+encodeURIComponent(g)+"&rowid="+id
      toggle_extra(url, id, e, 0)
    })
  })
}

function cell_decorator_username(e) {
  var v = $(e).attr("v")
  if ((v=="") || (v=="empty")) {
    return
  }
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/ajax_user/ajax_user?username="+encodeURIComponent(v)+"&rowid="+id
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
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
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
  var query = "volatile_filters=true&actions_f_svcname="+mon_svcname
  query += "&actions_f_status_log=empty"
  query += "&actions_f_begin="+encodeURIComponent(">-1d")
  url = $(location).attr("origin") + "/init/svcactions/svcactions?"+query
  var d = "<a class='clickable action16' target='_blank' href="+url+">&nbsp</a>"

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
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
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
  $(e).addClass("corner")
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
  $(e).addClass("corner")
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
  s = "<a class='action16' href=''></a>"
  $(e).html(s)
}

function _cell_decorator_dash_link_actions(svcname) {
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_begin=>-7d&volatile_filters=true"
  s = "<a class='action16 clickable' target='_blank' href='"+url+"'></a>"
  return s
}

function _cell_decorator_dash_link_action_error(svcname) {
  url = $(location).attr("origin") + "/init/svcactions/svcactions?actions_f_svcname="+svcname+"&actions_f_status=err&actions_f_ack=!1|empty&actions_f_begin=>-30d&volatile_filters=true"
  s = "<a class='alert16 clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/default/svcmon?svcmon_f_mon_svcname="+svcname+"&volatile_filters=true"
  s = "<a class='svc clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/nodes/nodes?nodes_f_nodename="+nodename+"&volatile_filters=true"
  s = "<a class='node16 clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/checks/checks?checks_f_chk_nodename="+nodename+"&volatile_filters=true"
  s = "<a class='check16 clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/nodenetworks/nodenetworks?nodenetworks_f_mac="+mac+"&volatile_filters=true"
  s = "<a class='net16 clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/obsolescence/obsolescence_config?obs_f_obs_type="+t+"&volatile_filters=true"
  s = "<a class='"+t+"16 clickable' target='_blank' href='"+url+"'></a>"
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
  url = $(location).attr("origin") + "/init/forms/workflow?wfid="+v+"&volatile_filters=true"
  s = "<a class='clickable' target='_blank' href='"+url+"'></a>"
  $(e).html(s)
}

function cell_decorator_run_log(e) {
  var v = $(e).attr("v")
  if (typeof v === "undefined") {
    var s = ""
  } else {
    var s = "<pre>"+v.replace(/ERR:/g, "<span class='err'>ERR:</span>")+"</pre>"
  }
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

function cell_decorator_disk_array(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var line = $(e).parent(".tl")
  var model = line.find("[name$=_array_model]").attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/disks/ajax_array?array="+v+"&rowid="+id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_disk_array_dg(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    array = line.find("[name$=_disk_arrayid],[name$=_array_name]").attr("v")
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    url = $(location).attr("origin") + "/init/disks/ajax_array_dg?array="+array+"&dg="+v+"&rowid="+id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_tag_exclude(e) {
  var v = $(e).attr("v")
  if (v == "empty") {
    v = ""
  }
  $(e).html(v)
  $(window).bind("click", function() {
    $("input.tag_exclude").parent().html(v)
  })
  $(e).bind("click", function(){
    event.stopPropagation()
    i = $("<input class='tag_exclude'></input>")
    var _v = $(this).attr("v")
    if (_v == "empty") {
      _v = ""
    }
    i.val(_v)
    i.bind("keyup", function(){
      if (!is_enter(event)) {
        return
      }
      var url = $(location).attr("origin") + "/init/tags/call/json/tag_exclude"
      var data = {
        "tag_exclude": $(this).val(),
        "tag_id": $(this).parents(".tl").find("[name=tags_c_id]").attr("v")
      }
      var _i = $(this)
      $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
          _i.parent().html(data.tag_exclude)
        }
      })
    })
    $(e).empty().append(i)
    i.focus()
  })
}

function cell_decorator_dash_entry(e) {
  var v = $(e).attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    var line = $(e).parent(".tl")
    var nodename = line.children("[name$=dash_nodename]").attr("v")
    var svcname = line.children("[name$=dash_svcname]").attr("v")
    var dash_md5 = line.children("[name$=dash_md5]").attr("v")
    var dash_created = line.children("[name$=dash_created]").attr("v")
    var rowid = line.attr("cksum")
    url = $(location).attr("origin") + "/init/dashboard/ajax_alert_events?dash_nodename="+nodename+"&dash_svcname="+svcname+"&dash_md5="+dash_md5+"&dash_created="+dash_created+"&rowid="+rowid
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = line.attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(url, id, this, 0)
  })
}

function cell_decorator_rset_md5(e) {
  var v = $(e).attr("v")
  var s = ""
  s = "<div class='clickable'>"+v+"</div>"
  $(e).html(s)
  $(e).addClass("corner")
  $(e).click(function(){
    if (get_selected() != "") {return}
    url = $(location).attr("origin") + "/init/compliance/ajax_rset_md5?rset_md5="+v
    table_id = $(e).parents("table").attr("id").replace(/^table_/, '')
    span_id = $(e).parent(".tl").attr("spansum")
    id = table_id + "_x_" + span_id
    toggle_extra(url, id, this, 0)
  })
}

function T_sub(s, d) {
  if (typeof d === "undefined") {
    return s
  }
  var re = /{{\w+}}/g
  var l = s.match(re)
  for (i=0; i<l.length; i++) {
    var m = l[i]
    var v = m.substring(2, m.length-2)
    if (!(v in d)) {
      continue
    }
    s = s.replace(m, d[v])
  }
  return s
}

function T(s, d) {
  try {
    l = navigator.languages[0]
  } catch(e) {
    l = navigator.userLanguage
  }
  if (!(l in t_dictionary)) {
      return T_sub(s, d)
  }
  user_t_dictionary = t_dictionary[l]
  if (!(s in user_t_dictionary)) {
      return T_sub(s, d)
  }
  return T_sub(user_t_dictionary[s], d)
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
  if (s == 'empty') {
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
    var s = line.children("[cell=1][name$=status_updated]").attr("v")
  }
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

function cell_decorator_date_future(e) {
  _cell_decorator_date(e, 0)
}

function cell_decorator_datetime_status(e) {
  _cell_decorator_datetime(e, 15)
}

function cell_decorator_datetime_future(e) {
  _cell_decorator_datetime(e, 0)
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

function _cell_decorator_date(e, max_age) {
  s = $(e).attr("v")
  if (_outdated(s, max_age)) {
    var cl = " class='nowrap highlight'"
  } else {
    var cl = " class='nowrap'"
  }
  $(e).html("<div"+cl+">"+s.split(" ")[0]+"</div>")
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

function cell_decorator_size_mb(e) {
  v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_mb(v)+"</div>"
  $(e).html(s)
}

function cell_decorator_size_b(e) {
  v = $(e).attr("v")
  if (v == "empty") {
    return
  }
  s = "<div class='nowrap'>"+fancy_size_b(v)+"</div>"
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

function cell_decorator_rsetvars(e) {
  var s = $(e).attr("v")
  $(e).html("<pre>"+s.replace(/\|/g, "\n")+"</pre>")
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
 "rsetvars": cell_decorator_rsetvars,
 "dash_entry": cell_decorator_dash_entry,
 "disk_array_dg": cell_decorator_disk_array_dg,
 "disk_array": cell_decorator_disk_array,
 "size_mb": cell_decorator_size_mb,
 "size_b": cell_decorator_size_b,
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
 "username": cell_decorator_username,
 "groups": cell_decorator_groups,
 "nodename": cell_decorator_nodename,
 "nodename_no_os": cell_decorator_nodename_no_os,
 "svc_action_err": cell_decorator_svc_action_err,
 "availstatus": cell_decorator_availstatus,
 "overallstatus": cell_decorator_overallstatus,
 "chk_type": cell_decorator_chk_type,
 "svcmon_links": cell_decorator_svcmon_links,
 "svc_ha": cell_decorator_svc_ha,
 "env": cell_decorator_env,
 "date_future": cell_decorator_date_future,
 "datetime_future": cell_decorator_datetime_future,
 "datetime_weekly": cell_decorator_datetime_weekly,
 "datetime_daily": cell_decorator_datetime_daily,
 "datetime_status": cell_decorator_datetime_status,
 "datetime_no_age": cell_decorator_datetime_no_age,
 "date_no_age": cell_decorator_date_no_age,
 "dash_severity": cell_decorator_dash_severity,
 "dash_links": cell_decorator_dash_links,
 "tag_exclude": cell_decorator_tag_exclude,
 "_network": cell_decorator_network,
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
    var c = cl[i]
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
  var pager = $("#"+id).find(".pager")
  var p_page = parseInt(p_page)
  var p_start = parseInt(p_start)
  var p_end = parseInt(p_end)
  var p_total = parseInt(p_total)

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
  l = $("#link_"+t.id)
  if (l.length != 1) {
    // linkable = false
    return
  }
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
        ! attr.match(/svc_name/gi) &&
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

function table_relocate_extra_rows(t) {
  $("td[id^="+t.id+"_x_]").each(function(){
    var cksum = $(this).attr("id").split("_x_")[1]
    var d = $(".tl[spansum="+cksum+"]")
    if (d.length == 0) {
      $(this).parent().remove()
    } else {
      $(this).parent().insertAfter(d)
    }
  })
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
    'volatile_filters': opts['volatile_filters'],
    'child_tables': opts['child_tables'],
    'dataable': opts['dataable'],
    'action_menu': opts['action_menu'],
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
    'bind_action_menu': function(){
      table_bind_action_menu(this)
    },
    'bind_filter_selector': function(){
      table_bind_filter_selector(this)
    },
    'bind_filter_input_events': function(){
      table_bind_filter_input_events(this)
    },
    'bind_persistent_filter': function(){
      table_bind_persistent_filter(this)
    },
    'bind_bookmark': function(){
      table_bind_bookmark(this)
    },
    'insert_bookmark': function(bookmark){
      table_insert_bookmark(this, bookmark)
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
    'add_filtered_to_visible_columns': function(){
      table_add_filtered_to_visible_columns(this)
    },
    'relocate_extra_rows': function(){
      table_relocate_extra_rows(this)
    },
    'format_header': function(){
      table_format_header(this)
    },
    'action_menu_param_moduleset': function(){
      return table_action_menu_param_moduleset(this)
    },
    'action_menu_param_module': function(){
      return table_action_menu_param_module(this)
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

  create_overlay()
  t.add_filtered_to_visible_columns()
  t.hide_cells()
  t.format_header()
  t.add_filterbox()
  t.add_scrollers()
  t.bind_refresh()
  t.bind_link()
  t.bind_bookmark()
  t.bind_persistent_filter()
  t.scroll_enable()

  if (t.dataable) {
    t.refresh()
  } else {
    t.bind_checkboxes()
    t.hide_cells()
    t.decorate_cells()
    t.bind_filter_selector()
    t.bind_action_menu()
    t.pager()
    t.restripe_lines()
  }
}

