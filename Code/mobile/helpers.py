import hashlib

from mobile.constants import SECRET_KEY


def hash_password(password: str, salt: str) -> str:
    """Hashes a password using SHA-256. Both salting and peppering are
    used.
    """
    return hashlib.sha256(f"{password}{salt}{SECRET_KEY}".encode()).hexdigest()


def validate_password(username: str, password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if username in password:
        return False
    return True


def get_price(minutes: float) -> float:
    return round(10 + max(0, 2.5 * minutes), 2)


def clean_username(username: str) -> str:
    return username.strip().lower()
