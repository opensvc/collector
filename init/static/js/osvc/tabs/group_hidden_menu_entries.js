function group_hidden_menu_entries(divid, options) {
	o = {}
	o.options = options
	o.div = $("#"+divid)
	o.data = menu_search_key()

	o.set = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcpostrest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
			}
			
		})
	}

	o.del = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcdeleterest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
			}
		})
	}

	o.get = function(callback) {
		var params = {
			"meta": "0",
			"limit": "0"
		}
		services_osvcgetrest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], params, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
			}
			o.hidden = []
			for (i=0; i<jd.data.length; i++) {
				o.hidden.push(jd.data[i].menu_entry)
			}
			callback()
		})
	}

	o.format_entry = function(section, entry) {
		var div = $("<div></div>")
		o.area.append(div)

		// entry
		var e = $(menu_create_entry_s(section, entry))

		// checkbox
		var input = $("<input class='ocb' type='checkbox' />")
		input.attr("id", entry.id)
		if (o.hidden.indexOf(entry.id) >= 0) {
			input.prop("checked", true)
			e.find(".menu_icon,.menu_title").css({"color": "darkred"})
		}
		var label = $("<label class='ocb'></label>")
		label.attr("for", entry.id)

		e.find(".menu_box").prepend([input, label])
		div.append(e)

		// click
		input.bind("click", function() {
			var id = $(this).attr("id")
			var val = $(this).is(":checked")
			if (val == true) {
				o.set(id)
				$(this).parent().find(".menu_icon,.menu_title").css({"color": "darkred"})
			} else {
				o.del(id)
				$(this).parent().find(".menu_icon,.menu_title").css({"color": "black"})
			}
		})
	}

	o.format_section = function(section) {
		var title = $("<h2></h2>")
		title.text(i18n.t("menu."+section+".title"))
		o.area.append(title)
		for (entry in o.data[section]) {
			o.format_entry(section, o.data[section][entry])
		}
	}

	o.init = function() {
		var area = $("<div class='group_hidden_menu'></div>")
		o.area = area
		for (section in o.data) {
			o.format_section(section)
		}
		o.div.empty()
		o.div.append(area)
	}

	o.get(function() {
		o.init()
	})
	return o
}
