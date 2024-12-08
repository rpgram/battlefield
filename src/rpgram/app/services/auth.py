import random
import string


def secure_string_generator(length: int = 16):
    """Криптостойкий генератор паролей"""
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
