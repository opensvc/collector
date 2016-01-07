function dns_domain_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_name = o.div.find("#name")
		o.info_type = o.div.find("#type")
		o.info_account = o.div.find("#account")
		o.info_last_check = o.div.find("#last_check")
		o.info_notified_serial = o.div.find("#notified_serial")
		o.info_master = o.div.find("#master")

		o.load_dns_domain()
	}

	o.load_dns_domain = function() {
		services_osvcgetrest("R_DNS_DOMAIN", [o.options.domain_id], "", function(jd) {
			o._load_dns_domain(jd.data[0])
		})
	}

	o._load_dns_domain = function(data) {
		o.info_id.html(data.id)
		o.info_name.html(data.name)
		o.info_type.html(data.type)
		o.info_account.html(data.account)
		o.info_last_check.html(data.last_check)
		o.info_notified_serial.html(data.notified_serial)
		o.info_master.html(data.master)

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
						services_osvcpostrest("R_DNS_DOMAIN", [o.options.domain_id], "", data, function(jd) {
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
						"NATIVE",
						"MASTER",
						"SLAVE"
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
		services_osvcpostrest("R_DNS_DOMAIN", [o.options.domain_id], "", data, function(jd) {
			e.hide()
			e.prev().text(val).show()
		})
	}

	o.div.load("/init/static/views/dns_domain_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}

