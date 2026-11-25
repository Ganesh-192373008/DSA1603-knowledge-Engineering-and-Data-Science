# Q1: Rule-based expert system for airline refund requests
# A small custom forward-chaining engine (production rules, salience, explanation facility).
# (experta could be used instead; the engine below does the same job without extra installs.)

class Rule:
    def __init__(self, rid, name, salience, cond, kind, why, outcome=None, refund=None, flag=None):
        self.rid, self.name, self.salience = rid, name, salience
        self.cond, self.kind, self.why = cond, kind, why      # kind: 'flag' or 'decision'
        self.outcome, self.refund, self.flag = outcome, refund, flag

# ---------------- Knowledge base: 19 IF-THEN production rules ----------------
# Fact fields: fare, hours, reason, price (INR), tier, claims.   wm["flags"] = derived facts
R = Rule
RULES = [
 # --- inference rules that derive new facts (highest salience: fire first) ---
 R("R01", "HighValue",       100, lambda f: f["price"] >= 40000,                       "flag", "ticket price >= Rs 40,000", flag="high_value"),
 R("R02", "FrequentClaimer", 100, lambda f: f["claims"] >= 3,                          "flag", "3 or more past refund claims", flag="frequent_claimer"),
 R("R03", "EliteMember",     100, lambda f: f["tier"] in ("gold", "platinum"),         "flag", "frequent-flyer tier is gold/platinum", flag="elite"),
 R("R04", "LateCancel",      100, lambda f: f["hours"] < 24,                           "flag", "cancelled < 24 h before departure", flag="late"),
 R("R05", "EarlyCancel",     100, lambda f: f["hours"] >= 72,                          "flag", "cancelled >= 72 h before departure", flag="early"),
 R("R06", "RefundableFare",  100, lambda f: f["fare"] in ("first", "business", "economy_flex"), "flag", "fare class is refundable", flag="refundable"),
 # --- decision rules (salience decides which one wins when several match) ---
 R("R07", "AirlineFault",     90, lambda f: f["reason"] in ("airline_cancelled", "schedule_change"),
   "decision", "airline cancelled / changed the flight", "APPROVE", 100),
 R("R08", "ManualCheckMedical", 85, lambda f: f["reason"] in ("medical", "bereavement") and "frequent_claimer" in f["flags"] and "high_value" in f["flags"],
   "decision", "medical/bereavement claim on a costly ticket by a frequent claimer needs document check", "ESCALATE", None),
 R("R09", "Compassionate",    80, lambda f: f["reason"] in ("medical", "bereavement"),
   "decision", "medical/bereavement reason: fare rules waived", "APPROVE", 100),
 R("R10", "ExcessClaims",     75, lambda f: f["claims"] >= 5 and f["reason"] == "voluntary",
   "decision", "voluntary request with 5+ past claims (possible abuse)", "REJECT", 0),
 R("R11", "VisaDenied",       65, lambda f: f["reason"] == "visa_denied",
   "decision", "visa refusal letter must be verified", "ESCALATE", None),
 R("R12", "CostlyLateRefund", 70, lambda f: "high_value" in f["flags"] and "late" in f["flags"] and f["reason"] == "voluntary" and "elite" not in f["flags"],
   "decision", "high-value voluntary refund requested very late", "ESCALATE", None),
 R("R13", "EliteGoodStanding",60, lambda f: "elite" in f["flags"] and f["reason"] == "voluntary" and "late" not in f["flags"] and "frequent_claimer" not in f["flags"],
   "decision", "elite member in good standing", "APPROVE", 100),
 R("R14", "FlexFareNormal",   50, lambda f: "refundable" in f["flags"] and f["reason"] == "voluntary" and "late" not in f["flags"],
   "decision", "refundable fare, cancelled in time (10% fee)", "APPROVE", 90),
 R("R15", "FlexFareLate",     45, lambda f: "refundable" in f["flags"] and f["reason"] == "voluntary" and "late" in f["flags"],
   "decision", "refundable fare but cancelled late (50% fee)", "APPROVE", 50),
 R("R16", "SaverEarly",       40, lambda f: f["fare"] == "economy_saver" and f["reason"] == "voluntary" and "early" in f["flags"],
   "decision", "non-refundable saver fare cancelled early: partial refund", "APPROVE", 50),
 R("R17", "SaverMiddle",      30, lambda f: f["fare"] == "economy_saver" and f["reason"] == "voluntary" and "early" not in f["flags"] and "late" not in f["flags"],
   "decision", "non-refundable saver fare, 24-72 h: only taxes refunded", "APPROVE", 25),
 R("R18", "SaverLate",        20, lambda f: f["fare"] == "economy_saver" and f["reason"] == "voluntary" and "late" in f["flags"],
   "decision", "non-refundable saver fare cancelled late", "REJECT", 0),
 R("R19", "Default",           1, lambda f: f["decision"] is None,
   "decision", "no specific policy covers this case", "ESCALATE", None),
]

def run(request):
    wm = dict(request, flags=set(), decision=None)
    fired, done = [], set()
    while True:
        # conflict set = rules whose IF-part matches and that have not fired yet
        agenda = [r for r in RULES if r.rid not in done and r.cond(wm)]
        if not agenda:
            break
        agenda.sort(key=lambda r: (-r.salience, r.rid))   # conflict resolution: highest salience first
        r = agenda[0]
        done.add(r.rid)
        if r.kind == "flag":
            wm["flags"].add(r.flag)
            fired.append((r, "derived fact '%s'" % r.flag))
        elif wm["decision"] is None:
            wm["decision"] = (r.outcome, r.refund, r)
            fired.append((r, "DECISION %s" % r.outcome))
        else:
            fired.append((r, "matched but overridden by %s (higher salience)" % wm["decision"][2].rid))
    return wm, fired

def explain(n, request):
    wm, fired = run(request)
    outcome, refund, rule = wm["decision"]
    print(f"Request {n}: {request}")
    print("  Rules fired (in order):")
    for r, note in fired:
        print(f"    [{r.salience:>3}] {r.rid} {r.name:<18} -> {note}. Because: {r.why}")
    pct = f" with {refund}% refund" if refund is not None else ""
    print(f"  FINAL DECISION: {outcome}{pct}  (decided by {rule.rid} {rule.name}, salience {rule.salience})\n")

requests = [
 dict(fare="economy_saver", hours=10,  reason="voluntary",         price=8000,  tier="none",     claims=0),
 dict(fare="business",      hours=100, reason="voluntary",         price=60000, tier="gold",     claims=1),
 dict(fare="economy_flex",  hours=30,  reason="medical",           price=55000, tier="silver",   claims=4),
 dict(fare="economy_saver", hours=90,  reason="voluntary",         price=9000,  tier="none",     claims=6),
 dict(fare="economy_saver", hours=5,   reason="schedule_change",   price=20000, tier="none",     claims=7),
 dict(fare="economy_flex",  hours=6,   reason="voluntary",         price=45000, tier="silver",   claims=0),
 dict(fare="first",         hours=48,  reason="visa_denied",       price=90000, tier="platinum", claims=0),
 dict(fare="economy_flex",  hours=30,  reason="name_change",       price=7000,  tier="none",     claims=0),
]
print(f"Knowledge base: {len(RULES)} rules\n")
for i, req in enumerate(requests, 1):
    explain(i, req)
