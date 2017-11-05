function topology(divid, options) {
	var o = {}
	o.divid = divid
	o.options = options
	o.div = $("#"+o.divid)
	o.link = {
		"fn": "topology",
		"title": "link.topology"
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": {
				"fn": o.link.fn,
				"parameters": o.options,
				"title": o.link.title
			}
		})

		// button
		o.button.attr("value", i18n.t("topology.redraw"))

		// toggle config
		o.toggle_config.bind("click", function() {
			o.config.slideDown()
			o.toggle_config.hide()
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
		})

		// form submit
		o.div.find("form").bind("submit", function(event) {
			o.update_options()
			event.preventDefault()
			o.config.empty()
			o.options.display = []
			$(this).find("input:checked").each(function () {
				o.options.display.push($(this).attr("name"))
			})
			o.draw()
		})
		o.draw()
	}

	o.update_options = function() {
		var display = []
		o.div.find("input[type=checkbox]").each(function() {
			if ($(this).is(":checked")) {
				display.push($(this).attr("name"))
			}
		})
		o.options.display = display
	}

	o.draw = function() {
		var i = 0
		url = $(location).attr("origin") + "/init/topo/call/json/json_topo_data"
		_height = $(window).height()
				-$(".header").outerHeight()
				-$(".footer").outerHeight()
				-o.e_title.outerHeight()
				-24
		o.viz.height(_height)
		$.getJSON(url, o.options, function(_data){
			var eid = o.viz[0]
			var blacklist = ["timestep", "damping", "minVelocity", "maxVelocity"]
			var options = {
				configure: {
					"container": o.config[0],
					"filter": function (option, path) {
						if (path.indexOf('physics') < 0) {
							return false
						}
						if (blacklist.indexOf(option) >= 0) {
							return false
						}
					}
				},
				physics: {
					barnesHut: {
						//enabled: true,
						gravitationalConstant: -3000,
						centralGravity: 0.7,
						avoidOverlap: 0.7,
						//springLength: 95,
						springConstant: 0.1,
						damping: 0.5
					}
				},
				"groups": {
					"sync": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c5", "color": osvc.colors.svc, "size": 50}},
					"app": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": osvc.colors.svc, "size": 50}},
					"container": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf135", "color": osvc.colors.svc, "size": 50}},
					"container.docker": {"shape": "image", "image": "/init/static/svg/docker-seagreen.svg"},
					"fs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf07c", "color": osvc.colors.svc, "size": 50}},
					"hb": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf21e", "color": osvc.colors.svc, "size": 50}},
					"share": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e0", "color": osvc.colors.svc, "size": 50}},
					"stonith": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1e2", "color": osvc.colors.svc, "size": 50}},
					"disk": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": osvc.colors.svc, "size": 50}},
					"disk.scsireserv": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf023", "color": osvc.colors.svc, "size": 50}},
					"disks": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": osvc.colors.disk, "size": 50}},
					"array": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf1c0", "color": osvc.colors.disk, "size": 100}},
					"ip": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf124", "color": osvc.colors.svc, "size": 50}},
					"sansw": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0ec", "color": osvc.colors.net, "size": 50}},
					"node": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf233", "color": osvc.colors.node, "size": 50}},
					"apps": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf069", "color": osvc.colors.app, "size": 100}},
					"countries": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": osvc.colors.node, "size": 110}},
					"flag-ad": {"shape": "image", "image": "/init/static/svg/flags/ad.svg"},
					"flag-ae": {"shape": "image", "image": "/init/static/svg/flags/ae.svg"},
					"flag-af": {"shape": "image", "image": "/init/static/svg/flags/af.svg"},
					"flag-ag": {"shape": "image", "image": "/init/static/svg/flags/ag.svg"},
					"flag-ai": {"shape": "image", "image": "/init/static/svg/flags/ai.svg"},
					"flag-al": {"shape": "image", "image": "/init/static/svg/flags/al.svg"},
					"flag-am": {"shape": "image", "image": "/init/static/svg/flags/am.svg"},
					"flag-ao": {"shape": "image", "image": "/init/static/svg/flags/ao.svg"},
					"flag-aq": {"shape": "image", "image": "/init/static/svg/flags/aq.svg"},
					"flag-ar": {"shape": "image", "image": "/init/static/svg/flags/ar.svg"},
					"flag-as": {"shape": "image", "image": "/init/static/svg/flags/as.svg"},
					"flag-at": {"shape": "image", "image": "/init/static/svg/flags/at.svg"},
					"flag-au": {"shape": "image", "image": "/init/static/svg/flags/au.svg"},
					"flag-aw": {"shape": "image", "image": "/init/static/svg/flags/aw.svg"},
					"flag-ax": {"shape": "image", "image": "/init/static/svg/flags/ax.svg"},
					"flag-az": {"shape": "image", "image": "/init/static/svg/flags/az.svg"},
					"flag-ba": {"shape": "image", "image": "/init/static/svg/flags/ba.svg"},
					"flag-bb": {"shape": "image", "image": "/init/static/svg/flags/bb.svg"},
					"flag-bd": {"shape": "image", "image": "/init/static/svg/flags/bd.svg"},
					"flag-be": {"shape": "image", "image": "/init/static/svg/flags/be.svg"},
					"flag-bf": {"shape": "image", "image": "/init/static/svg/flags/bf.svg"},
					"flag-bg": {"shape": "image", "image": "/init/static/svg/flags/bg.svg"},
					"flag-bh": {"shape": "image", "image": "/init/static/svg/flags/bh.svg"},
					"flag-bi": {"shape": "image", "image": "/init/static/svg/flags/bi.svg"},
					"flag-bj": {"shape": "image", "image": "/init/static/svg/flags/bj.svg"},
					"flag-bl": {"shape": "image", "image": "/init/static/svg/flags/bl.svg"},
					"flag-bm": {"shape": "image", "image": "/init/static/svg/flags/bm.svg"},
					"flag-bn": {"shape": "image", "image": "/init/static/svg/flags/bn.svg"},
					"flag-bo": {"shape": "image", "image": "/init/static/svg/flags/bo.svg"},
					"flag-bq": {"shape": "image", "image": "/init/static/svg/flags/bq.svg"},
					"flag-br": {"shape": "image", "image": "/init/static/svg/flags/br.svg"},
					"flag-bs": {"shape": "image", "image": "/init/static/svg/flags/bs.svg"},
					"flag-bt": {"shape": "image", "image": "/init/static/svg/flags/bt.svg"},
					"flag-bv": {"shape": "image", "image": "/init/static/svg/flags/bv.svg"},
					"flag-bw": {"shape": "image", "image": "/init/static/svg/flags/bw.svg"},
					"flag-by": {"shape": "image", "image": "/init/static/svg/flags/by.svg"},
					"flag-bz": {"shape": "image", "image": "/init/static/svg/flags/bz.svg"},
					"flag-ca": {"shape": "image", "image": "/init/static/svg/flags/ca.svg"},
					"flag-cc": {"shape": "image", "image": "/init/static/svg/flags/cc.svg"},
					"flag-cd": {"shape": "image", "image": "/init/static/svg/flags/cd.svg"},
					"flag-cf": {"shape": "image", "image": "/init/static/svg/flags/cf.svg"},
					"flag-cg": {"shape": "image", "image": "/init/static/svg/flags/cg.svg"},
					"flag-ch": {"shape": "image", "image": "/init/static/svg/flags/ch.svg"},
					"flag-ci": {"shape": "image", "image": "/init/static/svg/flags/ci.svg"},
					"flag-ck": {"shape": "image", "image": "/init/static/svg/flags/ck.svg"},
					"flag-cl": {"shape": "image", "image": "/init/static/svg/flags/cl.svg"},
					"flag-cm": {"shape": "image", "image": "/init/static/svg/flags/cm.svg"},
					"flag-cn": {"shape": "image", "image": "/init/static/svg/flags/cn.svg"},
					"flag-co": {"shape": "image", "image": "/init/static/svg/flags/co.svg"},
					"flag-cr": {"shape": "image", "image": "/init/static/svg/flags/cr.svg"},
					"flag-cu": {"shape": "image", "image": "/init/static/svg/flags/cu.svg"},
					"flag-cv": {"shape": "image", "image": "/init/static/svg/flags/cv.svg"},
					"flag-cw": {"shape": "image", "image": "/init/static/svg/flags/cw.svg"},
					"flag-cx": {"shape": "image", "image": "/init/static/svg/flags/cx.svg"},
					"flag-cy": {"shape": "image", "image": "/init/static/svg/flags/cy.svg"},
					"flag-cz": {"shape": "image", "image": "/init/static/svg/flags/cz.svg"},
					"flag-de": {"shape": "image", "image": "/init/static/svg/flags/de.svg"},
					"flag-dj": {"shape": "image", "image": "/init/static/svg/flags/dj.svg"},
					"flag-dk": {"shape": "image", "image": "/init/static/svg/flags/dk.svg"},
					"flag-dm": {"shape": "image", "image": "/init/static/svg/flags/dm.svg"},
					"flag-do": {"shape": "image", "image": "/init/static/svg/flags/do.svg"},
					"flag-dz": {"shape": "image", "image": "/init/static/svg/flags/dz.svg"},
					"flag-ec": {"shape": "image", "image": "/init/static/svg/flags/ec.svg"},
					"flag-ee": {"shape": "image", "image": "/init/static/svg/flags/ee.svg"},
					"flag-eg": {"shape": "image", "image": "/init/static/svg/flags/eg.svg"},
					"flag-eh": {"shape": "image", "image": "/init/static/svg/flags/eh.svg"},
					"flag-er": {"shape": "image", "image": "/init/static/svg/flags/er.svg"},
					"flag-es": {"shape": "image", "image": "/init/static/svg/flags/es.svg"},
					"flag-et": {"shape": "image", "image": "/init/static/svg/flags/et.svg"},
					"flag-eu": {"shape": "image", "image": "/init/static/svg/flags/eu.svg"},
					"flag-fi": {"shape": "image", "image": "/init/static/svg/flags/fi.svg"},
					"flag-fj": {"shape": "image", "image": "/init/static/svg/flags/fj.svg"},
					"flag-fk": {"shape": "image", "image": "/init/static/svg/flags/fk.svg"},
					"flag-fm": {"shape": "image", "image": "/init/static/svg/flags/fm.svg"},
					"flag-fo": {"shape": "image", "image": "/init/static/svg/flags/fo.svg"},
					"flag-fr": {"shape": "image", "image": "/init/static/svg/flags/fr.svg"},
					"flag-ga": {"shape": "image", "image": "/init/static/svg/flags/ga.svg"},
					"flag-gb-eng": {"shape": "image", "image": "/init/static/svg/flags/gb-eng.svg"},
					"flag-gb-sct": {"shape": "image", "image": "/init/static/svg/flags/gb-sct.svg"},
					"flag-gb": {"shape": "image", "image": "/init/static/svg/flags/gb.svg"},
					"flag-gb-wls": {"shape": "image", "image": "/init/static/svg/flags/gb-wls.svg"},
					"flag-gd": {"shape": "image", "image": "/init/static/svg/flags/gd.svg"},
					"flag-ge": {"shape": "image", "image": "/init/static/svg/flags/ge.svg"},
					"flag-gf": {"shape": "image", "image": "/init/static/svg/flags/gf.svg"},
					"flag-gg": {"shape": "image", "image": "/init/static/svg/flags/gg.svg"},
					"flag-gh": {"shape": "image", "image": "/init/static/svg/flags/gh.svg"},
					"flag-gi": {"shape": "image", "image": "/init/static/svg/flags/gi.svg"},
					"flag-gl": {"shape": "image", "image": "/init/static/svg/flags/gl.svg"},
					"flag-gm": {"shape": "image", "image": "/init/static/svg/flags/gm.svg"},
					"flag-gn": {"shape": "image", "image": "/init/static/svg/flags/gn.svg"},
					"flag-gp": {"shape": "image", "image": "/init/static/svg/flags/gp.svg"},
					"flag-gq": {"shape": "image", "image": "/init/static/svg/flags/gq.svg"},
					"flag-gr": {"shape": "image", "image": "/init/static/svg/flags/gr.svg"},
					"flag-gs": {"shape": "image", "image": "/init/static/svg/flags/gs.svg"},
					"flag-gt": {"shape": "image", "image": "/init/static/svg/flags/gt.svg"},
					"flag-gu": {"shape": "image", "image": "/init/static/svg/flags/gu.svg"},
					"flag-gw": {"shape": "image", "image": "/init/static/svg/flags/gw.svg"},
					"flag-gy": {"shape": "image", "image": "/init/static/svg/flags/gy.svg"},
					"flag-hk": {"shape": "image", "image": "/init/static/svg/flags/hk.svg"},
					"flag-hm": {"shape": "image", "image": "/init/static/svg/flags/hm.svg"},
					"flag-hn": {"shape": "image", "image": "/init/static/svg/flags/hn.svg"},
					"flag-hr": {"shape": "image", "image": "/init/static/svg/flags/hr.svg"},
					"flag-ht": {"shape": "image", "image": "/init/static/svg/flags/ht.svg"},
					"flag-hu": {"shape": "image", "image": "/init/static/svg/flags/hu.svg"},
					"flag-id": {"shape": "image", "image": "/init/static/svg/flags/id.svg"},
					"flag-ie": {"shape": "image", "image": "/init/static/svg/flags/ie.svg"},
					"flag-il": {"shape": "image", "image": "/init/static/svg/flags/il.svg"},
					"flag-im": {"shape": "image", "image": "/init/static/svg/flags/im.svg"},
					"flag-in": {"shape": "image", "image": "/init/static/svg/flags/in.svg"},
					"flag-io": {"shape": "image", "image": "/init/static/svg/flags/io.svg"},
					"flag-iq": {"shape": "image", "image": "/init/static/svg/flags/iq.svg"},
					"flag-ir": {"shape": "image", "image": "/init/static/svg/flags/ir.svg"},
					"flag-is": {"shape": "image", "image": "/init/static/svg/flags/is.svg"},
					"flag-it": {"shape": "image", "image": "/init/static/svg/flags/it.svg"},
					"flag-je": {"shape": "image", "image": "/init/static/svg/flags/je.svg"},
					"flag-jm": {"shape": "image", "image": "/init/static/svg/flags/jm.svg"},
					"flag-jo": {"shape": "image", "image": "/init/static/svg/flags/jo.svg"},
					"flag-jp": {"shape": "image", "image": "/init/static/svg/flags/jp.svg"},
					"flag-ke": {"shape": "image", "image": "/init/static/svg/flags/ke.svg"},
					"flag-kg": {"shape": "image", "image": "/init/static/svg/flags/kg.svg"},
					"flag-kh": {"shape": "image", "image": "/init/static/svg/flags/kh.svg"},
					"flag-ki": {"shape": "image", "image": "/init/static/svg/flags/ki.svg"},
					"flag-km": {"shape": "image", "image": "/init/static/svg/flags/km.svg"},
					"flag-kn": {"shape": "image", "image": "/init/static/svg/flags/kn.svg"},
					"flag-kp": {"shape": "image", "image": "/init/static/svg/flags/kp.svg"},
					"flag-kr": {"shape": "image", "image": "/init/static/svg/flags/kr.svg"},
					"flag-kw": {"shape": "image", "image": "/init/static/svg/flags/kw.svg"},
					"flag-ky": {"shape": "image", "image": "/init/static/svg/flags/ky.svg"},
					"flag-kz": {"shape": "image", "image": "/init/static/svg/flags/kz.svg"},
					"flag-la": {"shape": "image", "image": "/init/static/svg/flags/la.svg"},
					"flag-lb": {"shape": "image", "image": "/init/static/svg/flags/lb.svg"},
					"flag-lc": {"shape": "image", "image": "/init/static/svg/flags/lc.svg"},
					"flag-li": {"shape": "image", "image": "/init/static/svg/flags/li.svg"},
					"flag-lk": {"shape": "image", "image": "/init/static/svg/flags/lk.svg"},
					"flag-lr": {"shape": "image", "image": "/init/static/svg/flags/lr.svg"},
					"flag-ls": {"shape": "image", "image": "/init/static/svg/flags/ls.svg"},
					"flag-lt": {"shape": "image", "image": "/init/static/svg/flags/lt.svg"},
					"flag-lu": {"shape": "image", "image": "/init/static/svg/flags/lu.svg"},
					"flag-lv": {"shape": "image", "image": "/init/static/svg/flags/lv.svg"},
					"flag-ly": {"shape": "image", "image": "/init/static/svg/flags/ly.svg"},
					"flag-ma": {"shape": "image", "image": "/init/static/svg/flags/ma.svg"},
					"flag-mc": {"shape": "image", "image": "/init/static/svg/flags/mc.svg"},
					"flag-md": {"shape": "image", "image": "/init/static/svg/flags/md.svg"},
					"flag-me": {"shape": "image", "image": "/init/static/svg/flags/me.svg"},
					"flag-mf": {"shape": "image", "image": "/init/static/svg/flags/mf.svg"},
					"flag-mg": {"shape": "image", "image": "/init/static/svg/flags/mg.svg"},
					"flag-mh": {"shape": "image", "image": "/init/static/svg/flags/mh.svg"},
					"flag-mk": {"shape": "image", "image": "/init/static/svg/flags/mk.svg"},
					"flag-ml": {"shape": "image", "image": "/init/static/svg/flags/ml.svg"},
					"flag-mm": {"shape": "image", "image": "/init/static/svg/flags/mm.svg"},
					"flag-mn": {"shape": "image", "image": "/init/static/svg/flags/mn.svg"},
					"flag-mo": {"shape": "image", "image": "/init/static/svg/flags/mo.svg"},
					"flag-mp": {"shape": "image", "image": "/init/static/svg/flags/mp.svg"},
					"flag-mq": {"shape": "image", "image": "/init/static/svg/flags/mq.svg"},
					"flag-mr": {"shape": "image", "image": "/init/static/svg/flags/mr.svg"},
					"flag-ms": {"shape": "image", "image": "/init/static/svg/flags/ms.svg"},
					"flag-mt": {"shape": "image", "image": "/init/static/svg/flags/mt.svg"},
					"flag-mu": {"shape": "image", "image": "/init/static/svg/flags/mu.svg"},
					"flag-mv": {"shape": "image", "image": "/init/static/svg/flags/mv.svg"},
					"flag-mw": {"shape": "image", "image": "/init/static/svg/flags/mw.svg"},
					"flag-mx": {"shape": "image", "image": "/init/static/svg/flags/mx.svg"},
					"flag-my": {"shape": "image", "image": "/init/static/svg/flags/my.svg"},
					"flag-mz": {"shape": "image", "image": "/init/static/svg/flags/mz.svg"},
					"flag-na": {"shape": "image", "image": "/init/static/svg/flags/na.svg"},
					"flag-nc": {"shape": "image", "image": "/init/static/svg/flags/nc.svg"},
					"flag-ne": {"shape": "image", "image": "/init/static/svg/flags/ne.svg"},
					"flag-nf": {"shape": "image", "image": "/init/static/svg/flags/nf.svg"},
					"flag-ng": {"shape": "image", "image": "/init/static/svg/flags/ng.svg"},
					"flag-ni": {"shape": "image", "image": "/init/static/svg/flags/ni.svg"},
					"flag-nl": {"shape": "image", "image": "/init/static/svg/flags/nl.svg"},
					"flag-no": {"shape": "image", "image": "/init/static/svg/flags/no.svg"},
					"flag-np": {"shape": "image", "image": "/init/static/svg/flags/np.svg"},
					"flag-nr": {"shape": "image", "image": "/init/static/svg/flags/nr.svg"},
					"flag-nu": {"shape": "image", "image": "/init/static/svg/flags/nu.svg"},
					"flag-nz": {"shape": "image", "image": "/init/static/svg/flags/nz.svg"},
					"flag-om": {"shape": "image", "image": "/init/static/svg/flags/om.svg"},
					"flag-pa": {"shape": "image", "image": "/init/static/svg/flags/pa.svg"},
					"flag-pe": {"shape": "image", "image": "/init/static/svg/flags/pe.svg"},
					"flag-pf": {"shape": "image", "image": "/init/static/svg/flags/pf.svg"},
					"flag-pg": {"shape": "image", "image": "/init/static/svg/flags/pg.svg"},
					"flag-ph": {"shape": "image", "image": "/init/static/svg/flags/ph.svg"},
					"flag-pk": {"shape": "image", "image": "/init/static/svg/flags/pk.svg"},
					"flag-pl": {"shape": "image", "image": "/init/static/svg/flags/pl.svg"},
					"flag-pm": {"shape": "image", "image": "/init/static/svg/flags/pm.svg"},
					"flag-pn": {"shape": "image", "image": "/init/static/svg/flags/pn.svg"},
					"flag-pr": {"shape": "image", "image": "/init/static/svg/flags/pr.svg"},
					"flag-ps": {"shape": "image", "image": "/init/static/svg/flags/ps.svg"},
					"flag-pt": {"shape": "image", "image": "/init/static/svg/flags/pt.svg"},
					"flag-pw": {"shape": "image", "image": "/init/static/svg/flags/pw.svg"},
					"flag-py": {"shape": "image", "image": "/init/static/svg/flags/py.svg"},
					"flag-qa": {"shape": "image", "image": "/init/static/svg/flags/qa.svg"},
					"flag-re": {"shape": "image", "image": "/init/static/svg/flags/re.svg"},
					"flag-ro": {"shape": "image", "image": "/init/static/svg/flags/ro.svg"},
					"flag-rs": {"shape": "image", "image": "/init/static/svg/flags/rs.svg"},
					"flag-ru": {"shape": "image", "image": "/init/static/svg/flags/ru.svg"},
					"flag-rw": {"shape": "image", "image": "/init/static/svg/flags/rw.svg"},
					"flag-sa": {"shape": "image", "image": "/init/static/svg/flags/sa.svg"},
					"flag-sb": {"shape": "image", "image": "/init/static/svg/flags/sb.svg"},
					"flag-sc": {"shape": "image", "image": "/init/static/svg/flags/sc.svg"},
					"flag-sd": {"shape": "image", "image": "/init/static/svg/flags/sd.svg"},
					"flag-se": {"shape": "image", "image": "/init/static/svg/flags/se.svg"},
					"flag-sg": {"shape": "image", "image": "/init/static/svg/flags/sg.svg"},
					"flag-sh": {"shape": "image", "image": "/init/static/svg/flags/sh.svg"},
					"flag-si": {"shape": "image", "image": "/init/static/svg/flags/si.svg"},
					"flag-sj": {"shape": "image", "image": "/init/static/svg/flags/sj.svg"},
					"flag-sk": {"shape": "image", "image": "/init/static/svg/flags/sk.svg"},
					"flag-sl": {"shape": "image", "image": "/init/static/svg/flags/sl.svg"},
					"flag-sm": {"shape": "image", "image": "/init/static/svg/flags/sm.svg"},
					"flag-sn": {"shape": "image", "image": "/init/static/svg/flags/sn.svg"},
					"flag-so": {"shape": "image", "image": "/init/static/svg/flags/so.svg"},
					"flag-sr": {"shape": "image", "image": "/init/static/svg/flags/sr.svg"},
					"flag-ss": {"shape": "image", "image": "/init/static/svg/flags/ss.svg"},
					"flag-st": {"shape": "image", "image": "/init/static/svg/flags/st.svg"},
					"flag-sv": {"shape": "image", "image": "/init/static/svg/flags/sv.svg"},
					"flag-sx": {"shape": "image", "image": "/init/static/svg/flags/sx.svg"},
					"flag-sy": {"shape": "image", "image": "/init/static/svg/flags/sy.svg"},
					"flag-sz": {"shape": "image", "image": "/init/static/svg/flags/sz.svg"},
					"flag-tc": {"shape": "image", "image": "/init/static/svg/flags/tc.svg"},
					"flag-td": {"shape": "image", "image": "/init/static/svg/flags/td.svg"},
					"flag-tf": {"shape": "image", "image": "/init/static/svg/flags/tf.svg"},
					"flag-tg": {"shape": "image", "image": "/init/static/svg/flags/tg.svg"},
					"flag-th": {"shape": "image", "image": "/init/static/svg/flags/th.svg"},
					"flag-tj": {"shape": "image", "image": "/init/static/svg/flags/tj.svg"},
					"flag-tk": {"shape": "image", "image": "/init/static/svg/flags/tk.svg"},
					"flag-tl": {"shape": "image", "image": "/init/static/svg/flags/tl.svg"},
					"flag-tm": {"shape": "image", "image": "/init/static/svg/flags/tm.svg"},
					"flag-tn": {"shape": "image", "image": "/init/static/svg/flags/tn.svg"},
					"flag-to": {"shape": "image", "image": "/init/static/svg/flags/to.svg"},
					"flag-tr": {"shape": "image", "image": "/init/static/svg/flags/tr.svg"},
					"flag-tt": {"shape": "image", "image": "/init/static/svg/flags/tt.svg"},
					"flag-tv": {"shape": "image", "image": "/init/static/svg/flags/tv.svg"},
					"flag-tw": {"shape": "image", "image": "/init/static/svg/flags/tw.svg"},
					"flag-tz": {"shape": "image", "image": "/init/static/svg/flags/tz.svg"},
					"flag-ua": {"shape": "image", "image": "/init/static/svg/flags/ua.svg"},
					"flag-ug": {"shape": "image", "image": "/init/static/svg/flags/ug.svg"},
					"flag-um": {"shape": "image", "image": "/init/static/svg/flags/um.svg"},
					"flag-un": {"shape": "image", "image": "/init/static/svg/flags/un.svg"},
					"flag-us": {"shape": "image", "image": "/init/static/svg/flags/us.svg"},
					"flag-uy": {"shape": "image", "image": "/init/static/svg/flags/uy.svg"},
					"flag-uz": {"shape": "image", "image": "/init/static/svg/flags/uz.svg"},
					"flag-va": {"shape": "image", "image": "/init/static/svg/flags/va.svg"},
					"flag-vc": {"shape": "image", "image": "/init/static/svg/flags/vc.svg"},
					"flag-ve": {"shape": "image", "image": "/init/static/svg/flags/ve.svg"},
					"flag-vg": {"shape": "image", "image": "/init/static/svg/flags/vg.svg"},
					"flag-vi": {"shape": "image", "image": "/init/static/svg/flags/vi.svg"},
					"flag-vn": {"shape": "image", "image": "/init/static/svg/flags/vn.svg"},
					"flag-vu": {"shape": "image", "image": "/init/static/svg/flags/vu.svg"},
					"flag-wf": {"shape": "image", "image": "/init/static/svg/flags/wf.svg"},
					"flag-ws": {"shape": "image", "image": "/init/static/svg/flags/ws.svg"},
					"flag-ye": {"shape": "image", "image": "/init/static/svg/flags/ye.svg"},
					"flag-yt": {"shape": "image", "image": "/init/static/svg/flags/yt.svg"},
					"flag-za": {"shape": "image", "image": "/init/static/svg/flags/za.svg"},
					"flag-zm": {"shape": "image", "image": "/init/static/svg/flags/zm.svg"},
					"flag-zw": {"shape": "image", "image": "/init/static/svg/flags/zw.svg"},
					"flag-zz": {"shape": "image", "image": "/init/static/svg/flags/zz.svg"},
					"cities": {"shape": "image", "image": "/init/static/svg/city.svg", "size": 50},
					"buildings": {"shape": "image", "image": "/init/static/svg/building.svg", "size": 45},
					"rooms": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": osvc.colors.node, "size": 80}},
					"racks": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": osvc.colors.node, "size": 70}},
					"enclosures": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf041", "color": osvc.colors.node, "size": 60}},
					"hvvdcs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": osvc.colors.node, "size": 90}},
					"hvpools": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": osvc.colors.node, "size": 70}},
					"hvs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf0c2", "color": osvc.colors.node, "size": 50}},
					"envs": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf24d", "color": osvc.colors.svc, "size": 100}},
					"resource": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf292", "color": osvc.colors.svc, "size": 50}},
					"svc_undef": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "gray", "size": 50}},
					"svc_na": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "gray", "size": 50}},
					"svc_warn": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "orange", "size": 50}},
					"svc_up": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "seagreen", "size": 50}},
					"svc_down": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "darkred", "size": 50}},
					"svc_stdby_down": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "lightred", "size": 50}},
					"svc_stdby_up": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": "lightgreen", "size": 50}},
					"svc": {"shape": "icon", "icon": {"face": "FontAwesome", "code": "\uf111", "color": osvc.colors.svc, "size": 50}}
				},
				clickToUse: true,
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
			require(["vis"], function(vis) {
				var network = new vis.Network(eid, _data, options)
				network.on("click", function(params) {
					if (params.nodes.length == 0) {
						return
					}
					var node = _data.nodes[params.nodes[0]]
					if (node.node_id) {
						osvc.flash.show({
							id: "node-"+node.node_id,
							text: node.label.split(/\s/)[0],
							cl: "icon node16",
							bgcolor: osvc.colors.node,
							fn: function(id){node_tabs(id, {"node_id": node.node_id})}
						})
					} else
					if (node.svc_id) {
						osvc.flash.show({
							id: "svc-"+node.svc_id,
							text: node.label.split(/\s/)[0],
							cl: "icon svc",
							bgcolor: osvc.colors.svc,
							fn: function(id){service_tabs(id, {"svc_id": node.svc_id})}
						})
					}
				})
			})
		})
	}

	o.div.load('/init/static/views/topology.html?v='+osvc.code_rev, function() {
		o.div.i18n()
		o.viz = o.div.find("#viz")
		o.button = o.div.find("button[name=submit]")
		o.toggle_config = o.div.find("[name=configure_toggle]")
		o.config = o.div.find("[name=configure]")
		o.e_title = o.div.find("[name=title]")
		o.init()
	})
}


