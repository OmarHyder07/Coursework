var socket = io();

var canvas = document.getElementById("Canvas"),
    hasInput = false;
    context = canvas.getContext("2d");
canvas.width = window.innerWidth/1.2;
canvas.height = window.innerHeight/1.2;

function updateWindow() {
    // Dynamically changes canvas size when the webpage window size is changed
    canvas.width = window.innerWidth/1.2;
    canvas.height = window.innerHeight/1.2;
    socket.emit("window_size", {width: window.innerWidth/1.2, height: window.innerHeight/1.2});
}

window.addEventListener("resize", updateWindow);
updateWindow();

socket.on("particle_data", function(particles) {
    // Method for taking frame data from backend and animating the particles
    context.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        if (p[3] != 1){
            context.beginPath();
            // arc draws particle/circle
            context.arc(p[0], p[1], p[2], 0, Math.PI * 2, false);
            // context.fillStyle = "red";
            // context.fill();

            context.lineWidth = 1;
            context.stroke();

            context.font = "12px Arial";
            context.fillStyle = "black";
            context.textAlign = "center";
            if (p[8] != 1){
                context.fillText(p[4], p[0], p[1] + p[2] + 20);
            }
            if (p[7] != 0 && p[8] != 1){
               canvas_arrow(context, p[0], p[1], p[0] + p[5]/4, p[1] + p[6]/4);
            }
            
            context.stroke();

            context.closePath();
        }
    }
});

socket.emit("request_particle_data");