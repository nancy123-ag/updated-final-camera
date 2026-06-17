function startBackend() {
    fetch("http://127.0.0.1:5000/start")
    .then(res => res.json())
    .then(data => {
        document.getElementById("status").innerText =
        "Status: " + data.status;
    })
}

function stopBackend() {
    fetch("http://127.0.0.1:5000/stop")
    .then(res => res.json())
    .then(data => {
        document.getElementById("status").innerText =
        "Status: " + data.status;
    })
}
