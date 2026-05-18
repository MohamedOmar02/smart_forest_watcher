"""
Celery async tasks for the camera_management app.

Triggered from api.py after a new Detection is saved:
  send_camera_alert.delay(detection_id)

Responsibilities:
  1. Push a WebSocket event to the 'camera_alerts' channel group
     → all connected browsers receive the notification instantly.
  2. Send an email to the Supervisor AND the assigned Client.
"""

import json
from celery          import shared_task
from asgiref.sync    import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
import os
import logging
import requests

CAMERA_GROUP = "camera_alerts"
logger = logging.getLogger(__name__)


@shared_task(name="send_camera_alert")
def send_camera_alert(detection_id: int):
    # ── 1. Load detection ────────────────────────────────────────────────────
    from camera_management.models import Detection   # late import avoids circular
    try:
        detection = Detection.objects.select_related(
            'camera__parcelle__project__client'
        ).get(pk=detection_id)
    except Detection.DoesNotExist:
        return

    camera  = detection.camera
    project = camera.parcelle.project
    client  = project.client

    # ── 2. WebSocket push ────────────────────────────────────────────────────
    payload = json.dumps({
        "type":         "camera_alert",
        "camera_id":    camera.camera_id,
        "camera_name":  camera.name,
        "parcelle":     camera.parcelle.name,
        "project":      project.name,
        "confidence":   detection.confidence_score,
        "image_url":    detection.image.url,
        "detected_at":  detection.detected_at.isoformat(),
    })

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        CAMERA_GROUP,
        {"type": "camera_message", "text": payload}
    )

    # ── 3. Email alert ───────────────────────────────────────────────────────
    subject  = f"🔥 Fire Detected — {camera.name} ({project.name})"
    message  = (
        f"Fire was detected by camera '{camera.name}' "
        f"in parcelle '{camera.parcelle.name}', project '{project.name}'.\n\n"
        f"Confidence: {detection.confidence_score * 100:.1f}%\n"
        f"Detected at: {detection.detected_at:%Y-%m-%d %H:%M UTC}\n\n"
        f"Please check the dashboard immediately."
    )

    recipients = []
    notification_targets = []

    # Always email the supervisor (Django superusers)
    from django.contrib.auth.models import User
    supervisors = User.objects.filter(is_superuser=True).values('username', 'email')
    for supervisor in supervisors:
        if supervisor['email']:
            recipients.append(supervisor['email'])
            notification_targets.append(supervisor['email'])

    # Also email the assigned client
    if client and client.email:
        recipients.append(client.email)
        notification_targets.append(client.email)

    if recipients:
        send_mail(
            subject,
            message,
            'smartforgreen-alerts@gmail.com',
            recipients,
            fail_silently=True,
        )

    # ── 4. Push to Notification microservice (REST) ─────────────────────────
    NOTIF_URL = os.environ.get('NOTIF_SERVICE_URL', 'http://localhost:5001/send_notification')

    # Determine detected types from bounding_boxes if labelled by the AI pipeline
    detected_types = set()
    boxes = detection.bounding_boxes or []
    for b in boxes:
        if isinstance(b, dict):
            lbl = b.get('label') or b.get('class') or b.get('type')
            if lbl:
                detected_types.add(str(lbl).lower())

    # Fallback: if no labelled boxes, assume this is a fire detection
    if not detected_types:
        detected_types.add('fire')

    title = f"Alert: {' & '.join(t.title() for t in detected_types)} detected"
    body = (
        f"Detected by camera '{camera.name}' in parcelle '{camera.parcelle.name}', project '{project.name}'.\n\n"
        f"Types: {', '.join(sorted(detected_types))}\n"
        f"Confidence: {detection.confidence_score * 100:.1f}%\n"
        f"Detected at: {detection.detected_at:%Y-%m-%d %H:%M UTC}\n"
        f"Image: {detection.image.url}\n"
    )

    data = {
        'camera_id': camera.camera_id,
        'camera_name': camera.name,
        'parcelle': camera.parcelle.name,
        'project': project.name,
        'confidence': detection.confidence_score,
        'detected_at': detection.detected_at.isoformat(),
        'image_url': detection.image.url,
        'bounding_boxes': boxes,
    }

    if notification_targets:
        for user_identifier in set(notification_targets):
            try:
                resp = requests.post(NOTIF_URL, json={
                    'user_id': user_identifier,
                    'title': title,
                    'body': body,
                    'data': data,
                }, timeout=5)
                if not resp.ok:
                    logger.warning('Notification service returned %s for user %s', resp.status_code, user_identifier)
            except Exception as exc:
                logger.exception('Failed to send notification to service for user %s: %s', user_identifier, exc)
