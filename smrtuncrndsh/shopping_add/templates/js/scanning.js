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

        var date = $("#receipt-form-date");
        console.debug(Date.parse(date.val()));
        console.debug($("input[name=receipt-form-dates]:checked").length);
        if (!$("input[name=receipt-form-dates]:checked").length && !$("#receipt-form-date").val()) {
            event.preventDefault();
            makeFlashMessage('info', "Date missing! Please select a date for the receipt from the options or enter one manually.", "show-pdf-flashes");
        }
        if ($("input[name=receipt-form-dates]:checked").length && $("#receipt-form-date").val()) {
            event.preventDefault();
            makeFlashMessage('info', "Duplicate dates! Please either select a date for the receipt from the options or enter one manually.", "show-pdf-flashes");
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
