//
// startup
//
function startup(divid, options) {
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
			o.config.slideDown()
			o.toggle_config.hide()
		})

		// show disabled
		o.e_show_disabled = o.div.find("[name=show_disabled]")
		o.e_show_disabled.uniqueId()
		o.e_show_disabled.siblings("label").attr("for", o.e_show_disabled.attr("id"))
		if (o.options.show_disabled && (o.options.show_disabled != false)) {
			o.e_show_disabled.prop("checked", true)
		}
		o.e_show_disabled.bind("change", function() {
			o.options.show_disabled = o.e_show_disabled.prop("checked")
		})

		// create checkboxes
		var node_ids = []
		services_osvcgetrest("R_SERVICE_INSTANCES", "", {
			"limit": "0",
			"meta": "0",
			"query": "svc_id in " + o.options.svc_ids.join(","),
			"props": "node_id"
		}, function(jd) {
			var data = jd.data
			for (var i=0; i<data.length; i++) {
				var node_id = data[i].node_id
				if (node_ids.indexOf(node_id) >= 0) {
					// already done
					continue
				}
				node_ids.push(node_id)

				//input
				var input = $("<input type='checkbox' name='node_id' class='ocb'></input>")
				input.uniqueId()
				input.css({"vertical-align": "text-bottom"})
				if (!o.options.display && (i == 0)) {
					input.prop("checked", true)
					o.options.display = [input.siblings("span").attr("node_id")]
				} else if (o.options.display.indexOf(node_id) >= 0) {
					input.prop("checked", true)
				} else {
					input.prop("checked", false)
				}

				// ocb label
				var label = $("<label></label>")
				label.attr("for", input.attr("id"))

				// title
				var title = $("<span></span>")
				title.attr("node_id", node_id)
				title.css({"margin-left": "0.2em"})

				// container div
				var d = $("<div class='nowrap'></div>")
				d.append(input)
				d.append(label)
				d.append(title)
				title.osvc_nodename()

				d.insertBefore(o.div.find("input[type=submit]"))
			}

			// form submit
			o.div.find("form").bind("submit", function(event) {
				event.preventDefault()
				o.config.empty()
				o.options.display = []
				$(this).find("input:checked").each(function () {
					o.options.display.push($(this).siblings("span").attr("node_id"))
				})
				o.draw()
			})

			o.draw()
		})

		}

		o.draw = function() {
	}

	o.create_link = function(){
		var display = []
			o.div.find("input[type=checkbox][name=node_id]:checked").each(function() {
			display.push($(this).siblings("span").attr("node_id"))
		})
		o.options.display = display
		osvc_create_link("startup", o.options)
	}

	o.draw = function() {
		var i = 0
		url = $(location).attr("origin") + "/init/topo/call/json/json_startup_data"
		if (o.viz.parents(".overlay").length == 0) {
			_height = $(window).height()-$(".header").outerHeight()-16
			o.viz.height(_height)
		}
		var data = {
			"svc_ids": o.options.svc_ids,
			"node_ids": o.options.display,
			"show_disabled": o.e_show_disabled.prop("checked")
		}
		$.getJSON(url, data, function(_data){
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
						gravitationalConstant: -2500,
						centralGravity: 1,
						springLength: 95,
						springConstant: 0.1,
						damping: 0.5
					}
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
				},
				"groups": {
					"trigger": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf121", "color": "black", "size": 40}},
					"subset": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1b3", "color": "#CC9966", "size": 50}},
					"sync": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c5", "color": "cadetblue", "size": 50}},
					"app": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "seagreen", "size": 50}},
					"container": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "cornflowerblue", "size": 50}},
					"container.docker": {"shape": "image", "image": "/init/static/svg/docker-cornflowerblue.svg"},
					"fs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf07c", "color": "slategray", "size": 50}},
					"hb": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf21e", "color": "red", "size": 50}},
					"share": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e0", "color": "cadetblue", "size": 50}},
					"stonith": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e2", "color": "red", "size": 50}},
					"disk": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": "#dddd66", "size": 50}},
					"disk.scsireserv": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf023", "color": "#dddd66", "size": 50}},
					"ip": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf124", "color": "cadetblue", "size": 50}},
					"node": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf233", "color": "aqua", "size": 50}},
					"resource": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf292", "color": "seagreen", "size": 75}},
					"svc": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "seagreen", "size": 100}}
				}

			}
			var network = new vis.Network(eid, _data, options)
		})
	}

	o.div.load('/init/static/views/startup.html', "", function() {
		o.div.i18n()
		o.viz = o.div.find("#viz")
		o.link = o.div.find(".link16")
		o.button = o.div.find("input[type=submit]")
		o.toggle_config = o.div.find("[name=configure_toggle]")
		o.config = o.div.find("[name=configure]")
		o.init()
	})
}


