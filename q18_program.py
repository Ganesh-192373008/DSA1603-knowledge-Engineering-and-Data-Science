# Q18: Modus Ponens and Modus Tollens on the water-supply rule chain
rules = [("PumpOn", "TankFilling"),
         ("TankFilling", "TapsHaveWater"),
         ("TapsHaveWater", "GardenWatered")]

def modus_ponens(true_facts):
    """A, A->B  therefore  B  (repeated until nothing new)"""
    facts, log = set(true_facts), []
    changed = True
    while changed:
        changed = False
        for a, b in rules:
            if a in facts and b not in facts:
                facts.add(b)
                log.append(f"Modus Ponens: {a}, ({a} -> {b})  =>  {b}")
                changed = True
    return facts, log

def modus_tollens(false_facts):
    """NOT B, A->B  therefore  NOT A  (repeated until nothing new)"""
    neg, log = set(false_facts), []
    changed = True
    while changed:
        changed = False
        for a, b in rules:
            if b in neg and a not in neg:
                neg.add(a)
                log.append(f"Modus Tollens: NOT {b}, ({a} -> {b})  =>  NOT {a}")
                changed = True
    return neg, log

print("(a) The pump is on. What can be inferred?")
facts, log = modus_ponens({"PumpOn"})
print("\n".join("   " + l for l in log))
print("   Inferred true facts:", sorted(facts))

print("\nExtra demonstration of Modus Tollens: the garden is NOT watered")
neg, log = modus_tollens({"GardenWatered"})
print("\n".join("   " + l for l in log))
print("   Inferred false facts:", sorted(neg))
