// Canvas setup
var canvas = document.getElementById("Canvas"); // Links to div id="Canvas"
var context = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

var particles = [];

function drawParticles() {
    // Clear canvas 
    context.clearRect(0,0, canvas.width, canvas.height);

    for(var i = 0; i < particles.length; i++) {
        var p = particles[i];
        context.beginPath();
        // arc draws particle/circle
        context.arc(p.x, p.y, p.radius/2, 0, Math.PI * 2, false);
        context.fillStyle = "red";
        context.fill();
        context.closePath();
    }
}

function updateCanvas() {
    drawParticles();
    requestAnimationFrame(updateCanvas);
}

requestAnimationFrame(updateCanvas);

var eventSource = new EventSource("/stream");

eventSource.onmessage = function(event) {
    var dataArray = JSON.parse(event.data);
    particles = dataArray.map(function(p) {
        return {
            x: p[0], 
            y: p[1],
            radius: p[2]
        }
    })
}