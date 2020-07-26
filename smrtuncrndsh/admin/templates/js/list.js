$(function() {
    $('input[name="daterange"]').daterangepicker({
        opens: 'center',
        drops: 'auto',
        // autoApply: true,
        showWeekNumbers: false,
        linkedCalendars: false,
    });

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
        ondragend: function() { table.columns(2).search($('.price-slider').val()).draw(); },
        theme: 'theme-blue',
    });

    $('.price-slider').jRange({
        setValue: Math.floor(min_price)+','+Math.ceil(max_price),
    });

    var table = $("#shopping-list-table").DataTable( {
        "initComplete": function () {
            // Apply the search
            this.api().columns().every( function () {
                var that = this;
                
                $( 'input', this.footer() ).on( 'focusout clear', function () {
                    if ( this.name === "daterange") {
                        console.log("no search on daterange");
                    }
                    else {
                        if (this.type === "checkbox") {
                            var value = this.checked;
                        }
                        else if (this.type === "date") {
                            var value = this.valueAsDate.toUTCString();
                        }
                        else {
                            var value = this.value;
                        }

                        if ( that.search() !== value ) {
                            that
                                .search( value )
                                .draw();
                        }
                    }
                    
                } );
            } );
            //$(".card-fill.pager").prepend('<a class="new material-icons" href="{#{ url_for("admin_bp.new_shopping_list") }#}">add_circle</a>')
        },
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "ajax": {
            url: "{{ url_for('admin_bp.query_shopping_list') }}",
            type: 'POST'
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {
                "data": "id",
                "render": $.fn.dataTable.render.number(),
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

    $('input[name="daterange"]').on('apply.daterangepicker', function(ev, picker) {
        var start = picker.startDate.format('YYYY-MM-DD');
        var end = picker.endDate.format('YYYY-MM-DD');
        console.log(start, end);
        table.columns(1).search(start+' - '+end).draw();
    });

    $('input[name="daterange"]').on('cancel.daterangepicker', function(ev, picker) {
        $('input[name="daterange"]').val('');
        table.columns(1).search('').draw();
    });
});