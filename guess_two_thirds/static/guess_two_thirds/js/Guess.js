// Popup
function hideShow(id) {
    let x = document.getElementById(id);
    if (x.style.display === "none") {
        x.style.display = "grid";
        $('body').css('overflow', 'hidden');
    } else {
        x.style.display = "none";
        $('body').css('overflow', 'auto');
    }
}
