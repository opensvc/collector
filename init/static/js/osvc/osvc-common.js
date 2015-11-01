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
}

function spinner_add(e, text)
{
    if (e.children(".spinner").length > 0) {
        return
    }
    if (!text) {
        text = ""
    }
    s = $("<span class='spinner'><span>")
    s.text(text)
    e.append(s)
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


