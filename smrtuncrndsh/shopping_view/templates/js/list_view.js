$(function() {
    // $.fn.dataTable.ext.errMode = 'throw';
    
    $('input[name="daterange"]').daterangepicker({
        opens: 'center',
        drops: 'auto',
        autoApply: true,
        showWeekNumbers: false,
        linkedCalendars: false,
    });

    var min_price = getMinPrice();
    var max_price = getMaxPrice();

    var table = $("#shopping-view-list-table").DataTable( {
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "ajax": {
            url: "{{ url_for('shopping_view_bp.query_shopping_list') }}",
            type: 'POST',
            error: handleAjaxError,
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {
                "data": "date",
                "render": $.fn.dataTable.render.text(),
                "data-title": "Date",
            },
            {
                "data": "price",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' €'),
            },
            {
                "data": "shop",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "category",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "items[</br>]"
            },
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('shopping_view_bp.edit_shopping_list', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons edit-user-list' id='"+oData.id+"' rel='ajax:modal'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('shopping_view_bp.delete_shopping_list', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });

    register_search(table);

    if (parseInt($('#edit-instead-of-view').text(), 10) > -1) {
        {% set url = url_for('shopping_view_bp.edit_shopping_list', id='0') %}
        $.ajax({
            url: '{{ url }}' + parseInt($('#edit-instead-of-view').text(), 10),
            type: "GET",
            data: '',
            success: function(newHTML, textStatus, jqXHR) {
                console.log("RESPONSE:\n"+textStatus);
                $.modal.close();
                $(newHTML).appendTo('body').modal();
                $(".multi-items-amount").each(function() {
                    var val=$( this ).attr("value");
                    var amount=$( this ).text();
                    console.log("Add id '"+val+"' "+amount+"x to options");
                    for (var i = 1; i < amount; i++) { 
                        $("#items_obj option[value='"+val+"']").first().clone().appendTo("#items_obj");
                    }
                });
                $(".select-items-multi-chosen").chosen();
            }
        });
    }
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
