google.charts.load('current', {'packages': ['corechart']});
google.charts.setOnLoadCallback(function () {initChart()});
var lastData = {};
var chartWrapper = null;

$(document).ready(function() {    
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
    var container = $('.chart_container');
    var chart_vars = container.children('#chart_vars');
    eval(chart_vars.text());
    var url = createURLFromGet(GET_params, chartSource);
    if (!$.isEmptyObject(lastData)) {url = null};
    drawChart(chartType, 'chart', options, url);
}

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
    google.visualization.events.addListener(chartWrapper, 'ready', chartReadyHandler);
    google.visualization.events.addListener(chartWrapper, 'error', chartErrorHandler);
}

function drawChart(charType, containerId, options, dataSourceUrl){
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
                data: lastData,
                options: options,
                containerId: containerId,
            });
        }
    }

    var width = $("#chart").parent().css('width');
    $('#chart').parent().css("height", parseInt(width)*2/5);
    chartWrapper.draw();
}

function chartReadyHandler(){
    $('.graphReloader').css('animation-name', 'none');
}
function chartErrorHandler(){
    $('.graphReloader').css('animation-name', 'none');
}

function createURLFromGet(GET_params, baseUrl){
    var url = baseUrl+'?';
    for (var param in GET_params) {
        if (GET_params.hasOwnProperty(param)) {
            url+='&'+param+'='+GET_params[param];
        }
    }
    return url;
}
/*
function addSelectedRowsToGET(GET_params){
    var selected = '';
    selectedTableRows.slice(0,10).forEach(function(item){
        selected+=item+',';
    })
    if (selected != ''){
        GET_params['selected_rows'] = selected.slice(0, -1);
    }
    return GET_params;
}
*/












