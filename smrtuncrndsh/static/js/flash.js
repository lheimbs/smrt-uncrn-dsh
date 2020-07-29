$(function() {
    $("i.close-flash").each(function() {
        $( this ).on("click", function (){
            $( this ).parent().remove();
        });
    });
});