//
// startup
//
function startup(divid, options) {
  var o = {}
  o.divid = divid
  o.options = options
  o.div = $("#"+o.divid)

  o.init = function() {
    return startup_init(o)
  }
  o.draw = function() {
    return startup_draw(o)
  }
  o.create_link = function(){
    return startup_create_link(this)
  }

  o.div.load('/init/static/views/startup.html', "", function() {
    o.div.i18n();
    o.viz = o.div.find("#viz")
    o.link = o.div.find(".link16")
    o.link_text = o.link.children()
    o.init()
  })
}

function startup_create_link(o) {
  var display = []
  o.div.find("input[type=checkbox][name=nodename]:checked").each(function() {
    display.push($(this).siblings("span").text())
  })
  o.options.display = display
  url = $(location).attr("origin");
  url += "/init/topo/startup?"
  var l = []
  if (o.options.svcnames) {
    l.push("svcnames="+encodeURIComponent(o.options.svcnames.join(",")))
  }
  if (o.options.display) {
    l.push("display="+encodeURIComponent(o.options.display.join(",")))
  }
  l.push("show_disabled="+encodeURIComponent(o.e_show_disabled.prop("checked")))

  url += l.join("&");
  o.link_text.empty().html(url);
  o.link_text.autogrow({vertical: true, horizontal: true});
}

function startup_init(o) {
  // link
  o.link_text.bind("click", function() {
    window.open(o.link_text.val(), '_blank')
  })
  o.link.bind("click", function() {
    o.create_link()
    o.link_text.slideToggle().select()
  })

  // show disabled
  o.e_show_disabled = o.div.find("[name=show_disabled]")
  o.e_show_disabled.uniqueId()
  o.e_show_disabled.siblings("label").attr("for", o.e_show_disabled.attr("id"))
  console.log(o.options.show_disabled)
  if (o.options.show_disabled && (o.options.show_disabled != "false")) {
    o.e_show_disabled.prop("checked", true)
  }

  // create checkboxes
  var nodenames = []
  services_osvcgetrest("R_SERVICE_INSTANCES", "", {
   "limit": "0",
   "meta": "0",
   "query": "mon_svcname in " + o.options.svcnames.join(","),
   "props": "mon_nodname"
  }, function(jd) {
    var data = jd.data
    for (var i=0; i<data.length; i++) {
      var nodename = data[i].mon_nodname
      if (nodenames.indexOf(nodename) >= 0) {
        // already done
        continue
      }
      nodenames.push(nodename)

      //input
      var input = $("<input type='checkbox' name='nodename' class='ocb'></input>")
      input.uniqueId()
      input.css({"vertical-align": "text-bottom"})
      if (o.options.display && (o.options.display.indexOf(nodename) >= 0)) {
        input.prop("checked", true)
      } else {
        input.prop("checked", false)
      }
      input.bind("change", function() {
        o.create_link()
      })

      // ocb label
      var label = $("<label></label>")
      label.attr("for", input.attr("id"))

      // title
      var title = $("<span></span>")
      title.addClass("icon hw16")
      title.css({"margin-left": "0.2em"})
      title.text(nodename)

      // container div
      var d = $("<div></div>")
      d.append(input)
      d.append(label)
      d.append(title)

      d.insertBefore(o.div.find("input[type=submit]"))
    }
    if (o.div.find("input[type=checkbox]:checked").length == 0) {
      o.div.find("input[type=checkbox]").first().each(function(){
        $(this).prop("checked", true)
        o.options.display = [$(this).siblings("span").text()]
      })
    }

    // form submit
    o.div.find("form").bind("submit", function(event) {
      event.preventDefault()
      o.options.display = []
      $(this).find("input:checked").each(function () {
        o.options.display.push($(this).siblings("span").text())
      })
      o.draw()
    })

    o.draw()
  })
}

function startup_draw(o) {
  var i = 0
  url = $(location).attr("origin") + "/init/topo/call/json/json_startup_data"
  if (o.viz.parents(".overlay").length == 0) {
      _height = $(window).height()-$(".header").outerHeight()-16
      o.viz.height(_height)
  }
  var data = {
    "svcnames": o.options.svcnames,
    "nodenames": o.options.display,
    "show_disabled": o.e_show_disabled.prop("checked")
  }
  $.getJSON(url, data, function(_data){
    var eid = o.viz[0]
    var options = {
      physics: {
        barnesHut: {
          //enabled: true,
          gravitationalConstant: -2500,
          centralGravity: 1,
          springLength: 95,
          springConstant: 0.1,
          damping: 0.5
        }
      },
      clickToUse: false,
      height: _height+'px',
      nodes: {
        size: 32,
        font: {
          face: "arial",
          size: 12
        }
      },
      edges: {
        font: {
          face: "arial",
          size: 12
        }
      }
    }
    var network = new vis.Network(eid, _data, options)
  })
}




