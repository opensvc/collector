function variable_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.comp
	o.options.icon = "comp16"
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "variable",
			"name": o.options.variable_name
		}
	}

	o.load(function() {
		o._load()
	})

	o._load = function() {
		var title = o.options.variable_name
		
		o.closetab.text(title)

		i = o.register_tab({
			"title": "variable_tabs.content",
			"title_class": "icon comp16"
		})
		o.tabs[i].callback = function(divid) {
			variable_content(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}

	return o
}

function variable_content(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "variable",
			"id": o.options.variable_id,
			"name": o.options.variable_name
		}
	}
	o.rulesets = {}
	var head = {}

	services_osvcgetrest("R_COMPLIANCE_RULESET_VARIABLE", [o.options.ruleset_id, o.options.variable_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		var div = $("<div style='padding:1em'></div>")
		o.area = div
		o.div.append(div)
		o.render(jd.data[0])
		osvc_tools(o.div, {
			"link": o.link
		})
	},
	function() {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})

	o.render = function(variable) {
		try {
			var data = $.parseJSON(variable.var_value)
		} catch(e) {
			var data = variable.var_value
		}
		var variable_name = $("<h3 class='b'></h3>")
		variable_name.text(variable.var_name)
		o.area.append(variable_name)

		var p1 = $("<p></p>")
		p1.text(i18n.t("designer.var_class", {"name": variable.var_class}))
		o.area.append(p1)

		var p2 = $("<p></p>")
		p2.text(i18n.t("designer.var_last_mod", {"by": variable.var_author, "on": variable.var_updated}))
		o.area.append(p2)

		o.area.append("<br>")

		var form_div = $("<div></div>")
		form_div.uniqueId()
		o.area.append(form_div)
		form(form_div.attr("id"), {
			"data": data,
			"var_id": variable.id,
			"rset_id": variable.ruleset_id,
			"display_mode": true,
			"digest": true,
			"form_name": variable.var_class,
			"disable_edit": false
		})
		o.area.append("<br>")
		o.area.append("<br>")
	}
}

