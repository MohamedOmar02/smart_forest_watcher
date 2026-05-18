"""
Developer helper to send one test fire detection through the existing camera
upload API, so the normal alert pipeline can run:

upload API -> Detection saved -> Celery alert worker -> notification service

Example:
    python camera_management/dev_send_test_detection.py ^
      --camera-id CAM-001 ^
      --api-key my-secret ^
      --server-url http://127.0.0.1:8000/camera_management/api/upload/ ^
      --image img/detections/alert.jpg
"""

import argparse
import json
from pathlib import Path

import requests


DEFAULT_IMAGE = Path("img/detections/alert.jpg")
DEFAULT_SERVER_URL = "http://127.0.0.1:8000/camera_management/api/upload/"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Send a sample fire detection image through the camera upload API."
    )
    parser.add_argument("--camera-id", required=True, help="Camera.camera_id value")
    parser.add_argument("--api-key", required=True, help="Camera.api_key value")
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help=f"Upload endpoint URL. Default: {DEFAULT_SERVER_URL}",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help=f"Path to the test image. Default: {DEFAULT_IMAGE}",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.97,
        help="Detection confidence to send. Default: 0.97",
    )
    parser.add_argument(
        "--label",
        default="fire",
        help="Label stored in bounding_boxes and used by the alert worker. Default: fire",
    )
    return parser


def main():
    args = build_parser().parse_args()
    image_path = args.image

    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    bounding_boxes = [
        {
            "x1": 48,
            "y1": 36,
            "x2": 302,
            "y2": 228,
            "confidence": args.confidence,
            "label": args.label,
        }
    ]

    with image_path.open("rb") as image_file:
        response = requests.post(
            args.server_url,
            data={
                "camera_id": args.camera_id,
                "api_key": args.api_key,
                "confidence": str(args.confidence),
                "bounding_boxes": json.dumps(bounding_boxes),
            },
            files={"image": (image_path.name, image_file, "image/jpeg")},
            timeout=30,
        )

    print(f"Status: {response.status_code}")
    print(response.text)

    if not response.ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
