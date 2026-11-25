# Q9: Knowledge graph of an electricity network with rdflib + SPARQL
from rdflib import Graph, Namespace, RDF, RDFS, Literal

EX = Namespace("http://example.org/grid#")          # custom namespace
g = Graph()
g.bind("ex", EX)

# ---------- 1. Schema: entity types and relations ----------
for cls in ["GeneratingStation", "Substation", "Transformer", "Feeder", "ConsumerArea", "District"]:
    g.add((EX[cls], RDF.type, RDFS.Class))
# relations: feeds (GeneratingStation->Substation, Substation->Substation/Transformer, Transformer->Feeder)
#            serves (Feeder->ConsumerArea)      locatedIn (Substation->District)
for prop in ["feeds", "serves", "locatedIn"]:
    g.add((EX[prop], RDF.type, RDF.Property))
g.add((EX.serves, RDFS.domain, EX.Feeder));       g.add((EX.serves, RDFS.range, EX.ConsumerArea))
g.add((EX.locatedIn, RDFS.domain, EX.Substation)); g.add((EX.locatedIn, RDFS.range, EX.District))

# ---------- 2. Instance data ----------
def entity(name, cls):
    g.add((EX[name], RDF.type, EX[cls]))
    g.add((EX[name], RDFS.label, Literal(name)))

for n in ["GS1", "GS2"]:                         entity(n, "GeneratingStation")
for n in ["SS1", "SS2", "SS3", "SS4"]:           entity(n, "Substation")
for n in ["T1", "T2", "T3", "T4", "T5", "T6"]:   entity(n, "Transformer")
for n in ["F1", "F2", "F3", "F4", "F5", "F6"]:   entity(n, "Feeder")
for n in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]: entity(n, "ConsumerArea")
for n in ["North", "Central", "South"]:          entity(n, "District")

feeds = [("GS1", "SS1"), ("GS1", "SS2"), ("GS2", "SS3"), ("SS1", "SS4"),          # upstream links
         ("SS1", "T1"), ("SS1", "T2"), ("SS2", "T3"), ("SS3", "T4"), ("SS4", "T5"), ("SS4", "T6"),
         ("T1", "F1"), ("T2", "F2"), ("T3", "F3"), ("T4", "F4"), ("T5", "F5"), ("T6", "F6")]
serves = [("F1", "A1"), ("F1", "A2"), ("F2", "A2"), ("F3", "A3"), ("F3", "A4"),
          ("F4", "A5"), ("F4", "A6"), ("F5", "A7"), ("F6", "A7"), ("F6", "A8")]
located = [("SS1", "North"), ("SS2", "North"), ("SS3", "Central"), ("SS4", "South")]
for a, b in feeds:   g.add((EX[a], EX.feeds, EX[b]))
for a, b in serves:  g.add((EX[a], EX.serves, EX[b]))
for a, b in located: g.add((EX[a], EX.locatedIn, EX[b]))
print("Triples in the graph:", len(g))

def local(term):                                  # http://example.org/grid#A1 -> A1
    return str(term).split("#")[-1]

# ---------- 3. SPARQL: consumer areas depending on a substation (directly or indirectly) ----------
def dependents(sub):
    q = f"""
    PREFIX ex: <http://example.org/grid#>
    SELECT DISTINCT ?area WHERE {{
        ex:{sub} ex:feeds+ ?f .          # follow 'feeds' links any number of times
        ?f a ex:Feeder .
        ?f ex:serves ?area .
    }} ORDER BY ?area"""
    return [local(r.area) for r in g.query(q)]

for sub in ["SS1", "SS2", "SS3", "SS4"]:
    district = local(g.value(EX[sub], EX.locatedIn))
    print(f"Failure of {sub} ({district}) affects: {dependents(sub)}")

# ---------- 4. Single points of failure: consumer areas served by exactly one feeder ----------
q_spof = """
PREFIX ex: <http://example.org/grid#>
SELECT ?area (COUNT(DISTINCT ?f) AS ?n) WHERE { ?f ex:serves ?area }
GROUP BY ?area HAVING (COUNT(DISTINCT ?f) = 1) ORDER BY ?area"""
print("\nSingle points of failure (area -> only feeder -> substations upstream):")
for r in g.query(q_spof):
    area = local(r.area)
    feeder = local(g.value(predicate=EX.serves, object=r.area))
    up = g.query(f"""PREFIX ex: <http://example.org/grid#>
        SELECT DISTINCT ?s WHERE {{ ?s a ex:Substation . ?s ex:feeds+ ex:{feeder} }} ORDER BY ?s""")
    print(f"  {area} -> {feeder} -> {[local(u.s) for u in up]}")
