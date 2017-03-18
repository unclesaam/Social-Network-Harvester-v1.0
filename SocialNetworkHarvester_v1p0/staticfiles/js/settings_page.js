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
    var img = sign.children().children('img')
    if (sign.attr('type') == 'plus') {
        img.css("margin-left","-200%");
        sign.attr('type', 'minus');
    } else if (sign.attr('type') == 'minus') {
        img.css("margin-left", "-300%");
        sign.attr('type', 'plus');
    }
}