function designer(divid, options) {
  var o = {}
  o.divid = divid
  o.div = $('#'+divid)
  if (!options) {
    options = {}
  }
  o.options = options

  o.url_images = services_get_url() + "/init/static/images",
  o.url_action = services_get_url() + "/init/compliance/call/json/json_tree_action",
  o.url = services_get_url() + "/init/compliance/call/json/json_tree",

  o.init = function() {
    return designer_init(o)
  }
  o.show_variable = function(e) {
    return designer_show_variable(o, e)
  }
  o.show_importer = function() {
    return designer_show_importer(o)
  }
  o.json_data_url = function(t) {
    return designer_json_data_url(o, t)
  }
  o.resizer = function(t) {
    return designer_resizer(o)
  }
  o.monitor_doc_height = function(t) {
    return designer_monitor_doc_height(o)
  }
  o.comp_import = function(t) {
    return designer_comp_import(o)
  }
  o.link = function(t) {
    return designer_link(o)
  }
  o.set_stats = function(value, label, node) {
    return designer_set_stats(o, value, label, node)
  }
  o.set_log_op_entry = function(label, obj_type, node) {
    return designer_set_log_op_entry(o, label, obj_type, node)
  }
  o.__rename = function(e, data) {
    return designer__rename(o, e, data)
  }
  o.__move = function(e, data) {
    return designer__move(o, e, data)
  }
  o.__remove = function(e, data) {
    return designer__remove(o, e, data)
  }
  o.__create = function(e, data) {
    return designer__create(o, e, data)
  }
  o.__select = function(e, data) {
    return designer__select(o, e, data)
  }

  o.div.load('/init/static/views/designer.html', "", function() {
    o.init()
  })
  return o
}

function designer_resizer(o){
  if (!o.e_search_input || !o.e_close) {
    // we were triggered by an event but not fully initialized
    return
  }
  var i_height = o.e_search_input.outerHeight()
  var t_height = o.e_close.outerHeight()
  var height = $(window).height()-$(".header").outerHeight()-$(".footer").outerHeight()
  var l_width = 0
  o.div.find(".catree:visible,#casep").each(function(){
    l_width += $(this).outerWidth(true)
  })
  o.div.height(height)

  // occupy all vertical space
  o.e_tree.outerHeight(height - i_height)
  o.e_tree2.outerHeight(height - i_height)
  o.e_sep.outerHeight(height)
  o.e_info.outerHeight(height - t_height)

  // make the info panel occupy the whole right-most space
  o.e_info.outerWidth(o.div.innerWidth() - l_width - 1)
}

function designer_link(o){
  var url = get_view_url()
  var re = /#$/;
  url = url.replace(re, "");
  args = "obj_filter="+encodeURIComponent($("#casearch").val())
  args += "&obj_filter2="+encodeURIComponent($("#casearch2").val())
  osvc_create_link(url, args);
}

function designer_set_stats(o, value, label, node) {
  return {
    "label": label,
    "action": function(obj){
      $.ajax({
        async: false,
        type: "POST",
        url: o.url_action,
        data: {
         "operation": "set_stats",
         "value": value,
         "obj_id": obj.attr("obj_id")
        },
        success: function(msg){
          designer_json_status(msg)
        }
      });
    }
  }
}

function designer_set_log_op_entry(o, label, obj_type, node) {
  return {
    "label": label,
    "action": function(obj){
      $.ajax({
        async: false,
        type: "POST",
        url: o.url_action,
        data: {
         "operation": "set_log_op",
         "type": label,
         "obj_type": obj_type,
         "obj_id": obj.attr("obj_id"),
         "parent_obj_id": node.parents("li").attr("obj_id")
        },
        success: function(msg){
          $("[name=catree]:visible").jstree("refresh");
          designer_json_status(msg)
        }
      });
    }
  }
}

function designer_json_status(msg){
  if (msg == 0 || msg == "0") {
    $(".flash").html("")
    return
  }
  if ("err" in msg) {
    s = msg["err"]
  } else if ("error" in msg) {
    s = msg["error"]
  } else {
    s = ""
  }
  $(".flash").html(s).slideDown()
}

function designer_json_data_url(o, tree) {
   return function() {
     if (tree==2) {
       var search = o.e_search_input2
       var osearch = o.options.search2
     } else {
       var search = o.e_search_input
       var osearch = o.options.search
     }
     var val = search.val()
     if ((!val || (val == "")) && osearch) {
       val = osearch
       search.val(val)
     }
     if (!val || (val == "")) {
       val = "opensvc"
       search.val(val)
     }
     var url = o.url+"?obj_filter="+encodeURIComponent(val)
     return url
   }
}

function designer__rename(o, e, data) {
  data.rslt.obj.each(function() {
    var rel = $(this).attr('rel')
    var obj_id = $(this).attr('obj_id')
    var new_name = data.rslt.new_name
    $.ajax({
      async: false,
      type: "POST",
      url: o.url_action,
      data: {
       "operation": "rename",
       "obj_type": rel,
       "obj_id": obj_id,
       "new_name": new_name
      },
      error: function(jqXHR, exception) {
        if (jqXHR.status === 0) {
          msg = 'Connection error.'
        } else if (jqXHR.status == 404) {
          msg = 'Requested page not found. [404]'
        } else if (jqXHR.status == 500) {
          msg = 'Internal Server Error [500].'
        } else if (exception === 'parsererror') {
          msg = 'Requested JSON parse failed.'
        } else if (exception === 'timeout') {
          msg = 'Time out error.'
        } else if (exception === 'abort') {
          msg = 'Ajax request aborted.'
        } else {
          msg = 'Error: ' + jqXHR.responseText
        }
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
          designer_json_status(msg)
        }
        $("[rel="+rel+"][obj_id="+obj_id+"]").each(function(){
          $(this).parents("[name=catree]").jstree("rename_node", this, new_name)
        })
      }
    })
  })
}

function designer__move(o, e, data) {
    if (data.rslt.cy) {
        var operation = "copy"
    } else {
        var operation = "move"
    }
    var dst_id = data.rslt.np.attr("id")
    var dst_rel = data.rslt.np.attr("rel")
    var dst_obj_id = data.rslt.np.attr("obj_id")
    var dst_tree_id = data.rslt.np.parents("[name=catree]").attr("id")
    var text = data.rslt.o.text().replace(/^\s*/, "")
    var rel = data.rslt.o.attr("rel")
    var id = data.rslt.o.attr("id")
    var tree_id = data.rslt.o.parents("[name=catree]").attr("id")
    var obj_id = data.rslt.o.attr("obj_id")
    var parent_obj_id = data.rslt.op.attr("obj_id")

    if ((dst_rel==rel) && (dst_obj_id==obj_id)) {
      // copy on self is not allowed
      $.jstree.rollback(data.rlbk)
      return
    }

    if (dst_id == "rset_head") {
      // actually a detach
      return
    }
    if (id.indexOf("copy_") == 0) {
      // avoid recursing when copying the same node elsewhere
      return
    }

    $.ajax({
      async: false,
      type: "POST",
      url: o.url_action,
      data: {
        "operation": operation,
        "obj_type": rel,
        "obj_id": obj_id,
        "dst_type": dst_rel,
        "dst_id": dst_obj_id,
        "parent_obj_id": parent_obj_id,
      },
      error: function(jqXHR, exception) {
        if (jqXHR.status === 0) {
          msg = 'Connection error.'
        } else if (jqXHR.status == 404) {
          msg = 'Requested page not found. [404]'
        } else if (jqXHR.status == 500) {
          msg = 'Internal Server Error [500].'
        } else if (exception === 'parsererror') {
          msg = 'Requested JSON parse failed.'
        } else if (exception === 'timeout') {
          msg = 'Time out error.'
        } else if (exception === 'abort') {
          msg = 'Ajax request aborted.'
        } else {
          msg = 'Error: ' + jqXHR.responseText
        }
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        try {
          new_obj_id = msg["obj_id"]
        } catch(e) {
          new_obj_id = -1
        }
        if ((msg != "0") && (new_obj_id < 0)) {
          $.jstree.rollback(data.rlbk)
          designer_json_status(msg)
          return
        }

        $("[rel="+dst_rel+"][obj_id="+dst_obj_id+"]").each(function(){
          var this_dst_id = $(this).attr("id")
          var this_dst_tree_id = $(this).parents("[name=catree]").attr("id")
          if ((this_dst_tree_id == dst_tree_id) && (this_dst_id == dst_id)) {
            return
          }
          $(this).parents("[name=catree]").jstree("move_node", "#copy_"+id, "#"+this_dst_id, "last")
        })
        if (rel.indexOf("hidden") > 0) {
          $("[rel=ruleset_head]").children("ul").children("li[rel="+rel+"][obj_id="+obj_id+"]").remove()
        }
        $("[id^=copy_]").each(function(){
          var parent_id = $(this).parents("li").first().attr("id")
          var id = $(this).attr("id").replace(/^(\w*_)*/, "")
          if (new_obj_id > 0) {
            // the server provided a new obj_id. replace the original's.
            $(this).attr("obj_id", new_obj_id)
            var regex = new RegExp(obj_id + "$")
            id = id.replace(regex, new_obj_id)
          }
          $(this).attr("id", parent_id+"_"+id)
        })
        if ((rel == "filterset")&&(dst_rel.indexOf("ruleset")==0)) {
          // purge old ruleset's filterset
          $("[obj_id="+dst_obj_id+"][rel^=ruleset]").children("ul").children("li[rel=filterset]").each(function(){
            if ($(this).attr("obj_id") == obj_id) {
              $(this).prependTo($(this).parent())
              return
            }
            $(this).remove()
          })
        }
      }
    });
}

function designer__remove(o, e, data) {
  data.rslt.obj.each(function() {
    var obj_id = $(this).attr("obj_id")
    var obj_rel = $(this).attr("rel")
    if (!confirm(i18n.t("designer.warn_remove"))) {
      $.jstree.rollback(data.rlbk)
      return
    }
    $.ajax({
      async: false,
      type: "POST",
      url: o.url_action,
      data: {
        "operation": "delete",
        "obj_type": $(this).attr("rel"),
        "obj_id": $(this).attr("obj_id"),
      },
      error: function(jqXHR, exception) {
        if (jqXHR.status === 0) {
          msg = 'Connection error.'
        } else if (jqXHR.status == 404) {
          msg = 'Requested page not found. [404]'
        } else if (jqXHR.status == 500) {
          msg = 'Internal Server Error [500].'
        } else if (exception === 'parsererror') {
          msg = 'Requested JSON parse failed.'
        } else if (exception === 'timeout') {
          msg = 'Time out error.'
        } else if (exception === 'abort') {
          msg = 'Ajax request aborted.'
        } else {
          msg = 'Error: ' + jqXHR.responseText
        }
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
          designer_json_status(msg)
        }
        $("[name=catree]:visible").each(function(){
          $(this).jstree("delete_node", "[rel="+obj_rel+"][obj_id="+obj_id+"]")
        })
      }
    });
  });
}

function designer__create(o, e, data) {
  data.rslt.obj.each(function() {
    var tmp_obj = $(this)
    var parent_id = data.rslt.parent.attr("id")
    var parent_obj_id = data.rslt.parent.attr("obj_id")
    var parent_rel = data.rslt.parent.attr("rel")
    var tree_id = data.rslt.parent.parents("[name=catree]").attr("id")
    var new_data = tmp_obj.text()
    var new_rel = ""
    var new_rel_short = ""
    if (parent_rel == "modset") {
      new_rel = "module"
      new_rel_short = "mod"
    } else if (parent_rel == "moduleset_head") {
      new_rel = "modset"
      new_rel_short = "mset"
    } else if (parent_rel == "ruleset_head") {
      new_rel = "ruleset"
      new_rel_short = "rset"
    } else if (parent_rel == "filterset_head") {
      new_rel = "filterset"
      new_rel_short = "fset"
    } else if (parent_rel.indexOf("ruleset") == 0) {
      new_rel = "variable"
      new_rel_short = "var"
    } else {
      return
    }
    $.ajax({
      async: false,
      type: "POST",
      url: o.url_action,
      data: {
        "operation": "create",
        "obj_name": new_data,
        "obj_type": new_rel,
        "parent_obj_id": parent_obj_id
      },
      error: function(jqXHR, exception) {
        if (jqXHR.status === 0) {
          msg = 'Connection error.'
        } else if (jqXHR.status == 404) {
          msg = 'Requested page not found. [404]'
        } else if (jqXHR.status == 500) {
          msg = 'Internal Server Error [500].'
        } else if (exception === 'parsererror') {
          msg = 'Requested JSON parse failed.'
        } else if (exception === 'timeout') {
          msg = 'Time out error.'
        } else if (exception === 'abort') {
          msg = 'Ajax request aborted.'
        } else {
          msg = 'Error: ' + jqXHR.responseText
        }
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg == "0") {
          $("[name=catree]:visible").jstree("refresh");
          return
        }
        if ((msg != "0") && !("obj_id" in msg)) {
          $.jstree.rollback(data.rlbk)
          designer_json_status(msg)
          return
        }
        var new_obj_id = msg['obj_id']
        tmp_obj.attr("obj_id", new_obj_id)

        if ((parent_id == "rset_head") || (parent_id == "fset_head") || (parent_id == "moduleset_head")) {
          var new_id = new_rel_short+new_obj_id
          tmp_obj.attr("id", new_id)
          $("[rel="+parent_rel+"]:visible").each(function(){
              var this_tree_id = $(this).parents("[name=catree]").attr("id")
              if (this_tree_id == tree_id) {
                return
              }
              var new_id = new_rel_short+new_obj_id
              $(this).parents("[name=catree]").jstree("create_node", "#"+parent_id, "first", {"data": new_data.replace(/^\s*/, ""), "attr": {"rel": new_rel, "id": new_id, "obj_id": new_obj_id}})
          })
        } else {
          var new_id = parent_id+'_'+new_rel_short+new_obj_id
          tmp_obj.attr("id", new_id)
          $("[rel="+parent_rel+"][obj_id="+parent_obj_id+"]:visible").each(function(){
              var this_tree_id = $(this).parents("[name=catree]").attr("id")
              if (($(this).attr("id") == parent_id) && (this_tree_id == tree_id)) {
                return
              }
              var par_id = $(this).attr("id")
              var new_id = par_id+'_'+new_rel_short+new_obj_id
              $(this).parents("[name=catree]").jstree("create_node", "#"+par_id, "first", {"data": new_data.replace(/^\s*/, ""), "attr": {"rel": new_rel, "id": new_id, "obj_id": new_obj_id}})
          })
        }
        
        //$("{name=jstree]:visible").find()
      }
    });
  });
}

function designer_show_importer(o) {
  if (!services_ismemberof("Manager", "CompManager")) {
    return
  }
  var div = $("<div id='impoprt'></div>")
  var title = $("<h3 data-i18n='designer.import'></h3>")
  var textarea = $("<textarea id='import_text' class='pre' style='width:100%;height:20em;margin-bottom:1em'></textarea>")
  var input = $("<input type='button'></input>")
  input.attr("value", i18n.t("designer.import"))
  input.bind("click", function() {
    o.comp_import()
  })
  div.append(title)
  div.append(textarea)
  div.append("<br>")
  div.append(input)
  div.i18n()
  o.e_info.html(div)
}

function designer_show_variable(o, e) {
  var var_id = e.attr('obj_id')
  var rset_id = e.parents("li").first().attr('obj_id')

  services_osvcgetrest("R_COMPLIANCE_RULESET_VARIABLE", [rset_id, var_id], "", function(jd){
    if (jd.error && (jd.error.length > 0)) {
      o.e_info.html(services_error_fmt(jd))
      return
    }
    var data = jd.data[0]
    var div = $("<div></div>")
    var form_div = $("<div></div>")
    var title = $("<h3>"+data.var_name+"</h3>")
    var p1 = $("<p></p>")
    var p2 = $("<p></p>")

    p1.text(i18n.t("designer.var_class", {"name": data.var_class}))
    p2.text(i18n.t("designer.var_last_mod", {"by": data.var_author, "on": data.var_updated}))
    form_div.uniqueId()
    id = form_div.attr("id")

    div.append(title)
    div.append(p1)
    div.append(p2)
    div.append("<br>")
    div.append(form_div)
    o.e_info.html(div)

    try {
      var _data = $.parseJSON(data.var_value)
    } catch(err) {
      var _data = data.var_value
    }

    form(id, {
      "data": _data,
      "var_id": var_id,
      "rset_id": rset_id,
      "display_mode": true,
      "digest": true,
      "form_name": data.var_class,
      "disable_edit": false
    })
  },
  function(xhr, stat, error) {
    o.e_info.html(services_ajax_error_fmt(xhr, stat, error))
  })
}

function designer__select(o, e, data) {
  data.rslt.obj.each(function() {
    if ($(this).is("[rel$=_head]")) {
      o.show_importer()
      return
    } else if ($(this).is("[rel=variable]")) {
      o.show_variable($(this))
      return
    }
    $.ajax({
    async: false,
    type: "POST",
    url: o.url_action,
    data: {
      "operation": "show",
      "obj_type": $(this).attr('rel'),
      "obj_id": $(this).attr('obj_id'),
    },
    error: function(jqXHR, exception) {
      if (jqXHR.status === 0) {
        msg = 'Connection error.'
      } else if (jqXHR.status == 404) {
        msg = 'Requested page not found. [404]'
      } else if (jqXHR.status == 500) {
        msg = 'Internal Server Error [500].'
      } else if (exception === 'parsererror') {
        msg = 'Requested JSON parse failed.'
      } else if (exception === 'timeout') {
        msg = 'Time out error.'
      } else if (exception === 'abort') {
        msg = 'Ajax request aborted.'
      } else {
        msg = 'Error: ' + jqXHR.responseText
      }
      $.jstree.rollback(data.rlbk)
      $(".flash").html(msg).slideDown()
    },
    success: function(msg){
      o.e_info.html(msg)
      o.e_info.find("script").each(function(i){
        eval($(this).text());
        $(this).remove();
      });
      o.resizer()
    }
  });
 });
}

function designer_init(o) {
  o.e_calink = o.div.find("#calink")
  o.e_close = o.div.find("#caclose")
  o.e_tree = o.div.find("#catree")
  o.e_tree_container = o.e_tree.parent()
  o.e_tree2 = o.div.find("#catree2")
  o.e_tree_container2 = o.e_tree2.parent()
  o.e_info = o.div.find("#cainfo")
  o.e_sep = o.div.find("#casep")
  o.e_search_input = o.div.find("#casearch")
  o.e_search_input2 = o.div.find("#casearch2")


  if (o.options.search2) {
    o.e_tree_container2.show(500)
  }
  o.resizer()

  o.e_calink.bind("click", function() {
    o.link()
  })
  o.e_close.bind("click", function() {
    o.div.find("[name=catree]").jstree("close_all", "fold")
    o.resizer()
  })

  o.jstree_data = {
   "types": {
    "types": {
     "module": {
      "icon": {
       "image": o.url_images+"/action16.png",
      },
     },
     "module_autofix": {
      "icon": {
       "image": o.url_images+"/actionred16.png",
      },
     },
     "modset": {
      "icon": {
       "image": o.url_images+"/modset16.png",
      },
     },
     "group": {
      "icon": {
       "image": o.url_images+"/guys16.png",
      },
     },
     "group_pub": {
      "icon": {
       "image": o.url_images+"/guys16.png",
      },
     },
     "group_resp": {
      "icon": {
       "image": o.url_images+"/admins16.png",
      },
     },
     "filter": {
      "icon": {
       "image": o.url_images+"/filter16.png",
      },
     },
     "filterset": {
      "icon": {
       "image": o.url_images+"/filter16.png",
      },
     },
     "ruleset": {
      "icon": {
       "image": o.url_images+"/pkg16.png",
      },
     },
     "ruleset_hidden": {
      "icon": {
       "image": o.url_images+"/pkglight16.png",
      },
     },
     "ruleset_cxt": {
      "icon": {
       "image": o.url_images+"/rsetcxt16.png",
      },
     },
     "ruleset_cxt_hidden": {
      "icon": {
       "image": o.url_images+"/rsetcxtlight16.png",
      },
     },
     "variable": {
      "icon": {
       "image": o.url_images+"/comp16.png",
      },
     },
     "table": {
      "icon": {
       "image": o.url_images+"/db16.png",
      },
     },
    },
   },
   "json_data" : {
    "ajax" : {
     "url" : o.json_data_url(),
    },
   },
   "contextmenu": {
     "items": function(node){
       var_classes = {}
       function var_class_entry(var_class) {
         return {
           "label": var_class,
           "action": function(obj){
             $.ajax({
               async: false,
               type: "POST",
               url: o.url_action,
               data: {
                "operation": "set_var_class",
                "var_class": var_class,
                "obj_id": obj.attr("obj_id"),
               },
               success: function(msg){
                 //$("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                 designer_json_status(msg)
               }
             });
           }
         }
       }
       for (i=0;i<o.options.var_class_names.length;i++) {
         var var_class = o.options.var_class_names[i]
         var_classes['set_var_class_'+var_class] = var_class_entry(var_class)
       }
       h = {
         "remove" : {
           "label": "Delete",
           "_disabled": false,
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){this.remove(obj)}
         },
         "rename" : {
           "label": "Rename",
           "_disabled": false,
           //"_class": "class",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           //"submenu": {},
           "action": function(obj){this.rename(obj)}
         }
       }
  
       //
       // moduleset_head
       //
       if (node.attr("rel")=="moduleset_head") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         h["create"] = {
           "label": "Add moduleset",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){this.create(obj, "first", {"attr": {"rel": "modset"}})}
         }
       }
  
       //
       // filterset_head
       //
       else if (node.attr("rel")=="filterset_head") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         h["create"] = {
           "label": "Add filterset",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){this.create(obj, "first", {"attr": {"rel": "filterset"}})}
         }
       }
  
       //
       // ruleset_head
       //
       else if (node.attr("rel")=="ruleset_head") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         h["create"] = {
           "label": "Add ruleset",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){this.create(obj, "first", {"attr": {"rel": "ruleset"}})}
         }
       }
  
  
       //
       // module
       //
       else if (node.attr("rel").indexOf("module") == 0) {
         h["autofix"] = {
           "label": "Autofix",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "on": {
               "label": "On",
               "action": function(obj){
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_autofix",
                    "autofix": true,
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var r = obj.attr('rel')
                     if (r == 'module') {
                       obj.attr('rel', 'module_autofix')
                     }
                     $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                     designer_json_status(msg)
                   }
                 });
               }
             },
             "off": {
               "label": "Off",
               "action": function(obj){
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_autofix",
                    "autofix": false,
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var r = obj.attr('rel')
                     if (r == 'module_autofix') {
                       obj.attr('rel', 'module')
                     }
                     $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                     designer_json_status(msg)
                   }
                 });
               }
             },
           }
         }
       }
  
       //
       // moduleset
       //
       else if (node.attr("rel")=="modset") {
         h["create"] = {
           "label": "Add module",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){this.create(obj, "first", {"attr": {"rel": "module"}})}
         }
         h["clone"] = {
           "label": "Clone",
           "action": function(obj){
             $.ajax({
               async: false,
               type: "POST",
               url: o.url_action,
               data: {
                "operation": "clone",
                "obj_id": obj.attr("obj_id"),
                "obj_type": obj.attr("rel"),
               },
               success: function(msg){
                 $("[name=catree]:visible").jstree("refresh");
                 designer_json_status(msg)
               }
             });
           }
         }
         if (node.parents("li").attr("rel") == "modset") {
           h["remove"]["_disabled"] = true
           h["detach_moduleset"] = {
             "label": "Detach moduleset",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_moduleset_from_moduleset",
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": obj.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   var rel = obj.attr("rel")
                   var obj_id = obj.attr("obj_id")
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var child_modset_id = l.pop()
                   var parent_modset_id = l.pop()
                   l = [parent_modset_id, child_modset_id]
                   id = l.join("_")
                   $("[name=catree]").each(function(){
                     t = $(this)
                     t.children("ul").children("[rel=moduleset_head]").find("[id$="+id+"]").each(function(){
                       t.jstree("delete_node", "#"+$(this).attr("id"))
                     })
                   })
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
  
       //
       // ruleset
       //
       else if (node.attr("rel").indexOf("ruleset") == 0) {
         h["create"] = {
           "label": "Add variable",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "action": function(obj){
              this.create(obj, "first", {"attr": {"rel": "variable"}})
           }
         }
         h["clone"] = {
           "label": "Clone",
           "action": function(obj){
             $.ajax({
               async: false,
               type: "POST",
               url: o.url_action,
               data: {
                "operation": "clone",
                "obj_id": obj.attr("obj_id"),
                "obj_type": obj.attr("rel"),
               },
               success: function(msg){
                 $("[name=catree]:visible").jstree("refresh");
                 designer_json_status(msg)
               }
             });
           }
         }
         h["set_type"] = {
           "label": "Set type",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "contextual": {
               "label": "Contextual",
               "action": function(obj){
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_type",
                    "type": "contextual",
                    "obj_type": "ruleset",
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                     var r = obj.attr('rel')
                     if (r == 'ruleset') {
                       e.attr('rel', 'ruleset_cxt')
                     } else if (r == 'ruleset_hidden') {
                       e.attr('rel', 'ruleset_cxt_hidden')
                     }
                     $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                     designer_json_status(msg)
                   }
                 });
               }
             },
             "explicit": {
               "label": "Explicit",
               "action": function(obj){
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_type",
                    "type": "explicit",
                    "obj_type": "ruleset",
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                     var r = obj.attr('rel')
                     if (r == 'ruleset_cxt') {
                       e.attr('rel', 'ruleset')
                     } else if (r == 'ruleset_cxt_hidden') {
                       e.attr('rel', 'ruleset_hidden')
                     }
                     $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                     designer_json_status(msg)
                   }
                 });
               }
             },
           }
         }
         h["set_publication"] = {
           "label": "Set publication",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "published": {
               "label": "Published",
               "action": function(obj){
                 var t = this
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_public",
                    "publication": true,
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                     var r = obj.attr("rel")
                     if (r == "ruleset_cxt_hidden") {
                       e.attr("rel", "ruleset_cxt")
                     } else if (r == "ruleset_hidden") {
                       e.attr("rel", "ruleset")
                     }
                     designer_json_status(msg)
                   }
                 });
               }
             },
             "not_published": {
               "label": "Not published",
               "action": function(obj){
                 $.ajax({
                   async: false,
                   type: "POST",
                   url: o.url_action,
                   data: {
                    "operation": "set_public",
                    "publication": false,
                    "obj_id": obj.attr("obj_id"),
                   },
                   success: function(msg){
                     var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                     var r = obj.attr("rel")
                     if (r == "ruleset_cxt") {
                       e.attr("rel", "ruleset_cxt_hidden")
                     } else if (r == "ruleset") {
                       e.attr("rel", "ruleset_hidden")
                     }
                     designer_json_status(msg)
                   }
                 });
               }
             },
           }
         }
         if (node.attr("rset_type") == "contextual") {
           h["detach_filterset"] = {
             "label": "Detach filterset",
             "action": function(obj){
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_filterset",
                  "obj_id": obj.attr("obj_id"),
                 },
                 success: function(msg){
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var fset_id = l.pop()
                   var rset_id = l.pop()
                   l = [rset_id, fset_id]
                   id = l.join("_")
                   $("[name=catree]:visible").each(function(){
                     $(this).jstree("delete_node", "[id$="+id+"]")
                   })
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
         if (node.parents("li").attr("rel") == "modset") {
           h["remove"]["_disabled"] = true
           h["detach_ruleset"] = {
             "label": "Detach ruleset",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_ruleset_from_moduleset",
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": obj.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   var rel = obj.attr("rel")
                   var obj_id = obj.attr("obj_id")
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var child_rset_id = l.pop()
                   var parent_modset_id = l.pop()
                   l = [parent_modset_id, child_rset_id]
                   id = l.join("_")
                   $("[name=catree]").each(function(){
                     t = $(this)
                     t.children("ul").children("[rel=moduleset_head]").find("[id$="+id+"]").each(function(){
                       t.jstree("delete_node", "#"+$(this).attr("id"))
                     })
                   })
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
         if (node.parents("li").attr("rel").indexOf("ruleset") == 0 &&
             node.parents("li").attr("rel") != "ruleset_head") {
           h["remove"]["_disabled"] = true
           h["detach_ruleset"] = {
             "label": "Detach ruleset",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_ruleset",
                  "publication": false,
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": obj.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   var rel = obj.attr("rel")
                   if ((rel == "ruleset_hidden") || (rel == "ruleset_cxt_hidden")) {
                     var obj_id = obj.attr("obj_id")
                     var id = obj.attr("id")
                     var v = $("#catree").find("[obj_id="+obj_id+"][rel="+rel+"]")
                     if (v.length == 1) {
                       // re-attach the rule at head level
                       $("[name=catree]").jstree("move_node", "#"+id, "#rset_head")
                     }
                     var l = id.split("_")
                     var child_rset_id = l.pop()
                     var parent_rset_id = l.pop()
                     l = [parent_rset_id, child_rset_id]
                     id = l.join("_")
                     $("[name=catree]").each(function(){
                       t = $(this)
                       t.find("[id$="+id+"]").each(function(){
                         if ($(this).parents("li").first().attr("id") == "rset_head") {
                           return
                         }
                         t.jstree("delete_node", "#"+$(this).attr("id"))
                       })
                     })
                     // set id of restored non-published contextual ruleset at rset_head level
                     $("[id^=copy_]").each(function(){
                       var n_id = "rset"+$(this).attr("obj_id")
                       $(this).attr("id", n_id)
                     })
                   } else {
                     t.move_node(obj, "#rset_head")
                   }
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
  
       //
       // group responsible or publication
       //
       if (node.attr("rel").indexOf("group_") == 0) {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         if (node.parents("li").attr("rel").indexOf("ruleset") == 0) {
            var set_group_publication = "set_rset_group_publication"
            var set_group_responsible = "set_rset_group_responsible"
         } else if (node.parents("li").attr("rel") == "modset") {
            var set_group_publication = "set_modset_group_publication"
            var set_group_responsible = "set_modset_group_responsible"
         }
         if ((node.parents("li").attr("rel").indexOf("ruleset") == 0) || 
             (node.parents("li").attr("rel") == "modset")) {
           h["set_gtype"] = {
             "label": "Set group role",
             "separator_before": false,
             "separator_after": false,
             "icon": false,
             "submenu": {
               "publication": {
                 "label": "Publication",
                 "action": function(obj){
                   var t = this
                   $.ajax({
                     async: false,
                     type: "POST",
                     url: o.url_action,
                     data: {
                      "operation": set_group_publication,
                      "obj_id": obj.attr("obj_id"),
                      "parent_obj_id": obj.parents("li").attr("obj_id")
                     },
                     success: function(msg){
                       $("[name=catree]:visible").find("li[obj_id="+obj.parents("li").attr("obj_id")+"][rel="+obj.parents("li").attr("rel")+"]").children("ul").children("li[obj_id="+obj.attr("obj_id")+"]").attr("rel", "group_pub")
                       designer_json_status(msg)
                     }
                   });
                 }
               },
               "responsible": {
                 "label": "Responsible",
                 "action": function(obj){
                   $.ajax({
                     async: false,
                     type: "POST",
                     url: o.url_action,
                     data: {
                      "operation": set_group_responsible,
                      "obj_id": obj.attr("obj_id"),
                      "parent_obj_id": obj.parents("li").attr("obj_id")
                     },
                     success: function(msg){
                       $("[name=catree]:visible").find("li[obj_id="+obj.parents("li").attr("obj_id")+"][rel="+obj.parents("li").attr("rel")+"]").children("ul").children("li[obj_id="+obj.attr("obj_id")+"]").attr("rel", "group_resp")
                       designer_json_status(msg)
                     }
                   });
                 }
               },
             }
           }
         }
       }
       //
       // group responsible
       //
       if (node.attr("rel")=="group_resp") {
         if (node.parents("li").attr("rel").indexOf("ruleset") == 0 || node.parents("li").attr("rel") == "modset") {
           h["detach_group_responsible"] = {
             "label": "Detach responsible",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_responsible_group",
                  "parent_obj_type": obj.parents("li").attr("rel"),
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": obj.parents("li").attr("obj_id")
                 },
                 success: function(msg){
                     var id = obj.attr("id")
                     var l = id.split("_")
                     var child_id = l.pop()
                     var parent_id = l.pop()
                     l = [parent_id, child_id]
                     id = l.join("_")
                     $("[name=catree]:visible").each(function(){
                       $(this).jstree("delete_node", "[id$="+id+"][rel="+obj.attr("rel")+"]")
                     })
  
                   t.delete_node(obj)
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
  
       //
       // group publication
       //
       if (node.attr("rel")=="group_pub") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         if (node.parents("li").attr("rel").indexOf("ruleset") == 0 || node.parents("li").attr("rel") == "modset") {
           h["detach_group_publication"] = {
             "label": "Detach publication",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_publication_group",
                  "parent_obj_type": obj.parents("li").attr("rel"),
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": obj.parents("li").attr("obj_id")
                 },
                 success: function(msg){
                     var id = obj.attr("id")
                     var l = id.split("_")
                     var child_id = l.pop()
                     var parent_id = l.pop()
                     l = [parent_id, child_id]
                     id = l.join("_")
                     $("[name=catree]:visible").each(function(){
                       $(this).jstree("delete_node", "[id$="+id+"][rel="+obj.attr("rel")+"]")
                     })
  
                   t.delete_node(obj)
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
  
       //
       // null
       //
       else if (node.attr("rel") == null) {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
       }
  
       //
       // table
       //
       else if (node.attr("rel")=="table") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
       }
  
       //
       // filter
       //
       else if (node.attr("rel")=="filter") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         if (node.parents("li").attr("rel") == "filterset") {
           h["set_log_op"] = {
             "label": "Set logical operator",
             "separator_before": false,
             "separator_after": false,
             "icon": false,
             "submenu": {
               "and": set_log_op_entry("AND", "filter", node),
               "and_not": set_log_op_entry("AND NOT", "filter", node),
               "or": set_log_op_entry("OR", "filter", node),
               "or not": set_log_op_entry("AND NOT", "filter", node)
             }
           }
           h["detach_filter"] = {
             "label": "Detach filter",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_filter",
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": node.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   t.delete_node(obj)
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
  
       //
       // variable
       //
       else if (node.attr("rel")=="variable") {
         h["set_var_class"] = {
           "label": "Set variable class",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": var_classes,
         }
       }
  
       //
       // filterset
       //
       else if (node.attr("rel")=="filterset") {
         h["set_stats"] = {
           "label": "Set statistics",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "yes": o.set_stats(true, "Compute daily statitiscs", node),
             "no": o.set_stats(false, "Do not compute daily statistics", node)
           }
         }
         if (node.parents("li").attr("rel") == "filterset") {
           h["remove"]["_disabled"] = true
           h["rename"]["_disabled"] = true
           h["set_log_op"] = {
             "label": "Set logical operator",
             "separator_before": false,
             "separator_after": false,
             "icon": false,
             "submenu": {
               "and": set_log_op_entry("AND", "filterset", node),
               "and_not": set_log_op_entry("AND NOT", "filterset", node),
               "or": set_log_op_entry("OR", "filterset", node),
               "or not": set_log_op_entry("AND NOT", "filterset", node)
             }
           }
           h["detach_filterset"] = {
             "label": "Detach filterset",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_filterset",
                  "parent_obj_type": "filterset",
                  "obj_id": obj.attr("obj_id"),
                  "parent_obj_id": node.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var fset_id = l.pop()
                   var rset_id = l.pop()
                   l = [rset_id, fset_id]
                   id = l.join("_")
                   $("[name=catree]:visible").each(function(){
                     $(this).jstree("delete_node", "[id$="+id+"]")
                   })
                   designer_json_status(msg)
                 }
               });
             }
           }
         } else if (node.parents("li").attr("rel").indexOf("ruleset") == 0) {
           h["remove"]["_disabled"] = true
           h["rename"]["_disabled"] = true
           h["detach_filterset"] = {
             "label": "Detach filterset",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: o.url_action,
                 data: {
                  "operation": "detach_filterset",
                  "parent_obj_type": "ruleset",
                  "parent_obj_id": node.parents("li").attr("obj_id"),
                 },
                 success: function(msg){
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var fset_id = l.pop()
                   var rset_id = l.pop()
                   l = [rset_id, fset_id]
                   id = l.join("_")
                   $("[name=catree]:visible").each(function(){
                     $(this).jstree("delete_node", "[id$="+id+"]")
                   })
                   designer_json_status(msg)
                 }
               });
             }
           }
         }
       }
       o.resizer()
       return h
     }
   },
   "search": {
     "show_only_matches": false
   },
   "crrm": {
     "move": {
       "always_copy": true,
       "check_move": function (m) {
          if (m.o.attr('rel').indexOf("ruleset")==0 && m.np.attr('rel')=="modset") { return true }
          if (m.o.attr('rel')=="filterset" && m.np.attr('rel').indexOf("ruleset")==0) { return true }
          if (m.o.attr('rel').indexOf("ruleset")==0 && m.np.attr('rel').indexOf("ruleset")==0) { return true }
          if (m.o.attr('rel')=="variable" && m.np.attr('rel').indexOf("ruleset")==0) { return true }
          if (m.o.attr('rel')=="filter" && m.np.attr('rel')=="filterset") { return true }
          if (m.o.attr('rel')=="filterset" && m.np.attr('rel')=="filterset") { return true }
          if (m.o.attr('rel').indexOf("group")==0 && m.np.attr('rel').indexOf("ruleset")==0) { return true }
          if (m.o.attr('rel').indexOf("group")==0 && m.np.attr('rel')=="modset") { return true }
          if (m.o.attr('rel')=="modset" && m.np.attr('rel')=="modset") { return true }
          return false
       }
     }
   },
   "plugins" : [
     "themes",
     "json_data",
     "ui",
     "types",
     "crrm",
     "contextmenu",
     "dnd",
     //"hotkeys",
     "cookies",
     "search",
     "adv_search"
   ]
  }

  o.monitor_doc_height();

  o.e_tree.jstree(o.jstree_data).bind("rename.jstree", o.__rename)
                                  .bind("move_node.jstree", o.__move)
                                  .bind("remove.jstree", o.__remove)
                                  .bind("create.jstree", o.__create)
                                  .bind("select_node.jstree", o.__select)
  
  o.jstree_data["cookies"] = {
    "save_opened": "jstree_open2",
    "save_selected": "jstree_select2",
  }
  o.jstree_data["json_data"]["ajax"]["url"] = o.json_data_url(2)
  
  o.e_tree2.jstree(o.jstree_data).bind("rename.jstree", o.__rename)
                                   .bind("move_node.jstree", o.__move)
                                   .bind("remove.jstree", o.__remove)
                                   .bind("create.jstree", o.__create)
                                   .bind("select_node.jstree", o.__select)
  
  
  o.e_search_input.keyup(function(event){
    if (is_enter(event)) {
      $("#catree:visible").jstree("refresh");
    }
  })
  o.e_search_input2.keyup(function(event){
    if (is_enter(event)) {
      $("#catree2:visible").jstree("refresh");
    }
  })
  
  // tree width dragging
  o.e_sep.mousedown(function(){
    $("body").addClass("noselect")
    var ini_x = event.pageX
    var ini_w = $("#catree").width()
    $(document).bind("mousemove", function(){
      $("#catree").css({"width": ini_w+event.pageX-ini_x})
      o.resizer()
    })
  })
  $(document).mouseup(function(){
    $("body").removeClass("noselect")
    $(this).unbind("mousemove")
  })

  o.e_sep.dblclick(function(){
    o.e_tree_container2.toggle()
    o.e_tree_container2.find("#catree2:visible").jstree("refresh");
    o.resizer()
  })
  
  $(window).bind("resize", o.resizer)
  $(window).bind("load", o.resizer)
  o.resizer()
}

function designer_comp_import(o) {
  $.ajax({
    async: false,
    type: "POST",
    url: o.url_action,
    data: {
     "operation": "import",
     "value": $("#import_text").val(),
    },
    success: function(msg){
      o.e_info.html(msg)
    }
  });
}

//
// monitor doc height changes to trigger the resizer
//
function designer_monitor_doc_height(o){
  var lastHeight, newHeight, timer;
  try {
    lastHeight = $(document).height()
  } catch(e) {
    lastHeight = 0
  }
  (function run() {
    try {
      newHeight = $(document).height()
    } catch(e) {
      newHeight = 0
    }

    if( lastHeight != newHeight ) {
      o.resizer()
    }
    lastHeight = newHeight
    timer = setTimeout(run, 200)
  })()
}


