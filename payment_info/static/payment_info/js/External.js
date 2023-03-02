// External

// disable otree headers
element = document.getElementById('_otree-title')
element.remove()

var myVar;

myVar = setTimeout(showPage, 5000);


function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("content").style.display = "block";
}


// function to send information to external database
var submitted = false;

function postToGoogle() {
    var participant_code = $('#participant_code').val();
    var payoff = $('#payoff').val();
    var name = $('#name').val();
    var iban = $('#iban').val();
    var iban_confirmation = $('#iban_confirm').val();

    $.ajax({
        url: "https://docs.google.com/forms/d/e/1FAIpQLScc7TncWV2_Tzwurq3_xz7jgIEz0f0dc1ZsIQBD3lzZq55E9A/formResponse",
        data: {
            "entry.564270328": participant_code, "entry.1632998851": payoff,
            "entry.487668435": name, "entry.1271164732": iban, "entry.979605448": iban_confirmation
        },
        type: "POST",
        dataType: "xml",
        statusCode: {
            0: function () {
                return false
                //Success message
            },
            200: function () {
                return true
                //Success Message
            }
        }
    });
}

// format spacing for iban input
document.getElementById('iban').addEventListener('input', function (e) {
//    e.target.value = e.target.value.replace(/[^\dA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
   e.target.value = e.target.value.replace(/[^\da-zA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
});

document.getElementById('iban_confirm').addEventListener('input', function (e) {
  e.target.value = e.target.value.replace(/[^\da-zA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
//  e.target.value = e.target.value.replace(/[^\dA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
});


function validateiban(){
    var iban = document.getElementById('iban'),
    confirm_iban = document.getElementById('iban_confirm')

    if (iban.value==confirm_iban.value) {
        postToGoogle.call()
        confirm_iban.setCustomValidity("");
    }
    else {
        confirm_iban.setCustomValidity("IBANs don't match!");
}
}


