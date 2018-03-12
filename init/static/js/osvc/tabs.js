//
// base tabs object
// derive to make object-specific tabs
//
function tabs(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.tabs = []

	o.load = function(callback) {
		o.div.load('/'+osvc.app+'/static/views/tabs.html?v='+osvc.code_rev, "", function() {
			o.init()
			callback(o)
			if (o.link) {
				o.link.parameters = o.options
			}
			osvc_tools(o.e_tabs, {
				"close": true,
				"link": o.link
			})
		})
	}

	o.init = function() {
		o.e_tabs = o.div.children().first()
		o.closetab = o.div.find(".closetab")
		o.tabs_ul = o.closetab.parent()
		o.display = o.div.find(".tab_display")

		o.closetab
		.css({"background-color": o.options.bgcolor})
		.addClass("icon "+o.options.icon)

		// set a tab identifer to help find peers
		var tab_id = null
		for (key in o.options) {
			if (key.indexOf("_id") >= 1) {
				var tab_id = key + "_" + o.options[key]
			}
		}
		if (!tab_id) {
			for (key in o.options) {
				if (key.indexOf("_name") >= 1) {
					var tab_id = key + "_" + md5(o.options[key])
				}
			}
		}
		o.e_tabs.attr("tab_id", tab_id)
	}

	o.register_tab = function(data) {
		// allocate a div to store tab information
		e = $("<div></div>")
		e.addClass("hidden")
		e.css({"width": "100%"})
		e.uniqueId()
		o.display.append(e)
		data.divid = e.attr("id")
		data.div = e

		var index = o.tabs.length
		o.tabs.push(data)

		o.add_tab(index)

		return index
	}

	o.add_tab = function(index) {
		var data = o.tabs[index]
		if (o.options.show_tabs && o.options.show_tabs.indexOf(data.title) < 0) {
			return
		}

		var e = $("<li></li>")
		.addClass(data.title_class)
		.text(i18n.t(data.title))
		o.tabs_ul.append(e)
		data.tab = e

		e.bind("click", function() {
			var current_tab_active = null
			for (var i=0; i<o.tabs.length; i++) {
				if (!o.tabs[i].tab) {
					continue
				}
				if (!o.tabs[i].tab.hasClass("tab_active")) {
					continue
				}
				current_tab_active = o.tabs[i]
				current_tab_active.tab.removeClass("tab_active")
				current_tab_active.tab.removeAttr("title").tooltipster('destroy')
				current_tab_active.div.hide()
			}
			data.tab.addClass("tab_active")
			data.tab.attr("title", i18n.t("tabs.click_to_reload")).tooltipster()
			data.div.show()
			if (data.div.is(":empty") || (current_tab_active.divid == data.divid)) {
				// interpret a click on the active tab as a wish to reload
				$("#"+data.divid).empty()
				o.options.reload = true
				data.callback(data.divid)
			}
		})
	}

	o.find_tab = function(tab_title) {
		if (!tab_title) {
			return
		}
		for (var i=0; i<o.tabs.length; i++) {
			if (o.tabs[i].title != tab_title) {
				continue
			}
			// found the tab
			return o.tabs[i]
		}
	}

	o.set_tab = function(tab_title) {
		if (!tab_title) {
			// set the first tab active
			o.closetab.next("li").trigger("click")
			return
		}
		var tab = o.find_tab(tab_title)
		if (!tab) {
			// set the first tab active
			o.closetab.next("li").trigger("click")
			return
		}
		// found the tab, set active and stop iterating
		tab.tab.trigger("click")
	}

	return o
}

tab_properties_generic_autocomplete = function(options) {
	if (options.privileges && !services_ismemberof(options.privileges)) {
		return
	}
	options.div.bind("click", function(event) {
		if ($(event.target).hasClass("tag")) {
			return
		}
		var updater = $(this).attr("upd")
		var e = $("<td></td>")
		var form = $("<form></form>")
		var input = $("<input class='aci oi' type='text'></input>")
		e.append(form)
		form.append(input)
		e.css({"padding-left": "0px"})
		input.val($(this).text())
		input.attr("pid", $(this).attr("id"))
		var opts = []
		options.get(function(data) {
			if (data.length == 0) {
				opts = data
			} else {
				try {
					("label" in data[0])
					opts = data
				} catch (err) {
					for (var i=0; i<data.length; i++) {
						var d = {
							"label": data[i],
							"value": data[i]
						}
						opts.push(d)
					}
				}
			}
			input.click(function(){
				input.autocomplete("search")
			})
			input.keyup(function(){
				var opts = input.autocomplete("option").source
				var current = input.val()
				var found = false
				for (var i=0; i<opts.length; i++) {
					var opt = opts[i]
					if (opt.label == current) {
						found = true
						break
					}
				}
				if (!found) {
					input.addClass("constraint_violation")
				} else {
					input.removeClass("constraint_violation")
					input.attr("acid", opt.value)
				}
			})
			input.autocomplete({
				source: opts,
				minLength: 0,
				focus: function(event, ui) {
					event.preventDefault()
					input.val(ui.item.label)
					input.attr("acid", ui.item.value)
				},
				select: function(event, ui) {
					event.preventDefault()
					input.val(ui.item.label)
					input.attr("acid", ui.item.value)
				}
			})
		})
		input.bind("blur", function(){
			$(this).parents("td").first().siblings("td").show()
			$(this).parents("td").first().remove()
		})
		$(this).parent().append(e)
		$(this).hide()
		input.focus()

		e.find("form").submit(function(event) {
			event.preventDefault()
			var input = $(this).find("textarea,input[type=text],select")
			if (input.hasClass("constraint_violation")) {
				return
			}
			var data = {}
			if (options.value_key) {
				data[options.value_key] = input.attr("acid")
			} else {
				data[input.attr("pid")] = input.attr("acid")
			}
			options.post(data, function(jd) {
				if (rest_error(jd)) {
					osvc.flash.error(services_error_fmt(jd))
					return
				}
				var upd = e.prev().attr("upd")
				e.prev().text(input.val()).show()
				if (upd == "org_group") {
					e.prev().osvc_org_group()
				} else if ((upd == "org_group_id") || (upd == "primary_group")) {
					e.prev().osvc_org_group({"group_id": e.attr("acid")})
				} else if (upd == "app") {
					e.prev().osvc_app()
				} else if (upd == "user_app") {
					e.prev().osvc_app()
				}

				if (options.callback) {
					options.callback(e)
				}

				input.blur()
				tab_properties_generic_update_peers(options.div)
				tab_properties_generic_lists_refresh(options.div)
			},
			function(xhr, stat, error) {
				osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
			})
		})
	})
}

function tab_properties_generic_update_peers(div) {
	var val = div.text()
	tab_id = div.parents("[tab_id]").first().attr("tab_id")
	$("[tab_id="+tab_id+"]").find("[upd]#"+div.attr("id")).each(function(){
		if ($(this)[0] == div[0]) {
			return
		}
		$(this).text(val)
	})
}

function tab_properties_generic_lists_refresh(div) {
	$("[generic_list]").each(function(){
		var genlist = $(this)[0].generic_list
		if (!genlist.options.depends) {
			return
		}
		for (var i=0; i<genlist.options.depends.length; i++) {
			var depend = genlist.options.depends[i]
			if (div.attr("id") == depend) {
				genlist.refresh()
			}
		}
	})
}

tab_properties_generic_autocomplete_org_group_id = function(options) {
	options.get = function(callback) {
		var opts = [{"value": 0, "label": ""}]
		services_osvcgetrest("/users/%1/groups", [options.user_id], {"filters": ["privilege F"], "meta": "false", "limit": "0"}, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var group = jd.data[i]
				opts.push({"value": group.id, "label": group.role})
			}
		})
		callback(opts)
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_generic_autocomplete_variable_class = function(options) {
	options.callback = function(e) {
		e.prev().osvc_form()
	}
	options.get = function(callback) {
		var opts = [{"value": 0, "label": ""}]
			services_osvcgetrest("/forms", [options.user_id], {"props": "form_name", "query": "form_type=obj", "filters": ["privilege F"], "meta": "false", "limit": "0"}, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var form_line = jd.data[i]
				opts.push({"value": form_line.form_name, "label": form_line.form_name})
			}
		})
		callback(opts)
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_generic_autocomplete_org_group = function(options) {
	options.get = function(callback) {
		var opts = []
		for (var i=0; i<_groups.length; i++) {
			var group = _groups[i]
			if (group.privilege) {
				continue
			}
			var role = group.role
			opts.push(role)
		}
		callback(opts)
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_generic_autocomplete_app_id = function(options) {
	options.get = function(callback) {
		services_osvcgetrest("R_APPS", "", {"props": "id,app", "meta": "false", "limit": "0"}, function(jd) {
			var opts = []
			for (var i=0; i<jd.data.length; i++) {
				var d = {
					"label": jd.data[i].app,
					"value": jd.data[i].id
				}
				opts.push(d)
			}
			callback(opts)
		})
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_generic_autocomplete_user_app = function(options) {
	options.get = function(callback) {
		services_osvcgetrest("R_USER_APPS_RESPONSIBLE", [_self.id], {"props": "app", "meta": "false", "limit": "0"}, function(jd) {
			var opts = []
			for (var i=0; i<jd.data.length; i++) {
				var app = jd.data[i].app
				opts.push(app)
			}
			callback(opts)
		})
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_generic_boolean = function(options) {
	if (options.div.text() == "true") {
		options.div.attr('class', 'fa toggle-on');
	} else {
		options.div.attr('class','fa toggle-off');
	}
	options.div.empty()

	if (!options.privileges || services_ismemberof(options.privileges)) {
		options.div.addClass("clickable")
		options.div.bind("click", function (event) {
			toggle_prop()
		})
	}

        function toggle_prop() {
		var data = {}
		var key = options.div.attr("id")
		if (options.div.hasClass("toggle-on")) {
			data[key] = false
		} else {
			data[key] = true
		}
		options.post(data, function(jd) {
			if (rest_error(jd)) {
				return
			}
			if (jd.data[0][key] == false) {
				options.div.removeClass("toggle-on").addClass("toggle-off")
			} else {
				options.div.removeClass("toggle-off").addClass("toggle-on")
			}
			tab_properties_generic_update_peers(options.div)
			tab_properties_generic_lists_refresh(options.div)
		},
		function() {}
	)}
}

tab_properties_generic_simple = function(options) {
	if (options.privileges && !services_ismemberof(options.privileges)) {
		return
	}

	options.div.bind("click", function(event) {
		event.stopPropagation()
		if ($(this).siblings().find("form").length > 0) {
			$(this).siblings().show()
			$(this).siblings().find("input[type=text]:visible,select,textarea").focus()
			$(this).hide()
			return
		}
		var updater = options.div.attr("upd")
		if (updater == "text") {
			var e = $("<td><form><textarea class='oi'></textarea></form></td>")
			var button = $("<input type='submit'>")
			e.find("form").append("<br>").append(button)
			button.attr("value", i18n.t("prov_template_properties.save"))
		} else {
			var e = $("<td><form><input class='oi' type='text'></input></form></td>")
		}
		e.css({"padding-left": "0px"})
		e.attr("colspan", $(this).attr("colspan"))
		var input = e.find(".oi").first()
		input.uniqueId() // for date picker
		input.attr("pid", options.div.attr("id"))
		input.val(options.div.text())
		input.bind("blur", function(ev){
			var a = $(":active").last()
			if ($(ev.target).parents("td")[0] == a.parents("td")[0]) {
				input.focus()
				return
			}
			$(this).parents("td").first().siblings("td").show()
			$(this).parents("td").first().hide()
		})
		options.div.parent().append(e)
		options.div.hide()
		input.focus()
		e.find("form").submit(function(event) {
			event.preventDefault()
			var input = $(this).find(".oi").first()
			input.blur()
			var data = {}
			var val = input.val()
			if (updater == "datetime") {
				var m = moment(val).tz(osvc.server_timezone)
				val = m.format(m._f)
			}
			if (updater == "size_mb") {
				val = Math.ceil(convert_size(val) / 1024 / 1024)
			}
			data[input.attr("pid")] = val
			options.post(data, function(jd) {
				if (rest_error(jd)) {
					osvc.flash.error(services_error_fmt(jd))
					return
				}
				e.hide()
				var cell = e.prev()
				if (updater == "size_mb") {
					$.data(cell[0], "v", val)
					cell_decorator_size_mb(cell)
				} else {
					cell.text(val).show()
				}
				tab_properties_generic_update_peers(options.div)
				tab_properties_generic_lists_refresh(options.div)
			},
			function(xhr, stat, error) {
				osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
			})
		})
		if (updater == "date") {
			input.datepicker({
				dateFormat:'yy-mm-dd',
				onSelect: function() {
					input.parents("td").first().siblings("td").click()
				}
			}).datepicker("show");
		} else if (updater == "datetime") {
			input.datetimepicker({
				dateFormat:'yy-mm-dd',
				onSelect: function() {
					input.parents("td").first().siblings("td").click()
				}
			}).datepicker("show");
		}
	})
}

tab_properties_generic_updater = function(options) {
	options.div.find("[upd]").each(function(){
		if (options.condition && !options.condition($(this))) {
			return
		}
		if (!options.privileges || services_ismemberof(options.privileges)) {
			$(this).addClass("clickable")
			if ($(this).text() == "") {
				$(this).addClass("editable editable-placeholder")
			}
			$(this).hover(
				function() {
					$(this).addClass("editable")
					$(this).removeClass("editable-placeholder")
				},
				function() {
					if ($(this).text() == "") {
						$(this).addClass("editable editable-placeholder")
					} else {
						$(this).removeClass("editable editable-placeholder")
					}
				}
			)
		}
		var updater = $(this).attr("upd")
		if (updater == "org_group") {
			$(this).osvc_org_group()
		} else if ((updater == "org_group_id") || (updater == "primary_group")) {
			$(this).osvc_org_group({"group_id": $(this).attr("acid")})
		} else if (updater == "app") {
			$(this).osvc_app()
		} else if (updater == "user_app") {
			$(this).osvc_app()
		} else if (updater == "variable_class") {
			$(this).osvc_form()
		}

		if ((updater == "string") || (updater == "text") || (updater == "integer") || (updater == "date") || (updater == "datetime") || (updater == "size_mb")) {
			tab_properties_generic_simple($.extend({}, options, {"div": $(this)}))
		} else if (updater == "boolean") {
			tab_properties_generic_boolean($.extend({}, options, {"div": $(this)}))
		} else if (updater == "org_group") {
			tab_properties_generic_autocomplete_org_group($.extend({}, options, {"div": $(this)}))
		} else if (updater == "org_group_id") {
			tab_properties_generic_autocomplete_org_group_id($.extend({}, options, {"div": $(this)}))
		} else if (updater == "app_id") {
			tab_properties_generic_autocomplete_app_id($.extend({}, options, {"div": $(this)}))
		} else if (updater == "user_app") {
			tab_properties_generic_autocomplete_user_app($.extend({}, options, {"div": $(this)}))
		} else if (updater == "variable_class") {
			tab_properties_generic_autocomplete_variable_class($.extend({}, options, {"div": $(this)}))
		}
	})
}

tab_properties_generic_list = function(options) {
	if (!options.limit) {
		options.limit = 0
	}
	if (!options.request_data) {
		options.request_data = {}
	}
	if (options.limit) {
		options.request_data.limit = options.limit
	}
	if (!options.request_data.props) {
		var props = []
		if (options.key) {
			props.push(options.key)
		}
		if (options.id) {
			props.push(options.id)
		}
		options.request_data.props = props.join(",")
	}
	if (options.data) {
		render(options.data, options.data.length, options.data.length)
		return
	}
	options.tag_ids = []

	function clear() {
		for (i=0; i<options.tags_ids; i++) {
			options.e_list.children("[tag_id="+options.tags_ids[i]+"]").remove()
		}
		options.tag_ids = []
	}

	function refresh() {
		if (typeof(options.request_parameters) === "function") {
			options.last_request_parameters = options.request_parameters()
		} else {
			options.last_request_parameters = options.request_parameters
		}
		spinner_add(options.e_list)
		services_osvcgetrest(options.request_service, options.last_request_parameters, options.request_data, function(jd) {
			spinner_del(options.e_list)
			if (!jd.data) {
				return
			}
			render(jd.data, jd.meta.count, jd.meta.total)
		})
	}

	function render(data, n, total) {
		options.e_list.addClass("tag_container")
		var title = options.e_title.text().replace(/\s*\([0-9]+\)\s*/, "")
		options.e_title.text(title + " ("+total+")")
		clear()
		for (var i=0; i<data.length; i++) {
			var e = $("<span></span>")
			if (options.bgcolor) {
				e.css({"background-color": options.bgcolor})
			}
			if (options.use_item_class) {
				e.addClass(options.item_class)
			}
			e.addClass("icon tag tag_attached")
			if (options.key) {
				if (typeof(options.key) === "string") {
					var val = data[i][options.key]
				} else {
					var val = options.key(data[i])
				}
			} else {
				var val = data[i]
			}
			if (options.lowercase && val) {
				val.toLowerCase()
			}
			e.text(val)
			if (options.id) {
				e.attr("tag_id", data[i][options.id])
			}
			if (options.extra_attr) {
				for (var j=0; j<options.extra_attr.length; j++) {
					var key = options.extra_attr[j]
					e.attr(key, data[j][key])
				}
			}
			options.e_list.append(e)
			options.tag_ids.push(data[i][options.id])
			e.bind("dblclick", function(event){
				if (!options.ondblclick) {
					return
				}
				var opts = {
					"name": $(this).text(),
					"id": $(this).attr("tag_id")
				}
				if (options.extra_attr) {
					for (var j=0; j<options.extra_attr.length; j++) {
						var key = options.extra_attr[j]
						opts[key] = $(this).attr(key)
					}
				}
				if (options.flash_id) {
					var flash_id = options.flash_id($(this))
				} else if (options.flash_id_prefix) {
					var flash_id = options.flash_id_prefix + "-" + $(this).attr("tag_id")
				} else {
					var flash_id = options.key + "-" + $(this).attr("tag_id")
				}
				osvc.flash.show({
					"id": flash_id,
					"text": $(this).text(),
					"cl": options.item_class,
					"bgcolor": options.bgcolor,
					"fn": function(id) {
						options.ondblclick(id, opts)
					}
				})
			})
			if (data.length > 4) {
				options.e_list.addClass("grow")
			}
		}
		if (total > n) {
			var e = $("<span></span>")
			e.text("...")
			options.e_list.append(e)
		}
	}

	if (!options.e_list) {
		console.log("generic_list DOM element not found,", options)
		return
	}
	refresh()
	options.e_list.attr("generic_list", "")
	options.e_list[0].generic_list = {}
	options.e_list[0].generic_list.options = options
	options.e_list[0].generic_list.refresh = refresh
}

function tab_tools(options) {
	var o = {}
	o.menu = options.div
	o.data = options.data
	o.action_menu_data = options.am_data
	o.open_event = {}
	format_action_menu(o, o)
	return o
}

function osvc_editor(divid, options) {
	var o = {}
	o.options = options
	if (divid.length) {
		o.div = divid
	} else {
		o.div = $("#"+divid)
	}

	o.init = function() {
		var textarea = $("<div class='oi oidefinition' style='min-height:30em'></div>")
		var button = $("<button class='button_div icon fa-save' style='margin:0.5em 0 0.5em 0.5em'></button>")
		textarea.uniqueId()
		button.text(i18n.t("form_properties.save"))
		textarea.text(o.options.text)
		o.div.append(textarea)
		o.editor = ace.edit(textarea.attr("id"))
		o.editor.setReadOnly(true)
		var vim = ace.require("ace/keyboard/vim").handler
		o.editor.setKeyboardHandler(vim)
		if (!o.options.mode) {
			o.options.mode = "yaml"
		}
		var mode = ace.require("ace/mode/"+o.options.mode).Mode
		o.editor.session.setMode(new mode())
		o.editor.focus()
		var VimApi = ace.require("ace/keyboard/vim").CodeMirror.Vim
		VimApi.defineEx("write", "w", function(cm, input) {
			o.options.save(o.editor.getValue())
		})      
		button.bind("click", function() {
			o.options.save(o.editor.getValue())
		})      
		if (o.options.privileges && services_ismemberof(o.options.privileges)) {
			o.editor.setReadOnly(false)
			o.div.append(button)
		}
		if (o.options.obj_type && o.options.obj_id) {
			services_osvcgetrest("/"+o.options.obj_type+"/%1/am_i_responsible", [o.options.obj_id], "", function(jd) {
				if (jd.data) {
					o.editor.setReadOnly(false)
					o.div.append(button)
				}
			})
		}
		if (o.options.callback) {
			o.options.callback()
		}
	}

	require(["ace"], function() {
		o.init()
	})
	return o
}

//
// handle the revisions tab
//
// options:
// - id: 1			the object id
// - base_url: "/forms"		the rest api base url
//
function generic_revisions(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})

		o.log = o.div.find('#log')
		o.diff = o.div.find('#diff')
		o.revisions = o.div.find('#revisions')
		o.bt_rollback = o.div.find('#rollback')
		o.bt_content = o.div.find('#bcontent')
		o.bt_diff = o.div.find('#bdiff')
		o.bt_diff_to_now = o.div.find('#bdiff_to_now')
		o.bt_group = o.bt_content.parent()
		o.bt = o.bt_group.parent()

		o.load_form()
		o.bt_binds()
	}

	o.load_form = function() {
		services_osvcgetrest(o.options.base_url+"/%1/revisions", [o.options.id], "", function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				if (jd.data[i]["content"].indexOf("rollback") >= 0) {
					jd.data[i]["style"] = "background-color:#d9534f !important;color:white"
				}
			}

			var options = {
				zoomKey: "altKey",
				zoomable: true,
				clickToUse: false
			}
			// Determine the start date
			if (jd.data.length > 8) {
				options.start = jd.data[8].start
				options.start = jd.data[0].start
			}

			require(["vis"], function(vis) {
				var timeline = new vis.Timeline(o.revisions[0], jd.data, options)
				o.revisions.on('click', function(e) {
					var props = timeline.getEventProperties(e)
					o.bt.show()
					o.bt_rollback.data('cid', props['item'])
					o.bt_group.find(".active").click()
				})
			})
		})
	}

	o.bt_binds = function() {
		o.bt_rollback.on("click", function(e) {
                        services_osvcpostrest(o.options.base_url+"/%1/rollback/%2", [o.options.id, o.bt_rollback.data('cid')])
			o.revisions.empty()
			o.diff.empty()
			o.bt.hide()
			o.load_form()
		})
		o.bt_content.on("click", function(e) {
			o.bt_group.find(".active").removeClass("active")
			o.bt_content.addClass("active")
			o.diff.empty()
			spinner_add(o.diff)
                        services_osvcgetrest(o.options.base_url+"/%1/revisions/%2", [o.options.id, o.bt_rollback.data('cid')], {}, function(jd){
				spinner_del(o.diff)
				o.diff.html(jd.data.content)
			},function(xhr) {
				spinner_del(o.diff)
				o.diff.html(xhr)
			})
		})
		o.bt_diff.on("click", function(e) {
			o.bt_group.find(".active").removeClass("active")
			o.bt_diff.addClass("active")
			o.diff.empty()
			spinner_add(o.diff)
                        services_osvcgetrest(o.options.base_url+"/%1/diff/%2", [o.options.id, o.bt_rollback.data('cid')], {}, function(jd){
				spinner_del(o.diff)
				jd.data = jd.data.substring(jd.data.indexOf("@@"))
				o.diff.html(jd.data)
				require(["hljs"], function(hljs) {
					hljs.highlightBlock(o.diff[0])
				})
			},function(xhr) {
				spinner_del(o.diff)
				o.diff.html(xhr)
			})
		})
		o.bt_diff_to_now.on("click", function(e) {
			o.bt_group.find(".active").removeClass("active")
			o.bt_diff_to_now.addClass("active")
			o.diff.empty()
			spinner_add(o.diff)
                        services_osvcgetrest(o.options.base_url+"/%1/diff/%2", [o.options.id, o.bt_rollback.data('cid')], {"other": "HEAD"}, function(jd){
				spinner_del(o.diff)
				jd.data = jd.data.substring(jd.data.indexOf("@@"))
				o.diff.html(jd.data)
				require(["hljs"], function(hljs) {
					hljs.highlightBlock(o.diff[0])
				})
			},function(xhr) {
				spinner_del(o.diff)
				o.diff.html(xhr)
			})
		})
	}

	o.div.load("/init/static/views/revisions.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


