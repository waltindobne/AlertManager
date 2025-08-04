from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQA0K--77E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Ux9ali6zwUOVumGyMkXtmJ-MNITJfoiAbjW_SwlOMSg"

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    try:
        alert_info = data['alerts'][0]
        alert_name = alert_info['labels'].get('alertname', 'Sem nome')
        instance = alert_info['labels'].get('instance', 'Desconhecida')
        severity = alert_info['labels'].get('severity', 'N/A')
        description = alert_info.get('annotations', {}).get('description') or \
                      alert_info.get('annotations', {}).get('summary', 'Sem descrição')

        status = data.get('status', 'unknown').upper()

        starts_at = alert_info.get('startsAt')
        starts_at_fmt = datetime.fromisoformat(starts_at.replace("Z", "+00:00")).strftime('%d/%m/%Y %H:%M:%S') if starts_at else "N/A"

        message = (
            f"🚨 *Alerta* *{status}*\n"
            f"• *Nome:* {alert_name}\n"
            f"• *Instância:* {instance}\n"
            f"• *Severidade:* {severity}\n"
            f"• *Início:* {starts_at_fmt}\n"
            f"• *Descrição:* {description}"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    payload = {"text": message}

    response = requests.post(WEBHOOK_URL, json=payload)

    print(f"Enviando mensagem formatada:\n{message}")
    print(f"Resposta Google Chat: {response.status_code} - {response.text}")

    if response.status_code != 200:
        return jsonify({'message': message, 'error': response.text}), 500

    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
