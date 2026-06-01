var socket = io();

const container = document.getElementById('container');
const leftCanvas = document.getElementById('leftCanvas');

let vtatCanvas = null;
let energyCanvas = null;

// Initially, make the left canvas occupy the full container
function resizeLeftCanvas() {
    leftCanvas.width = container.clientWidth;
    leftCanvas.height = container.clientHeight;
}

// Resize canvases after adding the second and third canvases
function resizeCanvases() {
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    leftCanvas.width = containerWidth / 2 ; // Adjust for gap
    leftCanvas.height = containerHeight;

    if (document.getElementById('bottomRightCanvas')) {
        const topRightCanvas = document.getElementById('topRightCanvas');
        const bottomRightCanvas = document.getElementById('bottomRightCanvas');

        const rightWidth = containerWidth / 2 - 10; // Adjust for gap
        const rightHeight = (containerHeight - 10) / 2; // Half of the container height, minus gap

        topRightCanvas.width = bottomRightCanvas.width = rightWidth;
        topRightCanvas.height = bottomRightCanvas.height = rightHeight;
    } else if (document.getElementById('topRightCanvas')){
        const topRightCanvas = document.getElementById('topRightCanvas');
        topRightCanvas.width = leftCanvas.width;
        topRightCanvas.height = leftCanvas.height;
    }
}

var gOneAdded = false;
// Add the second canvas dynamically
function addTopRightCanvas(type){
    gOneAdded = true;
    rightContainer.id = 'rightContainer';

    var topRightCanvas = document.createElement('canvas');
    topRightCanvas.id = 'topRightCanvas';

    if (type == "energy"){
        energyCanvas = topRightCanvas;
    } else {
        vtatCanvas = topRightCanvas;
    }
    
    rightContainer.appendChild(topRightCanvas);
    

    container.appendChild(rightContainer);

    // Make the right container visible
    rightContainer.style.display = 'flex';

    // Resize all canvases
    resizeCanvases();
};

var gTwoAdded = false;
function addBottomRightCanvas(type){
    gTwoAdded = true;
    var bottomRightCanvas = document.createElement('canvas');
    bottomRightCanvas.id = 'bottomRightCanvas';

    if (type == "energy"){
        energyCanvas = bottomRightCanvas;
    } else {
        vtatCanvas = bottomRightCanvas;
    }

    rightContainer.appendChild(bottomRightCanvas);
    resizeCanvases();
}

// Adjust canvas size on window resize
window.addEventListener('resize', () => {
    if (document.getElementById('rightContainer')) {
        resizeCanvases();
    } else {
        resizeLeftCanvas();
    }
});

socket.on("SHM_data", function(data) {

    let canvas = leftCanvas;
    let ctx = canvas.getContext("2d");

    ctx.clearRect(0,0, canvas.width, canvas.height);

    let displacement = data[0];
    let velocity = data[1];
    let acceleration = data[2];
    let mass = data[5];
    let x = data[6];
    
    ctx.strokeStyle = "black";

    
    ctx.beginPath();
    ctx.arc(canvas.width/2, canvas.height/2 + displacement, 40, 0, Math.PI * 2, false);
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.beginPath(); 
    ctx.strokeStyle = "black";
    ctx.moveTo(5*canvas.width/16, canvas.height/2);
    ctx.lineTo(5*canvas.width/16, canvas.height/2 + displacement);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.font = "16px Arial";
    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.fillText(mass, canvas.width/2 + 75, canvas.height/2 + displacement)
    ctx.fillText(x, 5*canvas.width/16 + 30, canvas.height/2 + displacement);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.strokeStyle = "grey";
    ctx.moveTo(canvas.width/4, canvas.height/2);
    ctx.lineTo(3*canvas.width/4, canvas.height/2);
    ctx.lineWidth = 1;
    ctx.stroke();

    if (data[3] != 0){
        ctx.beginPath();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "green";
        canvas_arrow(ctx, canvas.width/2 , canvas.height/2 + displacement, canvas.width/2, canvas.height/2 + velocity/2);
        ctx.stroke();
    }

    if (data[4] != 0){
        ctx.beginPath();
        ctx.lineWidth = 2;
        canvas_arrow(ctx, canvas.width/2, canvas.height/2 + displacement, canvas.width/2, canvas.height/2 + acceleration/2);
        ctx.strokeStyle = "red";
        ctx.stroke();
    }
});

let t = 0;
let lastV = [0, 0];
let lastA = [0, 0];
let yv = 0;
let ya = 0;

socket.on("displayVTATGraph", function(data){
    let isVT = data[0];
    let isAT = data[1];
    let v = data[2];
    let a = data[3];
    let tOut = data[4];
    let vOut = data[5];
    let aOut = data[6];

    var vtctx = vtatCanvas.getContext("2d");
    
    let graphEnd = 15*vtatCanvas.width/16;
    let x = t + 0.5;
    vtctx.clearRect(0, 13*vtatCanvas.height/16, vtatCanvas.width, vtatCanvas.height);
    if (isVT == 1){
        yv = vtatCanvas.height/2 + v/8
        vtctx.beginPath();
        if (t != 0){
            vtctx.moveTo(lastV[0], lastV[1]);
            vtctx.lineTo(x, yv);
            vtctx.lineWidth = 2;
            vtctx.strokeStyle = "green";
            vtctx.stroke();
        }
        else {
            vtctx.moveTo(0, yv);
            vtctx.lineTo(0, yv);
            vtctx.lineWidth = 2;
            vtctx.strokeStyle = "green";
            vtctx.stroke();
            vtctx.beginPath();
            vtctx.strokeStyle = "black";
            vtctx.lineWidth = 0.5;
            canvas_arrow(vtctx, 0, vtatCanvas.height/2, graphEnd, vtatCanvas.height/2);
            vtctx.stroke();
        }
        lastV = [x, yv];
        vtctx.beginPath();
        vtctx.font = "16px Arial";
        vtctx.fillStyle = "black";
        vtctx.textAlign = "center";
        vtctx.fillText(vOut, graphEnd - 30, 7*vtatCanvas.height/8 + 15);
        vtctx.stroke(); 
    }
    if (isAT == 1){
        ya = vtatCanvas.height/2 + a/8
        vtctx.beginPath();
        if (t != 0){
            vtctx.moveTo(lastA[0], lastA[1]);
            vtctx.lineTo(x, ya);
            vtctx.lineWidth = 2;
            vtctx.strokeStyle = "red";
            vtctx.stroke();
        }
        else {
            vtctx.moveTo(0, ya);
            vtctx.lineTo(0, ya);
            vtctx.lineWidth = 2;
            vtctx.strokeStyle = "red";
            vtctx.stroke();
            vtctx.beginPath();
            vtctx.strokeStyle = "black";
            vtctx.lineWidth = 0.5;
            canvas_arrow(vtctx, 0, vtatCanvas.height/2, graphEnd, vtatCanvas.height/2);
            vtctx.stroke();
        }
        lastA = [x, ya];
        vtctx.beginPath();
        vtctx.font = "16px Arial";
        vtctx.fillStyle = "black";
        vtctx.textAlign = "center";
        vtctx.fillText(aOut, graphEnd - 30, 7*vtatCanvas.height/8 + 30);
        vtctx.stroke(); 
    }

    
    t += 0.5
    if (x > graphEnd){
        t = 0;
        vtctx.clearRect(0,0, vtatCanvas.width, vtatCanvas.height);
    }
    
    
    vtctx.beginPath();
    vtctx.font = "16px Arial";
    vtctx.fillStyle = "black";
    vtctx.textAlign = "center";
    vtctx.fillText(tOut, graphEnd - 30, 7*vtatCanvas.height/8);
    vtctx.stroke(); 
    
    
});

socket.on("displayEnergy", function(data){
    ke = data[0];
    pe = data[1];
    time = data[2];
    totalEnergy = data[3];
    energyChart.data.labels.push(time.toFixed(2));
    energyChart.data.datasets[0].data.push(ke.toFixed(2));
    energyChart.data.datasets[1].data.push(pe.toFixed(2));
    energyChart.data.datasets[2].data.push(totalEnergy.toFixed(2));

    if (energyChart.data.labels.length > 100) {
        energyChart.data.labels.shift();
        energyChart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    energyChart.update();
});

var vtatGraphMade = false;
var energyGraphMade = false;

function GraphInitialiser(type){
    if (vtatGraphMade == false){
        vtatGraphMade = true;
        if (gOneAdded == false){
            addTopRightCanvas(type);
        } else if (gTwoAdded == false){
            addBottomRightCanvas(type);
    }};
}

socket.on("vtGraph", function(){
    GraphInitialiser("");
    socket.emit("vt_graph_made")
});

socket.on("atGraph", function(){
    GraphInitialiser("");
    socket.emit("at_graph_made")
});

let energyChart = null;

socket.on("energyGraph", function(){
    if (energyGraphMade == false){
        energyGraphMade = true;
        if (gOneAdded == false){
            addTopRightCanvas("energy");
        } else if (gTwoAdded == false){
            addBottomRightCanvas("energy");
        }
        let energyctx = energyCanvas.getContext("2d");
        energyChart = new Chart(energyctx, {
            type: 'line',
            data: {
              labels: [], // Time labels
              datasets: [
                { label: 'Kinetic Energy (KE)', data: [], borderColor: 'blue', fill: false },
                { label: 'Potential Energy (PE)', data: [], borderColor: 'green', fill: false },
                { label: 'Total Energy (E)', data: [], borderColor: 'red', fill: false },
              ]
            },
            options: {
              responsive: true,
              animation: false,
              plugins: { legend: { position: 'top' } },
              scales: {
                x: { title: { display: true, text: 'Time (s)' } },
                y: { title: { display: true, text: 'Energy (J)' } }
              }
            }
        });
        };
    socket.emit("energy_graph_made")
});

// Initialize the first canvas
resizeLeftCanvas();
socket.emit("request_SHM_data");