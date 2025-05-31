import QRCodeStyling from "https://esm.sh/qr-code-styling@1.5.0";

window.onload = function() {
    const searchParams = new URLSearchParams(window.location.search);
    const id = searchParams.get("id")

    document.getElementById("wedding-link").src = "/wedding?" + id;

    const qrCode = new QRCodeStyling({
        width: 300,
        height: 300,
        data: "http://192.168.0.36:5000/wedding?" + id,
        image: "http://192.168.0.36:5000/favicon.png",
        dotsOptions: {
            color: "#000",
            type: "rounded"
        },
        backgroundOptions: {
            color: "#fff",
        },
        imageOptions: {
            crossOrigin: "anonymous",
            margin: 10
        }
    });

    qrCode.append(document.getElementById("qr-img"));
}