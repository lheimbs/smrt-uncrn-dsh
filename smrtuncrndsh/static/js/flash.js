
function makeFlashMessage(type, message) {
    new_message = $("<div>").addClass("flash message "+type)
        .append($("<span>").text(message))
        .append($("<i>").addClass("close-flash material-icons").text("close"));

    $(new_message).appendTo(".flashes");
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
