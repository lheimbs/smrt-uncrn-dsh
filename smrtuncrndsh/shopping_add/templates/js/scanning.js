$(function() {
    function load_items_fdl(element) {
        return $(element).flexdatalist({
            url: "{{ url_for('shopping_add_bp.query_items') }}",
            minLength: 0,
            // maxShownResults: 100,
            valueProperty: 'name',
            selectionRequired: false,
            visibleProperties: ["name", "price", "volume", "price_per_volume", "sale"],
            searchIn: 'name',
            searchContain: true,
            requestType: 'POST',
            requestContentType: 'json',
            cache: false,
        });
    }

    // handle submit of receipt scan
    $(document).on('submit', '#scan-pdf-form', function(event) {
        event.preventDefault();

        $.ajax({
            url: "{{ url_for('shopping_add_bp.scan_reciept') }}",
            type: "POST",
            data: new FormData( this ),
            processData: false,
            contentType: false,
            success: function(newHTML, textStatus, jqXHR) {
                console.log("RESPONSE:\n"+textStatus);
                $.modal.close();
                $(newHTML).appendTo('body').modal();

                // category flexdatalist
                var receipt_category = $("#receipt-form-category").flexdatalist({
                    url: "{{ url_for('shopping_add_bp.query_categories') }}",
                    minLength: 0,
                    // maxShownResults: 100,
                    valueProperty: 'name',
                    selectionRequired: false,
                    visibleProperties: "name",
                    searchIn: 'name',
                    searchContain: true,
                    requestType: 'POST',
                    requestContentType: 'json',
                    cache: false,
                });
                $("#add-pdf-form input[name^=receipt-form-shops-][name$=-category]").each(function( index ) {
                    $(this).flexdatalist({
                        url: "{{ url_for('shopping_add_bp.query_categories') }}",
                        minLength: 0,
                        // maxShownResults: 100,
                        valueProperty: 'name',
                        selectionRequired: false,
                        visibleProperties: "name",
                        searchIn: 'name',
                        searchContain: true,
                        requestType: 'POST',
                        requestContentType: 'json',
                        cache: false,
                    });
                });
                $("#add-pdf-form input[name^=receipt-form-shops-][name$=-shop]").each(function( index ) {
                    $(this).flexdatalist({
                        url: "{{ url_for('shopping_add_bp.query_shops') }}",
                        minLength: 0,
                        // maxShownResults: 100,
                        valueProperty: 'name',
                        selectionRequired: false,
                        visibleProperties: "name",
                        searchIn: 'name',
                        searchContain: true,
                        requestType: 'POST',
                        requestContentType: 'json',
                        cache: false,
                    });
                });
                $("#add-pdf-form input[name^=receipt-form-items-][name$=-item]").each(function( index ) {
                    var prev_value = $(this).val();
                    // console.log(prev_value);
                    var items = load_items_fdl($(this));
                    // items.flexdatalist(prev_value, prev_value);
                    // items.flexdatalist('value', prev_value);
                    $('#'+this.id+'-flexdatalist').val(prev_value);
                });
            },
            error: function(response, textStatus, errorThrown) {
                $.modal.close();
                handleAjaxError(response, textStatus, errorThrown);
            },
            complete: function(jqXHR, textStatus) {

            }
        });
    });

    $(document).on('submit', '#add-pdf-form', function(event) {
        var price = $("#receipt-form-price");
        if (
            (!$("input[name=receipt-form-sums]:checked").length && !$.isNumeric(price.val())) ||
            ($("input[name=receipt-form-sums]:checked").length && $.isNumeric(price.val()))) {
            event.preventDefault();
            makeFlashMessage('info', "Please either select a price for the receipt from the options or enter one manually.", "show-pdf-flashes");
        }
        else {
            if (!$.isNumeric(price.val())) {
                price.attr('value', 0);
            }
        }

        if ($('input[name^=receipt-form-shops-][name$=-shop]').length > 1) {
            event.preventDefault();
            makeFlashMessage('info', "Too many shop options. Please remove all other shops so that only one remains.", "show-pdf-flashes");
        }
    });

    $(document).on('click', '#show-pdf-shops-table .btn-remove-pdf', function(event) {
        if ($('#show-pdf-shops-table >tbody:last >tr').length > 1) {
            this.closest("tr").remove();
        }
    });
    $(document).on('click', '#show-pdf-items-table .btn-remove-pdf', function(event) {
        if ($('#show-pdf-items-table >tbody:last >tr').length > 1) {
            this.closest("tr").remove();
        }
    });
    $(document).on('click', '#show-pdf-items-table .btn-add-pdf-item', function(event) {
        var $last = $(this).closest('tbody').find('tr').last().prev();
        var num = parseInt($last.find("input:first").prop('id').match(/\d+/g), 10) +1;
        var $klon = $last.clone();
        $klon.find('.items-item input:nth-child(2)').remove();
        $klon.find('[id]').each(function () {
            this.id = this.id.replace(/\d+/, num);
        });
        $klon.find('[name]').each(function () {
            this.name = this.name.replace(/\d+/, num);
        });
        $klon.insertAfter($last);
        load_items_fdl($(this).closest('tbody').find('tr').last().prev().find("input[name^=receipt-form-items-][name$=-item]"));
    });

    $(".clear-pdf-form").on("click", function() {
        $('#pdf-form-reciept').val('');
        $('#pdf-form-category').val('');
    });

    $(".clear-receipt-form").on("click", function() {
        // TODO
    });
});


// Remove a modal's html after closing
$(document).on($.modal.AFTER_CLOSE, function(event, modal) {
    modal.elm[0].remove();
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
    console.debug("RESPONSE: ", response, "STATUS: ", textStatus, "ERROR: ", errorThrown);
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