# Q14: Evaluate first-order statements over a finite domain and verify quantifier duality
people = ["Kavin", "Latha", "Mohan", "Nila"]
projects = ["Alpha", "Beta"]
assigned = {"Kavin": {"Alpha", "Beta"}, "Latha": {"Alpha"},
            "Mohan": {"Beta"}, "Nila": {"Alpha", "Beta"}}
trained_alpha = {"Kavin", "Latha", "Nila"}
score_beta = {"Kavin": 88, "Mohan": 72, "Nila": 95}

Assigned = lambda x, p: p in assigned[x]
Trained = lambda x: x in trained_alpha                   # security training for Alpha
Score = lambda x: score_beta.get(x, float("-inf"))       # Latha has no Beta score

forall = lambda pred: all(pred(x) for x in people)
exists = lambda pred: any(pred(x) for x in people)

S1 = forall(lambda x: (not Assigned(x, "Alpha")) or Trained(x))
S2 = exists(lambda x: Assigned(x, "Beta") and Score(x) >= 90)
S3 = all(any(Assigned(x, p) for p in projects) for x in people)
S4 = not exists(lambda x: Assigned(x, "Alpha") and not Trained(x))
S5 = forall(lambda x: (not Assigned(x, "Beta")) or Score(x) >= 80)

print("S1  forall x (Assigned(x,Alpha) -> Trained(x))         :", S1)
print("S2  exists x (Assigned(x,Beta) AND Score(x,Beta)>=90)   :", S2,
      "-> witnesses:", [x for x in people if Assigned(x, "Beta") and Score(x) >= 90])
print("S3  forall x exists p Assigned(x,p)                     :", S3)
print("S4  NOT exists x (Assigned(x,Alpha) AND NOT Trained(x)) :", S4)
print("S5  forall x (Assigned(x,Beta) -> Score(x,Beta)>=80)    :", S5,
      "-> counter-example:", [x for x in people if Assigned(x, "Beta") and Score(x) < 80])

print("\nQuantifier duality checks")
# NOT exists x P(x)  <=>  forall x NOT P(x)
P = lambda x: Assigned(x, "Alpha") and not Trained(x)
lhs = not exists(P)
rhs = forall(lambda x: not P(x))
duality1 = (lhs == rhs)
print("NOT exists x P  ==  forall x NOT P   (P = Assigned(x,Alpha) AND NOT Trained(x)):", lhs, "==", rhs, "->", duality1)
print("S1 == S4 (same meaning, different form):", S1, "==", S4, "->", S1 == S4)

# NOT forall x Q(x)  <=>  exists x NOT Q(x)
Q = lambda x: (not Assigned(x, "Beta")) or Score(x) >= 80
lhs = not forall(Q)
rhs = exists(lambda x: not Q(x))
duality2 = (lhs == rhs)
print("NOT forall x Q  ==  exists x NOT Q   (Q = S5 body):", lhs, "==", rhs, "->", duality2)
print("Duality holds for both quantifiers on this domain:", duality1 and duality2)
