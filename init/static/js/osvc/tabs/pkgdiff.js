function pkgdiff(divid, options) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  o.options = options

  o.draw = function draw(data) {
    return pkgdiff_draw(o, data)
  }

  spinner_add(o.div, i18n.t("api.loading"))
  services_osvcgetrest("R_PACKAGES_DIFF", "", o.options, function(jd) {
    spinner_add(o.div, i18n.t("api.formatting"))
    if (jd.error) {
      o.div.html(services_error_fmt(jd))
      return
    }
    o.draw(jd)
  },
  function(xhr, stat, error) {
    o.div.html(services_ajax_error_fmt(xhr, stat, error))
  })
  return o
}

function pkgdiff_draw(o, data) {
  if (data.data.length == 0) {
    o.div.html(i18n.t("pkgdiff.no_diff"))
    return
  }

  var t = $("<table></table>")

  // table header
  var header1 = $("<tr></tr>")
  header1.append($("<th></th>"))
  header1.append($("<th></th>"))
  header1.append($("<th></th>"))
  header1.append($("<th style='text-align:center' colspan="+data.meta.nodenames.length+" data-i18n='pkgdiff.nodes'></th>"))
  t.append(header1)

  var header2 = $("<tr></tr>")
  header2.append($("<th data-i18n='pkgdiff.package'></th>"))
  header2.append($("<th data-i18n='pkgdiff.arch'></th>"))
  header2.append($("<th data-i18n='pkgdiff.type'></th>"))
  for (var i=0; i<data.meta.nodenames.length; i++) {
    header2.append($("<th>"+data.meta.nodenames[i]+"</th>"))
  }
  t.append(header2)

  var packages = {}
  var keys = []
  for (var i=0; i<data.data.length; i++) {
    var p = data.data[i]
    var key = p.pkg_name + "." + p.pkg_arch
    if (!(key in packages)) {
      packages[key] = {
        "pkg_name": p.pkg_name,
        "pkg_arch": p.pkg_arch,
        "pkg_type": p.pkg_type,
        "pkg_version": {}
      }
      keys.push(key)
    }
    packages[key].pkg_version[p.pkg_nodename] = p.pkg_version
  }

  for (var i=0; i<keys.length; i++) {
    var key = keys[i]
    var p = packages[key]
    var l = $("<tr></tr>")
    if (i%2 == 0) {
      l.addClass("cell1")
    }
    l.append($("<td>"+p.pkg_name+"</td>"))
    l.append($("<td>"+p.pkg_arch+"</td>"))
    l.append($("<td>"+p.pkg_type+"</td>"))
    for (var j=0; j<data.meta.nodenames.length; j++) {
      var nodename = data.meta.nodenames[j]
      if (nodename in p.pkg_version) {
        l.append($("<td style='border-left:dotted 1px'>"+p.pkg_version[nodename]+"</td>"))
      } else {
        l.append($("<td style='border-left:dotted 1px'></td>"))
      }
    }
    t.append(l)
  }
  o.div.html(t)
  o.div.i18n()
}

function svc_pkgdiff(divid, options) {
  o = {}
  o.div = $("#"+divid)
  o.options = options

  var t
  var d
 
  o.div.empty()

  t = $("<h3 data-i18n='pkgdiff.title_cluster'></h3>")
  d = $("<div></div>")
  d.uniqueId()
  o.div.append(t)
  o.div.append(d)
  pkgdiff(d.attr("id"), {"svcnames": o.options.svcnames})

  t = $("<h3 data-i18n='pkgdiff.title_encap'></h3>")
  d = $("<div></div>")
  d.uniqueId()
  o.div.append(t)
  o.div.append(d)
  pkgdiff(d.attr("id"), {"svcnames": o.options.svcnames, "encap": "true"})
  o.div.i18n()
  return o
}
