# key_exchange.py

import random
import elliptic_curve as ec

def generate_keypair(generator, a, p, n):
    """Генерация ключевой пары (private, public)"""
    private_key = random.randint(1, n - 1)
    public_key = ec.scalar_mult(private_key, generator, a, p)
    return private_key, public_key


def ecdh_shared_secret(private_key, other_public, a, p):
    """Вычисление общего секрета"""
    return ec.scalar_mult(private_key, other_public, a, p)
