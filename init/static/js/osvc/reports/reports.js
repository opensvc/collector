function reports(divid, options) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  
  o.init = function init(options) {
    return reports_init(o, options)
  }

  o.create_report = function create_report(data, count) {
    return reports_create_report(o, data, count);
  }

  o.create_sections_metric = function create_sections_metric(section, count)
  {
    return reports_create_sections_metric(o, section, count);
  }

  o.create_sections_chart = function create_sections_chart(section, count)
  {
    return reports_create_sections_chart(o, section, count);
  }

  o.refresh = function refresh() {
    return reports_refresh(o);
  }
  
  o.div.load("/init/static/views/reports.html", function() {
    o.div_reports_header = o.div.find("#reports_header");
    o.div_reports_data = o.div.find("#reports_data");
    o.ql_link = o.div.find("#reports_ql_link");
    o.reports_select = o.div_reports_header.find("#reports_select");
    o.init(options)
  })

  return o;
}


function reports_init(o, options)
{
  //var timer;

  o.ql_link.bind("click", function() { 
    var url = osvc_create_link("reports", {"report_id" : o.reports_select.val() });
  });

  o.reports_select.bind("change", function()
  {
    o.refresh();
  });

  // Init Select Report
  services_osvcgetrest("R_GET_REPORTS", "", {"meta": "false", "limit": "0"}, function(jd) {
      var data = jd.data;
      for (var i=0;i<data.length;i++)
      {
        var option = $('<option />');
        option.attr('value', data[i].id).text(data[i].report_name);
        o.reports_select.append(option);
      }
      if (data.length >0) 
      {
        if (options !== undefined)
        {
          o.reports_select.val(options.report_id);
          // Coming from link, supress parent text-align
          $(document).find("#link").removeAttr("style");
        }

        reports_load_selected(o,o.reports_select.val());
      }
  });
}

function reports_refresh(o)
{
  o.div_reports_data.empty();
  // Reload data
  reports_load_selected(o,o.reports_select.val());
}

function reports_load_selected(o, report_id)
{
  services_osvcgetrest("R_GET_REPORT", [report_id], {"meta": "false", "limit": "0"}, function(jd) {
      var data = jd.data;
      o.create_report(jd.data);
      l=0;
      // If charts reports
      if (data.Sections[0].Charts !== undefined)
        for(l=0;l<data.Sections[0].Charts.length;l++)
        {
          reports_load_charts(o, data.Sections[0].Charts[l], l);
        }
      // If metrics reports
      if (data.Sections[0].Metrics !== undefined)
        for (k=0;k<data.Sections[0].Metrics.length;k++)
        {
          reports_load_metrics(o, data.Sections[0].Metrics[k], l++);
        }
    });
}

function reports_load_charts(o, chart, count)
{
  reports_charts_plot(services_get_direct_json_link("R_GET_REPORT_CHART",[chart.metric_id]), 'charts_'+count, count);
}

function reports_load_metrics(o, metric, count)
{
  services_osvcgetrest("R_GET_REPORT_METRIC", [metric.metric_id], {"meta": "false", "limit": "0"}, function(jd) {
      var d = jd.data;

      var objname = [];
      var th = "";

      for (var key in d[0]) {
        th += "<th>" + key + "</th>";
        objname.push(key); 
      }
      $("#metrics_"+count).append(th);

      for (j=0;j<d.length;j++)
      {
        var tr = "<tr><td>";
        tr += d[j][objname[0]] +"</td>";
        tr += "<td>"+ d[j][objname[1]];
        tr += "</td></tr>";
        $("#metrics_"+count).append(tr);
      }

      $("#spinner_"+count).remove();

    });
}

function reports_create_report(o, data)
{
  var global = 0;


  var div = "<div id='report' class='reports_div'>";
  div += "<div style='text-align:center'><h1>" + data.Title + "</h1></div>";
  j=0;
  if (data.Sections[0].Charts !== undefined)
    for(j=0;j<data.Sections[0].Charts.length;j++)
    {
      div += o.create_sections_chart(data.Sections[0].Charts[j], j);
    }

  if (data.Sections[0].Metrics !== undefined)
    for(i=0;i<data.Sections[0].Metrics.length;i++)
    {
      div += o.create_sections_metric(data.Sections[0].Metrics[i], j++);
    }

  div += "</div>";    

  o.div_reports_data.append(div);
}

function reports_create_sections_metric(o, section, count)
{
  var div = "<div style='float:left;margin:20px;width:28%' class='reports_section'>";

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
  var div = "<div style='width:95%;height:600px;max-height:600px;overflow:auto;' class='reports_section'>";

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
                show: true,
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