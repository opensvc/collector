function scheduler_stats(divid) {
	var o = {}
	o.div = $("#"+divid)
	o.feed_task_status_data = {}

	o.refresh = function() {
		services_osvcgetrest("R_SCHEDULER_STATS", "", "", function(jd) {
			o.load_feed_task_status(jd)

			if (o.div.find("[name=feed_task_status]").length == 0) {
				// stop refreshing if the user nav'ed out
				return
			}
			setTimeout(function() {
				o.refresh()
			}, 6000)
		})
	}

	o.load_feed_task_status = function(data) {
		var now = new Date()
		if (o.plot_feed_task_status) {
			o.plot_feed_task_status.destroy()
		}
		for (key in data.feed.status) {
			if (!(key in o.feed_task_status_data)) {
				o.feed_task_status_data[key] = []
			}
		}
		for (key in o.feed_task_status_data) {
			if (key in data.feed.status) {
				var val = data.feed.status[key].count
			} else {
				var val = 0
			}
			o.feed_task_status_data[key].push([now, val])

			// don't store too many history to not fill up the client ram
			if (o.feed_task_status_data[key].length > 600) {
				o.feed_task_status_data[key].shift()
			}
		}
		var series = []
		var data = []
		for (key in o.feed_task_status_data) {
			series.push({"label": key})
			data.push(o.feed_task_status_data[key])
		}

		$.jqplot.config.enablePlugins = true
		var options = {
			stackSeries: true,
			cursor:{
				zoom: true,
				showTooltip: true
			},
			grid: {
				borderWidth: 0.5
			},
			legend: {
				show: true,
				location: 'e',
				placement: "outside"
			},
			gridPadding: {
				right: 90
			},
			seriesDefaults: {
				markerOptions: {size: 2},
				fill: true,
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
		}
		try {
			o.plot_feed_task_status = $.jqplot(o.e_feed_task_status.attr("id"), data, options)
		} catch (e) { }
	}

	o.div.load("/init/static/views/scheduler_stats.html", function() {
		o.div.i18n()
		o.e_feed_task_status = $("[name=feed_task_status]")
		o.e_feed_task_status.uniqueId()

		o.refresh()
	})

	return o
}
