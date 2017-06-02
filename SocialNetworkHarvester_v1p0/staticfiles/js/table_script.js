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
    var img = sign.children().children('img')
    if (sign.attr('type') == 'plus') {
        img.css("margin-left", "-200%");
        sign.attr('type', 'minus');
    } else if (sign.attr('type') == 'minus') {
        img.css("margin-left", "-300%");
        sign.attr('type', 'plus');
    }
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

function drawTable(table, fnDrawCallback, fnDrawCallbackKwargs){
    var language = {
        "decimal": "",
        "emptyTable": "Pas de données disponibles",
        "info": "Présentation de _START_ à _END_ de _TOTAL_ entrées",
        "infoEmpty": "",
        "infoFiltered": "(filtré de _MAX_ entrées au total)",
        "infoPostFix": "",
        "thousands": ",",
        "lengthMenu": "Voir _MENU_ lignes",
        "loadingRecords": "En cours de téléchargement...",
        "processing": "En traitement...",
        "search": "Recherche:",
        "zeroRecords": "Aucune entrée ne correspond à votre recherche.",
        "paginate": {
            "first": "Première page",
            "last": "Dernière page",
            "next": "Suivant",
            "previous": "Précédent"
        },
        "aria": {
            "sortAscending": ": activer pour ordonner les colomnes en ordre croissant",
            "sortDescending": ": activer pour ordonner les colomnes en ordre décroissant"
        }
    };
    var languageParams = {};
    var dynamic=false;
    var scriptTag = table.children('.tableVars');
    eval(scriptTag.text());
    var source = makeUrl('/tool/ajaxTable',{
        tableId     :   table.attr('id'),
        pageURL     :   window.location.pathname,
        fields      :   getFieldsStr(columns),
        modelName   :   modelName,
        dynamic     :   dynamic,
        srcs        :   JSON.stringify(srcs),
    });

    if (languageParams){
        for(var param in languageParams){
            language[param] = languageParams[param];
        }
    }
    createTableHead(table, columns);
    $.fn.dataTable.ext.errMode = 'throw';
    table.DataTable({
        "iDisplayLength": 10,
        "autoWidth": false,
        "serverSide": true,
        "sAjaxSource": source,
        "columnDefs": defineColumns(columns),
        "language": language,
        "processing": true,
        "fnDrawCallback": function (oSettings) {
            oSettings.json.selecteds.forEach(function(id){
                $("#"+ oSettings.sTableId+" #"+id).addClass('selected');
            });
            set_all_selected(table);
            setTableSelectedCountDisplay(table)
            if (fnDrawCallback != null){
                fnDrawCallback(fnDrawCallbackKwargs);
            }
        }
    });
    slowLiveInputSearch();
    customSelectCheckbox(table);
    if (dynamic){
        setDynamicReload(table, srcs.map(function(item){
            if(item.hasOwnProperty("tableId")){return item.tableId}
        }));
    }
    table.attr('drawn', 'True');
}

function defineColumns(columns){
    var columnsDefs = [
        {
            "orderable": false,
            "searchable": false,
            "className": 'select-checkbox',
            "targets": 0,
            "render": function () {
                return ""
            }
        },
    ];
    columns.forEach(function(col,i){
        if (!col.hasOwnProperty("orderable") || !col["orderable"]){
            col["asSorting"] = default_asSorting;
        }
        if (!col.hasOwnProperty("searchable")) {
            col["searchable"] = true;
        }
        col["targets"] = i+1;
        columnsDefs.push(col);
    });
    log(columnsDefs);
    return columnsDefs
}


function getFieldsStr(columns){
    var mainFields = [];
    var otherFields = [];
    columns.forEach(function (col, i) {
        mainFields.push(col['fields'][0]);
        for(var j=1;i<col['fields'].length;i++){
            if(otherFields.indexOf(col['fields'][j])<0){
                otherFields.push(col['fields'][j]);
            }
        }
    });
    log(mainFields.join() + "," + otherFields.join())
    return mainFields.join()+","+otherFields.join();
}


function createTableHead(table, columns){
    var thead = "<thead><tr><th><input type='checkbox' class='table_select_master'> </input> </th>";
    columns.forEach(function (col, i) {
        var colStr = "";
        if (col.hasOwnProperty("colStr")){colStr = col["colStr"];}
        thead += "<th>" + colStr + "</th>";
    });
    thead += "</tr></thead>";
    table.html(thead);
    $(table).find("input.table_select_master").click(function () {
        selectAllRows($(this));
    });
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
        var url = makeUrl('/setUserSelection', {
            pageURL     :   window.location.pathname,
            tableId     :   table.attr('id'),
        });
        if (!checkbox.parent().hasClass('selected')){
            $.ajax({
                "url": makeUrl(url, {selected:id}),
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
                "url": makeUrl(url, {unselected: id}),
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
    if (text === null){return '<i>Undefined</i>'}
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
        "<tr>" +
        "    <td><input type='checkbox' id='selectAllFieldsChechbox' name='masterFieldSelector'></td>" +
        "    <td><b>Sélectionner tous les champs</b></td>" +
        "    <td><a class='fieldHelper'>?</a>" +
        "        <div class='fieldHelpText'>" +
        "            Ralentira la création du fichier de beaucoup! N'utiliser cette fonction que si vous " +
        "            nécéssitez VRAIMENT tous les champs des objects.'" +
        "        </div>" +
        "    </td>" +
        "</tr>"
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
    var displayer = $('#downloadSelection').children('#content')
        .children().children().find('#selectedRowsCount');
    var tableIdContainer = displayer.parent().find('#selectedTableId');
    var tableTitleDisplay = displayer.parent().find('#selectedTableTitle');
    displayer.html("" + (length?length:0) + " lignes sélectionnées dans la table");
    tableIdContainer.html(table[0].id)
    tableTitleDisplay.html(tableTitle)

}


function downloadSelectedRows(elem) {
    var delimiter = $(elem).parent().parent().find('.delimiterSelector').find(":selected").attr("value");
    var os = $(elem).parent().parent().find('.osSelector').find(":selected").attr("value");
    var fileType = $(elem).parent().parent().find('.fileTypeSelect').filter(function(i,f){return f.checked})[0].value;
    var tableId = $(elem).parent().parent().find('#selectedTableId').html()
    var baseURL = $(elem).parent().parent().find('#sourceURL').attr('value');
    var filename = $(elem).parent().parent().find('#DownloadfileName').attr('value');
    var bar = $(elem).parent().parent().find('#progressBar');
    if (baseURL.indexOf('?') > -1){
        sourceURL = baseURL +'&';
    } else {
        sourceURL = baseURL + '?';
    }
    var ref = sourceURL+'download=true&pageURL='+ window.location.pathname+
        '&fileType=' + fileType +
        '&filename='+filename +
        '&delimiter='+delimiter+
        '&selected_os='+os+
        '&tableId='+ tableId+
        '&fields=';
    var fields = $(elem).parent().parent().find('.fieldSelector')
        .filter(function (i, f) {return f.checked}).map(function (i, item) {return item.name})
    fields.each(function(i,item){
        ref += item+',';
    });
    ref = ref.slice(0, -1);
    if(fields.length == 0) {
        alert("Please select at least one field.")
    } else {
        window.location = ref;
        displayDownloadProgress(bar);
    }
}

function displayDownloadFieldHelp(event){
    var text = $(event.target).siblings('.fieldHelpText')
    text.position({
        my: "right-10 bottom-10",
        of: event,
        collision: "fit",
        within: $("#centerPopupOutter")
    });
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
        });
    }
}

function reloadTable(tableId){
    var table = $('table'+tableId+'.display.dataTable');
    table.addClass('unselectable');
    table.DataTable().ajax.reload(function(response){
        selectedCounts[tableId] = response['selectedCount']
        setTableSelectedCountDisplay(table)
        table.remove('unselectable');
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
            ' (dont ' + curSelect + ' ligne'+ (curSelect > 1 ? 's' : '')+' sélectionnée'+
            (curSelect>1?'s':'')+' d\'un total de '+totSelect+' sélection'+
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


var downloadProgressUpdateTimer = null;
var lastLinesTransfered = -1;
function displayDownloadProgress(progressBar){
    progressBar.parent().show();
    progressBar.parent().parent().find("#selectedCountContainer").hide();
    progressBar.parent().parent().find("#submitButton").attr("disabled", true);
    var progressPercent = progressBar.siblings('#progressPercent');
    var pageURL = window.location.pathname;
    var tableId = progressBar.parent().parent().find("#selectedTableId").html();
    var url = '/tool/downloadProgress?tableId='+tableId+'&pageURL='+pageURL;
    clearInterval(downloadProgressUpdateTimer);
    downloadProgressUpdateTimer = setInterval(function(){
        $.ajax({
            url: url,
            success: function (response) {
                var progress = response['downloadProgress'];
                var linesTransfered = response['linesTransfered'];
                if (progress == "-1"){
                    clearInterval(downloadProgressUpdateTimer);
                    closeCenterPopup();
                    displayNewErrors(['Une erreur est survenue sur le serveur. Veuillez réessayer.'], 0);
                } else {
                    progressBar.val(progress);
                    progressPercent.html(' '+progress+'%')
                    if (progress == "100"){
                        clearInterval(downloadProgressUpdateTimer);
                        closeCenterPopup();
                        displayNewMessages(['Le téléchargement s\'est complété avec succès.']);
                    }
                }
                if (linesTransfered == lastLinesTransfered && progress != "100"){
                    clearInterval(downloadProgressUpdateTimer);
                    closeCenterPopup();
                    displayNewErrors(['Le téléchargement as été interrompu ou encore le suivi du progrès en temps réel a échoué.'], 0);
                } else {
                    lastLinesTransfered = linesTransfered;
                }
            }
        })
    }, 2000)
}

var autoRefreshs = [];
function setDynamicReload(tthis, sources_TableIds){
    $(document).ready(function () {
        if (autoRefreshs.indexOf(tthis.attr("id")) < 0) {
            autoRefreshs.push(tthis.attr("id")) // insure that this "bind" fct is called only once per page
            $('body').bind('selectedTableRowsChanged', function (event, tableId) {
                if (tableId == 'FbPagesTable') {
                    reloadTable('#FBPostTable');
                }
            });
        }
    });
}