function array_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_array_name = o.div.find("#array_name")
		o.info_array_model = o.div.find("#array_model")
		o.info_array_firmware = o.div.find("#array_firmware")
		o.info_array_level = o.div.find("#array_level")
		o.info_array_cache = o.div.find("#array_cache")
		o.info_array_updated = o.div.find("#array_updated")
		o.load_array()
	}

	o.load_array = function() {
		services_osvcgetrest("R_ARRAY", [o.options.array_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_array()
		})
	}

	o._load_array = function() {
		o.info_id.html(o.data.id)
		o.info_array_name.html(o.data.array_name)
		o.info_array_model.html(o.data.array_model)
		o.info_array_firmware.html(o.data.array_firmware)
		o.info_array_level.html(o.data.array_level)
		o.info_array_updated.html(o.data.array_updated)
		$.data(o.info_array_cache, "v", o.data.array_cache)
		cell_decorator_size_mb(o.info_array_cache)
	}

	o.div.load("/init/static/views/array_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}

