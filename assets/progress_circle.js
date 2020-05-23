window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_2: {
        make_radial_indicator: function(bar_div_id, temperature) {
            var el = document.getElementById(bar_div_id);

            var options = {
                color: el.getAttribute('data-color') || '#555555',
                bg_color: el.getAttribute('data-bgcolor') || '#123456',
                bar_width: el.getAttribute('data-width') || 10,
                radius: el.getAttribute('data-radius') || 50,
                unit: el.getAttribute('data-unit') || '%',
            }
            console.log(temperature);

            if (el.childElementCount > 0) {
                el.innerHTML = "";
            }

            var radialObj = radialIndicator('#'+bar_div_id, {
                radius: options.radius,
                barColor : options.color,
                barBgColor: options.bg_color,
                barWidth : options.bar_width,
                minValue: temperature.min,
                maxValue: temperature.max,
                initValue : temperature.old,
                roundCorner : true,
                displayNumber: ((temperature.display) ? true : false),
                format: '#### ' + options.unit
            }); 

            //Using Instance
            radialObj.animate(temperature.new);
        }
    }
});