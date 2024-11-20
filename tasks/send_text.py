from celery import shared_task
import requests
from logs import logger
from navyojan import settings

@shared_task(name='send_text_task')
def send_text_task(phone_number, message):
    logger.info(f"Sending WhatsApp message to: {phone_number} with message: {message}")
    try:
        response = requests.post(
            'https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/bulk/',
            headers={
                'Content-Type': 'application/json',
                'authkey': settings.MSG_AUTH  # Add your auth key here
            },
            json={  # Changed from 'data' to 'json' for JSON payload
                "integrated_number": phone_number,
                "content_type": "template",
                "payload": {
                    "messaging_product": "whatsapp",
                    "type": "template",
                    "template": {
                        "name": "navyojan2",
                        "language": {
                            "code": "en",
                            "policy": "deterministic"
                        },
                        "namespace": "6ba15e80_075c_4999_a702_54f825d6ccbb",
                        "to_and_components": [
                            {
                                "to": [phone_number],  # Use the phone_number parameter
                                "components": {
                                    "body_1": {
                                        "type": "text",
                                        "value": message  # Use the message parameter
                                    },
                                    "body_2": {
                                        "type": "text",
                                        "value": "123"  # Example static value
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )
        if response.status_code == 200:
            logger.info(f"WhatsApp message sent to: {phone_number}")
        else:
            logger.debug(f"Failed to send WhatsApp message to: {phone_number}, Status code: {response.status_code}")
    except Exception as e:
        logger.debug(f"Error: {e}")
