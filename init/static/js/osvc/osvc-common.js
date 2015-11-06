// OpenSvc Common JS function
// MD 08062015

function is_enter(e) {
  var characterCode = -1;
  if (e && e.which) {
    e = e
    characterCode = e.which
  } else if (e && e.keyCode) {
    characterCode = e.keyCode
  }
  if (characterCode == 13) {
    return true
  }
  return false
}

function is_blank(str) {
    return (!str || /^\s*$/.test(str));
}

function is_empty_or_null(str) {
  if (str=='' || str=="null" || str==null)
    return false;
  else
    return true;
}

function toggle(divid, head)
{
  if (head) {
    e = $("#"+head).find("#"+divid);
  } else {
    e = $('#'+divid);
  }
  e.slideToggle();
}

function mul_toggle(divid,divid2, head)
{
  if (head) {
    e1 = $("#"+head).find("#"+divid);
    e2 = $("#"+head).find("#"+divid2);
  } else {
    e1 = $('#'+divid);
    e2 = $('#'+divid2);
  }
  e1.slideToggle(200, function() {
    e2.slideToggle(200);
  });
}

function float2int (value) {
    return value | 0;
}

function spinner_del(e, text)
{
    e.children(".spinner").remove()
    e.children(".spinner_text").remove()
}

function spinner_add(e, text)
{
    if (e.children(".spinner").length > 0) {
        return
    }
    if (!text) {
        text = ""
    }
    var s = $("<span class='spinner fa-spin'><span>")
    e.append(s)
    var t = $("<span style='margin-left:1em' class='spinner_text'><span>")
    t.text(text)
    e.append(t)
    if (!e.is(":visible")) {
        e.slideToggle()
    }
}

function print_date(d) {
  var day = d.getDate()
  var month = d.getMonth()+1
  var year = d.getFullYear()
  var hours = d.getHours()
  var minutes = d.getMinutes()
  if (month<10) { month = "0"+month }
  if (day<10) { day = "0"+day }
  if (hours<10) { hours = "0"+hours }
  if (minutes<10) { minutes = "0"+minutes }
  var ds = year+"-"+month+"-"+day+" "+hours+":"+minutes
  return ds
}

String.prototype.beginsWith = function (string) {
    return(this.indexOf(string) === 0);
};

function str_from_datetime(date)
{
  var d = (date+'').split(' ');
  return [d[3], d[1], d[2], d[4]].join(' ');
}

function js_utc_date_from_str(str_date)
{
  return new Date(str_date.replace(" ","T")+"Z");
}

function diff_date(d1,d2)
{
  var date1 = new Date(d1);
  var date2 = new Date(d2);
  var timeDiff = Math.abs(date2.getTime() - date1.getTime());
  var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
  return diffDays;
}

function link(divid, options)
{
    var link_id = options.link_id;
    $("#"+divid).load("/init/" + link_id, options, function() {
    });   
}

function osvc_create_link(fn, parameters, target)
{
  if (!target) {
    target = $(".flash")
  }
  if (!parameters) {
    parameters = {}
  }

  // Security for old link
  fn = fn.replace("?","");

  var link_id =  services_osvcpostrest("R_POST_LINK", "", "", {"fn": fn, "param": JSON.stringify(parameters)}, function(jd) {
      if (jd.error) {
        target.html(services_error_fmt(jd))
        return
      }
      var link_id = jd.link_id;
      var url = $(location).attr("origin");

      url += "/init/link/link?link_id="+link_id;
      if (fn.beginsWith("https://")) // if is not an ajax link, but a function js call
        url +="&js=false";
      else
        url += "&js=true";

      // header
      var e = $("<div></div>")

      var title = $("<div class='attach16 fa-2x' data-i18n='api.link'></div>")
      e.append(title)

      var subtitle = $("<div style='color:lightgray' data-i18n='api.link_text'></div>")
      e.append(subtitle)

      // link display area
      p = $("<textarea style='width:100%' class='clickable'></textarea>")
      p.val(url)
      p.css({
        "width": "100%",
        "background": "rgba(0,0,0,0)",
        "border": "rgba(0,0,0,0)",
        "padding": "2em 0 0 0",
      })
      p.select()
      p.bind("click", function() {
        send_link($(this).val())
      })

      e.i18n()
      e.append(p)

      target.empty().append(e);
      p.autogrow();

      osvc_show_link(url, target)
    },
    function(xhr, stat, error) {
      $(".flash").show("fold").html(services_ajax_error_fmt(xhr, stat, error))
    })
}

function osvc_show_link(url, target) {
  if (!target) {
    target = $(".flash")
  }
  // header
  var e = $("<div></div>")

  var title = $("<div class='attach16 fa-2x' data-i18n='api.link'></div>")
  e.append(title)

  var subtitle = $("<div style='color:lightgray' data-i18n='api.link_text'></div>")
  e.append(subtitle)

  // link display area
  p = $("<textarea style='width:100%' class='clickable'></textarea>")
  p.val(url)
  p.css({
    "width": "100%",
    "background": "rgba(0,0,0,0)",
    "border": "rgba(0,0,0,0)",
    "padding": "2em 0 0 0",
  })
  p.bind("click", function() {
    send_link($(this).val())
  })

  e.i18n()
  e.append(p)

  target.empty().append(e).show("fold")
  p.autogrow();
  p.select()
}

function osvc_get_link(divid,link_id)
{
  services_osvcgetrest("R_GET_LINK",[link_id] , "", function(jd) {
      if (jd.data.length === 0) { // Link not found
        var val = "<div style='text-align:center'>" + i18n.t("link.notfound")+"</div>"
        $('#'+divid).html(val);
        return;
      }
      var result = jd.data;

      var param = JSON.parse(result[0].link_parameters);
      var link = result[0].link_function;

      // if ajax link
      if (link.beginsWith("https://"))
      {
        $("#"+divid).load(link, param, function() {});   
      }
      else // or js function link
      {
        var fn = window[link];
        fn(divid,param);
      }
  });
}
