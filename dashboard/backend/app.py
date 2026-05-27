from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/api/status")
def status():
    return {"status": "dashboard backend running"}

@app.route("/api/telemetry")
def telemetry():
    return {
        "latitude": 25.7617,
        "longitude": -80.1918,
        "battery": 11.8,
        "temperature": 27.4,
        "ph": 7.1,
        "turbidity": 320,
        "tds": 510,
        "mode": "AUTO"
    }

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
