$(document).ready(function(){
    
    $(document).resize(function(){
        resizeParentFrame();
    });
    $(document).click(function(){
        parent.alertClick();
    })
    resizeParentFrame();
});









function resizeChildren(){
    //$(document).resize();
}







function resizeParentFrame(offset){
    //console.log('resizing requested')
    if (offset==undefined){offset=0;};
    //parent.alertsize(document.documentElement.offsetHeight+offset);
    /*parent.alertsize(Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight ));*/

}































