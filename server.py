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
        "name": data.get('name', ''),
                
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


all_messages = []
# Pidetään kirjaa varatuista nimistä
registered_users = set()

@app.route('/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if not username:
        return jsonify(False)
    # Palauttaa True, jos nimi ei ole vielä käytössä
    return jsonify(username.lower() not in registered_users)

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    if not data:
        return jsonify({"error": "Data puuttuu"}), 400
    
    # Kun joku lähettää viestin, varataan hänen nimensä järjestelmään
    if data.get('senderName'):
        registered_users.add(data.get('senderName').lower())

    # Tallennetaan koko viesti (sisältää senderName, recipientName, message jne.)
    all_messages.append(data)
    print(f"Viesti lähetetty: {data.get('senderName')} -> {data.get('recipientName')}")
    return jsonify({"ok": True}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    # Puhelin kysyy viestejä omalla nimellään
    my_name = request.args.get('username')
    
    if not my_name:
        return jsonify([])

    my_name_lower = my_name.lower()
    my_messages = []

    for m in all_messages:
        # 1. Tarkistetaan onko kyseessä suora yksityisviesti
        recipient = m.get('recipientName')
        if recipient and recipient.lower() == my_name_lower:
            my_messages.append(m)
            continue # Viesti lisätty, siirrytään seuraavaan
            
        # 2. Tarkistetaan onko kyseessä ryhmäviesti (oma nimi löytyy listalta)
        recipients_list = m.get('recipientsNames')
        if recipients_list and isinstance(recipients_list, list):
            # any() tarkistaa löytyykö listalta yhtään nimeä, joka täsmää
            if any(name.lower() == my_name_lower for name in recipients_list):
                my_messages.append(m)

    return jsonify(my_messages)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

