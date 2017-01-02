// source: http://keithscode.com/tutorials/javascript/3-a-simple-javascript-password-validator.html 
// creates function to display colors for password validation
function PassValidation()
{
    // create variables for passwords
    var password = document.getElementById('password');
    var password2 = document.getElementById('password2');
    // create variable for confirmation message
    var message = document.getElementById('confirmMessage');
    // create variables for the colors
    var correctcolor = "#28bb9c";
    var incorrectcolor = "#ff6666";
    //Compare the values in the password field 
    //and the confirmation field
    if(password.value == password2.value){
        //The passwords match. 
        //Set the color to the good color and inform
        //the user that they have entered the correct password 
        password2.style.backgroundColor = correctcolor;
        message.style.color = correctcolor;
        message.innerHTML = "Passwords Match"
    }else{
        // if the passwords do not match, display incorrectcolor
        password2.style.backgroundColor = incorrectcolor;
        message.style.color = incorrectcolor;
        message.innerHTML = "Passwords Do Not Match"
    }
}

