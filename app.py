from flask import Flask, request
import requests

app = Flask(__name__)

WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQA0K--77E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=CKykf6Cstty3Wq9uvtYEC5oyhOLjRE6Sa5aAnTIXMjg"

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    try:
        alert_name = data['alerts'][0]['labels']['alertname']
        status = data['status']
        message = f"🚨 Alerta {status.upper()}: {alert_name}"
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    payload = {"text": message}

    response = requests.post(WEBHOOK_URL, json=payload)

    # DEBUG prints
    print(f"Enviando mensagem: {message}")
    print(f"Resposta Google Chat: {response.status_code} - {response.text}")

    if response.status_code != 200:
        return jsonify({'message': message, 'error': response.text}), 500

    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
