document.addEventListener("DOMContentLoaded", add_logic);

function add_logic(){
    toggle_password_button();
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