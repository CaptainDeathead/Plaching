
window.onload = function() {
    document.getElementById("register-form").addEventListener("submit", function(e) {
        e.preventDefault();

        fname = document.getElementById("fname").value.trim();
        lname = document.getElementById("lname").value.trim();
        pfname = document.getElementById("pfname").value.trim();
        phone = document.getElementById("phone").value.trim();
        email = document.getElementById("email").value.trim();
        date = document.getElementById("date").value.trim();

        if (fname == '') {
            alert("First name is required!");
            return;
        }
        if (lname == '') {
            alert("Last name is required!");
            return;
        }
        if (pfname == '') {
            alert("partner's first name is required!");
            return;
        }
        if (phone == '') {
            alert("Phone number is required!");
            return;
        }
        if (email == '') {
            alert("Email is required!");
            return;
        }
        if (date == '') {
            alert("Date is required!");
            return;
        }

        var failed = false;

        showLoadingScreen();

        fetch("/register", {
            method: "POST",
            body: JSON.stringify({
                "fname": fname,
                "lname": lname,
                "pfname": pfname,
                "phone": phone,
                "email": email,
                "date": date 
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then(response => {
            if (response.status == 409) {
                alert("Wedding already found with this email address!");
                failed = true;
                hideLoadingScreen();
            }
            return response.json();
        })
        .then(data => {
            if (!failed) {
                console.log("Success:", data);
                document.getElementsByTagName("body")[0].innerHTML = "<h1>Already registered! Verify email if you have not already.</h1>";
                window.location.href = "/register_next";
            }
        });
    });
}

function showLoadingScreen() {
    document.getElementById("loader").style.display = "block";
    document.getElementById("submit-btn").disabled = true;
}

function hideLoadingScreen() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("submit-btn").disabled = false;
}