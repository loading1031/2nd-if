"""API 키 Fernet 암호화 유틸리티."""

import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _get_fernet() -> Fernet:
    """SECRET_KEY에서 Fernet 키를 파생."""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_key(plaintext: str) -> bytes:
    """평문 API 키를 암호화."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode())


def decrypt_key(ciphertext: bytes) -> str:
    """암호화된 API 키를 복호화."""
    f = _get_fernet()
    return f.decrypt(ciphertext).decode()
