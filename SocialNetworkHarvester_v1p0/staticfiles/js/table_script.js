$.getScript("/static/js/DataTables-1.10.9/js/jquery.dataTables.min.js")
$.getScript("/static/js/Select-1.0.1/js/dataTables.select.min.js")


$(document).ready(function() {
    
    $(".section_title").click(function(){
        var content = $(this).parent().next(".section_content");
        var options = $(this).next(".section_options");
        var table = content.children();
        if(options.length != 0){
            menuToggle(options);
        }
        if(content.length != 0){
            content.slideToggle(300);
            if (table.attr('drawn') == 'False'){
                drawTable(table)
            }
        }
    });

    $('.table_select_master').click(function(){
        table = $(this).parents('.display')
        if($(this).prop('checked')){
            table.DataTable().rows().select()
        } else {
            table.DataTable().rows().deselect()
        }
    });

    $('#reloadTableLink').click(function(){
        var content = $(this).parent().parent().next(".section_content");
        var table = content.children().children("table");
        console.log(table.DataTable())
        table.DataTable().ajax.reload();
    })
    
});

function drawTable(table){
    var scriptTag = table.children('.tableVars')
    eval(scriptTag.text())
    if (fields) {
        source = source+'?fields='+fields;
    }
    table.dataTable({
        "iDisplayLength": 10,
        "autoWidth": false,
        "sAjaxSource":source,
        "columnDefs": columnsDefs,
        "select": {
            "style":    'multi',
            "selector": 'td:first-child'
        },
        "order": [[ 1, 'asc' ]],
    });
}

function menuToggle(elem){
    if (elem.css('width') == '0px'){
        elem.animate({
            width: parseInt(elem.parent().css("width")) - parseInt(elem.prev(".section_title").css("width"))-35
        },300);
    } else {
        elem.animate({width:0},300);
    }
}
