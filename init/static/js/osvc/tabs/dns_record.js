//
// dns records
//
function dns_record_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    services_osvcgetrest("R_DNS_RECORD", [o.options.record_id], {"meta": "0"}, function(jd) {
      o.data = jd.data[0]
      o._load()
    })
  })

  o._load = function() {
    var title = o.data.name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "dns_record_tabs.properties",
      "title_class": "dns16"
    })
    o.tabs[i].callback = function(divid) {
      dns_record_properties(divid, o.options)
    }

    if ((typeof(o.data.type) === "string") && (o.data.type.length > 0) && (o.data.type[0] == "A")) {
      // tab alerts
      i = o.register_tab({
        "title": "dns_record_tabs.nodes",
        "title_class": "node16"
      })
      o.tabs[i].callback = function(divid) {
        table_nodenetworks_addr(divid, o.data.content)
      }
    }

    o.set_tab(o.options.tab)
  }

  return o
}

function dns_record_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_name = o.div.find("#name")
		o.info_type = o.div.find("#type")
		o.info_content = o.div.find("#content")
		o.info_prio = o.div.find("#prio")
		o.info_ttl = o.div.find("#ttl")
		o.info_domain = o.div.find("#domain")
		o.info_change_date = o.div.find("#change_date")
		o.info_nodes = o.div.find("#nodes")
		o.load_dns_record()
	}

	o.load_dns_record = function() {
		services_osvcgetrest("R_DNS_RECORD", [o.options.record_id], "", function(jd) {
			o._load_dns_record(jd.data[0])
		})
	}

	o._load_dns_record = function(data) {
		o.info_id.html(data.id)
		o.info_name.html(data.name)
		o.info_type.html(data.type)
		o.info_content.html(data.content)
		o.info_prio.html(data.prio)
		o.info_ttl.html(data.ttl)
		o.info_change_date.html(data.change_date)

		services_osvcgetrest("R_DNS_DOMAIN", [data.domain_id], "", function(jd) {
			o.info_domain.html(jd.data[0].name)
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
						services_osvcpostrest("R_DNS_RECORD", [o.options.record_id], "", data, function(jd) {
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
				} else if (updater == "domain") {
					var e = $("<td></td>")
					var form = $("<form></form>")
					var input = $("<input class='oi' type='text'></input>")
					e.append(form)
					form.append(input)
					e.css({"padding-left": "0px"})
					input.val($(this).text())
					input.attr("pid", $(this).attr("id"))
					services_osvcgetrest("R_DNS_DOMAINS", "", "", function(jd) {
						var opts = []
						for (var i=0; i<jd.data.length; i++) {
							opts.push({
								"label": jd.data[i].name,
								"value": jd.data[i].id
							})
						}
						input.autocomplete({
							source: opts,
							minLength: 0,
							select: function(event, ui) {
								o.set_domain(e, ui.item.value, ui.item.label)
								event.preventDefault()
							}
						})
					})
					input.bind("blur", function(){
						$(this).parents("td").first().siblings("td").show()
						$(this).parents("td").first().hide()
					})
					$(this).parent().append(e)
					$(this).hide()
					input.focus()

					e.find("form").submit(function(event) {
						event.preventDefault()
						var val = input.val()
						o.set_domain(e, val, label)
					})
				} else if (updater == "type") {
					var e = $("<td></td>")
					var form = $("<form></form>")
					var input = $("<input class='oi' type='text'></input>")
					e.append(form)
					form.append(input)
					e.css({"padding-left": "0px"})
					input.val($(this).text())
					input.attr("pid", $(this).attr("id"))
					var opts = [
						"A",
						"AAAA",
						"A6",
						"CNAME",
						"DNAME",
						"DNSKEY",
						"DS",
						"HINFO",
						"ISDN",
						"KEY",
						"LOC",
						"MX",
						"NAPTR",
						"NS",
						"NSEC",
						"PTR",
						"SOA",
						"SRV",
						"TXT"
					]
					input.autocomplete({
						source: opts,
						minLength: 0,
						select: function(event, ui) {
							o.set_type(e, ui.item.label)
							event.preventDefault()
						}
					})
					input.bind("blur", function(){
						$(this).parents("td").first().siblings("td").show()
						$(this).parents("td").first().hide()
					})
					$(this).parent().append(e)
					$(this).hide()
					input.focus()

					e.find("form").submit(function(event) {
						event.preventDefault()
						var val = input.val()
						o.set_type(e, val)
					})
				}
			})
		})
	}

	o.set_type = function(e, val) {
		var data = {
			"type": val
		}
		services_osvcpostrest("R_DNS_RECORD", [o.options.record_id], "", data, function(jd) {
			e.hide()
			e.prev().text(val).show()
		})
	}

	o.set_domain = function(e, val, label) {
		var data = {
			"domain_id": val
		}
		services_osvcpostrest("R_DNS_RECORD", [o.options.record_id], "", data, function(jd) {
			e.hide()
			e.prev().text(label).show()
		})
	}

	o.div.load("/init/static/views/dns_record_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}

