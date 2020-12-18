$(function() {
    // handle submit of receipt scan
    $(document).on('click', '.edit-user-list', function(event) {
        event.preventDefault();

        // var num = parseInt($(this).prop('id').match(/\d+/g), 10);
        $.ajax({
            url: $(this).attr("href"),
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
    });

    // $(document).on('submit', '#list-edit-form', function(event) {
    //     event.preventDefault();

    //     $.ajax({
    //         url: $(this).attr("action"),
    //         type: "GET",
    //         dataType: 'json',
    //         contentType: 'application/json',
    //         data: JSON.stringify( $(this).serializeArray() ),
    //         // data: new FormData( this ),
    //         success: function(newHTML, textStatus, jqXHR) {
    //             console.log("RESPONSE:\n"+textStatus);
    //         }
    //     });
    // });

    function reset_selected(e) {
        // remove result-selected class from all li under the dropdown
        $('.chosen-drop .chosen-results li').removeClass('result-selected');
        // add active-result class to all li which are missing the respective class
        $('.chosen-drop .chosen-results li').each(function() {
            if (!$(this).hasClass('active-result'))
            $(this).addClass('active-result');
        });
    }

    $(function() {
        $('.chosen-container-multi').on('mousemove keyup', reset_selected)
    });

    $(document).on('submit', '#list-edit-form', function() {
        //$(".select-items-multi-chosen").trigger("chosen:updated");
        ids = [];
        $(".choice-id").each(function(){
            if(($.trim($(this).text()).length>0)){
            ids.push($(this).text());
            }
        });
        $("#test").val(ids);
    });
});
