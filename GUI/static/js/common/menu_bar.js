var showMenu = false;

function showMenuBar() {
    showMenu = !showMenu;
    var menu = document.getElementById('menu');
    if(showMenu){
        menu.style.display = "flex";
    }
    else{
        menu.style.display = "none";
    }
}