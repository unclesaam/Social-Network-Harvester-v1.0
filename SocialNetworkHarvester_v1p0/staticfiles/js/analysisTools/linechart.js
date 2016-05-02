
$(document).ready(function() {    
    $('.graphReloader').click(function(){
        $(this).css('animation-name', 'spin');
        var container = $('.chart_container');
        var chart_vars = container.children('#chart_vars');
        eval(chart_vars.text());
        GET_params = addSelectedRowsToGET(GET_params);
        var url = createURLFromGet(GET_params, chartSource);
        drawChart(chartType, 'chart', options, url);
    });

    $('body').on('selectedTableRowsChanged', drawChartData);
});

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(function(){
    createChart();
});

function drawChartData(){
    log(selectedTableRows)
    var container = $('.chart_container');
    var chart_vars = container.children('#chart_vars');
    eval(chart_vars.text());
    GET_params = addSelectedRowsToGET(GET_params);
    var url = createURLFromGet(GET_params, chartSource);
    drawChart(chartType, 'chart', options, url);
}

function createChart() {
    var container = $('.chart_container');
    var chart_vars = container.children('#chart_vars');
    eval(chart_vars.text());
    var url = createURLFromGet(GET_params, chartSource);
    drawChart(chartType, 'chart', options, url);
    $(window).resize(function(){

        drawChart(chartType, 'chart', options, url);
    });
    $("#menu_select").click(function(){
        drawChart(chartType, 'chart', options, url);
    })
}

function drawChart(charType, containerId, options, dataSourceUrl){
    var chart = new google.visualization.ChartWrapper({
        chartType: charType,
        dataSourceUrl: dataSourceUrl,
        options: options,
        containerId: containerId,
    });
    var width = $("#chart").parent().css('width');
    $('#chart').parent().css("height", parseInt(width)*2/5);
    chart.draw();
    google.visualization.events.addListener(chart, 'ready', chartReadyHandler);
    google.visualization.events.addListener(chart, 'ready', chartErrorHandler);
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












