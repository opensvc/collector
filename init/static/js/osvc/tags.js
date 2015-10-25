function e_tag(tag_data, init_data) {
  if (init_data.candidates == true) {
    cl = "tag tag_candidate"
  } else {
    cl = "tag tag_attached"
  }
  s = "<span tag_id='"+tag_data.tag_id+"' class='"+cl+"'>"+tag_data.tag_name+" </span>"
  e = $(s)
  e.bind("mouseover", function(){
    if (init_data.responsible && init_data.candidates != true) {
      $(this).addClass("tag_del")
    }
  })
  e.bind("mouseout", function(){
    if (init_data.responsible && init_data.candidates != true) {
      $(this).removeClass("tag_del")
    }
  })
  e.bind("click", function(event){
    event.stopPropagation()
    if (!init_data.responsible) {
      return
    }
    if ($(this).hasClass("tag_candidate")) {
      tag_attach(init_data, tag_data.tag_name)
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
      tag_detach($(this), tag_data, init_data)
    }
  })
  return e
}

function tag_detach(tag, tag_data, init_data) {
    $("#"+init_data.tid).html(T("Detaching tag ..."))
    _data = {
      "tag_id": tag_data.tag_id
    }
    if ("nodename" in init_data) {
      _data.nodename = init_data.nodename
    } else if ("svcname" in init_data) {
      _data.svcname = init_data.svcname
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
        init_tags(init_data)
     }
    })
}

function e_add_tag(init_data) {
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
      tag_input_keyup(event, init_data, tag, tag_name)
    })
    e.focus()
  })
  return e
}

function tags(data) {
  if ("url" in data) {
    url = data.url
  } else if ("nodename" in data) {
    url = $(location).attr("origin") + "/init/tags/call/json/json_node_tags/"+data.nodename
  } else if ("svcname" in data) {
    url = $(location).attr("origin") + "/init/tags/call/json/json_svc_tags/"+data.svcname
  } else {
    return
  }
  $.getJSON(url, function(_data){
    d = $("<div></div>")
    for (i=0; i<_data.length; i++) {
      d.append(e_tag(_data[i], data))
    }
    if (data.responsible && data.candidates != true) {
      d.append(e_add_tag(data))
    }
    $(document).bind("click", function(){
      $(this).find(".tag").removeClass("tag_detach1").removeClass("tag_detach2").removeClass("tag_detach3")
    })
    $("#"+data.tid).html(d)
  })
}

function tag_input_candidates(init_data, tag, tag_name) {
  tid = init_data.tid
  prefix = $("#"+tid).find(".tag_input").val()
  if (prefix.length == 0) {
    prefix = "%"
  }
  prefix = prefix.replace(/\//, "_")
  prefix = encodeURIComponent(prefix)
  if ("nodename" in init_data) {
    var url = $(location).attr("origin") + "/init/tags/call/json/list_node_avail_tags/"+init_data.nodename+"/"+prefix
  } else if ("svcname" in init_data) {
    var url = $(location).attr("origin") + "/init/tags/call/json/list_svc_avail_tags/"+init_data.svcname+"/"+prefix
  } else {
    return
  }
  ctid = tid+"c"
  data = {
   "tid": ctid,
   "responsible": init_data.responsible,
   "url": url,
   "candidates": true
  }
  if ("nodename" in init_data) {
    data.nodename = init_data.nodename
  } else if ("svcname" in init_data) {
    data.svcname = init_data.svcname
  }
  $("#"+ctid).parent().remove()
  e = $("<span><h3>"+T("Candidate tags")+"</h3><div id='"+ctid+"' class='tags'></div></span>")
  $("#"+tid).append(e)
  init_tags(data)
}

function tag_input_keyup(event, init_data, tag, tag_name) {
  if (!is_enter(event)) {
    tag.removeClass("tag_create")
    tag.find("input").removeClass("tag_create")
    tag_input_candidates(init_data, tag, tag_name)
    return
  }
  tag_attach(init_data, tag_name)
}

function tag_attach(init_data, tag_name) {
  // ajax
  //$("#"+init_data.tid).html(T("Attaching tag ..."))
  _data = {
    "tag_name": tag_name
  }
  if ("nodename" in init_data) {
    _data.nodename = init_data.nodename
  } else if ("svcname" in init_data) {
    _data.svcname = init_data.svcname
  }
  if (tag.hasClass("tag_create") || tag.hasClass("tag_candidate")) {
    var url = $(location).attr("origin") + "/init/tags/call/json/create_and_add_tag"
  } else {
    var url = $(location).attr("origin") + "/init/tags/call/json/add_tag"
  }
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
        data = {
          "tid": init_data.tid.substr(0, 32),
          "responsible": init_data.responsible
        }
        if ("nodename" in init_data) {
          data.nodename = init_data.nodename
        } else if ("svcname" in init_data) {
          data.svcname = init_data.svcname
        }
        init_tags(data)
     }
  })
}


