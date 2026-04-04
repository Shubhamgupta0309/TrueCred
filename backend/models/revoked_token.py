"""Model for persisted JWT revocations."""
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField


class RevokedToken(Document):
    """Stores revoked JWT token identifiers (jti)."""

    jti = StringField(required=True, unique=True)
    token_type = StringField(default='access')
    user_id = StringField()
    revoked_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()

    meta = {
        'collection': 'revoked_tokens',
        'indexes': [
            'jti',
            'expires_at',
            '-revoked_at',
        ],
    }

    @classmethod
    def revoke(cls, jti, token_type='access', user_id=None, expires_at=None):
        """Idempotently persist a token revocation."""
        existing = cls.objects(jti=jti).first()
        if existing:
            return existing

        record = cls(
            jti=jti,
            token_type=token_type,
            user_id=str(user_id) if user_id is not None else None,
            expires_at=expires_at,
        )
        record.save()
        return record
