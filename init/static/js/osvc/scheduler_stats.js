function scheduler_stats(divid) {
	var o = {}
	o.div = $("#"+divid)

	o.refresh = function() {
		services_osvcgetrest("R_SCHEDULER_STATS", "", "", function(jd) {
			o.load_feed_task_status(jd)

			setTimeout(function() {
				o.refresh()
			}, 3000)
		})
	}

	o.load_feed_task_status = function(data) {
		if (o.plot_feed_task_status) {
			o.plot_feed_task_status.destroy()
		}
		var d = []
		var labels = []
		for (key in data.feed.status) {
			labels.push(key)
			d.push(data.feed.status[key].count)
		}
		console.log(d)

		$.jqplot.config.enablePlugins = true;
		o.plot_feed_task_status = $.jqplot(o.e_feed_task_status.attr("id"), [d], {
			stackSeries: true,
			grid: {
				borderWidth: 0.5
			},
			legend: {
				show: false,
				location: 'e',
				placement: "outside"
			},
			gridPadding: {
				right: 90
			},
			seriesDefaults: {
				renderer: $.jqplot.BarRenderer,
				rendererOptions: {
					barDirection: 'horizontal',
					barWidth: 20,
					barPadding: 6
				},
				shadowAngle: 135
			},
			series: [
				{label: 'count'}
			],
			axes: {
				xaxis: {
					min: 0,
					tickOptions: {formatString:'%d'}
				},
				yaxis: {
					renderer: $.jqplot.CategoryAxisRenderer,
					ticks: labels
				}
			}
		})
	}

	o.div.load("/init/static/views/scheduler_stats.html", function() {
		o.div.i18n()
		o.e_feed_task_status = $("[name=feed_task_status]")
		o.e_feed_task_status.uniqueId()

		o.refresh()
	})

	return o
}
