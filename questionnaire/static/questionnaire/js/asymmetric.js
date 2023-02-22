// Confirm information function in asymmetric treatment
var confirmed = false

$(document).ready(function() {
    $("#confirm_asymmetric").click(function(){
        confirmed = true
    });
});

function checkbeforesubmit() {
    if (confirmed == false){
        alert("Please click the OK button that you have seen the message.")
        return false
    } else {
        return true
    }
}


