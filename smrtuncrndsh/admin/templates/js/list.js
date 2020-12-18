$(function() {
    $('input[name="daterange"]').daterangepicker({
        opens: 'center',
        drops: 'auto',
        autoApply: true,
        showWeekNumbers: false,
        linkedCalendars: false,
    });

    // TODO: bar does not resize properly
    var min_price = getMinPrice();
    var max_price = getMaxPrice();
    $('.price-slider').jRange({
        from: min_price,
        to: max_price,
        step: 1,
        scale: [Math.floor(min_price), Math.round(max_price/4), Math.round(max_price/2), Math.round((max_price/4)*3), Math.ceil(max_price)],
        format: '%s €',
        width: 150,
        showLabels: true,
        isRange : true,
        setValue: Math.floor(min_price)+','+Math.ceil(max_price),
        theme: 'theme-blue',
    });

    $('.price-slider').jRange({
        setValue: Math.floor(min_price)+','+Math.ceil(max_price),
    });

    var table = $("#shopping-list-table").DataTable( {
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "stateSave":  true,
        "ajax": {
            url: "{{ url_for('admin_bp.query_shopping_list') }}",
            type: 'POST'
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {
                "data": "id",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "date",
                "render": $.fn.dataTable.render.text(),
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
                "data": "user",
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
                    {% set url = url_for('admin_bp.edit_shopping_list', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.delete_shopping_list', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });

    register_search(table);
});


var csrf_token = "{{ csrf_token() }}";

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});