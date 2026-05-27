let map = L.map("map").setView([25.7617, -80.1918], 15);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

let boatMarker = L.marker([25.7617, -80.1918]).addTo(map);
boatMarker.bindPopup("USV Position").openPopup();

function updateTelemetry() {
    fetch("/api/status")
        .then(response => response.json())
        .then(data => {
            document.getElementById("status").textContent = data.status;
        });

    fetch("/api/telemetry")
        .then(response => response.json())
        .then(data => {
            document.getElementById("lat").textContent = data.latitude;
            document.getElementById("lon").textContent = data.longitude;
            document.getElementById("battery").textContent = data.battery;
            document.getElementById("temp").textContent = data.temperature;
            document.getElementById("ph").textContent = data.ph;
            document.getElementById("turbidity").textContent = data.turbidity;
            document.getElementById("tds").textContent = data.tds;
            document.getElementById("mode").textContent = data.mode;

            boatMarker.setLatLng([data.latitude, data.longitude]);
            map.setView([data.latitude, data.longitude]);
        });
}

updateTelemetry();
setInterval(updateTelemetry, 1000);
