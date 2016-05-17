//
// prov template
//
function prov_template_tabs(divid, options) {
  var o = tabs(divid)
  o.options = options

  o.load(function() {
    if (o.options.tpl_name) {
      var title = o.options.tpl_name
    } else {
      var title = o.options.tpl_id
    }
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "form_tabs.properties",
      "title_class": "icon prov"
    })
    o.tabs[i].callback = function(divid) {
      prov_template_properties(divid, o.options)
    }

    // tab definition
    i = o.register_tab({
      "title": "form_tabs.definition",
      "title_class": "icon edit16"
    })
    o.tabs[i].callback = function(divid) {
      prov_template_definition(divid, o.options)
    }

    o.set_tab(o.options.tab)
  })
  return o
}


function prov_template_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_tpl_name = o.div.find("#tpl_name")
		o.info_tpl_comment = o.div.find("#tpl_comment")
		o.info_tpl_author = o.div.find("#tpl_author")
		o.info_tpl_created = o.div.find("#tpl_created")
		o.info_publications = o.div.find("#publications")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("/provisioning_templates/%1", [o.options.tpl_id], "", function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_tpl_name.html(data.tpl_name)
		o.info_tpl_comment.html(data.tpl_comment)
		o.info_tpl_author.html(data.tpl_author)
		o.info_tpl_created.html(osvc_date_from_collector(data.tpl_created))

		var am_data = [
			{
				"title": "action_menu.data_actions",
				"class": "hd16",
				"children": [
					{
						"selector": ["tab"],
						"foldable": false,
						"cols": [],
						"children": [
							{
								"title": "action_menu.del",
								"class": "del16",
								"fn": "data_action_del_prov_templates",
								"privileges": ["Manager", "ProvisioningManager"]
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
			"privileges": ["ProvisioningManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/provisioning_templates/%1", [o.options.tpl_id], "", data, callback, error_callback)
			}
		})
		prov_template_publications({
			"tid": o.info_publications,
			"tpl_id": data.id
		})
		prov_template_responsibles({
			"tid": o.info_responsibles,
			"tpl_id": data.id
		})
	}

	o.div.load("/init/static/views/prov_template_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function prov_template_definition(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/provisioning_templates/%1", [o.options.tpl_id], {"props": "tpl_command"}, function(jd) {
			o.load(jd.data[0])
		})
	}

	o.load = function(data) {
		var div = $("<div style='padding:1em'></div>")
		o.div.append(div)
		if (data.tpl_command && (data.tpl_command.length > 0)) {
			var text = data.tpl_command
		} else {
			var text = i18n.t("prov_template_properties.no_command")
		}
		$.data(div, "v", text)
		cell_decorator_tpl_command(div)

		div.bind("click", function() {
			div.hide()
			var edit = $("<div name='edit'></div>")
			var textarea = $("<textarea class='oi oidefinition'></textarea>")
			var button = $("<input type='button' style='margin:0.5em 0 0.5em 0'>")
			button.attr("value", i18n.t("prov_template_properties.save"))
			if (data.tpl_command && (data.tpl_command.length > 0)) {
				textarea.val(div.text())
			}
			edit.append(textarea)
			edit.append(button)
			o.div.append(edit)
			button.bind("click", function() {
				var data = {
					"tpl_command": textarea.val()
				}
				services_osvcpostrest("/provisioning_templates/%1", [o.options.tpl_id], "", data, function(jd) {
					if (jd.error && (jd.error.length > 0)) {
						$(".flash").show("blind").html(services_error_fmt(jd))
						return
					}
					o.init()
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

