document.addEventListener("DOMContentLoaded", add_logic);

let socket;

function add_logic(){
    toggle_password_button();
    create_chat_dialog();
    listen_to_send();

    socket = connect_websocket();
    scroll_to_bottom();
}


function toggle_password_button(){
    let toggle_buttons = document.querySelectorAll("button.toggle-password");

    toggle_buttons.forEach(function(button){
        let visible = false;
        const input_field = document.querySelector(`#${button.dataset.target}`);

        button.addEventListener("click", function(){
            visible = !visible;

            input_field.type = visible ? "text" : "password";
        });
    });
}

function create_chat_dialog(){
    const open_dialog_button = document.querySelector("#open-dialog-button");
    const close_dialog_button = document.querySelector("#close-dialog-button");

    const dialog = document.querySelector("#create-chat-dialog");

    if(!open_dialog_button || !close_dialog_button || !dialog){
        return;
    }

    open_dialog_button.addEventListener("click", function(){
        dialog.showModal(); // showModal bloqueia o resto da página
    });

    close_dialog_button.addEventListener("click", function(){
        dialog.close();
    });

    dialog.addEventListener("click", function(event){
        if(event.target === dialog){
            dialog.close();
        }
    });
}

function listen_to_send(){
    const send_message_button = document.querySelector("#send-message-button");

    const input = document.querySelector("#message-input");
    
    if (!send_message_button || !input){
        return;
    }
    send_message_button.addEventListener("click", send_message);

    input.addEventListener("keydown", function(event){
        if (event.key === "Enter" && !event.shiftKey){
            event.preventDefault();
            send_message();
        }
    });
}

function send_message(){
    const input = document.querySelector("#message-input");
    
    if (!input.value.trim()){
        return;
    }

    const body = document.querySelector("#chat-body")
    const recipient_id = body.dataset.recipientId // * sempre vem como string, não devo esquecer de converter!
    
    const info = JSON.stringify({
        content: input.value,
        recipient_id: recipient_id
    });

    socket.send(info);

    input.value = "";
}

function connect_websocket(){
    let protocol = location.protocol === "https:" ? "wss:" : "ws:";

    const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

    socket.addEventListener("open", function(){
        console.log("Websocket conectado!");
    });

    socket.addEventListener("message", function(event){
        console.log("Recebi: ", event.data);

        const message = JSON.parse(event.data)
        add_message(message);
    });

    socket.addEventListener("error", function(event){
        console.error("Erro no socket! ", event)
    });

    socket.addEventListener("close", function(event){
        console.error("Websocket fechado! ", event.code, event.reason)
    });

    return socket;
}

function scroll_to_bottom(){
    const messages = document.querySelector(".messages");

    if (!messages){
        return;
    }

    messages.scrollTop = messages.scrollHeight;


}

function add_message(message){
    const body = document.querySelector("#chat-body");
    const other_user_id = Number(body.dataset.recipientId);

    const no_messages = document.querySelector("#no-messages-div");

    if (no_messages){
        no_messages.remove()
    }

    const messages = document.querySelector(".messages");
    const message_div = document.createElement("div");

    if(message.user_id === other_user_id){
        message_div.classList.add("received-message");
    }
    else {
        message_div.classList.add("sent-message");
    }

    const message_content = document.createElement("p");
    message_content.textContent = message.content;

    const time_stamp = document.createElement("span");

    console.log(message);
    console.log(message.timestamp);
    
    const date = new Date(message.timestamp);

    time_stamp.textContent = date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    message_div.appendChild(message_content);
    message_div.appendChild(time_stamp);

    messages.appendChild(message_div);

    scroll_to_bottom();
}