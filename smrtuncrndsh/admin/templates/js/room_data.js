$(function() {
    var table = $("#room-data-table").DataTable( {
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
            $(".card-fill.pager").prepend('<a class="new material-icons" href="{#{ url_for("admin_bp.new_room_data") }#}">add_circle</a>')
        },
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "ajax": {
            url: "{{ url_for('admin_bp.query_room_data') }}",
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
                "data": "temperature",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' °C'),
            },
            {
                "data": "humidity",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' %'),
            },
            {
                "data": "pressure",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' hPa'),
            },
            {
                "data": "brightness",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' lx'),
            },
            {
                "data": "altitude",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' m'),
            },
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.edit_room_data', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.delete_room_data', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });
});