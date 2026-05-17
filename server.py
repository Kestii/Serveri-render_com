from flask import Flask, request, jsonify

app = Flask(__name__)

locations = {}
phone_infos = {}

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


@app.route('/phoneInfo', methods=['POST'])
def update_phone_info():
    data = request.json
    if not data:
        return jsonify({"virhe": "data puuttuu"}), 400

    laite_id = data.get('id')
    if not laite_id:
        return jsonify({"virhe": "id puuttuu"}), 400

    # Validoidaan alirakenteet
    battery = data.get('batteryInfo', {})
    
    phone_infos[laite_id] = {
        "id": laite_id,
        
        # List<AppUsage>
        "dailyUsage": [
            {
                "packageName": u.get('packageName'),
                "totalTimeMs": u.get('totalTimeMs'),
                "totalTimeMinutes": u.get('totalTimeMinutes'),
                "lastTimeUsed": u.get('lastTimeUsed')
            }
            for u in data.get('dailyUsage', [])
        ],
        
        # List<AppLaunch>
        "launchCounts": [
            {
                "packageName": l.get('packageName'),
                "numberOfLaunch": l.get('numberOfLaunch')
            }
            for l in data.get('launchCounts', [])
        ],
        
        # List<AppSession>
        "usageSessions": [
            {
                "packageName": s.get('packageName'),
                "startTime": s.get('startTime'),
                "endTime": s.get('endTime'),
                "durationMs": s.get('durationMs'),
                "hourOfDay": s.get('hourOfDay')
            }
            for s in data.get('usageSessions', [])
        ],
        
        # BatteryInfo
        "batteryInfo": {
            "level": battery.get('level'),
            "isCharging": battery.get('isCharging'),
            "chargingMethod": battery.get('chargingMethod'),
            "health": battery.get('health'),
            "temperature": battery.get('temperature')
        },
        
        "collectedAt": data.get('collectedAt')
    }

    return jsonify({"ok": True})


@app.route('/phoneInfo', methods=['GET'])
def get_phone_info():
    # Palauttaa List<PhoneInformation> — täsmää Android:n return tyyppiä
    return jsonify(list(phone_infos.values()))


@app.route('/phoneInfo/<laite_id>', methods=['GET'])
def get_phone_info_yksi(laite_id):
    if laite_id not in phone_infos:
        return jsonify({"virhe": "laitetta ei löydy"}), 404
    return jsonify(phone_infos[laite_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)