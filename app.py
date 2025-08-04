from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQA0K--77E/messages?key=CHAVE_AQUI&token=TOKEN_AQUI"

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    try:
        alert_info = data['alerts'][0]
        alert_name = alert_info['labels'].get('alertname', 'Sem nome')
        instance = alert_info['labels'].get('instance', 'Desconhecida')
        severity = alert_info['labels'].get('severity', 'N/A')
        description = alert_info.get('annotations', {}).get('description', 'Sem descrição')

        status = data.get('status', 'unknown').upper()

        starts_at = alert_info.get('startsAt')
        starts_at_fmt = datetime.fromisoformat(starts_at.replace("Z", "+00:00")).strftime('%d/%m/%Y %H:%M:%S') if starts_at else "N/A"

        # Define cor da borda de acordo com severidade
        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#1E90FF"
        }
        border_color = color_map.get(severity.lower(), "#808080")

        payload = {
            "cardsV2": [
                {
                    "cardId": "alert-card",
                    "card": {
                        "header": {
                            "title": f"🚨 Alerta {status}",
                            "subtitle": f"{alert_name} - {severity.upper()}",
                            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Alert_icon.svg",
                            "imageType": "CIRCLE",
                            "imageAltText": "Ícone de alerta"
                        },
                        "sections": [
                            {
                                "header": "Detalhes do Alerta",
                                "collapsible": True,
                                "uncollapsibleWidgetsCount": 1,
                                "widgets": [
                                    {
                                        "decoratedText": {
                                            "startIcon": {"knownIcon": "PERSON"},
                                            "text": f"<b>Instância:</b> {instance}"
                                        }
                                    },
                                    {
                                        "decoratedText": {
                                            "startIcon": {"knownIcon": "TIMER"},
                                            "text": f"<b>Início:</b> {starts_at_fmt}"
                                        }
                                    },
                                    {
                                        "decoratedText": {
                                            "startIcon": {"knownIcon": "DESCRIPTION"},
                                            "text": f"<b>Descrição:</b> {description}"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    response = requests.post(WEBHOOK_URL, json=payload)

    print(f"Resposta Google Chat: {response.status_code} - {response.text}")

    if response.status_code != 200:
        return jsonify({'error': response.text}), 500

    return jsonify({'status': 'sent'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
