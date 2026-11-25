# Q2: Truth-table entailment for the smart greenhouse KB
from itertools import product

symbols = ["L", "E", "H", "V"]

print(f"{'L':^3}{'E':^3}{'H':^3}{'V':^3} | {'R1':^4}{'R2':^4}{'Facts':^6}| {'KB':^4}")
print("-" * 36)
models = []
for L, E, H, V in product([True, False], repeat=4):
    r1 = (not (L and E)) or V
    r2 = (not H) or L
    f = E and H
    k = r1 and r2 and f
    t = lambda b: "T" if b else "F"
    print(f"{t(L):^3}{t(E):^3}{t(H):^3}{t(V):^3} | {t(r1):^4}{t(r2):^4}{t(f):^6}| {t(k):^4}")
    if k:
        models.append(dict(L=L, E=E, H=H, V=V))

print("\nModels of KB (rows where KB is True):", models)
entails_V = all(m["V"] for m in models)
entails_notV = all(not m["V"] for m in models)
print("KB entails V     :", entails_V)
print("KB entails NOT V :", entails_notV)
