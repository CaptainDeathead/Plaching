function get_wedding_id() {
    const pathParts = window.location.pathname.split("/").filter(Boolean); 

    if (pathParts[0] === "weddings" && pathParts.length > 1) {
        const weddingId = pathParts[1];
        return weddingId;
    } else {
        console.log("weddingId not found in URL path");
    }
}

window.onload = function() {
    setupUploadMenu();

    const weddingId = get_wedding_id()

    fetch("/weddings/" + weddingId + "/getInfo")
        .then(response => response.json())
        .then(data => {
            let fname = data.fname;
            let lname = data.lname;
            let pfname = data.pfname;
            window.numPhotos = data.numPhotos;

            document.getElementById("title").innerText = document.getElementById("title").innerText.replace("FILLIN_FNAME", fname).replace("FILLIN_PFNAME", pfname).replace("FILLIN_LNAME", lname);

            populate_photos(window.numPhotos);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

function display_image(index) {
    document.getElementById("photo-index").innerText = (index + 1).toString() + " / " + numPhotos.toString();

    let view_img = document.getElementById("photo-view-img");
    view_img.src = window.location.href + "/photos/" + index.toString();

    document.getElementById("photo-view-overlay").style.display = "block";
}

function loadBatch(batchSize, index, imageUrls) {
    const container = document.getElementById("photo-album");
    for (let i = 0; i < batchSize && index < imageUrls.length; i++, index++) {
        const currentIndex = index;
        const img = new Image();

        img.loading = "lazy"; // native lazy-loading hint
        img.src = imageUrls[index];
        img.onclick = () => display_image(currentIndex);
        container.appendChild(img);
    }
    if (index < imageUrls.length) {
        setTimeout(() => loadBatch(batchSize, index, imageUrls), 200); // small pause before next batch
    }
}

function populate_photos(numPhotos) {
    let batchSize = 10;
    let index = 0;

    let imageUrls = [];

    for (let i = 0; i < numPhotos; i++) {
        imageUrls.push(window.location.href + "/thumbnails/" + i.toString());
    }

    loadBatch(batchSize, index, imageUrls);
}

function setupUploadMenu() {
    document.getElementById("openUploader").onclick = () => {
        document.getElementById("uploadOverlay").style.display = "block";
    };

    document.getElementById("closeUploader").onclick = () => {
        document.getElementById("uploadOverlay").style.display = "none";
    };

    document.getElementById("uploadBtn").onclick = () => {
        const weddingId = get_wedding_id();

        const file = document.getElementById("fileInput").files[0];
        if (!file) {
            alert("Please select a file.");
            return;
        }

        document.getElementById("uploadOverlay").style.display = "none";
        document.body.innerHTML = "<h1>Uploading...</h1>\n<h2>Please wait (Yes it is actually uploading). A popup will appear when the upload is complete. Please stay on this page.</h2>";

        const formData = new FormData();
        formData.append("file", file);

        fetch("/weddings/" + weddingId + "/photos/upload", {
            method: "POST",
            body: formData
        })
        .then(res => res.text())
        .then(data => {
            alert(data);
            window.location.reload();
        })
        .catch(err => {
            console.error(err);
            alert("Upload failed.");
            window.location.reload();
        });
    };
}