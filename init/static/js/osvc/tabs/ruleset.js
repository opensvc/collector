//
// ruleset
//
function ruleset_tabs(divid, options) {
  var o = tabs(divid)
  o.options = options

  o.load(function() {
    if (o.options.ruleset_name) {
      var title = o.options.ruleset_name
    } else {
      var title = o.options.ruleset_id
    }
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "ruleset_tabs.ruleset",
      "title_class": "pkg16"
    })
    o.tabs[i].callback = function(divid) {
      ruleset_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "ruleset_tabs.export",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      ruleset_export(divid, o.options)
    }

    o.set_tab(o.options.tab)
  })
  return o
}

function ruleset_export(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	services_osvcgetrest("R_COMPLIANCE_RULESET_EXPORT", [o.options.ruleset_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		var div = $("<pre style='padding:1em'></pre>")
		div.text(JSON.stringify(jd, null, 4))
		o.div.empty().append(div)
		hljs.highlightBlock(div[0])
	},
	function() {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})
}

function ruleset_properties(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.rulesets = {}
	var head = {}
	services_osvcgetrest("R_COMPLIANCE_RULESET_EXPORT", [o.options.ruleset_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		for (var i=0; i<jd.rulesets.length; i++) {
			var rset = jd.rulesets[i]
			o.rulesets[rset.ruleset_name] = rset
			if (o.options.ruleset_name && (o.options.ruleset_name == rset.ruleset_name)) {
				head = rset
				continue
			}
			if (o.options.ruleset_id && (o.options.ruleset_id == rset.id)) {
				head = rset
				continue
			}
		}
		var div = $("<div style='padding:1em'></div>")
		o.area = div
		o.div.append(div)
		o.render(head)
	},
	function() {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})

	o.render_title = function(chain) {
		var div = $("<div></div>")
		for (var i=0; i<chain.length; i++) {
			var rset = chain[i]
			if (i>0) {
				div.append("<br>")
				div.append("<span class='icon fa-arrow-right'></span>")
			}
			var e = $("<span style='font-size:1.2em' class='pkg16'></span>")
			e.text(rset.ruleset_name)
			if (i == chain.length-1) {
				e.addClass("highlight")
			}
			div.append(e)
		}
		return div
	}

	o.render_usage = function(ruleset_id, div) {
		var data = {
			"modulesets": {
				"title": "ruleset_tab.usage_modulesets",
				"cl": "action16"
			},
			"rulesets": {
				"title": "ruleset_tab.usage_rulesets",
				"cl": "pkg16"
			},
			"nodes": {
				"title": "ruleset_tab.usage_nodes",
				"cl": "node16"
			},
			"services": {
				"title": "ruleset_tab.usage_services",
				"cl": "svc"
			}
		}
		services_osvcgetrest("R_COMPLIANCE_RULESET_USAGE", [ruleset_id], "", function(jd) {
			if (!jd && jd.error) {
				div.html(services_error_fmt(jd))
				return
			}
			for (key in data) {
				var l = jd.data[key]
				if (l.length == 0) {
					continue
				}
				var title = $("<h3 class='line'></h3>")
				var title_span = $("<span></span>")
				title_span.text(i18n.t(data[key].title, {"n": l.length}))
				title.append(title_span)
				div.append(title)

				for (var j=0; j<l.length; j++) {
					var e = $("<span></span>")
					e.text(l[j])
					e.addClass(data[key].cl)
					div.append(e)
				}
			}
		},
		function() {
			div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.render = function(rset, chain) {
		var p1 = $("<p></p>")
		var p2 = $("<p></p>")
		var p3 = $("<p></p>")

		if (!chain) {
			chain = [rset]
		} else {
			chain.push(rset)
		}
		o.area.append(o.render_title(chain))

		p1.text(i18n.t("ruleset_tab.type", {"type": rset.ruleset_type}))
		p2.text(i18n.t("ruleset_tab.public", {"public": rset.ruleset_public}))
		o.area.append(p1)
		o.area.append(p2)

		if (rset.ruleset_type == "contextual") {
			p3.text(i18n.t("ruleset_tab.filterset", {"name": rset.fset_name}))
			o.area.append(p3)
		}

		var usage = $("<div></div>")
		o.area.append(usage)
		o.render_usage(rset.id, usage)

		var variables_title = $("<h3 class='line'></h3>")
		var variables_title_span = $("<span></span>")
		variables_title_span.text(i18n.t("ruleset_tab.variables_title", {"n": rset.variables.length}))
		variables_title.append(variables_title_span)
		o.area.append(variables_title)

		for (var i=0; i<rset.variables.length; i++) {
			var variable = rset.variables[i]
			try {
				var data = $.parseJSON(variable.var_value)
			} catch(e) {
				var data = variable.var_value
			}
			var variable_name = $("<h3></h3>")
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
				"rset_id": rset.id,
				"display_mode": true,
				"digest": true,
				"form_name": variable.var_class,
				"disable_edit": false
			})
			o.area.append("<br>")
		}
		o.area.append("<br>")

		if (!rset.rulesets) {
			return
		}
		for (var i=0; i<rset.rulesets.length; i++) {
			o.render(o.rulesets[rset.rulesets[i]], chain)
		}
	}
}
