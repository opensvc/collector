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
		o.info_form_created.html(data.form_created)

		o.load_publications()
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
				if ((updater == "string") || (updater == "integer") || (updater == "date") || (updater == "datetime")) {
					var e = $("<td><form><input class='oi' type='text'></input></form></td>")
					e.css({"padding-left": "0px"})
					var input = e.find("input")
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
						var input = $(this).find("input[type=text],select")
						input.blur()
						var data = {}
						data[input.attr("pid")] = input.val()
						services_osvcpostrest("R_FORM", [o.options.form_id], "", data, function(jd) {
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
				} else if (updater == "form_type") {
					var e = $("<td></td>")
					var form = $("<form></form>")
					var input = $("<input class='oi' type='text'></input>")
					e.append(form)
					form.append(input)
					e.css({"padding-left": "0px"})
					input.val($(this).text())
					input.attr("pid", $(this).attr("id"))
					var opts = ["custo", "folder", "generic", "obj"]
					input.autocomplete({
						source: opts,
						minLength: 0,
						select: function(event, ui) {
							o.set_form_type(e, ui.item.label)
							event.preventDefault()
						}
					})
					input.bind("blur", function(){
						$(this).parents("td").first().siblings("td").show()
						$(this).parents("td").first().hide()
					})
					$(this).parent().append(e)
					$(this).hide()
					input.focus()

					e.find("form").submit(function(event) {
						event.preventDefault()
						var val = input.val()
						o.set_form_type(e, val)
					})
				}
			})
		})
	}

	o.set_form_type = function(e, val) {
		var data = {
			"form_type": val
		}
		services_osvcpostrest("R_FORM", [o.options.form_id], "", data, function(jd) {
			e.hide()
			e.prev().text(val).show()
		})
	}

	o.load_publications = function() {
		o.load_groups(o.info_publications, {"service": "R_FORM_PUBLICATIONS"})
	}

	o.load_responsibles = function() {
		o.load_groups(o.info_responsibles, {"service": "R_FORM_RESPONSIBLES"})
	}

	o.load_groups = function(div, options) {
		div.empty().addClass("tag_container")
		services_osvcgetrest(options.service, [o.options.form_id], {"props": "role", "orderby": "role"}, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var g = $("<span class='tag tag_attached'></span>")
				g.text(jd.data[i].role)
				div.append(g)
			}
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
		var div = $("<div></div>")
		o.div.append(div)
		$.data(div, "v", data.form_yaml)
		cell_decorator_yaml(div)

		div.bind("click", function() {
			div.hide()
			var edit = $("<div name='edit'></div>")
			var textarea = $("<textarea class='oi' style='width:97%;min-height:20em'></textarea>")
			var button = $("<input type='button' style='margin:0.5em 0 0.5em 0'>")
			button.attr("value", i18n.t("form_properties.save"))
			textarea.val(div.text())
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

