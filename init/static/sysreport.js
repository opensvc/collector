function sysreport_timeline(id, data){
  var options = {
    template: function (item) {
      return '<pre style="text-align:left">' + item.stat + '</pre>';
    },
    clickToUse: true
  };
  var container = document.getElementById(id);
  var groups = []
  var groupids = []
  for (i=0; i<data.length; i++) {
    if (groupids.indexOf(data[i]['group']) >= 0) {
       continue
    }
    groupids.push(data[i]['group'])
    groups.push({
      'id': data[i]['group']
    })
  }
  if (groupids.length == 1) {
     groups = null
  }
  var timeline = new vis.Timeline(container, data, groups, options);
  timeline.on('select', function (properties) {
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_commit"
    var item_id = properties.items[0]
    var item = null;
    for (i=0; i<data.length; i++) {
      if (data[i]['id'] == item_id) {
        item = data[i]
        break
      }
    }
    _data = {
     'cid': item.cid,
     'nodename': item.group
    }
    $.ajax({
         type: "POST",
         url: url,
         data: _data,
         success: function(msg){
           $("#"+id+"_show").html(msg)
           $("#"+id+"_show").find(".diff").each(function(i, block){
             hljs.highlightBlock(block);
           })
           $("#"+id+"_show").find("[name=tree]").children("h2").bind('click', function(){
             next = $(this).next()
             if (next.is("pre")) {
               next.remove()
             } else {
               sysreport_show_file($(this))
             }
           })
         }
    })
  });

  // bind admin tool
  $("#"+id).siblings(".lock").bind("click", function(){
    var e = $(this).siblings("#"+id+"_admin")
    if (e.is(":visible")) {
      e.hide()
    } else {
      e.show()
      var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin"
      sync_ajax(url, [], id+"_admin", function(){})
    }
  })
}

function sysreport_show_file(e) {
  var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_show_file"
  data = {
   'nodename': e.attr("nodename"),
   'fpath': e.attr("fpath"),
   'oid': e.attr("oid"),
   'cid': e.attr("cid")
  }
  $.ajax({
       type: "POST",
       url: url,
       data: data,
       success: function(msg){
         s = "<pre style='padding:1em'>"+msg+"</pre>"
         $(s).insertAfter(e)
         hljs.highlightBlock(e.next("pre"));
       }
  })
}

function sysreport_admin_secure(tid) {
  $("#"+tid).find("[sec_id]").bind("mouseover", function(){
    $(this).find(".nologo16").addClass("del16").addClass("clickable")
  }).bind("mouseout", function(){
    $(this).find(".nologo16").removeClass("del16").removeClass("clickable")
  })
  $("#"+tid).find(".meta_del").bind("click", function(){
    var sec_id = $(this).parent().attr("sec_id")
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_del_secure"
    url += "?sec_id="+sec_id
    sync_ajax(url, [], "", function(){$("[sec_id="+sec_id+"]").remove()})
  })
  $("#"+tid).find(".meta_add").find("input").bind("keyup", function(){
    if (!is_enter(event)) {
      return
    }
    var pattern = $(this).val()
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_add_secure"
    url += "?pattern="+encodeURIComponent(pattern)
    sync_ajax(url, [], "", function(){$(".lock").click().click()})
  })
}

