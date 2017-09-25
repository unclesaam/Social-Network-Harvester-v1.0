$.getScript("/static/js/DataTables-1.10.9/js/jquery.dataTables.min.js",function(){
    openSections();
})
$.getScript("/static/js/Select-1.0.1/js/dataTables.select.min.js", function(){
    $.fn.dataTable.ext.errMode = function ( settings, helpPage, message ) {
        //log(settings);log(helpPage);log("message: "+message);
        displayNewErrors(['Une erreur est survenue. Veuillez contacter l\'administrateur.']);
    };
})
$.getScript("/static/js/linkify/linkify.min.js", function(){
    $.getScript("/static/js/linkify/linkify-string.min.js")
})

var default_asSorting = ["desc", "asc", "none"];
var selectedCounts = {};
var tableBindingMap = {}

$(document).ready(function() {

    $(".section_title, .tableOpenCloseIcon").click(function(){
        toggleSectionView($(this));
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
    }).bind('selectedTableRowsChanged', function (event, tableId) {
        if (tableBindingMap.hasOwnProperty(tableId)) {
            for (var i = 0; i < tableBindingMap[tableId].length; i++) {
                reloadTable('#' + tableBindingMap[tableId][i]);
            }
        }
    });

    $(".option_checkbox").each(function(){
        $(this).prop('checked', false) ;
    }).click(function() {
        selectRow($(this));
    });

    $('.tableDownloader').click(function(){
        displayDownloadPopup($(this));
    });

    $(document).on('mouseover', '.fieldHelper', function(event){
        displayDownloadFieldHelp(event);
    }).on('mouseout', '.fieldHelper',function(){
        $('.fieldHelpText').removeAttr('style')
    });

    $(document).on('click', '#selectAllFieldsChechbox', function(event){
        selectAllFields(event);
    });

    $('.display').on('dt.stateLoadParams', function(event){
        log(event)
    });

});



function toggleSectionView(section){
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

function openSections(){
    var hash = window.location.hash;
    if (hash != ""){
        hash.split('#').forEach(function(item, i){
            if (item == "allTables"){
                $('.display').each(function(i,obj) {
                    toggleSectionView($(obj).parent().parent().find('.section_title'));
                });
            }else if (item != ""){
                var obj = $("#"+item);
                log(obj.parent().parent().find('.section_title'))
                //setTimeout(function(){
                    toggleSectionView(obj.parent().parent().find('.section_title'));
                //},500)
            };
        });
    }
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
    var url = makeUrl("/tool/table/selection", {
        pageURL: window.location.pathname,
        tableId: table.attr('id'),
    });
    if (checkbox.prop('checked')) {
        url += "&opt_" + checkbox.attr('name') + "=True";
    } else {
        url += "&opt_" + checkbox.attr('name') + "=False";
    }
    $.ajax({
        'url': url,
        'success': function (response) {
            table.DataTable().ajax.reload(null, false)
        }
    })
}


function selectAllRows(checkbox){
    var table = checkbox.parents('.display');
    setProcessing(table, true);
    var dynamic = false;
    eval(getTableVars(table))
    var url = makeUrl("/tool/table/selection", {
        tableId: table.attr('id'),
        pageURL: window.location.pathname,
        fields: getFieldsStr(columns),
        modelName: modelName,
        dynamic: dynamic,
        srcs: JSON.stringify(srcs),
    });
    if (checkbox.prop('checked')) {
        $.ajax({
            "url": makeUrl(url,{selected: "_all"}),
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
            "url": makeUrl(url, {unselected: "_all"}),
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
    var dynamic = false;
    eval(getTableVars(table));
    var source = makeUrl('/tool/table/ajax',{
        tableId     :   table.attr('id'),
        pageURL     :   window.location.pathname,
        fields      :   getFieldsStr(columns),
        modelName   :   modelName,
        dynamic     :   dynamic,
        srcs        :   JSON.stringify(srcs),
    });

    if (typeof languageParams !== 'undefined'){
        for(var param in languageParams){
            language[param] = languageParams[param];
        }
    }
    createTableHead(table, columns);
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
        },
    });
    slowLiveInputSearch();
    customSelectCheckbox(table);
    setHighlightFilteredWords(table);
    if (dynamic){
        srcs.forEach(function(item, i){
            if(item.hasOwnProperty("tableId")){
                addReloadBinding(item['tableId'], table.attr('id'));
            }
        });
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
    return columnsDefs
}


function getFieldsStr(columns){
    var mainFields = [];
    var otherFields = [];
    columns.forEach(function (col, i) {
        mainFields.push(col['fields'][0]);
        for(var j=1;j<col['fields'].length;j++){
            if(otherFields.indexOf(col['fields'][j])<0){
                otherFields.push(col['fields'][j]);
            }
        }
    });
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

function setHighlightFilteredWords(table){
    table.on('draw.dt', function(){
        var term = table.DataTable().search();
        table.DataTable().rows().every(function (rowIdx, tableLoop, rowLoop) {
            var rowNode = this.node();
            $(rowNode).find("td:visible").each(function () {
                highlight(term, $(this));
            });
        });
    })

}

RegExp.escape = function (text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/gi, "\\$&");
}

function highlight(term, base) {
    if (!term) return;
    var re = new RegExp(RegExp.escape(term), "gi"); //... just use term
    var replacement = "<span class='highlight'>" + term + "</span>";
    $("*", base).contents().each(function (i, el) {
        if (el.nodeType === 3) {
            var data = el.data;
            if (data = data.replace(re, replacement)) {
                var wrapper = $("<span>").html(data);
                $(el).before(wrapper.contents()).remove();
            }
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
        var url = makeUrl('/tool/table/selection', {
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
    var dynamic = false;
    eval(getTableVars(table));
    var url = makeUrl('/tool/table/ajax', {
        tableId: table.attr('id'),
        pageURL: window.location.pathname,
        //fields: getFieldsStr(columns),
        modelName: modelName,
        dynamic: dynamic,
        srcs: JSON.stringify(srcs),
    });
    lastPopupId = null;
    $('#downloadSelection').find('#sourceURL').attr('value', url);
    var displayer = $('#downloadSelection').children('#content').find('#selectedRowsCount');
    var tableIdContainer = displayer.parent().find('#selectedTableId');
    var tableTitleDisplay = displayer.parent().find('#selectedTableTitle');
    displayer.html("" + (length?length:0) + " lignes sélectionnées dans la table");
    tableIdContainer.html(table[0].id)
    tableTitleDisplay.html(tableTitle)

}

var tableVarsList = {};
function getTableVars(table){
    var scriptTag = table.children('.tableVars');
    if (!tableVarsList.hasOwnProperty(table.attr('id'))){
        tableVarsList[table.attr('id')] = scriptTag.text()
    }
    return tableVarsList[table.attr('id')];
}


function downloadSelectedRows(elem) {
    var params = $(elem).parent().parent();
    var strFields = "";
    var fields = params.find('.fieldSelector').filter(function (i, f) {
        return f.checked
    }).map(function (i, item) {
        strFields += item.name+",";
        return item.name
    });
    strFields = strFields.slice(0,strFields.length-1);
    log(strFields);
    var ref =  makeUrl(params.find('#sourceURL').attr('value'), {
        download:   true,
        pageURL:    window.location.pathname,
        fileType:   params.find('.fileTypeSelect').filter(function (i, f) {
                        return f.checked
                    })[0].value,
        filename:   params.find('#DownloadfileName').attr('value'),
        delimiter:  params.find('.delimiterSelector').find(":selected").attr("value"),
        os:         params.find('.osSelector').find(":selected").attr("value"),
        tableId:    params.find('#selectedTableId').html(),
        fields:     strFields,
    })
    if(fields.length == 0) {
        alert("Please select at least one field.")
    } else {
        window.location = ref;
        displayDownloadProgress(params.find('#progressBar'));
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
    clearInterval(downloadProgressUpdateTimer);
    downloadProgressUpdateTimer = setInterval(function(){
        $.ajax({
            url: makeUrl("/tool/table/downloadProgress", {
                tableId: progressBar.parent().parent().find("#selectedTableId").html(),
                pageURL: window.location.pathname,
            }),
            success: function (response) {
                var progress = response['downloadProgress'];
                var linesTransfered = response['linesTransfered'];
                if (progress == "-1"){
                    clearInterval(downloadProgressUpdateTimer);
                    closeCenterPopup();
                    displayNewErrors(['Une erreur est survenue sur le serveur. Veuillez réessayer.'], 60);
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
                    displayNewErrors(['Le téléchargement as été interrompu ou encore le suivi du progrès en temps réel a échoué.'], 60);
                } else {
                    lastLinesTransfered = linesTransfered;
                }
            }
        })
    }, 2000)
}

function addReloadBinding(srcTableId, thisTableId){
    if (!tableBindingMap.hasOwnProperty(srcTableId)){
        tableBindingMap[srcTableId] = [];
    }
    tableBindingMap[srcTableId].push(thisTableId);
}

function removeReloadBinding(srcTableId, thisTableId){
    //TODO: make binding great again
}

function undefinedTag(){
    return '<i>indéfini</i>';
}

function centeredTag(text){
    if (text == null){return "";}
    return "<center>"+text+"</center>";
}