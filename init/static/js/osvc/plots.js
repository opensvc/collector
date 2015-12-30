function comp_status_plot(url, id) {
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
    });
}
function avail_plot(id, data) {
    $.jqplot.config.enablePlugins = true;
        document.getElementById(id).style['height'] = '50px'
	$.jqplot(id, data, {
            width: 300,
            height: 50,
            cursor: {
                zoom:true,
                showTooltip:true
            },
            highlighter: {
                show: false
            },
	    grid: {
                drawGridlines: false,
                borderWidth: 0,
                shadow: false,
                background: 'rgba(0,0,0,0)'
            },
	    seriesDefaults: {
                breakOnNull : true,
                breakOnNull: true,
                fill: false
            },
	    series: [
                {
                    label: 'down',
                    color: 'red'
                },
                {
                    label: 'down acked',
                    color: 'gray'
                },
                {
                    label: 'ack',
                    markerOptions:{style:'filledDiamond'}
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer, 
		    tickOptions: {
                        fontSize:'7pt',
		        formatString:'%#m/%#d %R'
                    }
		}, 
		yaxis: {
		    min: 0.8, 
		    max: 1.2, 
		    tickOptions:{
                        showLabel: false,
                        size: 0,
                        formatString:'%d'
                    }
		}
	    }
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
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id, data[0])
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average cpu utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_swp_for_nodes(url, id) {
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
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average swap utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_mem_for_nodes(url, id) {
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
        $('#'+id).width('450px')
	p = $.jqplot(id, data[1], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average memory utilization'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_block_for_nodes(url, id) {
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
        $('#'+id+'_tps').width('450px')
	p = $.jqplot(id+'_tps', [data[1][0], data[1][1]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average io/s'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
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
        $('#'+id+'_bps').width('450px')
	p = $.jqplot(id+'_bps', [data[1][2], data[1][3]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average block devices bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_bps'), p)
    });
}
function stats_disk_for_svc(url, id) {
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
        $('#'+id).width('450px')
	p = $.jqplot(id, [data[1][0]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Disk size per service'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_avg_proc_for_nodes(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        if (data[0].length == 0) { return }
        plot_height(id+'_runq_sz', data[0])
        $('#'+id+'_runq_sz').width('450px')
	p = $.jqplot(id+'_runq_sz', [data[1][0]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average run queue size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_runq_sz'), p)

        plot_height(id+'_plist_sz', data[0])
        $('#'+id+'_plist_sz').width('450px')
	p = $.jqplot(id+'_plist_sz', [data[1][1]], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Average process list size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_plist_sz'), p)
    });
}
function dash_history(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
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
        });
        _jqplot_extra($('#'+id), p)
    });
}
function comp_history(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        //$('#'+id).height('300px')
        $('#'+id).width('100%')
        p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
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
        });
        _jqplot_extra($('#'+id), p)
    });
}
function stat_day(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        $('#'+id+'_err').height('300px')
        $('#'+id+'_err').width('300px')
	p = $.jqplot(id+'_err', [data[2]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
		    label: 'err',
                    markerOptions: {size: 2},
		    color: 'red'
		}
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
	});
        _jqplot_extra($('#'+id+'_err'), p)

        $('#'+id+'_apps').height('300px')
        $('#'+id+'_apps').width('300px')
	p = $.jqplot(id+'_apps', [data[11]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
		    label: 'apps',
                    markerOptions: {size: 2}
		}
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
	});
        _jqplot_extra($('#'+id+'_apps'), p)

        $('#'+id+'_nb_vcpu').height('300px')
        $('#'+id+'_nb_vcpu').width('300px')
	p = $.jqplot(id+'_nb_vcpu', [data[20]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'vcpu',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
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
	});
        _jqplot_extra($('#'+id+'_nb_vcpu'), p)

        $('#'+id+'_nb_vmem').height('300px')
        $('#'+id+'_nb_vmem').width('300px')

        max = 0
        for (i=0; i<data[21].length; i++) {
            max = Math.max(max, data[21][i][1])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[21].length; i++) {
            data[21][i][1] /= d['div']
        }

	p = $.jqplot(id+'_nb_vmem', [data[21]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'vmem',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nb_vmem'), p)

        $('#'+id+'_disk').height('300px')
        $('#'+id+'_disk').width('300px')

        max = 0
        for (i=0; i<data[5].length; i++) {
            max = Math.max(max, data[5][i][1]+data[31][i][1])
        }
        d = best_unit_mb(max)
        for (i=0; i<data[5].length; i++) {
            data[5][i][1] /= d['div']
            data[31][i][1] /= d['div']
        }

	p = $.jqplot(id+'_disk', [data[5], data[31]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'SAN disk size',
                    breakOnNull: true
                },
                {
                    label: 'DAS disk size',
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_disk'), p)

        $('#'+id+'_nodes_ram').height('300px')
        $('#'+id+'_nodes_ram').width('300px')

        max = 0
        for (i=0; i<data[6].length; i++) {
            max = Math.max(max, data[6][i][1])
        }
        d = best_unit_mb(max*1024)
        for (i=0; i<data[6].length; i++) {
            data[6][i][1] *= 1024
            data[6][i][1] /= d['div']
        }

	p = $.jqplot(id+'_nodes_ram', [data[6]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'ram size',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_nodes_ram'), p)

        $('#'+id+'_nodes_core').height('300px')
        $('#'+id+'_nodes_core').width('300px')
	p = $.jqplot(id+'_nodes_core', [data[7]], {
            cursor:{zoom:true, showTooltip:false},
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            legend: {
                show: true,
                location: 'n'
            },
	    series: [
                {
                    label: 'cores',
                    markerOptions: {size: 2},
                    breakOnNull: true
                }
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
	});
        _jqplot_extra($('#'+id+'_nodes_core'), p)

        $('#'+id+'_accounts').height('300px')
        $('#'+id+'_accounts').width('300px')
	p = $.jqplot(id+'_accounts', [data[12]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    markerOptions: {size: 2},
		    label: 'accounts'
		}
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
	});
        _jqplot_extra($('#'+id+'_accounts'), p)

        $('#'+id+'_resp_accounts').height('300px')
        $('#'+id+'_resp_accounts').width('300px')
	p = $.jqplot(id+'_resp_accounts', [data[22]], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    markerOptions: {size: 2},
		    label: 'sys responsible accounts'
		}
            ],
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%Y\n%b,%d'}
		}, 
		yaxis: {
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_resp_accounts'), p)

        $('#'+id+'_actions').height('300px')
        $('#'+id+'_actions').width('300px')
	p = $.jqplot(id+'_actions', [data[4],  data[3], data[2]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'ok',
                    color: 'lightgreen'
                },
                {
                    label: 'warn',
                    color: 'orange'
                },
                {
                    label: 'error',
                    color: 'red'
                }
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
	});
        _jqplot_extra($('#'+id+'_actions'), p)

        $('#'+id+'_nodes').height('300px')
        $('#'+id+'_nodes').width('300px')
	p = $.jqplot(id+'_nodes', [data[17],  data[14]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'PRD nodes'
                },
                {
                    label: 'other nodes'
                }
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
	});
        _jqplot_extra($('#'+id+'_nodes'), p)

        $('#'+id+'_virt_nodes').height('300px')
        $('#'+id+'_virt_nodes').width('300px')
	p = $.jqplot(id+'_virt_nodes', [data[23],  data[24]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'virtual nodes'
                },
                {
                    label: 'physical nodes'
                }
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
	});
        _jqplot_extra($('#'+id+'_virt_nodes'), p)

        $('#'+id+'_svc_type').height('300px')
        $('#'+id+'_svc_type').width('300px')
	p = $.jqplot(id+'_svc_type', [data[15],  data[0]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {label: 'PRD svc'},
                {label: 'other svc'}
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
	});
        _jqplot_extra($('#'+id+'_svc_type'), p)

        $('#'+id+'_svc_cluster').height('300px')
        $('#'+id+'_svc_cluster').width('300px')
	p = $.jqplot(id+'_svc_cluster', [data[16],  data[18]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    seriesDefaults: {
                breakOnNull: true,
                fill: true
            },
	    series: [
                {label: 'clustered svc'},
                {label: 'not clustered svc'}
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
	});
        _jqplot_extra($('#'+id+'_svc_cluster'), p)

        $('#'+id+'_svc_drp').height('300px')
        $('#'+id+'_svc_drp').width('300px')
	p = $.jqplot(id+'_svc_drp', [data[13],  data[19]], {
            cursor:{zoom:true, showTooltip:false},
	    stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                {
                    label: 'svc with drp'
                },
                {
                    label: 'svc without drp'
                }
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
	});
        _jqplot_extra($('#'+id+'_svc_drp'), p)
    });
}
function stat_compare_day(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        labels = new Array()
        for (i=0; i<data[0].length; i++){
            labels.push({'label': data[0][i]})
        }
        $('#'+id+'_svc').height('300px')
        $('#'+id+'_svc').width('300px')
	p = $.jqplot(id+'_svc', data[1][25], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_svc'), p)

        $('#'+id+'_nodes').height('300px')
        $('#'+id+'_nodes').width('300px')
	p = $.jqplot(id+'_nodes', data[1][26], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_nodes'), p)

        $('#'+id+'_nodes_virt_ratio').height('300px')
        $('#'+id+'_nodes_virt_ratio').width('300px')
	p = $.jqplot(id+'_nodes_virt_ratio', data[1][27], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_nodes_virt_ratio'), p)

        $('#'+id+'_svc_prd_ratio').height('300px')
        $('#'+id+'_svc_prd_ratio').width('300px')
	p = $.jqplot(id+'_svc_prd_ratio', data[1][28], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_svc_prd_ratio'), p)

        $('#'+id+'_svc_drp_ratio').height('300px')
        $('#'+id+'_svc_drp_ratio').width('300px')
	p = $.jqplot(id+'_svc_drp_ratio', data[1][29], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_svc_drp_ratio'), p)

        $('#'+id+'_svc_clu_ratio').height('300px')
        $('#'+id+'_svc_clu_ratio').width('300px')
	p = $.jqplot(id+'_svc_clu_ratio', data[1][30], {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
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
	});
        _jqplot_extra($('#'+id+'_svc_clu_ratio'), p)
    });
}
function stats_cpu(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        $("#"+id+"_u").width("600px")
	p = $.jqplot(id+"_u", data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Cpu usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                markerOptions: {size: 2},
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                breakOnNull : true,
                shadowWidth: 2
            },
	    series: [
                { label: 'usr' },
                { label: 'nice' },
                { label: 'sys' },
                { label: 'iowait' },
                { label: 'steal' },
                { label: 'irq' },
                { label: 'soft' },
                { label: 'guest' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_u'), p)
    });
}
function stats_proc(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id+'_runq_sz', [data[0]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Run queue size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'runq_sz' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_runq_sz'), p)

	p = $.jqplot(id+'_plist_sz', [data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Process list size'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'plist_sz' }
            ],
	    axes: {
		xaxis: {
                    min: data[1][0][0],
                    max: data[1][data[1].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_plist_sz'), p)

	p = $.jqplot(id+'_loadavg', [data[2],data[3],data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Load average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'loadavg 1\'' },
                { label: 'loadavg 5\'' },
                { label: 'loadavg 15\'' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_loadavg'), p)
    });
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

	p = $.jqplot(id, data[1], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: title
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_mem(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {

        max = 0
        for (i=0; i<data[1].length; i++) {
            max = Math.max(max, (data[1][i][1]+data[3][i][1]+data[4][i][1]+data[7][i][1]+data[0][i][1])/1024)
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']*1024
            data[3][i][1] /= d['div']*1024
            data[4][i][1] /= d['div']*1024
            data[7][i][1] /= d['div']*1024
            data[0][i][1] /= d['div']*1024
        }

	p = $.jqplot(id+'_u', [data[1], data[3], data[4], data[7], data[0]], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Memory usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used' },
                { label: 'used, buffer' },
                { label: 'used, cache' },
                { label: 'used, sys' },
                { label: 'free' }
            ],
	    axes: {
		xaxis: {
                    min: data[1][0][0],
                    max: data[1][data[1].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_u'), p)

	p = $.jqplot(id+'_pct', [data[2],data[6]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Memory usage percent'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used/mem' },
                { label: 'promised/(mem+swap)' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct'), p)

    });
}
function stats_swap(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {

        max = 0
        for (i=0; i<data[1].length; i++) {
            max = Math.max(max, (data[1][i][1]+data[3][i][1]+data[0][i][1])/1024)
        }
        d = best_unit_mb(max)
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']*1024
            data[3][i][1] /= d['div']*1024
            data[0][i][1] /= d['div']*1024
        }

	p = $.jqplot(id+'_u', [data[1], data[3], data[0]], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: 'Swap usage'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used' },
                { label: 'used, cached' },
                { label: 'free' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
                    tickOptions:{formatString: d['fmt']+' '+d['unit']}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_u'), p)

	p = $.jqplot(id+'_pct', [data[2],data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Swap usage percent'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'used/total' },
                { label: 'cached/used' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%.2f%%'}
		}
	    }
	});
        _jqplot_extra($('#'+id+'_pct'), p)
    });
}
function stats_block(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        max = 0
        for (i=0; i<data[0].length; i++) {
            max = Math.max(max, (data[0][i][1]))
            max = Math.max(max, (data[1][i][1]))
        }
        d = best_unit_mb(max, '')
        for (i=0; i<data[1].length; i++) {
            data[1][i][1] /= d['div']
            data[0][i][1] /= d['div']
        }

	p = $.jqplot(id+'_tps', [data[0],data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device transactions'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'read' },
                { label: 'write' }
            ],
	    axes: {
		xaxis: {
                    min: data[0][0][0],
                    max: data[0][data[0].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'io/s'},
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_tps'), p)

        max = 0
        for (i=0; i<data[2].length; i++) {
            max = Math.max(max, (data[2][i][1]))
            max = Math.max(max, (data[3][i][1]))
        }
        d = best_unit_mb(max, 'KB')
        for (i=0; i<data[2].length; i++) {
            data[2][i][1] /= d['div']
            data[3][i][1] /= d['div']
        }

	p = $.jqplot(id+'_bps', [data[2],data[3]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                markerOptions: {size: 2},
                fill: false,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: [
                { label: 'read' },
                { label: 'write' }
            ],
	    axes: {
		xaxis: {
                    min: data[2][0][0],
                    max: data[2][data[2].length-1][0],
		    renderer: $.jqplot.DateAxisRenderer, 
                    tickOptions:{formatString:'%b,%d\n%H:%M'}
		}, 
		yaxis: {
                    tickOptions:{formatString: d['fmt']+' '+d['unit']+'/s'},
		    min: 0
		}
	    }
	});
        _jqplot_extra($('#'+id+'_bps'), p)
    });
}
function stats_trend_mem(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Memory usage trend<br>high/low/average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_trend_cpu(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
	p = $.jqplot(id, [data], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Cpu usage trend<br>high/low/average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_blockdev(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]
        data = _data['time']['secps']['data']
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
	p = $.jqplot(id+'_secps_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Block device bandwidth'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_secps_time'), p)

        data = _data['time']['pct_util']['data']
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
	p = $.jqplot(id+'_pct_util_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device utilization'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_pct_util_time'), p)

        data = _data['time']['tps']['data']
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
	p = $.jqplot(id+'_tps_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device transactions'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_tps_time'), p)

        data = _data['time']['await']['data']
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
	p = $.jqplot(id+'_await_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device wait time'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_await_time'), p)

        data = _data['time']['svctm']['data']
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
	p = $.jqplot(id+'_svctm_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device service time'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_svctm_time'), p)

        data = _data['time']['avgrq_sz']['data']
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
	p = $.jqplot(id+'_avgrq_sz_time', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            title: {
                text: 'Block device request size'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_avgrq_sz_time'), p)

        data = _data['avg']
        for (i=0; i<data[1].length; i++) {
          data[1][i][1] /= d_tps['div']
          data[1][i][2] /= d_tps['div']
          data[1][i][3] /= d_tps['div']
        }
        plot_width_x(id+'_tps', data[0])
	p = $.jqplot(id+'_tps', [data[1]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device transactions<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id+'_tps'), p)

        for (i=0; i<data[2].length; i++) {
          data[2][i][1] /= d_avgrq_sz['div']
          data[2][i][2] /= d_avgrq_sz['div']
          data[2][i][3] /= d_avgrq_sz['div']
        }
        plot_width_x(id+'_avgrq_sz', data[0])
	p = $.jqplot(id+'_avgrq_sz', [data[2]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device request size<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id+'_avgrq_sz'), p)

        for (i=0; i<data[3].length; i++) {
          data[3][i][1] /= d_await['div']
          data[3][i][2] /= d_await['div']
          data[3][i][3] /= d_await['div']
        }
        plot_width_x(id+'_await', data[0])
	p = $.jqplot(id+'_await', [data[3]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device wait time<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id+'_await'), p)

        for (i=0; i<data[4].length; i++) {
          data[4][i][1] /= d_svctm['div']
          data[4][i][2] /= d_svctm['div']
          data[4][i][3] /= d_svctm['div']
        }
        plot_width_x(id+'_svctm', data[0])
	p = $.jqplot(id+'_svctm', [data[4]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device service time<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id+'_svctm'), p)

        for (i=0; i<data[5].length; i++) {
          data[5][i][1] /= d_pct_util['div']
          data[5][i][2] /= d_pct_util['div']
          data[5][i][3] /= d_pct_util['div']
        }
        plot_width_x(id+'_pct_util', data[0])
	p = $.jqplot(id+'_pct_util', [data[5]], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Block device utilization<br>high/low/average'
            },
            legend: {
                show: false,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
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
	});
        _jqplot_extra($('#'+id+'_pct_util'), p)

        for (i=0; i<data[6][0].length; i++) {
          data[6][0][i] /= d_secps['div']
          data[6][1][i] /= d_secps['div']
        }
        plot_width_x(id+'_secps', data[0])
	p = $.jqplot(id+'_secps', data[6], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Block device bandwidth<br>average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_secps'), p)

        plot_width_x(id+'_tm', data[7])
	p = $.jqplot(id+'_tm', data[8], {
	    stackSeries: true,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Hard/Soft times<br>average'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_tm'), p)
    });
}
function stats_netdev_err(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        errps = _data[0]
        collps = _data[1]
        dropps = _data[2]
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]

        labels = errps[0]
        data = errps[1]
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
	p = $.jqplot(id+'_errps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device errors/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_errps'), p)

        labels = collps[0]
        data = collps[1]
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
	p = $.jqplot(id+'_collps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device collisions/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_collps'), p)

        labels = dropps[0]
        data = dropps[1]
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
	p = $.jqplot(id+'_dropps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device drops/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_dropps'), p)
    });
}
function stats_netdev_avg(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        plot_width_x(id+'_kBps', data[0])
	p = $.jqplot(id+'_kBps', data[1], {
	    stackSeries: false,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Net device bandwidth'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_kBps'), p)

        plot_width_x(id+'_pckps', data[0])
	p = $.jqplot(id+'_pckps', data[2], {
	    stackSeries: false,
	    grid: {
                borderWidth: 0.5
            },
            title: {
                text: 'Net device packet rate'
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
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
	});
        _jqplot_extra($('#'+id+'_pckps'), p)
    });
}
function stats_netdev(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(_data) {
        bw = _data[0]
        pk = _data[1]
        colors = [ "#4bb2c5", "#4bb2c5", "#EAA228", "#EAA228", "#c5b47f", "#c5b47f", "#579575", "#579575", "#839557", "#839557", "#958c12", "#958c12", "#953579", "#953579", "#4b5de4", "#4b5de4", "#d8b83f", "#d8b83f", "#ff5800", "#ff5800", "#0085cc", "#0085cc", "#c747a3", "#c747a3", "#cddf54", "#cddf54", "#FBD178", "#FBD178", "#26B4E3", "#26B4E3", "#bd70c7", "#bd70c7"]

        labels = bw[0]
        data = bw[1]
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
	p = $.jqplot(id+'_kBps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device bandwidth'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_kBps'), p)

        labels = pk[0]
        data = pk[1]
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
	p = $.jqplot(id+'_pckps', data, {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: false,
            seriesColors: colors,
            title: {
                text: 'Net device packets/s'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
	});
        _jqplot_extra($('#'+id+'_pckps'), p)
    });
}
function convert_size(val) {
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
	return _val
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
    return _size + ' ' + unit
}
function best_unit_mb(max, iunit) {
    if (typeof(iunit)==='undefined') {
        iunit = "MB"
    }
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
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        labels = new Array()
        for (i=0;i<data[0].length;i++){
            labels.push({'label': data[0][i]})
        }
        h = labels.length
        h = Math.max(38*h, 300)
        $('#'+id+'_u').height(h+'px')
        //plot_width_x(id+'_u', data[0])
	p = $.jqplot(id+'_u', data[1], {
            cursor:{zoom:true, showTooltip:true},
            title: {
                text: 'Fs usage %'
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'e',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
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
  	});
        _jqplot_extra($('#'+id+'_u'), p)
    });
}
function stat_os(url, id) {
    $.jqplot.config.enablePlugins = true;
    $.getJSON(url, function(data) {
        $("#"+id).width("600px")
        //plot_width(id, data[0])
        labels = new Array()
        for (i=0;i<data[0].length;i++){
            labels.push({'label': data[0][i]})
        }
        h = labels.length
        h = Math.max(24*h, 300)
        $('#'+id).height(h+'px')
        if (id == 'stat_os_name') {
             title = ''
        } else {
             title = id.replace('stat_os_','')
        }
	p = $.jqplot(id, data[1], {
            cursor:{zoom:true, showTooltip:true},
	    stackSeries: true,
            title: {
                text: title
            },
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                show: true,
                location: 'ne',
                placement: "outside"
            },
            gridPadding: {
                right:90
            },
	    grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    seriesDefaults: {
                breakOnNull : true,
                fill: true,
                shadowAngle: 135,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
	    series: labels,
	    axes: {
		xaxis: {
		    renderer: $.jqplot.DateAxisRenderer, 
		    tickOptions:{formatString:'%F'}
		}, 
		yaxis: {
		    min: 0,
		    tickOptions:{formatString:'%i'}
		}
	    }
	});
        _jqplot_extra($('#'+id), p)
    });
}

function stats_appinfo(url, id) {
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
	p = $.jqplot(id, data, {
            cursor:{zoom:true},
            stackSeries: true,
            legend: {
                show: false
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
            seriesDefaults: {
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

	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_disk_array(url, id) {
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
	p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            stackSeries: true,
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
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

	});
        _jqplot_extra($('#'+id), p)
    });
}
function stats_disk_app(url, id) {
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
	p = $.jqplot(id, data, {
            cursor:{zoom:true, showTooltip:false},
            legend: {
                renderer: $.jqplot.EnhancedLegendRenderer,
                rendererOptions:{numberRows: 1},
                show: true,
                location: 'n'
            },
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
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

	});
        _jqplot_extra($('#'+id), p)
    });
}
function charts_plot(url, id) {
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
	p = $.jqplot(id, data, {
	    stackSeries: stackSeries,
            cursor:{zoom:true, showTooltip:false},
            legend: legend,
            grid: {
                borderWidth: 0.5,
                shadowOffset: 1.0,
                shadowWidth: 2
            },
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

	});
        _jqplot_extra($('#'+id), p)
    });
}
function obsplot(o) {
  var data = $.parseJSON(o.html())
  o.html("")
  if (data[0].length < 1) {
    return
  }
  options = {
	    cursor: {
                show: true,
                zoom: true
            },
            highlighter: {
                show: true
            },
            legend: {
                show: true,
                location: 'e',
                placement: "outside"
            },
            series: [
                {label: 'delta', renderer: $.jqplot.BarRenderer,
                 rendererOptions: {
                  barWidth: 10
                 }
                },
                {label: 'sigma'},
                {label: 'today', color: 'red', showMarker: false},
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    numberTicks: 5,
                    tickOptions:{formatString:'%b\n%Y'}
                },
                yaxis: {
                    min: 0,
                    max: data[2][1][1],
                    tickOptions:{formatString:'%i'}
                }
            }
  }
  p = $.jqplot(o.attr('id'), data, options)
  _jqplot_extra(o, p)
}

function jqplot_img(){
    if (!$.jqplot.use_excanvas) {
        $('div.jqplot-target').each(function(){
            _jqplot_img(this)
        })
    }
}

function _jqplot_extra(e, p){
	_jqplot_resize(e, p);
	_jqplot_img(e);
}

function _jqplot_resize(e, p){
	e.parent().resizable({delay:20});
	e.parent().bind('resize', function(event, ui) {
          e.width('100%');
          e.height('90%');
	  p.replot( { resetAxes: false } );
	});
}

function _jqplot_img(e){
            return;
            var outerDiv = $('<div></div>');
            var header = $('<div></div>');
            var div = $('<div></div>');

            outerDiv.append(header);
            outerDiv.append(div);

            outerDiv.addClass('jqplot-image-container');
            header.addClass('jqplot-image-container-header');
            div.addClass('jqplot-image-container-content');

            header.html('Right Click to Save Image As...');

            var close = $('<a>');
            close.addClass('jqplot-image-container-close');
            close.html('Close');
            close.click(function() {
                $(this).parents('div.jqplot-image-container').hide();
            })
            header.append(close);

            $(e).after(outerDiv);
            outerDiv.hide();

            outerDiv = header = div = close = null;

            if (!$.jqplot._noToImageButton) {
                var btn = $(document.createElement('button'));
                btn.text('View Plot Image');
                btn.addClass('jqplot-image-button');
                btn.bind('click', {chart: $(e)}, function(evt) {
                    var imgelem = evt.data.chart.jqplotToImageElem();
                    var div = $(e).nextAll('div.jqplot-image-container').first();
                    div.children('div.jqplot-image-container-content').empty();
                    div.children('div.jqplot-image-container-content').append(imgelem);
                    div.show();
                    div = null;
                });

                $(e).append(btn);
                //btn.after('<br />');
                btn = null;
            }
}

function savedonut(o) {
  try{
  var d = $.parseJSON(o.html())
  var total = fancy_size_mb(d['total'])
  var title = total
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
      filter_submit("saves", "saves_f_save_app", d)
    })
  })
  $("[id^=chart_group]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("saves", "saves_f_save_group", d)
    })
  })
  $("[id^=chart_server]").each(function(){
    savedonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      $("#saves_f_save_server").val(d)
      filter_submit("saves", "saves_f_save_server", d)
    })
  })
}

function diskdonut(o) {
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
}

function plot_diskdonuts() {
  $("[id^=chart_svc]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("disks", "disks_f_disk_svcname", d)
    })
  })
  $("[id^=chart_ap]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      i = d.lastIndexOf(" (")
      d = d.substring(0, i)
      filter_submit("disks", "disks_f_app", d)
    })
  })
  $("[id^=chart_dg]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      d = d.replace(/\w+ /, "")
      d = d.replace(/ \(.*\)/, "")
      filter_submit("disks", "disks_f_disk_group", d)
    })
  })
  $("[id^=chart_ar]").each(function(){
    diskdonut($(this))
    $(this).bind('jqplotDataClick', function(ev, seriesIndex, pointIndex, data) {
      d = data[seriesIndex]
      var reg = new RegExp(" \(.*\)", "g");
      d = d.replace(reg, "")
      filter_submit("disks", "disks_f_disk_arrayid", d)
    })
  })
}

