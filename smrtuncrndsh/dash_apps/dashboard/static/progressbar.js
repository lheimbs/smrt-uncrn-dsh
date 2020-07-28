// plugin-source: https://github.com/tigrr/circle-progress

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_2: {
        make_radial_indicator: function(bar_div_id, temperature) {
            
            var unit = document.getElementById(bar_div_id).getAttribute('data-unit') || '%';

            $("#"+bar_div_id).circleProgress({
                max: temperature.max,
                min: temperature.min,
                value: temperature.new,
                animation: 'easeInOutCirc',
                animationDuration: 2000,
                textFormat: function(value, max) {
                    return ''+value.toFixed(2) + unit;
                },
            });
        }
    }
});