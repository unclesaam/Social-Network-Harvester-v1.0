$.getScript("/static/js/jquery.actual.min.js")
$.getScript("/static/js/jquery-ui.js")



$(document).ready(function() {
    var menu = $("#side_menu");
    var OVERLAYING_TRESHOLD = 1200;
    
    if ($(window).width() <= OVERLAYING_TRESHOLD){
        menu.hide();
    }
    setContentPaneWidth();
    menu.height($( window ).height())

    $("#menu_select").click(function(){
        var overlaying = false;
        if (menu.css('display') != 'none') {
            menu.hide();
        }else{
            if ($(window).width() <= OVERLAYING_TRESHOLD){
                overlaying = true;
                menu.bind("clickoutside", function(){hide_menu();});
                $('.left_menu_item:not(#analysis_box)').click(function(){hide_menu();});
                $('.sub_left_menu_item').click(function(){hide_menu();});
            }
            menu.show();
        }
        setContentPaneWidth(overlaying);
    });
    
    $(window).resize(function(){
        if ($(window).width() <= OVERLAYING_TRESHOLD){
            menu.hide();
        } else if ($(window).width() >= OVERLAYING_TRESHOLD+300){
            menu.show();
        }
        setContentPaneWidth(false);
    });
    
    $('#login_button').click(function(){
        toggleLoginMenu();
    });
    
    $('#analysis_box').click(function(){
        var toolMenu = $('#SubLeftMenu');
        toolMenu.slideToggle(300);
    });
    $(".yetToCome").each(function(){
        if(!DEBUG){
            $(this).hide();
        }
        $(this).append(
            "<div class='yetToComeBox'>" +
                "À venir..."+
            "</div>")
        var yetToComeBox = $(this).children(".yetToComeBox");
        yetToComeBox.css("top", $(this).height() / 2 - yetToComeBox.height() / 2);
        yetToComeBox.css("left", $(this).width() / 2 - yetToComeBox.width() / 2);
    }).mouseover(function(){
        var yetToComeBox = $(this).children(".yetToComeBox");
        //log($(this).height() / 2 - yetToComeBox.height() / 2)
        //log($(this).width() / 2 - yetToComeBox.width() / 2)
        //log(yetToComeBox)
        yetToComeBox.css("top", $(this).height()/2 - yetToComeBox.height()/2);
        yetToComeBox.css("left", $(this).width()/2 - yetToComeBox.width()/2);
    })

    $("#centerPopupCloser").click(function(){
        closeCenterPopup();
        lastPopupId = null;
    });
    $("body").on('mouseover', '#centerPopupHelper', function (event) {
        $('#centerPopupHelpText').position({
            my: "right-10 bottom-10",
            of: event,
            collision: "fit",
            within: $("#centerPopupOutter")
        })
        $('#centerPopupHelpText').css('display', 'block');
    });
    $("body").on('mouseout', '#centerPopupHelper', function(){
        $('#centerPopupHelpText').removeAttr('style');
    });

    addWheelListener($("#centerPopupOutter")[0], function (event) {
        event.preventDefault();
        event.stopPropagation();
        //log(event.deltaY)
        var inner = $("#centerPopupInner")
        if(inner.height() > $(window).height()){
            var val = parseInt(inner.css('marginTop'), 10);
            val -= event.deltaY * 10;
            var maxOffset = 30;
            if (val > maxOffset) {
                val = maxOffset;
            }
            var min = inner.height() - $("#centerPopupOutter").height();
            if (val < -min-maxOffset){
                val = -min-maxOffset;
            }
            inner.css('marginTop', val);
        }
    });

    $('.error_container, .message_container').each(function(){
        animateMessage($(this))
    });

    $('.message_closer').on('click', function(){
        $(this).parent().animate({
            height:'0px',
        },150,function(){
            $(this).hide();
        });
    });
});

function animateMessage(messageObj){
    messageObj.show();
    messageObj.animate({
        padding: '5px',
        height: '16px',
    }, 300);
    setTimeout(function () {
        $('.autoClose').each(function () {
            messageObj.fadeOut(600);
        });
    }, 4000)
}

function displayNewMessages(messages){
    var container = $('#messages_container_container');
    container.html('')
    messages.forEach(function (item) {
        var messageObj = '<div class="message_container autoClose">' +
            '    <div class="message_content">'+item+'</div>' +
            '    <div class="message_closer">X</div> ' +
            '</div>'
        container.append(messageObj);
    });
    container.children('.message_container').each(function(){
        animateMessage($(this));
    });
}
function displayNewErrors(errors){
    var container = $('#messages_container_container');
    container.html('')
    if (errors.length > 5){
        var messageObj = '<div class="error_container autoClose">' +
        '<div class="message_content">' +
        'Too many error messages! click ' +
        '<a onclick="displayCenterPopup(\'multipleErrorsPopup\')"' +
        'style="text-decoration: underline; color:red; cursor:pointer">' +
        'here</a> to view them all</div>' +
        '<div class="message_closer">X</div></div>' +
        '<div class="popup" id="multipleErrorsPopup">' +
        '<div id="title">Multiple errors!</div>' +
        '<div id="help">Several errors have occured while proceeding your request.</div>' +
        '<div id="content">';
        errors.forEach(function (error) {
            messageObj += '<div class="popup_error_container" style="display:block;">' +
                '<div class="message_content">' + error + '</div></div>';
        });
        messageObj += '</div></div>'
        container.append(messageObj);
    }else{
        errors.forEach(function (item) {
            var messageObj = '<div class="error_container autoClose">' +
                '    <div class="message_content">' + item + '</div>' +
                '    <div class="message_closer">X</div> ' +
                '</div>'
            container.append(messageObj);
        });
    }
    container.children('.error_container').each(function () {
        animateMessage($(this));
    });
}

function setContentPaneWidth(overlaying){
    var side_menu = $("#side_menu");
    var cont = $('#content_container');
    
    side_menu.height($(window).height()-$("#head_banner").height());
    if (overlaying){
        side_menu.css("box-shadow", "0px 10px 10px 10px #CCC");
    } else {
        side_menu.css("box-shadow", "none");
    }
    
    if (side_menu.css('display') == 'none' || overlaying) {
        cont.width('100%');
        cont.css('margin-left', 'auto');
        cont.css('margin-right', 'auto');
    } else if (!overlaying){
        cont.width($(window).width()-side_menu.width()-30);
        cont.css('margin-left', side_menu.width()+10);
        cont.css('margin-right', '0px');
    }
}

function hide_menu(){
    var menu = $("#side_menu");
    if (menu.attr('state') == '1'){
        menu.hide();
        menu.attr('state', '0');
        menu.unbind("clickoutside");
        $('.left_menu_item:not(#analysis_box)').unbind('click');
        $('.sub_left_menu_item').unbind('click');
    } else{
        menu.attr('state', '1');
    }
}

function log(str){console.log(str);}

function toggleLoginMenu(){
    var login = $('#login_section');
    if (login[0] == undefined){
        login = $('#logout_section');
    }
    console.log(login[0])
    if (login.css('right') < '0'){
        login.animate({right:10},300);
        login.bind("clickoutside", function(){toggleLoginMenu();});
    } else {
        if (login.attr('state') == '1'){
            login.animate({right:-320},300);
            login.attr('state', '0');
            login.unbind("clickoutside");
        } else {
            login.attr('state', '1');
        }
    }
}

var lastPopupId = null;
function closeCenterPopup(){
    var outterPopup = $('#centerPopupOutter');
    var innerPopup = $('#centerPopupInner');
    if(outterPopup.css('display')=='block'){
        innerPopup.css('overflow', 'hidden')
        .animate({
            height: 0,
        }, 150, function () {
            innerPopup.removeAttr('style');
            outterPopup.removeAttr('style');
            outterPopup.hide();
            innerPopup.unbind('clickoutside');
        });
    }
}

function displayCenterPopup(containerId, afterFunction){
    var container = $('#' + containerId);
    var innerPopup = $('#centerPopupInner');
    if (containerId != lastPopupId) {
        //log('new popup')
        lastPopupId = containerId;
        $('#centerPopupTitle').html(container.children('#title').html());
        $('#centerPopupHelpText').html(container.children('#help').html());
        //log(container.children('#content').html())
        $('#centerPopupContent').html(container.children('#content').html());
    }
    var scriptTag = container.children('#functions');
    eval(scriptTag.text())
    var innerHeight = innerPopup.actual('height');
    innerPopup.css({
        overflow: 'hidden',
        height: 0,
    });
    $('#centerPopupOutter').show();
    innerPopup.animate({
        height: innerHeight,
    }, 150, function () {
        innerPopup.removeAttr('style');
        innerPopup.bind('clickoutside', function(event){
            if(event.target.id == 'centerPopupOutter'||
                event.target.id == 'centerPopupOutterTD'){
                closeCenterPopup();
            }
        });
        if(afterFunction != null){
            afterFunction();
        }
    })
}

function getPopupContainer(){
    return $('#centerPopupOutter table tr td #centerPopupInner #centerPopupContent');
}


//######################################################################################################
/*
 * jQuery outside events - v1.1 - 3/16/2010
 * http://benalman.com/projects/jquery-outside-events-plugin/
 * 
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function($,c,b){$.map("click dblclick mousemove mousedown mouseup mouseover mouseout change select submit keydown keypress keyup".split(" "),function(d){a(d)});a("focusin","focus"+b);a("focusout","blur"+b);$.addOutsideEvent=a;function a(g,e){e=e||g+b;var d=$(),h=g+"."+e+"-special-event";$.event.special[e]={setup:function(){d=d.add(this);if(d.length===1){$(c).bind(h,f)}},teardown:function(){d=d.not(this);if(d.length===0){$(c).unbind(h)}},add:function(i){var j=i.handler;i.handler=function(l,k){l.target=k;j.apply(this,arguments)}}};function f(i){$(d).each(function(){var j=$(this);if(this!==i.target&&!j.has(i.target).length){j.triggerHandler(e,[i.target])}})}}})(jQuery,document,"outside");
//######################################################################################################

// WHEEL EVENT CONTROLLER
(function (window, document) {
    var prefix = "", _addEventListener, support;
    if (window.addEventListener) {
        _addEventListener = "addEventListener";
    }
    else {
        _addEventListener = "attachEvent";
        prefix = "on";
    }
    support = "onwheel" in document.createElement("div") ? "wheel" : document.onmousewheel !== undefined ? "mousewheel" :
        "DOMMouseScroll";
    window.addWheelListener = function (elem, callback, useCapture) {
        _addWheelListener(elem, support, callback, useCapture);
        if (support == "DOMMouseScroll") {
            _addWheelListener(elem, "MozMousePixelScroll", callback, useCapture);
        }
    };
    function _addWheelListener(elem, eventName, callback, useCapture) {
        elem[_addEventListener]
        (prefix + eventName, support == "wheel" ? callback : function (originalEvent) {
            !originalEvent && ( originalEvent = window.event );
            var event = {
                originalEvent: originalEvent,
                target: originalEvent.target || originalEvent.srcElement,
                type: "wheel",
                deltaMode: originalEvent.type == "MozMousePixelScroll" ? 0 : 1,
                deltaX: 0,
                deltaZ: 0,
                preventDefault: function () {
                    originalEvent.preventDefault ? originalEvent.preventDefault() : originalEvent.returnValue = false;
                }
            };
            if (support == "mousewheel") {
                event.deltaY = -1 / 40 * originalEvent.wheelDelta;
                originalEvent.wheelDeltaX && ( event.deltaX = -1 / 40 * originalEvent.wheelDeltaX );
            } else {
                event.deltaY = originalEvent.detail;
            }
            return callback(event);
        }, useCapture || false);
    }
})
(window, document);






































































