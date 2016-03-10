function topology(divid, options) {
	var o = {}
	o.divid = divid
	o.options = options
	o.div = $("#"+o.divid)

	o.init = function() {
		// button
		o.button.attr("value", i18n.t("topology.redraw"))

		// link
		o.link.bind("click", function() {
			o.create_link()
		})

		// toggle config
		o.toggle_config.bind("click", function() {
			o.config.show("fold")
			o.toggle_config.hide()
		})

		// set checkboxes
		o.div.find("input[type=checkbox]").each(function() {
			var name = $(this).attr("name")
			$(this).uniqueId()
			$(this).next().attr("for", $(this).attr("id"))
			$(this).addClass("ocb")
			if (o.options.display.indexOf(name) >= 0) {
				$(this).prop("checked", true)
			} else {
				$(this).prop("checked", false)
			}
		})

		// form submit
		o.div.find("form").bind("submit", function(event) {
			event.preventDefault()
			o.config.empty()
			o.options.display = []
			$(this).find("input:checked").each(function () {
				o.options.display.push($(this).attr("name"))
			})
			o.draw()
		})
		o.draw()
	}

	o.create_link = function() {
		var display = []
		o.div.find("input[type=checkbox]").each(function() {
			if ($(this).is(":checked")) {
				display.push($(this).attr("name"))
			}
		})
		o.options.display = display
		osvc_create_link("topology", o.options)
	}

	o.draw = function() {
		var i = 0
		url = $(location).attr("origin") + "/init/topo/call/json/json_topo_data"
		if (o.viz.parents(".overlay").length == 0) {
			_height = $(window).height()-$(".header").outerHeight()-16
			o.viz.height(_height)
		}
		$.getJSON(url, o.options, function(_data){
			var eid = o.viz[0]
			var blacklist = ["timestep", "damping", "minVelocity", "maxVelocity"]
			var options = {
				configure: {
					"container": o.config[0],
					"filter": function (option, path) {
						if (path.indexOf('physics') < 0) {
							return false
						}
						if (blacklist.indexOf(option) >= 0) {
							return false
						}
					}
				},
				physics: {
					barnesHut: {
						//enabled: true,
						gravitationalConstant: -3000,
						centralGravity: 0.7,
						avoidOverlap: 0.7,
						//springLength: 95,
						springConstant: 0.1,
						damping: 0.5
					}
				},
				"groups": {
					"sync": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c5", "color": "lightgreen", "size": 50}},
					"app": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "lightgreen", "size": 50}},
					"container": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "lightgreen", "size": 50}},
					"fs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf07c", "color": "lightgreen", "size": 50}},
					"hb": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf21e", "color": "lightgreen", "size": 50}},
					"share": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e0", "color": "lightgreen", "size": 50}},
					"stonith": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e2", "color": "lightgreen", "size": 50}},
					"disk": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": "lightgreen", "size": 50}},
					"disk.scsireserv": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf023", "color": "lightgreen", "size": 50}},
					"disks": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": "#dddd66", "size": 50}},
					"array": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": "#dddd66", "size": 100}},
					"ip": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf124", "color": "lightgreen", "size": 50}},
					"sansw": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0ec", "color": "cadetblue", "size": 50}},
					"node": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf233", "color": "aqua", "size": 50}},
					"apps": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf069", "color": "lightgreen", "size": 100}},
					"countries": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 110}},
					"cities": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 100}},
					"buildings": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 90}},
					"rooms": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 80}},
					"racks": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 70}},
					"enclosures": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": "aqua", "size": 60}},
					"hvvdcs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": "aqua", "size": 90}},
					"hvpools": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": "aqua", "size": 70}},
					"hvs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": "aqua", "size": 50}},
					"envs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf24d", "color": "lightgreen", "size": 100}},
					"resource": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf292", "color": "lightgreen", "size": 50}},
					"svc": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "lightgreen", "size": 50}}
				},
				clickToUse: true,
				height: _height+'px',
				nodes: {
					size: 32,
					font: {
						face: "arial",
						size: 12
					}
				},
				edges: {
					font: {
						face: "arial",
						size: 12
					}
				}
			}
			var network = new vis.Network(eid, _data, options)
		})
	}

	o.div.load('/init/static/views/topology.html', "", function() {
		o.div.i18n()
		o.viz = o.div.find("#viz")
		o.link = o.div.find(".link16")
		o.button = o.div.find("input[type=submit]")
		o.toggle_config = o.div.find("[name=configure_toggle]")
		o.config = o.div.find("[name=configure]")
		o.init()
	})
}


