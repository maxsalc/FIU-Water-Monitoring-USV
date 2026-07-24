const startPosition = [25.7617, -80.1918];

const map = L.map("map", { zoomControl: false }).setView(startPosition, 15);

L.control.zoom({ position: "bottomright" }).addTo(map);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

const vehicleIcon = L.divIcon({
    className: "vehicle-marker",
    html: "<span>⌁</span>",
    iconSize: [40, 40],
    iconAnchor: [20, 20]
});

const boatMarker = L.marker(startPosition, {
    icon: vehicleIcon
}).addTo(map).bindTooltip("USV POSITION", {
    direction: "top",
    offset: [0, -18]
});

const route = L.polyline([], {
    color: "#d7ff62",
    weight: 3,
    dashArray: "7 8"
}).addTo(map);

let waypoints = [];
let addingWaypoint = false;

const $ = id => document.getElementById(id);

const setText = (id, value) => {
    $(id).textContent = value ?? "--";
};

const fmt = (value, digits = 4) => Number(value).toFixed(digits);

function renderWaypoints() {
    $("waypoint-count").textContent = waypoints.length;

    $("waypoint-list").innerHTML = waypoints.map((point, index) => `
        <li>
            <span class="waypoint-number">${String(index + 1).padStart(2, "0")}</span>
            <span class="mono">${fmt(point.lat)}, ${fmt(point.lng)}</span>
            <button class="remove-waypoint" data-index="${index}" aria-label="Remove waypoint">×</button>
        </li>
    `).join("");

    route.setLatLngs([
        boatMarker.getLatLng(),
        ...waypoints
    ]);

    $("waypoint-helper").textContent = waypoints.length
        ? "Route ready. Reorder or clear points before launch."
        : "Click “Add waypoint,” then select points on the map.";
}

$("waypoint-mode").addEventListener("click", () => {
    addingWaypoint = !addingWaypoint;

    $("waypoint-mode").classList.toggle("active", addingWaypoint);
    map.getContainer().classList.toggle("placing", addingWaypoint);
});

$("clear-route").addEventListener("click", () => {
    waypoints = [];
    renderWaypoints();
});

$("waypoint-list").addEventListener("click", event => {
    const button = event.target.closest(".remove-waypoint");

    if (button) {
        waypoints.splice(Number(button.dataset.index), 1);
        renderWaypoints();
    }
});

map.on("click", event => {
    if (!addingWaypoint) return;

    waypoints.push(event.latlng);
    renderWaypoints();
});

$("start-mission").addEventListener("click", () => {
    $("mode").textContent = waypoints.length
        ? "MISSION ACTIVE"
        : "NO ROUTE";
});

$("pause-mission").addEventListener("click", () => {
    $("mode").textContent = "PAUSED";
});

async function updateTelemetry() {
    try {
        const [statusResponse, telemetryResponse] = await Promise.all([
            fetch("/api/status"),
            fetch("/api/telemetry")
        ]);

        const status = await statusResponse.json();
        const data = await telemetryResponse.json();

        setText("status", status.status || "Vehicle connected");

        setText("lat", fmt(data.latitude));
        setText("lon", fmt(data.longitude));

        setText(
            "coordinates",
            `LAT ${fmt(data.latitude)} / LON ${fmt(data.longitude)}`
        );

        setText("battery", data.battery);
        setText("temp", data.temperature);
        setText("ph", data.ph);
        setText("turbidity", data.turbidity);
        setText("tds", data.tds);
        setText("mode", data.mode);

        const batteryPercent = Math.max(
            0,
            Math.min(100, ((Number(data.battery) - 10.5) / 2.1) * 100)
        );

        $("battery-bar").style.width = `${batteryPercent}%`;

        const nextPosition = [
            data.latitude,
            data.longitude
        ];

        boatMarker.setLatLng(nextPosition);

        route.setLatLngs([
            nextPosition,
            ...waypoints
        ]);

        if (!map.getContainer().matches(":hover")) {
            map.panTo(nextPosition, {
                animate: true,
                duration: 0.5
            });
        }

        $("last-updated").textContent = new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

    } catch (error) {
        $("status").textContent = "Vehicle offline — retrying";
    }
}

$("mission-date").textContent = new Date()
    .toLocaleDateString([], {
        month: "short",
        day: "2-digit",
        year: "numeric"
    })
    .toUpperCase();

$("refresh-button").addEventListener("click", updateTelemetry);

updateTelemetry();

setInterval(updateTelemetry, 1000);
