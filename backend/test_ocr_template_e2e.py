#!/usr/bin/env python3
"""
End-to-end OCR/template verification flow test.

Flow:
1) Health check
2) Register college user
3) Login
4) Upload template
5) List templates
6) OCR verify a certificate against uploaded template

Usage:
  python test_ocr_template_e2e.py

Optional env vars:
  BASE_URL=http://localhost:5000
"""

import io
import os
import sys
import uuid
import json
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def tiny_png_bytes() -> bytes:
    """Return a tiny valid PNG image byte stream."""
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def print_step(name: str, ok: bool, detail: str = ""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {name}")
    if detail:
        print(f"   {detail}")


def main() -> int:
    print("Running OCR/Template E2E test")
    print("=" * 72)

    session = requests.Session()

    # 1) Health check
    try:
        r = session.get(f"{BASE_URL}/api/health", timeout=15)
        ok = r.status_code == 200
        print_step("Health check", ok, f"status={r.status_code}")
        if not ok:
            return 1
    except Exception as exc:
        print_step("Health check", False, str(exc))
        return 1

    # 2) Register college user
    suffix = uuid.uuid4().hex[:8]
    username = f"college_e2e_{suffix}"
    email = f"college_e2e_{suffix}@example.com"
    password = "Pass@12345"

    register_payload = {
        "username": username,
        "email": email,
        "password": password,
        "first_name": "College",
        "last_name": "E2E",
        "role": "college",
    }

    try:
        r = session.post(f"{BASE_URL}/api/auth/register", json=register_payload, timeout=20)
        ok = r.status_code in (200, 201)
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("Register college user", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:500])
            return 1
    except Exception as exc:
        print_step("Register college user", False, str(exc))
        return 1

    # 3) Auto-verify email in development
    try:
        r = session.post(
            f"{BASE_URL}/api/dev/get-verification-token",
            json={"email": email},
            timeout=20,
        )
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("Fetch verification token (dev)", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:500])
            return 1

        token = body.get("token")
        if not token:
            print_step("Verification token present", False, "token missing in dev response")
            return 1
        print_step("Verification token present", True)

        r = session.get(f"{BASE_URL}/api/auth/verify-email", params={"token": token}, timeout=20)
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("Verify email", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:500])
            return 1
    except Exception as exc:
        print_step("Email verification (dev)", False, str(exc))
        return 1

    # 4) Login
    try:
        r = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username_or_email": email, "password": password},
            timeout=20,
        )
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("Login", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:500])
            return 1

        token = body.get("tokens", {}).get("access_token")
        user = body.get("user", {})
        user_id = user.get("id")
        if not token or not user_id:
            print_step("Extract auth token/user id", False, "missing token or user id in login response")
            return 1
        print_step("Extract auth token/user id", True, f"user_id={user_id}")
    except Exception as exc:
        print_step("Login", False, str(exc))
        return 1

    headers = {"Authorization": f"Bearer {token}"}

    # 5) Upload template
    template_file = tiny_png_bytes()
    files = {"template_file": ("template.png", io.BytesIO(template_file), "image/png")}
    data = {
        "template_name": "E2E Degree Template",
        "template_type": "degree",
        "organization_id": user_id,
        "organization_name": "E2E College",
        "organization_type": "college",
        "required_fields": "[]",
        "optional_fields": "[]",
    }

    try:
        r = session.post(
            f"{BASE_URL}/api/templates/templates/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=60,
        )
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("Template upload", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:800])
            print("   hint: ensure IPFS daemon and Tesseract are installed/running")
            return 1

        template_id = body.get("data", {}).get("template_id")
        print_step("Template created", bool(template_id), f"template_id={template_id}")
    except Exception as exc:
        print_step("Template upload", False, str(exc))
        return 1

    # 6) List templates
    try:
        r = session.get(
            f"{BASE_URL}/api/templates/templates/organization/{user_id}",
            headers=headers,
            timeout=30,
        )
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("List templates", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:500])
            return 1

        templates = body.get("data", {}).get("templates", [])
        print_step("Template found in list", len(templates) > 0, f"count={len(templates)}")
        if not templates:
            return 1
    except Exception as exc:
        print_step("List templates", False, str(exc))
        return 1

    # 7) OCR verify
    files = {"credential_file": ("certificate.png", io.BytesIO(template_file), "image/png")}
    data = {
        "organization_id": user_id,
        "template_type": "degree",
    }

    try:
        r = session.post(
            f"{BASE_URL}/api/ocr/verify-credential-ocr",
            headers=headers,
            files=files,
            data=data,
            timeout=60,
        )
        ok = r.status_code == 200
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        print_step("OCR verify", ok, f"status={r.status_code}")
        if not ok:
            print("   response:", json.dumps(body, indent=2)[:800])
            return 1

        score = body.get("data", {}).get("confidence_score")
        status = body.get("data", {}).get("verification_status")
        print_step("Verification result", True, f"status={status}, confidence={score}")
    except Exception as exc:
        print_step("OCR verify", False, str(exc))
        return 1

    print("=" * 72)
    print("✅ E2E flow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
