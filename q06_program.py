# Q6: Resolution refutation - prove C from A->B, B->C, A
from itertools import combinations

# Clause = frozenset of literals; "~X" is the negation of "X"
def neg(l): return l[1:] if l.startswith("~") else "~" + l

kb = [frozenset({"~A", "B"}),   # A -> B  == ~A v B
      frozenset({"~B", "C"}),   # B -> C  == ~B v C
      frozenset({"A"})]         # A
negated_goal = frozenset({"~C"})  # assume NOT C

clauses = kb + [negated_goal]
steps = {}  # clause -> description
for i, c in enumerate(clauses, 1):
    print(f"({i}) {sorted(c)}   [{'given' if c in kb else 'negated goal'}]")

def show(c): return "{" + ", ".join(sorted(c)) + "}" if c else "{} (empty clause)"

known = list(clauses)
n = len(known)
found = False
while not found:
    new = []
    for (i, a), (j, b) in combinations(enumerate(known, 1), 2):
        for lit in a:
            if neg(lit) in b:
                res = frozenset((a - {lit}) | (b - {neg(lit)}))
                if res not in known and res not in [r for r, _, _ in new]:
                    new.append((res, i, j))
                    break
    if not new:
        break
    for res, i, j in new:
        known.append(res)
        n += 1
        print(f"({n}) {show(res)}   [resolve ({i}) and ({j})]")
        if not res:
            found = True
            break

print()
print("Empty clause derived -> contradiction -> C is PROVED." if found
      else "No contradiction found -> C cannot be proved.")
