var socket = io();
let path = [];

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

socket.on("mag_data", function(data) {
    // Takes in data from the backend to be animated here
    let x = data[0];
    let y = data[1];
    let B = data[2];
    let r = data[3];
    let v = data[4];
    let a = data[5];
    context.clearRect(0,0, canvas.width, canvas.height);

    context.strokeStyle = "grey";
    context.beginPath();
    for (let i =0; i < path.length; i++) { // Draws trajectories
        let p = path[i];
        if (i===0) {
            context.moveTo(p.x , p.y );
        } else {
            context.lineTo(p.x , p.y );
        }
    }
    context.stroke();

    context.beginPath(); // Draws particle
    context.arc(x, y, 5, 0, Math.PI*2, false);
    context.lineWidth = 1;
    context.stroke();  

    context.strokeStyle = "black"; //Draws boundary
    context.beginPath(); 
    context.moveTo(canvas.width/16, 0);
    context.lineTo(canvas.width/16, canvas.height);
    context.stroke();

    path.push({x: x, y: y});

    let scale = 3*Math.abs(B);
    let space = 15*canvas.width/16;
    let noCrosses = space/scale;

    if (B < 0) { // This draws the background depending on magnetic field strength
        for (let y = 20; y < canvas.height-10; y += noCrosses) {
            for (let x = 2*canvas.width/16-10; x < canvas.width-10; x += noCrosses){
                drawFieldIn(context, x, y, B);
            }}
    } else if (B > 0) {
        for (let y = 20; y < canvas.height-10; y += noCrosses) {
            for (let x = 2*canvas.width/16-10; x < canvas.width-10; x += noCrosses){
                drawFieldOut(context, x, y);
            }}
    }

    // Writes length scale
    context.beginPath();
    context.font = "12px Arial";
    context.fillStyle = "black";
    context.textAlign = "center";
    context.fillText("0", canvas.width/32, canvas.height/2)
    context.fillText(Number((3*r/2).toPrecision(4)), canvas.width/16 - 30, 20)
    context.fillText(Number((r).toPrecision(4)), canvas.width/16 - 30, canvas.height/6);
    context.fillText(Number((r/2).toPrecision(4)), canvas.width/16 - 30, canvas.height/3);
    context.fillText(Number((-r/2).toPrecision(4)), canvas.width/16 - 30, 2*canvas.height/3);
    context.fillText(Number((-r).toPrecision(4)), canvas.width/16 - 30, 5*canvas.height/6);
    context.fillText(Number((-3*r/2).toPrecision(4)), canvas.width/16 - 30, canvas.height - 20);
    context.stroke();

    // Velocity and acceleration arrows
    context.beginPath();
    context.strokeStyle = "green";
    canvas_arrow(context, x, y, x + v[0] , y + v[1]);
    context.stroke();
    context.beginPath();
    context.strokeStyle = "red";
    canvas_arrow(context, x, y, x + a[0], y + a[1]);
    context.stroke();
});

function drawFieldIn(context, x, y, B) {
    context.strokeStyle = "blue";
    context.beginPath();
    context.moveTo(x-B, y+B);
    context.lineTo(x+B, y-B);
    context.moveTo(x-B, y-B);
    context.lineTo(x+B, y+B);
    context.stroke();
};

function drawFieldOut(context, x, y) {
    context.strokeStyle = "green";
    context.beginPath();
    context.arc(x, y, 1.5, 0, Math.PI*2, false);
    context.lineWidth = 1;
    context.stroke();
};

socket.emit("request_mag_data");