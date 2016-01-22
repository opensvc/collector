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
		o.div.load('/init/static/views/tabs.html', "", function() {
			o.init()
			callback(o)
		})
	}

	o.init = function() {
		o.closetab = o.div.find(".closetab")
		o.tabs_ul = o.closetab.parent()
		o.display = o.div.find(".tab_display")

		// empty tabs on click closetab
		o.closetab.bind("click", function() {
			o.div.parent().remove(); // Remove extraline
			o.div.remove();
		})
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
		var e = $("<li></li>")
		var p = $("<p></p>")
		p.addClass(data.title_class)
		p.text(i18n.t(data.title))
		e.append(p)
		o.tabs_ul.append(e)
		data.tab = e

		e.bind("click", function() {
			for (var i=0; i<o.tabs.length; i++) {
				o.tabs[i].tab.removeClass("tab_active")
				o.tabs[i].div.hide()
			}
			data.tab.addClass("tab_active")
			data.div.show()
			if (!data.div.is(":empty")) {
				return
			}
			data.callback(data.divid)
		})
	}

	o.set_tab = function(tab_title) {
		if (!tab_title) {
			// set the first tab active
			o.closetab.next("li").trigger("click")
			return
		}
		for (var i=0; i<o.tabs.length; i++) {
			if (o.tabs[i].title != tab_title) {
				continue
			}
			// found the tab, set active and stop iterating
			o.tabs[i].tab.trigger("click")
			return
		}
	}


	return o
}

tab_properties_generic_autocomplete = function(options) {
	if (options.privileges && !services_ismemberof(options.privileges)) {
		return
	}
	options.div.bind("click", function() {
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
			for (var i=0; i<data.length; i++) {
				if (options.value_key && options.label_key) {
					var d = {
						"label": data[i][options.label_key],
						"id": data[i][options.value_key]
					}
					opts.push(d)
				} else {
					var d = {
						"label": data[i],
						"id": data[i]
					}
					opts.push(d)
				}
			}
			input.autocomplete({
				source: opts,
				minLength: 0,
				focus: function(event, ui) {
					input.attr("acid", ui.item.id)
				},
				select: function(event, ui) {
					input.attr("acid", ui.item.id)
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
			var data = {}
			data[input.attr("pid")] = input.attr("acid")
			options.post(data, function(jd) {
				if (jd.error && (jd.error.length > 0)) {
					$(".flash").show("blind").html(services_error_fmt(jd))
					return
				}
				e.prev().text(input.val()).show()
				input.blur()
			},
			function(xhr, stat, error) {
				$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
			})
		})
	})
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
			if (role.match(/^user_/)) {
				continue
			}
			opts.push(role)
		}
		callback(opts)
	}
	tab_properties_generic_autocomplete(options)
}

tab_properties_boolean = function(options) {
	if (options.div.text() == "true") {
		options.div.attr('class', 'toggle-on');
	} else {
		options.div.attr('class','toggle-off');
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
			if (jd.error) {
				return
			}
			if (jd.data[0][key] == false) {
				options.div.removeClass("toggle-on").addClass("toggle-off")
			} else {
				options.div.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}
}

tab_properties_generic_updater = function(options) {
	if (options.privileges && !services_ismemberof(options.privileges)) {
		return
	}

	options.div.find("[upd]").each(function(){
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
					options.post(data, function(jd) {
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

tab_properties_generic_list = function(options) {
	if (!options.limit) {
		options.limit = 0
	}
	services_osvcgetrest(options.request_service, options.request_parameters, {"limit": options.limit, "props": options.key}, function(jd) {
		if (!jd.data) {
			return
		}
		options.e_title.text(i18n.t(options.title, {"n": jd.meta.total}))
		options.e_list.empty()
		for (var i=0; i<jd.data.length; i++) {
			var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
			e.addClass(options.item_class)
			e.addClass("tag tag_attached")
			var val = jd.data[i][options.key]
			if (options.lowercase) {
				val.toLowerCase()
			}
			e.text(val)
			options.e_list.append(e)
		}
		if (jd.meta.total > jd.meta.count) {
			var e = $("<span></span>")
			e.text("...")
			options.e_list.append(e)
		}
	})
}


