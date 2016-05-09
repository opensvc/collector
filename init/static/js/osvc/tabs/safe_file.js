//
// form
//
function safe_file_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options

	o.load(function() {
		var title = o.options.uuid
		o.closetab.children("p").text(title)

		// tab properties
		i = o.register_tab({
			"title": "safe_file_tabs.properties",
			"title_class": "icon safe16"
		})
		o.tabs[i].callback = function(divid) {
			safe_file_properties(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})
	return o
}

function safe_file_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_name = o.div.find("#name")
		o.info_uuid = o.div.find("#uuid")
		o.info_md5 = o.div.find("#md5")
		o.info_size = o.div.find("#size")
		o.info_uploader = o.div.find("#uploader")
		o.info_uploaded_from = o.div.find("#uploaded_from")
		o.info_uploaded_date = o.div.find("#uploaded_date")
		o.info_publications = o.div.find("#publications")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("/safe/%1", [o.options.uuid], "", function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_name.html(data.name)
		o.info_uuid.html(data.uuid)
		o.info_md5.html(data.md5)
		o.info_size.html(fancy_size_b(data.size))
		o.info_uploader.html(data.uploader)
		o.info_uploaded_from.html(data.uploaded_from)
		o.info_uploaded_date.html(data.uploaded_date)

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["SafeUploader", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/safe/%1", [o.options.uuid], "", data, callback, error_callback)
			}
		})
		safe_file_publications({
			"tid": o.info_publications,
			"uuid": data.uuid
		})
		safe_file_responsibles({
			"tid": o.info_responsibles,
			"uuid": data.uuid
		})

	}

	o.div.load("/init/static/views/safe_file_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


