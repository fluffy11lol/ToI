# ecdsa.py

import elliptic_curve as ec
import random

def hash_message(message, p):
    """Простая хэш-функция (сумма кодов символов mod p)"""
    return sum([ord(c) for c in message]) % p


def sign(message, private_key, generator, a, p, n):
    z = hash_message(message, p)
    while True:
        k = random.randint(1, n - 1)
        R = ec.scalar_mult(k, generator, a, p)
        if R is None:
            continue
        r = R[0] % n
        if r == 0:
            continue
        k_inv = ec.inverse_mod(k, n)
        s = (k_inv * (z + r * private_key)) % n
        if s == 0:
            continue
        return (r, s)


def verify(message, signature, public_key, generator, a, p, n):
    r, s = signature
    if not (1 <= r < n and 1 <= s < n):
        return False

    z = hash_message(message, p)
    s_inv = ec.inverse_mod(s, n)

    u1 = (z * s_inv) % n
    u2 = (r * s_inv) % n

    point = ec.point_add(
        ec.scalar_mult(u1, generator, a, p),
        ec.scalar_mult(u2, public_key, a, p),
        a, p
    )
    if point is None:
        return False

    x, _ = point
    return (x % n) == r
