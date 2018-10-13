var plots_colors = [
	"#4bb2c5",
	"#4bb2c5",
	"#EAA228",
	"#EAA228",
	"#c5b47f",
	"#c5b47f",
	"#579575",
	"#579575",
	"#839557",
	"#839557",
	"#958c12",
	"#958c12",
	"#953579",
	"#953579",
	"#4b5de4",
	"#4b5de4",
	"#d8b83f",
	"#d8b83f",
	"#ff5800",
	"#ff5800",
	"#0085cc",
	"#0085cc",
	"#c747a3",
	"#c747a3",
	"#cddf54",
	"#cddf54",
	"#FBD178",
	"#FBD178",
	"#26B4E3",
	"#26B4E3",
	"#bd70c7",
	"#bd70c7"
]
var hlc_defaults = {
	hlc: true,
	tickLength: 10,
	closeColor: plots_colors[2],
	lineWidth: 3
}
var chart_defaults = {
	cursor: {
		clickReset: true,
		zoom: true,
		show: true,
		showTooltip: false
	},
	grid: {
		gridLineColor: "#efefef",
		background: "transparent",
		borderWidth: 0,
		shadowOffset: 0,
		shadowWidth: 0
	},
	gridPadding: {
		right: 90
	},
	legend: {
		show: true,
		location: "e",
		placement: "outside"
	}
}

function comp_status_plot(url, id) {
  require(["jqplot"], function(){
    if (!$("#"+id).is(":visible")) {
        return
    }
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	$.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                drawGridlines: false,
                borderWidth: 0,
                shadow: false,
                background: 'rgba(0,0,0,0)'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadow: false
            },
	    series: [
                {
                    label: 'ok',
                    color: 'lightgreen'
                },
                {
                    label: 'errors',
                    color: 'red'
                },
                {
                    label: 'n/a',
                    color: 'gray'
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {
                        formatString:'%s',
                        showMark:false,
                        showGridline: false,
                        fontSize:'7pt'
                    },
                    ticks: data[0],
                    padMax: 0
		}, 
		yaxis: {
		    min: 0, 
		    tickOptions:{
                        showLabel: false,
                        size: 0,
                        formatString:'%d'
                    }
		}
	    }
	});
    })
  })
}

function plot_height(id, data) {
    h = Math.max(100+data.length*30, 200)+'px'
    $("#"+id).height(h)
}

function plot_width_x(id, data) {
    h = Math.max(100+data.length*40, 200)+'px'
    $("#"+id).width(h)
}

function plot_width(id, data) {
    w = 12
    for (i=0; i<data.length; i++) {
        w = Math.max(w, data[i].length)
    }
    w -= 12
    iw = $('#'+id).width()
    $('#'+id).width(iw+w*5+'px')
}

function stats_avg_cpu_for_nodes(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id, data[0])
	p = $.jqplot(id, data[1], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average cpu utilization'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'usr'},
                {label: 'nice'},
                {label: 'sys'},
                {label: 'iowait'},
                {label: 'steal'},
                {label: 'irq'},
                {label: 'soft'},
                {label: 'guest'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString:'%.2f %%', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    });
  })
}
function stats_avg_swp_for_nodes(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "MB")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height(id, data[0])
	p = $.jqplot(id, data[1], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average swap utilization'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'free'},
                {label: 'used'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit'], angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    });
  })
}
function stats_avg_mem_for_nodes(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "MB")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height(id, data[0])
	p = $.jqplot(id, data[1], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average memory utilization'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'free'},
                {label: 'cache'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit'], angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    });
  })
}
function stats_avg_block_for_nodes(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }

        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0]+data[1][1][i][0])
        }
        d = best_unit_mb(max, "")
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
            data[1][1][i][0] /= d['div']
        }

        plot_height(id+'_tps', data[0])
	p = $.jqplot(id+'_tps', [data[1][0], data[1][1]], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average io/s'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit']+'io/s', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_tps'), p)

        max = 0
        for (i=0; i<data[1][2].length; i++) {
            max = Math.max(max, data[1][2][i][0]+data[1][3][i][0])
        }
        d = best_unit_mb(max, "KB")
        for (i=0; i<data[1][2].length; i++) {
            data[1][2][i][0] /= d['div']
            data[1][3][i][0] /= d['div']
        }

        plot_height(id+'_bps', data[0])
	p = $.jqplot(id+'_bps', [data[1][2], data[1][3]], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average block devices bandwidth'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
		    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s', angle: -70, fontSize: "1em"}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_bps'), p)
    });
  })
}
function stats_disk_for_svc(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }

        max = 0
        for (i=0; i<data[1][0].length; i++) {
            max = Math.max(max, data[1][0][i][0])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1][0].length; i++) {
            data[1][0][i][0] /= d['div']
        }

        plot_height(id, data[0])
	p = $.jqplot(id, [data[1][0]], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Disk size per service'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:10
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'SAN disk size'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    });
  })
}
function stats_avg_proc_for_nodes(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id+'_runq_sz', data[0])
	p = $.jqplot(id+'_runq_sz', [data[1][0]], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average run queue size'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'runq sz'}
            ],
	    axes: {
		xaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_runq_sz'), p)

        plot_height(id+'_plist_sz', data[0])
	p = $.jqplot(id+'_plist_sz', [data[1][1]], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Average process list size'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                rendererOptions: {
                    barDirection:'horizontal',
                    barPadding: 6,
                    barMargin:15
                }, 
                shadowAngle: 135
            },
	    series: [
                {label: 'plist sz'}
            ],
	    axes: {
		xaxis: {
		    min: 0, 
		    tickOptions:{formatString:'%i'}
		},
		yaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    ticks: data[0]
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_plist_sz'), p)
    });
  })
}
function dash_history(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, [data], $.extend({}, chart_defaults, {
            stackSeries: true,
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                rendererOptions: {
                    barDirection:'vertical',
                    barPadding: 6,
                    barMargin:10
                },
                shadowAngle: 135
            },
            series: [
                { label: 'alerts' },
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString:'%i'}
                }
            }
        }))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function comp_history(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, data, $.extend({}, chart_defaults, {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                { label: 'ok' },
                { label: 'nok' },
                { label: 'na' }
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString:'%i'}
                }
            }
        }))
        _jqplot_extra($('#'+id), p)
    })
  })
}



function set_has_data(e) {
	e.children().empty()
	e.children(".ui-resizable-handle").remove()
	e.children(".perf_plot").show()
	e.children("[name=nodata]").remove()
}

function set_no_data(e) {
	e.children().empty()
	e.children(".ui-resizable-handle").remove()
	e.children(".perf_plot").hide()
	e.children("[name=nodata]").remove()
	e.append("<div name='nodata' class='icon db16 grayed' style='padding:1em'>no data</div>")
}

function stats_svc_cpu(url, id) {
    stats_svc(url, id, "cpu usage", "%")
}
function stats_svc_mem(url, id) {
    stats_svc(url, id, "mem usage", "%")
}
function stats_svc_nproc(url, id) {
    stats_svc(url, id, "nproc", "")
}
function stats_svc_rss(url, id) {
    stats_svc(url, id, "rss")
}
function stats_svc_swap(url, id) {
    stats_svc(url, id, "swap")
}
function stats_svc_pg(url, id) {
    stats_svc(url, id, "paging")
}
function stats_svc_avgpg(url, id) {
    stats_svc(url, id, "average paging")
}
function stats_svc_at(url, id) {
    stats_svc(url, id, "at")
}
function stats_svc_avgat(url, id) {
    stats_svc(url, id, "average at")
}
function stats_svc_cap(url, id) {
    stats_svc(url, id, "mem cap")
}
function stats_svc_cap_cpu(url, id) {
    stats_svc(url, id, "cpu cap", "")
}
function stats_svc(url, id, title, unit) {
  require(["jqplot"], function(){
    if(typeof(unit)==='undefined') {
        unit = "MB"
    }

    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data.length < 2) { return }
        if (data[1].length == 0) { return }
        if (data[1][0].length < 2) { return }
        svcnames = data[0]
        series = []
        for (i=0; i<svcnames.length; i++) {
            series.push({ label: svcnames[i] })
        }

        max = 0

        for (i=0; i<data[1].length; i++) {
          for (j=0; j<data[1][i].length; j++) {
            max = Math.max(max, data[1][i][j][1])
          }
        }
        d = best_unit_mb(max, unit)
        for (i=0; i<data[1].length; i++) {
          for (j=0; j<data[1][i].length; j++) {
            data[1][i][j][1] /= d['div']
          }
        }

	p = $.jqplot(id, data[1], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: title
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[2],
                    max: data[3],
		    renderer: $.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    });
  })
}
function mangle_data(data, keep) {
	function get_steps_list(data) {
		for (var i=0; i<data.length; i++) {
			if (data[i].length > 0) {
				return data[i].length
			}
		}
		return 1
	}
	function get_steps_dict(data) {
		for (var i in data) {
			if (data[i].length > 0) {
				return data[i].length
			}
		}
		return 1
	}
	function mangle_list(data, n) {
		if (data.length == 0) {
			for (var j=0; j<n ; j++) {
				data.push([null, null])
			}
			return data
		}
		for (var j=0; j<data.length; j++) {
			data[j][0] = osvc_date_from_collector(data[j][0])
		}
		return data
	}
	if (data instanceof Array) {
		n = get_steps_list(data)
		for (var i=0; i<data.length; i++) {
			data[i] = mangle_list(data[i], n)
		}
	} else {
		n = get_steps_dict(data)
		for (var i=0; i<keep.length; i++) {
			data[keep[i]] = mangle_list(data[keep[i]], n)
		}
	}
	return data
}
function prepare_data(options) {
        var data = options.data

	//
	var keep = []
	var series = []
	for (candidate in options.candidates) {
		if (candidate in data) {
			keep.push(candidate)
			series.push(options.candidates[candidate])
		}
	}

	// fix dates tz
        var data = mangle_data(data, keep)

	// extra data mangling
	if (typeof(options.mangler)!=='undefined') {
		data = options.mangler(data, keep)
	}
	// apply scaling to best unit
	var d = {}
	if (options.scale) {
		if (typeof(options.factor) === 'undefined') {
			options.factor = 1
		}
		var max = 0
		for (i=0; i<data[keep[0]].length; i++) {
			var val = 0
			for (var j=0; j<keep.length; j++) {
				val += data[keep[j]][i][1]
			}
			max = Math.max(max, val/options.factor)
		}
		d = best_unit_mb(max, options.iunit)
		for (var i=0; i<keep.length; i++) {
			for (var j=0; j<data[keep[0]].length; j++) {
				data[keep[i]][j][1] /= d['div']*options.factor
			}
		}
	}

	// get time axis min and max
	xmin = data[keep[0]][0][0]
	xmax = data[keep[0]][data[keep[0]].length-1][0]

	// filter out not kept metrics
	var _data = []
	for (var i=0; i<keep.length; i++) {
		_data.push(data[keep[i]])
	}
	return {
		series: series,
		data: _data,
		xmin: xmin,
		xmax: xmax,
		fmt: d.fmt,
		unit: d.unit
	}
}
function stats_cpu(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (is_dict_empty(data)) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
	var candidates = {
		"usr": {
			"label": "usr"
		},
		"nice": {
			"label": "nice"
		},
		"sys": {
			"label": "sys"
		},
		"iowait": {
			"label": "iowait"
		},
		"steal": {
			"label": "steal"
		},
		"irq": {
			"label": "irq"
		},
		"soft": {
			"label": "soft"
		},
		"guest": {
			"label": "guest"
		},
		"idle": {
			"label": "total",
			"color": "#aaaaaa",
			"shadow": false,
			"fill": false
			//"fillAlpha": 0.1
		}
	}

	_data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})

	p = $.jqplot(id+"_u", _data.data, $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Cpu usage'
            },
	    seriesDefaults: {
                markerOptions: {size: 2},
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                breakOnNull: true,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_u'), p)
    });
  })
}
function stats_mem(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (is_dict_empty(data)) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))

	var candidates = {
		"kbmemused": {
			"label": "used"
		},
		"kbbuffers": {
			"label": "used, buffer"
		},
		"kbcached": {
			"label": "used, cache"
		},
		"kbmemsys": {
			"label": "used, sys"
		},
		"kbmemfree": {
			"label": "free"
		}
	}
	function mangler(data, keep) {
		var in_memused = ["kbmemsys", "kbcached", "kbbuffers"]
		var keep_in_memused = []

		for (var i=0; i<in_memused.length; i++) {
			var candidate = in_memused[i]
			if (keep.indexOf(candidate) >= 0) {
				keep_in_memused.push(candidate)
			}
		}
		for (i=0; i<data["kbmemused"].length; i++) {
			for (var j=0; j<keep_in_memused.length; j++) {
				data["kbmemused"][i][1] -= data[keep_in_memused[j]][i][1]
			}
		}
		return data
	}

	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: true,
		factor: 1024,
		mangler: mangler
	})

	p = $.jqplot(id+'_u', _data.data, $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Memory usage'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: _data.fmt+' '+_data.unit}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_u'), p)

	var candidates = {
		"pct_memused": {
			"label": "used/mem"
		},
		"pct_commit": {
			"label": "promised/(mem+swap)"
		},
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})
	p = $.jqplot(id+'_pct', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Memory usage %'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pct'), p)

    });
  })
}
function stats_swap(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (is_dict_empty(data)) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
	var candidates = {
		"kbswpused": {
			"label": "used"
		},
		"kbswpcad": {
			"label": "used, cache"
		},
		"kbswpfree": {
			"label": "free"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: true,
		factor: 1024
	})

	p = $.jqplot(id+'_u', _data.data, $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Swap usage'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: _data.fmt+' '+_data.unit}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_u'), p)

	var candidates = {
		"pct_swpused": {
			"label": "used/total"
		},
		"pct_swpcad": {
			"label": "cached/used"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})

	p = $.jqplot(id+'_pct', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Swap usage percent'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pct'), p)
    })
  })
}
function stats_proc(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (is_dict_empty(data)) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
	var candidates = {
		"runq_sz": {
			"label": "runq_sz"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})
	p = $.jqplot(id+'_runq_sz', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Run queue size'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_runq_sz'), p)

	var candidates = {
		"plist_sz": {
			"label": "plist_sz"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})
	p = $.jqplot(id+'_plist_sz', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Process list size'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_plist_sz'), p)

	var candidates = {
		"ldavg_1": {
			"label": "loadavg 1"
		},
		"ldavg_5": {
			"label": "loadavg 5"
		},
		"ldavg_15": {
			"label": "loadavg 15"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: false
	})
	p = $.jqplot(id+'_loadavg', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Load average'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_loadavg'), p)
    });
  })
}

function stats_block(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (is_dict_empty(data)) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
	var candidates = {
		"rtps": {
			"label": "read"
		},
		"wtps": {
			"label": "write"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: true,
		iunit: ""
	})
	p = $.jqplot(id+'_tps', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Block device transactions'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: _data.fmt+' '+_data.unit+'io/s'},
		    min: 0
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_tps'), p)

	var candidates = {
		"rbps": {
			"label": "read"
		},
		"wbps": {
			"label": "write"
		}
	}
	var _data = prepare_data({
		candidates: candidates,
		data: data,
		scale: true,
		iunit: "KB"
	})
	p = $.jqplot(id+'_bps', _data.data, $.extend({}, chart_defaults, {
            title: {
                text: 'Block device bandwidth'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: _data.series,
	    axes: {
		xaxis: {
		    min: _data.xmin,
		    max: _data.xmax,
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: _data.fmt+' '+_data.unit+'/s'},
		    min: 0
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_bps'), p)
    })
  })
}
function stats_trend_mem(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], $.extend({}, chart_defaults, {
            title: {
                text: 'Memory usage trend<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer, 
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'mem usage KB' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {formatString:'%s'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function stats_trend_cpu(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], $.extend({}, chart_defaults, {
            title: {
                text: 'Cpu usage trend<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer, 
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'cpu usage %' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
		    tickOptions: {formatString:'%s'}
		}, 
		yaxis: {
		    min: 0,
		    max: 100,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}

function stats_blockdev(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        if (_data["avg"][0].length == 0) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
        _data.begin = osvc_date_from_collector(_data.begin)
        _data.end = osvc_date_from_collector(_data.end)
        data = _data['time']['secps']['data']
        data = mangle_data(data)
        labels = _data['time']['secps']['labels']
        max_secps = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_secps = Math.max(max_secps, Math.abs(data[i][j][1]))
          }
        }
        d_secps = best_unit_mb(max_secps, '')
        max_secps /= d_secps['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_secps['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_secps_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Block device bandwidth'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_secps['fmt']+' '+d_secps['unit']+'sect/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_secps_time'), p)

        data = _data['time']['pct_util']['data']
        data = mangle_data(data)
        labels = _data['time']['pct_util']['labels']
        max_pct_util = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_pct_util = Math.max(max_pct_util, Math.abs(data[i][j][1]))
          }
        }
        d_pct_util = best_unit_mb(max_pct_util, '')
        max_pct_util /= d_pct_util['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_pct_util['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_pct_util_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Block device utilization'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_pct_util['fmt']+' '+d_pct_util['unit']+'%'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pct_util_time'), p)

        data = _data['time']['tps']['data']
        data = mangle_data(data)
        labels = _data['time']['tps']['labels']
        max_tps = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_tps = Math.max(max_tps, Math.abs(data[i][j][1]))
          }
        }
        d_tps = best_unit_mb(max_tps, '')
        max_tps /= d_tps['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_tps['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_tps_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Block device transactions'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_tps['fmt']+' '+d_tps['unit']+'io/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_tps_time'), p)

        data = _data['time']['await']['data']
        data = mangle_data(data)
        labels = _data['time']['await']['labels']
        max_await = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_await = Math.max(max_await, Math.abs(data[i][j][1]))
          }
        }
        d_await = best_unit_mb(max_await, 'ms')
        max_await /= d_await['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_await['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_await_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Block device wait time'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_await['fmt']+' '+d_await['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_await_time'), p)

        data = _data['time']['svctm']['data']
        data = mangle_data(data)
        labels = _data['time']['svctm']['labels']
        max_svctm = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_svctm = Math.max(max_svctm, Math.abs(data[i][j][1]))
          }
        }
        d_svctm = best_unit_mb(max_svctm, 'ms')
        max_svctm /= d_svctm['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_svctm['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_svctm_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Block device service time'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_svctm['fmt']+' '+d_svctm['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_svctm_time'), p)

        data = _data['time']['avgrq_sz']['data']
        data = mangle_data(data)
        labels = _data['time']['avgrq_sz']['labels']
        max_avgrq_sz = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max_avgrq_sz = Math.max(max_avgrq_sz, Math.abs(data[i][j][1]))
          }
        }
        d_avgrq_sz = best_unit_mb(max_avgrq_sz, '')
        max_avgrq_sz /= d_avgrq_sz['div']
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d_avgrq_sz['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_avgrq_sz_time', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Block device request size'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: _data['begin'],
                    max: _data['end'],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    min: 0,
                    tickOptions:{formatString: d_avgrq_sz['fmt']+' '+d_avgrq_sz['unit']+'sectors'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_avgrq_sz_time'), p)

        data = _data['avg']
        for (i=0; i<data[1].length; i++) {
          data[1][i][1] /= d_tps['div']
          data[1][i][2] /= d_tps['div']
          data[1][i][3] /= d_tps['div']
        }
        plot_width_x(id+'_tps', data[0])
	p = $.jqplot(id+'_tps', [data[1]], $.extend({}, chart_defaults, {
            title: {
                text: 'Block device transactions<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'io/s' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_tps['fmt']+' '+d_tps['unit']+'io/s'},
		    max: max_tps,
		    min: 0
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_tps'), p)

        for (i=0; i<data[2].length; i++) {
          data[2][i][1] /= d_avgrq_sz['div']
          data[2][i][2] /= d_avgrq_sz['div']
          data[2][i][3] /= d_avgrq_sz['div']
        }
        plot_width_x(id+'_avgrq_sz', data[0])
	p = $.jqplot(id+'_avgrq_sz', [data[2]], $.extend({}, chart_defaults, {
            title: {
                text: 'Block device request size<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'rq sz (sectors)' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_avgrq_sz,
                    tickOptions:{formatString: d_avgrq_sz['fmt']+' '+d_avgrq_sz['unit']+'sectors'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_avgrq_sz'), p)

        for (i=0; i<data[3].length; i++) {
          data[3][i][1] /= d_await['div']
          data[3][i][2] /= d_await['div']
          data[3][i][3] /= d_await['div']
        }
        plot_width_x(id+'_await', data[0])
	p = $.jqplot(id+'_await', [data[3]], $.extend({}, chart_defaults, {
            title: {
                text: 'Block device wait time<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'wait' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_await,
                    tickOptions:{formatString: d_await['fmt']+' '+d_await['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_await'), p)

        for (i=0; i<data[4].length; i++) {
          data[4][i][1] /= d_svctm['div']
          data[4][i][2] /= d_svctm['div']
          data[4][i][3] /= d_svctm['div']
        }
        plot_width_x(id+'_svctm', data[0])
	p = $.jqplot(id+'_svctm', [data[4]], $.extend({}, chart_defaults, {
            title: {
                text: 'Block device service time<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'svc time' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
		    min: 0,
		    max: max_svctm,
                    tickOptions:{formatString: d_svctm['fmt']+' '+d_svctm['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_svctm'), p)

        for (i=0; i<data[5].length; i++) {
          data[5][i][1] /= d_pct_util['div']
          data[5][i][2] /= d_pct_util['div']
          data[5][i][3] /= d_pct_util['div']
        }
        plot_width_x(id+'_pct_util', data[0])
	p = $.jqplot(id+'_pct_util', [data[5]], $.extend({}, chart_defaults, {
            title: {
                text: 'Block device utilization<br>high/low/average'
            },
            legend: {
                show: false
            },
	    seriesDefaults: {
		rendererOptions: hlc_defaults,
                renderer: $.jqplot.OHLCRenderer
            },
	    series: [
                { label: 'util (%)' }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70}
		}, 
		yaxis: {
                    tickOptions:{formatString: d_pct_util['fmt']+' '+d_pct_util['unit']+'%'},
                    max: max_pct_util,
		    min: 0
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pct_util'), p)

        for (i=0; i<data[6][0].length; i++) {
          data[6][0][i] /= d_secps['div']
          data[6][1][i] /= d_secps['div']
        }
        plot_width_x(id+'_secps', data[0])
	p = $.jqplot(id+'_secps', data[6], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Block device bandwidth<br>average'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'read'},
                {label: 'write'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d_secps['fmt']+' '+d_secps['unit']+'sect/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_secps'), p)

        plot_width_x(id+'_tm', data[7])
	p = $.jqplot(id+'_tm', data[8], $.extend({}, chart_defaults, {
	    stackSeries: true,
            title: {
                text: 'Hard/Soft times<br>average'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'hard (msec)'},
                {label: 'soft (msec)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_tm'), p)
    });
  })
}
function stats_netdev_err(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        if (_data[0][0].length == 0) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
        errps = _data[0]
        collps = _data[1]
        dropps = _data[2]
        labels = errps[0]
        data = errps[1]
        data = mangle_data(data)
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_errps', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Net device errors/s'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_errps'), p)

        labels = collps[0]
        data = collps[1]
        data = mangle_data(data)
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_collps', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Net device collisions/s'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_collps'), p)

        labels = dropps[0]
        data = dropps[1]
        data = mangle_data(data)
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_dropps', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Net device drops/s'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_dropps'), p)
    })
  })
}
function stats_netdev_avg(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
        plot_width_x(id+'_kBps', data[0])
	p = $.jqplot(id+'_kBps', data[1], $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Net device bandwidth'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'avg rcv (kB/s)'},
                {label: 'avg send (kB/s)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_kBps'), p)

        plot_width_x(id+'_pckps', data[0])
	p = $.jqplot(id+'_pckps', data[2], $.extend({}, chart_defaults, {
	    stackSeries: false,
            title: {
                text: 'Net device packet rate'
            },
	    seriesDefaults: {
                renderer: $.jqplot.BarRenderer, 
                shadowAngle: 135
            },
	    series: [
                {label: 'avg rcv (pck/s)'},
                {label: 'avg send (pck/s)'}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.CategoryAxisRenderer, 
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {formatString:'%s', angle: -70},
                    ticks: data[0]
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pckps'), p)
    })
  })
}
function stats_netdev(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        if (_data[0][0].length == 0) {
          set_no_data($("#"+id))
          return
        }
        set_has_data($("#"+id))
        bw = _data[0]
        pk = _data[1]
        labels = bw[0]
        data = bw[1]
        data = mangle_data(data)
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, 'KB')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            if (data[i][j][1] == null) {continue}
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_kBps', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Net device bandwidth'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_kBps'), p)

        labels = pk[0]
        data = pk[1]
        data = mangle_data(data)
        max = 0
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            max = Math.max(max, Math.abs(data[i][j][1]))
          }
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data.length; i++) {
          for (j=0; j<data[i].length; j++) {
            if (data[i][j][1] == null) {continue}
            data[i][j][1] /= d['div']
          }
        }
        series = []
        for (i=0; i<labels.length; i++) {
          series.push({label: labels[i]})
        }
	p = $.jqplot(id+'_pckps', data, $.extend({}, chart_defaults, {
	    stackSeries: false,
            seriesColors: plots_colors,
            title: {
                text: 'Net device packets/s'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: series,
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	}))
        _jqplot_extra($('#'+id+'_pckps'), p)
    });
  })
}
function convert_size(val, target_unit) {
	val = "" + val
	if (!val.match(/^\s*[0-9]*[\.]{0,1}[0-9]*\s*[kmgtpe]{0,1}[i]{0,1}[b]{0,1}$/i)) {
		return val
	}
	if (val == "") {
		return 0
	}
	if (val instanceof Array) {
		var l = []
		for (var i=0; i<val.length; i++) {
			l.push(convert_size(val[i]))
		}
		return l
	}

	if (!target_unit) {
		target_unit = "b"
	} else {
		target_unit = target_unit.toLowerCase()
	}

	// strip all whitespaces
	var _val = val.replace(/\s+/g, "")

	// extract unit
	var unit = _val.match(/[a-zA-Z]+/)
	if (unit) {
		unit = unit[0].toLowerCase()
	} else {
		unit = null
	}

	// extract value
	_val = _val.match(/^[0-9]+/)
	if (!_val) {
		return val
	}
	_val = _val[0]

	if (!unit || (unit == "b")) {
		_val = _val * 1
	} else if ((unit == "k") || (unit == "kb")) {
		_val = _val * 1024
	} else if ((unit == "ki") || (unit == "kib")) {
		_val = _val * 1000
	} else if ((unit == "m") || (unit == "mb")) {
		_val = _val * 1024 * 1024
	} else if ((unit == "mi") || (unit == "mib")) {
		_val = _val * 1000 * 1000
	} else if ((unit == "g") || (unit == "gb")) {
		_val = _val * 1024 * 1024 * 1024
	} else if ((unit == "gi") || (unit == "gib")) {
		_val = _val * 1000 * 1000 * 1000
	} else if ((unit == "t") || (unit == "tb")) {
		_val = _val * 1024 * 1024 * 1024 * 1024
	} else if ((unit == "ti") || (unit == "tib")) {
		_val = _val * 1000 * 1000 * 1000 * 1000
	} else if ((unit == "p") || (unit == "pb")) {
		_val = _val * 1024 * 1024 * 1024 * 1024 * 1024
	} else if ((unit == "pi") || (unit == "pib")) {
		_val = _val * 1000 * 1000 * 1000 * 1000 * 1000
	} else if ((unit == "e") || (unit == "eb")) {
		_val = _val * 1024 * 1024 * 1024 * 1024 * 1024 * 1024
	} else if ((unit == "ei") || (unit == "eib")) {
		_val = _val * 1000 * 1000 * 1000 * 1000 * 1000 * 1000
        } else {
		return val
	}

	if (target_unit == "b") {
		return _val
	} else if ((target_unit == "k") || (target_unit == "kb")) {
		return Math.ceil(_val / 1024)
	} else if ((target_unit == "ki") || (target_unit == "kib")) {
		return Math.ceil(_val / 1000)
	} else if ((target_unit == "m") || (target_unit == "mb")) {
		return Math.ceil(_val / 1024 / 1024)
	} else if ((target_unit == "mi") || (target_unit == "mib")) {
		return Math.ceil(_val / 1000 / 1000)
	} else if ((target_unit == "g") || (target_unit == "gb")) {
		return Math.ceil(_val / 1024 / 1024 / 1024)
	} else if ((target_unit == "gi") || (target_unit == "gib")) {
		return Math.ceil(_val / 1000 / 1000 / 1000)
	} else if ((target_unit == "t") || (target_unit == "tb")) {
		return Math.ceil(_val / 1024 / 1024 / 1024 / 1024)
	} else if ((target_unit == "ti") || (target_unit == "tib")) {
		return Math.ceil(_val / 1000 / 1000 / 1000 / 1000)
	} else if ((target_unit == "p") || (target_unit == "pb")) {
		return Math.ceil(_val / 1024 / 1024 / 1024 / 1024 / 1024)
	} else if ((target_unit == "pi") || (target_unit == "pib")) {
		return Math.ceil(_val / 1000 / 1000 / 1000 / 1000 / 1000)
	} else if ((target_unit == "e") || (target_unit == "eb")) {
		return Math.ceil(_val / 1024 / 1024 / 1024 / 1024 / 1024 / 1024)
	} else if ((target_unit == "ei") || (target_unit == "eib")) {
		return Math.ceil(_val / 1000 / 1000 / 1000 / 1000 / 1000 / 1000)
	} else {
		console.log("unknown target unit")
		return val
	}
}

function fancy_size_b(size) {
    if (size<1024) {
        unit = 'B'
        _size = size
    } else if (size<1048576) {
        unit = 'KB'
        _size = size / 1024
    } else if (size<1073741824) {
        unit = 'MB'
        _size = size / 1048576
    } else if (size<1099511627776) {
        unit = 'GB'
        _size = size / 1073741824
    } else {
        unit = 'TB'
        _size = size / 1099511627776
    }
    if (_size>=100) {
        _size = Math.round(_size)
    } else if (_size>=10) {
        _size = Math.round(_size*10)/10
    } else {
        _size = Math.round(_size*100)/100
    }
    return _size + ' ' + unit
}
function fancy_size_mb(size) {
	if (size < 0) {
		var sign = "- "
		size = - size
	} else {
		var sign = ""
	}
    if (size<1024) {
        unit = 'MB'
        _size = size
    } else if (size<1048576) {
        unit = 'GB'
        _size = size / 1024
    } else {
        unit = 'TB'
        _size = size / 1048576
    }
    if (_size>=100) {
        _size = Math.round(_size)
    } else if (_size>=10) {
        _size = Math.round(_size*10)/10
    } else {
        _size = Math.round(_size*100)/100
    }
    return sign + _size + ' ' + unit
}
function best_unit_mb(max, iunit) {
    if (typeof(iunit)==='undefined') {
        iunit = "MB"
    }
    iunit = iunit.toUpperCase()
    if (iunit.length == 2) {
        unit = iunit[iunit.length-1]
    } else {
        unit = ""
    }
    if (unit == 'B') {
        mul = 1024
    } else {
        mul = 1000
    }

    if (iunit.length < 1) {
        idiv = 1
    } else if (iunit[0] == 'K') {
        idiv = mul
    } else if (iunit[0] == 'm') {
        idiv =  1/mul
    } else if (iunit[0] == 'M') {
        idiv = mul*mul
    } else if (iunit[0] == 'u') {
        idiv =  1/mul/mul
    } else if (iunit[0] == 'G') {
        idiv = mul*mul*mul
    } else if (iunit[0] == 'p') {
        idiv =  1/mul/mul/mul
    } else if (iunit[0] == 'T') {
        idiv = mul*mul*mul*mul
    } else if (iunit[0] == 'P') {
        idiv = mul*mul*mul*mul*mul
    } else {
        idiv = 1
    }
    max *= idiv

    if (unit == 's' && max<1/mul/mul) {
        unit = 'p'+unit
        div = 1/mul/mul/mul
    } else if (unit == 's' && max<1/mul) {
        unit = 'u'+unit
        div = 1/mul/mul
    } else if (unit == 's' && max<1) {
        unit = 'm'+unit
        div = 1/mul
    } else if (max<mul) {
        unit = ''+unit
        div = 1
    } else if (max<mul*mul) {
        unit = 'K'+unit
        div = mul
    } else if (max<mul*mul*mul) {
        unit = 'M'+unit
        div = mul*mul
    } else if (max<mul*mul*mul*mul) {
        unit = 'G'+unit
        div = mul*mul*mul
    } else if (max<mul*mul*mul*mul*mul) {
        unit = 'T'+unit
        div = mul*mul*mul*mul
    } else {
        unit = 'P'+unit
        div = mul*mul*mul*mul*mul
    }
    max /= div

    if (max >= 100) {
        fmt = '%i'
    } else if (max >= 10) {
        fmt = '%.1f'
    } else {
        fmt = '%.2f'
    }
    return {'unit': unit, 'div': div/idiv, 'fmt': fmt}
}
function stats_fs(url, id) {
	function filter_data(data, key) {
		return data[key].map(x => x[1])
	}
	function add_fs(fs, data) {
		options = {
			lineColor: "#4bb2c5",
			height: "1.5em",
			width: "5em",
			tooltipSuffix: " KB"
		}
		options2 = {
			lineColor: "#eaa228",
			height: "1.5em",
			width: "5em",
			chartRangeMin: 0,
			chartRangeMax: 100,
			tooltipSuffix: "%"
		}
		var div = $("<tr>")
		var cell_fs = $("<td>").text(fs)
		cell_fs.appendTo(div)
		var cell_size = $("<td class='text-right'>&nbsp;</td>").sparkline(filter_data(data, "size"), options)
		cell_size.appendTo(div)
		var cell_used = $("<td class='text-right'>&nbsp;</td>").sparkline(filter_data(data, "used"), options2)
		cell_used.appendTo(div)
		return div
	}

	$.getJSON(url, function(data) {
		div = $("#"+id)
		if (is_dict_empty(data)) {
			set_no_data(div)
			return
		}
		div.empty()
		var container = $("<table class='table table-hover'>")
		container.appendTo(div)
		var header = $("<tr>")
		$("<th>").appendTo(header)
		$("<th class='text-right'>").text(i18n.t("col.Size")).appendTo(header)
		$("<th class='text-right'>").text(i18n.t("col.Used")).appendTo(header)
		header.appendTo(container)
		var keys = []
		for (fs in data) {
			keys.push(fs)
		}
		keys.sort()
		for (var i=0; i<keys.length; i++) {
			var fs = keys[i]
			add_fs(fs, data[fs]).appendTo(container)
		}
		$.sparkline_display_visible()
	})
}

/*
        data[1] = mangle_data(data[1])
        labels = new Array()
        for (i=0;i<data[0].length;i++){
            labels.push({'label': data[0][i]})
        }
        h = labels.length
        h = Math.max(38*h, 300)
        $('#'+id+'_u').height(h+'px')
        //plot_width_x(id+'_u', data[0])
	p = $.jqplot(id+'_u', data[1], $.extend({}, chart_defaults, {
            title: {
                text: 'Fs usage %'
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
                    min: data[1][0][0][0],
                    max: data[1][0][data[1][0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    max: 100,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
  	}))
        _jqplot_extra($('#'+id+'_u'), p)
    })
  })
}
*/
function stats_resinfo(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max, "")
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, $.extend({}, chart_defaults, {
            cursor:{zoom:true},
            stackSeries: true,
            legend: {
                show: false
            },
            seriesDefaults: {
                markerOptions: {size: 2},
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function stats_disk_array(url, id) {
  require(["jqplot"], function(){
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, $.extend({}, chart_defaults, {
            stackSeries: true,
            seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                {label: 'used'},
                {label: 'free'},
                {label: 'reserved', fill: false, disableStack: true},
                {label: 'reservable', fill: false, disableStack: true}
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function stats_disk_app(url, id) {
  require(["jqplot"], function(){
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, $.extend({}, chart_defaults, {
            seriesDefaults: {
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: [
                {label: 'used'},
                {label: 'quota'}
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function charts_plot(url, id) {
  require(["jqplot"], function(){
    $.jqplot.config.enablePlugins = true
    $.getJSON(url, function(dd) {
        data = dd['data']
        instances = dd['instances']
        options = dd['options']
        stackSeries = options['stack']
        series = []
        unit = ""
        if (instances.length>1) {
	    legend = {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{
                  numberRows: 7,
                  numberColumns: instances.length/7
                },
                show: true,
                placement: "outside",
                location: 'e'
            }
	} else {
	    legend = {
		show: false
	    }
	}
        for (i=0; i<instances.length; i++) {
            serie = {
              'label': instances[i]['label'],
              'shadow': instances[i]['shadow'],
              'fill': instances[i]['fill']
            }
	    series.push(serie)
            unit = instances[i]['unit']
	}
        max = 0
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                max = Math.max(max, data[i][j][1])
            }
        }
        d = best_unit_mb(max, unit)
        for (i=0; i<data.length; i++) {
            for (j=0; j<data[i].length; j++) {
                data[i][j][1] /= d['div']
            }
        }
	p = $.jqplot(id, data, $.extend({}, chart_defaults, {
	    stackSeries: stackSeries,
            legend: legend,
            seriesDefaults: {
                breakOnNull : true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            series: series,
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
                },
                yaxis: {
                    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
                }
            }

	}))
        _jqplot_extra($('#'+id), p)
    })
  })
}
function obsplot(o) {
	require(["jqplot"], function(){
		var data = $.parseJSON(o.html())
		o.html("")
		if (data[0].length < 1) {
			return
		}
		options = $.extend({}, chart_defaults, {
			series: [
				{
					label: 'delta', renderer: $.jqplot.BarRenderer,
					rendererOptions: {
						barWidth: 10
					}
				},
				{
					label: 'sigma'
				},
				{
					label: 'today',
					color: 'red',
					showMarker: false
				}
			],
			axes: {
				xaxis: {
					renderer: $.jqplot.DateAxisRenderer,
					numberTicks: 5,
					tickOptions: {
						formatString:'%b\n%Y'
					}
				},
				yaxis: {
					min: 0,
					max: data[2][1][1],
					tickOptions: {
						formatString:'%i'
					}
				}
			}
		})
		p = $.jqplot(o.attr('id'), data, options)
		_jqplot_extra(o, p)
	})
}

function _jqplot_extra(e, p){
}

function savedonut(o) {
  require(["jqplot"], function(){
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var title = total
  o.html("")
  $.jqplot(o.attr('id'), d['data'], {
      grid:{background:'transparent',borderColor:'transparent',shadow:false,drawBorder:false,shadowColor:'transparent'},
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          showDataLabels: true
        }
      },
      title: { text: title }
    }
  )
  $('#'+o.attr('id')).bind('jqplotDataHighlight',
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('level: '+seriesIndex+', data: '+data[0]);
        }
  )
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight',
        function (ev) {
            $('#chart_info').html('-');
        }
  )
  } catch(e) {}
  })
}

function plot_savedonuts() {
  $("[id^=chart_svc]").each(function(){
    savedonut($(this))
  })
  $("[id^=chart_ap]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      osvc.tables.saves.filter_submit("app", d)
    })
  })
  $("[id^=chart_group]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      osvc.tables.saves.filter_submit("save_group", d)
    })
  })
  $("[id^=chart_server]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      $("#saves_f_save_server").val(d)
      osvc.tables.saves.filter_submit("save_server", d)
    })
  })
}

function diskdonut(o) {
  require(["jqplot"], function(){
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var backend_total = fancy_size_mb(d['backend_total'])
  var title = total + ' (' + backend_total + ')'
  o.html("")
  $.jqplot(o.attr('id'), d['data'],
    {
      grid:{background:'transparent',borderColor:'transparent',shadow:false,drawBorder:false,shadowColor:'transparent'},
      seriesDefaults: {
        renderer: $.jqplot.DonutRenderer,
        rendererOptions: {
          sliceMargin: 0,
          showDataLabels: true
        }
      },
      title: { text: title }
    }
  );
  $('#'+o.attr('id')).bind('jqplotDataHighlight', 
        function (ev, seriesIndex, pointIndex, data) {
            $('#chart_info').html('level: '+seriesIndex+', data: '+data[0]);
        }
  );
  $('#'+o.attr('id')).bind('jqplotDataUnhighlight', 
        function (ev) {
            $('#chart_info').html('-');
        }
  );
  } catch(e) {}
  })
}

function plot_diskdonuts() {
  $("[id^=chart_svc]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      osvc.tables.disks.filter_submit("svc_id", d)
    })
  })
  $("[id^=chart_ap]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      osvc.tables.disks.filter_submit("app", d)
    })
  })
  $("[id^=chart_dg]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      d = d.replace(/\w+ /, "")
      d = d.replace(/ \(.*\)/, "")
      osvc.tables.disks.filter_submit("disk_group", d)
    })
  })
  $("[id^=chart_ar]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      osvc.tables.disks.filter_submit("disk_arrayid", d)
    })
  })
}

