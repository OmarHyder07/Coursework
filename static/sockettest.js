var socket = io();

var canvas = document.getElementById("Canvas");
var particle = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

function updateWindow() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    socket.emit("window_size", {width: window.innerWidth, height: window.innerHeight});
}

window.addEventListener("resize", updateWindow);
updateWindow()

socket.on("particle_data", function(particles) {

    particle.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        if (p[3] != 0){
            particle.beginPath();
            // arc draws particle/circle
            particle.arc(p[0], p[1], p[2]/2, 0, Math.PI * 2, false);
            particle.fillStyle = "red";
            particle.fill();
            particle.closePath();
        }
    }
});


socket.emit("request_data");