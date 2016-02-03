//
// network
//
function network_tabs(divid, options) {
  var o = tabs(divid)
  o.options = options

  o.load(function() {
    o.closetab.children("p").text(o.options.network_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "icon net16"
    })
    o.tabs[i].callback = function(divid) {
      network_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "network_tabs.segments",
      "title_class": "icon net16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/networks/segments/"+o.options.network_id, [], divid, function(){})
    }

    o.set_tab(o.options.tab)
  })
  return o
}


function network_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		// updateable
		o.info_pvid = o.div.find("#pvid")
		o.info_network = o.div.find("#network")
		o.info_netmask = o.div.find("#netmask")
		o.info_gateway = o.div.find("#gateway")
		o.info_name = o.div.find("#name")
		o.info_comment = o.div.find("#comment")
		o.info_team_responsible = o.div.find("#team_responsible")
		o.info_prio = o.div.find("#prio")

		// non updateable
		o.info_begin = o.div.find("#begin")
		o.info_end = o.div.find("#end")
		o.info_broadcast = o.div.find("#broadcast")
		o.info_updated = o.div.find("#updated")

		o.load_network()
	}

	o.load_network = function() {
		services_osvcgetrest("R_NETWORK", [o.options.network_id], "", function(jd) {
			o._load_network(jd.data[0])
		})
	}

	o._load_network = function(data) {
		o.info_pvid.html(data.pvid)
		o.info_network.html(data.network)
		o.info_netmask.html(data.netmask)
		o.info_gateway.html(data.gateway)
		o.info_name.html(data.name)
		o.info_comment.html(data.comment)
		o.info_team_responsible.html(data.team_responsible)
		o.info_prio.html(data.prio)

		o.info_begin.html(data.begin)
		o.info_end.html(data.end)
		o.info_broadcast.html(data.broadcast)
		o.info_updated.html(data.updated)

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["NetworkManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("R_NETWORK", [o.options.network_id], "", _data, callback, error_callback)
			}
		})
	}

	o.div.load("/init/static/views/network_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


