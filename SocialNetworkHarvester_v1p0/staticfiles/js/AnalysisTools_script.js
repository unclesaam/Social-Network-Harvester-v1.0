$(document).ready(function() {    

});

google.load('visualization', '1.1', {packages: ['line']});
google.setOnLoadCallback(function(){
    lineChart = createChart();
    google.visualization.events.addListener(lineChart, 'ready', function(){
        resizeParentFrame();
    });
    $(document).resize(function(){
        var cont = $(".chart_container");
        var width = cont.css('width');
        cont.css("height", parseInt(width)*2/5);
        lineChart.draw(data, options);
    });
});


function createChart() {

    data = new google.visualization.DataTable();
    data.addColumn('number', 'Date');
    data.addColumn('number', 'Mickael Temporao (Tweets)');
    data.addColumn('number', 'BCC (Youtube videos)');
    data.addColumn('number', 'Samuel Cloutier (Facebook statuses)');

    data.addRows([
    [1,  37.8, 80.8, 41.8],
    [2,  30.9, 69.5, 32.4],
    [3,  25.4,   57, 25.7],
    [4,  11.7, 18.8, 10.5],
    [5,  11.9, 17.6, 10.4],
    [6,   8.8, 13.6,  7.7],
    [7,   7.6, 12.3,  9.6],
    [8,  12.3, 29.2, 10.6],
    [9,  16.9, 42.9, 14.8],
    [10, 12.8, 30.9, 11.6],
    [11,  5.3,  7.9,  4.7],
    [12,  6.6,  8.4,  5.2],
    [13,  4.8,  6.3,  3.6],
    [14,  4.2,  6.2,  3.4],
    [15,  37.8, 80.8, 41.8],
    [16,  30.9, 69.5, 32.4],
    [17,  25.4,   57, 25.7],
    [18,  11.7, 18.8, 10.5],
    [19,  11.9, 17.6, 10.4],
    [20,   8.8, 13.6,  7.7],
    [21,   7.6, 12.3,  9.6],
    [22,  12.3, 29.2, 10.6],
    [23,  16.9, 42.9, 14.8],
    [24, 12.8, 30.9, 11.6],
    [25,  5.3,  7.9,  4.7],
    [26,  6.6,  8.4,  5.2],
    [27,  4.8,  6.3,  3.6],
    [28,  4.2,  6.2,  3.4],
    [29,  37.8, 80.8, 41.8],
    [30,  30.9, 69.5, 32.4],
    [31,  25.4,   57, 25.7],
    [32,  11.7, 18.8, 10.5],
    [33,  11.9, 17.6, 10.4],
    [34,   8.8, 13.6,  7.7],
    [35,   7.6, 12.3,  9.6],
    [36,  12.3, 29.2, 10.6],
    [37,  16.9, 42.9, 14.8],
    [38, 12.8, 30.9, 11.6],
    [39,  5.3,  7.9,  4.7],
    [40,  6.6,  8.4,  5.2],
    [41,  4.8,  6.3,  3.6],
    [42,  4.2,  6.2,  3.4],
    [43,  37.8, 80.8, 41.8],
    [44,  30.9, 69.5, 32.4],
    [45,  25.4,   57, 25.7],
    [46,  11.7, 18.8, 10.5],
    [47,  11.9, 17.6, 10.4],
    [48,   8.8, 13.6,  7.7],
    [49,   7.6, 12.3,  9.6],
    [50,  12.3, 29.2, 10.6]
    ]);

    options = {
        chart: {
          title: 'User activity comparison',
          subtitle: 'Tweets, Facebook posts and comments, Youtube videos and comments'
        },
    };

    chart = new google.charts.Line(document.getElementById('linechart_1'));
    chart.draw(data, options);
return chart;
}

function resizeChildren(){
    chart.draw(data, options);
}


























