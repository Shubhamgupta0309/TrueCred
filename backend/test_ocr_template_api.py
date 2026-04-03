#!/usr/bin/env python3
"""
Smoke tests for OCR/template API route registration and auth guard behavior.
These tests intentionally run without auth and expect 401 (not 404).
"""
import requests

BASE_URL = "http://localhost:5000"


def test_template_upload_requires_auth():
    """Template upload endpoint should be registered and protected."""
    try:
        response = requests.post(f"{BASE_URL}/api/templates/templates/upload", files={})
        print(f"Template upload status: {response.status_code}")
        print(f"Template upload response: {response.text[:200]}")
        return response.status_code == 401
    except Exception as exc:
        print(f"Template upload check failed: {exc}")
        return False


def test_template_org_list_requires_auth():
    """Template list endpoint should be registered and protected."""
    try:
        response = requests.get(f"{BASE_URL}/api/templates/templates/organization/dummy-org")
        print(f"Template org list status: {response.status_code}")
        print(f"Template org list response: {response.text[:200]}")
        return response.status_code == 401
    except Exception as exc:
        print(f"Template org list check failed: {exc}")
        return False


def test_ocr_verify_requires_auth():
    """OCR verification endpoint should be registered and protected."""
    try:
        response = requests.post(f"{BASE_URL}/api/ocr/verify-credential-ocr", files={})
        print(f"OCR verify status: {response.status_code}")
        print(f"OCR verify response: {response.text[:200]}")
        return response.status_code == 401
    except Exception as exc:
        print(f"OCR verify check failed: {exc}")
        return False


if __name__ == "__main__":
    print("Testing OCR/template endpoints...")
    print("=" * 60)

    checks = {
        "Template upload auth guard": test_template_upload_requires_auth(),
        "Template org list auth guard": test_template_org_list_requires_auth(),
        "OCR verify auth guard": test_ocr_verify_requires_auth(),
    }

    print("\nResults")
    print("-" * 60)
    for name, passed in checks.items():
        print(f"{'✅' if passed else '❌'} {name}")

    all_ok = all(checks.values())
    print("\nOverall:", "✅ PASS" if all_ok else "❌ FAIL")
