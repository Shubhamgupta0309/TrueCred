#!/usr/bin/env python3
"""
Real-account end-to-end OCR/template flow test.

This script does not modify database logic or user data beyond creating a template
through the existing API. It uses an existing verified account.

Required environment variables:
  TEST_EMAIL
  TEST_PASSWORD

Optional environment variables:
  BASE_URL=http://localhost:5000
  TEST_ROLE=college
  TEST_ORGANIZATION_ID=<defaults to logged in user id>
  TEST_ORGANIZATION_NAME=<defaults to logged in username>
  TEST_ORGANIZATION_TYPE=<defaults to logged in role>
"""

import io
import json
import os
import sys
import uuid

import requests
from PIL import Image, ImageDraw, ImageFont

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
TEST_ROLE = os.getenv("TEST_ROLE", "college")


def print_step(name: str, ok: bool, detail: str = ""):
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}")
    if detail:
        print(f"       {detail}")


def make_certificate_image_bytes() -> bytes:
    image = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    lines = [
        "TRUECRED TEST CERTIFICATE",
        "This certifies that",
        "SHUBHAM GUPTA",
        "has successfully completed",
        "Bachelor of Technology",
        "Awarded on: 13 March 2026",
        "Certificate No: TC-E2E-001",
    ]

    y = 120
    for line in lines:
        draw.text((140, y), line, fill="black", font=font)
        y += 90

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def require_env() -> bool:
    missing = []
    if not TEST_EMAIL:
        missing.append("TEST_EMAIL")
    if not TEST_PASSWORD:
        missing.append("TEST_PASSWORD")
    if missing:
        print_step("Environment configuration", False, f"Missing: {', '.join(missing)}")
        return False
    print_step("Environment configuration", True, f"email={TEST_EMAIL}, role={TEST_ROLE}")
    return True


def main() -> int:
    print("Running real-account OCR/template E2E test")
    print("=" * 72)

    if not require_env():
        return 1

    session = requests.Session()

    try:
        response = session.get(f"{BASE_URL}/api/health", timeout=15)
        ok = response.status_code == 200
        print_step("Health check", ok, f"status={response.status_code}")
        if not ok:
            return 1
    except Exception as exc:
        print_step("Health check", False, str(exc))
        return 1

    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username_or_email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=20,
        )
        ok = response.status_code == 200
        body = response.json() if "application/json" in response.headers.get("content-type", "") else {"raw": response.text}
        print_step("Login", ok, f"status={response.status_code}")
        if not ok:
            print(json.dumps(body, indent=2)[:1000])
            return 1

        token = body.get("tokens", {}).get("access_token")
        user = body.get("user", {})
        user_id = user.get("id")
        username = user.get("username")
        role = user.get("role")
        email_verified = user.get("email_verified", user.get("is_email_verified"))

        ok = bool(token and user_id)
        print_step("Extract auth context", ok, f"user_id={user_id}, username={username}, role={role}, email_verified={email_verified}")
        if not ok:
            return 1
    except Exception as exc:
        print_step("Login", False, str(exc))
        return 1

    if role != TEST_ROLE:
        print_step("Role check", False, f"expected={TEST_ROLE}, actual={role}")
        return 1
    print_step("Role check", True, role)

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = session.get(f"{BASE_URL}/api/auth/profile", headers=headers, timeout=20)
        ok = response.status_code == 200
        print_step("Authenticated profile fetch", ok, f"status={response.status_code}")
        if not ok:
            return 1
    except Exception as exc:
        print_step("Authenticated profile fetch", False, str(exc))
        return 1

    organization_id = os.getenv("TEST_ORGANIZATION_ID", user_id)
    organization_name = os.getenv("TEST_ORGANIZATION_NAME", username or "Test Organization")
    organization_type = os.getenv("TEST_ORGANIZATION_TYPE", role)

    cert_bytes = make_certificate_image_bytes()
    unique_name = f"E2E Template {uuid.uuid4().hex[:8]}"

    try:
        files = {"template_file": ("template.png", io.BytesIO(cert_bytes), "image/png")}
        data = {
            "template_name": unique_name,
            "template_type": "degree",
            "organization_id": organization_id,
            "organization_name": organization_name,
            "organization_type": organization_type,
            "required_fields": "[]",
            "optional_fields": "[]",
        }
        response = session.post(
            f"{BASE_URL}/api/templates/templates/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=90,
        )
        body = response.json() if "application/json" in response.headers.get("content-type", "") else {"raw": response.text}
        ok = response.status_code == 200
        print_step("Template upload", ok, f"status={response.status_code}")
        if not ok:
            print(json.dumps(body, indent=2)[:1500])
            return 1
        template_id = body.get("data", {}).get("template_id")
        print_step("Template created", bool(template_id), f"template_id={template_id}")
        if not template_id:
            return 1
    except Exception as exc:
        print_step("Template upload", False, str(exc))
        return 1

    try:
        response = session.get(
            f"{BASE_URL}/api/templates/templates/organization/{organization_id}",
            headers=headers,
            timeout=30,
        )
        body = response.json() if "application/json" in response.headers.get("content-type", "") else {"raw": response.text}
        ok = response.status_code == 200
        print_step("Template list", ok, f"status={response.status_code}")
        if not ok:
            print(json.dumps(body, indent=2)[:1000])
            return 1
        templates = body.get("data", {}).get("templates", [])
        matched = any(item.get("id") == template_id for item in templates)
        print_step("Uploaded template visible", matched, f"count={len(templates)}")
        if not matched:
            return 1
    except Exception as exc:
        print_step("Template list", False, str(exc))
        return 1

    try:
        files = {"credential_file": ("certificate.png", io.BytesIO(cert_bytes), "image/png")}
        data = {"organization_id": organization_id, "template_type": "degree"}
        response = session.post(
            f"{BASE_URL}/api/ocr/verify-credential-ocr",
            headers=headers,
            files=files,
            data=data,
            timeout=90,
        )
        body = response.json() if "application/json" in response.headers.get("content-type", "") else {"raw": response.text}
        ok = response.status_code == 200
        print_step("OCR verification", ok, f"status={response.status_code}")
        if not ok:
            print(json.dumps(body, indent=2)[:1500])
            return 1
        status = body.get("data", {}).get("verification_status")
        score = body.get("data", {}).get("confidence_score")
        print_step("Verification result", status is not None, f"status={status}, confidence={score}")
    except Exception as exc:
        print_step("OCR verification", False, str(exc))
        return 1

    print("=" * 72)
    print("PASS: Real-account OCR/template E2E completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
