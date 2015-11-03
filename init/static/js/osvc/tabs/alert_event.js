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
    o.begin_date = options.begin_date;
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

function alert_event_build_timeline(o, result)
{
   var items = new vis.DataSet({
    type: { start: 'ISODate', end: 'ISODate' }
  });

   var first ={};
   if (result.length == 0)
   {
      first =
      {
        id : 100,
        start : o.begin_date,
        end: new Date(),
        className : 'red',
        group : 'Alert',
        title : o.begin_date + ' to now',
        type : "range",
      }
   }

   for (i=0;i<result.length;i++)
   {
    var begin_date = result[i].dash_begin;
    var end_date;
    var end_date_title ="";
    if (result[i].dash_end != null)
    {
      end_date = result[i].dash_end;
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

    items.add([
      {
        id : i,
        //value : i.toString(),
        start : begin_date,
        end : end_date,
        className : classe,
        group : 'Alert',
        title : begin_date + ' to ' + end_date_title,
        type : "range",
      },
    ]);
   }

   items.add(first);

   var groups = [];
   groups.push(
   {
    'id' : 'Alert',
   });

  o.div.empty();

  var container = $("#"+o.divid)[0];
  var options = {
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
      alert_event_build_timeline(o,result);
    });
}
