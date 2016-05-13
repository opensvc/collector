//
// form
//
function form_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options

	o.load(function() {
		if (o.options.form_name) {
			var title = o.options.form_name
		} else {
			var title = o.options.form_id
		}
		o.closetab.children("p").text(title)

		// tab properties
		i = o.register_tab({
			"title": "form_tabs.properties",
			"title_class": "icon wf16"
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

		// tab request
		i = o.register_tab({
			"title": "form_tabs.request",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			$("#"+divid).css({"padding": "1em"})
			form(divid, options)
		}

		o.set_tab(o.options.tab)
	})
	return o
}

function form_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
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
		o.info_form_author.html(data.form_author)
		o.info_form_created.html(osvc_date(data.form_created))

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
				var data = ["custo", "folder", "generic", "obj"]
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

	o.div.load("/init/static/views/form_properties.html", function() {
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

	o.init = function() {
		o.load_form()
	}

	o.load_form = function() {
		o.div.empty()
		services_osvcgetrest("R_FORM", [o.options.form_id], {"props": "form_yaml"}, function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		var div = $("<div style='padding:1em'></div>")
		o.div.append(div)
		if (data.form_yaml && (data.form_yaml.length > 0)) {
			var text = data.form_yaml
		} else {
			var text = i18n.t("form_properties.no_yaml")
		}
		$.data(div, "v", text)
		cell_decorator_yaml(div)

		div.bind("click", function() {
			div.hide()
			var edit = $("<div name='edit'></div>")
			var textarea = $("<textarea class='oi oidefinition'></textarea>")
			var button = $("<input type='button' style='margin:0.5em 0 0.5em 0'>")
			button.attr("value", i18n.t("form_properties.save"))
			if (data.form_yaml && (data.form_yaml.length > 0)) {
				textarea.val(div.text())
			}
			edit.append(textarea)
			edit.append(button)
			o.div.append(edit)
			button.bind("click", function() {
				var data = {
					"form_yaml": textarea.val()
				}
				services_osvcpostrest("R_FORM", [o.options.form_id], "", data, function(jd) {
					if (jd.error && (jd.error.length > 0)) {
						$(".flash").show("blind").html(services_error_fmt(jd))
						return
					}
					o.init()

					// force a new render in the rendering tab
					o.div.parents(".tab_display").first().find("[name=form_area]").parent().empty()
				},
				function(xhr, stat, error) {
					$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
				})
			})
		})
	}

	o.init()

	return o
}

