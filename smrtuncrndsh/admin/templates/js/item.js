$(function() {
    var table = $("#shopping-items-table").DataTable( {
        "initComplete": function () {
            $(".card-fill.pager").prepend('<a class="new material-icons" href="{{ url_for("admin_bp.new_shopping_item") }}">add_circle</a>')
        },
        "processing": true,
        "serverSide": true,
        "autoWidth": false,
        "stateSave":  true,
        "ajax": {
            url: "{{ url_for('admin_bp.query_shopping_items') }}",
            type: 'POST'
        },
        'select': {
            'style':    'os',
            'selector': 'td:first-child',
            // 'blurable': true,
            'className': 'row-selected'
        },
        "dom": '<"card mb-5"<"data-table top"li>rt><"card-fill pager"p>',
        "columns": [
            {
                "data": "id",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "name",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "price",
                "render": $.fn.dataTable.render.number(' ', ',', 2, '', ' €'),
            },
            {
                "data": "volume",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "price_per_volume",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "sale",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "note",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "lists",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    {% set url = url_for('admin_bp.edit_shopping_list', id='0') %}
                    var list_links = oData.lists.map(function(list_id, index) {
                        return '<a href="{{ url }}'+list_id+'">List '+(index+1)+'</a>';
                    });
                    $(nTd).html(list_links.join(", "));
                },
            },
            {
                "data": "category",
                "render": $.fn.dataTable.render.text(),
            },
            {
                "data": "edit",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html("<a href='#' id='edit-item-link-"+oData.id+"' rel='ajax:modal' class='material-icons edit-item-link'>edit</a>");
                },
            },
            {
                "data": "delete",
                "searchable": false,
                "orderable": false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html("<a href='#' id='delete-item-link-"+oData.id+"' class='material-icons'>delete_forever</a>");
                },
            },
        ]
    });

    register_search(table);
});

$(document).on('click', 'a[id^="edit-item-link-"][rel="ajax:modal"]', function() {
    {% set url_id = url_for('admin_bp.edit_shopping_item', id='0') %}
    {% set url_ids = url_for('admin_bp.edit_shopping_item', ids='0') %}

    var this_id = parseInt(this.id.replace('edit-item-link-', ''));
    var ids = get_selection_ids();
    if (ids.length > 0) {
        if (!ids.includes(this_id)) {
            ids.push(this_id);
        }
        var url = '{{ url_ids }}'+ids.join(',');
    }
    else {
        var url = '{{ url_id }}'+this_id;
    }
    $.ajax({
        url: url,
        success: function(newHTML, textStatus, jqXHR) {
            $(newHTML).appendTo('body').modal();

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
            $("#add-new-item-form #name").val($("#items-flexdatalist").val());
            if ($("#add-new-item-form #name").val()) {
                // focus price if the items name is already set
                $("#add-new-item-form #price").focus();
            }
            else {
                // otherwise focus the name input
                $("#add-new-item-form #name").focus();
            }
        },
        error: function(response, textStatus, errorThrown) {
            $.modal.close();
            handleAjaxError(response, textStatus, errorThrown);
        }
    });
    return false;
});

$(document).on('click', 'a[id^="delete-item-link-"]', function() {
    {% set del_url_id = url_for('admin_bp.delete_shopping_item', id='0') %}
    {% set del_url_ids = url_for('admin_bp.delete_shopping_item', ids='0') %}

    var this_id = parseInt(this.id.replace('delete-item-link-', ''));
    var ids = get_selection_ids();
    if (ids.length > 0) {
        if (!ids.includes(this_id)) {
            ids.push(this_id);
        }
        var url = '{{ del_url_ids }}'+ids.join(',');
    }
    else {
        var url = '{{ del_url_id }}'+this_id;
    }
    $(this).attr('href', url);
    console.log(this.href);
    $(this).click();
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
    }
});