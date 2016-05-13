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


    $('.category_opener').click(function(){
        var content = $(this).parent().next(".category_content");
        content.slideToggle(300);
    })

})