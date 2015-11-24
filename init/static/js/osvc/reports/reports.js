function reports_single(divid,options)
{
    o = reports_init(divid, options);

    if (options !== undefined)
    {
      reports_load_selected(o,options.report_id);
      $(document).find("#link").removeAttr("style");
    }
}

function reports(divid, options)
{
  o = reports_init(divid, options, function () {
    o.reports_select = o.div_reports_header.find("#reports_select");
    o.reports_select_off = o.div_reports_header.find("#reports_select_off");

    o.div_reports_data.bind("click", function () {
      o.reports_select.hide("slide", { direction: "left" }, 500);
      o.reports_select_off.show("slide", { direction: "left" }, 500);
    });

     o.reports_select_off.bind("click", function() {
      o.reports_select.show("slide", { direction: "left" }, 500);
      o.reports_select_off.hide("slide", { direction: "left" }, 500);
     });
    o.load(options);
    o.reports_select_off.show();
   });
}

function reports_init(divid, options, callback) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  
  o.current_reports = 0;

  o.init = function init(options) {
    return reports_init(o, options)
  }

  o.load = function load(options) {
    return reports_load(o, options)
  }

  o.create_report = function create_report(data, report_id) {
    return reports_create_report(o, data, report_id);
  }

  o.create_sections_metric = function create_sections_metric(section, count)
  {
    return reports_create_sections_metric(o, section, count);
  }

  o.create_sections_chart = function create_sections_chart(section, count)
  {
    return reports_create_sections_chart(o, section, count);
  }

  o.select_report = function select_report(report_id)
  {
    return reports_set_selected(o, report_id);
  }

  o.refresh = function refresh(event) {
    return reports_refresh(o, event);
  }
  
  o.create_section = function create_section(section, count) {
    return reports_create_section(o, section, count);
  }

  o.build_selection = function build_selection(data) {
    return reports_build_selection(o, data);
  }

  o.div.load("/init/static/views/reports.html", function() {
    o.div_reports_header = o.div.find("#reports_header");
    o.div_reports_data = o.div.find("#reports_data");
    o.ql_link = o.div.find("#reports_ql_link");
    callback();
  })
  return o;
}

function reports_load(o, options)
{  
  // Init Select Report
  services_osvcgetrest("R_GET_REPORTS", "", {"meta": "false", "limit": "0"}, function(jd) {
      var data = jd.data;
 
      if (data.length >0) 
      {
        o.build_selection(data);
        reports_load_selected(o,data[0].id);
        o.select_report(data[0].id); 
      }
  });
}

function reports_build_selection(o, data)
{
  var div = $("<div></div>");
  var sect_div = $("<div style='clear:both'></div>");
  div.append(sect_div);
  for (var i=0;i<data.length;i++)
  {
    var faccess = "<div id='reports_fa_"+i+"' class='report_button_div' value='" + data[i].id + "'>" + data[i].report_name + "</div>";
    sect_div.append(faccess);
    sect_div.find("#reports_fa_"+i).bind("click", function()
      {
        o.refresh(this);
      });
  }
  o.reports_select.append(div.children());
}

function reports_set_selected(o, report_id)
{
  o.reports_select.find("[value="+o.current_reports+"]").removeClass("report_button_div_active");
  o.current_reports = report_id;
  o.reports_select.find("[value="+o.current_reports+"]").addClass("report_button_div_active");
}

function reports_refresh(o, event)
{
  o.div_reports_data.empty();
  var report_id = $(event).attr("value");
  // Reload data
  reports_load_selected(o,report_id);
  o.select_report(report_id);
}

function reports_load_selected(o, report_id)
{
  services_osvcgetrest("R_GET_REPORT", [report_id], {"meta": "false", "limit": "0"}, function(jd) {
      var data = jd.data;
      o.create_report(jd.data, report_id);
      // Refresh data
      for(cs=0;cs<data.Sections.length;cs++)
      {
        l=0;
        // If charts reports
        if (data.Sections[cs].Charts !== undefined)
          for(l=0;l<data.Sections[cs].Charts.length;l++)
          {
            reports_load_charts(o, data.Sections[cs].Charts[l], l, cs);
          }
        // If metrics reports
        if (data.Sections[cs].Metrics !== undefined)
          for (k=0;k<data.Sections[cs].Metrics.length;k++)
          {
            reports_load_metrics(o, data.Sections[cs].Metrics[k], l++, cs);
          }
      }
    });
}

function reports_load_charts(o, chart, count, sectioncount)
{
  reports_charts_plot(services_get_direct_json_link("R_GET_REPORT_CHART",[chart.metric_id]), 'section '+ sectioncount+ 'charts_'+count, count);
}

function reports_load_metrics(o, metric, count, sectioncount)
{
  services_osvcgetrest("R_GET_REPORT_METRIC", [metric.metric_id], {"meta": "false", "limit": "0"}, function(jd) {
      var d = jd.data;

      var objname = [];
      var th = "";

      for (var key in d[0]) {
        th += "<th>" + key + "</th>";
        objname.push(key); 
      }
      $("#section_" + sectioncount).find("#metrics_"+count).append(th);

      for (j=0;j<d.length;j++)
      {
        if (d[j][objname[1]] != null)
        {
          var tr = "<tr><td>";
          tr += d[j][objname[0]] +"</td>";
          tr += "<td>"+ d[j][objname[1]];
          tr += "</td></tr>";
          $("#section_" + sectioncount).find("#metrics_"+count).append(tr);
        }
      }

       $("#section_" + sectioncount).find("#spinner_"+count).remove();

    });
}

function reports_create_report(o, data, report_id)
{
  var div = $("<div></div>");
  var div_report = $("<div id='report'></div>");
  div.append(div_report);
  div_report.append("<div style='text-align:center'><span><h1><span class='clickable link16'></span>" + data.Title + "</h1></span></div>");

  for(cs=0;cs<data.Sections.length;cs++)
  {
    div_report.append(o.create_section(data.Sections[cs],cs));
  } 
  o.div_reports_data.append(div);
  o.div_reports_data.find(".link16").bind("click", function() { 
    var url = osvc_create_link("reports_single", {"report_id" : report_id });
  });
}

function reports_create_section(o, section, count)
{
  var div = $("<div></div>");
  var sect_div = $("<div id='section_" + count + "' style='clear:both'></div>");
  div.append(sect_div);
  if (section.Title !== undefined) sect_div.append("<h3 class='line yellow' style='text-align:left;padding: 0.3em''><span><span class='menu16'>" + section.Title + "</span><span></h3>");
  if (section.Desc !== undefined) sect_div.append("<div>" + section.Desc + "</div>");
  j=0;
  if (section.Charts !== undefined)
    for(j=0;j<section.Charts.length;j++)
    {
      sect_div.append(o.create_sections_chart(section.Charts[j], j));
    }

  if (section.Metrics !== undefined)
    for(i=0;i<section.Metrics.length;i++)
    {
      sect_div.append(o.create_sections_metric(section.Metrics[i], j++));
    }

  return div.html();
}

function reports_create_sections_metric(o, section, count)
{
  var div = "<div style='float:left;margin:20px;width:28%;min-width:200px;' class='reports_section'>";

  div += "<h3>" + section.Title ;
  if (section.Desc !== undefined && section.Desc != "")
  {
    div += "<br>(" + section.Desc + ")";
  }
  div += "</h3><br>";

  div += "<div id='spinner_" + count + "' class='spinner'></div>"
  div += "<table id='metrics_" + count + "' class='reports_table'>";
  div += "</table>";
  div += "</div>";
  return div;
}

function reports_create_sections_chart(o, section, count)
{
  var div = "<div style='width:94%;height:600px;max-height:600px;overflow:auto;' class='reports_section'>";

  div += "<h3>" + section.Title ;
  if (section.Desc !== undefined && section.Desc != "")
  {
    div += "<br>(" + section.Desc + ")";
  }
  div += "</h3><br>";

  div += "<div id='spinner_" + count + "' class='spinner'></div>"
  div += "<div id='charts_" + count + "'></div>";
  div += "</div>";
  return div;
}

function reports_charts_plot(url, id, count) {
    $.jqplot.config.enablePlugins = true
    $.getJSON(url, function(dd) {
        data = dd['data']
        instances = dd['instances']
        options = dd['options']
        stackSeries = options['stack']
        series = []
        unit = ""
        if (instances.length>1) {
      legend = {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{
                  numberRows: 0,
                  numberColumns: 8//instances.length/7
                },
                show: false,
                placement: "outside",
                location: 's',
                fontSize : '1',
                rowSpacing : '0.1em'
            }
  } else {
      legend = {
    show: false
      }
  }
        for (i=0; i<instances.length; i++) {
            serie = {
              'label': instances[i]['label'],
              'shadow': instances[i]['shadow'],
              'fill': instances[i]['fill']
            }
      series.push(serie)
            unit = instances[i]['unit']
  }
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max, unit)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
  p = $.jqplot(id, data, {
      stackSeries: stackSeries,
            cursor:{zoom:true, showTooltip:false},
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
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

  });
        $("#spinner_"+count).remove();
        _jqplot_extra($('#'+id), p);
    });
}