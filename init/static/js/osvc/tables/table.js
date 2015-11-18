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
    var url = services_get_url() + "/init/ajax_user/call/json/set_user_group"
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
    var url = services_get_url() + "/init/ajax_group/call/json/set_group_hidden_menu_entry"
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
    box_w = $(box).width()
    doc_w = $('body').width()

    // trim the box width to fit the doc
    if ((box_w+20)>doc_w) {
        $(box).css("width", doc_w - 30)
        $(box).css("overflow-x", "auto")
        box_w = $(box).width()
    }

    // align to the right doc border
    if (box_off_l + box_w > doc_w) {
        $(box).offset({"left": doc_w - box_w - 20})
        box_off_l = $(box).offset().left
    }

    // align to the left doc border
    if (box_off_l < 0) {
        $(box).offset({"left": 10})
        box_off_l = $(box).offset().left
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
function sparkl(url, id) {
    if (!$("#"+id).is(":visible")) {
        return
    }
    chartoptions = {type: 'tristate'};
    $.getJSON(url, function(data) {
        $(document.getElementById(id)).sparkline(data, chartoptions);
    });
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
  var input = $("<input class='oi' name='fi'>")
  var value_to_filter_tool = $("<span class='clickable icon values_to_filter'></span><br>")
  var value_cloud = $("<span></span>")
  var input_id = t.id+"_f_"+c
  var header = $("<h3></h3>")

  header.text(i18n.t("table.column_filter_header", {"col": t.colprops[c].title}))
  value_to_filter_tool.attr("title", i18n.t("table.value_to_filter_tool_title"))

  input.attr("id", input_id)
  if (t.options.request_vars && (input_id in t.options.request_vars)) {
    input.val(t.options.request_vars[input_id])
  }
  value_cloud.attr("id", t.id+"_fc_"+c)
  value_cloud.css({"overflow-wrap": "break-word"})

  input_float.append(header)
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

function table_parent_table_data(t, ptid) {
  if (!(ptid in osvc.tables)) {
    console.log("table", t.id, "parent table", ptid, "not found")
    return {}
  }
  var pt = osvc.tables[ptid]
  var data = {}
  for (c in pt.colprops) {
    var current = $("#"+pt.id+"_f_"+c).val()
    if ((current != "") && (typeof current !== 'undefined')) {
      data[pt.id+"_f_"+c] = current
    } else if (pt.colprops[c].force_filter != "") {
      data[pt.id+"_f_"+c] = pt.colprops[c].force_filter
    }
  }
  return data
}

function table_parent_tables_data(t) {
  if (!t.options.parent_tables || (t.options.parent_tables.length == 0)) {
    return {}
  }
  var data = {}
  for (var i=0; i<t.options.parent_tables.length; i++) {
    data = $.extend(data, t.parent_table_data(t.options.parent_tables[i]))
  }
  return data
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

    var data = t.parent_tables_data()

    // refresh open tabs to overlay to preserve what was in use
    if (t.div.find(".extraline:visible").children("td").children("table").length > 0) {
      $("#overlay").empty().hide()
      t.div.find(".extraline").children("td").children("table").parent().each(function() {
        var e = $("<div></div>")
        e.attr("id", $(this).attr("id"))
        e.append($(this).children())
        $("#overlay").append(e)
      })
      $("#overlay").hide().show("scale")
    }

    data.table_id = t.id
    data.visible_columns = t.visible_columns.join(',')
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
             t.div.find(".nodataline>td").text(i18n.t("api.loading"))
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

//
// used by non-rest server side tool
// all users should migrate to direct use of the rest api from the js code
//
function table_ajax_submit(t, tool, additional_inputs, input_name, additional_input_name) {
    // close dialogs
    t.div.find(".white_float").hide()
    t.div.find(".white_float_input").hide()

    var data = {
      "tableid": t.id,
      "table_id": t.id,
    }
    data[t.id+"_page"] = t.e_header.find("#"+t.id+"_page").val()

    if (additional_inputs) {
      for (var i=0; i<additional_inputs.length; i++) {
        var iid = additional_inputs[i]
        data[iid] = $("#"+iid).val()
      }
    }
    t.div.find("[name="+input_name+"]").each(function() {
      data[$(this).attr("id")] = $(this).val()
    })
    t.div.find("[name="+additional_input_name+"]").each(function() {
      data[$(this).attr("id")] = $(this).val()
    })
    t.div.find("input[id^="+t.id+"_f_]").each(function(){
      data[$(this).attr("id")] = $(this).val()
    })
    data = $.extend(data, t.parent_tables_data())
    $.ajax({
         type: "POST",
         url: t.ajax_url+"/"+tool,
         data: data,
         context: document.body,
         beforeSend: function(req){
	   t.set_refresh_spin()
         },
         success: function(msg){
	   t.unset_refresh_spin()
           t.refresh()
         }
    })
}
function toggle_extra(url, id, e, ncols) {
    line=$(e).parents(".tl").first()
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
        $("#"+id).children().each(function(){
          $(this).width($(window).width()-$(this).children().position().left-20)
        })
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

function table_page_submit(t, v){
  t.div.find("#"+t.id+"_page").val(v)
  t.refresh()
  t.refresh_column_filters()
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
    if (is_enter(event)) {
      return
    }
    var input = $(this)
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
       beforeSend: function(req){
         dest.empty()
         dest.addClass("spinner")
       },
       success: function(msg){
          var data = $.parseJSON(msg)
          t.format_values_cloud(dest, data)
       }
      })
    }, 1000)
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

function table_add_overlay(t) {
  if ($("#overlay").length > 0) {
    t.e_overlay = $("#overlay")
    return
  }
  var e = $("<div class='white_float hidden stackable' id='overlay'></div>")
  $("body").append(e)
 
  $(window).resize(function(){
    resize_overlay()
    resize_extralines()
  })
  e.bind("DOMSubtreeModified", resize_overlay)
  t.e_overlay = e
}

function resize_overlay() {
  if ($("#overlay:visible").length == 0) {
    return
  }
  _resize_overlay()
  $("#overlay").find("img").one("load", function(){
    _resize_overlay()
  })
}

function _resize_overlay() {
  e = $("#overlay")
  e.unbind("DOMSubtreeModified", resize_overlay)
  e.css({
   'overflow': 'auto',
   'position': 'fixed',
   'height': $(window).height()-60,
   'width': $(window).width()-60,
   'top': ($(window).height()-e.height())/2,
   'left': ($(window).width()-e.width())/2
  })
  e.bind("DOMSubtreeModified", resize_overlay)
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
  t.e_overlay.show()
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
  t.e_overlay.show()
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
  t.e_overlay.show()
  sysrepdiff("overlay", {"nodes": nodes.join(",")})
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
  t.e_overlay.show()
  sysrep("overlay", {"nodes": nodes.join(",")})
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
  t.e_overlay.show()
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
  t.e_overlay.show()
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
  t.e_overlay.show()
  sync_ajax('/init/nodes/ajax_grpprf?node='+nodes.join(","), [], 'overlay', function(){})
}

function tool_nodediff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_nodediff(\""+t.id+"\")'>"+i18n.t("action_menu.node_diff")+"</div>"
}

function tool_nodesantopo(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon hd16' onclick='trigger_tool_nodesantopo(\""+t.id+"\")'>"+i18n.t("action_menu.node_san_topo")+"</div>"
}

function tool_nodesysrepdiff(t, data) {
  if (data.length<2) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_nodesysrepdiff(\""+t.id+"\")'>"+i18n.t("action_menu.node_sysrep_diff")+"</div>"
}

function tool_nodesysrep(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon log16' onclick='trigger_tool_nodesysrep(\""+t.id+"\")'>"+i18n.t("action_menu.node_sysrep")+"</div>"
}

function tool_grpprf(t, data) {
  if (data.length==0) {
    return ""
  }
  return "<div class='clickable icon spark16' onclick='trigger_tool_grpprf(\""+t.id+"\")'>"+i18n.t("action_menu.node_perf")+"</div>"
}

function tool_svcdiff(t, data) {
  if (data.length<=1) {
    return ""
  }
  return "<div class='clickable icon common16' onclick='trigger_tool_svcdiff(\""+t.id+"\")'>"+i18n.t("action_menu.svc_diff")+"</div>"
}

function tool_topo(t) {
  var datasvc = table_action_menu_get_svcs_data(t)
  var datanode = table_action_menu_get_nodes_data(t)
  if (datasvc.length+datanode.length==0) {
    return ""
  }
  return "<div class='clickable icon dia16' onclick='trigger_tool_topo(\""+t.id+"\")'>"+i18n.t("action_menu.topology")+"</div>"
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
  var s = "<li class='clickable'>"+i18n.t("action_menu.actions_on_selected_nodes")+" (<b>"+data.length+"</b>)"+table_action_menu_node_entries(t, "nodes")+"</li>"
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
    if (t.e_header_filters && t.e_header_filters.find("th[col="+colname+"]").find("input").val()) {
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

    var data = {}
    t.div.find("input[id^="+t.id+"_f_]").each(function(){
      data[$(this).attr("id")] = $(this).val()
    })
    data = $.extend(data, t.parent_tables_data())
    var l = []
    for (k in data) {
      l.push(encodeURIComponent(k)+"="+encodeURIComponent(data[k]))
    }
    var q = l.join("&")
    var url = t.ajax_url+"/csv"
    if (q.length > 0) {
      url += "?"+q
    }
    document.location.href = url
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
  if (!t.options.headers || !t.options.filterable) {
    return
  }

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
      right.text(" >>")
      t.e_pager.append(right)
    }
  }
  t.e_pager.append(selector)
  keep_inside(selector[0])

  t.e_pager.children("span").each(function () {
    $(this).addClass('current_page clickable')
  })
  t.e_pager.find("[name=pager_right]").click(function(){
    t.page_submit(p_page+1)
  })
  t.e_pager.find("[name=pager_left]").click(function(){
    t.page_submit(p_page-1)
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

function table_add_ws_handler(t) {
  if (!t.options.events) {
    return
  }
  for (var i=0; i<t.options.events.length; i++) {
    console.log("register table", t.id, t.options.events[i], "event handler")
    var ev = t.options.events[i]
    wsh[t.id] = function(data) {
      if (data["event"] == ev) {
        t.refresh()
      }
    }
  }
}

function table_format_values_cloud(t, span, data) {
  span.removeClass("spinner")

  var keys = []
  var max = 0
  var min = 0
  var delta = 0
  for (key in data) {
    keys.push(key)
    n = data[key]
    if (n > max) max = n
    min = max
  }
  for (key in data) {
    n = data[key]
    if (n < min) min = n
    delta = max - min
  }

  // header
  var header = $("<h3></h3>")
  header.text(i18n.t("table.unique_matching_values", {"count": keys.length}))
  span.append(header)

  // 'empty' might not be comparable with other keys type
  if ('empty' in keys) {
    var skeys = keys
    skeys.remove('empty')
    skeys = ['empty'] + skeys.sort()
  } else {
    skeys = keys.sort()
  }

  // candidates
  for (var i=0; i<skeys.length ; i++) {
    var key = skeys[i]
    var n = data[key]
    if (delta > 0) {
      var size = 100 + 100. * (n - min) / delta
    } else {
      var size = 100
    }

    e = $("<a class='h cloud_tag'></a>")
    e.text(key)
    e.css({"font-size": size+"%"})
    e.attr("title", i18n.t("table.number_of_occurence", {"count": data[key]}))
    e.bind("click", function(){
      span.siblings("input").val($(this).text())
      t.refresh()
      t.refresh_column_filters()
      t.save_column_filters()
    })
    span.append(e)
  }
}

function table_flash(t) {
  if (!t.options.flash || t.options.flash.length == 0) {
    return
  }
  var e = $("<span><span class='alert16 err fa-2x'></span><span data-i18n='table.tool_error'></span></span>")
  e.i18n()
  var p = $("<pre></pre>")
  p.text(t.options.flash)
  p.css({
    "padding": "5px",
    "padding-left": "20px",
  })
  e.append(p)
  $(".flash").show("blind").html(e)
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
      return table_cell_decorator(opts['id'])
    },
    'page_submit': function(v){
      return table_page_submit(this, v)
    },
    'ajax_submit': function(tool, additional_inputs, input_name, additional_input_name){
      return table_ajax_submit(this, tool, additional_inputs, input_name, additional_input_name)
    },
    'column_values': function(){
      return table_column_values(this)
    },
    'format_values_cloud': function(span, data){
      return table_format_values_cloud(this, span, data)
    },
    'add_ws_handler': function(){
      return table_add_ws_handler(this)
    },
    'hide_cells': function(){
      return table_hide_cells(this)
    },
    'scroll': function(){
      return table_scroll(opts['id'])
    },
    'bind_filter_reformat': function(){
      return table_bind_filter_reformat(this)
    },
    'bind_action_menu': function(){
      return table_bind_action_menu(this)
    },
    'filter_selector': function(e, k, v){
      return table_filter_selector(this, e, k, v)
    },
    'bind_filter_selector': function(){
      return table_bind_filter_selector(this)
    },
    'bind_filter_input_events': function(){
      return table_bind_filter_input_events(this)
    },
    'insert_bookmark': function(name){
      return table_insert_bookmark(this, name)
    },
    'bind_checkboxes': function(){
      return table_bind_checkboxes(this)
    },
    'pager': function(options){
      return table_pager(this, options)
    },
    'trim_lines': function(){
      return table_trim_lines(this)
    },
    'restripe_lines': function(){
      return table_restripe_lines(opts['id'])
    },
    'scroll_enable': function(){
      return table_scroll_enable(this)
    },
    'scroll_enable_dom': function(){
      return table_scroll_enable_dom(this)
    },
    'scroll_disable_dom': function(){
      return table_scroll_disable_dom(this)
    },
    'set_refresh_spin': function(){
      return table_set_refresh_spin(this)
    },
    'unset_refresh_spin': function(){
      return table_unset_refresh_spin(this)
    },
    'link': function(){
      return table_link(this)
    },
    'add_scrollers': function(){
      return table_add_scrollers(this)
    },
    'add_filterbox': function(){
      return table_add_filterbox(this)
    },
    'refresh_column_filter': function(c, val){
      return table_refresh_column_filter(this, c, val)
    },
    'refresh_column_filters': function(){
      return table_refresh_column_filters(this)
    },
    'reset_column_filters': function(){
      return table_reset_column_filters(this)
    },
    'add_column_header': function(e, c){
      return table_add_column_header(this, e, c)
    },
    'add_column_headers': function(){
      return table_add_column_headers(this)
    },
    'add_column_header_slim': function(e, c){
      return table_add_column_header_slim(this, e, c)
    },
    'add_column_headers_slim': function(){
      return table_add_column_headers_slim(this)
    },
    'add_column_header_input': function(e, c){
      return table_add_column_header_input(this, e, c)
    },
    'add_column_headers_input': function(){
      return table_add_column_headers_input(this)
    },
    'add_filtered_to_visible_columns': function(){
      return table_add_filtered_to_visible_columns(this)
    },
    'relocate_extra_rows': function(){
      return table_relocate_extra_rows(this)
    },
    'action_menu_param_moduleset': function(){
      return table_action_menu_param_moduleset(this)
    },
    'action_menu_param_module': function(){
      return table_action_menu_param_module(this)
    },
    'on_change': function(){
      if (!t.options.on_change) {
        return
      }
      t.options.on_change()
    },
    'refresh_child_tables': function(){
      for (var i=0; i<this.child_tables.length; i++) {
        var id = this.child_tables[i]
        if (!(id in osvc.tables)) {
          console.log("child table not found in osvc.tables:", id)
          continue
        }
        osvc.tables[id].refresh()
      }
    },
    'insert': function(data){
      return table_insert(this, data)
    },
    'refresh': function(){
      return table_refresh(this)
    },
    'stick': function(){
      return table_stick(this)
    },
    'parent_table_data': function(ptid){
      return table_parent_table_data(this, ptid)
    },
    'parent_tables_data': function(){
      return table_parent_tables_data(this)
    },
    'get_column_filters': function(callback){
      return table_get_column_filters(this, callback)
    },
    'add_pager': function(){
      return table_add_pager(this)
    },
    'add_wsswitch': function(){
      return table_add_wsswitch(this)
    },
    'add_volatile': function(){
      return table_add_volatile(this)
    },
    'add_refresh': function(){
      return table_add_refresh(this)
    },
    'add_link': function(){
      return table_add_link(this)
    },
    'add_bookmarks': function(){
      return table_add_bookmarks(this)
    },
    'add_csv': function(){
      return table_add_csv(this)
    },
    'add_column_selector': function(){
      return table_add_column_selector(this)
    },
    'add_commonality': function(){
      return table_add_commonality(this)
    },
    'invert_column_filter': function(c){
      return table_invert_column_filter(this, c)
    },
    'save_column_filters': function(){
      return table_save_column_filters(this)
    },
    'add_overlay': function(){
      return table_add_overlay(this)
    },
    'flash': function(){
      return table_flash(this)
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
  t.add_ws_handler()
  t.flash()

  function init_post_get_column_filters() {
    t.refresh()
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

