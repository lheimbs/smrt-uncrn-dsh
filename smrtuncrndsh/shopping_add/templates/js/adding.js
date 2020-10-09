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

    function load_items_list() {
        return $("#items").flexdatalist({
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
    }
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

    // when search for a shop returns nothing, the new shops category field will appear
    $('#shop-name.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
        if (!items.length) {
            $('#btn-add-shopping-category').removeClass("is-hidden").addClass("is-visible");
        }
        else {
            $('#btn-add-shopping-category').removeClass("is-visible").addClass("is-hidden");
        }
    });

    $('#shop-name.flexdatalist').on('select:flexdatalist', function(event, selected, options) {
        $('#btn-add-shopping-category').removeClass("is-visible").addClass("is-hidden");
        $('#shop-category').removeClass("is-visible").addClass("is-hidden");
    });

    // show shop category input and make it flexbox
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
    $('#items.flexdatalist').on('after:flexdatalist.search', function(event, keyword, data, items) {
        if (!items.length) {
            $('#new_items-_-name').val(keyword);
            $('#btn-add-new-item').removeClass("is-hidden").addClass("is-visible");
        }
        else {
            $('#btn-add-new-item').removeClass("is-visible").addClass("is-hidden");
        }
    });


    // get new item form from ajax
    $('a[rel="ajax:modal"]').click(function(event) {
        $.ajax({
            url: $(this).attr('href'),
            success: function(newHTML, textStatus, jqXHR) {
                $(newHTML).appendTo('body').modal();
                after_new_items_form_created();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Handle AJAX errors
            }
            // More AJAX customization goes here.
        });
      
        return false;
    });

    

    // dialog to add a new item
    function after_new_items_form_created() {
        $(document).on('submit', '#add-new-item-form', function(event) {
            event.preventDefault();

            console.log("submit ajax: "+JSON.stringify( $(this).serializeArray() ));
            $.ajax({
                url: "{{ url_for('shopping_add_bp.shopping_add_new_item') }}",
                type: "POST",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify( $(this).serializeArray() ),
                success: function(response) {
                    console.info("Success");
                    console.log(response);

                    const newLocal = $("#items").flexdatalist('value');
                    var current_selected = newLocal;
                    console.log("current_selected: "+JSON.stringify(current_selected));
                    current_selected.push(response.item);
                    console.log("new current selected: "+JSON.stringify(current_selected));

                    $("#items").flexdatalist('reset');
                    var items = load_items_list();
                    $("#items").flexdatalist('value', JSON.stringify(current_selected));

                    $.modal.close();
                },
                error: function(response, textStatus, errorThrown) {
                    console.error("Error");
                    console.log(response);
                    // if (response.status==0) {
                    //     alert('You are offline!!\n Please Check Your Network.');
                    // } else if(response.status==404) {
                    //     alert('Requested URL not found.');
                    // } else if(response.status==500) {
                    //     alert('Internel Server Error.');
                    // } else if(e=='parsererror') {
                    //     alert('Error.\nParsing JSON Request failed.');
                    // } else if(e=='timeout'){
                    //     alert('Request Time out.');
                    // } else {
                    //     alert('Unknow Error.\n'+response.responseText);
                    // }
                },
            });
        });

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
        $("#name").val($("#items-flexdatalist").val());
    }

    $(document).on('focus', 'input', function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top + 'px'
        }, 'fast');
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