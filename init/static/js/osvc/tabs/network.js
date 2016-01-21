//
// network
//
function network_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    o.closetab.children("p").text(o.options.network_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "net16"
    })
    o.tabs[i].callback = function(divid) {
      network_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "network_tabs.segments",
      "title_class": "net16"
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

		o.load_groups()

	}

	o.load_groups = function() {
	   	services_osvcgetrest("R_GROUPS", [], {"meta": "false", "limit": "0","query": "not role starts with user_"}, function(jd) {
			var data = jd.data
			var pg = []
			var org_groups = {}
			var priv_groups = {}

			for (var i=0; i<data.length; i++) {
				var d = data[i]
				if (d.privilege == true) {
					priv_groups[d.role] = d
				} else {
					org_groups[d.role] = data[i]

					// for automplete
					pg.push({
						"label" : d.role,
						"id" : d.id
					})
				}
			}

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
					//$(this).unbind("mouseenter mouseleave click")
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
						e.find("form").submit(function(event) {
							event.preventDefault()
							var input = $(this).find("input[type=text],select")
							input.blur()
							var data = {}
							data[input.attr("pid")] = input.val()
							services_osvcpostrest("R_NETWORK", [o.options.network_id], "", data, function(jd) {
								if (jd.error && (jd.error.length > 0)) {
									$(".flash").show("blind").html(services_error_fmt(jd))
									return
								}
								e.hide()
								e.prev().text(input.val()).show()
							},
							function(xhr, stat, error) {
								$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
							})
						})
					} else if (updater == "group") {
						var e = $("<td></td>")
						var form = $("<form></form>")
						var input = $("<input class='oi' type='text'></input>")
						e.append(form)
						form.append(input)
						e.css({"padding-left": "0px"})
						input.val($(this).text())
						input.attr("pid", $(this).attr("id"))
						input.autocomplete({
							source: pg,
							minLength: 0,
							select: function(event, ui) {
								o.set_group(e, ui.item.label)
								event.preventDefault()
							}
						})
						e.find("form").submit(function(event) {
							event.preventDefault()
							var val = input.val()
							if (!(val in org_groups)) {
								return
							}
							o.set_group(e, val)
						})
						input.bind("blur", function(){
							$(this).parents("td").first().siblings("td").show()
							$(this).parents("td").first().hide()
						})
						$(this).parent().append(e)
						$(this).hide()
						input.focus()
					}
				})
			})
		})
	}

	o.set_group = function(e, val) {
		var data = {
			"team_responsible": val
		}
		services_osvcpostrest("R_NETWORK", [o.options.network_id], "", data, function(jd) {
			e.hide()
			e.prev().text(val).show()
		})
	}

	o.div.load("/init/static/views/network_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


