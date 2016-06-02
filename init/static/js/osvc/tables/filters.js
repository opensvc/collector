/*
        {
            "user_id": 1, 
            "bookmark": "current", 
            "col_name": "app", 
            "col_tableid": "disks", 
            "col_filter": "SIC", 
            "id": 46604
        }
*/
function table_column_filters() {
	var o = {}

	o.load = function() {
		var data = {
			"limit": "0",
			"meta": "0",
			"props": "bookmark,col_name,col_tableid,col_filter"
		}
		services_osvcgetrest("R_USERS_SELF_TABLE_FILTERS", "", data, function(jd) {
			o.store_data(jd.data)
		})
	}

	o.store_data = function(data) {
		o.data = {}
		for (var i=0; i<data.length; i++) {
			var d = data[i]
			if (!(d.col_tableid in o.data)) {
				o.data[d.col_tableid] = {}
			}
			if (!(d.bookmark in o.data[d.col_tableid])) {
				o.data[d.col_tableid][d.bookmark] = {}
			}
			o.data[d.col_tableid][d.bookmark][d.col_name] = d.col_filter
		}
	}

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "column_filters_change") {
			var d = data.data
			if (d.user_id != _self.id) {
				return
			}
			o.load()
			return
		}
	}

	wsh["table_filters"] = function(data) {
		o.event_handler(data)
	}

	return o
}

