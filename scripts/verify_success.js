document.addEventListener("DOMContentLoaded", function(arg) {
    const searchParams = new URLSearchParams(window.location.search);
    const id = btoa(searchParams.get("email"));

    const url = "https://plaching.plazmasoftware.com/weddings/" + id;

    document.getElementById("wedding-link").href = document.getElementById("wedding-link").textContent = url;
    document.getElementById("qr-img").src = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + url;
});