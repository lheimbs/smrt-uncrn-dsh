window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        make_circular_progressbar: function(progress_id) {
            var el = document.getElementById(progress_id); // get canvas

            var options = {
                percent:  el.getAttribute('data-percent') || 25,
                size: el.getAttribute('data-size') || 220,
                lineWidth: el.getAttribute('data-line') || 15,
                rotate: el.getAttribute('data-rotate') || 0,
                color: el.getAttribute('data-color') || '#555555',
                anim_time: el.getAttribute('data-animtime') || 2
            }
            console.log(options);

            var canvas = document.createElement('canvas');
            canvas.id = 'canvas-circular-progress';
            var span = document.createElement('span');
            span.id = 'span-circular-progress';
            span.textContent = options.percent + '%';
                
            if (typeof(G_vmlCanvasManager) !== 'undefined') {
                G_vmlCanvasManager.initElement(canvas);
            }

            var ctx = canvas.getContext('2d');
            canvas.width = canvas.height = options.size;

            el.appendChild(span);
            el.appendChild(canvas);

            ctx.translate(options.size / 2, options.size / 2); // change center
            ctx.rotate((-1 / 2 + options.rotate / 180) * Math.PI); // rotate -90 deg

            //imd = ctx.getImageData(0, 0, 240, 240);
            var radius = (options.size - options.lineWidth) / 2;

            var drawCircle = function(color, lineWidth, percent) {
                    percent = Math.min(Math.max(0, percent || 1), 1);
                    ctx.beginPath();
                    ctx.arc(0, 0, radius, 0, Math.PI * 2 * percent, false);
                    ctx.strokeStyle = color;
                    ctx.lineCap = 'round'; // butt, round or square
                    ctx.lineWidth = lineWidth
                    ctx.stroke();
            };

            drawCircle('#efefef', options.lineWidth, 100 / 100);
            var i = 0; 
            var int = setInterval(function(){
                i++;
                drawCircle(options.color, options.lineWidth, i / 100);
                span.textContent=i+"%"; if(i>=options.percent) {
                    clearInterval(int);
                }
            } ,options.anim_time);

            return true;
        }
    }
});







