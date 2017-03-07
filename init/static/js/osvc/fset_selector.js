function fset_selector(divid, callback) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.div.empty()
	o.callback = callback
	o.get_data = []
	o.get_deferred = $.Deferred()

	o.load_span = function() {
		spinner_add(o.div)
		spinner_del(o.div)
		if (osvc.filterset.length == 1) {
			var fset_name = osvc.filterset[0].fset_name
			var fset_id = osvc.filterset[0].id
		} else {
			var fset_name = i18n.t("fset_selector.none")
			var fset_id = -1
		}
		o.span.text(fset_name)
		o.span.attr("fset_id", fset_id)
		o.div.bind("click", function() {
			if (!o.area.is(":visible")) {
				o.area.slideDown()
				$("#search_input").focus()
				o.load_area()
			}
		})
		return o
	}

	o.load_data = function() {
		services_osvcgetrest("R_FILTERSETS", "", {"limit": "0", "props": "id,fset_name", "meta": "0"}, function(jd) {
			o.get_data = jd.data
			o.get_deferred.resolve(true)
		})
	}

	o.load_area = function() {
		$.when(
			o.get_deferred
		).then(function() {
			o._load_area()
		})
	}

	o._load_area = function() {
		o.area.empty()
		var current_fset_id = o.span.attr("fset_id")

		// add the "none" option
		o.add_fset(-1, i18n.t("fset_selector.none"))
		for (var i=0; i<o.get_data.length; i++) {
			var data = o.get_data[i]
			o.add_fset(data.id, data.fset_name)
		}

		o.area.find("[fset_id="+current_fset_id+"]").addClass("menu_current")
		o.area.attr("ready", "1")
	}


	o.set_fset = function(new_fset_id, new_fset_name) {
		if (new_fset_id <= 0) {
			o.unset_fset()
			return
		}
		services_osvcpostrest("R_USERS_SELF_FILTERSET_ONE", [new_fset_id], "", "", function(jd) {
			if (!new_fset_name) {
				new_fset_name = o.area.find("[fset_id="+new_fset_id+"]").find("[name=title]").text()
			}
			o.span.empty()
			o.span.text(new_fset_name)
			o.span.attr("fset_id", new_fset_id)
			o.close()
			o.callbacks()
		},
		function(xhr, stat, error) {
			o.span.html(services_ajax_error_fmt(xhr, stat, error))
			o.span.show()
		})
	}

	o.close = function() {
		if (o.area.is(':visible')) {
			o.area.stop().slideUp()
		}
	}

	o.unset_fset = function() {
		services_osvcdeleterest("R_USERS_SELF_FILTERSET", [], "", "", function(jd) {
			o.span.empty()
			o.span.text(i18n.t("fset_selector.none"))
			o.span.attr("fset_id", "-1")
			o.close()
			o.callbacks()
		},
		function(xhr, stat, error) {
			o.span.html(services_ajax_error_fmt(xhr, stat, error))
			o.span.show()
		})
	}

	o.container = function() {
		var e = $("<a class='icon filter16' name='fset_selector'></a>")

		var span_selector = $("<span class='clickable'></span>")
		span_selector.uniqueId()
		e.append(span_selector)
		o.span = span_selector

		e.i18n()
		o.div.append(e)

		o.area = $("<div style='position:fixed' class='menu hidden stackable' name='fset_selector_entries'></div>")
		o.div.append(o.area)

		o.load_span()
	}

	o.callbacks = function() {
		// refresh tables
		for (tid in osvc.tables) {
			osvc.tables[tid].refresh()
		}
		if (o.callback) {
			o.callback()
		}
	}

	o.add_fset = function(id, name) {
		var e = $("<div class='menu_entry menu_box' fset_id='"+id+"'></div>")
		var icon = $("<div class='menu_icon filter16'></div>")
		e.append(icon)

		var text = $("<div></div>")
		var title = $("<div name='title'></div>")
		title.text(name)
		text.append(title)
		var subtitle = $("<div></div>")
		text.append(subtitle)
		e.append(text)

		e.bind("click", function() {
			var new_fset_id = $(this).attr("fset_id")
			var new_fset_name = $(this).find("[name=title]").text()
			o.set_fset(new_fset_id, new_fset_name)
		})

		o.area.append(e)
	}

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "gen_filtersets_change") {
			o.load_data()
			return
		}
		if (data.event == "gen_filterset_user_change") {
			var d = data.data
			if (d.user_id != _self.id) {
				return
			}
			o.span.text(d.fset_name)
			o.span.attr("fset_id", d.fset_id)
			o.callbacks()
			return
		}
		if (data.event == "gen_filterset_user_delete") {
			o.span.text(i18n.t("fset_selector.none"))
			o.span.attr("fset_id", "-1")
			o.callbacks()
			return
		}
	}

	wsh["fset_selector"] = function(data) {
		o.event_handler(data)
	}

	o.load_data()
	o.container()
	return o
}

