//
// column filter tool: distinct values to filtering string
//
function link_title_table(options) {
	return i18n.t("col.Table") + " " + "<span class='icon_fixed_width "+options.icon+"'>"+i18n.t("table.name."+options.name)+"</span>"
}

function values_to_filter(input, cloud){
	l = []
	var reg = new RegExp("[ ]+$", "g");
	cloud.find("a.cloud_tag").each(function(){
                s = this.text
      		s = s.replace(reg, "")
		if (s == "None") {s = "empty"}
		l.push(s)
	})
        v = '(' + l.join(",") + ')'
	input.val(v)
}

function _invert_filter(v){
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
		return v
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
		return v
	}
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
             var t = osvc.tables[id]
             if (typeof t === 'undefined') { return }
             t.refresh_child_tables()
             t.on_change()
         }
    })
}

function toggle_extratable(e) {
	var id = toggle_extraline(e)
	var d = $("<div style='background-color:white'></div>")
	d.uniqueId()
	$("#"+id).empty().append(d)
	return d.attr("id")
}

function toggle_extraline(e) {
	return toggle_extra(null, null, e, null)
}

function toggle_extra(url, id, e, ncols) {
	if ($(e).hasClass("tl")) {
		var line = $(e)
	} else {
		var line = $(e).parents(".tl").first()
	}
	if (!ncols) {
		ncols = line.children().length
	}
	var extra = $("<tr class='extraline stackable empty_on_pop'></tr>")
	extra.attr("anchor", line.attr("cksum"))
	if (line.next().is(".extraline")) {
		line.next().remove()
	}
	var td = $("<td colspan="+ncols+"></td>")
	if (id) {
		td.attr("id", id)
	} else {
		td.uniqueId()
		id = td.attr("id")
	}
	extra.css({"background-color": line.css("background-color")})
	extra.append(td)
	extra.insertAfter(line)

	// ajax load url, if specified
	if (url) {
		sync_ajax(url, [], id, function(){
			$("#"+id).removeClass("spinner")
		})
	}
	return id
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

function get_pos(e) {
	var posx = 0
	var posy = 0
	if (e.pageX || e.pageY) {
		posx = e.pageX
		posy = e.pageY
	} else if (e.clientX || e.clientY) {
		posx = e.clientX + document.body.scrollLeft
			+ document.documentElement.scrollLeft;
		posy = e.clientY + document.body.scrollTop
			+ document.documentElement.scrollTop;
	}
	return [posx, posy]
}

//
// get text selection
//
function get_selected() {
	if (window.getSelection) {
		return window.getSelection().toString()
	} else if (document.getSelection) {
		return document.getSelection().toString()
	} else {
		var selection = document.selection && document.selection.createRange()
		if (selection.text) {
			return selection.text.toString()
		}
		return ""
	}
	return ""
}

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




function table_init(opts) {
	var defaults = {
		"pager": {"page": 1},
		"extrarow": false,
		"extrarow_class": "",
		"checkboxes": true,
		"span": ["id"],
		"spankeys": ["id"],
		"keys": ["id"],
		"force_cols": [],
		"hide_cols": [],
		"columns": [],
		"colprops": {},
		"volatile_filters": false,
		"child_tables": [],
		"parent_tables": [],
		"orderby": [],
		"linkable": true,
		"sortable": true,
		"filterable": true,
		"refreshable": true,
		"bookmarkable": true,
		"exportable": true,
		"columnable": true,
		"commonalityable": true,
		"headers": true,
		"wsable": false,
		"pageable": true,
		"on_change": false,
		"events": [],
		"delay": 2000,
		"live_max_perpage": 50,
		"detached_decorate_cells": true,
		"histogram_trigger_max_line": 100000,
		"request_vars": {}
	}

	var t = {
		'options': $.extend({}, defaults, opts),
		'colprops': {},
		'need_refresh': false,
		'delay_refresh': false,
		'id': opts.id,
		'spin_class': 'fa-spin highlight',

		'bind_action_menu': function(){
			return table_bind_action_menu(this)
		},
		'action_menu_param_moduleset': function(){
			return table_action_menu_param_moduleset(this)
		},
		'action_menu_param_module': function(){
			return table_action_menu_param_module(this)
		}
	}

	t.save_prefs = function() {
		if (t.options.volatile_prefs) {
			return
		}
		osvc.user_prefs.save()
	}

	t.fold = function() {
		t.e_scroll_zone.hide()
		t.e_toolbar.addClass("grayed")
		t.e_folder.removeClass("fa-angle-down").addClass("fa-angle-up")
		if (t.e_pager) {
			t.e_pager.hide()
		}
		osvc.user_prefs.data.tables[t.id].folded = true
		t.save_prefs()
	}
	t.unfold = function() {
		t.e_toolbar.removeClass("grayed")
		t.e_folder.removeClass("fa-angle-up").addClass("fa-angle-down")
		t.e_scroll_zone.show()
		if (t.e_pager) {
			t.e_pager.show()
		}
		t.refresh()
		osvc.user_prefs.data.tables[t.id].folded = false
		t.save_prefs()
	}
	t.folded = function() {
		return !t.e_scroll_zone.is(":visible")
	}
	t.add_folder = function() {
		var e = $("<div class='icon'></div>")
		if (osvc.user_prefs.data.tables[t.id].folded) {
			e.addClass("fa-angle-up")
		} else {
			e.addClass("fa-angle-down")
		}
		e.on("click", function(event) {
			event.stopImmediatePropagation()
			if (t.folded()) {
				t.unfold()
			} else {
				t.fold()
			}
		})
		t.e_toolbar.append(e)
		t.e_folder = e
	}

	//
	// pin toolbar and header to top on scroll past
	//
	t.sticky_relocate = function() {
		if (t.folded()) {
			t.e_sticky.empty()
			return
		}
		var header_offset = $(".header").height()
		var top_offset = header_offset + t.e_header_tr.height() + t.e_toolbar.height()
		var window_top = $(window).scrollTop() + header_offset
		var table_visible = check_visible(t.div, top_offset)

		if (!table_visible) {
			t.e_sticky.empty()
			return
		}
		t.e_sticky.css({
			"width": t.e_table.parent()[0].getBoundingClientRect().width,
			"left": t.e_table.parent().offset().left
		})

		// handle table toolbar stickyness
		var table_top = t.div.offset().top
		var clone = t.e_sticky.children("div")
		if (window_top > table_top) {
			// add the top-fixed clone element if not already present
			if (clone.length == 0) {
				var clone = t.e_toolbar.clone(true, true)
				t.e_sticky.append(clone)
			}
		} else {
			clone.remove()
		}

		// handle table header stickyness
		var scroll_zone = t.e_sticky.find(".table_scroll_zone")
		var clone = scroll_zone.find("div>tr")
		if (window_top > table_top) {
			// add the top-fixed clone element if not already present
			if (scroll_zone.length == 0) {
				var clone = t.e_header_tr.clone(true, true)

				// adjust top-fixed clone element width
				scroll_zone.css({
					"width": "100%"
				})
				clone.css({
					"display": "flex",
					"width": t.e_header_tr[0].getBoundingClientRect().width
				})

				// adjust top-fixed clone element children width
				var e_children = t.e_header_tr.children()
				var i = 0
				clone.children().each(function(){
					$(this).css({
						"box-sizing": "border-box",
						"width": e_children[i].getBoundingClientRect().width
					})
					i++
				})
				var scroll_div = $("<div class='table_scroll_zone'><div style='overflow-x:hidden'></div></div>")
				scroll_div.children().append(clone)
				t.e_sticky.append(scroll_div)
			}
			// adjust left scroll position
			// adjust horizontal scroll position
			var left = t.e_header_tr.scrollParent().scrollLeft()
			clone.scrollParent().scrollLeft(left)
		} else {
			clone.parent().remove()
		}
	}

	t.add_filtered_to_visible_columns = function() {
		for (col in t.colprops) {
			if (t.options.hide_cols.indexOf(col) >= 0) {
				if (t.e_tool_column_selector_area) {
					t.e_tool_column_selector_area.find("[colname="+col+"]").prop("disabled", true).prop("checked", false)
				}
				continue
			}
			var val = t.colprops[col].current_filter
			if ((typeof val === "undefined") || (val == "")) {
				continue
			}
			if (t.options.visible_columns.indexOf(col) < 0) {
				t.options.visible_columns.push(col)
				if (t.e_tool_column_selector_area) {
					t.e_tool_column_selector_area.find("[colname="+col+"]").prop("disabled", true)
				}
			} else {
				if (t.e_tool_column_selector_area) {
					t.e_tool_column_selector_area.find("[colname="+col+"]").removeAttr("disabled")
				}
			}
		}
	}

	t.restripe_lines = function() {
		if (t.renderer != "table") {
			return
		}
		var prev_spansum = ""
		var cls = ["cell1", "cell2"]
		var cl = "cell1"
		var i = 1
		t.e_body.children(".tl").each(function(){
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

	t.trim_lines = function() {
		perpage = t.options.pager.perpage
		lines = t.e_body.children(".tl")
		if (lines.length <= perpage) {
			return
		}
		for (i=perpage; i<lines.length; i++) {
			$(lines[i]).remove()
		}
		lines = null
	}


	//
	// table horizontal scroll
	//
	t.scroll_enable = function() {
		t.scroll_left.click(function(){
			t.e_table.parent().animate({'scrollLeft': '-='+$(window).width()}, 500, t.scroll)
		})
		t.scroll_right.click(function(){
			t.e_table.parent().animate({'scrollLeft': '+='+$(window).width()}, 500, t.scroll)
		})
		$(window).on("scroll", function(){
			t.scroll()
		})
		t.e_table.parents(".table_scroll_zone>div").on("scroll", function(){
			t.scroll()
		})
		$(window).resize(function(){
			t.scroll()
			t.change_renderer()
		})
		$(".down16,.right16").click(function() {
			t.scroll()
		})
		t.scroll_enable_dom()
	}

	t.scroll = function() {
		t.scroll_disable_dom()
		t.sticky_relocate()
		var to_p = t.e_table.parent()
		var ww = to_p.width()
		var tw = t.e_table.width()
		var off = to_p.scrollLeft()
		if (ww >= tw) {
			t.scroll_left.hide()
			t.scroll_right.hide()
			t.scroll_enable_dom()
			return
		}
		if (off > 0) {
			t.scroll_left.show()
		} else {
			t.scroll_left.hide()
		}
		if (off+ww+1 < tw) {
			t.scroll_right.show()
		} else {
			t.scroll_right.hide()
		}
		t.scroll_enable_dom()
	}

	t.scroll_enable_dom = function() {
		t.e_table.on("DOMNodeInserted DOMNodeRemoved", t.scroll)
	}

	t.scroll_disable_dom = function() {
		t.e_table.off("DOMNodeInserted DOMNodeRemoved", t.scroll)
	}

	t.add_scrollers = function() {
		t.scroll_left = $("<div id='table_"+t.id+"_left' class='scroll_left'>&nbsp</div>")
		$("#table_"+t.id).prepend(t.scroll_left)
		t.scroll_right = $("<div id='table_"+t.id+"_right' class='scroll_right'>&nbsp</div>")
		$("#table_"+t.id).append(t.scroll_right)
	}

	//
	// column filter tool: invert column filter
	//
	t.invert_column_filter = function(c) {
		var val = t.colprops[c].current_filter
		if (typeof val === "undefined") {
			return
		}
		t.colprops[c].current_filter = _invert_filter(val)
		t.save_column_filters()
	}

	t.stick = function() {
		// bypass conditions
		if (t.div.parents(".tableo").length > 0) {
			return
		}
		t.sticky_relocate()
		$(".menu.flash").scroll(function(){
			t.sticky_relocate()
		})
		$(window).scroll(function(){
			t.sticky_relocate()
		})
		$(window).resize(function(){
			t.e_sticky.empty()
			t.sticky_relocate()
		})
		t.sticky_relocate()
	}

	t.get_col_header = function(col) {
		if (t.renderer != "table") {
			var e = t.e_body.find(".prop[col="+col+"]")
		} else {
			var e = t.e_header_tr.children("th[col="+col+"]")
		}
		return e
	}

	t.get_all_headers = function() {
		if (t.renderer != "table") {
			var e = t.e_body.find(".prop[col]")
		} else {
			var e = t.e_header_tr.children("th")
		}
		return e
	}

	t.reset_column_filters = function() {
		var e = t.get_all_headers()
		e.each(function() {
			$(this).removeClass("col-filtered-volatile")
			$(this).removeClass("col-filtered")
			$(this).removeClass("col-filter-changed")
		})
		t.refresh_column_headers()
		t.refresh_column_filters()
	}

	t.get_visible_columns = function() {
		// if visible columns is not explicitely set in options
		// fetch it from the db-stored user prefs
		if (t.options.visible_columns) {
			return
		}

		if (!osvc.user_prefs.data.tables[t.id]["visible_columns"] ||
		    osvc.user_prefs.data.tables[t.id]["visible_columns"].length == 0) {
			// init with default visibility defined in colprops
			if (t.options.default_columns) {
				t.options.visible_columns = t.options.default_columns
			} else {
				t.options.visible_columns = t.options.columns
			}
		} else {
			// adjust with db-stored user's prefs
			t.options.visible_columns = osvc.user_prefs.data.tables[t.id]["visible_columns"]
		}
	}

	t.add_table = function() {
		if (t.renderer == "table") {
			t.add_table_table()
		} else {
			t.add_table_grid()
		}
	}

	t.add_table_grid = function() {
		var container = $("#"+t.divid)

		var d = $("<div class='tableo'></div>")
		var toolbar = $("<div class='toolbar clickable' name='toolbar'></div>")
		var table_scroll_zone = $("<div class='table_scroll_zone'></div>")
		var table_div = $("<div></div>")
		var table = $("<div class='d-flex flex-wrap'></div>")
		t.e_sticky = $("<div class='stick'></div>")

		if (osvc.user_prefs.data.tables[t.id].folded) {
			table_scroll_zone.hide()
			toolbar.addClass("grayed")
		}

		d.attr("id", t.id)
		t.div = d
		table.attr("id", "table_"+t.id)
		table_scroll_zone.append(table_div)
		table_div.append(table)
		d.append(toolbar)
		d.append(t.e_sticky)
		d.append(table_scroll_zone)
		container.empty().append(d)
		t.e_scroll_zone = table_scroll_zone
		t.e_table = table
		t.e_header = $("<thead><tr class='theader'></tr></thead>")
		t.e_header_tr = t.e_header.children("tr")
		t.e_body = table
		t.e_toolbar = toolbar
	}

	t.add_table_table = function() {
		var container = $("#"+t.divid)

		var d = $("<div class='tableo'></div>")
		var toolbar = $("<div class='toolbar clickable' name='toolbar'></div>")
		var table_scroll_zone = $("<div class='table_scroll_zone'></div>")
		var table_div = $("<div></div>")
		var table = $("<table><thead><tr class='theader'></tr></thead><tbody></tbody></table>")
		t.e_sticky = $("<div class='stick'></div>")

		if (osvc.user_prefs.data.tables[t.id].folded) {
			table_scroll_zone.hide()
			toolbar.addClass("grayed")
		}

		d.attr("id", t.id)
		t.div = d
		table.attr("id", "table_"+t.id)
		table_scroll_zone.append(table_div)
		table_div.append(table)
		d.append(toolbar)
		d.append(t.e_sticky)
		d.append(table_scroll_zone)
		container.empty().append(d)
		t.e_scroll_zone = table_scroll_zone
		t.e_table = table
		t.e_header = table.find("thead")
		t.e_header_tr = t.e_header.children("tr")
		t.e_body = table.find("tbody")
		t.e_toolbar = toolbar
	}

	t.on_change = function() {
		if (!t.options.on_change) {
			return
		}
		t.options.on_change(t)
	}

	t.refresh_child_tables = function() {
		for (var i=0; i<t.options.child_tables.length; i++) {
			var id = t.options.child_tables[i]
			if (!(id in osvc.tables)) {
				console.log("child table not found in osvc.tables:", id)
				continue
			}
			osvc.tables[id].refresh()
		}
	}

	t.parent_table_data = function(ptid) {
		if (!(ptid in osvc.tables)) {
			console.log("table", t.id, "parent table", ptid, "not found")
			return {}
		}
		var pt = osvc.tables[ptid]
		var data = {}
		for (c in pt.colprops) {
			var current = pt.colprops[c].current_filter
			if ((current != "") && (typeof current !== 'undefined')) {
				data[pt.id+"_f_"+c] = current
			} else if ((typeof(pt.colprops[c].force_filter) !== "undefined") && (pt.colprops[c].force_filter != "")) {
				data[pt.id+"_f_"+c] = pt.colprops[c].force_filter
			}
		}
		return data
	}

	t.parent_tables_data = function() {
		if (!t.options.parent_tables || (t.options.parent_tables.length == 0)) {
			return {}
		}
		var data = {}
		for (var i=0; i<t.options.parent_tables.length; i++) {
			data = $.extend(data, t.parent_table_data(t.options.parent_tables[i]))
		}
		return data
	}

	t.is_rest_url = function() {
		if (t.options.ajax_url.match(/\/rest\//)) {
			return true
		}
		return false
	}

	t.prepare_request_commonality_url = function() {
		var url = t.options.ajax_url
		if (!t.is_rest_url()) {
			return t.options.ajax_url + "/commonality"
		}
		return t.options.ajax_url
	}

	t.prepare_request_data_url = function() {
		var url = t.options.ajax_url
		if (!t.is_rest_url()) {
			return t.options.ajax_url + "/data"
		}
		return t.options.ajax_url
	}

	t.prepare_request_col_values_url = function(col) {
		var url = t.options.ajax_url
		if (!t.is_rest_url()) {
			return t.options.ajax_url + "_col_values/"+col
		}
		return t.options.ajax_url
	}

	t.prepare_request_data = function(options) {
		if (!options) {
			options = {}
		}
		var data = t.parent_tables_data()
		if (t.id in osvc.user_prefs.data.tables) {
			data.limit = osvc.user_prefs.data.tables[t.id].perpage
		} else {
			data.limit = t.options.pager.perpage
		}
		data.offset = t.options.pager.offset
		if (t.is_rest_url()) {
			data.data_format = "table"
			data.filters = []
			if (options.col_values) {
				data.stats = true
				data.props = options.col_values
				data.limit = 0
			}
		} else {
			data.table_id = t.id
		}
		for (c in t.colprops) {
			var fid = t.id+"_f_"+c
			var f_val = null
			var current = t.colprops[c].current_filter
			if ((current != "") && (typeof current !== 'undefined')) {
				f_val = current
			} else if ((typeof(t.colprops[c].force_filter) !== "undefined") && (t.colprops[c].force_filter != "")) {
				f_val = t.colprops[c].force_filter
			}
			if (data[fid] && t.colprops[c]._class && (t.colprops[c]._class.indexOf("datetime") >= 0)) {
				f_val = t.convert_dates_in_filter(data[fid])
			}
			if (f_val == null) {
				continue
			}
			if (t.is_rest_url()) {
				data.filters.push(c+" "+f_val)
			} else {
				data[fid] = f_val
			}
		}
                data.orderby = t.options.orderby.join(",")
		return data
	}

	t.convert_dates_in_filter = function(s) {
		function convert_date(s) {
			if (s.match(/[mdhsMyY]/)) {
				// must be a delta filter => no conversion needed
				return s
			}
			var l = s.match(/([!<>=]*)(.*)/)
			// ">2016-01".match(/([!<>=]*)(.*)/) returns [">2016-01", ">", "2016-01"]
			return l[1] + osvc_date_to_collector(l[2])
		}

		var l = s.split("&")
		for (var i=0; i<l.length; i++) {
			_l = l[i].split("|")
			for (var j=0; j<_l.length; j++) {
				_l[j] = convert_date(_l[j])
			}
			l[i] = _l.join("|")
		}
		return l.join("&")

	}

	t.has_filter_in_request_vars = function() {
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

	t.set_orderby = function(c, event) {
		if (!t.options.sortable) {
			return
		}
		var desc_idx = t.options.orderby.indexOf("~"+c)
		var has_desc = (desc_idx >= 0)
		var asc_idx = t.options.orderby.indexOf(c)
		var has_asc = (asc_idx >= 0)
		if (event.ctrlKey || event.metaKey) {
			// subsort
			if (!has_desc && !has_asc) {
				// null => asc
				t.options.orderby.push(c)
			} else if (has_desc) {
				// asc => null
				t.options.orderby.splice(desc_idx, 1)
			} else {
				// asc => desc
				t.options.orderby.splice(asc_idx, 1)
				t.options.orderby.push("~"+c)
			}
		} else {
			// no subsort
			if (!has_desc && !has_asc) {
				// null => asc
				t.options.orderby = [c]
			} else if (has_desc) {
				// asc => null
				t.options.orderby = []
			} else {
				// asc => desc
				t.options.orderby = ["~"+c]
			}
		}
		t.refresh_column_headers()
		t.refresh_column_filters()
		t.refresh()
	}

	t.init_colprops = function() {
		for (var i=0; i<t.options.columns.length; i++) {
			var c = t.options.columns[i]
			t.colprops[c] = $.extend({}, colprops[c], t.options.colprops[c])
		}
	}

	t._cell_decorator = function(cell, span, line) {
                var col = cell.attr('col')
		if (span && t.options.span.indexOf(col) >= 0) {
			cell.empty()
			return
		}
		var cl = cell.attr('class')
		if (!cl) {
			return
		}
		cl = cl.split(/\s+/)
		for (i=0; i<cl.length; i++) {
			var c = cl[i]
			if (!(c in cell_decorators)) {
				continue
			}
			cell_decorators[c](cell, line)
		}
	}

	t.cell_decorator = function(lines) {
		if (!lines) {
			lines = t.e_body.children(".tl")
		}
		var spansum1 = null
		lines.each(function(){
			var line = $(this)
			if (t.renderer != "table") {
				line.children(".row").children("[cell=1]").each(function(){
					t._cell_decorator($(this), false, line.children())
				})
			} else {
				var spansum2 = line.attr("spansum")
				if (spansum1 == spansum2) {
					var span = true
				} else {
					var span = false
				}
				spansum1 = spansum2
				line.children("[cell=1]").each(function(){
					t._cell_decorator($(this), span, line)
				})
			}
		})
		return lines
	}

	t.refresh_column_headers = function() {
		if (t.renderer != "table") {
			return
		}
		if (!t.options.headers) {
			return
		}
		t.e_header_tr.empty()
		t.add_column_headers()
	}

	t.add_column_headers = function() {
		if (t.renderer != "table") {
			return
		}
		if (!t.options.headers) {
			return
		}
		if (t.options.checkboxes) {
			var th = $("<th class='text-center'><div class='fa fa-bars clickable mb-1 d-block'></div></th>")
			th.click(function(e){
				t.action_menu = table_action_menu(t, e)
				t.action_menu.menu.find("input").first().focus()
				t.scroll_to_sidepanel()
			})

			var mcb_id = t.id+"_mcb"
			var input = $("<input type='checkbox' class='ocb'></input>")
			input.attr("id", mcb_id)
			var label = $("<label></label>")
			label.attr("for", mcb_id)
			input.on("click", function(event) {
				event.stopPropagation()
				$("#am_"+t.id).remove()
				t.check_all(this.checked)
				t.highlighed_checked_lines()
				t.scroll()
			})
			th.append(input)
			th.append(label)
			t.e_header_tr.append(th)
		}

		if (t.options.extrarow) {
			t.e_header_tr.append($("<th></th>"))
		}
		for (i=0; i<t.options.columns.length; i++) {
			var c = t.options.columns[i]
			if (t.options.visible_columns.indexOf(c) >= 0) {
				t.add_column_header(c)
			}
		}
		t.bind_header_filter_selector()
	}

	t.check_all = function(checked){
		var name = t.id+"_ck"
		c = document.getElementsByName(name)
		for(i = 0; i < c.length; i++) {
			if (c[i].type == 'checkbox' && c[i].disabled == false) {
				c[i].checked = checked
				c[i].value = checked
			}
			if (checked && !(c[i].id in t.lines_checked)) {
				t.lines_checked[c[i].id] = true
			} else if (!checked && (c[i].id in t.lines_checked)) {
				delete t.lines_checked[c[i].id]
			}
		}
	}

	t.add_column_header = function(c) {
		var th = $("<th></th>")
		th.attr("col", c)
		th.text(i18n.t("col."+t.colprops[c].title))
		th.addClass(t.colprops[c]._class)
		t.set_column_header_attr(c, th)
	}

	t.set_column_header_attr = function(c, th) {
		var asc_idx = t.options.orderby.indexOf(c)
		var desc_idx = t.options.orderby.indexOf("~"+c)
		t.e_header_tr.append(th)
		if (asc_idx >= 0) {
			var order = $("<span class='icon fa-caret-down' title='"+asc_idx+"'></span>")
			order.tooltipster()
			th.prepend(order)
		}
		if (desc_idx >= 0) {
			var order = $("<span class='icon fa-caret-up' title='"+desc_idx+"'></span>")
			order.tooltipster()
			th.prepend(order)
		}
		if (t.options.sortable) {
			th.css({"cursor": "row-resize"})
			th.on("click", function(event){
				t.set_orderby(c, event)
			})
		}
	}

	t.add_column_filter_sidepanel = function (c) {
		if (t.e_filter) {
			t.e_filter.remove()
		}
		var sidepanel = t.get_sidepanel()
		var input_float = $("<div style='max-width:21em'></div>")
		var header = $("<h4></h4>")
		var input = $("<input class='oi mt-3 mb-3' style='width:100%' name='fi'>")
		var value_to_filter_tool = $("<div data-i18n='table.value_to_filter_tool_title' class='button_div icon_fixed_width values_to_filter'></div>")
		var invert_tool = $("<div data-i18n='table.invert_filter' class='button_div lightgrayed icon_fixed_width invert16'></div>")
		var clear_tool = $("<div data-i18n='table.clear_filter' class='button_div lightgrayed icon_fixed_width clear16'></div>")
		var filterbox = $("<div id='filterbox'></div>")
		var value_pie = $("<div></div>")
		var value_cloud = $("<span></span>")

		var input_id = t.id+"_f_"+c
		if (t.options.request_vars && (input_id in t.options.request_vars)) {
			input.val(t.options.request_vars[input_id])
		} else if (t.colprops[c] && (typeof t.colprops[c].current_filter !== "undefined")) {
			input.val(t.colprops[c].current_filter)
		}
		input.attr("id", input_id)
		input.attr("placeholder", i18n.t("table.filter_placeholder"))
		t.bind_filter_reformat(input, c)

		// update the column name in header
		if (c in t.colprops) {
			header.html("<span class='icon "+t.colprops[c].img+"'>"+i18n.t("col."+t.colprops[c].title)+"</span>")
		} else {
			header.html("<span class='icon "+colprops[c].img+"'>"+i18n.t("col."+colprops[c].title)+"</span>")
		}
		value_pie.attr("id", t.id+"_fp_"+c)
		value_pie.css({"margin-top": "0.8em"})
		value_cloud.attr("id", t.id+"_fc_"+c)
		value_cloud.css({"overflow-wrap": "break-word"})

		input_float.append(header)
		input_float.append(input)
		input_float.append(value_to_filter_tool)
		input_float.append(invert_tool)
		input_float.append(clear_tool)
		input_float.append(filterbox)
		input_float.append(value_pie)
		input_float.append(value_cloud)

		t.e_filter = input_float
		input_float.i18n()
		sidepanel.append(input_float)

		// clear tool click
		clear_tool.on("click", function(event){
			if ($(this).is(".lightgrayed")) {
				return
			}
			input.val("")
			input.trigger("keyup")
			t.save_column_filters()
			t.refresh_column_filters_in_place()
			t.refresh()
		})

		// invert tool click
		invert_tool.on("click", function(event){
			if ($(this).is(".lightgrayed")) {
				return
			}
			input.val(_invert_filter(input.val()))
			input.trigger("keyup")
			t.save_column_filters()
			t.refresh_column_filters_in_place()
			t.refresh()
		})

		// refresh column filter cloud on keyup
		var xhr = null
		input.on("keyup", function(event) {
			var input = $(this)
			var col = c
			t.colprops[c].current_filter = input.val()

			if (is_enter(event) || is_special_key(event)) {
				return
			}

			var val = input.val()

			// handle clear/invert tools visibibity
			if (val == "") {
				invert_tool.addClass("lightgrayed")
				clear_tool.addClass("lightgrayed")
			} else {
				invert_tool.removeClass("lightgrayed")
				clear_tool.removeClass("lightgrayed")
			}

			// handle header colorization
			var current_filter = t.colprops[c].current_filter
			if (current_filter != val) {
				t.get_col_header(col).removeClass("col-filtered").addClass("col-filter-changed")
			} else {
				t.get_col_header(col).removeClass("col-filter-changed")
				if (val != "") {
					t.get_col_header(col).addClass("col-filtered")
				}
			}

			var dest = input.siblings("[id^="+t.id+"_fc_]")
			var pie = input.siblings("[id^="+t.id+"_fp_]")
			if (t.options.pager.total > t.options.histogram_trigger_max_line) {
				dest.empty()
				pie.empty()
				return
			}
			clearTimeout(t.refresh_timer)
			t.refresh_timer = setTimeout(function validate(){
				if (xhr) {
					xhr.abort()
				}
				var data = t.prepare_request_data({"col_values": col})
				//data[input.attr('id')] = input.val()
				pie.height(0)
				xhr = $.ajax({
					type: "GET",
					url: t.prepare_request_col_values_url(col),
					data: data,
					sync: false,
					context: document.body,
					beforeSend: function(req){
						t.scroll_disable_dom()
						pie.empty()
						dest.empty()
						t.scroll_enable_dom()
						dest.addClass("icon spinner")
					},
					success: function(msg){
						var data = msg["data"][col]
						var total = msg["data"]["_total"]
						dest.removeClass("icon spinner")
						if (t.colprops[col] && t.colprops[col]._class && t.colprops[col]._class.match(/datetime/)) {
							data = t.convert_cloud_dates(data)
						}
						t.format_values_cloud(dest, data, col, total)
						t.format_values_pie(pie, data, col)
					}
				})
			}, 1000)
		})

		// validate column filter on <enter> keypress
		input.on("keypress", function(event) {
			if (is_enter(event)) {
				t.save_column_filters()
				t.refresh_column_filters_in_place()
				t.refresh()
			}
		})

		// values to column filter click
		input.siblings(".values_to_filter").on("click", function(event) {
			var input = $(this).parent().find("input")
			var ck = input.attr("id").replace("_f_", "_fc_")
			var cloud = $(this).parent().find("#"+ck)
			values_to_filter(input, cloud)
			input.trigger("keyup")
			t.colprops[c].current_filter = input.val()
			t.save_column_filters()
			t.refresh_column_filters_in_place()
			t.refresh()
		})

		input.focus().trigger("keyup")
	}

	t.refresh_column_filters = function() {
		t.e_sticky.empty()
		t.refresh_column_filters_in_place()
	}

	t.filter_submit = function(c, val) {
		t.refresh_column_filter(c, val)
		t.refresh()
	}

	t.refresh_column_filter = function(c, val) {
		if (!t.options.filterable) {
			return
		}

		if (!(c in t.colprops)) {
			return
		}

		if ((c in t.colprops) && (typeof(t.colprops[c].force_filter) !== "undefined") && (t.colprops[c].force_filter != "")) {
			val = t.colprops[c].force_filter
		}

		if (typeof(val) === "undefined") {
			val = t.colprops[c].current_filter
		} else {
			t.colprops[c].current_filter = val
		}

		// update the header cell colorization
		var th = t.get_col_header(c)
		th.removeClass("col-filtered-volatile")
		th.removeClass("col-filtered")
		th.removeClass("col-filter-changed")
		var cl = ""
		if (val && val.length > 0) {
			if (!t.options.volatile_filters) {
				th.addClass("col-filtered")
			} else {
				th.addClass("col-filtered-volatile")
			}
		}
	}

	t.refresh_column_filters_in_place = function() {
		for (i=0; i<t.options.visible_columns.length; i++) {
			var c = t.options.visible_columns[i]
			t.refresh_column_filter(c)
		}
	}

	t.set_column_filters = function() {
		if (t.options.volatile_filters || t.has_filter_in_request_vars()) {
			return
		}
		var tf = osvc.user_prefs.data.tables[t.id]["filters"]
		t.reset_column_filters()
		for (col in tf) {
			var f = tf[col]
			if (col.indexOf(".") >= 0) {
				var k = col.split('.')[1]
			} else {
				var k = col
			}
			t.refresh_column_filter(k, f)
		}
	}

	t.page_submit = function(offset){
		if (offset < 0) {
			offset = 0
		}
		t.options.pager.offset = offset
		t.refresh()
		t.refresh_column_filters_in_place()
	}

	t.hide_cells = function() {
		for (i=0; i<t.options.columns.length; i++) {
			var c = t.options.columns[i]
			if (t.options.visible_columns.indexOf(c) >= 0) {
				continue
			}
			t.e_table.find(".tl>[col="+c+"],.tl>.row>[col="+c+"]").hide()
		}
	}

	t.get_ordered_visible_columns = function() {
		// return visible columns ordered like columns
		var l = []
		for (var i=0; i<t.options.columns.length; i++) {
			var c = t.options.columns[i]
			if (t.options.visible_columns.indexOf(c) < 0 &&
			    t.options.force_cols.indexOf(c) < 0) {
				continue
			}
			l.push(c)
		}
		return l
	}

	t.check_toggle_vis = function(checked, c) {
		var idx = t.options.visible_columns.indexOf(c)
		if (checked && (idx < 0)) {
			t.options.visible_columns.push(c)
		} else if (!checked && (idx >= 0)) {
			t.options.visible_columns = t.options.visible_columns.filter(function(x){if (x!=c){return true}})
		}
		osvc.user_prefs.data.tables[t.id].visible_columns = t.options.visible_columns
		t.save_prefs()
		t.refresh_column_headers()
		t.refresh_column_filters()
		if (checked) {
			if (t.options.force_cols.indexOf(c) >=0 ) {
				t.e_table.find(".tl>[col="+c+"],.tl>.row>[col="+c+"]").show()
			} else {
				t.refresh()
			}
		}
	}

	t.bind_checkboxes = function() {
		t.e_body.children("tr").children("td:first-child").children("input[name="+t.id+"_ck]").each(function(){
			this.value = this.checked
			$(this).click(function(){
				this.value = this.checked
			})
		})
	}

	t.bind_header_filter_selector = function() {
		t.get_all_headers().each(function(){
			$(this).on("contextmenu", function(event) {
				var cell = $(event.target)
				var col = cell.attr('col')
				t.add_column_filter_sidepanel(col)
			})
		})
	}

	t.get_all_cells = function() {
		if (t.renderer != "table") {
			return t.e_body.children(".tl").children(".row").children(".cell[col]")
		} else {
			return t.e_body.children("tr").children("td[col]")
		}
	}

	t.get_col_cells = function(col) {
		if (t.renderer != "table") {
			return t.e_body.children(".tl").children(".row").children(".cell[col="+col+"]")
		} else {
			return t.e_body.children("tr").children("td[col="+col+"]")
		}
	}

	t.bind_filter_selector = function() {
		t.get_all_cells().each(function(){
			$(this).on("mouseup", function(event) {
				t.div.find(".tl.extraline").remove()
			})
			$(this).on("contextmenu", function(event) {
				var cell = $(event.target)
				if (typeof cell.attr("cell") === 'undefined') {
					cell = cell.parents("[cell=1]").first()
				}
				t.filter_selector(event, cell.attr('col'), $.data(cell[0], 'v'))
			})
		})
	}

	t.prop_fmt = function(k) {
		var prop = $("<div class='prop text-gray col-4 align-self-center'></div>")
			.attr("col", k)
		if ((k != "extra") && (t.options.visible_columns.indexOf(k) < 0)) {
			prop.addClass("hidden")
		}
		if (k in t.colprops) {
			prop.text(i18n.t("col."+t.colprops[k].title))
		}
		t.set_column_header_attr(k, prop)
		return prop
	}

	t.cell_fmt = function(k, v) {
		var cl = ""
		var classes = ["cell"]
		if ((k == "extra") && (typeof(t.options.extrarow_class) !== 'undefined')) {
			classes.push(t.options.extrarow_class)
		}
		if ((k != "extra") && (t.options.visible_columns.indexOf(k) < 0)) {
			classes.push("hidden")
		}
		if (k in t.colprops) {
			if (t.colprops[k]._class) {
				classes = classes.concat(t.colprops[k]._class.split(" "))
			}
			if (t.colprops[k]._dataclass) {
				classes = classes.concat(t.colprops[k]._dataclass.split(" "))
			}
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
		if (t.renderer != "table") {
			var s = $("<div cell='1' col='"+k+"' "+cl+">"+text+"</div>")
		} else {
			var s = $("<td cell='1' col='"+k+"' "+cl+">"+text+"</td>")
		}
		$.data(s[0], "v", v)
		return s
	}

	t.last_checkbox_clicked = null

	t.checkbox_click = function(e) {
		$("#am_"+t.id).remove()
		var ref_id = $(e.target).attr("id")
		var new_checked = $(e.target).prop("checked")
		if (new_checked && !(ref_id in t.lines_checked)) {
			t.lines_checked[ref_id] = true
		} else if (!new_checked && (ref_id in t.lines_checked)) {
			delete t.lines_checked[ref_id]
		}
		if (e.shiftKey && t.last_checkbox_clicked) {
			var cbs = t.div.find("input[name="+t.id+"_ck]")
			var start = -1
			var end = -1
			for (var i=0; i<cbs.length; i++) {
				var cb = $(cbs[i])
				if ((cb.attr("id")!=ref_id) && (cb.attr("id")!=t.last_checkbox_clicked)) {
					continue
				}
				if (start < 0) {
					start = i
				} else {
					end = i
				}
			}
			// at least one checkbox between start and end
			for (var i=start+1; i<end; i++) {
				var cb = $(cbs[i])
				var cbid = cb.attr("id")
				var new_checked = !cb.prop("checked")
				cb.prop("checked", new_checked)
				if (new_checked && !(cbid in t.lines_checked)) {
					t.lines_checked[cbid] = true
				} else if (!new_checked && (cbid in t.lines_checked)) {
					delete t.lines_checked[cbid]
				}
			}
		}
		t.last_checkbox_clicked = ref_id
		t.highlighed_checked_lines(e)
	}
	t.highlighed_checked_lines = function(event) {
		if (event && $("#am_"+t.id).length > 0) {
			table_action_menu(t, event)
		}
		t.div.find("input[name="+t.id+"_ck]").each(function(){
			var line = $(this).parents(".tl").first()
			if ($(this).is(":checked")) {
				line.addClass("tl_checked")
			} else {
				line.removeClass("tl_checked")
			}
			line.next(".extraline").css({"background-color": line.css("background-color")})
		})
	}

	t.line_cksum = function(line, sum) {
		if (sum == "keys") {
			var keys = t.options.keys
		} else if (sum == "span") {
			var keys = t.options.spankeys
		}
		if (!keys) {
			return ""
		}
		var colindex = []
		var cols = t.get_ordered_visible_columns()
		for (var i=0; i<keys.length; i++) {
			index = cols.indexOf(keys[i])
			if (index < 0) {
				continue
			}
			colindex.push(index)
		}
		var s = ""
		for (var i=0; i<colindex.length; i++) {
			s += line[colindex[i]]
		}
		return md5(s)
	}

	t.data_to_lines = function (data) {
		if (t.renderer == "table") {
			return t.data_to_lines_table(data)
		} else {
			return t.data_to_lines_grid(data)
		}
	}

	t.data_to_lines_table = function (data) {
		var lines = $("<span></span>")
		for (var i=0; i<data.length; i++) {
			var cksum = t.line_cksum(data[i], "keys")
			var spansum = t.line_cksum(data[i], "span")
			var line = $("<tr class='tl h' spansum='"+spansum+"' cksum='"+cksum+"'></tr>")
			var ckid = t.id + "_ckid_" + cksum
			if (t.options.checkboxes) {
				var cb = $("<input class='ocb' type='checkbox' id='"+ckid+"' name='"+t.id+"_ck'>")
				var label = $("<label for='"+ckid+"'></label>")
				var td = $("<td name='"+t.id+"_tools' class='tools'></td>")
				if (ckid in t.lines_checked) {
					cb.prop("checked", true)
				}
				td.append([cb, label])
				line.append(td)
				cb.on("click", t.checkbox_click)
			}
			if (t.options.extrarow) {
				var k = "extra"
				var v = ""
				var cell = t.cell_fmt(k, v)
				line.append(cell)
			}
			var cols = t.get_ordered_visible_columns()
			for (var j=0; j<cols.length; j++) {
				var k = cols[j]
				var v = data[i][j]
				var cell = t.cell_fmt(k, v)
				line.append(cell)
			}
			lines.append(line)
		}
		return lines.children().detach()
	}

	t.data_to_lines_grid = function (data) {
		var lines = $("<span></span>")
		for (var i=0; i<data.length; i++) {
			var cksum = t.line_cksum(data[i], "keys")
			var spansum = t.line_cksum(data[i], "span")
			var line = $("<div class='tl h col-sm-12 col-md-6 col-lg-4 col-xl-3 pt-3 pb-3 container-auto' spansum='"+spansum+"' cksum='"+cksum+"'></div>")
			var ckid = t.id + "_ckid_" + cksum
			if (t.options.checkboxes) {
				var cb = $("<input class='ocb' type='checkbox' id='"+ckid+"' name='"+t.id+"_ck'>")
				var label = $("<label for='"+ckid+"'></label>")
				var td = $("<div name='"+t.id+"_tools' class='tools'></div>")
				if (ckid in t.lines_checked) {
					cb.prop("checked", true)
				}
				td.append([cb, label])
				line.append(td)
				cb.on("click", t.checkbox_click)
			}
			if (t.options.extrarow) {
				var k = "extra"
				var v = ""
				var prop = t.prop_fmt(k)
				var cell = t.cell_fmt(k, v)
				cell.addClass("col")
				var _line = $("<div class='row'></div>").append([prop, cell])
				line.append(_line)
			}
			var cols = t.get_ordered_visible_columns()
			for (var j=0; j<cols.length; j++) {
				var k = cols[j]
				var v = data[i][j]
				var prop = t.prop_fmt(k)
				var cell = t.cell_fmt(k, v)
				cell.addClass("col")
				var _line = $("<div class='row'></div>").append([prop, cell])
				line.append(_line)
			}
			lines.append(line)
		}
		return lines.children().detach()
	}

	t.refresh_callback = function(msg){
		// don't install the new data if nothing has changed.
		// avoids flickering and useless client load.
		var md5sum = md5(JSON.stringify(msg))
		if (md5sum == t.md5sum) {
			var msg = ""
			console.log("refresh: data unchanged,", md5sum)
			t.need_refresh = false
			t.unset_refresh_spin()
			return
		}
		console.log("refresh: data changed,", md5sum)
		t.md5sum = md5sum

		// disable DOM insert event trigger for perf
		t.need_refresh = false
		t.scroll_disable_dom()

		if (is_dict(msg) && "data" in msg) {
			t.lines = msg["data"]
			t.options.pager = msg['meta']
		} else {
			t.div.html(msg)
			return
		}
		t.redraw()
	}

	t.redraw = function() {
		msg = t.data_to_lines(t.lines)
		if (t.options.detached_decorate_cells) {
			msg = t.cell_decorator(msg)
		}

		// detach extralines
		var extralines = t.e_body.children(".extraline:visible").detach()

		// detach old lines
		var old_lines = $("<tbody></tbody>").append(t.e_body.children(".tl").detach())

		// insert new lines
		t.e_body.append(msg)

		if (!t.options.detached_decorate_cells) {
			msg = t.cell_decorator(msg)
		}

		// reattach extralines
		extralines.each(function(){
			var cksum = $(this).attr("anchor")
			var new_line = t.e_body.children(".tl[cksum="+cksum+"]")
			if (new_line.length == 0) {
				// the extraline parent line disappeared
				return
			}
			// the extraline parent line is still there in the new dataset
			var content = $(this).children("td:last").children().detach()
			var id = toggle_extraline(new_line.get(0))
			$("#"+id).append(content)
		})
		extralines.remove()

		t.e_body.children(".tl").each(function(){
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
				if ($.data(old_cell[0], "v") == $.data(new_cell[0], "v")) {
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

		t.pager()
		t.add_filtered_to_visible_columns()
		t.bind_checkboxes()
		t.bind_filter_selector()
		t.bind_action_menu()
		t.restripe_lines()
		t.hide_cells()
		t.unset_refresh_spin()
		t.e_body.find(".tl").children(".tohighlight").removeClass("tohighlight").effect("highlight", 1000)
		t.scroll_enable_dom()
		t.scroll()
		t.highlighed_checked_lines()

		if (t.renderer != "table") {
			t.refresh_column_filters_in_place()
			t.bind_header_filter_selector()
		}

		t.refresh_child_tables()
		t.on_change()

		if (t.need_refresh) {
			t.e_tool_refresh.trigger("click")
		}
	}

	t.insert = function(data) {
		var params = {}
		if (!t.is_rest_url()) {
			params.table_id = t.id
		}
		for (i=0; i<data.length; i++) {
			try {
				var key = data[i]["key"]
				var val = data[i]["val"]
				var op = data[i]["op"]
				params[t.id+"_f_"+key] = op+val
			} catch(e) {
				return
			}
		}
		for (c in t.colprops) {
			if (c == key) {
				continue
			}
			var current = t.colprops[c].current_filter

			if ((current != "") && (typeof current !== 'undefined')) {
				params[t.id+"_f_"+c] = current
			} else if ((typeof(t.colprops[c].force_filter) !== "undefined") && (t.colprops[c].force_filter != "")) {
				params[t.id+"_f_"+c] = t.colprops[c].force_filter
			}
		}
		params.props = t.get_ordered_visible_columns().join(',')
		$.ajax({
			type: "GET",
			url: t.prepare_request_data_url(),
			data: params,
			context: document.body,
			beforeSend: function(req){
				t.set_refresh_spin()
			},
			success: function(msg){
				t.need_refresh = false

				// disable DOM insert event trigger for perf
				t.scroll_disable_dom()

				if (!is_dict(msg) || !("data" in msg)) {
					return
				}
				var lines = msg['data']
				t.options.pager = msg['meta']

				msg = t.data_to_lines(lines)

				// replace already displayed lines
				modified = []

				n_new_lines = 0

				$(msg).each(function(){
					n_new_lines += 1
					new_line = $(this)
					cksum = new_line.attr("cksum")
					$("#table_"+t.id).find("[cksum="+cksum+"]").each(function(){
						$(this).before(new_line)
						for (i=1; i<$(this).children().length+1; i++) {
							cell = $(":nth-child("+i+")", this)
							if (!cell.is(":visible")) {
								continue
							}
							new_cell = $(":nth-child("+i+")", new_line)
							if ($.data(cell[0], "v") == $.data(new_cell[0], "v")) {
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
				t.cell_decorator()

				$(".highlight").each(function(){
					$(this).removeClass("highlight")
					$(this).effect("highlight", 1000)
				})

				t.unset_refresh_spin()
				t.scroll_enable_dom()
				t.scroll()

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

	t.refresh = function() {
		if (t.div.length > 0 && !t.div.is(":visible")) {
			return
		}
		if (t.folded()) {
			return
		}
		if (t.delay_refresh || t.e_title.hasClass("table_refresh")) {
			t.need_refresh = true
			return
		} else {
			t.set_refresh_spin()
		}

		var data = t.prepare_request_data()

		data.props = t.get_ordered_visible_columns().join(',')
		data["offset"] = t.options.pager.offset
		$.ajax({
			type: "GET",
			url: t.prepare_request_data_url(),
			data: data,
			context: document.body,
			beforeSend: function(req){
				t.div.find(".nodataline>td").text(i18n.t("api.loading"))
			},
			success: t.refresh_callback,
			error: function(e) {
				if((e.status != 403) && (e.state() == "rejected")) {
					// redirect to the security exception form
					document.location = document.location
				}
			}
		})
	}

	t.link = function() {
		if (t.options.caller) {
			t.link_fn()
		} else {
			t.link_href()
		}
	}

	t.link_fn = function() {
		var options = t.options
		options.volatile_filters = true

		// fset
		var current_fset = $("[name=fset_selector]").find("span").attr("fset_id")
		options.fset_id = current_fset

		// col filters
		for (c in t.colprops) {
			var val = t.colprops[c].current_filter
			if ((val == "") || (typeof val === "undefined")) {
				continue
			}
			options.request_vars[t.id+'_f_'+c] = val
		}
		osvc_create_link(t.options.caller, options, "link_title_table", {"icon": t.options.icon, "name": t.options.name})
	}

	t.link_href = function() {
		var url = get_view_url()
		url = url.replace(/#$/, "")+"?";
		var args = "clear_filters=true&discard_filters=true"

		// fset
		var current_fset = $("[name=fset_selector]").find("span").attr("fset_id")
		args += "&dbfilter="+current_fset

		// col filters
		for (c in t.colprops) {
			var val = t.colprops[c].current_filter
			if ((val == "") || (typeof val === "undefined")) {
				continue
			}
			args += '&'+t.id+"_"+c+"="+encodeURIComponent(val)
		}
		osvc_create_link(url, args, "link_title_table", {"name": t.options.name})
	}

	t.position_on_pointer = function(event, e) {
		var pos = $(event.target).position()
		var szpos = t.div.children(".table_scroll_zone").position()
		e.css({
			"left": pos.left + szpos.left + "px",
			"top": pos.top + szpos.top + $(event.target).height() + "px"
		})
		keep_inside(e[0])
	}

	t.filter_selector = function(e, k, v) {

		// open the filter sidepanel
		t.add_column_filter_sidepanel(k)
		t.add_filterbox()

		// reset selected toggles
		t.e_fsr.find(".bgred").each(function(){
			$(this).removeClass("bgred")
		})

		// get selected text
		try {
			var sel = window.getSelection().toString()
		} catch(e) {
			var sel = document.selection.createRange().text
		}
		if (sel.length == 0) {
			sel = v
		}

		// store original sel
		var _sel = sel

		function mangle_sel(){
			var __sel = _sel
			if (t.e_fsr.find("#fsrwildboth").hasClass("bgred")) {
				__sel = '%' + __sel + '%'
			} else if (t.e_fsr.find("#fsrwildleft").hasClass("bgred")) {
				__sel = '%' + __sel
			} else if (t.e_fsr.find("#fsrwildright").hasClass("bgred")) {
				__sel = __sel + '%'
			}
			if (t.e_fsr.find("#fsrneg").hasClass("bgred")) {
				__sel = '!' + __sel
			}
			return __sel
		}

		t.e_fsr.find("#fsrview").each(function() {
			$(this).text(t.colprops[k].current_filter)
			$(this).off()
			$(this).on("contextmenu dblclick", function(){
				sel = $(this).text()
				t.colprops[k].current_filter = sel
				t.e_sidepanel.find("input[name=fi]").val(sel).trigger("keyup")
				t.save_column_filters()
				t.refresh_column_filters_in_place()
				t.refresh()
				t.e_fsr.hide()
			})
			$(this).on("click", function() {
				cur = $(this).text()
				//cur = sel
				$(this).removeClass("highlight")
				$(this).addClass("b")
				t.colprops[k].current_filter = cur
				t.e_sidepanel.find("input[name=fi]").val(cur).trigger("keyup")
				t.get_col_header(k).each(function() {
					$(this).removeClass("col-filtered")
					$(this).addClass("col-filter-changed")
				})
			})
		})
		t.e_fsr.find("#fsrreset").each(function(){
			$(this).off()
			$(this).on("click", function(){
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(t.colprops[k].current_filter)
					$(this).removeClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrclear").each(function(){
			$(this).off()
			$(this).on("click", function(){
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text("")
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrneg").each(function(){
			$(this).off()
			$(this).on("click", function(){
				if ($(this).hasClass("bgred")) {
					$(this).removeClass("bgred")
				} else {
					$(this).addClass("bgred")
				}
				sel = mangle_sel()
			})
		})
		t.e_fsr.find("#fsrwildboth").each(function(){
			$(this).off()
			$(this).on("click", function(){
				if ($(this).hasClass("bgred")) {
					$(this).removeClass("bgred")
				} else {
					t.e_fsr.find("[id^=fsrwild]").each(function(){
						$(this).removeClass("bgred")
					})
					$(this).addClass("bgred")
				}
				sel = mangle_sel()
			})
		})
		t.e_fsr.find("#fsrwildleft").each(function(){
			$(this).off()
			$(this).on("click", function(){
				if ($(this).hasClass("bgred")) {
					$(this).removeClass("bgred")
				} else {
					t.e_fsr.find("[id^=fsrwild]").each(function(){
						$(this).removeClass("bgred")
					})
					$(this).addClass("bgred")
				}
				sel = mangle_sel()
			})
		})
		t.e_fsr.find("#fsrwildright").each(function(){
			$(this).off()
			$(this).on("click", function(){
				if ($(this).hasClass("bgred")) {
					$(this).removeClass("bgred")
				} else {
					t.e_fsr.find("[id^=fsrwild]").each(function(){
						$(this).removeClass("bgred")
					})
					$(this).addClass("bgred")
				}
				sel = mangle_sel()
			})
		})
		t.e_fsr.find("#fsreq").each(function(){
			$(this).off()
			$(this).on("click", function(){
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(sel)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrandeq").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '&' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsroreq").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '|' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrsup").each(function(){
			$(this).off()
			$(this).on("click", function(){
				val = '>' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrandsup").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '&>' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrorsup").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '|>' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrinf").each(function(){
			$(this).off()
			$(this).on("click", function(){
				val = '<' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrandinf").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '&<' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrorinf").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				val = cur + '|<' + sel
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrempty").each(function(){
			$(this).off()
			$(this).on("click", function(){
				if (t.e_fsr.find("#fsrneg").hasClass("bgred")) {
					val = '!empty'
				} else {
					val = 'empty'
				}
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrandempty").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				if (t.e_fsr.find("#fsrneg").hasClass("bgred")) {
					val = cur + '&!empty'
				} else {
					val = cur + '&empty'
				}
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
		t.e_fsr.find("#fsrorempty").each(function(){
			$(this).off()
			$(this).on("click", function(){
				cur =  t.colprops[k].current_filter
				if (t.e_fsr.find("#fsrneg").hasClass("bgred")) {
					val = cur + '|!empty'
				} else {
					val = cur + '|empty'
				}
				t.e_fsr.find("#fsrview").each(function(){
					$(this).text(val)
					$(this).addClass("highlight")
				})
			})
		})
	}

	t.add_filterbox = function() {
		var s = "<div id='fsr"+t.id+"' class='right_click_menu'>"
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
		s += "</div>"
		t.e_fsr = $(s)
		t.e_sidepanel.find("#filterbox").html(t.e_fsr)
	}

	t.save_column_filters = function() {
		if (t.options.volatile_filters) {
			return
		}
		var data = []
		var del_data = []

		for (c in t.colprops) {
			var val = t.colprops[c].current_filter
			if (val != "" && (typeof val !== "undefined")) {
				// filter value to save
				osvc.user_prefs.data.tables[t.id].filters[c] = val
			} else if (c in osvc.user_prefs.data.tables[t.id].filters) {
				// filter to delete
				delete osvc.user_prefs.data.tables[t.id].filters[c]
			}
		}
		t.save_prefs()
	}

	t.unset_refresh_spin = function() {
		if (t.e_title) {
			t.e_title.removeClass("table_refresh")
			t.e_sticky.find(".table_title").removeClass("table_refresh")
		}
		if (!t.e_tool_refresh_spin) {
			return
		}
		t.e_tool_refresh_spin.removeClass(t.spin_class)
		t.delay_refresh = true
		t.e_tool_refresh_spin.addClass("grayed")
		setTimeout(function(){
			t.delay_refresh = false
			t.e_tool_refresh_spin.removeClass("grayed")
			if (t.need_refresh) {
				t.refresh()
			}
		}, t.options.delay)
	}

	t.set_refresh_spin = function() {
		if (t.e_title) {
			t.e_title.addClass("table_refresh")
			t.e_sticky.find(".table_title").addClass("table_refresh")
		}
		if (t.e_tool_refresh_spin) {
			t.e_tool_refresh_spin.addClass(t.spin_class)
		}
	}

	t.add_ws_handler = function() {
		if (!t.options.events || (t.options.events.length == 0)) {
			return
		}
		console.log("register table", t.id, t.options.events.join(","), "event handler")
		wsh[t.id] = function(data) {
			if (t.options.events.indexOf(data["event"]) < 0) {
				return
			}
			if (!t.live_enabled()) {
				return
			}
			t.refresh()
		}
	}

	t.add_pager = function() {
		if (!t.options.pageable) {
			return
		}
		var e = $("<div class='pager hidden'></div>")
		t.e_toolbar.prepend(e)
		t.e_pager = e
	}

	t.bind_filter_reformat = function(input, attr) {
		if ( typeof(attr) == 'undefined' || attr == false ) {
			return
		}
		if ( ! attr.match(/nodename/gi) &&
		     ! attr.match(/svcname/gi) &&
		     ! attr.match(/fqdn/gi) &&
		     ! attr.match(/assetname/gi) &&
		     ! attr.match(/svc_id/gi) &&
		     ! attr.match(/node_id/gi) &&
		     ! attr.match(/disk_id/gi) &&
		     ! attr.match(/disk_svcname/gi) &&
		     ! attr.match(/save_svcname/gi)
		) {return}
		input.on("change keyup input", function(){
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
	}

	t.format_values_cloud = function(span, data, col, total) {
		span.removeClass("spinner")

		var keys = []
		var max = 0
		var min = Number.MAX_SAFE_INTEGER 
		var delta = 0
		for (key in data) {
			keys.push(key)
			n = data[key]
			if (n > max) max = n
			if (n < min) min = n
		}
		delta = max - min
		if (!total) {
			var total = keys.length
		}

		// header
		var header = $("<h4></h4>")
		header.text(i18n.t("table.unique_matching_values", {"count": total}))
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
		t.scroll_disable_dom()
		for (var i=0; i<skeys.length ; i++) {
			var key = skeys[i]
			var n = data[key]
			if (delta > 0) {
				var size = 100 + 100. * (n - min) / delta
			} else {
				var size = 100
			}

			e = $("<a class='h cloud_tag' style='font-size:"+size+"%'>"+key+"</a>")
			e.attr("title", i18n.t("table.number_of_occurence", {"count": data[key]})).tooltipster()
			span.append([e, "&nbsp;&nbsp;"])
		}
		t.scroll_enable_dom()
		span.children("a").on("click", trigger)

		function trigger() {
			span.siblings("input").val($(this).text()).trigger("keyup")
			t.colprops[col].current_filter = $(this).text()
			t.refresh()
			t.refresh_column_filters_in_place()
			t.save_column_filters()
		}
	}

	t.format_values_pie = function(o, data, col) {
		require(["jqplot"], function() {t._format_values_pie(o, data, col)})
	}

	t._format_values_pie = function(o, data, col) {
		o.empty()

		// avoid ploting too difuse datasets and single pie dataset
		var n = Object.keys(data).length
		if ((n > 200) || (n < 2)) {
			return
		}

		o.height("15em")
		o.width("100%")

		// format as jqplot expects
		var l = []
		for (key in data) {
			l.push([key, data[key]])
		}

		l.sort(function(a, b){
			if(a[1] < b[1]) return 1;
			if(a[1] > b[1]) return -1;
			return 0;
		})

		// jqplot pie aspect
		options = {
			grid:{
				background: 'transparent',
				borderColor: 'transparent',
				shadow: false,
				drawBorder: false,
				shadowColor: 'transparent'
			},
			seriesDefaults: {
				sortData: true,
				renderer: $.jqplot.PieRenderer,
				shadow: false,
				//seriesColors: c,
				rendererOptions: {
					padding: 10,
					sliceMargin: 4,
					dataLabelPositionFactor: 1,
					startAngle: -90,
					dataLabelThreshold: 4,
					dataLabelNudge: 12,
					dataLabels: 'percent',
					showDataLabels: true
				}
			},
			legend: {
				show:false,
			}
		}
		$.jqplot(o.attr('id'), [l], options)
		o.off('jqplotDataHighlight')
		o.off('jqplotDataUnhighlight')
		o.off('jqplotDataClick')
		o.on('jqplotDataHighlight', function(ev, seriesIndex, pointIndex, data) {
			var val = data[0]
			$(this).next().find("a").each(function(){
				$(this).removeClass("pie_hover")
				if ($(this).text() == val) {
					$(this).addClass("pie_hover")
				}
			})
		})
		o.on('jqplotDataUnhighlight', function(ev, seriesIndex, pointIndex, data) {
			$(this).next().find("a").removeClass("pie_hover")
		})
		o.on('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
			var val = data[0]
			var input = $(this).siblings("input")
			input.val(val)
			input.trigger("keyup")
			t.colprops[col].current_filter = val
			t.refresh()
			t.refresh_column_filters_in_place()
			t.save_column_filters()
		})
	}

	t.convert_cloud_dates = function(data) {
		var _data = {}
		for (var d in data) {
			_data[osvc_date_from_collector(d)] = data[d]
		}
		return _data
	}

	//
	// table tool: link
	//
	t.add_link = function() {
		if (!t.options.linkable) {
			return
		}
		var e = $("<div class='button_div clickable' name='tool_link'></div>")
		var span = $("<span class='icon_fixed_width link16' data-i18n='table.link'></span>")
		span.attr("title", i18n.t("table.link_help")).tooltipster()
		e.append(span)
		try { e.i18n() } catch(e) {}

		// bindings
		e.on("click", function(event) {
			event.stopPropagation()
			t.link()
		})

		$(this).on("keypress", function() {
			if ($('input').is(":focus")) { return }
			if ($('textarea').is(":focus")) { return }
			if ( event.which == 108 ) {
				t.link()
			}
		})

		t.e_tool_link = e
		return e
	}

	//
	// table tool: csv export
	//
	t.add_csv = function() {
		if (!t.options.exportable) {
			return
		}

		var e = $("<div class='button_div clickable' name='tool_csv'></div>")
		t.e_tool_csv = e

		var span = $("<span class='icon_fixed_width csv' data-i18n='table.csv'></span>")
		e.append(span)

		e.on("click", function(event) {
			event.stopPropagation()
			var _e = t.e_tool_csv.children("span")
			if (!_e.hasClass("csv")) {
				return
			}
			_e.removeClass("csv").addClass("csv_disabled")
			setTimeout(function() {
				_e.removeClass("csv_disabled").addClass("csv")
			}, 10000)

			var data = t.prepare_request_data()
			var l = []
			for (k in data) {
				l.push(encodeURIComponent(k)+"="+encodeURIComponent(data[k]))
			}
			var q = l.join("&")
			var url = t.options.ajax_url+"/csv"
			if (q.length > 0) {
				url += "?"+q
			}
			document.location.href = url
		})
		try { e.i18n() } catch(e) {}
		return e
	}

	//
	// table tool: refresh
	//
	t.add_refresh = function() {
		if (!t.options.refreshable) {
			return
		}

		var e = $("<div class='button_div clickable' name='tool_refresh'><span class='fa refresh16'></span><span style='padding-left:0.45em'></span></div>")
		e.children().last().text(i18n.t('table.refresh'))

		// bindings
		e.on("click", function(event) {
			event.stopPropagation()
			t.refresh()
		})

		$(this).on("keypress", function() {
			if ($('input').is(":focus")) { return }
			if ($('textarea').is(":focus")) { return }
			if ( event.which == 114 ) {
				t.refresh()
			}
		})

		t.e_tool_refresh = e
		t.e_tool_refresh_spin = e.find(".refresh16")
		return e
	}

	//
	// table tool: websocket toggle
	//
	t.add_wsswitch = function() {
		if (!t.options.wsable) {
			return
		}

		// checkbox
		var input = $("<input type='checkbox' class='ocb' />")
		input.uniqueId()

		// label
		var label = $("<label></label>")
		label.attr("for", input.attr("id"))

		// title
		var title = $("<span data-i18n='table.live' style='padding-left:0.3em;'></span>")
		title.attr("title", i18n.t("table.live_help")).tooltipster()

		// container
		var e = $("<div class='button_div'></div>")
		e.append(input)
		e.append(label)
		e.append(title)
		try { e.i18n() } catch(e) {}

		if (t.live_enabled()) {
			input.prop("checked", true)
			t.pager()
		} else {
			input.prop("checked", false)
		}

		e.on("click", function(event) {
			event.stopImmediatePropagation()
			var input = $(this).children("input")
			if (input.is(":checked")) {
				input.prop("checked", false)
				current_state = 0
			} else {
				input.prop("checked", true)
				current_state = 1
			}

			osvc.user_prefs.data.tables[t.id].wsenabled = current_state
			t.save_prefs()

			if (t.need_refresh && current_state == 1) {
				// honor past change events
				t.refresh()
			}

			// refresh perpage table tool
			var selector = t.add_perpage_selector()
			t.e_sidepanel.find("[name=perpage]").html(selector.html())
		})

		t.e_wsswitch = e
		return e
	}

	t.live_enabled = function() {
		if (!("wsenabled" in osvc.user_prefs.data.tables[t.id]) || osvc.user_prefs.data.tables[t.id].wsenabled) {
			return true
		}
		return false
	}

	//
	// table tool: volatile toggle
	//
	t.add_volatile = function() {
		if (!t.options.headers || !t.options.filterable) {
			return
		}

		// checkbox
		var input = $("<input type='checkbox' class='ocb' />")
		if (t.options.volatile_filters) {
			input.prop("checked", true)
		}
		input.uniqueId()

		// label
		var label = $("<label></label>")
		label.attr("for", input.attr("id"))

		// title
		var title = $("<span style='padding-left:0.3em'></span>")
		title.text(i18n.t("table.volatile"))
		title.attr("title", i18n.t("table.volatile_help")).tooltipster()

		// container
		var e = $("<div class='button_div'></div>")
		e.append(input)
		e.append(label)
		e.append(title)

		e.on("click", function(event) {
			event.stopImmediatePropagation()
			var input = $(this).children("input")
			var current_state
			if (input.is(":checked")) {
				input.prop("checked", false)
				current_state = false
			} else {
				input.prop("checked", true)
				current_state = true
			}
			t.options.volatile_filters = current_state
			t.refresh_column_filters_in_place()
		})

		return e
	}

	//
	// create the tools sidepanel
	//
	t.add_tools_panel = function() {
		if (t.folded()) {
			return
		}
		var sidepanel = t.get_sidepanel()
		sidepanel.append(t.add_commonality())
		sidepanel.append(t.add_column_selector())
		sidepanel.append(t.add_csv())
		sidepanel.append(t.add_bookmarks())
		sidepanel.append(t.add_link())
		sidepanel.append(t.add_refresh())
		sidepanel.append(t.add_wsswitch())
		sidepanel.append(t.add_volatile())
		sidepanel.append(t.add_renderer_selector())
		sidepanel.append(t.add_perpage_selector())
		sidepanel.append(t.add_filters_summary())
		t.scroll_to_sidepanel()
	}

	t.scroll_to_sidepanel = function() {
		t.e_sidepanel.parents("body,.menu").first().scrollTop(0)
	}

	//
	// table tools toggle
	//
	t.add_tools_toggle = function() {
		t.e_toolbar.on("click", function() {
			t.unfold()
			t.add_tools_panel()
		})
	}

	t.add_table_title = function() {
		// add the table title
		var title = $("<div class='table_title'></div>")
		title.text(i18n.t("table.name."+t.options.name))
		t.e_title = title
		t.e_toolbar.append(title)
	}

	t.clear_current_filters = function() {
		for (c in t.colprops) {
			var current = t.colprops[c].current_filter
			if ((current == "") || (typeof current === 'undefined')) {
				continue
			}
			if ((typeof(t.colprops[c].force_filter) !== "undefined") && (t.colprops[c].force_filter != "")) {
				continue
			}
			t.colprops[c].current_filter = ""
		}
	}

	//
	// table tool: filters summary
	//
	t.add_filters_summary = function () {
		var e = $("<div class='pl-3 pr-3 pb-3'></div>")
		var _e = $("<div class='d-flex pb-2'></div>")
		var title = $("<div class='pb-2'></div>").text(i18n.t("table.filters"))
		var tools = $("<span style='flex:1;text-align:right'></div>")
		var clear_tool = $("<span class='icon clear16 clickable'></span>")
		tools.append(clear_tool)
		_e.append(title)
		_e.append(tools)
		e.append(_e)

		// clear all filters
		clear_tool.on("click", function(event){
			t.clear_current_filters()
			t.save_column_filters()
			t.refresh_column_filters_in_place()
			t.refresh()
			t.add_tools_panel()
		})

		for (c in t.colprops) {
			var current = t.colprops[c].current_filter
			if ((current == "") || (typeof current === 'undefined')) {
				continue
			}
			var _e = $("<div class='d-flex pt-2 pb-2 pl-2' style='border-top: 1px solid rgba(220, 220, 220, 0.2);'></div>")
			if ((typeof(t.colprops[c].force_filter) !== "undefined") && (t.colprops[c].force_filter != "")) {
				current = t.colprops[c].force_filter
				var force = true
			} else {
				var force = false
			}
			var left = $("<div></div>")
			var colname = $("<div class='icon_fixed_width nowrap'></div>")
			var val = $("<div class='trunc20'>"+current+"</div>")
			colname.text(i18n.t("col."+t.colprops[c].title))
			colname.addClass(t.colprops[c].img)
			if (current.length > 20) {
				val.attr("title", current).tooltipster()
			}
			left.append([colname, val])
			_e.append(left)
			if (!force) {
				var tools = $("<span style='flex:1;text-align:right'></div>")
				var clear_tool = $("<span class='icon clear16 clickable'></span>")
				var invert_tool = $("<span class='icon invert16 clickable'></span>")
				clear_tool.attr("col", c)
				invert_tool.attr("col", c)
				tools.append(clear_tool)
				tools.append(invert_tool)
				_e.append(tools)

				clear_tool.on("click", function(event){
					var c = $(this).attr("col")
					t.colprops[c].current_filter = ""
					t.save_column_filters()
					t.refresh_column_filters_in_place()
					t.refresh()
					t.add_tools_panel()
				})
				invert_tool.on("click", function(event){
					var c = $(this).attr("col")
					t.colprops[c].current_filter = _invert_filter(t.colprops[c].current_filter)
					t.save_column_filters()
					t.refresh_column_filters_in_place()
					t.refresh()
					t.add_tools_panel()
				})
			}
			e.append(_e)
		}
		if (e.children().length > 1) {
			t.e_sidepanel.append(e)
		}
	}

	//
	// table tool: commonality
	//
	t.add_commonality = function() {
		if (!t.options.commonalityable) {
			return
		}

		var e = $("<div class='button_div clickable' name='tool_commonality'></div>")
		t.e_tool_commonality = e

		var span = $("<span class='icon_fixed_width common16' data-i18n='table.commonality'></span>")
		span.attr("title", i18n.t("table.commonality_help")).tooltipster()
		e.append(span)


		e.on("click", function(event) {
			event.stopPropagation()
			var sidepanel = t.get_sidepanel()
			var area = $("<div></div>")
			area.uniqueId()
			sidepanel.append(area)
			t.e_tool_commonality_area = area

			spinner_add(t.e_tool_commonality_area)
			var data = t.prepare_request_data()
			if (t.is_rest_url()) {
				data.commonality = true
			}
			$.ajax({
				type: "GET",
				url: t.prepare_request_commonality_url(),
				data: data,
				context: document.body,
				success: function(msg){
					t.e_tool_commonality_area.html(format(msg))
				}
			})
		})

		function format(data) {
			var data = data.data
			var table = $("<table class='table table-sm'></table>")
			var th = $("<tr><th data-i18n='table.pct'></th><th data-i18n='table.column'></th><th data-i18n='table.value'></th></tr>")
			th.i18n()
			table.append(th)
			for (var i=0; i<data.length; i++) {
				var d = data[i]
				var line = $("<tr style='margin:0.3em 0'></tr>")

				// pct
				var pct = $("<td></td>")
				pct.append(_cell_decorator_pct(d.percent))
				line.append(pct)

				// column
				var col = $("<td></td>")
				if (d[0] in t.colprops) {
					col.addClass("nowrap icon_fixed_width "+t.colprops[d.prop].img)
					col.text(i18n.t("col."+t.colprops[d.prop].title))
				} else {
					col.text(d.prop)
				}
				line.append(col)

				// val
				var val = $("<td></td>")
				val.text(d.value)
				line.append(val)

				table.append(line)
			}
			return table
		}

		try { e.i18n() } catch(e) {}
		return e
	}

	//
	// table tool: pager
	//
	t.pager = function() {
		if (!t.e_pager) {
			return
		}
		t.e_pager.show()

		if (t.e_wsswitch && t.e_wsswitch.find("input").is(":checked")) {
			var wsswitch = true
		} else {
			var wsswitch = false
		}

		var p_start = parseInt(t.options.pager.offset)
		var p_end = parseInt(t.options.pager.offset)+parseInt(t.options.pager.count)
		var p_total = parseInt(t.options.pager.total)
		var p_perpage = parseInt(osvc.user_prefs.data.tables[t.id].perpage)

		if (t.live_enabled()) {
			if (p_perpage > t.options.live_max_perpage) {
				p_perpage = t.options.live_max_perpage
				t.options.pager.perpage = t.options.live_max_perpage
			}
		}

		if ((p_total > 0) && (p_end > p_total)) {
			p_end = p_total
		}
		var s_total = ""
		if (p_total > 0) {
			s_total = "/" + p_total
		}

		t.e_pager.empty()

		// main pager
		if (p_total == 0) {
			t.e_pager.text("No records found matching filters")
		} else {
			// left arrow
			if (p_start > 0) {
				var left = $("<span name='pager_left'></span>")
				left.text("<< ")
				t.e_pager.append(left)
			}

			// line start - line end
			var center = $("<span name='pager_center'></span>")
			center.text((p_start+1)+"-"+p_end+s_total)
			t.e_pager.append(center)

			// right arrow
			if ((p_total < 0) || (p_end < p_total)) {
				var right = $("<span name='pager_right'></span>")
				right.text(" >>")
				t.e_pager.append(right)
			}
		}

		t.e_pager.children("span").each(function () {
			$(this).addClass('current_page clickable')
		})
		t.e_pager.find("[name=pager_right]").click(function(event){
			event.stopPropagation()
			t.page_submit(p_start+p_perpage)
		})
		t.e_pager.find("[name=pager_left]").click(function(event){
			event.stopPropagation()
			t.page_submit(p_start-p_perpage)
		})

		// resync the sticky toolbar
		t.e_sticky.empty()
		t.sticky_relocate()
	}

	t.get_renderer = function() {
		var p_renderer = osvc.user_prefs.data.tables[t.id].renderer
		if ((typeof(p_renderer) === "undefined") || (p_renderer == "auto")) {
			if ($(window).width() < 640) {
				return "grid"
			} else {
				return "table"
			}
		}
		return p_renderer
	}

	t.change_renderer = function() {
		var p_renderer = osvc.user_prefs.data.tables[t.id].renderer
		if ((typeof(p_renderer) !== "undefined") && (p_renderer != "auto")) {
			return
		}
		var new_renderer = t.get_renderer()
		if (new_renderer != t.renderer) {
			t.renderer = new_renderer
			t.div.empty()
			t.init_table()
			t.redraw()
		}
	}

	//
	// table tool: renderer selector
	//
	t.add_renderer_selector = function () {
		var e = $("<div name='renderer' class='p-3'></div>")
		var title = $("<div>"+i18n.t("table.renderer")+"</div>")
		var selector = $("<div class='action_menu_selector'></div>")
		var p_renderer = osvc.user_prefs.data.tables[t.id].renderer
		var l = [
			{
				"name": "table",
				"icon": "icon fa-list"
			},
			{
				"name": "auto",
				"icon": "icon fa-undo"
			},
			{
				"name": "grid",
				"icon": "icon fa-th"
			}
		]
		for (i=0; i<l.length; i++) {
			var v = l[i]
			var entry = $("<div renderer="+v.name+" class='clickable "+v.icon+"'></div>")
			if ((v.name == p_renderer) || ((v.name == "auto") && (typeof(p_renderer) === "undefined"))) {
				entry.addClass("action_menu_selector_selected")
			}
			selector.append(entry)
		}

		// click event
		selector.children().click(function(event){
			event.stopPropagation()
			$(this).siblings().removeClass("action_menu_selector_selected")
			$(this).addClass("action_menu_selector_selected")
			var new_renderer = $(this).attr("renderer")
			osvc.user_prefs.data.tables[t.id].renderer = new_renderer
			t.renderer = new_renderer
			t.save_prefs()
			if (new_renderer == "auto") {
				$(window).trigger("resize")
			} else {
				t.div.empty()
				t.init_table()
				t.redraw()
			}
		})
		e.append(title)
		e.append(selector)
		return e
	}

	//
	// table tool: perpage selector
	//
	t.add_perpage_selector = function () {
		var e = $("<div name='perpage' class='p-3'></div>")
		var title = $("<div>"+i18n.t("table.lines_per_page")+"</div>")
		var selector = $("<div class='action_menu_selector'></div>")
		var p_perpage = parseInt(osvc.user_prefs.data.tables[t.id].perpage)

		if (t.live_enabled()) {
			var l = [20, 50]
		} else {
			var l = [20, 50, 100, 500]
		}
		for (i=0; i<l.length; i++) {
			var v = l[i]
			var entry = $("<div name='perpage_val' class='clickable'>"+v+"</span>")
			if (v == p_perpage) {
				entry.addClass("action_menu_selector_selected")
			}
			selector.append(entry)
		}

		// click event
		selector.children().click(function(event){
			event.stopPropagation()
			$(this).siblings().removeClass("action_menu_selector_selected")
			$(this).addClass("action_menu_selector_selected")
			var new_perpage = parseInt($(this).text())
			osvc.user_prefs.data.tables[t.id].perpage = new_perpage
			t.save_prefs()
			t.refresh()
		})
		e.append(title)
		e.append(selector)
		return e
	}

	//
	// table tool: column selector
	//
	t.add_column_selector = function() {
		if (!t.options.columnable) {
			return
		}

		var e = $("<div class='button_div clickable' name='tool_column_selector'></div>")
		t.e_tool_column_selector = e

		var span = $("<span class='icon_fixed_width columns' data-i18n='table.columns'></span>")
		e.append(span)

		try { e.i18n() } catch(e) {}

		// bindings
		e.on("click", function(event) {
			event.stopPropagation()
			t.show_column_selector()
		})
		return e
	}

	t.show_column_selector = function() {
		var sidepanel = t.get_sidepanel()
		var area = $("<div style='width:21em'></div>")
		sidepanel.append(area)
		t.e_tool_column_selector_area = area

		for (var i=0; i<t.options.columns.length; i++) {
			var colname = t.options.columns[i]

			// checkbox
			var input = $("<input type='checkbox' class='ocb' />")
			input.attr("colname", colname)
			input.uniqueId()
			if (t.options.visible_columns.indexOf(colname) >= 0) {
				input.prop("checked", true)
			}

			// filtered columns are always visible
			if (t.options.filterable) {
				var val = t.colprops[colname].current_filter
				if ((val != "") && (typeof val !== "undefined")) {
					input.prop("disabled", true)
					input.prop("checked", true)
				}
			}

			// label
			var label = $("<label></label>")
			label.attr("for", input.attr("id"))

			// title
			var title = $("<span style='padding-left:1em;'></span>")
			title.text(i18n.t("col."+t.colprops[colname].title))
			title.addClass("icon_fixed_width")
			title.addClass(t.colprops[colname].img)

			// container
			var _e = $("<div class='button_div' style='white-space:nowrap'></div>")
			_e.append(input)
			_e.append(label)
			_e.append(title)

			area.append(_e)

			// click event
			_e.on("click", function(event) {
				if ($(event.target).is("label")) {
					return
				}
				var input = $(this).children("input")
				var colname = input.attr("colname")
				var current_state
				if ($(event.target).is("input")) {
					if (input.is(":checked")) {
						current_state = true
					} else {
						current_state = false
					}
				} else {
					if (input.is(":checked")) {
						current_state = false
					} else {
						current_state = true
					}
					input.prop("checked", current_state)
				}
				if (!current_state) {
					if (t.options.force_cols.indexOf(colname) >=0 ) {
						// don't remove forced columns
						t.e_table.find(".tl>[col="+colname+"],.tl>.row>[col="+colname+"]").hide()
					} else {
						t.e_table.find(".tl>[col="+colname+"],.tl>.row>[col="+colname+"]").remove()
					}
					// reset the table data md5 so that toggle on-off-on a column is not interpreted
					// as unchanged data
					t.md5sum = null
				}
				t.check_toggle_vis(current_state, colname)
			})
		}

		try { area.i18n() } catch(e) {}
	}

	//
	// table tool: bookmarks
	//
	t.add_bookmarks = function() {
		if (!t.options.bookmarkable) {
			return
		}

		var e = $("<div class='button_div clickable' name='tool_bookmark'></div>")

		var span = $("<span class='icon_fixed_width bookmark16' data-i18n='table.bookmarks'></span>")
		e.append(span)
		try { e.i18n() } catch(err) {}
		t.e_tool_bookmarks = e

		// bindings
		e.on("click", function(event) {
			event.stopPropagation()
			t.show_bookmarks()
		})
		return e
	}

	t.show_bookmarks = function() {
		var sidepanel = t.get_sidepanel()
		var area = $("<div></div>")
		sidepanel.append(area)

		var save = $("<p class='button_div icon add16' data-i18n='table.bookmarks_save'></p>")
		area.append(save)

		var save_name = $("<div class='hidden'><hr><div class='icon edit16 ml-3' data-i18n='table.bookmarks_save_name'></div><div>")
		area.append(save_name)

		var save_name_input = $("<input class='oi ml-3'>")
		save_name.append(save_name_input)

		area.append("<hr>")

		var listarea = $("<span></span>")
		area.append(listarea)
		t.e_tool_bookmarks_listarea = listarea

		var bookmarks = []
		for (var b in osvc.user_prefs.data.tables[t.id]["bookmarks"]) {
			bookmarks.push(b)
		}
		bookmarks.sort()

		if (!bookmarks.length) {
			var e = $("<div class='pl-3'></div>")
			e.text(i18n.t("table.bookmarks_no_bookmarks"))
			listarea.html(e)
		}

		for (var i=0; i<bookmarks.length; i++) {
			var name = bookmarks[i]
			t.insert_bookmark(name)
		}

		try { area.i18n() } catch(err) {}
		t.e_tool_bookmarks_area = area
		t.e_tool_bookmarks_save = save
		t.e_tool_bookmarks_save_name = save_name
		t.e_tool_bookmarks_save_name_input = save_name_input

		save.on("click", function() {
			var now = new Date()
			save_name_input.val(print_date(now))
			save_name.toggle("blind")
			save_name_input.focus()
		})

		save_name_input.on("keyup", function(event) {
			if (!is_enter(event)) {
				return
			}
			var name = $(this).val()
			osvc.user_prefs.data.tables[t.id].bookmarks[name] = $.extend({}, osvc.user_prefs.data.tables[t.id].filters)
			t.save_prefs()
			t.insert_bookmark(name)
			t.e_tool_bookmarks_save_name.hide()
			t.e_tool_bookmarks_save.show()
		})
	}

	t.init_current_filters = function() {
		if (!t.options.request_vars) {
			return
		}
		for (key in t.options.request_vars) {
			var c = key.split("_f_")[1]
			if (!(c in t.colprops)) {
				continue
			}
                        t.colprops[c].current_filter = t.options.request_vars[key]
		}
	}

	t.get_sidepanel = function() {
		// flush the sidepanel if it already exists
		var am = $("#am_"+t.id)
		am.remove()

		// create a new side panel
		var am = $("<div id='am_"+t.id+"' class='action_menu action_menu_popup stackable'></div>")

		// add a close button
		var closer = $("<div class='fa fa-times clickable link'></div>")
		closer.css({
			"text-align": "right",
			"width": "100%",
			"padding": "0.5rem",
			"font-size": "1.3rem"
		})
		closer.on("click", function(){
			am.remove()
			t.e_sticky.empty()
			t.sticky_relocate()
		})
		am.append(closer)
		t.div.children(".table_scroll_zone").prepend(am)

		t.e_sidepanel = am

		t.sticky_relocate()
		return am
	}

	t.insert_bookmark = function(name) {
		// remove the "no_bookmarks" msg
		if (t.e_tool_bookmarks_listarea.find("p").length == 0) {
			t.e_tool_bookmarks_listarea.text("")
		}

		// append the bookmark to the list area
		var bookmark = $("<p class='button_div'></p>")
		bookmark.append($("<a class='icon bookmark16'>"+name+"</a>"))
		bookmark.append($("<a style='float:right' class='link icon del16'>&nbsp;</a>"))
		t.e_tool_bookmarks_listarea.append(bookmark)

		// "del" binding
		bookmark.find(".del16").on("click", function() {
			var name = $(this).prev().text()
			var line = $(this).parents("p").first()
			delete osvc.user_prefs.data.tables[t.id].bookmarks[name]
			t.save_prefs()
			line.hide("blind", function(){line.remove()})
		})

		// "load" binding
		bookmark.find(".bookmark16").on("click", function() {
			var name = $(this).text()
			osvc.user_prefs.data.tables[t.id].filters = $.extend({}, osvc.user_prefs.data.tables[t.id].bookmarks[name])
			t.save_prefs()
			t.clear_current_filters()
			t.set_column_filters()
			t.refresh()
		})
	}

	t.init_prefs = function() {
		if (!("tables" in osvc.user_prefs.data)) {
			osvc.user_prefs.data.tables = {}
		}
		if (!(t.id in osvc.user_prefs.data.tables)) {
			osvc.user_prefs.data.tables[t.id] = {}
		}
		t.renderer = t.get_renderer()
		if (!("perpage" in osvc.user_prefs.data.tables[t.id])) {
			osvc.user_prefs.data.tables[t.id]["perpage"] = 20
		}
		if (!("filters" in osvc.user_prefs.data.tables[t.id])) {
			osvc.user_prefs.data.tables[t.id]["filters"] = {}
		}
		if (!("visible_columns" in osvc.user_prefs.data.tables[t.id])) {
			osvc.user_prefs.data.tables[t.id]["visible_columns"] = t.options.default_columns
		}
		if (!("bookmarks" in osvc.user_prefs.data.tables[t.id])) {
			osvc.user_prefs.data.tables[t.id]["bookmarks"] = {}
		}
		if (!("folded" in osvc.user_prefs.data.tables[t.id]) && "folded" in t.options) {
			osvc.user_prefs.data.tables[t.id]["folded"] = t.options.folded
		}
	}

	t.refresh_menu_data_cache = function(entry, e) {
		var scope = entry.attr("scope")
		var selector = $.data(entry[0], "selector")
		var cache_id = selector.condition + '-' + scope
		t.action_menu_req_cache = null
		t.action_menu_data_cache[cache_id] = table_action_menu_get_cols_data(t, e, scope, selector)
	}

	t.init_table = function() {
		t.add_table()
		t.get_visible_columns()
		t.init_current_filters()
		t.add_filtered_to_visible_columns()
		t.add_column_headers()
		t.refresh_column_filters_in_place()
		t.add_pager()
		t.add_tools_toggle()
		t.add_folder()
		t.add_table_title()
		t.hide_cells()
		t.add_scrollers()
		t.scroll_enable()
		t.stick()
		t.set_column_filters()
		t.refresh()
	}

	t.refresh_timer = null
	t.lines_checked = {}
	t.init_colprops()

	// remove the hosting element id for the js links to not encode it
	t.divid = t.options.divid
	delete t.options.divid


	osvc.tables[t.id] = t

	$.when(
		osvc.user_loaded
	).then(function(){
		t.init_prefs()
		t.init_table()
		t.add_ws_handler()
	})

	return t
}

//
// Standard table cell decorators
//
function delta_properties(delta, s, max_age, seconds) {
	if (seconds) {
		var mult = 60
	} else {
		var mult = 1
	}
	if (delta > 0) {
		var prefix = "-"
	} else {
		var prefix = ""
		delta = -delta
	}

	var minute = mult
	var hour = 60 * mult
	var day = 1440 * mult
	var week = 10080 * mult
	var month = 43200 * mult
	var year = 524520 * mult

	if (delta < minute) {
		var cl = "icon second"
		var text = prefix + i18n.t("table.second", {"count": Math.floor(delta)})
		var color = "#000000"
	} else if (delta < hour) {
		var cl = "icon minute"
		var text = prefix + i18n.t("table.minute", {"count": Math.floor(delta/minute)})
		var color = "#000000"
	} else if (delta < day) {
		var cl = "icon hour"
		var text = prefix + i18n.t("table.hour", {"count": Math.floor(delta/hour)})
		var color = "#181818"
	} else if (delta < week) {
		var cl = "icon day"
		var text = prefix + i18n.t("table.day", {"count": Math.floor(delta/day)})
		var color = "#333333"
	} else if (delta < month) {
		var cl = "icon  week"
		var text = prefix + i18n.t("table.week", {"count": Math.floor(delta/week)})
		var color = "#333333"
	} else if (delta < year) {
		var cl = "icon month"
		var text = prefix + i18n.t("table.month", {"count": Math.floor(delta/month)})
		var color = "#484848"
	} else {
		var cl = "icon year"
		var text = prefix + i18n.t("table.year", {"count": Math.floor(delta/year)})
		var color = "#666666"
	}

	cl += " nowrap"

	if (prefix == "-" && max_age && (delta > max_age)) {
		cl += " icon-red text-red"
	}

	if (!s) {
		s = ""
	}

	return {
		cl: cl,
		color: color,
		server_date: s,
		client_date: osvc_date_from_collector(s),
		text: text
	}
}

function cell_decorator_date(e, line) {
	cell_decorator_datetime(e, line)
	s = $.data(e[0], "v")
	e.text(s.split(" ")[0])
}

function datetime_age(s) {
	// return age in seconds
	if (typeof s === 'undefined') {
		return
	}
	if (!s || (s == 'empty')) {
		return
	}
	var d = moment.tz(s, "YYYY-MM-DD HH:mm:ss", osvc.server_timezone)
	var now = moment()
	var delta = (now -d)/1000
	return delta
}

function _outdated(s, max_age) {
	var delta = datetime_age(s)
	if (!delta) {
		return true
	}
	if (delta > max_age * 60) {
		return true
	}
	return false
}

function status_outdated(line) {
	var l = line.children("[cell=1][col=mon_updated]")
	if (l.length == 0) {
		l = line.children("[cell=1][col=svc_status_updated]")
	}
	if (l.length == 0) {
		l = line.children("[cell=1][col=status_updated]")
	}
	if (l.length == 0) {
		l = line.children("[cell=1][col$=updated]")
	}
	if (l.length == 0) {
		return true
	}
	var s = $.data(l[0], "v")
	return _outdated(s, 15)
}

function cell_decorator_date_no_age(e, line) {
	var v = $.data(e[0], "v")
	if (typeof v === 'undefined') {
		return
	}
	var s = v.split(" ")[0]
	e.html(s)
}

function cell_decorator_datetime_no_age(e, line) {
	cell_decorator_datetime(e, line)
}

function cell_decorator_date_future(e, line) {
	e.attr("max_age", 0)
	cell_decorator_datetime(e, line)
}

function cell_decorator_datetime_status(e, line) {
	e.attr("max_age", 15)
	cell_decorator_datetime(e, line)
}

function cell_decorator_datetime_future(e, line) {
	cell_decorator_datetime(e, line)
}

function cell_decorator_datetime_daily(e, line) {
	e.attr("max_age", 1440)
	cell_decorator_datetime(e, line)
}

function cell_decorator_datetime_weekly(e, line) {
	e.attr("max_age", 10080)
	cell_decorator_datetime(e, line)
}

function cell_decorator_datetime(e, line) {
	var s = $.data(e[0], "v")
	if (s == "1000-01-01 00:00:00") {
		e.empty()
		return
	}
	var max_age = e.attr("max_age") * 60
	var delta = datetime_age(s)

	if (!delta) {
		e.html()
		return
	}
	var props = delta_properties(delta, s, max_age, true)
	if (e.text() == props.text) {
		return
	}
	if (e.children().length) {
		// already decorated, just update properties
		var div = e.children()
		div
		.text(props.text)
		.css({"color": props.color})
		if (!div.hasClass(props.cl)) {
			div.removeClass().addClass(props.cl)
		}
		return
	}
	var content = $("<div class='"+props.cl+"' style='color:"+props.color+"' title='"+props.client_date+"'>"+props.text+"</div>").tooltipster()
	e.html(content)
}

function cell_decorator_duration_from_sec(e, line) {
	var s = $.data(e[0], "v")
	if (s == "") {
		e.empty()
		return
	}
	var delta = parseInt(s) * -1
	var props = delta_properties(delta, null, null, true)

	if (!delta) {
		e.html()
		return
	}
	if (e.text() == props.text) {
		return
	}
	if (e.children().length) {
		// already decorated, just update properties
		var div = e.children()
		div
		.text(props.text)
		.css({"color": props.color})
		if (!div.hasClass(props.cl)) {
			div.removeClass().addClass(props.cl)
		}
		return
	}
	var content = $("<div class='"+props.cl+"' style='color:"+props.color+"'>"+props.text+"</div>")
	e.html(content)
}

function cell_decorator_pct(e, line) {
	var v = $.data(e[0], "v")
	d = _cell_decorator_pct(v)
	e.html(d)
}

function _cell_decorator_pct(v) {
	var d = $("<div><div>")
	d.css({
		"background": "repeating-linear-gradient(to right, #009900, #009900 "+v+"%, #990000 0%, #990000)",
		"border-radius": "3px",
		"color": "white",
		"text-align": "center",
		"width": "100%"
	})
	d.text(v+"%")
	return d
}

cell_decorators = {
	"date_future": cell_decorator_date_future,
	"datetime_future": cell_decorator_datetime_future,
	"datetime_weekly": cell_decorator_datetime_weekly,
	"datetime_daily": cell_decorator_datetime_daily,
	"datetime_status": cell_decorator_datetime_status,
	"datetime_no_age": cell_decorator_datetime_no_age,
	"date_no_age": cell_decorator_date_no_age,
	"duration_from_sec": cell_decorator_duration_from_sec,
	"date": cell_decorator_date,
	"pct": cell_decorator_pct,
}

//
// action menu
//

//
// install handler for click events on the table checkbox column.
// only function called at table init.
//
function table_bind_action_menu(t) {
	table_action_menu_init_data(t)

	$("#table_"+t.id).find("[name="+t.id+"_tools]").each(function(){
		$(this).on("contextmenu", function(event) {
			// longpress => open the action menu
			t.action_menu = table_action_menu(t, event)
			t.action_menu.menu.find("input").first().focus()
			t.scroll_to_sidepanel()
			return false
		})
		$(this).on("mouseup", function(event) {
			if (event.button == 2) {
				// right-click => open the action menu
				t.action_menu = table_action_menu(t, event)
				t.action_menu.menu.find("input").first().focus()
				t.scroll_to_sidepanel()
			} else {
				// left-click => close the action menu, the menu and the filter box
				var shiftClick = jQuery.Event("click")
				shiftClick.shiftKey = event.shiftKey
				$(event.target).find("input").trigger(shiftClick)
				$("#fsr"+t.id).hide()
			}
		})
	})
}

//
// action menu formatter entry point
//
function table_action_menu(t, e){
	o = {}
	o.menu_id = "am_"+t.id
	o.menu = $("#"+o.menu_id)
	o.open_event = e

	// purge the caches
	t.action_menu_req_cache = null
	t.action_menu_data_cache = {}

	// create the menu sidepanel
	o.menu = t.get_sidepanel()

	// add the search tool
	format_search(t, o)

	// populate the action menu
	format_action_menu(t, o)
	return o
}

function format_search(t, o) {
	o.e_search = $("<input class='oi' id='amsearch' style='width:100%'>")
	o.e_search.attr("placeholder", i18n.t("table.filter_menu"))
	o.menu.append(o.e_search)
	if (is_in_view(o.e_search)) {
		o.e_search.focus()
	}
	o.e_search.on("keyup", function(event) {
		o.search = o.e_search.val().toLowerCase()
		format_action_menu(t, o)
	})
}

function format_action_menu(t, o) {
	if (o.e_search) {
		// purge previously displayed actions
		o.e_search.nextAll().remove()
	}

	// format the data as menu
	var ul = $("<ul></ul>")
	for (var i=0; i<t.action_menu_data.length; i++) {
		var li = table_action_menu_format_section(t, o, o.open_event, t.action_menu_data[i])
		if (li.html().length == 0) {
			continue
		}
		ul.append(li)
	}

	// empty menu banner
	if (ul.html().length == 0) {
		o.menu.append("<div style='padding-top:1em' class='icon alert16'>"+i18n.t("action_menu.no_action")+"</div>")
		return
	}
	o.menu.append(ul)

	// display actions only for the clicked section
	var folders = o.menu.find(".action_menu_folder")
	folders.addClass("icon_fixed_width right16")
	folders.children("ul,.action_menu_selector").hide()
	folders.on("click", function(e){
		// the fn might have inserted children dom nodes (forms for example)
		// we don't want a click in those children to propagate to the li
		// click trigger, which would close the leaf
		if (!$(e.target).is(".action_menu_folder,.action_menu_folder>span>span")) {
			return
		}

		e.stopPropagation()
		var v = $(this).hasClass("down16")
		folders.removeClass("down16")
		folders.addClass("right16")
		folders.children("ul,.action_menu_selector").hide("blind", 300)
		if (!v) {
			var selector = $(this).children(".action_menu_selector")
			selector.show()
			var scope = selector.children(".action_menu_selector_selected").attr("scope")
			$(this).children("ul").hide()
			if (scope) {
				$(this).children("ul[scope="+scope+"]").show()
			} else {
				$(this).children("ul").show("blind", 300)
			}
			$(this).removeClass("right16")
			$(this).addClass("down16")
		} else {
			table_action_menu_unfocus_leaf(t, $(this))
		}
	})

	return o
}

function table_action_menu_format_section(t, o, e, section) {
	var ul = $("<ul></ul>")
	for (var i=0; i<section.children.length; i++) {
		var li = table_action_menu_format_selector(t, o, e, section.children[i])
		if (!li || (li.children("ul").children().length == 0)) {
			continue
		}
		ul.append(li)
	}
	var content = $("<li></li>")
	if (ul.children().length == 0) {
		return content
	}
	var title = $("<h4></h4>")
	title.text(i18n.t(section.title)).addClass("icon "+section.class)
	content.append(title)
	content.append(ul)

	return content
}

//
// filter a dataset, removing elements not meeting conditions defined
// in the action menu data
//
function table_action_menu_condition_filter(t, condition, data) {
	var cond = []
	var or_cond = condition.split(",")
	for (var i=0; i<or_cond.length; i++) {
		cond.push(or_cond[i].split("+"))
	}
	var _data = []
	for (var i=0; i<data.length; i++) {
		for (var j=0; j<cond.length; j++) {
			var violation = false
			for (var k=0; k<cond[j].length; k++) {
				if (!(cond[j][k] in data[i])) {
					violation = true
					break
				}
				var val = data[i][cond[j][k]]
				if ((typeof val !== "boolean") && ((typeof val === "undefined") || (val=="") || (val == "empty"))) {
					violation = true
					break
				}
			}
			if (!violation) {
				_data.push(data[i])
				break
			}
		}
	}
	return _data
}

function table_action_menu_get_cols_data_clicked(t, e, scope, selector) {
	var data = []
	var cell = $(e.target)
	var line = cell.parents(".tl").first()
	var d = {}
	for (var i=0; i<selector.cols.length; i++) {
		var c = selector.cols[i]
		var s = t.column_selectors[c]
		var cell = line.find(s).first()
		if (cell.length == 0) {
			continue
		}
		var val = $.data(cell[0], "v")
		if ((typeof val !== "boolean") && ((typeof val === "undefined") || (val=="") || (val == "empty"))) {
			continue
		}
		d[c] = val
	}
	data.push(d)
	return table_action_menu_condition_filter(t, selector.condition, data)
}

function table_action_menu_get_cols_data_checked(t, e, scope, selector) {
	var data = []
	var sigs = []
	t.div.find(".tl").each(function(){
		var ck = $(this).find("input[id^="+t.id+"_ckid_]").first()
		if ((ck.length == 0) || !ck.is(":checked")) {
			return
		}
		var d = {}
		var sig = ""
		for (var i=0; i<selector.cols.length; i++) {
			var c = selector.cols[i]
			var s = t.column_selectors[c]
			try {
				var val = $.data($(this).find(s).first()[0], "v")
			} catch(e) {
				sig += "-"
				continue
			}
			if ((typeof val !== "boolean") && ((typeof val === "undefined") || (val=="") || (val == "empty"))) {
				sig += "-"
				continue
			}
			sig += val
			d[c] = val
		}
		if (sigs.indexOf(sig) < 0) {
			sigs.push(sig)
			data.push(d)
		}
	})
	return table_action_menu_condition_filter(t, selector.condition, data)
}

function table_action_menu_get_cols_data_all(t, e, scope, selector) {
	var data = []
	var cols = []

	// fetch all columns meaningful for the action menu
	// so we can cache the result and avoid other requests
	if (t.action_menu_req_cache) {
		data = t.action_menu_req_cache
	} else {
		var reverse_col = {}
		for (var c in t.column_selectors) {
			var s = t.column_selectors[c]
			var col = t.div.find(".tl").first().find(s).first().attr("col")
			if (!col) {
				continue
			}
			cols.push(col)
			reverse_col[col] = c
		}
		if (cols.length == 0) {
			t.action_menu_req_cache = []
			return data
		}

		var sigs = []
		var url = t.prepare_request_data_url()
		var vars = t.prepare_request_data()
		vars["props"] = cols.join(",")
		vars["offset"] = 0
		vars["limit"] = t.action_menu_req_max
		$.ajax({
			async: false,
			type: "GET",
			url: url,
			data: vars,
			success: function(msg){
				if (!is_dict(msg) || !("data" in msg)) {
					return []
				}
				var lines = msg['data']
				if (typeof(lines) === "string") {
					return []
				}
				for (i=0; i<lines.length; i++) {
					var d = {}
					var sig = ""
					for (var j=0; j<cols.length; j++) {
						col = cols[j]
						var val = lines[i][j]
						d[reverse_col[col]] = val
						sig += "-"+val
					}
					if (sigs.indexOf(sig) < 0) {
						sigs.push(sig)
						data.push(d)
					}
				}
			}
		})
		t.action_menu_req_cache = data
	}

	// digest cached data for the selector
	var sigs = []
	var _data = []
	for (i=0; i<data.length; i++) {
		var d = {}
		var _d = data[i]
		var sig = ""
		for (var j=0; j<selector.cols.length; j++) {
			var col = selector.cols[j]
			if (!(col in _d)) {
				continue
			}
			var val = _d[col]
			d[col] = val
			sig += "-"+val
		}
		if (sigs.indexOf(sig) < 0) {
			sigs.push(sig)
			_data.push(d)
		}
	}
	return table_action_menu_condition_filter(t, selector.condition, _data)
}

function table_action_menu_get_cols_data(t, e, scope, selector) {
	if (scope == "clicked") {
		return table_action_menu_get_cols_data_clicked(t, e, scope, selector)
	} else if (scope == "checked") {
		return table_action_menu_get_cols_data_checked(t, e, scope, selector)
	} else if (scope == "all") {
		return table_action_menu_get_cols_data_all(t, e, scope, selector)
	} else if (scope == "tab") {
		return [t.data]
	}
	return []
}

function table_prepare_scope_action_list(t, o, e, selector, scope, data, cache_id) {
	var ul = $("<ul></ul>")
	ul.attr("scope", scope)
	for (var j=0; j<selector.children.length; j++) {
		var leaf = selector.children[j]
		if (leaf.max && data && (data.length > leaf.max)) {
			continue
		}
		if (leaf.min && data && (data.length < leaf.min)) {
			continue
		}
		var li = table_action_menu_format_leaf(t, e, leaf)
		if (!li) {
			continue
		}
		if (o.search && ! li.text().toLowerCase().match(o.search)) {
			continue
		}
		if (cache_id) {
			li.attr("cache_id", cache_id)
			li.attr("scope", scope)
			$.data(li[0], "selector", selector)
		}
		li.on("click", function(e) {
			e.stopPropagation()
			var fn = $(this).attr("fn")
			if (fn) {
				window[fn](t, e)
			} else {
				table_action_menu_agent_action(t, e)
			}
		})
		ul.append(li)
	}
	return ul
}

function table_selector_match_table(t, selector) {
	if (!selector.table) {
		return true
	}
	for (var i=0; i<selector.table.length; i++) {
		var tid = selector.table[i]
		if (tid == t.options.name) {
			return true
		}
	}
	return false
}

function table_action_menu_format_selector(t, o, e, selector) {
	if (!table_selector_match_table(t, selector)) {
		return
	}
	var content = $("<li></li>")
	if (selector.foldable && ((o.search == "") || (typeof(o.search) === "undefined"))) {
		content.addClass("action_menu_folder")
	}
	if (selector.title) {
		var title = $("<span></span>")
		var _title = $("<span></span>")
		_title.text(i18n.t(selector.title))
		if ("class" in selector) {
			_title.addClass("icon_fixed_width "+selector["class"])
		}
		title.append(_title)
	}
	if (selector.selector.length == 0) {
		// no selector, special case for tools not working on data lines
		var ul = table_prepare_scope_action_list(t, o, e, selector)
		if (ul.length > 0) {
			content.prepend(ul)
			content.prepend(title)
		}
		return content
	}
	var e_selector = $("<div class='action_menu_selector'></div>")

	if (!t.action_menu_data_cache) {
		t.action_menu_data_cache = {}
	}

	for (var i=0; i<selector.selector.length; i++) {
		var scope = selector.selector[i]

		// don't compute the "all" scope on right-click
		if ((scope == "all") && (e.which == 3)) {
			continue
		}

		// don't compute the "clicked" scope on not right-click
		if ((scope == "clicked") && (e.which != 3)) {
			continue
		}

		// compute selected cursor
		cache_id = selector.condition
		cache_id += '-'+scope
		if (cache_id in t.action_menu_data_cache) {
			var data = t.action_menu_data_cache[cache_id]
		} else {
			var data = table_action_menu_get_cols_data(t, e, scope, selector)
			t.action_menu_data_cache[cache_id] = data
		}

		// prepare action list for scope
		var ul = table_prepare_scope_action_list(t, o, e, selector, scope, data, cache_id)

		// prepare the selector scope button
		var s = $("<div class='ellipsis'></div>")
		s.attr("scope", scope)

		// disable the scope if no data and not in natural table
		if (data.length == 0 && !table_selector_match_table(t, selector)) {
			s.addClass("action_menu_selector_disabled")
		}

		// set as selected if not disabled and no other scope is already selected
		if ((e_selector.children(".action_menu_selector_selected").length == 0) && !s.hasClass("action_menu_selector_disabled")) {
			s.addClass("action_menu_selector_selected")
		}

		// set the span text
		if ((scope == "clicked") && (data.length > 0)) {
			var l = []
			for (var j=0; j<selector.cols.length; j++) {
				var c = selector.cols[j]
				if (c in data[0]) {
					l.push(data[0][c])
				}
			}
			s.text(l.join("-"))
			if (selector.clicked_decorator) {
				selector.clicked_decorator(s, data[0])
			}
			s.hover(function() {
				$(this).removeClass("ellipsis");
				var maxscroll = $(this).width();
				var speed = maxscroll * 15;
				$(this).animate({
					scrollLeft: maxscroll
				}, speed, "linear");
			}, function() {
				$(this).stop();
				$(this).addClass("ellipsis");
				$(this).animate({
					scrollLeft: 0
				}, 'slow');
			})
		} else if ((scope == "checked") || (scope == "all")) {
			var count = data.length
			var suffix = ""
			if (count == t.action_menu_req_max) {
				suffix = "+"
			}
			s.text(scope+" ("+count+suffix+")")
		} else {
			s.text(scope)
		}

		// add the action list and bind click handler if not disabled
		if ((ul.children().length > 0) && !s.hasClass("action_menu_selector_disabled")) {
			if (!s.hasClass("action_menu_selector_selected")) {
				ul.hide()
			}
			content.append(ul)
			s.addClass("clickable")
			s.on("click", function(e) {
				e.stopPropagation()
				$(this).siblings().removeClass("action_menu_selector_selected")
				$(this).addClass("action_menu_selector_selected")
				var scope = $(this).attr("scope")
				$(this).parent().siblings("ul").hide()
				$(this).parent().siblings("ul[scope="+scope+"]").show()
			})
		} else {
			s.on("click", function(e) {
				e.stopPropagation()
			})
		}

		e_selector.append(s)

		// set the "checked" scope as selected if not disabled: take precedence to the "clicked" scope
		if ((scope == "checked") && !s.hasClass("action_menu_selector_disabled") && (data.length > 0)) {
			s.click()
		}

	}
	if (content.children("ul").length > 0) {
		content.prepend(e_selector)
		if (selector.title) {
			content.prepend(title)
		}
	}

	if ((selector.selector.length == 1) && (selector.selector[0] == "tab")) {
		e_selector.remove()
	}
	return content
}

function table_action_menu_format_leaf(t, e, leaf) {
	var li = $("<li class='action_menu_leaf clickable button_div search_entry'></li>")
	if (leaf.privileges && !services_ismemberof(leaf.privileges)) {
		return
	}
	if (leaf.action) {
		try {
			var params = leaf.params.join(",")
		} catch(err) {
			var params = ""
		}
		li.attr("action", leaf.action)
		li.attr("params", params)
	}
	li.attr("fn", leaf.fn)
	li.addClass("icon_fixed_width "+leaf['class'])
	li.text(i18n.t(leaf.title))
	return li
}


//
// format action submit result as a flash message
//
function table_action_menu_status(msg){
	var s = "accepted: "+msg.accepted+", rejected: "+msg.rejected
	if (msg.factorized>0) {
		s = "factorized: "+msg.factorized+", "+s
	}
	var table_id = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
	var vars = {}
	var ids = []
	for (var i=0; i<msg.data.length; i++) {
		ids.push(msg.data[i].action_id)
	}
	vars[table_id+"_f_id"] = "("+ids.join(",")+")"
	console.log(vars)
        osvc.flash.show({
		id: "aq-"+table_id,
		cl: "icon action16",
		text: i18n.t("action_menu.agent_actions"),
		bgcolor: osvc.colors.link,
		fn: function(id){
			var d = $("<div><div>")
			$("#"+id).html(d)
			d.uniqueId()
			table_action_queue(d.attr("id"), {
				"id": table_id,
				"request_vars": vars,
				"volatile_filters": true,
				"volatile_prefs": true
			})
			osvc.tables[table_id].e_title.text(osvc.tables[table_id].e_title.text() + " ("+s+")")
		}
	})

}

//
// Only leave the chosen leaf and its parents visible.
// Used by tools needing the space to pop addtional questions.
//
function table_action_menu_focus_on_leaf(t, entry) {
	// hide other choices
	entry.parent().parent().parent().parent().siblings().hide()
	entry.parent().parent().parent().siblings('ul').hide()
	entry.parent().parent().siblings('li').hide()
	entry.parent().siblings('ul').hide()

	// hide other actions in this selector scope
	entry.siblings().hide()
	entry.addClass("action_menu_leaf_selected")
}

function table_action_menu_unfocus_leaf(t, folder) {
	var entry = folder.find("li:visible")
	entry.siblings(":not(li)").remove()

	// show other choices
	entry.parents("li:not(.action_menu_folder)").siblings().show()
	entry.parents("li.action_menu_folder").siblings('li').show()
	entry.siblings().show()

	entry.removeClass("action_menu_leaf_selected")
}

function table_action_menu_yes_no(msg, callback) {
	var e = $("<div style='margin-top:0.6em'></div>")
	var title = $("<div></div>")
	title.text(i18n.t(msg))
	var yes = $("<button class='icon_fixed_width ok button_div clickable' name='yes'>"+i18n.t("action_menu.yes")+"</button>")
	var no = $("<button class='icon_fixed_width nok button_div clickable' name='no'>"+i18n.t("action_menu.no")+"</button>")
	e.append(title)
	e.append(yes)
	e.append(no)
	e.append($("<br>"))
	yes.on("click", function(event){
		event.preventDefault()
		event.stopPropagation()
		$(this).off("click")
		$(this).prop("disabled", true)
		callback(event)
		e.remove()
	})
	no.on("click", function(event){
		event.preventDefault()
		event.stopPropagation()
		e.remove()
	})
	return e
}


