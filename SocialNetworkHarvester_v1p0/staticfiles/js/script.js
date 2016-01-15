$(document).ready(function() {
    var select = $("#menu_select");
    var menu = $("#side_menu");
    var OVERLAYING_TRESHOLD = 1200;
    
    if ($(window).width() <= OVERLAYING_TRESHOLD){
        menu.hide();
    }
    setContentPaneWidth();
    menu.height($( window ).height())
    
    select.click(function(){
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
        //$('#inner_container_frame')[0]
            //.contentWindow.resizeChildren($('#inner_container').css('width'));
    });
    
    $('#login_button').click(function(){
        toggleLoginMenu();
    });
    
    $('#analysis_box').click(function(){
        var toolMenu = $('#SubLeftMenu');
        toolMenu.slideToggle(300);
    });
    
    
    

    console.log('page loaded');
});

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








































































