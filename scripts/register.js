
window.onload = function() {
    document.getElementById("register-form").addEventListener("submit", function(e) {
        e.preventDefault();

        fname = document.getElementById("fname").value.trim();
        lname = document.getElementById("lname").value.trim();
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

        fetch("/register", {
            method: "POST",
            body: JSON.stringify({
                "fname": fname,
                "lname": lname,
                "phone": phone,
                "email": email,
                "date": date 
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then(data => {
            console.log("Success:", data);
        });
    });
}
