var socket = io();
var path = [];

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

socket.on("widthChange", function(scalar){
    // When the width of area is changed, the trajectories need to be scaled to fit the new width
    var newpath = [];
    for(var i = 0, length = path.length; i < length; i++){
        let p = path[i];
        newpath.push({x: p.x * scalar, y: canvas.height - ((canvas.height - p.y)* scalar)});
    }
    globalThis.path = newpath;
});

socket.on("projection_data", function(data) {
    // Takes in frame data from backend and animates it here
    let x = data[0];
    let y = data[1];
    let radius = data[2];
    let vx = data[3];
    let vy = data[4];
    let isArrows = data[5];
    let width = data[6];
    let height = data[7];

    context.clearRect(0,0, canvas.width, canvas.height);

    context.strokeStyle = "grey";
    context.beginPath();
    for (let i =0; i < path.length; i++) { //draws particle trajectories
        let p = path[i];
        if (i===0) {
            context.moveTo(p.x , p.y );
        } else {
            context.lineTo(p.x , p.y );
        }
    }
    context.stroke();

    context.beginPath();
    context.arc(x, y, radius, 0, Math.PI * 2, false);
    context.lineWidth = 1;
    context.stroke();
    context.font = "12px Arial";
    context.fillStyle = "black";
    context.textAlign = "center";
    context.fillText(width, x, y-100);

    context.lineWidth=1;
    if (isArrows != 0) {
        canvas_arrow(context, x, y, x, y + vy);
        canvas_arrow(context,x, y,x +vx, y);
    }

    context.stroke();
    context.closePath();

    path.push({x: x, y: y});   
});

socket.emit("request_projection_data");