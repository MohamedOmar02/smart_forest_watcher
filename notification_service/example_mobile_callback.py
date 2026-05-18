"""
Simple example mobile callback that a mobile app could run to receive notifications.
Run this on the mobile device (or a simulator) and register its URL with the microservice.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route('/mobile_callback', methods=['POST'])
def mobile_callback():
    payload = request.get_json() or {}
    print('Received notification:', payload)
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
