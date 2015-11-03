//
// topo
//
function topology(divid, options) {
  var o = {}
  o.divid = divid
  o.options = options
  o.div = $("#"+o.divid)

  o.init = function() {
    return topo_init(o)
  }
  o.draw = function() {
    return topo_draw(o)
  }
  o.create_link = function(){
    return topo_create_link(this)
  }

  o.div.load('/init/static/views/topology.html', "", function() {
    o.div.i18n();
    o.viz = o.div.find("#viz")
    o.link = o.div.find(".link16")
    o.link_text = o.link.children()
    o.init()
  })
}

function topo_create_link(o) {
  var display = []
  o.div.find("input[type=checkbox]").each(function() {
    if ($(this).is(":checked")) {
      display.push($(this).attr("name"))
    }
  })
  o.options.display = display
  url = $(location).attr("origin");
  url += "/init/topo/topo?"
  var l = []
  if (o.options.nodenames) {
    l.push("nodenames="+encodeURIComponent(o.options.nodenames.join(",")))
  }
  if (o.options.svcnames) {
    l.push("svcnames="+encodeURIComponent(o.options.svcnames.join(",")))
  }
  if (o.options.display) {
    l.push("display="+encodeURIComponent(o.options.display.join(",")))
  }
  url += l.join("&");
  o.link_text.empty().html(url);
  o.link_text.autogrow({vertical: true, horizontal: true});
}

function topo_init(o) {
  // link
  o.link_text.bind("click", function() {
    window.open(o.link_text.val(), '_blank')
  })
  o.link.bind("click", function() {
    o.create_link()
    o.link_text.slideToggle().select()
  })

  // set checkboxes
  o.div.find("input[type=checkbox]").each(function() {
    var name = $(this).attr("name")
    $(this).uniqueId()
    $(this).next().attr("for", $(this).attr("id"))
    $(this).addClass("ocb")
    if (o.options.display.indexOf(name) >= 0) {
      $(this).prop("checked", true)
    } else {
      $(this).prop("checked", false)
    }
    $(this).bind("change", function() {
      o.create_link()
    })
  })

  // form submit
  o.div.find("form").bind("submit", function(event) {
    event.preventDefault()
    o.options.display = []
    $(this).find("input:checked").each(function () {
      o.options.display.push($(this).attr("name"))
    })
    o.draw()
  })
  o.draw()
}

function topo_draw(o) {
  var i = 0
  url = $(location).attr("origin") + "/init/topo/call/json/json_topo_data"
  if (o.viz.parents(".overlay").length == 0) {
      _height = $(window).height()-$(".header").outerHeight()-16
      o.viz.height(_height)
  }
  $.getJSON(url, o.options, function(_data){
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
