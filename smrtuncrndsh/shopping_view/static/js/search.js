function register_search(table) {
    function search_table() {
        // Apply the search
        table.columns().every( function () {
            var that = this;
            $( 'input', this.footer() ).each(function () {
                if (this.type === "checkbox") {
                    var value = this.checked;
                }
                else if (this.type === "date") {
                    if (this.valueAsDate != null) {
                        var value = this.valueAsDate.toUTCString();
                    }
                    else {
                        var value = '';
                    }
                }
                else {
                    var value = this.value;
                }
    
                if ( that.search() !== value ) {
                    that.search( value ).draw();
                }
            });
        });
    }

    $('#search-cancel').click(function() {
        // Clear the search
        table.columns().every( function () {
            input = $( 'input', this.footer() );
            if (input.length != 0 && input[0].type == "checkbox") {
                input[0].checked = false;
            }
            else {
                input.val('');
            }
        } );
        search_table();
    });

    $('#search-go').click(search_table);
}

$.fn.dataTable.ext.errMode = 'throw';