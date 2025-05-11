import tkinter as tk
from tkinter import messagebox
import random
from math import isqrt

# --- Арифметика в конечном поле ---



def modinv(a, p):
    """Обратный элемент по модулю p"""
    if a == 0:
        raise ValueError('Нет обратного элемента для нуля')
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % p

def point_add(P, Q, a, p):
    """Сложение двух точек на эллиптической кривой"""
    if P is None:
        return Q
    if Q is None:
        return P
    if P == Q:
        if P[1] == 0:
            return None
        m = (3 * P[0]**2 + a) * modinv(2 * P[1], p) % p
    elif P[0] == Q[0]:
        return None
    else:
        m = (Q[1] - P[1]) * modinv(Q[0] - P[0], p) % p
    x_r = (m**2 - P[0] - Q[0]) % p
    y_r = (m * (P[0] - x_r) - P[1]) % p
    return (x_r, y_r)

def is_simple(p):
    i = 2
    while i < p:
        if p % i == 0:
            return False
        i = i + 1
    return True

def scalar_mult(k, P, a, p):
    """Умножение точки на скаляр"""
    result = None
    addend = P
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result

def generate_points(a, b, p):
    """Генерация всех точек эллиптической кривой"""
    points = [None]  # Точка на бесконечности
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                points.append((x, y))
    return points

def auto_generate_ab(p):
    """Автоматический подбор a и b для заданного p"""
    while True:
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)
        discriminant = (4 * a**3 + 27 * b**2) % p
        if discriminant != 0:
            return a, b

# --- Алгоритмы ---

def keygen(G, a, p, n):
    """Генерация пары ключей"""
    private_key = random.randint(1, n - 1)
    public_key = scalar_mult(private_key, G, a, p)
    return private_key, public_key

def ecdsa_sign(message, d, G, a, p, n):
    """Генерация цифровой подписи"""
    e = hash(message) % n
    while True:
        k = random.randint(1, n - 1)
        R = scalar_mult(k, G, a, p)
        if R is None:
            continue
        r = R[0] % n
        if r == 0:
            continue
        try:
            k_inv = modinv(k, n)
        except ValueError:
            continue
        s = (k_inv * (e + d * r)) % n
        if s != 0:
            break
    return r, s

def ecdsa_verify(message, signature, Q, G, a, p, n):
    """Проверка цифровой подписи"""
    r, s = signature
    if not (1 <= r < n and 1 <= s < n):
        return False
    e = hash(message) % n
    try:
        s_inv = modinv(s, n)
    except ValueError:
        return False
    u1 = (e * s_inv) % n
    u2 = (r * s_inv) % n
    P = point_add(
        scalar_mult(u1, G, a, p),
        scalar_mult(u2, Q, a, p),
        a, p
    )
    if P is None:
        return False
    return P[0] % n == r

# --- GUI ---

class ECDSAGUI:
    def __init__(self, root):
        self.root = root
        root.title("ECDSA на эллиптических кривых")

        self.label_p = tk.Label(root, text="Введите p (простое число > 3):")
        self.label_p.pack()
        self.entry_p = tk.Entry(root)
        self.entry_p.pack()

        self.generate_group_button = tk.Button(root, text="Сгенерировать группу EM(a,b)", command=self.generate_group)
        self.generate_group_button.pack()

        self.group_text = tk.Text(root, height=15, width=60)
        self.group_text.pack()

        self.keygen_button = tk.Button(root, text="Выполнить обмен ключами", command=self.exchange_keys, state=tk.DISABLED)
        self.keygen_button.pack()

        self.sign_label = tk.Label(root, text="Введите сообщение для подписи:")
        self.sign_label.pack()
        self.entry_message = tk.Entry(root, width=50)
        self.entry_message.pack()

        self.sign_button = tk.Button(root, text="Подписать сообщение", command=self.sign_message, state=tk.DISABLED)
        self.sign_button.pack()

        self.verify_button = tk.Button(root, text="Проверить подпись", command=self.verify_signature, state=tk.DISABLED)
        self.verify_button.pack()

        self.output_text = tk.Text(root, height=10, width=60)
        self.output_text.pack()

    def generate_group(self):
        try:
            self.p = int(self.entry_p.get())
            if self.p <= 3:
                messagebox.showerror("Ошибка", "p должно быть больше 3")
                return
            if not is_simple(self.p):
                messagebox.showerror("Ошибка", "p должно быть простым")
                return
            self.a, self.b = auto_generate_ab(self.p)

            self.points = generate_points(self.a, self.b, self.p)
            self.group_text.delete(1.0, tk.END)
            self.group_text.insert(tk.END, f"p = {self.p}\n")
            self.group_text.insert(tk.END, f"Автоматически подобраны параметры:\n a = {self.a}\n b = {self.b}\n")
            self.group_text.insert(tk.END, f"Всего точек: {len(self.points)}\n")
            for pt in self.points:
                self.group_text.insert(tk.END, f"{pt}\n")

            self.G = next(pt for pt in self.points if pt is not None)
            self.n = len(self.points)

            self.keygen_button.config(state=tk.NORMAL)
            messagebox.showinfo("Готово", f"Группа сгенерирована!\nПараметры:\n a = {self.a}\n b = {self.b}\nГенератор G: {self.G}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def exchange_keys(self):
        self.private_key, self.public_key = keygen(self.G, self.a, self.p, self.n)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Закрытый ключ (d): {self.private_key}\n")
        self.output_text.insert(tk.END, f"Открытый ключ (Q): {self.public_key}\n")
        self.sign_button.config(state=tk.NORMAL)
        messagebox.showinfo("Готово", "Ключи успешно сгенерированы!")

    def sign_message(self):
        msg = self.entry_message.get()
        if not msg:
            messagebox.showerror("Ошибка", "Введите сообщение")
            return
        self.signature = ecdsa_sign(msg, self.private_key, self.G, self.a, self.p, self.n)
        self.output_text.insert(tk.END, f"\nПодпись (r, s): {self.signature}\n")
        self.verify_button.config(state=tk.NORMAL)

    def verify_signature(self):
        msg = self.entry_message.get()
        valid = ecdsa_verify(msg, self.signature, self.public_key, self.G, self.a, self.p, self.n)
        result = "Подпись верна" if valid else "Подпись неверна"
        self.output_text.insert(tk.END, f"{result}\n")

# --- Запуск приложения ---

if __name__ == "__main__":
    root = tk.Tk()
    app = ECDSAGUI(root)
    root.mainloop()
