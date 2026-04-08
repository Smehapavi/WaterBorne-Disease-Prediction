from flask import Flask

app = Flask(__name__)

# global variable
latest_data = "D:0 C:0 T:0"

@app.route("/data")
def send_data():
    return latest_data

@app.route("/update/<d>/<c>/<t>")
def update(d, c, t):
    global latest_data
    latest_data = f"D:{d} C:{c} T:{t}"
    return "updated"

app.run(host="0.0.0.0", port=5000)