var socket = io();

var canvas = document.getElementById("Canvas"),
    hasInput = false;
    context = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

canvas.onclick = function(e) {
    if (hasINput);
}

function addInput(x, y) {
    var input = document.createElement("input");
    input.type = "text";
    input.style.position = "fixed";
    input.style.left = (canvas.width/4) + "px";
    input.style.top = (canvas.height + 20) + "px";
    
    input.onkeydown = handleEnter;

    document.body.appendChild(input);
    input.focus();
    hasInput = True;

}

function updateWindow() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    socket.emit("window_size", {width: window.innerWidth, height: window.innerHeight});
}

window.addEventListener("resize", updateWindow);
updateWindow()

socket.on("particle_data", function(particles) {

    context.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        if (p[3] != 0){
            context.beginPath();
            // arc draws particle/circle
            context.arc(p[0], p[1], p[2]/2, 0, Math.PI * 2, false);
            context.fillStyle = "red";
            context.fill();
            context.closePath();
        }
    }
});


socket.emit("request_data");