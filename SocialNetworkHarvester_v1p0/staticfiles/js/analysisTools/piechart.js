google.charts.load('current', {'packages': ['corechart']});
google.charts.setOnLoadCallback(function () {initChart()});
var lastData = {};
var chartWrapper = null;
var visibilityThreshold = 1;

$(document).ready(function() {
    visibilityThreshold = $('#threshold_setter')[0].value;
    $('.graphReloader').click(function(){
        $(this).css('animation-name', 'spin');
        var container = $('.chart_container');
        var chart_vars = container.children('#chart_vars');
        eval(chart_vars.text());
        var url = createURLFromGet(GET_params, chartSource);
        drawChart(chartType, 'chart', options, url);
    });

    $('body').on('selectedTableRowsChanged', loadChart);
});

function loadChart(){
    var container = $('.chart_container');
    var chart_vars = container.children('#chart_vars');
    eval(chart_vars.text());
    var url = createURLFromGet(GET_params, chartSource);
    drawChart(chartType, 'chart', options, url);
}

function reloadChartFromLocalData(){
    chartWrapper.draw();
    //var container = $('.chart_container');
    //var chart_vars = container.children('#chart_vars');
    //eval(chart_vars.text());
    //var url = createURLFromGet(GET_params, chartSource);
    //if (!$.isEmptyObject(lastData)) {url = null};
    //drawChart(chartType, 'chart', options, url);
}

var tmtfct = null;
function initChart() {
    loadChart()
    $(window).resize(function () {
        if (this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function () {
            $(this).trigger('resizeEnd');
        }, 500);
    });
    $(window).on('resizeEnd', reloadChartFromLocalData);
    $("#menu_select").click(reloadChartFromLocalData);
    $('#threshold_setter').change(function(){
        visibilityThreshold = this.value;
        clearTimeout(tmtfct);
        tmtfct = setTimeout(function(){
            loadChart();
        },500)
    });
    google.visualization.events.addListener(chartWrapper, 'ready', chartReadyHandler);
    google.visualization.events.addListener(chartWrapper, 'error', chartErrorHandler);
}

function drawChart(charType, containerId, options, dataSourceUrl){
    $('.graphReloader').css('animation-name', 'spin');
    if(!chartWrapper){
        if (dataSourceUrl) {
            chartWrapper = new google.visualization.ChartWrapper({
                chartType: charType,
                dataSourceUrl: dataSourceUrl,
                options: options,
                containerId: containerId,
            });
        } else {
            chartWrapper = new google.visualization.ChartWrapper({
                chartType: charType,
                dataTable: lastData,
                options: options,
                containerId: containerId,
            });
        }
    }
    if (dataSourceUrl){
        // TODO: Make it so the parameter name never changes. Now its called "ze", but might change in the future becuz Google...
        chartWrapper.ze = dataSourceUrl;
        chartWrapper.ue = dataSourceUrl;
    }
    var width = $("#chart").parent().css('width');
    $('#chart').parent().css("height", parseInt(width)*2/5);
    chartWrapper.draw();
}

function chartReadyHandler(){
    $('.graphReloader').css('animation-name', 'none');
}
function chartErrorHandler(event){
    $('.graphReloader').css('animation-name', 'none');
    log('chart has encountered an error')
    log(event)
}

function createURLFromGet(GET_params, baseUrl){
    var url = baseUrl+'?';
    for (var param in GET_params) {
        if (GET_params.hasOwnProperty(param)) {
            if (GET_params[param] instanceof Function){
                url += '&' + param + '=' + GET_params[param]();
            } else{
                url += '&' + param + '=' + GET_params[param];
            }
        }
    }
    return url;
}












