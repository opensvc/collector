function reports(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  
  o.init = function init() {
    return reports_init(o)
  }

  o.create_report = function create_report(data, count) {
    return reports_create_report(o, data, count);
  }

  o.create_sections = function create_sections(section, count)
  {
    return reports_create_sections(o, section, count);
  }

  o.refresh = function refresh() {
    return reports_refresh(o);
  }
  
  o.div.load("/init/static/views/reports.html", function() {
    o.div_reports_header = o.div.find("#reports_header");
    o.div_reports_data = o.div.find("#reports_data");
    o.ql_link = o.div.find("#reports_ql_link");
    o.reports_select = o.div_reports_header.find("#reports_select");

    o.init()
  })

  return o;
}


function reports_init(o)
{
  //var timer;

  o.ql_link.bind("click", function() { 
    var url = osvc_create_link("reports", "");
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
      if (data.length >0) reports_load_selected(o,data[0].id);
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
      for (k=0;k<data.Sections[0].Metrics.length;k++)
      {
        reports_load_metrics(o, data.Sections[0].Metrics[k], k);
      }
    });
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
  var div = "<div id='report' class='reports_div'>";
  div += "<div style='text-align:center'><h1>" + data.Title + "</h1></div>";
  
  for(i=0;i<data.Sections[0].Metrics.length;i++)
  {
    div += o.create_sections(data.Sections[0].Metrics[i], i);
  }

  div += "</div>";    
  o.div_reports_data.append(div);
}

function reports_create_sections(o, section, count)
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