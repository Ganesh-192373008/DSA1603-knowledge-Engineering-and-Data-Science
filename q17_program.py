# Q17: Travel ontology (owlready2): match travellers to tour packages by interests
from owlready2 import *

onto = get_ontology("http://example.org/travel.owl")

with onto:
    # ---------- 1. Class hierarchy ----------
    class Interest(Thing): pass
    class AdventureInterest(Interest): pass
    class CulturalInterest(Interest): pass
    class WaterSport(AdventureInterest): pass
    class ScubaDiving(WaterSport): pass            # ScubaDiving is-a WaterSport
    class Hiking(AdventureInterest): pass
    class Trekking(AdventureInterest): pass
    class HeritageWalk(CulturalInterest): pass
    class TourPackage(Thing): pass
    class Traveller(Thing): pass
    class Destination(Thing): pass

    # synonym handling: the two terms denote the same concept
    Trekking.equivalent_to.append(Hiking)

    # ---------- 2. Properties ----------
    class hasInterest(ObjectProperty):   domain = [Traveller];   range = [Interest]
    class offersActivity(ObjectProperty): domain = [TourPackage]; range = [Interest]
    class hasDestination(ObjectProperty): domain = [TourPackage]; range = [Destination]
    class interestLevel(DataProperty, FunctionalProperty): domain = [Interest]; range = [int]

    # ---------- 3. Individuals ----------
    himalaya, andaman, rajasthan, goa = Destination("Himalaya"), Destination("Andaman"), Destination("Rajasthan"), Destination("Goa")

    def package(name, activity_cls, dest):
        p = TourPackage(name)
        p.offersActivity = [activity_cls(name + "_activity")]
        p.hasDestination = [dest]
        return p
    p1 = package("HimalayanTrek",     Hiking,       himalaya)
    p2 = package("AndamanDiving",     ScubaDiving,  andaman)
    p3 = package("RajasthanHeritage", HeritageWalk, rajasthan)
    p4 = package("GoaBeaches",        WaterSport,   goa)

    def traveller(name, *interests):
        t = Traveller(name)
        t.hasInterest = []
        for cls, level in interests:
            i = cls(f"{name}_{cls.name}")
            i.interestLevel = level
            t.hasInterest.append(i)
        return t
    divya  = traveller("Divya",  (Trekking, 5))                       # says "trekking"
    farhan = traveller("Farhan", (ScubaDiving, 4))
    gita   = traveller("Gita",   (HeritageWalk, 5))
    hari   = traveller("Hari",   (Hiking, 3), (ScubaDiving, 2))

    # ---------- defined classes: which travellers suit which package ----------
    class SuitsHimalayanTrek(Traveller):     equivalent_to = [Traveller & hasInterest.some(Hiking)]
    class SuitsAndamanDiving(Traveller):     equivalent_to = [Traveller & hasInterest.some(ScubaDiving)]
    class SuitsRajasthanHeritage(Traveller): equivalent_to = [Traveller & hasInterest.some(HeritageWalk)]
    class SuitsGoaBeaches(Traveller):        equivalent_to = [Traveller & hasInterest.some(WaterSport)]
    class AdventureLover(Traveller):         equivalent_to = [Traveller & hasInterest.some(AdventureInterest)]

print("Class hierarchy")
for c in [AdventureInterest, CulturalInterest, WaterSport, ScubaDiving, Hiking, Trekking, HeritageWalk]:
    print(f"  {c.name:<17} subclass-of {c.is_a[0].name}")
print("Synonym: Trekking == Hiking  (equivalent classes)")

sync_reasoner_hermit(infer_property_values=True)      # needs Java; use sync_reasoner_pellet() for Pellet

people = [divya, farhan, gita, hari]
matches = [("HimalayanTrek", SuitsHimalayanTrek), ("AndamanDiving", SuitsAndamanDiving),
           ("RajasthanHeritage", SuitsRajasthanHeritage), ("GoaBeaches", SuitsGoaBeaches)]
print("\nPackage matches (inferred by the reasoner)")
for name, cls in matches:
    names = [t.name for t in people if isinstance(t, cls)]
    print(f"  {name:<18}-> {', '.join(names) if names else 'none'}")
print("\nAdventure lovers:", ", ".join(t.name for t in people if isinstance(t, AdventureLover)))
print("\nInterest levels")
for t in people:
    print(f"  {t.name:<7}", dict(sorted((i.name.split('_')[1], i.interestLevel) for i in t.hasInterest)))
