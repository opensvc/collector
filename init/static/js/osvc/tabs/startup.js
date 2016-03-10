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
			o.config.show("fold")
			o.toggle_config.hide()
		})

		// show disabled
		o.e_show_disabled = o.div.find("[name=show_disabled]")
		o.e_show_disabled.uniqueId()
		o.e_show_disabled.siblings("label").attr("for", o.e_show_disabled.attr("id"))
		console.log(o.options.show_disabled)
		if (o.options.show_disabled && (o.options.show_disabled != "false")) {
			o.e_show_disabled.prop("checked", true)
		}

		// create checkboxes
		var nodenames = []
		services_osvcgetrest("R_SERVICE_INSTANCES", "", {
			"limit": "0",
			"meta": "0",
			"query": "mon_svcname in " + o.options.svcnames.join(","),
			"props": "mon_nodname"
		}, function(jd) {
			var data = jd.data
			for (var i=0; i<data.length; i++) {
				var nodename = data[i].mon_nodname
				if (nodenames.indexOf(nodename) >= 0) {
					// already done
					continue
				}
				nodenames.push(nodename)

				//input
				var input = $("<input type='checkbox' name='nodename' class='ocb'></input>")
				input.uniqueId()
				input.css({"vertical-align": "text-bottom"})
				if (o.options.display && (o.options.display.indexOf(nodename) >= 0)) {
					input.prop("checked", true)
				} else {
					input.prop("checked", false)
				}
				input.bind("change", function() {
					o.create_link()
				})

				// ocb label
				var label = $("<label></label>")
				label.attr("for", input.attr("id"))

				// title
				var title = $("<span></span>")
				title.addClass("icon hw16")
				title.css({"margin-left": "0.2em"})
				title.text(nodename)

				// container div
				var d = $("<div></div>")
				d.append(input)
				d.append(label)
				d.append(title)

				d.insertBefore(o.div.find("input[type=submit]"))
			}
			if (o.div.find("input[type=checkbox]:checked").length == 0) {
				o.div.find("input[type=checkbox]").first().each(function(){
					$(this).prop("checked", true)
					o.options.display = [$(this).siblings("span").text()]
				})
			}

			// form submit
			o.div.find("form").bind("submit", function(event) {
				event.preventDefault()
				o.config.empty()
				o.options.display = []
				$(this).find("input:checked").each(function () {
					o.options.display.push($(this).siblings("span").text())
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
			o.div.find("input[type=checkbox][name=nodename]:checked").each(function() {
			display.push($(this).siblings("span").text())
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
			"svcnames": o.options.svcnames,
			"nodenames": o.options.display,
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
					"app": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "lightgreen", "size": 50}},
					"container": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": "cornflowerblue", "size": 50}},
					"fs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf07c", "color": "slategray", "size": 50}},
					"hb": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf21e", "color": "red", "size": 50}},
					"share": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e0", "color": "cadetblue", "size": 50}},
					"stonith": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e2", "color": "red", "size": 50}},
					"disk": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": "#dddd66", "size": 50}},
					"disk.scsireserv": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf023", "color": "#dddd66", "size": 50}},
					"ip": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf124", "color": "cadetblue", "size": 50}},
					"node": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf233", "color": "aqua", "size": 50}},
					"resource": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf292", "color": "lightgreen", "size": 75}},
					"svc": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "lightgreen", "size": 100}}
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


