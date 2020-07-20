// Create a new date from a string, return as a timestamp.
function timestamp(str) {
    return new Date(str).getTime();
}

$('#filter-form').submit(function(event) {
    event.preventDefault(); //this will prevent the default submit
    // $("#date_min").val(
    console.log($("#date_min")[0].value, $("#date_max")[0].value);
    console.log($("#price_min")[0].value, $("#price_max")[0].value);


    $(this).unbind('submit').submit(); // continue the submit unbind preventDefault
});


// Append a suffix to dates.
// Example: 23 => 23rd, 1 => 1st.
function nth(d) {
    if (d > 3 && d < 21) return 'th';
    switch (d % 10) {
        case 1:
            return "st";
        case 2:
            return "nd";
        case 3:
            return "rd";
        default:
            return "th";
    }
}
// Create a string representation of the date.
function formatDate(date) {
    return date.getDate() + "." +
        date.getMonth() + "." +
        date.getFullYear();
}
function formatDateISO(date) {
    return date.getFullYear() + '-' +
    ("0" + date.getMonth()).slice(-2) + '-' +
        ("0" + date.getDate()).slice(-2);
}

$( window ).on( "load", function() {
    $("#date_min").val(getCurrMinDate());
    $("#date_max").val(getCurrMaxDate());
    console.log($("#date_min")[0].value, $("#date_max")[0].value);

    $("#price_min").val(getCurrMinPrice());
    $("#price_max").val(getCurrMaxPrice());
    console.log($("#price_min")[0].value, $("#price_max")[0].value);
});

function cancelFilters() {
    $("#date_min").val(getMinDate());
    $("#date_max").val(getMaxDate());
    $("#price_min").val(getMinPrice());
    $("#price_max").val(getMaxPrice());
    $("#shop").val("");
    $("#shop").val("");
    $("#category").val("");
}

$(function() {
    var dateSlider = document.getElementById('date-min-max-slider');
    noUiSlider.create(dateSlider, {
        // Create two timestamps to define a range.
        range: {
            min: timestamp(getMinDate()),
            max: timestamp(getMaxDate()),
        },
        connect: true,
        tooltips: [true, true],
        // Steps of one week
        step: 7 * 24 * 60 * 60 * 1000,
        // Two more timestamps indicate the handle starting positions.
        start: [
            timestamp(getCurrMinDate()),
            timestamp(getCurrMaxDate())
        ],
        // No decimals
        format: wNumb({
            decimals: 0
        })
    });

    var dateValues = [
        $("#date-min-max-slider .noUi-handle-lower .noUi-tooltip")[0],
        $("#date-min-max-slider .noUi-handle-upper .noUi-tooltip")[0]
    ];

    dateSlider.noUiSlider.on('update', function (values, handle) {
        var date = formatDate(new Date(+values[handle]));
        var date_iso = formatDateISO(new Date(+values[handle]));

        // update tooltips
        dateValues[handle].innerHTML = date;
    });

    dateSlider.noUiSlider.on('set', function (values, handle) {
        var date_iso = formatDateISO(new Date(+values[handle]));
        // update dateinputs
        if (handle) {
            $("#date_max").val(date_iso);
        } else {
            console.log("date min", date_iso)
            $("#date_min").val(date_iso);
        }
    });
});

$(function() {
    var slider = document.getElementById('price-min-max-slider');
    noUiSlider.create(slider, {
        start: [
            parseFloat(getCurrMinPrice()),
            parseFloat(getCurrMaxPrice())
        ],
        connect: true,
        tooltips: [true, true],
        range: {
            'min': getMinPrice(),
            'max': getMaxPrice()
        }
    });
    slider.noUiSlider.on('set', function (values, handle) {
        var value = values[handle];
        console.log(handle, value);
        // update price inputs
        if (handle === 0) {
            // document.getElementById("price_max").value = value;
            $("#price_min").val(value);
            console.log($("#price_min")[0].value);
        } else {
            // document.getElementById("price_min").value = value;
            $("#price_max").val(value);
            console.log($("#price_max")[0].value);
        }
    });
});
