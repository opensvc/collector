// OpenSvc Common JS function
// MD 08062015

function is_enter(e) {
  var characterCode
  if(e && e.which) {
    e = e
    characterCode = e.which
  }else{
    characterCode = e.keyCode
  }
  if(characterCode == 13) {
    return true
  }else{
    return false
  }
}

function is_blank(str) {
    return (!str || /^\s*$/.test(str));
}

function toggle(divid)
{
  $('#'+divid).slideToggle();
}

function mul_toggle(divid,divid2)
{
  $('#'+divid).slideToggle(200, function() {
    $('#'+divid2).slideToggle(200);
  });
}

function float2int (value) {
    return value | 0;
}