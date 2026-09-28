document.addEventListener("DOMContentLoaded", add_logic);

function add_logic(){
    toggle_password_button();
    create_chat_dialog();
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
        console.log("Create chat dialog elements loading failed!");
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