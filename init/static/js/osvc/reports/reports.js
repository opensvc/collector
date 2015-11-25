function reports_single(divid,options)
{
    if (options !== undefined)
    {
      if (options.report_id !== undefined && (options.metric_id === undefined && options.chart_id === undefined))
        {
          o = reports_init(divid, options , function ()
          {
            reports_load_selected(o,options.report_id);
          });
        }
      else if (options.metric_id !== undefined || options.chart_id !== undefined)
      {
        o = reports_init(divid, options , function ()
        {
          reports_load_selected_sub(o,options);
        });
      }
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

  o.create_sections_metric = function create_sections_metric(section, count, sectioncount)
  {
    return reports_create_sections_metric(o, section, count, sectioncount);
  }

  o.create_sections_chart = function create_sections_chart(section, count, sectioncount)
  {
    return reports_create_sections_chart(o, section, count, sectioncount);
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
    if (callback !== undefined) callback();
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
      o.report_id = report_id; // Current selected report
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

function reports_load_selected_sub(o, options)
{
  services_osvcgetrest("R_GET_REPORT", [options.report_id], {"meta": "false", "limit": "0"}, function(jd) {
    var data = jd.data;
    
    o.report_id = options.report_id; // Current selected report
    for(cs=0;cs<data.Sections.length;cs++)
    {
      if (data.Sections[cs].Metrics !== undefined)
        for(i=0;i<data.Sections[cs].Metrics.length;i++)
        {
          if (options.metric_id == data.Sections[cs].Metrics[i].metric_id)
          {
            var div = $("<div></div>");
            var sect_div = $("<div id='section_0' style='clear:both;'></div>");
            div.append(sect_div);
            var met_div=o.create_sections_metric(data.Sections[cs].Metrics[i], 0,0);
            div.append(met_div);
            o.div_reports_data.append(div);
            o.div_reports_data.find(".reports_section").removeAttr("style");
            reports_load_metrics(o,data.Sections[cs].Metrics[i],0,0);
          }
        }
        else if (data.Sections[cs].Charts !== undefined)
        for(i=0;i<data.Sections[cs].Charts.length;i++)
        {
          if (options.chart_id == data.Sections[cs].Charts[i].metric_id)
          {
            var div = $("<div></div>");
            var sect_div = $("<div id='section_0' style='clear:both'></div>");
            div.append(sect_div);
            var met_div=o.create_sections_chart(data.Sections[cs].Charts[i], 0,0);
            div.append(met_div);
            o.div_reports_data.append(div);
            reports_load_charts(o,data.Sections[cs].Charts[i],0,0);
          }
        }
    }
    });
    /*
    if (options.metric_id != undefined)
    {
      
      var div = $("<div></div>");
      var sect_div = $("<div id='section_0' style='clear:both'></div>");
      div.append(sect_div);
      var met_div=o.create_sections_metric(sample, 0);
      div.append(met_div);
      div_reports_data.append(div);
      reports_load_metrics(sample,0,0);
    }*/
}

function reports_load_charts(o, chart, count, sectioncount)
{
  reports_charts_plot(services_get_direct_json_link("R_GET_REPORT_CHART",[chart.metric_id]), "", sectioncount, count);
  // Activate link
  $("#link_"+ sectioncount + "_" + count).bind("click", function() {  
    var url = osvc_create_link("reports_single", 
      {"chart_id" : chart.metric_id, "report_id" : o.report_id});
  });
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
      $("#metrics_"+ sectioncount + "_" +count).append(th);

      for (j=0;j<d.length;j++)
      {
        if (d[j][objname[1]] != null)
        {
          var tr = "<tr><td>";
          tr += d[j][objname[0]] +"</td>";
          tr += "<td>"+ d[j][objname[1]];
          tr += "</td></tr>";
          $("#metrics_"+ sectioncount + "_" +count).append(tr);
        }
      }

      $("#spinner_"+ sectioncount + "_" +count).remove();

      // Activate link
      $("#link_"+ sectioncount + "_" + count).bind("click", function() { 
        var url = osvc_create_link("reports_single", 
          {"metric_id" : metric.metric_id, "report_id" : o.report_id});
      });

    });
}

function reports_create_report(o, data, report_id)
{
  var div = $("<div></div>");
  var div_report = $("<div id='report'></div>");
  div.append(div_report);
  div_report.append("<div style='text-align:center'><span><h1><span id='report_title' class='clickable link16'></span>" + data.Title + "</h1></span></div>");

  for(cs=0;cs<data.Sections.length;cs++)
  {
    div_report.append(o.create_section(data.Sections[cs],cs));
  } 
  o.div_reports_data.append(div);

  div_report.find("#report_title").bind("click", function() { 
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
      sect_div.append(o.create_sections_chart(section.Charts[j], j, count));
    }

  if (section.Metrics !== undefined)
    for(i=0;i<section.Metrics.length;i++)
    {
      sect_div.append(o.create_sections_metric(section.Metrics[i], j++, count));
    }

  return div.html();
}

function reports_create_sections_metric(o, section, count, sectioncount)
{
  var link_id = "link_"+ sectioncount + "_" + count;
  var div = "<div style='float:left;width:28%;min-width:200px;' class='reports_section'>";

  div += "<h3><span id='"+ link_id +"' class='clickable link16'></span>" + section.Title ;
  if (section.Desc !== undefined && section.Desc != "")
  {
    div += "<br>(" + section.Desc + ")";
  }
  div += "</h3><br>";

  div += "<div id='spinner_" + sectioncount + "_" + count + "' class='spinner'></div>"
  div += "<table id='metrics_" + sectioncount + "_" + count + "' class='reports_table'>";
  div += "</table>";
  div += "</div>";
  return div;
}

function reports_create_sections_chart(o, section, count, sectioncount)
{
  var link_id = "link_"+ sectioncount + "_" + count;
  var div = "<div style='width:94%;height:600px;overflow-y:auto' class='reports_section'>";

  div += "<h3><span id='"+ link_id +"' class='clickable link16'></span>" + section.Title ;
  if (section.Desc !== undefined && section.Desc != "")
  {
    div += "<br>(" + section.Desc + ")";
  }
  div += "</h3><br>";

  div += "<div id='spinner_" + sectioncount + "_" + count + "' class='spinner'></div>"
  div += "<div id='charts_" + sectioncount + "_" + count + "'></div>";
  div += "</div>";
  return div;
}

function reports_charts_plot(url, id, section, count) {
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
                  numberColumns: 10//instances.length/10
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

  id = "charts_" + section + "_"+count;

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
        $("#section_" + section).find("#spinner_"+count).remove();
        _jqplot_extra($('#'+id), p);
    });
}