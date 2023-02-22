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


// Bid button function
// $(document).ready(function() {
//     $("#btn-yes").click(function(){
//         document.getElementById('bid_hidden').value = 'True';
//     });
//     $("#btn-no").click(function(){
//         document.getElementById('bid_hidden').value = 'False';
//     });
//     // keeps them selected
//     $('#btn-yes').on('click', function(){
//         $('#btn-no').removeClass('active');
//         $('#btn-no').removeClass('selected_red');
//         $(this).addClass('active');
//         $(this).addClass('selected_green');
//     });
//     $('#btn-no').on('click', function(){
//         $('#btn-yes').removeClass('active');
//         $('#btn-yes').removeClass('selected_green');
//         $(this).addClass('active');
//         $(this).addClass('selected_red');
//     });
// });

//Check if bid is given before submitting the form
function checkValue() {
    var form = document.getElementById('bid_hidden')
    if (form.value == ""){
        alert("Please make a choice.")
        return false
    } else {
        return true
    }
}

