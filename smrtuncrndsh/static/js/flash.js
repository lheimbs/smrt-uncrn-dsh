
function makeFlashMessage(type, message, flashclass = "flashes") {
    new_message = $("<div>").addClass("flash message "+type)
        .append($("<span>").text(message))
        .append($("<i>").addClass("close-flash material-icons").text("close"));

    $(new_message).appendTo("."+flashclass);

    $('main').animate({ scrollTop: (0) }, 'fast');
}

function makeAddItemFlashMessage(type, message) {
    new_message = $("<div>").addClass("flash message "+type)
        .append($("<span>").text(message))
        .append($("<i>").addClass("close-flash material-icons").text("close"));

    $(new_message).appendTo(".add-new-item-errors");
}

$(document).on("click", "i.close-flash", function() {
    $(this).parent().remove();
});
