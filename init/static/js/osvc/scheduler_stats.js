function scheduler_stats(divid) {
	var o = {}
	o.div = $("#"+divid)
	o.queue_data = {}

	o.queues = function() {
		services_osvcgetrest("R_SCHEDULER_STATS", "", "", function(jd) {
			o.load_queue(jd)

			if (o.div.find("[name=queue]").length == 0) {
				// stop refreshing if the user nav'ed out
				return
			}
			setTimeout(function() {
				o.queues()
			}, 6000)
		})
	}

	o.plot_options = function(series) {
		return options = $.extend({}, chart_defaults, {
			stackSeries: false,
			seriesDefaults: {
				markerOptions: {size: 2},
				fill: false,
				shadowAngle: 135,
				shadowOffset: 1.0,
				breakOnNull : true,
				shadowWidth: 2
			},
			series: series,
			axes: {
				xaxis: {
					renderer: $.jqplot.DateAxisRenderer,
					tickOptions:{formatString:'%b,%d\n%H:%M'}
				},
				yaxis: {
					min: 0,
					tickOptions: {formatString:'%d'}
				}
			}
		})
	}

	o.load_queue = function(data) {
		var now = new Date()
		if (o.plot_queue) {
			o.plot_queue.destroy()
		}
		for (key in data.queue) {
			if (!(key in o.queue_data)) {
				o.queue_data[key] = []
			}
		}
		for (key in o.queue_data) {
			if (key in data.queue) {
				var val = data.queue[key].count
			} else {
				var val = 0
			}
			o.queue_data[key].push([now, val])

			// don't store too many history to not fill up the client ram
			if (o.queue_data[key].length > 600) {
				o.queue_data[key].shift()
			}
		}
		var series = []
		var data = []
		for (key in o.queue_data) {
			series.push({"label": key})
			data.push(o.queue_data[key])
		}

		$.jqplot.config.enablePlugins = true
		var options = o.plot_options(series)
		options.seriesDefaults.fill = false
		options.stackSeries = false
		try {
			o.plot_queue = $.jqplot(o.e_queue.attr("id"), data, options)
		} catch (e) { }
	}

	o.tasks = function() {
		var div = $("[name=tasks]")
		div.uniqueId()
		table_scheduler_tasks(div.attr("id"))
	}

	require(["jqplot"], function() {
		o.div.load("/init/static/views/scheduler_stats.html?v="+osvc.code_rev, function() {
			o.div.i18n()
			o.e_queue = $("[name=queue]")
			o.e_queue.uniqueId()
			o.e_tasks = $("[name=tasks]")
			o.e_tasks_table = $("<table class='table'></table>")
			o.e_tasks.append(o.e_tasks_table)

			o.queues()
			o.tasks()
		})
	})

	return o
}
