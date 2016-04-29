//MD 27082015
// Wiki function

function alert_event(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid
    o.div = $("#"+divid);
    o.div.html("<span class='icon spinner'><span>");
    o.begin_date = options.begin_date.replace(" ","T")+"Z"; // corrected timestamp to UC;
    o.node_id = options.node_id;
    o.svc_id =  options.svc_id;
    o.md5name = options.md5name;

    o.alert_event_load = function()
    {
    	return alert_event_load(o);
    }
    alert_event_init(o);  
}

function alert_event_init(o)
{
 	o.alert_event_load();
}

function alert_event_d3_timeline(o,result)
{ 
  var data = [{label : "", times : []}];

  var first ={};
  if (result.length == 0)
  {
    var sdate = new Date(o.begin_date);
    var edate = new Date();
    desc = str_from_datetime(sdate) + " " + i18n.t("alert_event.tonow");
    first = {"color":"red", "desc": desc,"label" : diff_date(sdate,edate)+ " " + i18n.t("alert_event.days"),"starting_time": sdate, "ending_time": edate};
    data[0].times.push(first);
  }

  for (i=0;i<result.length;i++) // Build timeline from Rest Result
  {
    var begin_date = js_utc_date_from_str(result[i].dash_begin);
    var end_date;
    var end_date_title ="";
    if (result[i].dash_end != null)
    {
      end_date = js_utc_date_from_str(result[i].dash_end);
      end_date_title = str_from_datetime(end_date);
    }
    else
    {
      if (i < result.length-1)
      {
        end_date = js_utc_date_from_str(result[(i)+1].dash_begin);
        end_date_title= str_from_datetime(end_date);
      }
      else
      {
        end_date = new Date();
        end_date_title = i18n.t("alert_event.now");
      }
    }
    var color = "#FF2020";
    if (i%2==0) color = "#FF6060";
    begin_date = new Date(begin_date);

    desc = str_from_datetime(begin_date) + " " + i18n.t("alert_event.to") + " " + end_date_title;

    data[0].times.push({"color": color,"label" : diff_date(begin_date,end_date) + " " + i18n.t("alert_event.days"), "desc": desc,"starting_time": begin_date, "ending_time": end_date});
  }


  o.div.empty();
  o.div.append("<div id='detail_label'> <span id='details' style='color:#FF0000'><i>"+ i18n.t("alert_event.help")+"</i></span></div>")

  var chart = d3.timeline();

  var tf = {
    format: d3.time.format("%m-%y"),
    tickTime: d3.time.months,
    tickInterval: 1,
    tickSize: 3,
  }

  chart.tickFormat(tf);

  chart.mouseover(function (d, i, datum) {
      $("#details").html(i18n.t("alert_event.label") + " " + datum.times[i].desc);
      $("#detail_label").show();
    });

  chart.rotateTicks(45);
  var container = $("#"+o.divid)[0];
  var svg = d3.select("#"+o.divid).append("svg").attr("width", "800")
    .datum(data).call(chart);
  }

function alert_event_load(o)
{
    services_osvcgetrest("R_ALERT_EVENT", "", {"md5name": o.md5name,"svc_id" : o.svc_id,"node_id" : o.node_id}, function(jd) {
      if (jd.data === undefined) {
        return;
      }
      var result=jd.data;
      alert_event_d3_timeline(o,result);
    });
}
