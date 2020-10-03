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

    var items = $("#items").flexdatalist({
        url: "{{ url_for('shopping_add_bp.query_items') }}",
        minLength: 0,
        multiple: true,
        maxShownResults: 100,
        valueProperty: ['id', 'name'],
        selectionRequired: true,
        visibleProperties: ["name", "price", "volume", "price_per_volume", "sale"],//
        searchIn: 'name',
        searchContain: true,
        requestType: 'POST',
        requestContentType: 'json',
        cache: false,
        allowDuplicateValues: true,
    });
    // items.flexdatalist('add', )


    function clear_form() {
        console.log("Cear form");
        $("#add-form")[0].reset();
        $("ul[id='new_items']").empty();
        $("#date").val("");
        $("#price").val("");
        $("#shop-category").val("");
        shop.val("");
        category.val("");
        items.val("");
    }

    $(".clear-form").click(clear_form);

    $(document).on('click', 'form button[type=submit]', function(e) {
        e.preventDefault(); //prevent the default action
        var isValid = $(e.target).parents('form').isValid();
        if(isValid) {
            this.submit(); // use the native submit method of the form element

            setTimeout(clear_form(), 100);
        }
    });

    $("#add-new-shopping-item").click(function() {
        var $ul = $("ul[id='new_items']");
        if ($ul.find("input:last").length <= 0 ) {
            var num = 0;
        }
        else {
            var num = parseInt($ul.find("input:last").prop("id").match(/\d+/g), 10) + 1;
        }

        var $new_li = make_new_item_form().replaceAll("new_items-_", "new_items-"+num).replace('#_', '#'+(num+1));
        $ul.append($new_li);

        $ul.find("input[id='new_items-"+num+"-category']").flexdatalist({
            url: "{{ url_for('shopping_add_bp.query_categories') }}",
            minLength: 0,
            // maxShownResults: 100,
            valueProperty: 'id',
            selectionRequired: false,
            visibleProperties: ["name"],
            searchIn: 'name',
            searchContain: true,
            requestType: 'POST',
            requestContentType: 'json',
            cache: false,
        });

    });
    $("#remove-new-shopping-item").click(function() {
        $("ul[id='new_items']").find("li:last").remove();
    });

    $("#shop-name-flexdatalist").focusout(function() {
        console.log("focus lost");
        var $shop_cat = $("#shop-category");
        if (shop.val().startsWith('{') && shop.val().endsWith('}')) {
            // value is numeric, so an entry was chosen from datalist -> hide new category
            if (!$shop_cat.hasClass("is-hidden")) {
                $shop_cat.addClass(['is-hidden']);
            }
        }
        else {
            if ($shop_cat.hasClass("is-hidden")) {
                $shop_cat.removeClass(['is-hidden']);
            }
        }
    });
    shop.on('select:flexdatalist', function(event, set, options) {
        var $shop_cat = $("#shop-category");
        if (!$shop_cat.hasClass("is-hidden")) {
            $shop_cat.addClass(['is-hidden']);
        }
    });


    $('#items.flexdatalist').on('shown:flexdatalist.results', function(event, results) {
        console.log("show results")
        console.log(results);

        if (!results.length) {
            console.log("No items found");
            $('ul#items-flexdatalist-results').append(
                $('<li>').append(
                    '<button>Add new Item</button>'
                )
            );
        }
    });
});

var csrf_token = "{{ csrf_token() }}";
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});