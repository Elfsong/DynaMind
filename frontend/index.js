// Author: Du Mingzhe (mingzhe@nus.edu.sg)
// Date: 2023-04-29

const socket = io("http://0.0.0.0:12345");

const submit_button = document.getElementById("submit-button");
const submit_input  = document.getElementById("submit-input");
const message_container = document.getElementById("message-container");

var last_system_msg = null;

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
    } else if (m_style == "speak") {
        message_el.classList.add("alert", "alert-success");
        message_container.removeChild(last_system_msg);
    } else if (m_style == "system") {
        message_el.classList.add("alert", "alert-light");
        last_system_msg = message_div;
    } else if (m_style == "task") {
        message_el.classList.add("alert", "alert-light");
        message_container.removeChild(last_system_msg);
    } else {
        message_el.classList.add("alert", "alert-secondary");
    }

    // message_el.classList.add("alert", "alert-primary");
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

$(".dropdown-menu li a").click(function(){
    $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
});
