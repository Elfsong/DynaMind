// Author: Du Mingzhe (mingzhe@nus.edu.sg)
// Date: 2023-04-29

const socket = io("http://localhost:12345");

const submit_button = document.getElementById("submit-button");
const submit_input  = document.getElementById("submit-input");
const message_container = document.getElementById("message-container");

socket.on("message", function(data) {
    console.log(data);

    const message_el = document.createElement("div");
    message_el.classList.add('alert', 'alert-primary');
    message_el.setAttribute('role', 'alert');
    message_el.textContent = data.content;

    message_container.appendChild(message_el);
    message_el.scrollIntoView();
});

submit_button.onclick = function() {
    socket.timeout(5000).emit("message", {"feedback": submit_input.value}, (err) => {
        if (err) { console.log("the server did not acknowledge the event in the given delay"); }
    });
    submit_input.value = "";
}

submit_input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.key === 'Enter') {submit_button.click();}
});
