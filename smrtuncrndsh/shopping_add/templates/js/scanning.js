$(function() {
    // 
    // REWE EBON ADDING
    // 

    // get form from ajax
    $('a#btn-scan-pdf[rel="ajax:modal"]').click(function(event) {
        $.ajax({
            url: $(this).attr('href'),
            success: function(newHTML, textStatus, jqXHR) {
                $(newHTML).appendTo('body').modal();

            },
            error: function(response, textStatus, errorThrown) {
                $.modal.close();
                handleAjaxError(response, textStatus, errorThrown);
            }
        });
        return false;
    });

    // handle submit of receipt scan
    $(document).on('submit', '#scan-pdf-form', function(event) {
        event.preventDefault();

        $.ajax({
            url: "{{ url_for('shopping_add_bp.scan_reciept') }}",
            type: "POST",
            // dataType: 'json',
            // contentType: 'application/json',
            // data: JSON.stringify( $(this).serializeArray() ),
            data: new FormData( this ),
            processData: false,
            contentType: false,
            success: function(response) {
                console.log("RESPONSE:\n"+response);
                if (response.status=="success") {
                    // const newLocal = $("#items").flexdatalist('value');
                    // var current_selected = newLocal;
                    // current_selected.push(response.item);

                    // var items = load_items_list();
                    // $("#items").flexdatalist('value', JSON.stringify(current_selected));

                    $.modal.close();

                    makeFlashMessage("success", response.text);
                    // $("#items-flexdatalist").focus();
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
});