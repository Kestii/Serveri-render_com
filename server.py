from flask import Flask, request, jsonify

app = Flask(__name__)
latest_location = {}

@app.route('/sijainti', methods=['POST'])
def vastaanota():
    latest_location.update(request.json)
    return jsonify({"ok": True})

@app.route('/sijainti', methods=['GET'])
def laheta():
    return jsonify(latest_location)