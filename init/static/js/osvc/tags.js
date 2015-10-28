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
  o.add_del_tag = function() {
    return tags_add_del_tag(this)
  }
  o.add_candidates = function(tag, tag_name) {
    return tags_add_candidates(this, tag, tag_name)
  }
  o.detach_tag = function(tag) {
    return tags_detach_tag(this, tag)
  }
  o.attach_tag = function(tag_data) {
    return tags_attach_tag(this, tag_data)
  }
  o._attach_tag = function(tag_data) {
    return _tags_attach_tag(this, tag_data)
  }
  o.bind_admin_tools = function() {
    return tags_bind_admin_tools(this)
  }
  o._bind_admin_tools = function() {
    return _tags_bind_admin_tools(this)
  }

  if (("candidates" in data) && ("nodename" in data)) {
    o.url = "R_NODE_CANDIDATE_TAGS"
    o.url_params = [data.nodename]
  } else if (("candidates" in data) && ("svcname" in data)) {
    o.url = "R_SERVICE_CANDIDATE_TAGS"
    o.url_params = [data.svcname]
  } else if ("nodename" in data) {
    o.url = "R_NODE_TAGS"
    o.url_params = [data.nodename]
  } else if ("svcname" in data) {
    o.url = "R_SERVICE_TAGS"
    o.url_params = [data.svcname]
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
  s = "<span tag_id='"+tag_data.id+"' class='"+cl+"'>"+tag_data.tag_name+" </span>"
  e = $(s)
  e.bind("mouseover", function(){
    if (o.data.responsible && o.data.candidates != true) {
      $(this).addClass("tag_drag")
    }
  })
  e.bind("mouseout", function(){
    if (o.data.responsible && o.data.candidates != true) {
      $(this).removeClass("tag_drag")
    }
  })
  e.bind("click", function(event){
    event.stopPropagation()
    if (!o.data.responsible) {
      return
    }
    if ($(this).hasClass("tag_candidate")) {
      o.attach_tag(tag_data)
      return
    }
  })
  return e
}

function tags_add_del_tag(o) {
  if (o.data.candidates) {
    return
  }
  e = $("<span class='tag_del'></span>")
  e.css({"display": "none"})
  e.text(i18n.t("tags.del"))
  e.droppable({
    accept: ".tag",
    activeClass: "tag_del_active",
    hoverClass: "tag_del_hover",
    drop: function(event, ui) {
      o.detach_tag(ui.draggable)
    }
  });
  return e
}

function tags_add_add_tag(o) {
  if (o.data.candidates) {
    return
  }
  e = $("<span class='tag_add'></span>")
  e.css({"display": "none"})
  e.text(i18n.t("tags.add"))
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
  // init error display zone
  if (!o.div.info) {
    info = $("<div></div>")
    o.div.append(info)
    o.div.info = info
  }
  o.div.info.empty()
  spinner_add(o.div.info)
  options = {
    "meta": "false",
    "limit": "0",
    "props": "id,tag_name"
  }
  if ("prefix" in o.data) {
    options["query"] = "tag_name starts with " + o.data.prefix
  }
  services_osvcgetrest(o.url, o.url_params, options, function(_data) {
    spinner_del(o.div.info)
    if (_data.error) {
      o.div.info.html(services_error_fmt(_data))
      return
    }
    _data = _data.data
    if ((_data.length == 0) && o.data.candidates) {
      o.div.info.text(i18n.t("tags.no_candidates"))
    }
    d = $("<div></div>")
    for (i=0; i<_data.length; i++) {
      d.append(o.add_tag(_data[i]))
    }
    if (o.data.responsible && o.data.candidates != true) {
      d.append(o.add_add_tag())
      d.append(o.add_del_tag())
    }
    o.div.find(".tag").parent().remove()
    o.div.prepend(d)
    $(".tag").draggable({
     "containment": $(".tags"),
     "opacity": 0.9,
     "revert": true,
     "stack": ".tag",
    })

    o.bind_admin_tools()
  },
  function(xhr, stat, error) {
    o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
  })
}

function tags_bind_admin_tools(o) {
  // show tag admin tools to responsibles and managers
  if (o.data.responsible) {
    o._bind_admin_tools()
    return
  }
  services_ismemberof("Manager", function() {
    o._bind_admin_tools()
  })
}

function _tags_bind_admin_tools(o) {
  o.div.hover(
    function(){
      o.div.find(".tag_add,.tag_del").fadeIn()
    },
    function(){
      o.div.find(".tag_add,.tag_del").fadeOut()
    }
  )
}

function tags_add_candidates(o, tag, tag_name) {
  prefix = o.div.find(".tag_input").val()
  if (prefix.length == 0) {
    prefix = "%"
  }
  prefix = prefix.replace(/\//, "_")
  prefix = encodeURIComponent(prefix)

  // 1st candidates exec: init a new tag object
  ctid = o.data.tid+"c"
  data = {
   "tid": ctid,
   "responsible": o.data.responsible,
   "parent_object": o,
   "prefix": prefix,
   "candidates": true
  }
  if ("nodename" in o.data) {
    data.nodename = o.data.nodename
  } else if ("svcname" in o.data) {
    data.svcname = o.data.svcname
  }
  o.div.find("#"+ctid).parent().remove()
  e = $("<span><h3>"+i18n.t("tags.candidates")+"</h3><div id='"+ctid+"' class='tags'></div></span>")
  o.div.append(e)
  o.candidates = tags(data)
}

function tag_input_keyup(event, o, tag, tag_name) {
  if (!is_enter(event)) {
    tag.removeClass("tag_create")
    tag.find("input").removeClass("tag_create")
    o.add_candidates(tag, tag_name)
    return
  }
  o.attach_tag({"tag_name": tag_name})
}

function tags_attach_tag(o, tag_data) {
  if (!tag_data.id) {
    // from <enter> in add tag
    o.div.info.empty()
    o.candidates.div.parent().remove()
    services_osvcgetrest("R_TAGS", "", {"meta": "false", "query": "tag_name="+tag_data.tag_name}, function(jd) {
      if (!jd.data || (jd.data.length == 0)) {
        // tag does not exist yet ... create
        spinner_add(o.div.info, i18n.t("tags.creating"))
        services_osvcpostrest("R_TAGS", "", "", tag_data, function(jd) {
          spinner_del(o.div.info)
          if (jd.error) {
            o.div.info.html(services_error_fmt(jd))
            return
          }
          o._attach_tag(jd.data)
        },
        function(xhr, stat, error) {
          o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
        })
      } else {
        // tag elready exists
        o._attach_tag(jd.data[0])
      }
    },
    function(xhr, stat, error) {
      o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
    })
  } else {
    // from click on a candidate
    o._attach_tag(tag_data)
  }
}

function _tags_attach_tag(o, tag_data) {
  if ("nodename" in o.data) {
    url = "R_TAG_NODE"
    url_params = [tag_data.id, o.data.nodename]
  } else if ("svcname" in o.data) {
    url = "R_TAG_SERVICE"
    url_params = [tag_data.id, o.data.svcname]
  } else {
    return
  }
  o.div.info.empty()
  spinner_add(o.div.info, i18n.t("tags.attaching"))
  services_osvcpostrest(url, url_params, "", "", function(jd) {
    spinner_del(o.div.info)
    if (jd.error) {
      o.div.info.html(services_error_fmt(jd))
      return
    }
    // refresh tags
    if (o.data.parent_object) {
      o.div.parent().remove()
      o.data.parent_object.load()
    } else {
      o.load()
    }
  },
  function(xhr, stat, error) {
    o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
  })
}

function tags_detach_tag(o, tag) {
  o.div.info.empty()
  tag.hide()
  spinner_add(o.div.info, i18n.t("tags.detaching"))
  if ("nodename" in o.data) {
    url = "R_TAG_NODE"
    url_params = [tag.attr("tag_id"), o.data.nodename]
  } else if ("svcname" in o.data) {
    url = "R_TAG_SERVICE"
    url_params = [tag.attr("tag_id"), o.data.svcname]
  } else {
    return
  }
  services_osvcdeleterest(url, url_params, function(jd) {
    spinner_del(o.div.info)
    if (jd.error) {
      o.div.info.html(services_error_fmt(jd))
      return
    }
    // refresh tags
    o.load()
  },
  function(xhr, stat, error) {
    tag.show()
    o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
  })
}


