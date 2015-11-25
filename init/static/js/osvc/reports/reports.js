function metric(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)

	o.load = function load() {
		// metric area
		var div = $("<div class='reports_section' style='float:left;min-width:28%'></div>")
		o.div.append(div)

		// link
		var title_h = $("<h3></h3>")
		var title_link = $("<span class='clickable icon link16'>&nbsp;</span>")
		title_link.bind("click", function() {  
			osvc_create_link("metric", o.options)
		})
		title_h.append(title_link)
		div.append(title_h)

		// title
		if (o.options.Title && o.options.Title != "") {
			title_h.append(o.options.Title)
		}

		// desc
		if (o.options.Desc !== undefined && o.options.Desc != "") {
			var desc = $("<div></div>")
			desc.text(o.options.Desc)
			div.append(desc)
		}

		// metric table area
		o.table = $("<table class='reports_table'></table>")
		div.append(o.table)

		// render table
		o.render_table()

	}

	o.render_table = function() {
		services_osvcgetrest("R_GET_REPORT_METRIC_SAMPLES", [o.options.metric_id], {"meta": "false", "limit": "0"}, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
				return
			}
			var data = jd.data;
			if (data.length == 0) {
				o.table.text(i18n.t("metrics.no_data"))
			}

			var objname = [];

			// table header
			var header = $("<tr></tr>")
			o.table.append(header)
			for (var key in data[0]) {
				var th = $("<th></th>")
				th.text(key)
				header.append(th)
				objname.push(key)
			}

			// table data
			for (var i=0; i<data.length; i++) {
				var point = data[i]
				var tr = $("<tr></tr>")
				for (var j=0; j<objname.length; j++) {
					var name = objname[j]
					var val = point[name]
					if (val == null) {
						continue
					}
					var td = $("<td></td>")
					td.text(val)
					tr.append(td)
				}
				o.table.append(tr)
			}
		})
	}

	o.load()
}

function chart(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)

	o.load = function load() {
		// chart area
		var div = $("<div class='reports_section'></div>")
		o.div.append(div)

		// link
		var title_link = $("<span class='clickable icon link16'></span>")
		var title_h = $("<h3></h3>")
		title_link.bind("click", function() {  
			osvc_create_link("chart", o.options)
		})
		title_h.append(title_link)
		div.append(title_h)

		// title
		if (o.options.Title && o.options.Title != "") {
			title_h.append(o.options.Title)
		}

		// desc
		if (o.options.Desc !== undefined && o.options.Desc != "") {
			var desc = $("<div></div>")
			desc.text(o.options.Desc)
			div.append(desc)
		}

		// chart plot area
		var plot_div = $("<div style='width:94%;height:600px;overflow-y:auto'>")
		plot_div.uniqueId()
		div.append(plot_div)

		// chart
		o.plot(plot_div.attr("id"));

	}

	o.plot = function reports_charts_plot(id) {
		$.jqplot.config.enablePlugins = true
		services_osvcgetrest("R_GET_REPORT_CHART_SAMPLES", [o.options.chart_id], {"meta": "false", "limit": "5000"}, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
				return
			}
			var data = jd.data
			var keys = {}
			var definition = jd.chart_definition
			var metric_definition = {}
			var stackSeries = definition.Options.stack
			var series = []
			var series_data = {}
			var max = 0
			var unit = ""

			for (var i=0; i<definition.Metrics.length; i++) {
				var m = definition.Metrics[i]
				metric_definition[m.metric_id] = m
				if (m.unit) {
					unit = m.unit
				}
			}

			for (var i=0; i<data.length; i++) {
				var point = data[i]
				var key = point.metric_id+"-"+point.instance
				if (!(key in keys)) {
					keys[key] = {
					  "metric_id": point.metric_id,
					  "instance": point.instance
					}
					series_data[key] = []
				}
				max = Math.max(max, point.value)
			}

			var divisor = best_unit_mb(max, unit)
			for (var i=0; i<data.length; i++) {
				var point = data[i]
				var key = point.metric_id+"-"+point.instance
				series_data[key].push([point.date, point.value/divisor['div']])
			}

			var series_list = Object.keys(series_data).map(function (key) {
				return series_data[key];
			})

			if (Object.keys(keys).length > 1) {
				legend = {
				  renderer: $.jqplot.EnhancedLegendRenderer,
				  rendererOptions: {
				    numberRows: 0,
				    numberColumns: 10
				  },
				  show: true,
				  placement: "outside",
				  location: 's',
				  fontSize : '1',
				  rowSpacing : '0.05em',
				  yoffset: 40
				}
			} else {
				legend = {
				  show: false
				}
			}
			for (key in keys) {
				var kc = keys[key]
				var serie = {
				  'label': kc.instance,
				  'shadow': metric_definition[kc.metric_id].shadow,
				  'fill': metric_definition[kc.metric_id].fill
				}
				series.push(serie)
			}
			delete metric_definition
			delete series_data
	
			p = $.jqplot(id, series_list, {
				stackSeries: stackSeries,
				cursor:{
				  zoom:true,
				  showTooltip:false
				},
				legend: legend,
				grid: {
				  borderWidth: 0.5,
				  shadowOffset: 1.0,
				  shadowWidth: 2
				},
				seriesDefaults: {
				  breakOnNull : true,
				  shadowAngle: 135,
				  shadowOffset: 1.0,
				  shadowWidth: 2
				},
				series: series,
				axes: {
				  xaxis: {
				    renderer: $.jqplot.DateAxisRenderer,
				    numberTicks: 5,
				    tickOptions:{
				      formatString:'%b,%d\n%H:%M'
				    }
				  },
				  yaxis: {
				    min: 0,
				    tickOptions:{
				      formatString: divisor['fmt']+' '+divisor['unit']
				    }
				  }
				}
			})
		})
	}
	o.load()
}

function report(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)

	o.create = function() {
		// report area
		o.report_div = $("<div class='reports_div'></div>");
		o.div.append(o.report_div)

		// title
		var title_link = $("<span class='clickable icon link16'></span>")
		var title_h = $("<h1></h1>")
		title_h.append(title_link)
		title_h.append(o.definition.Title)
		o.report_div.append(title_h)

		// bind the report link click
		title_link.bind("click", function() { 
			osvc_create_link("report", {"report_id" : o.options.report_id })
		})
 	}

	o.load_sections = function() {
		for(var i=0; i<o.definition.Sections.length; i++) {
			var section = o.definition.Sections[i]

			// section area
			var section_div = $("<div style='clear:both;'></div>")
			section_div.uniqueId()
			o.report_div.append(section_div)

			// title
			if (section.Title !== undefined) {
				var title_h = $("<h3 class='line yellow' style='text-align:left;padding: 0.3em'></h3>")
				var title_span = $("<span class='menu16'></span>")
				title_span.text(section.Title)
				title_h.append(title_span)
				section_div.append(title_h)
			}

			// desc
			if (section.Desc !== undefined) {
				section_div.append("<div style='padding:1em'>" + section.Desc + "</div>")
			}

			// charts reports
			if (section.Charts !== undefined) {
				for(var l=0; l<section.Charts.length; l++) {
					chart(section_div.attr("id"), section.Charts[l])
				}
			}
			// metrics reports
			if (section.Metrics !== undefined) {
				for (var l=0; l<section.Metrics.length; l++) {
					metric(section_div.attr("id"), section.Metrics[l])
				}
			}
		}
	}

	o.load = function() {
		services_osvcgetrest("R_GET_REPORT", [o.options.report_id], {"meta": "false", "limit": "0"}, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				$("#flash").show("blind").html(services_error_fmt(jd))
				return
			}
			o.definition = jd.data
			o.create()
			o.load_sections()
		})
	}

	o.load()
}

function reports(divid, options)
{
	var o = {}
	o.options = options
	o.divid = divid
	o.div = $("#"+divid)
  
	o.current_reports = 0;

	o.init = function init() {
		return reports_init(o)
	}
	o.load = function load() {
		return reports_load(o)
	}
	o.select_report = function select_report(report_id) {
		return reports_set_selected(o, report_id);
	}
	o.refresh = function refresh(report_id) {
		return reports_refresh(o, report_id);
	}
	o.build_selection = function build_selection(data) {
		return reports_build_selection(o, data);
	}
	o.load_selected = function(report_id) {
		return reports_load_selected(o, report_id)
	}

	o.div.load("/init/static/views/reports.html", function() {
		o.init()
	})
	return o;
}

function reports_init(o) {
	o.div_reports_header = o.div.find("#reports_header");
	o.div_reports_data = o.div.find("#reports_data");
	o.ql_link = o.div.find("#reports_ql_link");
	o.reports_select = o.div_reports_header.find("#reports_select");
	o.reports_select_off = o.div_reports_header.find("#reports_select_off");

	o.div_reports_data.bind("click", function () {
		o.reports_select.hide("slide", { direction: "left" }, 500);
		o.reports_select_off.show("slide", { direction: "left" }, 500);
	})

	o.reports_select_off.bind("click", function() {
		o.reports_select.show("slide", { direction: "left" }, 500);
		o.reports_select_off.hide("slide", { direction: "left" }, 500);
	})
	o.load();
	o.reports_select_off.show();
}

function reports_load(o) {  
	// Init Select Report
	services_osvcgetrest("R_GET_REPORTS", "", {"meta": "false", "limit": "0"}, function(jd) {
		if (jd.error && (jd.error.length > 0)) {
			$("#flash").show("blind").html(services_error_fmt(jd))
			return
		}
		var data = jd.data;
		if (data.length == 0) {
			return
		}
		o.build_selection(data);
		o.load_selected(data[0].id);
		o.select_report(data[0].id); 
	})
}

function reports_build_selection(o, data) {
	var sect_div = $("<div style='clear:both'></div>")
	o.reports_select.empty()
	o.reports_select.append(sect_div)

	for (var i=0; i<data.length; i++) {
		var faccess = $("<div class='report_button_div'></div>")
		faccess.attr("report_id", data[i].id)
		faccess.text(data[i].report_name)
		faccess.bind("click", function(event) {
			var report_id = $(this).attr("report_id");
			o.refresh(report_id)
		})
		sect_div.append(faccess)
	}
}

function reports_set_selected(o, report_id) {
	o.current_reports = report_id
	o.reports_select.find("[report_id="+o.current_reports+"]").removeClass("report_button_div_active")
	o.reports_select.find("[report_id="+o.current_reports+"]").addClass("report_button_div_active")
}

function reports_refresh(o, report_id) {
	o.div_reports_data.empty();
	o.load_selected(report_id);
	o.select_report(report_id);
}

function reports_load_selected(o, report_id) {
	o.report_id = report_id
	report("reports_data", {"report_id": report_id})
}


