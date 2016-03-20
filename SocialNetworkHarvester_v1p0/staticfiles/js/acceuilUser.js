$(document).ready(function(){
    resizeBoxes();
})

function resizeBoxes(old_width){
    var container_width = $('#inner_container').width();
    if(old_width != container_width){
        if(container_width == 1200){
            var boxWidth = container_width/4;
        }else if(900 < container_width){
            var boxWidth = container_width/3;
        }else if(600 < container_width){
            var boxWidth = container_width/2;
        }else{
            var boxWidth = container_width;
        }
        $('.section_box').each(function(){
            $(this).css('width', boxWidth-22+'px');
        })
    }
    setTimeout(function(){resizeBoxes(container_width)}, 0.1)
}







/*
Browser detection!
*/
var matched, browser;jQuery.uaMatch = function( ua ) {ua = ua.toLowerCase();var match = /(chrome)[ \/]([\w.]+)/.exec( ua ) ||/(webkit)[ \/]([\w.]+)/.exec( ua ) ||/(opera)(?:.*version|)[ \/]([\w.]+)/.exec( ua ) ||/(msie) ([\w.]+)/.exec( ua ) ||ua.indexOf("compatible") < 0 && /(mozilla)(?:.*? rv:([\w.]+)|)/.exec( ua ) ||[];return {browser: match[ 1 ] || "",version: match[ 2 ] || "0"};};matched = jQuery.uaMatch( navigator.userAgent );browser = {};if ( matched.browser ) {browser[ matched.browser ] = true;browser.version = matched.version;}if ( browser.chrome ) {browser.webkit = true;} else if ( browser.webkit ) {browser.safari = true;}jQuery.browser = browser;



















