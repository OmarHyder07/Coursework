const textarea = document.getElementById('content'); 
const select = document.getElementById('phrase-select');

function sendPrompt() {
  // Gets prompt from textarea and sends it to backend
    var text = document.getElementById("content")
    socket.emit("newPrompt", { text: text.value});
    text.value = "";
};

textarea.addEventListener('click', function () {
    select.style.display = 'block'; // Shows the dropdown menu when textarea is clicked on
});

select.addEventListener('change', function () {
  // Adds clicked on phrase to textarea
    const selectedPhrase = select.value;
    if (selectedPhrase) {
      textarea.value += (textarea.value ? '\n' : '') + selectedPhrase;
      select.value = ""; // Reset the dropdown to default
    }
    select.style.display = 'none'; // Hide the dropdown after selection
  }
);

document.addEventListener('click', function (event) {
  // Hides dropdown menu when user clicks off textarea
    if (!textarea.contains(event.target) && !select.contains(event.target)) {
      select.style.display = 'none';
    }
  }
);

socket.on("update_dropdown", function(data) {
  // Adds child prompts to dropdown menu
    const option = document.createElement("option");
    option.value = data;
    option.textContent = data;
    select.appendChild(option);
});

socket.on("displayData", function(data){
  var list = document.getElementById("dataList");
  list.innerHTML = ''; 
  for(var i =0, length=data.length; i<length; i++){
    const newLine = document.createElement("li");
    newLine.textContent = data[i]
    list.appendChild(newLine);
  }
});

socket.on("confirm", function() {
    socket.emit("confirmNewPrompt");
})

socket.on("disconnect", function(redirect){
    socket.disconnect();
    window.location.href = redirect; //redirects to new URL
});

function canvas_arrow(context, fromx, fromy, tox, toy) {
  // Draws arrow
    var headlen = 10; // length of head in pixels
    var dx = tox - fromx;
    var dy = toy - fromy;
    var angle = Math.atan2(dy, dx);
    context.moveTo(fromx, fromy);
    context.lineTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    context.moveTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
};
