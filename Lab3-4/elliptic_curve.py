# elliptic_curve.py

def inverse_mod(k, p):
    """Модульный обратный элемент k^-1 mod p (расширенный алгоритм Евклида)"""
    if k == 0:
        raise ZeroDivisionError('division by zero')
    if k < 0:
        # k**-1 = (-k)**-1
        return p - inverse_mod(-k, p)

    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = p, k

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    gcd, x, y = old_r, old_s, old_t
    assert gcd == 1
    return x % p


def is_on_curve(point, a, b, p):
    """Проверка принадлежности точки кривой y² = x³ + a*x + b mod p"""
    if point is None:
        return True
    x, y = point
    return (y ** 2) % p == (x ** 3 + a * x + b) % p


def point_add(point1, point2, a, p):
    """Сложение двух точек"""
    if point1 is None:
        return point2
    if point2 is None:
        return point1

    x1, y1 = point1
    x2, y2 = point2

    if x1 == x2 and y1 != y2:
        return None

    if point1 == point2:
        m = (3 * x1 ** 2 + a) * inverse_mod(2 * y1, p)
    else:
        m = (y2 - y1) * inverse_mod(x2 - x1, p)

    m %= p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p

    return (x3, y3)


def scalar_mult(k, point, a, p):
    """Скалярное умножение k * point"""
    result = None
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1

    return result
