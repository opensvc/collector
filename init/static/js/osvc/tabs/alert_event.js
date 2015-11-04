//MD 27082015
// Wiki function

function alert_event(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid
    o.div = $("#"+divid);
    o.div.html("<span class='spinner'><span>");
    o.nodes = options.nodes;
    o.begin_date = options.begin_date.replace(" ","T")+"Z"; // corrected timestamp to UC;
    o.svcname =  options.svcname;
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

function d3_test(o,result)
{ 
var data = [{label : "", times : []}];

var first ={};
   if (result.length == 0)
   {
      var sdate = new Date(o.begin_date);
      var edate = new Date();
      var d = (sdate+'').split(' ');
      desc = [d[3], d[1], d[2], d[4]].join(' ') + " to now";
      first = {"color":"red", "desc": desc,"label" : alert_event_diff_date(sdate,edate),"starting_time": sdate, "ending_time": edate};
      data[0].times.push(first);
   }

   for (i=0;i<result.length;i++)
   {
    var begin_date = result[i].dash_begin.replace(" ","T")+"Z";
    var end_date;
    var end_date_title ="";
    if (result[i].dash_end != null)
    {
      end_date = new Date(result[i].dash_end.replace(" ","T")+"Z");
      var d = (end_date+'').split(' ');
      end_date_title = [d[3], d[1], d[2], d[4]].join(' ') ;
    }
    else
    {
      if (i < result.length-1)
      {
        end_date = new Date(result[(i)+1].dash_begin.replace(" ","T")+"Z");
        var d = (end_date+'').split(' ');
        end_date_title= [d[3], d[1], d[2], d[4]].join(' ') ;
      }
      else
      {
        end_date = new Date();
        end_date_title = "now";
      }
    }
    var color = "#FF2020";
    if (i%2==0) color = "#FF6060";
    begin_date = new Date(begin_date);

    var d = (begin_date+'').split(' ');
    desc = [d[3], d[1], d[2], d[4]].join(' ') + " to " + end_date_title;

    data[0].times.push({"color": color,"label" : alert_event_diff_date(begin_date,end_date), "desc": desc,"starting_time": begin_date, "ending_time": end_date});
  }


  o.div.empty();
   o.div.append("<div id='detail_label' class='hidden'> Alert from <span id='details' style='color:#FF0000'></span></div>")


var chart = d3.timeline();

var tf = {
  format: d3.time.format("%m-%y"),
  tickTime: d3.time.months,
  tickInterval: 1,
  tickSize: 3,
}

chart.tickFormat(tf);

chart.mouseover(function (d, i, datum) {
    $("#details").html(datum.times[i].desc);
    $("#detail_label").show();
  });

chart.rotateTicks(45);
var container = $("#"+o.divid)[0];
var svg = d3.select("#"+o.divid).append("svg").attr("width", "800")
  .datum(data).call(chart);
}

function alert_event_diff_date(d1,d2)
{
  var date1 = new Date(d1);
  var date2 = new Date(d2);
  var timeDiff = Math.abs(date2.getTime() - date1.getTime());
  var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
  return diffDays + " days";
}

function alert_event_build_timeline(o, result)
{
   var items = new vis.DataSet({
    type: { start: 'ISODate', end: 'ISODate' }
  });

   var first ={};
   if (result.length == 0)
   {
    var days = (alert_event_diff_date(o.begin_date,new Date())).toString() + " days";
      first =
      [{
        id : 100,
        content : days,
        start : o.begin_date,
        end: new Date(),
        className : 'red',
        group : 'Alert',
        title : o.begin_date + ' to now',
        type : "range",
      },]
      items.add(first);
   }

   for (i=0;i<result.length;i++)
   {
    var begin_date = result[i].dash_begin.replace(" ","T")+"Z";
    var end_date;
    var end_date_title ="";
    if (result[i].dash_end != null)
    {
      end_date = result[i].dash_end.replace(" ","T")+"Z";;
      end_date_title = end_date;
    }
    else
    {
      if (i < result.length-1)
      {
        end_date = result[(i)+1].dash_begin;
        end_date_title=end_date;
      }
      else
      {
        end_date = new Date();
        end_date_title = "now";
      }
    }

    var classe = 'red';

    var days = (alert_event_diff_date(begin_date,end_date)).toString() + " days";

    items.add([
      {
        id : i,
        content : days,
        start : begin_date,
        end : end_date,
        className : classe,
        group : 'Alert',
        title : begin_date + ' to ' + end_date_title,
        type : "range",
      },
    ]);
   }

   var groups = [];
   groups.push(
   {
    'id' : 'Alert',
   });

  o.div.empty();

  var container = $("#"+o.divid)[0];
  var options = {
    template: function (item) {
      return '<pre style="text-align:left">' + item.content + '</pre>';
    },
    editable: false,
    showCurrentTime: true,
    zoomable: false,
  };

  var timeline = new vis.Timeline(container, items, groups, options);

  o.div.append("<div id='detail_label' class='hidden'> Alert from <span id='details' style='color:#FF0000'></span></div>")

  timeline.on('select', function (properties) {
      var item_id = properties.items[0]
      $('#details').html(items._data[item_id].title);
      $('#detail_label').show();
  });

}

function alert_event_load(o)
{
    services_osvcgetrest("R_ALERT_EVENT", "", {"md5name": o.md5name,"svcname" : o.svcname,"nodename" : o.nodes}, function(jd) {
      if (jd.data === undefined) {
        return;
      }
      var result=jd.data;
      //alert_event_build_timeline(o,result);
      d3_test(o,result);
    });
}
