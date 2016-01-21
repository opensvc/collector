//
// moduleset
//
function moduleset_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    var title = o.options.modset_name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "modset16"
    })
    o.tabs[i].callback = function(divid) {
      modset_properties(divid, o.options)
    }

    // tab quotas
    i = o.register_tab({
      "title": "modset_tabs.export",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      modset_export(divid, o.options)
    }

    o.set_tab(o.options.tab)
  })

  return o
}

function modset_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_modset_name = o.div.find("#modset_name")
		o.info_modset_author = o.div.find("#modset_author")
		o.info_modset_updated = o.div.find("#modset_updated")
		o.info_modules = o.div.find("#modules")
		o.info_nodes = o.div.find("#nodes")
		o.info_services = o.div.find("#services")
		o.info_modulesets = o.div.find("#modulesets")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("/compliance/modulesets", "", {"meta": "0", "filters": ["modset_name "+o.options.modset_name]}, function(jd) {
			o.data = jd.data[0]
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_modset_name.html(data.modset_name)
		o.info_modset_author.html(data.modset_author)
		o.info_modset_updated.html(data.modset_updated)

		o.load_modules()
		o.load_nodes()
		o.load_services()
		o.load_usage()

		tab_properties_generic_updater({
			"div": o.div,
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/compliance/modulesets/%1", [data.id], "", _data, callback, error_callback)
			}
		})
	}

	o.load_modules = function() {
		o.load_scope(o.info_modules, {"service": "/compliance/modulesets/%1/modules", "key": "modset_mod_name"})
	}

	o.load_nodes = function() {
		o.load_scope(o.info_nodes, {"service": "/compliance/modulesets/%1/nodes", "key": "nodename"})
	}

	o.load_services = function() {
		o.load_scope(o.info_services, {"service": "/compliance/modulesets/%1/services", "key": "svc_name"})
	}

	o.load_usage = function() {
		services_osvcgetrest("/compliance/modulesets/%1/usage", [o.data.id], "", function(jd) {
			o.populate(o.info_modulesets, jd.data.modulesets)
		})
	}

	o.populate = function(div, data) {
		var n = data.length
		div.siblings(".line").find("span > span").append(" ("+n+")")
		for (var i=0; i<n; i++) {
			var g = $("<span class='tag tag_attached'></span>")
			g.text(data[i])
			div.append(g, " ")
		}
	}

	o.load_scope = function(div, options) {
		div.empty().addClass("tag_container")
		services_osvcgetrest(options.service, [o.data.id], {
			"meta": 1,
			"limit": 0,
			"props": options.key,
			"orderby": options.key
		}, function(jd) {
			div.siblings(".line").find("span > span").append(" ("+jd.meta.total+")")
			for (var i=0; i<jd.data.length; i++) {
				var g = $("<span class='tag tag_attached'></span>")
				g.text(jd.data[i][options.key])
				div.append(g, " ")
			}
		})
	}

	o.div.load("/init/static/views/modset_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function modset_export(divid, options) {
	var o = {}

	// store parameters
	o.load_services = function() {
		o.load_scope(o.info_services, {"service": "/filtersets/%1/services", "key": "svc_name"})
	}

	o.load_scope = function(div, options) {
		div.empty().addClass("tag_container")
		services_osvcgetrest(options.service, [o.data.id], {
			"meta": 1,
			"limit": 0,
			"props": options.key,
			"orderby": options.key
		}, function(jd) {
			div.siblings(".line").find("span > span").append(" ("+jd.meta.total+")")
			for (var i=0; i<jd.data.length; i++) {
				var g = $("<span class='tag tag_attached'></span>")
				g.text(jd.data[i][options.key])
				div.append(g, " ")
			}
		})
	}

	o.div.load("/init/static/views/modset_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function modset_export(divid, options) {
	var o = {}

	// store parameters
	o.load_services = function() {
		o.load_scope(o.info_services, {"service": "/filtersets/%1/services", "key": "svc_name"})
	}

	o.load_scope = function(div, options) {
		div.empty().addClass("tag_container")
		services_osvcgetrest(options.service, [o.data.id], {
			"meta": 1,
			"limit": 0,
			"props": options.key,
			"orderby": options.key
		}, function(jd) {
			div.siblings(".line").find("span > span").append(" ("+jd.meta.total+")")
			for (var i=0; i<jd.data.length; i++) {
				var g = $("<span class='tag tag_attached'></span>")
				g.text(jd.data[i][options.key])
				div.append(g, " ")
			}
		})
	}

	o.div.load("/init/static/views/modset_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function modset_export(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.load_export()
	}

	o.load_export = function() {
		o.div.empty()
		services_osvcgetrest("/compliance/modulesets", "", {"filters": ["modset_name "+o.options.modset_name]}, function(jd) {
			services_osvcgetrest("/compliance/modulesets/%1/export", [jd.data[0].id], "", function(jd) {
				o._load_export(jd)
			})
		})
	}

	o._load_export = function(data) {
		var div = $("<pre style='padding:1em'></pre>")
		o.div.append(div)
		div.text(JSON.stringify(data, null, 4))
	}

	o.init()

	return o
}

