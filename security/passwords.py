from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain_password):
    return password_hasher.hash(plain_password)


def verify_password(plain_password, hashed_password):
    try:
        return password_hasher.verify(hashed_password, plain_password,)
    except VerifyMismatchError:
        return False
    except InvalidHashError:
        return False


def needs_rehash(password_hash: str) -> bool:
    return password_hasher.check_needs_rehash(password_hash)
