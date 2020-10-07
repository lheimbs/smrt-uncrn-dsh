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

    var new_items_category = $("#new_items-_-category").flexdatalist({
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
    })

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

    $(document).on('click', '#add-form button[type=submit]', function(e) {
        e.preventDefault(); //prevent the default action
        var isValid = $(e.target).parents('#add-form').isValid();
        if(isValid) {
            this.submit(); // use the native submit method of the form element

            setTimeout(clear_form(), 100);
        }
    });

    // $("#add-new-shopping-item").click(function() {
    //     var $ul = $("ul[id='new_items']");
    //     if ($ul.find("input:last").length <= 0 ) {
    //         var num = 0;
    //     }
    //     else {
    //         var num = parseInt($ul.find("input:last").prop("id").match(/\d+/g), 10) + 1;
    //     }

    //     var $new_li = make_new_item_form().replaceAll("new_items-_", "new_items-"+num).replace('#_', '#'+(num+1));
    //     $ul.append($new_li);

    //     $ul.find("input[id='new_items-"+num+"-category']").flexdatalist({
    //         url: "{{ url_for('shopping_add_bp.query_categories') }}",
    //         minLength: 0,
    //         // maxShownResults: 100,
    //         valueProperty: 'id',
    //         selectionRequired: false,
    //         visibleProperties: ["name"],
    //         searchIn: 'name',
    //         searchContain: true,
    //         requestType: 'POST',
    //         requestContentType: 'json',
    //         cache: false,
    //     });

    // });
    // $("#remove-new-shopping-item").click(function() {
    //     $("ul[id='new_items']").find("li:last").remove();
    // });

    // when search for a shop returns nothing, the new shops category field will appear
    $('#shop-name.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
        if (!items.length) {
            // console.log("no results");
            $('#shop-category').removeClass("is-hidden").addClass("is-visible");
        }
        else {
            // console.log("results");
            $('#shop-category').removeClass("is-visible").addClass("is-hidden");
        }
    });

    // When search for items returns an empty list, add an 'add-new-items' button
    $('#items.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
        if (!items.length) {
            $('#new_items-_-name').val(keyword);
            $('#btn-add-new-item').removeClass("is-hidden").addClass("is-visible");
        }
        else {
            $('#btn-add-new-item').removeClass("is-visible").addClass("is-hidden");
        }
    });


    // dialog to add a new item
    $('#add-new-item-form').submit(function(event) {
        event.preventDefault(); //prevent the default action
        $.ajax({
            url: "{{ url_for('shopping_add_bp.shopping_add_new_item') }}",
            type: "POST",
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify( $(this).serializeArray() ),
            success: function(response) {
                console.info(response);
                $.modal.close();
            },
            error: function(xhr) {
                console.error(xhr)
            },
        });
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