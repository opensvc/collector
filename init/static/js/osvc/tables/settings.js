function table_settings() {
	var o = {}

	o.load = function() {
		o.data = {}
		var data = {
			"limit": "0",
			"meta": "0",
			"props": "upc_table,upc_field,upc_visible"
		}
		services_osvcgetrest("R_USERS_SELF_TABLE_SETTINGS", "", data, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var d = jd.data[i]
				if (!(d.upc_table in o.data)) {
					o.data[d.upc_table] = {}
				}
				o.data[d.upc_table][d.upc_field] = d.upc_visible
			}
			osvc.table_settings_loaded.resolve(true)
			console.log("table settings loaded")
		})
	}

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "user_prefs_columns_change") {
			var d = data.data
			if (d.user_id != _self.id) {
				return
			}
			o.load()
			return
		}
	}

	o.load()

	wsh["table_settings"] = function(data) {
		o.event_handler(data)
	}

	return o
}

