//
// quotas
//
function quota_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    var title = o.options.quota_id
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      quota_properties(divid, o.options)
    }

    // tab usage
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "spark16"
    })
    o.tabs[i].callback = function(divid) {
      services_osvcgetrest("R_ARRAY_DISKGROUP_QUOTA", [0, 0, o.options.quota_id], {"meta": "0"}, function(jd) {
        $.ajax({
          "url": "/init/disks/ajax_app",
          "type": "POST",
          "success": function(msg) {$("#"+divid).html(msg)},
          "data": {"app_id": jd.data[0].app_id, "dg_id": jd.data[0].dg_id, "rowid": divid}
        })
      })
    }

    o.set_tab(o.options.tab)
  })

  return o
}

function quota_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.app_loaded = $.Deferred()

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_array_name = o.div.find("#array_name")
		o.info_array_model = o.div.find("#array_model")
		o.info_array_firmware = o.div.find("#array_firmware")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_size = o.div.find("#dg_size")
		o.info_dg_free = o.div.find("#dg_free")
		o.info_dg_used = o.div.find("#dg_used")
		o.info_dg_reserved = o.div.find("#dg_reserved")
		o.info_app = o.div.find("#app")
		o.info_quota = o.div.find("#quota")
		o.load_quota()
	}

	o.load_quota = function() {
		services_osvcgetrest("R_ARRAY_DISKGROUP_QUOTA", [0, 0, o.options.quota_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_quota()
		})
	}

	o._load_quota = function() {
		o.info_id.html(o.data.id)
		$.data(o.info_quota, "v", o.data.quota)
		cell_decorator_size_mb(o.info_quota)

		services_osvcgetrest("R_APPS", [0, o.data.app_id], "", function(jd) {
			o.info_app.html(jd.data[0].app)
			o.app_loaded.resolve(true)
		})

		services_osvcgetrest("R_ARRAY_DISKGROUP", [0, o.data.dg_id], "", function(jd) {
			o.info_dg_name.html(jd.data[0].dg_name)

			$.data(o.info_dg_free, "v", jd.data[0].dg_free)
			$.data(o.info_dg_size, "v", jd.data[0].dg_size)
			$.data(o.info_dg_used, "v", jd.data[0].dg_used)
			$.data(o.info_dg_reserved, "v", jd.data[0].dg_reserved)
			cell_decorator_size_mb(o.info_dg_free)
			cell_decorator_size_mb(o.info_dg_size)
			cell_decorator_size_mb(o.info_dg_used)
			cell_decorator_size_mb(o.info_dg_reserved)

			services_osvcgetrest("R_ARRAY", [jd.data[0].array_id], "", function(jd) {
				o.info_array_name.html(jd.data[0].array_name)
				o.info_array_model.html(jd.data[0].array_model)
				o.info_array_firmware.html(jd.data[0].array_firmware)
			})
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
						var new_quota = Math.ceil(convert_size(input.val()) / 1024 / 1024)
						data[input.attr("pid")] = new_quota
						services_osvcpostrest("R_ARRAY_DISKGROUP_QUOTA", [0, o.data.dg_id, o.options.quota_id], "", data, function(jd) {
							if (jd.error && (jd.error.length > 0)) {
								$(".flash").show("blind").html(services_error_fmt(jd))
								return
							}
							e.hide()
							var cell = e.prev()
							$.data(cell, "v", new_quota)
							cell_decorator_size_mb(cell)
							cell.show()
						},
						function(xhr, stat, error) {
							$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
						})
					})
				} else if (updater == "app") {
					var e = $("<td></td>")
					var form = $("<form></form>")
					var input = $("<input class='oi' type='text'></input>")
					e.append(form)
					form.append(input)
					e.css({"padding-left": "0px"})
					input.val($(this).text())
					input.attr("pid", $(this).attr("id"))
					services_osvcgetrest("R_APPS", "", {"limit": "0", "orderby": "app"}, function(jd) {
						var opts = []
						for (var i=0; i<jd.data.length; i++) {
							opts.push({
								"label": jd.data[i].app,
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
						o.set_app(e, val, label)
					})
				}
			})
		})
	}

	o.set_app = function(e, val, label) {
		var data = {
			"app_id": val
		}
		services_osvcpostrest("R_ARRAY_DISKGROUP_QUOTA", [0, o.data.dg_id, o.data.id], "", data, function(jd) {
			e.hide()
			e.prev().text(label).show()
		})
	}

	o.div.load("/init/static/views/quota_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}

