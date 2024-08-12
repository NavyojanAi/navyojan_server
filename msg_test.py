import requests

def send_otp_via_msg91(phone_number, otp):
    url = "https://api.msg91.com/api/v5/sms"
    payload = {
        "authkey": "426108Au0XEwhq668fc04cP1",
        "template_id": "668fc0f0d6fc0512cd4429f2",
        "mobile": phone_number,
        "otp": otp,
        "message": f"Your OTP is {otp}",  # Replace with the appropriate template or message
        "sender": "123456",  # Replace with your sender ID
        "route": "4",
        "country": "91",
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("OTP sent successfully.")
    else:
        print(f"Failed to send OTP. Status code: {response.status_code}, Response: {response.content}")

# Usage
phone_number = "8226890212"
otp = "1234"
send_otp_via_msg91(phone_number, otp)
