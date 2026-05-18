import json
import os
import sqlite3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), 'notification_service.db')
DB_PATH = os.environ.get('NOTIF_DB', DEFAULT_DB_PATH)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            callback_url TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            body TEXT,
            data TEXT,
            sent INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
    conn.commit()
    conn.close()

@app.before_first_request
def create_tables():
    init_db()

@app.route('/register_device', methods=['POST'])
def register_device():
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    device_id = payload.get('device_id')
    callback_url = payload.get('callback_url')
    if not (user_id and device_id):
        return jsonify({'error': 'user_id and device_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM devices WHERE user_id = ? AND device_id = ?',
        (user_id, device_id),
    )
    row = cursor.fetchone()

    if row:
        if callback_url is not None:
            cursor.execute(
                'UPDATE devices SET callback_url = ? WHERE id = ?',
                (callback_url, row['id']),
            )
    else:
        cursor.execute(
            'INSERT INTO devices (user_id, device_id, callback_url) VALUES (?, ?, ?)',
            (user_id, device_id, callback_url),
        )

    conn.commit()
    conn.close()
    return jsonify({'status': 'registered', 'user_id': user_id, 'device_id': device_id})

@app.route('/send_notification', methods=['POST'])
def send_notification():
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    title = payload.get('title')
    body = payload.get('body')
    extra = payload.get('data', {})
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notifications (user_id, title, body, data, sent) VALUES (?, ?, ?, ?, ?)',
        (user_id, title, body, json.dumps(extra), 0),
    )
    notification_id = cursor.lastrowid
    conn.commit()

    cursor.execute('SELECT device_id, callback_url FROM devices WHERE user_id = ?', (user_id,))
    devices = cursor.fetchall()
    deliveries = []
    sent_ok = False

    for d in devices:
        callback_url = d['callback_url']
        if not callback_url:
            deliveries.append({'device_id': d['device_id'], 'status': 'registered-polling-only'})
            continue
        try:
            resp = requests.post(callback_url, json={'title': title, 'body': body, 'data': extra}, timeout=5)
            deliveries.append({'device_id': d['device_id'], 'status_code': resp.status_code})
            if resp.ok:
                sent_ok = True
        except Exception as exc:
            deliveries.append({'device_id': d['device_id'], 'error': str(exc)})

    if sent_ok:
        cursor.execute('UPDATE notifications SET sent = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()
    return jsonify({'notification_id': notification_id, 'deliveries': deliveries})

@app.route('/notifications', methods=['GET'])
def list_notifications():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id query param required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, body, data, sent FROM notifications WHERE user_id = ? ORDER BY id DESC',
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    out = []
    for n in rows:
        try:
            data = json.loads(n['data']) if n['data'] else {}
        except Exception:
            data = n['data']
        out.append({
            'id': n['id'],
            'title': n['title'],
            'body': n['body'],
            'data': data,
            'sent': bool(n['sent']),
        })
    return jsonify({'notifications': out})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
