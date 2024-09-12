// requestAnimationFrame(updateCanvas) ---> calls drawParticles --->
// requestAnimationFrame....
// drawParticles uses the particles array which is updated on each frame.
// It doesn't matter the order of calling for animationframes and sending in 
// particle positions from the backend. if drawParticles is called multiple
// times before particle positions are sent again, it will just redraw the same
// thing and seem as though nothing has changed. 
// Therefore it's ideal to have it be called many times per second so as to
// instantly update when data IS sent. 


// Canvas setup
var canvas = document.getElementById("Canvas"); // Links to div id="Canvas"
var particle = canvas.getContext("2d"); // Allows rendering of 2d object
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

var particles = [];

function drawParticles() {
    // Clear canvas 
    particle.clearRect(0,0, canvas.width, canvas.height);
    for(var i = 0; i < particles.length; i++) {     
        var p = particles[i];     
        if (p.isAir != 0){
            particle.beginPath();
            // arc draws particle/circle
            particle.arc(p.x, p.y, p.radius/2, 0, Math.PI * 2, false);
            particle.fillStyle = "red";
            particle.fill();
            particle.closePath();
        }
    }
}

function updateCanvas() {
    drawParticles();
    // Recursively calls updateCanvas. Method makes browser run updateCanvas
    // BEFORE the next frame is painted. 
    requestAnimationFrame(updateCanvas);
}

// Tells browser we want to perform an animation;
// requests browser to use our function updateCanvas BEFORE the next frame.
requestAnimationFrame(updateCanvas);

var eventSource = new EventSource("/stream");

// Function runs on event (streamed particlce data from backend)
eventSource.onmessage = function(event) {
    var dataArray = JSON.parse(event.data);
    // Js array.map(function) creates a new array from 
    // calling a function for every array element.
    // js is a very odd language: we are calling the function which is also
    // within the assignment. erm...!
    particles = dataArray.map(function(p) {
        return { // JS object which holds key-value pairs 
            x: p[0], 
            y: p[1],
            radius: p[2],
            isAir: p[3]
        }
    })
}