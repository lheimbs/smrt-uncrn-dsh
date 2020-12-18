$(function() {

    var shop = $("#shop-name").flexdatalist({
        url: "{{ url_for('shopping_add_bp.query_shops') }}",
        minLength: 0,
        // maxShownResults: 100,
        valueProperty: ['id', 'name'],
        selectionRequired: false,
        visibleProperties: ["name"],
        searchIn: 'name',
        searchContain: true,
        requestType: 'POST',
        requestContentType: 'json',
        cache: false,
    });
    $("#shop-name").attr("required", false);
    $("#shop-name-flexdatalist").attr("required", true);

    var category = $("#category").flexdatalist({
        url: "{{ url_for('shopping_add_bp.query_categories') }}",
        minLength: 0,
        // maxShownResults: 100,
        valueProperty: ['id', 'name'],
        selectionRequired: false,
        visibleProperties: ["name"],
        searchIn: 'name',
        searchContain: true,
        requestType: 'POST',
        requestContentType: 'json',
        cache: false,
    });

    function load_items_list() {
        return $("#items").flexdatalist({
            url: "{{ url_for('shopping_add_bp.query_items') }}",
            minLength: 0,
            multiple: true,
            maxShownResults: 100,
            valueProperty: ['id', 'name'],
            selectionRequired: true,
            visibleProperties: ["name", "price", "volume", "price_per_volume", "sale"],
            searchIn: 'name',
            searchContain: true,
            requestType: 'POST',
            requestContentType: 'json',
            cache: false,
            allowDuplicateValues: true,
        });
    }
    var items = $("#items").flexdatalist({
        url: "{{ url_for('shopping_add_bp.query_items') }}",
        minLength: 0,
        multiple: true,
        maxShownResults: 100,
        valueProperty: ['id', 'name'],
        selectionRequired: true,
        visibleProperties: ["name", "price", "volume", "price_per_volume", "sale"],
        searchIn: 'name',
        searchContain: true,
        requestType: 'POST',
        requestContentType: 'json',
        cache: false,
        allowDuplicateValues: true,
    });

    function clear_form() {
        $("#add-form")[0].reset();
        $("#date").val("");
        $("#price").val("");
        $("#shop-category").val("");
        shop.val("");
        category.val("");

        var items = load_items_list();
    }
    // custom form clearing on reset button press
    $(".clear-form").on("click", function() {
        clear_form();
    });

    // when search for a shop returns nothing, the new shops category field will appear
    $('#shop-name.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
        if (!items.length) {
            $('#btn-add-shopping-category').removeClass("is-hidden").addClass("is-visible");
        }
        else {
            $('#btn-add-shopping-category').removeClass("is-visible").addClass("is-hidden");
        }
    });

    // hide new category & add-category-btn when a shop from the datalist is selected
    $('#shop-name.flexdatalist').on('select:flexdatalist', function(event, selected, options) {
        $('#btn-add-shopping-category').removeClass("is-visible").addClass("is-hidden");
        $('#shop-category').removeClass("is-visible").addClass("is-hidden");
    });

    // show shop category input and make it flexdatalist
    $(document).on('click', '#btn-add-shopping-category', function() {
        $('#shop-category').toggleClass("is-visible is-hidden");
        var add_text = 'Add Category <span class="material-icons">add</span>';
        var remove_text = 'Remove Category <span class="material-icons">remove</span>';
        $(this).html($(this).html() == add_text ? remove_text : add_text);

        $("#shop-category").flexdatalist({
            url: "{{ url_for('shopping_add_bp.query_categories') }}",
            minLength: 0,
            // maxShownResults: 100,
            valueProperty: ['id', 'name'],
            selectionRequired: false,
            visibleProperties: ["name"],
            searchIn: 'name',
            searchContain: true,
            requestType: 'POST',
            requestContentType: 'json',
            cache: false,
        });
    });

    // When search for items returns an empty list, add an 'add-new-items' button
    // $('#items.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
    //     if (!items.length) {
    //         $('#add-new-item-form #name').val(keyword);
    //         $('#btn-add-new-item').removeClass("is-hidden").addClass("is-visible");
    //     }
    //     else {
    //         $('#btn-add-new-item').removeClass("is-visible").addClass("is-hidden");
    //     }
    // });


    // get new item form from ajax
    $('a#btn-add-new-item[rel="ajax:modal"]').click(function(event) {
        $.ajax({
            url: $(this).attr('href'),
            success: function(newHTML, textStatus, jqXHR) {
                $(newHTML).appendTo('body').modal();

                // make category field flexdatalist
                $("#new-item-category").flexdatalist({
                    url: "{{ url_for('shopping_add_bp.query_categories') }}",
                    minLength: 0,
                    // maxShownResults: 100,
                    valueProperty: ['id', 'name'],
                    selectionRequired: false,
                    visibleProperties: ["name"],
                    searchIn: 'name',
                    searchContain: true,
                    requestType: 'POST',
                    requestContentType: 'json',
                    cache: false,
                });

                // set search value as new items name
                $("#add-new-item-form #name").val($("#items-flexdatalist").val());
                if ($("#add-new-item-form #name").val()) {
                    // focus price if the items name is already set
                    $("#add-new-item-form #price").focus();
                }
                else {
                    // otherwise focus the name input
                    $("#add-new-item-form #name").focus();
                }
            },
            error: function(response, textStatus, errorThrown) {
                $.modal.close();
                handleAjaxError(response, textStatus, errorThrown);
            }
        });
        return false;
    });

    $(document).on('submit', '#add-new-item-form', function(event) {
        event.preventDefault();

        $.ajax({
            url: "{{ url_for('shopping_add_bp.shopping_add_new_item') }}",
            type: "POST",
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify( $(this).serializeArray() ),
            success: function(response) {
                if (response.status=="success") {
                    const newLocal = $("#items").flexdatalist('value');
                    var current_selected = newLocal;
                    current_selected.push(response.item);

                    var items = load_items_list();
                    $("#items").flexdatalist('value', JSON.stringify(current_selected));

                    $.modal.close();

                    makeFlashMessage("success", response.text);
                    $("#items-flexdatalist").focus();
                }
                else {
                    if ("fields" in response) {
                        response.fields.forEach(item => makeAddItemFlashMessage("warning", item+": "+response.fields[item]));
                    }
                    else {
                        makeFlashMessage("error", response.status+": "+response.text);
                        $.modal.close();
                    }
                }
                console.debug(JSON.stringify(response));
            },
            error: function(response, textStatus, errorThrown) {
                $.modal.close();
                handleAjaxError(response, textStatus, errorThrown);
            },
        });
    });

    // open pdf-scan document form modal
    $(document).on('click', '#btn-scan-pdf', function(event) {
        event.preventDefault();

        // var num = parseInt($(this).prop('id').match(/\d+/g), 10);
        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            success: function(newHTML, textStatus, jqXHR) {
                console.log("RESPONSE:\n"+textStatus);
                $.modal.close();
                $(newHTML).appendTo('body').modal();
            }
        });
    });
});

// Remove a modal's html after closing
$(document).on($.modal.AFTER_CLOSE, function(event, modal) {
    modal.elm[0].remove();
});

$(document).on('focus', 'input', function() {
    $('html, body').animate({
        scrollTop: $(this).offset().top + 'px'
    }, 'fast');
});

var csrf_token = "{{ csrf_token() }}";
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    },
    error: handleAjaxError,
});

function handleAjaxError(response, textStatus, errorThrown) {
    console.debug("ajax setup, error");
    console.debug(response, textStatus, errorThrown);
    // Handle AJAX errors
    if (response.status==0) {
        makeFlashMessage('error', 'You are offline! Please Check Your Network.');
    } else if(response.status==404) {
        makeFlashMessage('error', 'Requested URL not found.');
    } else if(response.status==500) {
        makeFlashMessage('error', 'Internal Server Error.');
    } else if(textStatus=='parsererror') {
        makeFlashMessage('error', 'Parsing JSON Request failed.');
    } else if(textStatus=='timeout'){
        makeFlashMessage('error', 'Request Time out.');
    } else if(response.responseJSON=="The CSRF token has expired."){
        makeFlashMessage('error', "The CSRF token has expired. Please refresh the page.");
    } else {
        makeFlashMessage('error', 'Unknow Error: '+errorThrown);
    }
}