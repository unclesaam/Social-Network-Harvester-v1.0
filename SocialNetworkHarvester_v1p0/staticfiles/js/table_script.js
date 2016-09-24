$.getScript("/static/js/DataTables-1.10.9/js/jquery.dataTables.min.js")
$.getScript("/static/js/Select-1.0.1/js/dataTables.select.min.js")
$.getScript("/static/js/linkify/linkify.min.js", function(){
    $.getScript("/static/js/linkify/linkify-string.min.js")
})

var default_asSorting = ["desc", "asc", "none"];
var selectedCounts = {};

$(document).ready(function() {

    $(".section_title, .tableOpenCloseIcon").click(function(){
        toggleTableView($(this));
    });

    $('.table_select_master').each(function(){
        $(this).prop('checked', false) ;
    }).click(function(){
        selectAllRows($(this));
    });

    $('[id="reloadTableLink"]').click(function(){
        var content = $(this).parent().parent().next(".section_content");
        var table = content.children().children("table");
        reloadTable('#'+table.attr('id'))
    });

    // SHOW SNIPPETS //
    $("body").on('mouseover', '.snippetHover', function(event){
        //showSnippet(this, event);
    }).on('mouseout', '.snippetHover',function(){
        //$('#snippetContainer').remove();
    });

    $(".option_checkbox").each(function(){
        $(this).prop('checked', false) ;
    }).click(function() {
        selectRow($(this));
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

function toggleTableView(section){
    var content = section.parent().next(".section_content");
    var options = section.parent().find(".section_options");
    var table = content.children();
    if (options.length != 0) {
        menuToggle(options);
    }
    if (content.length != 0) {
        content.slideToggle(300);
        if (table.attr('drawn') == 'False') {
            drawTable(table);
        }
    }
    togglePlusMinusSign(section.parent().children(".tableOpenCloseIcon"));
}

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

function selectRow(checkbox){
    var content = checkbox.closest(".section_menu").next(".section_content");
    var table = content.children().children("table");
    var url = '/setUserSelection?pageURL=' + window.location.pathname + '&' +
        '&tableId=' + table.attr('id');
    if (checkbox.prop('checked')) {
        url += "&opt_" + checkbox.attr('name') + "=True";
    } else {
        url += "&opt_" + checkbox.attr('name') + "=False";
    }
    $.ajax({
        'url': url,
        'success': function (response) {
            table.DataTable().ajax.reload(null, false)
            //$('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
        }
    })
}

function selectAllRows(checkbox){
    var table = checkbox.parents('.display');
    setProcessing(table, true);
    if (checkbox.prop('checked')) {
        $.ajax({
            "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&selected=_all",
            "success": function (response) {
                setSelectedRows(response['selectedCount'])
                table.find('tr').each(function () {
                    $(this).addClass('selected');
                });
                setTableSelectedCountDisplay(table)
                setProcessing(table, false);
                $('body').trigger('selectedTableRowsChanged', [table[0].id]);
            }
        })
    } else {
        $.ajax({
            "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&unselected=_all",
            "success": function (response) {
                setSelectedRows(response['selectedCount'])
                table.find('tr').each(function () {
                    $(this).removeClass('selected');
                });
                setTableSelectedCountDisplay(table)
                setProcessing(table, false);
                $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
            }
        })
    }
}

function setSelectedRows(counts){
    if(counts){
        $.each(counts,function(key,val){
            selectedCounts['#'+ key] = val;
        });
    }
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
    eval(scriptTag.text());
    if (url.indexOf('?') > -1) {
        url = url + '&';
    } else {
        url = url + "?";
    }
    var source = url+"pageURL=" + window.location.pathname + "&fields="+fields;
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
        //"stateSave": true,
        "fnDrawCallback": function (oSettings) {
            oSettings.json.selecteds.forEach(function(id){
                $("#"+ oSettings.sTableId+" #"+id).addClass('selected');
            });
            set_all_selected(table);
            setTableSelectedCountDisplay(table)
        }
    });
    slowLiveInputSearch();
    customSelectCheckbox(table);
    table.attr('drawn', 'True');
}


function set_all_selected(table){
    var all_selected = true;
    table.find('tr').each(function (i, item) {
        if ($(item).attr('class') && !$(item).hasClass('selected')) {
            all_selected = false;
        }
    })
    if (all_selected) {
        table.find('.table_select_master').prop('checked', true);
    } else {
        table.find('.table_select_master').prop('checked', false);
    }
}

var resetRecentInput = null;
function slowLiveInputSearch(){
    $("div.dataTables_filter input").unbind()
    .keyup(function () {
        clearTimeout(resetRecentInput);
        var t = this
        resetRecentInput = setTimeout(function () {
            var table = $(t).parent().parent().parent().children('table')
            table.dataTable().fnFilter(t.value);
        }, 600);
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
        within: $("body")
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
                    setSelectedRows(response['selectedCount'])
                    checkbox.parent().addClass('selected');
                    $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
                    set_all_selected($(table))
                    setTableSelectedCountDisplay($(table))
                }
            })
        } else {
            $.ajax({
                "url": "/setUserSelection?pageURL=" + window.location.pathname + "&tableId=" + table.attr('id') + "&unselected=" + id,
                "success": function (response) {
                    setSelectedRows(response['selectedCount'])
                    checkbox.parent().removeClass('selected');
                    $('body').trigger('selectedTableRowsChanged', [table.attr('id')]);
                    set_all_selected($(table))
                    setTableSelectedCountDisplay($(table))
                }
            })
        }
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

function displayDownloadPopup(link){
    setDownloadableRows(link);
    setAvailableFields(link)
    displayCenterPopup('downloadSelection');
}

function setAvailableFields(link){
    var fields = link.children('.downloadFields').children()
    $('#centerPopupContent').html('')
    $('#DownloadfileName').attr('value', link.attr('filename'));
    $('#downloadFieldsTable').html(
        '<tr>' +
        '   <td><input type="checkbox"id="selectAllFieldsChechbox"name="masterFieldSelector"></td>' +
        '   <td><b>Select all fields</b></td>' +
        '   <td>' +
        '       <a class="fieldHelper">?</a>' +
        '       <div class="fieldHelpText">' +
        '           Will select all available fields. Selecting all fields will slow down the generation ' +
        '           of the file by a lot. Use only if you really need all this informations.' +
        '       </div>' +
        '   </td>'+
        '</tr>'
    );
    var i, j, temparray, chunk = 4;
    for (i = 0, j = fields.length; i < j; i += chunk) {
        temparray = fields.slice(i, i + chunk);
        var str = '<tr>';
        temparray.each(function(i,item){
            item = $(item);
            str +=
                '<td><input class="fieldSelector" type="checkbox" name="' + item.attr('field') + '"></td>' +
                '   <td>' + item.html() + '</td>' +
                '   <td> ' +
                '       <a class="fieldHelper">?</a> ' +
                '       <div class="fieldHelpText">' + item.attr('helper') + '</div>' +
                '   </td>'
        });
        str += '</tr>';
        $('#downloadFieldsTable tr:last').after(str);
    }
}


function setDownloadableRows(link){
    var table = link.parent().parent().parent().find('table.display');
    var tableTitle = table.parent().parent().parent().find('.section_title').html()
    var length = selectedCounts['#'+table[0].id];
    eval(table.children('.tableVars').text())
    var sourceURL = url;
    lastPopupId = null;
    $('#downloadSelection').find('#sourceURL').attr('value', sourceURL);
    var displayer = $('#downloadSelection').children('#content').children().children('#selectedRowsCount');
    var tableNameContainer = displayer.parent().children('#selectedTableName');
    var tableTitleDisplay = displayer.parent().children('#selectedTableTitle')
    displayer.html("" + (length?length:0) + " rows selected in");
    tableNameContainer.html(table[0].id)
    tableTitleDisplay.html(tableTitle)

}


function downloadSelectedRows(elem) {
    var fileType = $(elem).parent().parent().find('.fileTypeSelect').filter(function(i,f){return f.checked})[0].value;
    var sourceURL = $(elem).parent().parent().find('#sourceURL').attr('value');
    var filename = $(elem).parent().parent().find('#DownloadfileName').attr('value');
    log(filename)
    var ref = sourceURL+'?download=true&pageURL='+
        window.location.pathname+'&fileType=' + fileType +
        '&filename='+filename + '&fields=';
    var fields = $(elem).parent().parent().find('.fieldSelector')
        .filter(function (i, f) {return f.checked}).map(function (i, item) {return item.name})
    fields.each(function(i,item){
        ref += item+',';
    })
    ref = ref.slice(0, -1);
    if(fields.length == 0) {
        alert("Please select at least one field.")
    } else {
        window.location = ref
    }
}

function displayDownloadFieldHelp(event){
    var text = $(event.target).siblings('.fieldHelpText')
    text.position({
        my: "right-10 bottom-10",
        of: event,
        collision: "fit",
        within: $("#centerPopupOutter")
    })
    text.css('display', 'block');
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
    table.DataTable().ajax.reload(function(response){
        selectedCounts[tableId] = response['selectedCount']
        setTableSelectedCountDisplay(table)
    },false);
}

function setTableSelectedCountDisplay(table){
    var disp = table.next('.dataTables_info');
    if (disp.children('#selectShowing').length == 0) {
        var text = disp.html();
        text += '<span id="selectShowing"></span>';
        disp.html(text);
    }
    var totSelect = selectedCounts['#'+table.attr('id')];
    var curSelect = table.find('.selected').filter(function(i, item){
        return item.id;
    }).length;
    if (totSelect > 0){
        disp.children('#selectShowing').html(
            ' (Showing ' + curSelect + ' selected row'+
            (curSelect>1?'s':'')+' out of '+totSelect+' selection'+
            (totSelect>1?'s':'')+')'
        );
    } else {
        disp.children('#selectShowing').html('');
    }
}

function executeAjaxAndDisplayMessages(url, tableId){
    $.ajax({
        'url': url,
        'success': function (response) {
            $('#centerPopupOutter').hide();
            reloadTable(tableId)
            if (response['status'] == 'ok') {
                displayNewMessages(response['messages'])
            } else if (response['status'] == 'exception') {
                displayNewErrors(response['errors'])
            };
        }
    })
}


function getNumberOfSelectedRows(tableId){
    var table = $('table' + tableId + '.display.dataTable');
    //log(table)
}