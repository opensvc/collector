//
// app
//
function app_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function(){
    var i = 0

    if (!("app_id" in o.options) && ("app_name" in o.options)) {
      services_osvcgetrest("R_APPS", "", {"filters": ["app "+o.options.app_name]}, function(jd) {
        var app = jd.data[0]
        o.options.app_id = app.id
        o._load()
      })
    } else {
      o._load()
    }
  })

  o._load = function() {
    o.closetab.children("p").text(o.options.app_name ? o.options.app_name : o.options.app_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "svc"
    })
    o.tabs[i].callback = function(divid) {
      app_properties(divid, o.options)
    }

    // tab quotas
    i = o.register_tab({
      "title": "array_tabs.quotas",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      table_quota_app(divid, o.options.app_name)
    }

    o.set_tab(o.options.tab)
  }
  return o
}


function app_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id");
		o.info_description = o.div.find("#description");
		o.info_app = o.div.find("#app");
		o.info_app_team_ops = o.div.find("#app_team_ops");
		o.info_app_domain = o.div.find("#app_domain");
		o.info_updated = o.div.find("#updated");
		o.info_responsibles_title = o.div.find("#responsibles_title");
		o.info_responsibles = o.div.find("#responsibles");
		o.info_services_title = o.div.find("#services_title");
		o.info_services = o.div.find("#services");
		o.info_nodes_title = o.div.find("#nodes_title");
		o.info_nodes = o.div.find("#nodes");

		o.load_app()
	}

	o.load_app = function() {
		services_osvcgetrest("R_APP", [o.options.app_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			var data = jd.data[0]
			o.info_description.html(data.description);
			o.info_app_team_ops.html(data.app_team_ops);
			o.info_app_domain.html(data.app_domain);
			o.info_app.html(data.app);
			o.info_updated.html(data.updated);
			o.info_id.html(data.id);

			services_osvcgetrest("R_APP_RESPONSIBLES", [data.id], {"limit": 50, "props": "role"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_responsibles_title.text(i18n.t("app_properties.responsibles", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].role)
					o.info_responsibles.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_responsibles.append(e)
				}
			})
			services_osvcgetrest("R_APP_SERVICES", [data.id], {"limit": 50, "props": "svc_name"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_services_title.text(i18n.t("app_properties.services", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].svc_name)
					o.info_services.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_services.append(e)
				}
			})
			services_osvcgetrest("R_APP_NODES", [data.id], {"limit": 50, "props": "nodename"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_nodes_title.text(i18n.t("app_properties.nodes", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].nodename.toLowerCase())
					o.info_nodes.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_nodes.append(e)
				}
			})

			// modifications for privileged user
			if (services_ismemberof(["Manager", "AppManager"])) {
			}

		})

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

				} else if (updater == "group") {
					var e = $("<td></td>")
					var form = $("<form></form>")
					var input = $("<input class='oi' type='text'></input>")
					e.append(form)
					form.append(input)
					e.css({"padding-left": "0px"})
					input.val($(this).text())
					input.attr("pid", $(this).attr("id"))
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
					input.autocomplete({
						source: opts,
						minLength: 0
					})
					input.bind("blur", function(){
						$(this).parents("td").first().siblings("td").show()
						$(this).parents("td").first().hide()
					})
					$(this).parent().append(e)
					$(this).hide()
					input.focus()
				} else {
					return
				}
				e.find("form").submit(function(event) {
					event.preventDefault()
					var input = $(this).find("input[type=text],select")
					input.blur()
					data = {}
					data["nodename"] = o.options.nodename
					data[input.attr("pid")] = input.val()
					services_osvcpostrest("R_APP", [o.options.app_id], "", data, function(jd) {
						o.init()
					})
				})
			})
		})
	}

	o.div.load("/init/static/views/app_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o

}
