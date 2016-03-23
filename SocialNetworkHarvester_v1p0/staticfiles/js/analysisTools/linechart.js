
$(document).ready(function() {    

});

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(function(){
    var chart, options = createChart();
    $(".chartContainer").resize(function(){
        var width = $(this).css('width');
        $(this).css("height", parseInt(width)*2/5);
        chart.draw(data, options);
    });
});


function createChart() {

    var options = {
        title: 'User activity',
        subtitle: "Tweets, statuses, comments, videos",
        curveType: 'function',
        legend: { position: 'right' },
        chartArea: {
            left:40,
            top:40,
            bottom:40,
            right:200,
        },
        explorer:{
            axis: 'horizontal',
            keepInBounds: true,
        },
        hAxis: {
            format: 'decimal',
        }
    }
    var chart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        dataSourceUrl: "/tool/linechart?ajax=true",
        options: options,
        containerId: 'linechart_1'
    });
    chart.draw();
return chart, options;
}
























