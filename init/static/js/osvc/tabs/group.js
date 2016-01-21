//
// group
//
function group_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function(){
    var i = 0

    if (!("group_id" in o.options) && ("group_name" in o.options)) {
      services_osvcgetrest("R_GROUPS", "", {"filters": ["role "+o.options.group_name]}, function(jd) {
        var group = jd.data[0]
        o.options.group_id = group.id
        o._load()
      })
    } else {
      o._load()
    }
  })

  o._load = function() {
    o.closetab.children("p").text(o.options.group_name ? o.options.group_name : o.options.group_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "guys16"
    })
    o.tabs[i].callback = function(divid) {
      group_properties(divid, o.options)
    }

    // tab hidden menu entries
    i = o.register_tab({
      "title": "group_tabs.hidden_menu_entries",
      "title_class": "menu16"
    })
    o.tabs[i].callback = function(divid) {
      group_hidden_menu_entries(divid, o.options)
    }

    o.set_tab(o.options.tab)
  }
  return o
}

function group_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id");
		o.info_description = o.div.find("#description");
		o.info_privilege = o.div.find("#privilege");
		o.info_users_title = o.div.find("#users_title");
		o.info_users = o.div.find("#users");
		o.info_nodes_title = o.div.find("#nodes_title");
		o.info_nodes = o.div.find("#nodes");
		o.info_apps_title = o.div.find("#apps_title");
		o.info_apps = o.div.find("#apps");
		o.info_services_title = o.div.find("#services_title");
		o.info_services = o.div.find("#services");

		o.load_group()
	}

	o.load_group = function() {
		services_osvcgetrest("R_GROUP", [o.options.group_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			var data = jd.data[0]
			o.info_description.html(data.description);
			o.info_id.html(data.id);

			// nodes
			if (data.privilege == true) {
				o.info_privilege.attr('class', 'toggle-on');
			} else {
				o.info_privilege.attr('class','toggle-off');
			}

			services_osvcgetrest("R_NODES", "", {"limit": 50, "props": "nodename", "filters": ["team_responsible "+data.role]}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_nodes_title.text(i18n.t("group_properties.nodes", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].nodename)
					o.info_nodes.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_nodes.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_USERS", [data.id], {"limit": 50, "props": "first_name,last_name"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_users_title.text(i18n.t("group_properties.users", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].first_name + " " + jd.data[i].last_name)
					o.info_users.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_users.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_APPS", [data.id], {"limit": 50, "props": "app"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_apps_title.text(i18n.t("group_properties.apps", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].app)
					o.info_apps.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_apps.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_SERVICES", [data.id], {"limit": 50, "props": "svc_name"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_services_title.text(i18n.t("group_properties.services", {"n": jd.meta.total}))
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

			// modifications for privileged user
			if (services_ismemberof(["Manager", "UserManager"])) {
				o.info_privilege.addClass("clickable")
				o.info_privilege.bind("click", function (event) {
					o.toggle_privilege(this)
				})
			}

		})

	}

	o.toggle_privilege = function() {
		if (o.info_privilege.hasClass("toggle-on")) {
			var data = {privilege: false}
		} else {
			var data = {privilege: true}
		}
		services_osvcpostrest("R_GROUP", [o.options.group_id], "", data, function(jd) {
			if (jd.error) {
				return
			}
			if (jd.data[0].privilege == false) {
				o.info_privilege.removeClass("toggle-on").addClass("toggle-off")
			} else {
				o.info_privilege.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}

	o.div.load("/init/static/views/group_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o

}


function group_hidden_menu_entries(divid, options) {
	o = {}
	o.options = options
	o.div = $("#"+divid)

	o.set = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcpostrest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$(".flash").show("blind").html(services_error_fmt(jd))
			}
			
		})
	}

	o.del = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcdeleterest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$(".flash").show("blind").html(services_error_fmt(jd))
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
				$(".flash").show("blind").html(services_error_fmt(jd))
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
		for (entry in menu_data[section]) {
			o.format_entry(section, menu_data[section][entry])
		}
	}

	o.init = function() {
		var area = $("<div class='group_hidden_menu'></div>")
		o.area = area
		for (section in menu_data) {
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
