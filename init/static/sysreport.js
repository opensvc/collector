function sysreport_timeline(id, nodename, data){
  var options = {
    template: function (item) {
      return '<pre style="text-align:left">' + item.stat + '</pre>';
    },
    clickToUse: true
  };
  var container = document.getElementById(id);
  var timeline = new vis.Timeline(container, data, options);
  timeline.on('select', function (properties) {
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_commit"
    data = {
     'id': properties.items[0],
     'nodename': nodename
    }
    $.ajax({
         type: "POST",
         url: url,
         data: data,
         success: function(msg){
           $("#"+id+"_show").html(msg)
           $("#"+id+"_show").find("pre code").each(function(i, block){
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
