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
// group hidden menu entries tool
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
//
//
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

function table_invert_column_filter(t, c){
  var input = t.e_header_filters.find("th[col="+c+"]").find("input")
  _invert_filter(input)
  t.save_column_filters()
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
    $("#table_"+id).find('.tl>[name='+col+']').each(function(){
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

function table_reset_column_filters(t, c, val) {
  if (!t.options.filterable) {
    return
  }
  t.e_header_filters.find("th").each(function() {
    var input = $(this).find("input")
    var label = $(this).find(".col_filter_label")
    if ((c in t.colprops) && (t.colprops[c].force_filter != "")) {
      input.val(t.colprops[c].force_filter)
    } else if ((c in t.colprops) && (t.colprops[c].default_filter != "")) {
      input.val(t.colprops[c].default_filter)
    } else {
      input.val("")
    }
    label.empty()
    $(this).find(".clear16,.invert16").hide()
  })

  t.e_header_slim.find("th").each(function() {
    $(this).removeClass("bgblack")
    $(this).removeClass("bgred")
    $(this).removeClass("bgorange")
  })

}

function table_refresh_column_filter(t, c, val) {
  if (!t.options.filterable) {
    return
  }
  var th = t.e_header_filters.find("th[col="+c+"]")
  var input = th.find("input")
  var label = th.find(".col_filter_label")
  var val

  if (typeof(val) === "undefined") {
    val = input.val()
  }

  // make sure the column title is visible
  th.show()

  // update val in input, and text in display area
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
  var _val = val
  if (n > 20) {
    _val = val.substring(0, 17)+"..."
  }
  label.attr("title", val)
  label.text(_val)
  input.val(val)

  // toggle the clear and invert tools visibility
  if (val == "") {
    th.find(".clear16,.invert16").hide()
  } else {
    th.find(".clear16,.invert16").show()
  }

  // update the slim header cell colorization
  var th = t.e_header_slim.find("[col="+c+"]")
  th.removeClass("bgblack")
  th.removeClass("bgred")
  th.removeClass("bgorange")
  var cl = ""
  if ((val.length > 0) && (val != "**clear**")) {
    if (!t.options.volatile_filters) {
      th.addClass("bgred")
    } else {
      th.addClass("bgblack")
    }
  }
}

function table_add_filtered_to_visible_columns(t) {
  $("#table_"+t.id).find("[id^="+t.id+"_f_]").each(function(){
    var s = $(this).attr("id")
    var col = s.split("_f_")[1]
    var val = $(this).val()
    if (t.e_tool_column_selector_area) {
      // no column selector
      if (val === "") {
        t.e_tool_column_selector_area.find("[colname="+col+"]").removeAttr("disabled")
        return
      }
      t.e_tool_column_selector_area.find("[colname="+col+"]").prop("disabled", true)
      if (t.visible_columns.indexOf(col) >= 0) {
        return
      }
    }
    t.visible_columns.push(col)
  })
}

function table_add_column_header_input(t, tr, c) {
  var th = $("<th></th>")
  th.addClass(t.colprops[c]._class)
  th.attr("name", t.id+"_c_"+c)
  th.attr("col", c)

  var filter_tool = $("<span class='clickable filter16'></span>")
  var invert_tool = $("<span class='clickable hidden invert16'></span>")
  var clear_tool = $("<span class='clickable hidden clear16'></span>")
  var label = $("<span class='col_filter_label'></span>")
  var input_float = $("<div class='white_float_input stackable'>")
  var input = $("<input name='fi'>")
  var value_to_filter_tool = $("<span class='clickable values_to_filter'></span><br>")
  var value_cloud = $("<span></span>")
  var input_id = t.id+"_f_"+c

  input.attr("id", input_id)
  if (t.options.request_vars && (input_id in t.options.request_vars)) {
    input.val(t.options.request_vars[input_id])
  }
  value_cloud.attr("id", t.id+"_fc_"+c)

  input_float.append(input)
  input_float.append(value_to_filter_tool)
  input_float.append(value_cloud)
  th.append(filter_tool)
  th.append(invert_tool)
  th.append(clear_tool)
  th.append(label)
  th.append(input_float)
  tr.append(th)
}

function table_add_column_headers_input(t) {
  if (!t.options.headers || !t.options.filterable) {
    return
  }
  var tr = $("<tr class='theader_filters'></tr>")
  if (t.checkboxes) {
    var mcb_id = t.id+"_mcb"
    var th = $("<th></th>")
    var input = $("<input type='checkbox' class='ocb'></input>")
    input.attr("id", mcb_id)
    var label = $("<label></label>")
    label.attr("for", mcb_id)
    input.bind("click", function() {
      check_all(t.id+"_ck", this.checked)
    })
    th.append(input)
    th.append(label)
    tr.append(th)
  }
  if (t.extrarow) {
    tr.append($("<th></th>"))
  }
  for (i=0; i<t.columns.length; i++) {
    var c = t.columns[i]
    t.add_column_header_input(tr, c)
  }
  t.e_table.prepend(tr)
  t.e_header_filters = tr
  t.bind_filter_input_events()
}

function table_add_column_header_slim(t, tr, c) {
  var th = $("<th></th>")
  th.addClass(t.colprops[c]._class)
  th.attr("name", t.id+"_c_"+c)
  th.attr("col", c)
  tr.append(th)
}

function table_add_column_headers_slim(t) {
  var tr = $("<tr class='theader_slim'></tr>")
  if (t.checkboxes) {
    tr.append($("<th></th>"))
  }
  if (t.extrarow) {
    tr.append($("<th></th>"))
  }
  for (i=0; i<t.columns.length; i++) {
    var c = t.columns[i]
    t.add_column_header_slim(tr, c)
  }
  tr.bind("click", function() {
    t.e_header_filters.toggle()
  })
  t.e_table.prepend(tr)
  t.e_header_slim = tr
}

function table_add_column_header(t, tr, c) {
  var th = $("<th></th>")
  th.addClass(t.colprops[c]._class)
  th.attr("name", t.id+"_c_"+c)
  th.attr("col", c)
  th.text(t.colprops[c].title)
  tr.append(th)
}

function table_add_column_headers(t) {
  if (!t.options.headers) {
    return
  }
  var tr = $("<tr class='theader'></tr>")
  if (t.checkboxes) {
    tr.append($("<th></th>"))
  }
  if (t.extrarow) {
    tr.append($("<th></th>"))
  }
  for (i=0; i<t.columns.length; i++) {
    var c = t.columns[i]
    t.add_column_header(tr, c)
  }
  t.e_table.prepend(tr)
  t.e_header = tr
}

function table_refresh_column_filters(t) {
  for (i=0; i<t.visible_columns.length; i++) {
    var c = t.visible_columns[i]
    t.refresh_column_filter(c)
  }
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
  s += "<td cell='1' col='"+k+"' name='"+n+"' v='"+v+"'"+cl+">"+text+"</td>"
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
    var ckid = t.id + "_ckid_" + data[i]['id']
    if (t.checkboxes) {
      line += "<td name='"+t.id+"_tools' class='tools'><input class='ocb' value='"+data[i]['checked']+"' type='checkbox' id='"+ckid+"' name='"+t.id+"_ck'><label for='"+ckid+"'></label></td>"
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
    if (t.div.length > 0 && !t.div.is(":visible")) {
        return
    }
    if (t.e_tool_refresh && t.e_tool_refresh.length > 0 && t.e_tool_refresh_spin && t.e_tool_refresh_spin.hasClass("fa-spin")) {
        t.need_refresh = true
        return
    } else {
        t.set_refresh_spin()
    }

    // move open tabs to overlay to preserve what was in use
    if (t.div.find(".extraline").children("td").children("table").length > 0) {
      $("#overlay").empty().hide()
      t.div.find(".extraline").children("td").children("table").parent().each(function() {
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
             t.div.find(".nodataline>td").text(T("Loading data"))
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
                 t.div.html(msg)
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

             t.pager(pager)
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
               t.e_tool_refresh.trigger("click")
             }
         }
    })
}

function table_insert(t, data) {
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
             t.options.pager.total += n_new_lines

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
    t.div.find(".white_float").hide()
    t.div.find(".white_float_input").hide()

    var inputs = ['tableid', id+"_page"]
    var s = inputs.concat(additional_inputs).concat(getIdsByName(input_name))
    t.div.find("[name="+additional_input_name+"]").each(function(){s.push(this.id)})
    t.div.find("input[id^="+t.id+"_f_]").each(function(){s.push(this.id)})
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
    var toolbar = ""
    line.children("td.tools").each(function(){
      toolbar = "<td class='tools'></td>"
    })
    if (line.next().children("#"+id).attr("id")==id) {
        line.next().remove()
    }
    line.after("<tr class='extraline stackable'>"+toolbar+"<td id="+id+" colspan="+ncols+"></td></tr>")
    if (url) {
      sync_ajax(url, [], id, function(){
        $("#"+id).removeClass("spinner")
        $("#"+id).children().each(function(){$(this).width($(window).width()-$(this).children().position().left-20)})
      })
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

function table_save_column_filters(t) {
  if (t.options.volatile_filters) {
    return
  }
  var data = []
  var del_data = []

  t.e_header_filters.find("input[name=fi]").each(function(){
    var val = $(this).val()
    if (val != "") {
      // filter value to save
      var d = {
        'bookmark': 'current',
        'col_tableid': t.id,
        'col_name': $(this).parents("th").first().attr("col"),
        'col_filter': val
      }
      data.push(d)
    } else {
      // filter value to delete
      var d = {
        'bookmark': 'current',
        'col_tableid': t.id,
        'col_name': $(this).parents("th").first().attr("col")
      }
      del_data.push(d)
    }
  })

  if (data.length > 0) {
    services_osvcpostrest("R_USERS_SELF_TABLE_FILTERS", "", "", data, function(jd) {
      if (jd.error && (jd.error.length > 0)) {
        $(".flash").show("blind").html(services_error_fmt(jd))
      }
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  }
  if (del_data.length > 0) {
    services_osvcdeleterest("R_USERS_SELF_TABLE_FILTERS", "", "", del_data, function(jd) {
      if (jd.error && (jd.error.length > 0)) {
        $(".flash").show("blind").html(services_error_fmt(jd))
      }
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  }
}

function table_bind_filter_input_events(t) {
  var inputs = t.e_header_filters.find("input[name=fi]")
  var url = t.ajax_url + "_col_values/"

  // refresh column filter cloud on keyup
  inputs.bind("keyup", function(event) {
    var input = $(this)
    if (!is_enter(event)) {
      var col = input.attr('id').split('_f_')[1]
      t.e_header_slim.find("[col='"+col+"']").removeClass("bgred").addClass("bgorange")
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
      t.e_header_filters.find(".white_float_input").hide()
      t.save_column_filters()
      t.refresh_column_filters()
      t.refresh()
    }
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
    var c = $(this).parent().attr("col")
    var input = t.e_header_filters.find("th[col="+c+"]").find("input")
    if ((c in t.colprops) && (t.colprops[c].force_filter != "")) {
      input.val(t.colprops[c].force_filter)
    } else if ((c in t.colprops) && (t.colprops[c].default_filter != "")) {
      input.val(t.colprops[c].default_filter)
    } else {
      input.val("")
    }
    t.save_column_filters(c)
    t.refresh_column_filters()
    t.refresh()
  })

  // invert column filter click
  inputs.parent().siblings(".invert16").bind("click", function(event) {
    var c = $(this).parent().attr("col")
    t.invert_column_filter(c)
    t.refresh_column_filters()
    t.refresh()
  })

  // values to column filter click
  inputs.siblings(".values_to_filter").bind("click", function(event) {
    var k = $(this).parent().find("input").attr('id')
    var ck = k.replace("_f_", "_fc_")
    var col = k.split("_f_")[1]
    function f() {
      values_to_filter(k, ck)
      t.e_header_filters.find("th[col="+col+"]").find(".white_float_input").hide()
      t.save_column_filters()
      t.refresh_column_filters()
      t.refresh()
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
      t.filter_selector(event, cell.attr('name'), cell.attr('v'))
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
  s = "<div id='am_"+t.id+"' class='white_float action_menu stackable'><ul>"+s+"</ul></div>"

  // position the popup at the mouse click
  var pos = get_pos(e)
  t.div.append(s)
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
  $(".flash").html(s).show("blind")
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

function table_add_overlay(t) {
  if (t.e_overlay) {
    return
  }
  var e = $("<div class='white_float hidden stackable' id='overlay'></div>")
  $("body").append(e)
 
  $(window).resize(function(){
    resize_overlay()
    resize_extralines()
  })
  e.bind("DOMSubtreeModified", function(){
    resize_overlay()
  })
  t.e_overlay = e
}

function resize_overlay() {
  _resize_overlay()
  $("#overlay").find("img").one("load", function(){
    _resize_overlay()
  })
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
  topology("overlay", {
    "nodenames": nodenames,
    "svcnames": svcnames,
    "display": ["nodes", "services", "countries", "cities", "buildings", "rooms", "racks", "enclosures", "hvs", "hvpools", "hvvdcs"]
  })
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

function table_filter_selector(t, e, k, v){
  if(e.button != 2) {
    return
  }
  $("#am_"+t.id).remove()
  try {
    var sel = window.getSelection().toString()
  } catch(e) {
    var sel = document.selection.createRange().text
  }
  if (sel.length == 0) {
    sel = v
  }
  _sel = sel
  $("#fsr"+t.id).show()
  var pos = get_pos(e)
  $("#fsr"+t.id).find(".bgred").each(function(){
    $(this).removeClass("bgred")
  })
  function getsel(){
    __sel = _sel
    if ($("#fsr"+t.id).find("#fsrwildboth").hasClass("bgred")) {
      __sel = '%' + __sel + '%'
    } else
    if ($("#fsr"+t.id).find("#fsrwildleft").hasClass("bgred")) {
      __sel = '%' + __sel
    } else
    if ($("#fsr"+t.id).find("#fsrwildright").hasClass("bgred")) {
      __sel = __sel + '%'
    }
    if ($("#fsr"+t.id).find("#fsrneg").hasClass("bgred")) {
      __sel = '!' + __sel
    }
    return __sel
  }
  $("#fsr"+t.id).css({"left": pos[0] + "px", "top": pos[1] + "px"})
  $("#fsr"+t.id).find("#fsrview").each(function(){
    $(this).text($("[name="+k+"]").find("input").val())
    $(this).unbind()
    $(this).bind("dblclick", function(){
      sel = $(this).text()
      $(".theader_filters").find("[name="+k+"]").find("input").val(sel)
      t.save_column_filters()
      t.refresh_column_filters()
      t.refresh()
      $("#fsr"+t.id).hide()
    })
    $(this).bind("click", function(){
      sel = $(this).text()
      cur = sel
      $(this).removeClass("highlight")
      $(this).addClass("b")
      $(".theader_filters").find("[name="+k+"]").find("input").val(sel)
      $(".theader_slim").find("[name="+k+"]").each(function(){
        $(this).removeClass("bgred")
        $(this).addClass("bgorange")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrreset").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text("")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrclear").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text("**clear**")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrneg").each(function(){
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
  $("#fsr"+t.id).find("#fsrwildboth").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+t.id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+t.id).find("#fsrwildleft").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+t.id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+t.id).find("#fsrwildright").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr"+t.id).find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr"+t.id).find("#fsreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(sel)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrandeq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      cur =  $(".theader_filters").find("[name="+k+"]").find("input").val()
      val = cur + '&' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsroreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      cur =  $(".theader_filters").find("[name="+k+"]").find("input").val()
      val = cur + '|' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '>' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrandsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&>' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrorsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|>' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '<' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrandinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&<' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrorinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|<' + sel
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($("#fsr"+t.id).find("#fsrneg").hasClass("bgred")) {
        val = '!empty'
      } else {
        val = 'empty'
      }
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrandempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr"+t.id).find("#fsrneg").hasClass("bgred")) {
        val = val + '&!empty'
      } else {
        val = val + '&empty'
      }
      $("#fsr"+t.id).find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr"+t.id).find("#fsrorempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr"+t.id).find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr"+t.id).find("#fsrneg").hasClass("bgred")) {
        val = val + '|!empty'
      } else {
        val = val + '|empty'
      }
      $("#fsr"+t.id).find("#fsrview").each(function(){
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
  url = url.replace(/#$/, "")+"?";
  var args = "clear_filters=true&discard_filters=true"

  // fset
  var current_fset = $("[name=fset_selector]").find("span").attr("fset_id")
  args += "&dbfilter="+current_fset

  t.e_header_filters.find("input[name=fi]").each(function(){
    if ($(this).val().length==0) {
      return
    }
    args += '&'+$(this).attr('id')+"="+encodeURIComponent($(this).val())
  })
  //modification with new link handler
  osvc_create_link(url,args);
}

function table_add_scrollers(t) {
  var s = ""
  s = "<div id='table_"+t.id+"_left' class='scroll_left'>&nbsp</div>"
  $("#table_"+t.id).before(s)
  s = "<div id='table_"+t.id+"_right' class='scroll_right'>&nbsp</div>"
  $("#table_"+t.id).after(s)
}

function table_add_filterbox(t) {
  var s = "<span id='fsr"+t.id+"' class='right_click_menu stackable' style='display: none'>"
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
  t.div.append(s)
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
  'sync_services': 'action_sync_16',
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
  'switch': 'action_switch_16',
  'freeze': 'frozen16',
  'thaw': 'frozen16',
  'sync_all': 'action_sync_16',
  'sync_nodes': 'action_sync_16',
  'sync_drp': 'action_sync_16',
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

function cell_decorator_boolean(e) {
  var v = $(e).attr("v")
  true_vals = [1, "1", "T", "True", true]
  if (typeof v === "undefined") {
    var cl = ""
  } else if (true_vals.indexOf(v) >= 0) {
    var cl = "toggle-on"
  } else {
    var cl = "toggle-off"
  }
  s = "<span class='"+cl+"' title='"+v+"'></span>"
  $(e).html(s)
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
  s = "<a class='action16 icon-red clickable' href='"+url+"' target='_blank'>"+v+"</a>"
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
    toggle_extra(null, id, e, 0)
    node_tabs(id, {"nodename": v})
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
  t = {
    "warn": "orange",
    "up": "green",
    "stdby up": "green",
    "down": "red",
    "stdby down": "red",
    "undef": "gray",
    "n/a": "gray",
  }
  $(e).html("<div class='svc nowrap icon-"+t[c]+"'></div>")
}

function cell_decorator_svcmon_links(e) {
  var line = $(e).parent(".tl")
  var mon_svcname = line.children("[name$=mon_svcname]").attr("v")
  var query = "volatile_filters=true&actions_f_svcname="+mon_svcname
  query += "&actions_f_status_log=empty"
  query += "&actions_f_begin="+encodeURIComponent(">-1d")
  url = $(location).attr("origin") + "/init/svcactions/svcactions?"+query
  var d = "<a class='clickable action16' target='_blank' href="+url+"></a>"

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
      toggle_extra(null, id, e, 0)
      node_tabs(id, {"nodename": nodename, "tab": "node_tabs.compliance"})
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
  $(e).html("<div class='"+l.join(" ")+"' title='"+v+"'></div>")
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

function datetime_age(s) {
  // return age in minutes
  if (typeof s === 'undefined') {
    return
  }
  if (s == 'empty') {
    return
  }
  s = s.replace(/ /, "T")
  var d = new Date(s)
  var now = new Date()
  delta = now.getTime() - d.getTime() - now.getTimezoneOffset() * 60000
  return delta / 60000
}

function _outdated(s, max_age) {
  delta = datetime_age(s)
  if (!delta) {
    return true
  }
  if (delta > max_age) {
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
  cell_decorator_datetime(e)
}

function cell_decorator_date_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_status(e) {
  $(e).attr("max_age", 15)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_future(e) {
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_daily(e) {
  $(e).attr("max_age", 1440)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime_weekly(e) {
  $(e).attr("max_age", 10080)
  cell_decorator_datetime(e)
}

function cell_decorator_datetime(e) {
  var s = $(e).attr("v")
  var max_age = $(e).attr("max_age")
  var delta = datetime_age(s)

  if (!delta) {
    $(e).html()
    return
  }

  if (delta > 0) {
    var prefix = "-"
  } else {
    var prefix = ""
    delta = -delta
  }

  var hour = 60
  var day = 1440
  var week = 10080
  var month = 43200
  var year = 524520

  if (delta < hour) {
    var cl = "minute icon"
    var text = prefix + i18n.t("table.minute", {"count": Math.floor(delta)})
    var color = "#000000"
  } else if (delta < day) {
    var cl = "hour icon"
    var text = prefix + i18n.t("table.hour", {"count": Math.floor(delta/hour)})
    var color = "#181818"
  } else if (delta < week) {
    var cl = "day icon "
    var text = prefix + i18n.t("table.day", {"count": Math.floor(delta/day)})
    var color = "#333333"
  } else if (delta < month) {
    var cl = "week icon "
    var text = prefix + i18n.t("table.week", {"count": Math.floor(delta/week)})
    var color = "#333333"
  } else if (delta < year) {
    var cl = "month icon"
    var text = prefix + i18n.t("table.month", {"count": Math.floor(delta/month)})
    var color = "#484848"
  } else {
    var cl = "year icon"
    var text = prefix + i18n.t("table.year", {"count": Math.floor(delta/year)})
    var color = "#666666"
  } 

  if ($(e).text() == text) {
    return
  }
  cl += " nowrap"

  if (max_age && (delta > max_age)) {
    cl += " icon-red"
  }
  $(e).html("<div class='"+cl+"' style='color:"+color+"' title='"+s+"'>"+text+"</div>")
}

function cell_decorator_date(e) {
  cell_decorator_datetime(e)
  s = $(e).attr("v")
  $(e).text(s.split(" ")[0])
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
 "boolean": cell_decorator_boolean,
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
// table tool: column selector
//
function table_add_column_selector(t) {
  if (!t.options.columnable) {
    return
  }

  var e = $("<div class='floatw' name='tool_column_selector'></div>")
  t.e_tool_column_selector = e

  var span = $("<span class='columns' data-i18n='table.columns'></span>")
  e.append(span)
  try { e.i18n() } catch(e) {}

  var area = $("<div class='hidden white_float stackable'></div>")
  e.append(area)
  t.e_tool_column_selector_area = area

  for (var i=0; i<t.columns.length; i++) {
    var colname = t.columns[i]

    // checkbox
    var input = $("<input type='checkbox' class='ocb' />")
    input.attr("colname", colname)
    input.uniqueId()
    input.bind("click", function() {
      var colname = $(this).attr("colname")
      var current_state
      if ($(this).is(":checked")) {
        current_state = 1
      } else {
        current_state = 0
      }
      var data = {
        "upc_table": t.id,
        "upc_field": colname,
        "upc_visible": current_state,
      }
      services_osvcpostrest("R_USERS_SELF_TABLE_SETTINGS", "", "", data, function(jd) {
        check_toggle_vis(t.id, current_state, t.id+'_c_'+colname)
        t.refresh()
      },
      function(xhr, stat, error) {
        $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
      })
    })
    if (t.visible_columns.indexOf(colname) >= 0) {
      input.prop("checked", true)
    }
    if (t.e_header_filters.find("th[col="+colname+"]").find("input").val()) {
      input.prop("disabled", true)
    }

    // label
    var label = $("<label></label>")
    label.attr("for", input.attr("id"))

    // title
    var title = $("<span style='padding-left:0.3em;'></span>")
    title.text(t.colprops[colname].title)
    title.addClass(t.colprops[colname].img)

    // container
    var _e = $("<div style='white-space:nowrap'></div>")
    _e.append(input)
    _e.append(label)
    _e.append(title)

    area.append(_e)
  }

  // bindings
  e.bind("click", function() {
    t.e_tool_column_selector_area.toggle()
  })

  try { e.i18n() } catch(e) {}
  t.e_toolbar.prepend(e)
}

//
// table tool: commonality
//
function table_add_commonality(t) {
  if (!t.options.commonalityable) {
    return
  }

  var e = $("<div class='floatw' name='tool_commonality'></div>")
  t.e_tool_commonality = e

  var span = $("<span class='common16' data-i18n='table.commonality'></span>")
  e.append(span)

  var area = $("<div class='white_float hidden stackable'></div>")
  area.uniqueId()
  e.append(area)
  t.e_tool_commonality_area = area

  e.bind("click", function() {
    if (t.e_tool_commonality_area.is(":visible")) {
      t.e_tool_commonality_area.hide()
      return
    }
    click_toggle_vis(event, t.e_tool_commonality_area.attr("id"), 'block')
    t.e_tool_commonality_area.empty()
    spinner_add(t.e_tool_commonality_area)
    ajax(t.ajax_url+"/commonality", [], t.e_tool_commonality_area.attr("id"))
  })

  try { e.i18n() } catch(e) {}
  t.e_toolbar.prepend(e)
}

//
// table tool: csv export
//
function table_add_csv(t) {
  if (!t.options.exportable) {
    return
  }

  var e = $("<div class='floatw' name='tool_csv'></div>")
  t.e_tool_csv = e

  var span = $("<span class='csv' data-i18n='table.csv'></span>")
  e.append(span)

  e.bind("click", function() {
    var _e = t.e_tool_csv.children("span")
    if (!_e.hasClass("csv")) {
      return
    }
    _e.removeClass("csv").addClass("csv_disabled")
    setTimeout(function() {
      _e.removeClass("csv_disabled").addClass("csv")
    }, 10000)
    document.location.href = t.ajax_url+"/csv"
  })
  try { e.i18n() } catch(e) {}
  t.e_toolbar.prepend(e)
}

//
// table tool: bookmarks
//
function table_add_bookmarks(t) {
  if (!t.options.bookmarkable) {
    return
  }

  var e = $("<div class='floatw' name='tool_bookmark'></div>")

  var span = $("<span class='bookmark16' data-i18n='table.bookmarks'></span>")
  e.append(span)

  var area = $("<div class='white_float hidden stackable'></div>")
  e.append(area)

  var save = $("<a class='add16' data-i18n='table.bookmarks_save'></a>")
  area.append(save)

  var save_name = $("<div class='hidden'><hr><div class='edit16' data-i18n='table.bookmarks_save_name'></div><div>")
  area.append(save_name)

  var save_name_input = $("<input style='margin-left:1em' class='oi' />")
  save_name.append(save_name_input)

  area.append("<hr>")

  var listarea = $("<span></span>")
  area.append(listarea)
  t.e_tool_bookmarks_listarea = listarea

  var params = {
    "query": "col_tableid="+t.id,
    "limit": "0",
    "props": "bookmark"
  }
  spinner_add(listarea)
  services_osvcgetrest("R_USERS_SELF_TABLE_FILTERS", "", params, function(jd) {
    spinner_del(listarea)
    if (!jd.data) {
      return
    }
    if (!jd.data.length) {
      listarea.text(i18n.t("table.bookmarks_no_bookmarks"))
      return
    }

    var done = []
    for (var i=0; i<jd.data.length; i++) {
      var name = jd.data[i].bookmark
      if (name == "current") {
        continue
      }
      if (done.indexOf(name) >= 0) {
        continue
      }
      done.push(name)
      t.insert_bookmark(name)
    }
  },
  function(xhr, stat, error) {
    spinner_del(listarea)
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  })

  try { e.i18n() } catch(e) {}
  t.e_tool_bookmarks = e
  t.e_tool_bookmarks_area = area
  t.e_tool_bookmarks_save = save
  t.e_tool_bookmarks_save_name = save_name
  t.e_tool_bookmarks_save_name_input = save_name_input

  // bindings
  span.bind("click", function() {
    area.toggle()
  })

  save.bind("click", function() {
    var now = new Date()
    save_name_input.val(print_date(now))
    save_name.toggle("blind")
    save_name_input.focus()
  })

  save_name_input.bind("keyup", function(event) {
    if (!is_enter(event)) {
      return
    }
    var name = $(this).val()
    var data = {
      "col_tableid": t.id,
      "bookmark": name,
    }
    services_osvcpostrest("R_USERS_SELF_TABLE_FILTERS_SAVE_BOOKMARK", "", "", data, function(jd) {
      if (jd.error) {
        $(".flash").show("blind").html(services_error_fmt(jd))
        return
      }
      t.insert_bookmark(name)
      t.e_tool_bookmarks_save_name.hide()
      t.e_tool_bookmarks_save.show()
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  })

  t.e_toolbar.prepend(e)
}

function table_insert_bookmark(t, name) {
  // remove the "no_bookmarks" msg
  if (t.e_tool_bookmarks_listarea.find("p").length == 0) {
    t.e_tool_bookmarks_listarea.text("")
  }
 
  // append the bookmark to the list area
  var bookmark = $("<p></p>")
  bookmark.append($("<a class='bookmark16'>"+name+"</a>"))
  bookmark.append($("<a style='float:right' class='del16'>&nbsp;</a>"))
  t.e_tool_bookmarks_listarea.append(bookmark)

  // "del" binding
  bookmark.find(".del16").bind("click", function() {
    var name = $(this).prev().text()
    var line = $(this).parents("p").first()
    var data = {
      "col_tableid": t.id,
      "bookmark": name,
    }
    services_osvcdeleterest("R_USERS_SELF_TABLE_FILTERS", "", "", data, function(jd) {
      if (jd.error) {
        $(".flash").show("blind").html(services_error_fmt(jd))
        return
      }
      line.hide("blind", function(){line.remove()})
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  })

  // "load" binding
  bookmark.find(".bookmark16").bind("click", function() {
    var name = $(this).text()
    var data = {
      "col_tableid": t.id,
      "bookmark": name,
    }
    services_osvcpostrest("R_USERS_SELF_TABLE_FILTERS_LOAD_BOOKMARK", "", "", data, function(jd) {
      if (jd.error) {
        $(".flash").show("blind").html(services_error_fmt(jd))
        return
      }

      // update the column filters
      t.reset_column_filters()
      for (var i=0; i<jd.data.length; i++) {
        var data = jd.data[i]
        if (data.col_name.indexOf(".") >= 0) {
          var k = data.col_name.split('.')[1]
        } else {
          var k = data.col_name
        }
        var v = data.col_filter
        t.refresh_column_filter(k, v)
      }

      t.refresh()
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  })
}


//
// table tool: link
//
function table_add_link(t) {
  if (!t.options.linkable) {
    return
  }

  var e = $("<div class='floatw' name='tool_link'></div>")

  var span = $("<span class='link16' title='table.link_title' data-i18n='table.link'></span>")
  e.append(span)
  try { e.i18n() } catch(e) {}

  // bindings
  e.bind("click", function() {
    t.link()
  })

  $(this).bind("keypress", function(event) {
    if ($('input').is(":focus")) { return }
    if ($('textarea').is(":focus")) { return }
    if ( event.which == 108 ) {
      t.link()
    }
  })

  t.e_tool_link = e
  t.e_toolbar.prepend(e)
}

//
// table tool: refresh
//
function table_add_refresh(t) {
  if (!t.options.refreshable) {
    return
  }

  var e = $("<div class='floatw' name='tool_refresh'><span class='refresh16'></span><span data-i18n='table.refresh'></span></div>")
  try { e.i18n() } catch(e) {}

  // bindings
  e.bind("click", function(){
    t.refresh()
  })

  $(this).bind("keypress", function(event) {
    if ($('input').is(":focus")) { return }
    if ($('textarea').is(":focus")) { return }
    if ( event.which == 114 ) {
      t.refresh()
    }
  })

  t.e_tool_refresh = e
  t.e_tool_refresh_spin = e.find(".refresh16")
  t.e_toolbar.prepend(e)
}

//
// table tool: volatile toggle
//
function table_add_volatile(t) {
  // checkbox
  var input = $("<input type='checkbox' class='ocb' />")
  if (t.options.volatile_filters) {
    input.prop("checked", true)
  }
  input.uniqueId()
  input.bind("click", function() {
    var current_state
    if ($(this).is(":checked")) {
      current_state = true
    } else {
      current_state = false
    }
    t.options.volatile_filters = current_state
    t.refresh_column_filters()
  })

  // label
  var label = $("<label></label>")
  label.attr("for", input.attr("id"))

  // title
  var title = $("<span data-i18n='table.volatile' style='padding-left:0.3em;'></span>")
  title.attr("title", i18n.t("table.volatile_title"))

  // container
  var e = $("<span class='floatw'></span>")
  e.append(input)
  e.append(label)
  e.append(title)
  e.i18n()

  t.e_toolbar.prepend(e)
}

//
// table tool: websocket toggle
//
function table_add_wsswitch(t) {
  if (!t.options.wsable) {
    return
  }

  // checkbox
  var input = $("<input type='checkbox' class='ocb' />")
  input.uniqueId()
  input.bind("click", function() {
    var current_state
    if ($(this).is(":checked")) {
      current_state = 1
    } else {
      current_state = 0
    }
    var data = {
      "upc_table": t.id,
      "upc_field": "wsenabled",
      "upc_visible": current_state,
    }
    services_osvcpostrest("R_USERS_SELF_TABLE_SETTINGS", "", "", data, function(jd) {
      if (t.need_refresh) {
        t.refresh()
      }
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  })

  // label
  var label = $("<label></label>")
  label.attr("for", input.attr("id"))

  // title
  var title = $("<span data-i18n='table.live' style='padding-left:0.3em;'></span>")

  // container
  var e = $("<span class='floatw'></span>")
  e.append(input)
  e.append(label)
  e.append(title)
  try { e.i18n() } catch(e) {}

  var data = {
    "query": "upc_table="+t.id+" and upc_field=wsenabled",
    "meta": "0"
  }
  input.prop("disabled", true)
  services_osvcgetrest("R_USERS_SELF_TABLE_SETTINGS", "", data, function(jd) {
    input.prop("disabled", false)
    if (!jd.data) {
      return
    }
    if ((jd.data.length == 0) || (jd.data[0].upc_visible)) {
      input.prop("checked", true)
      t.pager()
    } else {
      input.prop("checked", false)
    }
  },
  function(xhr, stat, error) {
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  })

  t.e_toolbar.prepend(e)
  t.e_wsswitch = e
}


//
// table tool: pager
//
function table_pager(t, options) {
  if (!t.e_pager) {
    return
  }
  if (options) {
    t.options.pager = options
  }

  if (t.e_wsswitch && t.e_wsswitch.find("input").is(":checked")) {
    var wsswitch = true
  } else {
    var wsswitch = false
  }

  var p_page = parseInt(t.options.pager.page)
  var p_start = parseInt(t.options.pager.start)
  var p_end = parseInt(t.options.pager.end)
  var p_total = parseInt(t.options.pager.total)
  var p_perpage = parseInt(t.options.pager.perpage)
  var max_perpage = 50

  if (t.e_wsswitch && t.e_wsswitch.find("input").is(":checked")) {
    var wsswitch = true
    if (p_perpage > max_perpage) {
      p_perpage = max_perpage
      t.options.pager.perpage = max_perpage
    }
  } else {
    var wsswitch = false
  }

  if ((p_total > 0) && (p_end > p_total)) {
    p_end = p_total
  }
  var s_total = ""
  if (p_total > 0) {
    s_total = "/" + p_total
  }

  // perpage selector
  var l = [20, 50, 100, 500]
  var selector = $("<div name='pager_perpage' class='white_float stackable' style='display:none;max-width:50%;text-align:right;'></div>")
  for (i=0; i<l.length; i++) {
     var v = l[i]
     var entry = $("<span name='perpage_val' class='clickable'>"+v+"</span>")
     if (v == p_perpage) {
       entry.addClass("current_page")
     }
     if (wsswitch && (v > max_perpage)) {
       entry.addClass("grayed")
       entry.removeClass("clickable")
     }
     selector.append(entry)
     selector.append($("<br>"))
  }

  t.e_pager.empty()

  // main pager
  if (p_total == 0) {
    t.e_pager.text("No records found matching filters")
  } else {
    // left arrow
    if (p_page > 1) {
      var left = $("<span name='pager_left'></span>")
      left.text("<< ")
      t.e_pager.append(left)
    }

    // line start - line end
    var center = $("<span name='pager_center'></span>")
    center.text((p_start+1)+"-"+p_end+s_total)
    t.e_pager.append(center)

    // right arrow
    if ((p_total < 0) || ((p_page * p_perpage) < p_total)) {
      var right = $("<span name='pager_right'></span>")
      left.text(" >>")
      t.e_pager.append(right)
    }
  }
  t.e_pager.append(selector)
  keep_inside(selector[0])

  t.e_pager.children("span").each(function () {
    $(this).addClass('current_page clickable')
  })
  t.e_pager.find("[name=pager_right]").click(function(){
    filter_submit(t.id, t.id+"_page", p_page+1)
  })
  t.e_pager.find("[name=pager_left]").click(function(){
    filter_submit(t.id, t.id+"_page", p_page-1)
  })
  t.e_pager.find("[name=pager_center]").click(function(){
    t.e_pager.find("[name=pager_perpage]").toggle()
  })
  t.e_pager.find("[name=perpage_val]").click(function(){
    if ($(this).hasClass("grayed")) {
      return
    }
    var data = {
      "perpage": parseInt($(this).text())
    }
    services_osvcpostrest("R_USERS_SELF", "", "", data, function(jd) {
      t.refresh()
    },
    function(xhr, stat, error) {
      $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
    })
  })
}

function table_add_pager(t) {
  if (!t.options.pageable) {
    return
  }
  var e = $("<span class='pager floatw'></span>")
  t.e_toolbar.prepend(e)
  t.e_pager = e
}

//
// table horizontal scroll
//
function table_scroll(t){
  sticky_relocate(t.e_header, t.e_sticky_anchor)
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
  $("#table_"+t.id).parent().bind("scroll", function(){
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
  if (!t.e_tool_refresh_spin) {
    return
  }
  t.e_tool_refresh_spin.removeClass("fa-spin")
}

function table_set_refresh_spin(t) {
  if (!t.e_tool_refresh_spin) {
    return
  }
  t.e_tool_refresh_spin.addClass("fa-spin")
}

function table_stick(t) {
  // bypass conditions
  if (t.div.parents(".tableo").length > 0) {
    return
  }

  var anchor = $("<span></span>")
  anchor.uniqueId()
  anchor.insertBefore(t.e_header)
  t.e_sticky_anchor = anchor
  sticky_relocate(t.e_header, t.e_sticky_anchor)
  $(window).scroll(function(){
    sticky_relocate(t.e_header, t.e_sticky_anchor)
  })
  sticky_relocate(t.e_header, t.e_sticky_anchor)
}

function table_get_column_filters(t, callback) {
  var data = {
    "query": "col_tableid="+t.id+" and bookmark=current",
    "meta": "0"
  }
  services_osvcgetrest("R_USERS_SELF_TABLE_FILTERS", "", data, function(jd) {
    if (jd.error) {
      $(".flash").show("blind").html(services_error_fmt(jd))
      return
    }
    t.reset_column_filters()
    for (i=0; i<jd.data.length; i++) {
      var d = jd.data[i]
      if (d.col_name.indexOf(".") >= 0) {
        var k = d.col_name.split('.')[1]
      } else {
        var k = d.col_name
      }
      t.refresh_column_filter(k, d.col_filter)
    }
    callback(t)
  },
  function(xhr, stat, error) {
    $(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
  }) 
}

function table_init(opts) {
  var t = {
    'options': opts,
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
    'filter_selector': function(e, k, v){
      table_filter_selector(this, e, k, v)
    },
    'bind_filter_selector': function(){
      table_bind_filter_selector(this)
    },
    'bind_filter_input_events': function(){
      table_bind_filter_input_events(this)
    },
    'insert_bookmark': function(name){
      table_insert_bookmark(this, name)
    },
    'bind_checkboxes': function(){
      table_bind_checkboxes(this)
    },
    'pager': function(options){
      table_pager(this, options)
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
    'reset_column_filters': function(){
      table_reset_column_filters(this)
    },
    'add_column_header': function(e, c){
      table_add_column_header(this, e, c)
    },
    'add_column_headers': function(){
      table_add_column_headers(this)
    },
    'add_column_header_slim': function(e, c){
      table_add_column_header_slim(this, e, c)
    },
    'add_column_headers_slim': function(){
      table_add_column_headers_slim(this)
    },
    'add_column_header_input': function(e, c){
      table_add_column_header_input(this, e, c)
    },
    'add_column_headers_input': function(){
      table_add_column_headers_input(this)
    },
    'add_filtered_to_visible_columns': function(){
      table_add_filtered_to_visible_columns(this)
    },
    'relocate_extra_rows': function(){
      table_relocate_extra_rows(this)
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
    },
    'stick': function(){
      table_stick(this)
    },
    'get_column_filters': function(callback){
      table_get_column_filters(this, callback)
    },
    'add_pager': function(){
      table_add_pager(this)
    },
    'add_wsswitch': function(){
      table_add_wsswitch(this)
    },
    'add_volatile': function(){
      table_add_volatile(this)
    },
    'add_refresh': function(){
      table_add_refresh(this)
    },
    'add_link': function(){
      table_add_link(this)
    },
    'add_bookmarks': function(){
      table_add_bookmarks(this)
    },
    'add_csv': function(){
      table_add_csv(this)
    },
    'add_column_selector': function(){
      table_add_column_selector(this)
    },
    'add_commonality': function(){
      table_add_commonality(this)
    },
    'invert_column_filter': function(c){
      table_invert_column_filter(this, c)
    },
    'save_column_filters': function(){
      table_save_column_filters(this)
    },
    'add_overlay': function(){
      table_add_overlay(this)
    }
  }

  // selectors cache
  t.div = $("#"+t.id)
  t.e_toolbar = t.div.find("[name=toolbar]").first()
  t.e_table = t.div.find("table#table_"+t.id).first()

  osvc.tables[t.id] = t
  t.div.find("select").parent().css("white-space", "nowrap")
  t.div.find("select:visible").combobox()

  t.add_overlay()
  t.add_column_headers_slim()
  t.add_column_headers_input()
  t.add_column_headers()
  t.refresh_column_filters()
  t.add_commonality()
  t.add_column_selector()
  t.add_csv()
  t.add_bookmarks()
  t.add_link()
  t.add_refresh()
  t.add_wsswitch()
  t.add_volatile()
  t.add_pager()
  t.add_filtered_to_visible_columns()
  t.hide_cells()
  t.add_filterbox()
  t.add_scrollers()
  t.scroll_enable()
  t.stick()

  function init_post_get_column_filters() {
    if (t.dataable) {
      t.refresh()
    } else {
      t.pager()
      t.bind_checkboxes()
      t.hide_cells()
      t.decorate_cells()
      t.bind_filter_selector()
      t.bind_action_menu()
      t.restripe_lines()
    }
  }

  function has_filter_in_request_vars() {
    if (!t.options.request_vars) {
      return false
    }
    for (c in t.colprops) {
      if (t.id+"_f_"+c in t.options.request_vars) {
        return true
      }
    }
    return false
  }

  if (t.options.volatile_filters || has_filter_in_request_vars()) {
    // though column filters can still be set through the options.request_vars
    init_post_get_column_filters()
  } else {
    // get the column filters from the collector
    t.get_column_filters(
      init_post_get_column_filters
    )
  }
}

