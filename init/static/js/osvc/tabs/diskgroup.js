function diskgroup_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_name = o.div.find("#dg_name")
		o.info_dg_size = o.div.find("#dg_size")
		o.info_dg_free = o.div.find("#dg_free")
		o.info_dg_used = o.div.find("#dg_used")
		o.info_dg_reserved = o.div.find("#dg_reserved")
		o.info_dg_updated = o.div.find("#dg_updated")
		o.info_array_name = o.div.find("#array_name")
		o.info_array_model = o.div.find("#array_model")
		o.info_array_firmware = o.div.find("#array_firmware")
		o.load_diskgroup()
	}

	o.load_diskgroup = function() {
		services_osvcgetrest("R_ARRAY_DISKGROUP", [0, o.options.dg_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_diskgroup()
		})
	}

	o._load_diskgroup = function() {
		o.info_id.html(o.data.id)
		o.info_dg_name.html(o.data.dg_name)
		o.info_dg_updated.html(o.data.dg_updated)
		$.data(o.info_dg_free, "v", o.data.dg_free)
		$.data(o.info_dg_size, "v", o.data.dg_size)
		$.data(o.info_dg_used, "v", o.data.dg_used)
		$.data(o.info_dg_reserved, "v", o.data.dg_reserved)
		cell_decorator_size_mb(o.info_dg_free)
		cell_decorator_size_mb(o.info_dg_size)
		cell_decorator_size_mb(o.info_dg_used)
		cell_decorator_size_mb(o.info_dg_reserved)

		services_osvcgetrest("R_ARRAY", [o.data.array_id], "", function(jd) {
			o.info_array_name.html(jd.data[0].array_name)
			o.info_array_model.html(jd.data[0].array_model)
			o.info_array_firmware.html(jd.data[0].array_firmware)
		})
	}

	o.div.load("/init/static/views/diskgroup_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}

