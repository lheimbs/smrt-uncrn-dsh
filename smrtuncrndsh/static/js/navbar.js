
$(function() {
    $('nav').find('a').each(function() {
        $(this).toggleClass('active', $(this).attr('href') == window.location.pathname);
    });

    // $('.dropdown-container div').hide();
    $('.dropdown-container div').not(function() {
        return $(this).children().is(function() {
            return $(this).hasClass('active');
        })
    }).hide();

    $(".dropdown-container a.dropdown-button").click(function () {
        $(this).parent(".dropdown-container").children("div").slideToggle("100");
        toggleExpandIcon($(this).find(".expand-icon"));
    });

    $(".dropdown-container").each(function() {
        if ($(this).children("div").is(":visible")) {
            $(this).find(".expand-icon").text("expand_less");
        }
        else {
            $(this).find(".expand-icon").text("expand_more")
        }
    });
});

function toggleExpandIcon(icon) {
    var text = icon.text();
    icon.text(
        text == "expand_more" ? "expand_less" : "expand_more"
    );
}