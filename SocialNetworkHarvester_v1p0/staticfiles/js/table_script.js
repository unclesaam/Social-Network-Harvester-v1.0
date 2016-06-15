$.getScript("/static/js/DataTables-1.10.9/js/jquery.dataTables.min.js")
$.getScript("/static/js/Select-1.0.1/js/dataTables.select.min.js")
$.getScript("/static/js/linkify/linkify.min.js", function(){
    $.getScript("/static/js/linkify/linkify-string.min.js")
})

//var selectedTableRows = [];
var default_asSorting = ["desc", "asc", "none"];

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
                drawTable(table);
            }
        }
        //log($(this).parent().children(".tableOpenCloseIcon"))
        togglePlusMinusSign($(this).parent().children(".tableOpenCloseIcon"))
    });

    $('.tableOpenCloseIcon').click(function(){
        var content = $(this).parent().next(".section_content");
        var options = $(this).prev(".section_options");
        var table = content.children();
        if(options.length != 0){
            menuToggle(options);
        }
        if(content.length != 0){
            content.slideToggle(300);
            if (table.attr('drawn') == 'False'){
                drawTable(table);
            }
        }
        togglePlusMinusSign($(this));
    });

    $('.table_select_master').each(function(){
        $(this).prop('checked', false) ;
    }).click(function(){
        var table = $(this).parents('.display');
        log(table.attr('id'))
        setProcessing(table, true);
        //var fullURL = table.DataTable().ajax.json()['fullURL']
        //var modifiedURL = fullURL.replace(/iDisplayStart=[0-9]*/, 'iDisplayStart=0');
        //var modifiedURL = modifiedURL.replace(/fields=[a-z0-9,_]+&/, 'fields=&')
        if($(this).prop('checked')){
            $.ajax({
                "url": "/setUserSelection?pageURL="+ window.location.pathname+"&tableId=" + table.attr('id') + "&selected=_all",
                "success": function (response) {
                    table.find('tr').each(function () {
                        $(this).addClass('selected');
                    });
                    setProcessing(table, false);
                    $('body').trigger('selectedTableRowsChanged', [table[0].id]);
                }
            })
        } else {
            $.ajax({
                "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&unselected=_all",
                "success": function (response) {
                    table.find('tr').each(function () {
                        $(this).removeClass('selected');
                    });
                    setProcessing(table, false);
                    $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
                }
            })
        }
    });

    $('[id="reloadTableLink"]').click(function(){
        var content = $(this).parent().parent().next(".section_content");
        var table = content.children().children("table");
        var scriptTag = table.children('.tableVars');
        var GETValues=null;
        eval(scriptTag.text())
        var source = url+"?pageURL=" + window.location.pathname + "&fields="+fields;
        if (GETValues != null){
            source += obtainGETValues(GETValues);
        }
        table.DataTable().ajax.url(source);
        table.DataTable().ajax.reload();
    });

    $("body").on('mouseover', '.snippetHover', function(event){
        //showSnippet(this, event);
    });
    $("body").on('mouseout', '.snippetHover',function(){
        //$('#snippetContainer').remove();
    });

    $(".option_checkbox").each(function(){
        $(this).prop('checked', false) ;
    }).click(function() {
        var content = $(this).closest(".section_menu").next(".section_content");
        var table = content.children().children("table");
        var url = '/setUserSelection?pageURL=' + window.location.pathname + '&' +
            '&tableId=' + table.attr('id');
        if ($(this).prop('checked')) {
            url += "&opt_" + $(this).attr('name') + "=True";
        } else {
            url += "&opt_" + $(this).attr('name') + "=False";
        }
        $.ajax({
            'url': url,
            'success':function(response){
                $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
            }
        })
    });

    $('.tableDownloader').click(function(){
        displayDownloadPopup($(this));
    })

    $(document).on('mouseover', '.fieldHelper', function(event){
        displayDownloadFieldHelp(event);
    }).on('mouseout', '.fieldHelper',function(){
        $('.fieldHelpText').removeAttr('style')
    })

    $(document).on('click', '#selectAllFieldsChechbox', function(event){
        selectAllFields(event);
    })

    $('.display').on('dt.stateLoadParams', function(event){
        log(event)
    })

});

function togglePlusMinusSign(sign){
    var src = sign.children('img').attr('src')
    if(sign.attr('type') == 'plus') {
        src = src.replace(/\/[^\/]+\.png/, '/minus_icon_128.png')
        sign.attr('type', 'minus');
    } else if (sign.attr('type') == 'minus'){
        src = src.replace(/\/[^\/]+\.png/, '/plus_icon_128.png')
        sign.attr('type', 'plus');
    }
    sign.children('img').attr('src', src)
}

function obtainGETValues(GETValues){
    var ret = "";
    GETValues.forEach(function(entry){
        ret += "&"+entry;
    });
    return ret;
}

function setProcessing(table, value){
    var oSettings = null;
    table.dataTable().dataTableSettings.some(function(o){
        if (o.nTable.id == $(table).attr('id')){
            oSettings = o;
            return true;
        }
    })
    table.dataTable().oApi._fnProcessingDisplay(oSettings, value);
    if (value) {
        table.parent().parent().parent().css({'pointer-events': 'none'})
    } else {
        table.parent().parent().parent().removeAttr('style')
    }
}

function drawTable(table){
    var language = {
        "processing": "Working on it...",
        "thousands":",",
    };
    var languageParams = {};
    var scriptTag = table.children('.tableVars');
    var GETValues=null;
    eval(scriptTag.text());
    var source = url+"?pageURL=" + window.location.pathname + "&fields="+fields;
    if (GETValues != null){
        source += obtainGETValues(GETValues);
    }
    if (languageParams){
        for(var param in languageParams){
            language[param] = languageParams[param];
        }
    }
    $.fn.dataTable.ext.errMode = 'throw';
    table.DataTable({
        "iDisplayLength": 10,
        "autoWidth": false,
        "serverSide": true,
        "sAjaxSource": source,
        "columnDefs": columnsDefs,
        "language": language,
        "processing": true,
        "fnDrawCallback": function (oSettings) {
            oSettings.json.selecteds.forEach(function(id){
                $("#"+ oSettings.sTableId+" #"+id).addClass('selected');
            });
            set_all_selected(oSettings.sTableId);
        }
    });
    disableLiveInputSearch();
    customSelectCheckbox(table);
    table.attr('drawn', 'True');
}


function set_all_selected(tableId){
    var all_selected = true;
    $('#' + tableId + ' tr').each(function (i, item) {
        if ($(item).attr('class') && !$(item).hasClass('selected')) {
            all_selected = false;
        }
    })
    if (all_selected) {
        $('#' + tableId).find('.table_select_master').prop('checked', true);
    } else {
        $('#' + tableId).find('.table_select_master').prop('checked', false);
    }
}

function disableLiveInputSearch(){
    $("div.dataTables_filter input").unbind()
    .keyup( function (e) {
        if (e.keyCode == 13) {
            var table = $(this).parent().parent().parent().children('table')
            table.dataTable().fnFilter(this.value);
        }
    });
}

function showSnippet(tthis,event){
    var href = $(tthis).attr('href') + "?snippet=true";
    var snippet = "<div id='snippetContainer'>" +
        "<iframe id='snippet' scrolling='no' src=" + href + "/>" +
        "</div>"
    $("body").append(snippet);
    $('#snippetContainer').position({
        my: "left+10 top",
        of: event,
        collision: "fit",
        within: $("#content_container")
    })
    $('#snippet').on('load', function () {
        $(this).css('display', 'block');
    })
}

function customSelectCheckbox(table){
    table.on('click', 'td.select-checkbox', function () {
        var checkbox = $(this);
        var id = checkbox.parent().attr('id');
        if (!checkbox.parent().hasClass('selected')){
            $.ajax({
                "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&selected=" + id,
                "success": function (response) {
                    checkbox.parent().addClass('selected');
                    $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
                    set_all_selected(table.attr('id'))
                }
            })
        } else {
            $.ajax({
                "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&unselected=" + id,
                "success": function (response) {
                    checkbox.parent().removeClass('selected');
                    $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
                    set_all_selected(table.attr('id'))
                }
            })
        }
    });
}
/*
function pushUniqueIn(array, item){
    var index = $.inArray(item, array);
    if (index === -1) {
        array.push(item);
    }
}

function removeFrom(array, item){
    var index = $.inArray(item, array);
    if (index != -1) {
        array.splice(index, 1);
    }
}
*/
/*
function toggleFrom(array, id){
    var index = $.inArray(id, array);
    if (index === -1) {
        array.push(id);
    } else {
        array.splice(index,1);
    }
}*/

function menuToggle(elem){
    if (elem.css('width') == '0px'){
        elem.animate({
            width: parseInt(elem.parent().css("width")) - parseInt(elem.prev(".section_title").css("width"))-35
        },300);
    } else {
        elem.animate({width:0},300);
    }
}
/*
function getSourcesFromSelectedRows(){
    var sources = "";
    for (var i = 0; i<selectedTableRows.length; i++){
        sources += selectedTableRows[i]+",";
    }
    return "&selected_rows="+sources;
}
*/
function formatTweetText(text){
    text = linkifyStr(text, {linkClass :"TableToolLink"})

    //log(text);
    var userRegex = /@([A-Z]|[0-9]|_)+/ig;
    var usernames = text.match(userRegex);
    if (usernames != null) {
        usernames.forEach(function (username) {
            //log(username);
            text = text.replace(username, '<a class="TableToolLink snippetHover" target="_blank" href="/twitter/user/' + username.slice(1) + '">' + username + '</a>');
        });
    }

    var hashtagRegex = /#([A-Z]|[0-9]|_)+/ig;
    var hashtags = text.match(hashtagRegex);
    if (hashtags != null) {
        hashtags.forEach(function (hashtag) {
            //log(hashtag);
            text = text.replace(hashtag, '<a class="TableToolLink" target="_blank" href="/twitter/hashtag/' + hashtag.slice(1) + '">' + hashtag + '</a>');
        });
    }

    return text;
}

/*
function filterSelectedTableRows(filterStr, exclude){
    if(exclude == 'exclude'){
        return selectedTableRows.filter(function (item) {
            return !item.match(filterStr);
        })
    } else {
        return selectedTableRows.filter(function (item) {
            return item.match(filterStr);
        })
    }
}
*/

function displayDownloadPopup(link){
    setSelectedRows(link);
    setAvailableFields(link)

    displayCenterPopup('downloadSelection');
}

function setAvailableFields(link){
    var fields = link.children('.downloadFields').children()
    $('#centerPopupContent').html('')
    $('#downloadFieldsTable').html(
        '<tr>' +
        '   <td><input type="checkbox"id="selectAllFieldsChechbox"name="masterFieldSelector"></td>' +
        '   <td><b>Select all fields</b></td>' +
        '</tr>'
    );
    fields.each(function(i){
        if (i%3 == 0){
            var item1 = $(fields[i]);
            var item2 = $(fields[i+1]);
            var item3 = $(fields[i+2]);
            var str = '<tr>' +
                '   <td><input class="fieldSelector" type="checkbox" name="' + item1.attr('field') + '"></td>' +
                '   <td>' + item1.html() + '</td>' +
                '   <td> ' +
                '       <a class="fieldHelper">?</a> ' +
                '       <div class="fieldHelpText">' + item1.attr('helper') + '</div>' +
                '   </td>'
            if (item2.length != 0){
                str += '   <td> </td>' +
                    '   <td><input class="fieldSelector" type="checkbox" name="' + item2.attr('field') + '"></td>' +
                    '   <td>' + item2.html() + '</td>' +
                    '   <td> ' +
                    '       <a class="fieldHelper">?</a> ' +
                    '       <div class="fieldHelpText">' + item2.attr('helper') + '</div>' +
                    '   </td>'
            } else { str+= '</tr>' }
            if (item3.length != 0) {
                str += '   <td> </td>' +
                    '   <td><input class="fieldSelector" type="checkbox" name="' + item3.attr('field') + '"></td>' +
                    '   <td>' + item3.html() + '</td>' +
                    '   <td> ' +
                    '       <a class="fieldHelper">?</a> ' +
                    '       <div class="fieldHelpText">' + item3.attr('helper') + '</div>' +
                    '   </td>'
            } else {str += '</tr>'}
            $('#downloadFieldsTable tr:last').after(str);
        }
    });
}


function setSelectedRows(link){
    var itemClass = link[0].id
    lastPopupId = null;
    $('#downloadSelection').find('#itemType').attr('value', itemClass);
    var displayer = $('#downloadSelection').children('#content').children().children('#selectedRowsCount');
    var length = filterSelectedTableRows(itemClass).length
    displayer.html("" + length + " lines selected");
}


function downloadSelectedRows(elem) {
    var fileType = $(elem).parent().parent().find('.fileTypeSelect').filter(function(i,f){return f.checked})[0].value;
    var itemClass = $(elem).parent().parent().find('#itemType').attr('value');
    var fields = $(elem).parent().parent().find('.fieldSelector')
        .filter(function(i,f){return f.checked}).map(function (i, item) {return item.name})
    var ref = '/twitter/downloadTable?fileType=' + fileType + '&selectedTableRows=';
    filterSelectedTableRows(itemClass).forEach(function (item) {
        ref += item + ',';
    })
    ref = ref.slice(0, -1)
    ref += '&fields=';
    fields.each(function(i,item){
        ref += item+',';
    })
    ref = ref.slice(0, -1)
    window.location = ref
}

function displayDownloadFieldHelp(event){
    var text = $(event.target).siblings('.fieldHelpText')
    text.position({
        my: "left+10 top",
        of: event,
        collision: "fit",
        within: $("#content_container")
    })
    text.show()
}


function selectAllFields(event){
    var masterSelector = $(event.target);
    if (masterSelector.prop('checked')){
        masterSelector.parent().parent().parent().find('.fieldSelector').each(function(i,item){
            $(item).prop('checked',true);
        })
    } else {
        masterSelector.parent().parent().parent().find('.fieldSelector').each(function (i, item) {
            $(item).prop('checked', false);
        })
    }
}

function reloadTable(tableId){
    var table = $('table'+tableId+'.display.dataTable');
    var scriptTag = table.children('.tableVars');
    var dynamicSource = true;
    var GETValues = null;
    eval(scriptTag.text())
    var source = url + "?pageURL=" + window.location.pathname + "&fields=" + fields;
    /*if (dynamicSource) {
        source += getSourcesFromSelectedRows();
    }*/
    if (GETValues != null) {
        source += obtainGETValues(GETValues);
    }
    //table.DataTable().ajax.url(source);
    table.DataTable().ajax.reload(function(response){
        //log(table)
        //log(response)
    },false);
}