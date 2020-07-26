$(function() {
    var table = $("#probe-request-table").DataTable( {
        "initComplete": function () {
            // Apply the search
            this.api().columns().every( function () {
                var that = this;

                $( 'input', this.footer() ).on( 'focusout clear', function () {
                    
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
                } );
            } );
            //$(".card-fill.pager").prepend('<a class="new material-icons" href="{#{ url_for("admin_bp.new_probe_request") }#}">add_circle</a>')
        },
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "ajax": {
            url: "{{ url_for('admin_bp.query_probe_request') }}",
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
                "data": "macaddress",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "make",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "ssid",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "rssi",
                "render": $.fn.dataTable.render.number(),
            },
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.edit_probe_request', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.delete_probe_request', id='0') %}
                    $(nTd).html("<a href='{{ url }}"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });
});