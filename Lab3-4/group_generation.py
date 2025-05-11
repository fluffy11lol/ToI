# group_generation.py

def generate_points(a, b, p):
    """Генерация всех точек эллиптической кривой над F_p"""
    points = [None]  # точка на бесконечности

    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                points.append((x, y))

    return points
