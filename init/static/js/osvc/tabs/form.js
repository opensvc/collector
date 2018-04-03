//
// form
//
function form_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.form
	o.options.icon = "wf16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		$.when(osvc.forms_loaded).then(function(){
			if (o.options.form_name && o.options.form_name in osvc.forms.data) {
				options.data = osvc.forms.data[o.options.form_name]
			} 
			if (!o.options.form_id && options.data) {
				o.options.form_id = options.data.id
			}
			o._load()
		})
	})

	o._load = function() {
		if (o.options.form_name) {
			var title = o.options.form_name
		} else {
			var title = o.options.form_id
		}
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "form_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			form_properties(divid, o.options)
		}

		// tab definition
		i = o.register_tab({
			"title": "form_tabs.definition",
			"title_class": "icon edit16"
		})
		o.tabs[i].callback = function(divid) {
			form_definition(divid, o.options)
		}

		// tab revisions
		i = o.register_tab({
			"title": "form_tabs.revisions",
			"title_class": "icon time16"
		})
		o.tabs[i].callback = function(divid) {
			generic_revisions(divid, {
				"id": o.options.form_id,
				"base_url": "/forms"
			})
		}

		// tab request
		i = o.register_tab({
			"title": "form_tabs.request",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			requests(divid, {
				"form_name": o.options.form_name,
				"locked": true
			})
		}

		o.set_tab(o.options.tab)
	}
	return o
}

function form_properties(divid, options) {
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
		o.info_id = o.div.find("#id")
		o.info_form_name = o.div.find("#form_name")
		o.info_form_type = o.div.find("#form_type")
		o.info_form_folder = o.div.find("#form_folder")
		o.info_form_author = o.div.find("#form_author")
		o.info_form_created = o.div.find("#form_created")
		o.info_publications = o.div.find("#publications")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("R_FORM", [o.options.form_id], "", function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_form_name.html(data.form_name)
		o.info_form_type.html(data.form_type)
		o.info_form_folder.html(data.form_folder)
		o.info_form_author.html(data.form_author).osvc_fullname()
		o.info_form_created.html(osvc_date_from_collector(data.form_created))

		var am_data = [
			{
				"title": "action_menu.data_actions",
				"children": [
					{
						"selector": ["tab"],
						"foldable": false,
						"cols": [],
						"children": [
							{
								"title": "action_menu.del",
								"class": "del16",
								"fn": "data_action_del_form",
								"privileges": ["Manager", "FormsManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"id": data.id},
			"am_data": am_data
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["FormsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("R_FORM", [o.options.form_id], "", data, callback, error_callback)
			}
		})
		tab_properties_generic_autocomplete({
			"div": o.info_form_type,
			"privileges": ["FormsManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("R_FORM", [data.id], "", _data, callback, error_callback)
			},
			"get": function(callback) {
				var data = ["generic", "obj", "folder"]
				callback(data)
			}
		})
		form_publications({
			"tid": o.info_publications,
			"form_id": data.id
		})
		form_responsibles({
			"tid": o.info_responsibles,
			"form_id": data.id
		})

	}

	o.div.load("/init/static/views/form_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function form_definition(divid, options) {
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
		o.load_form()
	}

	o.resize = function() {
		var div = o.editor_div.children().first()
		var button = o.editor_div.find("button")
		var max_height = max_child_height(o.div)
			 - o.editor_div.css("padding-top").replace(/px/,"")
			 - o.editor_div.css("padding-bottom").replace(/px/,"")
		if (button.length > 0) {
			max_height = max_height
				 - button.height()
				 - button.css("margin-top").replace(/px/,"")
				 - button.css("margin-bottom").replace(/px/,"")
		}
		div.outerHeight(max_height)
		o.editor.editor.resize()
	}

	o.load_form = function() {
		o.div.empty()
		services_osvcgetrest("R_FORM", [o.options.form_id], {"props": "form_yaml"}, function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.editor_div = $("<div style='padding:1em'></div>")
		o.div.append(o.editor_div)
		if (data.form_yaml && (data.form_yaml.length > 0)) {
			var text = data.form_yaml
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.editor_div, {
			"text": text,
			"obj_type": "forms",
			"obj_id": o.options.form_id,
			"save": o.save,
			"callback": o.resize
		})
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
	}

	o.save = function(text) {
		var data = {
			"form_yaml": text
		}
		var result = o.div.find("[name=result]")
		if (result.length == 0) {
			result = $("<div name='result'></div>")
			o.div.children().append(result)
		}
		result.empty().show()
		spinner_add(result)
		services_osvcpostrest("R_FORM", [o.options.form_id], "", data, function(jd) {
			spinner_del(result)
			if (rest_error(jd)) {
				result.html(services_error_fmt(jd))
				return
			}
			result.html("<div data-i18n='forms.success' class='ok'></div>").i18n()
			result.fadeOut(2000)

			// force a new render in the rendering tab
			o.div.parents(".tab_display").first().find("[name=form_area]").parent().empty()
		},
		function(xhr, stat, error) {
			result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	require(["ace"], function() {
		o.init()
	})

	return o
}

