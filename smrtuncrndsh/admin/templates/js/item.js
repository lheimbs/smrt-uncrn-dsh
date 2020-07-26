$(function() {
    var table = $("#shopping-items-table").DataTable( {
        "initComplete": function () {
            // Apply the search
            this.api().columns().every( function () {
                var that = this;

                $( 'input', this.footer() ).on( 'keyup change clear', function () {
                    
                    if (this.type === "checkbox") {
                        var value = this.checked;
                    }
                    else {
                        var value = this.value;
                    }

                    if ( that.search() !== value ) {
                        that
                            .search( value )
                            .draw();
                    }
                } );
            } );
            $(".card-fill.pager").prepend('<a class="new material-icons" href="{{ url_for("admin_bp.new_shopping_item") }}">add_circle</a>')
        },
        // "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "stateSave":  true,
        // "stripeClasses": ['strip1', 'strip2'],
        "ajax": {
            url: "{{ url_for('admin_bp.query_shopping_items') }}",
            type: 'POST'
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "price"},
            {"data": "volume"},
            {"data": "price_per_volume"},
            {"data": "sale"},
            {"data": "note"},
            {"data": "category"},
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.edit_shopping_item', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.delete_shopping_item', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });
});