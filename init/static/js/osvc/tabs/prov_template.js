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
		o.info_responsibles = o.div.find("#responsibles")
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
		o.info_tpl_created.html(data.tpl_created)

		//o.load_publications()
		o.load_responsibles()

		o.div.find("[upd]").each(function(){
			$(this).addClass("clickable")
			$(this).hover(
				function() {
					$(this).addClass("editable")
				},
				function() {
					$(this).removeClass("editable")
				}
			)
			$(this).bind("click", function() {
				//$(this).unbind("mouseenter mouseleave click")
				if ($(this).siblings().find("form").length > 0) {
					$(this).siblings().show()
					$(this).siblings().find("input[type=text]:visible,select").focus()
					$(this).hide()
					return
				}
				var updater = $(this).attr("upd")
				if ((updater == "string") || (updater == "text") || (updater == "integer") || (updater == "date") || (updater == "datetime")) {
					if (updater == "text") {
						var e = $("<td><form><textarea class='oi'></textarea></form></td>")
						var button = $("<input type='submit'>")
						e.find("form").append("<br>").append(button)
						button.attr("value", i18n.t("prov_template_properties.save"))
					} else {
						var e = $("<td><form><input class='oi' type='text'></input></form></td>")
					}
					e.css({"padding-left": "0px"})
					var input = e.find("input,textarea")
					input.uniqueId() // for date picker
					input.attr("pid", $(this).attr("id"))
					input.attr("value", $(this).text())
					input.bind("blur", function(){
						$(this).parents("td").first().siblings("td").show()
						$(this).parents("td").first().hide()
					})
					$(this).parent().append(e)
					$(this).hide()
					input.focus()
					e.find("form").submit(function(event) {
						event.preventDefault()
						var input = $(this).find("textarea,input[type=text],select")
						input.blur()
						var data = {}
						data[input.attr("pid")] = input.val()
						services_osvcpostrest("/provisioning_templates/%1", [o.options.tpl_id], "", data, function(jd) {
							if (jd.error && (jd.error.length > 0)) {
								$(".flash").show("blind").html(services_error_fmt(jd))
								return
							}
							e.hide()
							e.prev().text(input.val()).show()
						},
						function(xhr, stat, error) {
							$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
						})
					})
				}
			})
		})
	}

	o.load_publications = function() {
		o.load_groups(o.info_publications, {"service": "/provisioning_templates/%1/publications"})
	}

	o.load_responsibles = function() {
		o.load_groups(o.info_responsibles, {"service": "/provisioning_templates/%1/responsibles"})
	}

	o.load_groups = function(div, options) {
		div.empty().addClass("tag_container")
		services_osvcgetrest(options.service, [o.options.tpl_id], {"props": "role", "orderby": "role"}, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var g = $("<span class='tag tag_attached'></span>")
				g.text(jd.data[i].role)
				div.append(g, " ")
			}
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
			var textarea = $("<textarea class='oi' style='width:97%;min-height:20em'></textarea>")
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

