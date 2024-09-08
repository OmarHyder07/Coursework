var id = null;
function myMove(xVel, yVel) {
  var elem = document.getElementById("myAnimation");   
  var posx = 0;
  var posy = 0;
  clearInterval(id);
  id = setInterval(frame, 10); // Calls frame method every 10ms (1000 would be every 1s)
  function frame() {
    if (posx == 100 | posy == 200) { // Define end point of particle
      clearInterval(id);
    } else {
      posx+= xVel; 
      posy+= yVel;
      elem.style.top = posy + 'px'; 
      elem.style.left = posx + 'px'; 
    }
  }
}

function makePoint() {
  strokeWeight(2);
  point(40,40);
}


// JS animation
// Element taken from HTML
// x coordinate:
// elem.style.left = x + 'px'
// where x is number of pixels from left
// y coordinate is same but from top

// Every frame need to send new velocities from main.py
// Could store original position in JS?
// 50 fps is every 20ms 