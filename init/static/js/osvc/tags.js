function tags(data) {
  o = {}
  o.div = $("#"+data.tid)
  o.data = data

  o.load = function() {
    return tags_load(this)
  }
  o.add_tag = function(data) {
    return tags_add_tag(this, data)
  }
  o.add_add_tag = function() {
    return tags_add_add_tag(this)
  }
  o.add_candidates = function(tag, tag_name) {
    return tags_add_candidates(this, tag, tag_name)
  }
  o.detach_tag = function(tag, tag_data) {
    return tags_detach_tag(this, tag, tag_data)
  }
  o.attach_tag = function(tag_name) {
    return tags_attach_tag(this, tag_name)
  }

  if ("url" in data) {
    o.url = data.url
  } else if ("nodename" in data) {
    o.url = $(location).attr("origin") + "/init/tags/call/json/json_node_tags/"+data.nodename
  } else if ("svcname" in data) {
    o.url = $(location).attr("origin") + "/init/tags/call/json/json_svc_tags/"+data.svcname
  } else {
    return
  }
  o.load()
  return o
}

function tags_add_tag(o, tag_data) {
  if (o.data.candidates == true) {
    cl = "tag tag_candidate"
  } else {
    cl = "tag tag_attached"
  }
  s = "<span tag_id='"+tag_data.tag_id+"' class='"+cl+"'>"+tag_data.tag_name+" </span>"
  e = $(s)
  e.bind("mouseover", function(){
    if (o.data.responsible && o.data.candidates != true) {
      $(this).addClass("tag_del")
    }
  })
  e.bind("mouseout", function(){
    if (o.data.responsible && o.data.candidates != true) {
      $(this).removeClass("tag_del")
    }
  })
  e.bind("click", function(event){
    event.stopPropagation()
    if (!o.data.responsible) {
      return
    }
    if ($(this).hasClass("tag_candidate")) {
      o.attach_tag(tag_data.tag_name)
      return
    }
    if ($(this).hasClass("tag_detach1")) {
      $(this).removeClass("tag_detach1").addClass("tag_detach2")
    } else
    if ($(this).hasClass("tag_detach2")) {
      $(this).removeClass("tag_detach2").addClass("tag_detach3")
    } else {
      $(this).addClass("tag_detach1")
    }
    if ($(this).hasClass("tag_detach3")) {
      o.detach_tag($(this), tag_data)
    }
  })
  return e
}

function tags_detach_tag(o, tag, tag_data) {
    o.div.html(T("Detaching tag ..."))
    _data = {
      "tag_id": tag_data.tag_id
    }
    if ("nodename" in o.data) {
      _data.nodename = o.data.nodename
    } else if ("svcname" in o.data) {
      _data.svcname = o.data.svcname
    }
    var url = $(location).attr("origin") + "/init/tags/call/json/del_tag"
    $.ajax({
     type: "POST",
     url: url,
     data: _data,
     success: function(msg){
        if (msg.ret != 0) {
          $(".flash").html(msg.msg).slideDown().effect("fade", 15000)
          return
        }
        o.load()
     }
    })
}

function tags_add_add_tag(o) {
  s = "<span class='tag_add'>"+T("Add tag")+" </span>"
  e = $(s)
  e.bind("click", function(){
    old_html = $(this).html()
    e = $(this).find(".tag_input")
    if (e.length>0) {
      return
    }
    s = "<input class='tag_input'></input>"
    $(this).html(s)
    e = $(this).find(".tag_input")
    e.bind("keyup", function(event){
      tag = $(this).parent()
      tag_name = $(this).val()
      tag_input_keyup(event, o, tag, tag_name)
    })
    e.focus()
  })
  return e
}

function tags_load(o) {
  spinner_add(o.div)
  $.getJSON(o.url, function(_data){
    spinner_del(o.div)
    d = $("<div></div>")
    for (i=0; i<_data.length; i++) {
      d.append(o.add_tag(_data[i]))
    }
    if (o.data.responsible && o.data.candidates != true) {
      d.append(o.add_add_tag())
    }
    $(document).bind("click", function(){
      $(this).find(".tag").removeClass("tag_detach1").removeClass("tag_detach2").removeClass("tag_detach3")
    })
    o.div.html(d)
  })
}

function tags_add_candidates(o, tag, tag_name) {
  prefix = o.div.find(".tag_input").val()
  if (prefix.length == 0) {
    prefix = "%"
  }
  prefix = prefix.replace(/\//, "_")
  prefix = encodeURIComponent(prefix)
  if ("nodename" in o.data) {
    var url = $(location).attr("origin") + "/init/tags/call/json/list_node_avail_tags/"+o.data.nodename+"/"+prefix
  } else if ("svcname" in o.data) {
    var url = $(location).attr("origin") + "/init/tags/call/json/list_svc_avail_tags/"+o.data.svcname+"/"+prefix
  } else {
    return
  }
  ctid = o.data.tid+"c"
  data = {
   "tid": ctid,
   "responsible": o.data.responsible,
   "url": url,
   "parent_object": o,
   "candidates": true
  }
  if ("nodename" in o.data) {
    data.nodename = o.data.nodename
  } else if ("svcname" in o.data) {
    data.svcname = o.data.svcname
  }
  $("#"+ctid).parent().remove()
  e = $("<span><h3>"+T("Candidate tags")+"</h3><div id='"+ctid+"' class='tags'></div></span>")
  o.div.append(e)
  tags(data)
}

function tag_input_keyup(event, o, tag, tag_name) {
  if (!is_enter(event)) {
    tag.removeClass("tag_create")
    tag.find("input").removeClass("tag_create")
    o.add_candidates(tag, tag_name)
    return
  }
  o.attach_tag(tag_name)
}

function tags_attach_tag(o, tag_name) {
  // ajax
  //$("#"+init_data.tid).html(T("Attaching tag ..."))
  _data = {
    "tag_name": tag_name
  }
  if ("nodename" in o.data) {
    _data.nodename = o.data.nodename
  } else if ("svcname" in o.data) {
    _data.svcname = o.data.svcname
  }
  if (tag.hasClass("tag_create") || tag.hasClass("tag_candidate")) {
    var url = $(location).attr("origin") + "/init/tags/call/json/create_and_add_tag"
  } else {
    var url = $(location).attr("origin") + "/init/tags/call/json/add_tag"
  }
  o.div.html(T("Attaching tag"))
  $.ajax({
     type: "POST",
     url: url,
     data: _data,
     success: function(msg){
        if (msg.ret == 2) {
          //$("#"+init_data.tid).html(bkp)
          $(".flash").html(msg.msg).slideDown().effect("fade", 5000)
          tag.addClass("tag_create")
          tag.find("input").addClass("tag_create")
          return
        } else if (msg.ret == 3) {
          //$("#"+init_data.tid).html(bkp)
          $(".flash").html(msg.msg).slideDown().effect("fade", 5000)
          return
        } else if (msg.ret == 1) {
          //$("#"+init_data.tid).html(bkp)
          $(".flash").html(msg.msg).slideDown().effect("fade", 5000)
          return
        }
        // refresh tags
        o.data.parent_object.load()
     }
  })
}


