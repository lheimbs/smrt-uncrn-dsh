$(function() {
    var table = $("#shopping-categories-table").DataTable( {
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
            $(".card-fill.pager").prepend('<a class="new material-icons" href="{{ url_for("admin_bp.new_shopping_category") }}">add_circle</a>')
        },
        "serverSide": true,
        "autoWidth": false,
        "ajax": {
            url: "{{ url_for('admin_bp.query_shopping_categories') }}",
            type: 'POST'
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.edit_shopping_category', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.delete_shopping_category', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });
});