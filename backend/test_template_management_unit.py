import io
from unittest.mock import patch

from app import create_app


class DummyUser:
    def __init__(self):
        self.college_id = "org-1"


class DummyQuery:
    def first(self):
        return DummyUser()


class DummyUserModel:
    @staticmethod
    def objects(*args, **kwargs):
        return DummyQuery()



def _auth_headers():
    app = create_app("development")
    with app.app_context():
        token = app.extensions["flask-jwt-extended"]._encode_jwt_from_config(
            identity="user-1",
            token_type="access",
            fresh=True,
            expires_delta=False,
        )
    return {"Authorization": f"Bearer {token}"}


def test_template_upload_returns_200_when_dependencies_mocked():
    app = create_app("development")
    client = app.test_client()

    with patch("routes.template_management.User", DummyUserModel), \
         patch("routes.template_management.ipfs_service.add_file", return_value={"Hash": "QmTestHash"}), \
         patch("routes.template_management.ipfs_service.get_gateway_url", return_value="https://ipfs.io/ipfs/QmTestHash"), \
         patch(
             "routes.template_management.template_matching_service.process_and_store_template",
             return_value={
                 "success": True,
                 "template_id": "tmpl-1",
                 "confidence": 91,
                 "key_fields": {"name": "John"},
             },
         ):
        data = {
            "template_file": (io.BytesIO(b"fake-image"), "template.png"),
            "template_name": "Degree Template",
            "template_type": "degree",
            "organization_id": "org-1",
            "organization_name": "My College",
            "organization_type": "college",
            "required_fields": "[]",
            "optional_fields": "[]",
        }

        response = client.post(
            "/api/templates/templates/upload",
            data=data,
            headers=_auth_headers(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["template_id"] == "tmpl-1"


def test_ocr_verify_requires_auth():
    app = create_app("development")
    client = app.test_client()
    response = client.post("/api/ocr/verify-credential-ocr", data={})
    assert response.status_code == 401
