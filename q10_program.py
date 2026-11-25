# Q10: Unification of first-order terms
# Variable = string starting with an uppercase letter; constant = lowercase string.
# Compound term / predicate = tuple (functor, arg1, arg2, ...)

def is_var(t):
    return isinstance(t, str) and t[:1].isupper()

def substitute(t, s):
    """Apply substitution s to term t (follows chains of bindings)."""
    if is_var(t):
        return substitute(s[t], s) if t in s else t
    if isinstance(t, tuple):
        return (t[0],) + tuple(substitute(a, s) for a in t[1:])
    return t

def occurs(v, t, s):
    t = substitute(t, s)
    if is_var(t):
        return v == t
    if isinstance(t, tuple):
        return any(occurs(v, a, s) for a in t[1:])
    return False

def unify(x, y, s=None):
    """Return a substitution (dict) that makes x and y identical, or None."""
    if s is None:
        s = {}
    x, y = substitute(x, s), substitute(y, s)
    if x == y:
        return s
    if is_var(x):
        return None if occurs(x, y, s) else {**s, x: y}
    if is_var(y):
        return None if occurs(y, x, s) else {**s, y: x}
    if isinstance(x, tuple) and isinstance(y, tuple):
        if x[0] != y[0] or len(x) != len(y):
            return None
        for a, b in zip(x[1:], y[1:]):
            s = unify(a, b, s)
            if s is None:
                return None
        return s
    return None

def fmt(t):
    if isinstance(t, tuple):
        return f"{t[0]}(" + ", ".join(fmt(a) for a in t[1:]) + ")"
    return t

tests = [
    (("borrowed", "P", "b204"), ("borrowed", "ravi", "b204")),
    (("wrote", "A", "ponniyin_selvan"), ("wrote", "kalki", "B")),
    (("borrowed", "X", "Y"), ("borrowed", "Y", "b204")),
    (("wrote", "kalki", "b1"), ("wrote", "sujatha", "b1")),
    (("likes", "X", "X"), ("likes", "Y", ("f", "Y"))),
]

for i, (a, b) in enumerate(tests, 1):
    s = unify(a, b)
    print(f"Test {i}: unify({fmt(a)}, {fmt(b)})")
    if s is None:
        print("   Result : FAIL (no unifier)")
    else:
        final = {v: fmt(substitute(v, s)) for v in s}
        print("   Result : SUCCESS, substitution =", final)
        print("   Check  :", fmt(substitute(a, s)), "==", fmt(substitute(b, s)))
