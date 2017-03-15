function user_prefs(initial_prefs) {
	var o = {}
	o.data = {}
	o.queued = false

	o.uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
		var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8)
		return v.toString(16)
	})

	o.load = function() {
		services_osvcgetrest("/users/self/prefs", "", {}, function(jd) {
			o.store_data(jd.data)
		})
	}

	o.store_data = function(data) {
		o.data = data
		console.log("user prefs loaded")
	}

	o.save = function() {
		if (o.queued) {
			return
		}
		clearTimeout(o.timer)
		o.timer = setTimeout(function(){
			o.queued = false
			o._save()
		}, 3000)
		o.queued = true
	}

	o._save = function() {
		var data = {
			"data": o.data,
			"uuid": o.uuid
		}
		services_osvcpostrest("/users/self/prefs", "", "", data, function(jd) {
			o.saving = false
			if (jd.error) {
				osvc.flash.error(services_error_fmt(jd))
				return
			}
			console.log("user prefs saved")
		},
		function(xhr, stat, error){
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "user_prefs_change") {
			var d = data.data
			if (d.user_id != _self.id) {
				return
			}
			if (d.uuid == o.uuid) {
				console.log("skip user prefs change event caused by our own post")
				return
			}
			o.load()
			return
		}
	}

	wsh["user_prefs_change"] = function(data) {
		o.event_handler(data)
	}

	if (initial_prefs) {
		o.store_data(initial_prefs)
	}

	return o
}

