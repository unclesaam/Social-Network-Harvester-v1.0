/**
 * Created by Sam on 12/02/2016.
 */


$('document').ready(function(){

    $('#save_button').click(function(){
        $('#settings_form').submit();
    })

    $('input').each(function(){
        $(this).css('width', 120+this.value.length*9+'px');
    })


    $('.category_title, .tableOpenCloseIcon').click(function(){
        var content = $(this).parent().next(".category_content");
        content.slideToggle(300);
        togglePlusMinusSign($(this).parent().children(".tableOpenCloseIcon"));
    })

})


function togglePlusMinusSign(sign) {
    var src = sign.children('img').attr('src')
    if (sign.attr('type') == 'plus') {
        src = src.replace(/\/[^\/]+\.png/, '/minus_icon_128.png')
        sign.attr('type', 'minus');
    } else if (sign.attr('type') == 'minus') {
        src = src.replace(/\/[^\/]+\.png/, '/plus_icon_128.png')
        sign.attr('type', 'plus');
    }
    sign.children('img').attr('src', src)
}