# Notification microservice (REST)

This small Flask microservice provides REST endpoints to register mobile devices and send notifications to devices without using Firebase.

Endpoints
- `POST /register_device` — register a device with JSON: `{ "user_id": "123", "device_id": "dev-1", "callback_url": "http://<device>:6001/mobile_callback" }`
- `POST /send_notification` — send a notification: `{ "user_id": "123", "title": "Hi", "body": "Hello", "data": {}}`
- `GET /notifications?user_id=123` — list stored notifications for a user

Run locally

1. Create a virtualenv and install requirements:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the example mobile callback (on the device or simulator):

```bash
python example_mobile_callback.py
```

3. Run the microservice:

```bash
set NOTIF_DB=sqlite:///notification_service.db
python app.py
```

4. Example usage (register device):

```bash
curl -X POST http://localhost:5001/register_device -H "Content-Type: application/json" -d "{\"user_id\":\"123\",\"device_id\":\"dev-1\",\"callback_url\":\"http://<device-host>:6001/mobile_callback\"}"
```

5. Send a notification:

```bash
curl -X POST http://localhost:5001/send_notification -H "Content-Type: application/json" -d "{\"user_id\":\"123\",\"title\":\"Alert\",\"body\":\"Motion detected\"}"
```

Notes
- The mobile app must expose an HTTP endpoint (callback URL) reachable from the microservice.
- This approach uses plain REST POST requests to deliver notifications to devices.
