from flask import Flask, request, jsonify

app = Flask(__name__)

locations = {}

@app.route('/sijainti', methods=['POST'])
def vastaanota():
    data = request.json

    laite_id = data.get('id')
    if not laite_id:
        return jsonify({"virhe": "id puuttuu"}), 400

    locations[laite_id] = {
        "id": laite_id,
        "name": data.get('name', ''),
        "lat": data.get('lat'),
        "lng": data.get('lng'),
        "timestamp": data.get('timestamp')
    }
    return jsonify({"ok": True})

@app.route('/sijainti', methods=['GET'])
def laheta():
    # Palauttaa listan kaikista laitteista (lista sopii Android:lle paremmin kuin dict)
    return jsonify(list(locations.values()))

@app.route('/sijainti/<laite_id>', methods=['GET'])
def laheta_yksi(laite_id):
    if laite_id not in locations:
        return jsonify({"virhe": "laitetta ei löydy"}), 404
    return jsonify(locations[laite_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)