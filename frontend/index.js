// Author: Du Mingzhe (mingzhe@nus.edu.sg)
// Date: 2023-04-29

const socket = io("http://localhost:12346");

const submit_button = document.getElementById("submit-button");
const submit_input  = document.getElementById("submit-input");
const message_container = document.getElementById("message-container");

// var credit = 5;

function add_message(data) {
    const m_style = data.style
    const message_div = document.createElement("div");
    if (m_style == "human"){
        message_div.classList.add("d-flex", "flex-row-reverse");
    } else {
        message_div.classList.add("d-flex", "flex-row");
    }

    const message_el = document.createElement("div");
    if (m_style == "human") {
        message_el.classList.add("alert", "alert-primary");
    } else if (m_style == "thought") {
        message_el.classList.add("alert", "alert-secondary");
    } else if (m_style == "reasoning") {
        message_el.classList.add("alert", "alert-secondary");
    } else if (m_style == "plan") {
        message_el.classList.add("alert", "alert-secondary");
    } else if (m_style == "criticism") {
        message_el.classList.add("alert", "alert-secondary");
    } else if (m_style == "speak") {
        message_el.classList.add("alert", "alert-success");
    } else if (m_style == "system") {
        message_el.classList.add("alert", "alert-light");
    } else if (m_style == "resource") {
        message_el.classList.add("alert", "alert-secondary");
    } else {
        message_el.classList.add("alert", "alert-secondary");
    }

    message_el.classList.add("alert", "alert-primary");
    message_el.setAttribute('role', 'alert');
    message_el.textContent = data.content;
    
    message_div.appendChild(message_el);
    message_container.appendChild(message_div);
    message_el.scrollIntoView();
}

socket.on("message", function(data) {
    console.log(data);
    add_message(data);
});

submit_button.onclick = function() {
    socket.timeout(5000).emit("receive", {"user_input": submit_input.value}, (err) => {
        if (err) { console.log("the server did not acknowledge the event in the given delay"); }
    });
    add_message({"content": submit_input.value, "style": "human"});
    submit_input.value = "";
}

submit_input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.key === 'Enter') {submit_button.click();}
});
