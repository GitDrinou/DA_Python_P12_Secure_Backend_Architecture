import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError


password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)
SPECIAL_CHAR_RE = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength(password):
    errors = []

    if len(password) < 8:
        errors.append("at least 8 characters")

    if not any(char.isupper() for char in password):
        errors.append("one uppercase letter")

    if not any(char.isdigit() for char in password):
        errors.append("one digit")

    if not SPECIAL_CHAR_RE.search(password):
        errors.append("one special character")

    if errors:
        raise ValueError(
            "Password must contain " + ", ".join(errors) + "."
        )


def hash_password(plain_password):
    validate_password_strength(plain_password)
    return password_hasher.hash(plain_password)


def verify_password(plain_password, hashed_password):
    try:
        return password_hasher.verify(hashed_password, plain_password,)
    except VerifyMismatchError:
        return False
    except InvalidHashError:
        return False
