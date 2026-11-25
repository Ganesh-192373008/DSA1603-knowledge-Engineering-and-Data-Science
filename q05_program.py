# Q5: Semantic network for a public library using networkx
import random
import networkx as nx

random.seed(7)
G = nx.DiGraph()
def link(a, label, b):
    G.add_edge(a, b, label=label)

# ---- taxonomy: genres and sub-genres (is-a) ----
taxonomy = {
    "Fantasy":            ["High Fantasy", "Children's Fantasy"],
    "Mystery":            ["Detective Fiction", "Children's Mystery"],
    "Science Fiction":    ["Space Opera", "Junior Science Fiction"],
    "Historical Fiction": ["Medieval Tales", "Colonial Era"],
    "Adventure":          ["Survival Stories", "Treasure Hunts"],
}
for genre, subs in taxonomy.items():
    link(genre, "is-a", "Book")
    for s in subs:
        link(s, "is-a", genre)

# ---- properties attached to genres / sub-genres (inherited by books below them) ----
link("Fantasy", "has-property", "fictional-world")
link("Mystery", "has-property", "suspenseful")
link("Historical Fiction", "has-property", "educational")
for s in ["Children's Fantasy", "Children's Mystery", "Junior Science Fiction", "Treasure Hunts"]:
    link(s, "has-property", "suitable-for-children")

# ---- 55 synthetic books (titles/authors are invented for this exercise) ----
adjectives = ["Silent", "Golden", "Hidden", "Lost", "Crimson", "Distant", "Broken", "Secret", "Ancient", "Last", "Wild", "Midnight"]
nouns = ["River", "Crown", "Garden", "Compass", "Island", "Shadow", "Letter", "Tower", "Voyage", "Key", "Forest", "Harbour"]
authors = ["A. Rao", "M. Fernandes", "K. Iyer", "S. Lopez", "T. Nakamura", "R. Mehta", "L. Becker", "D. Okafor", "P. Singh", "H. Costa"]
titles = random.sample([f"The {a} {n}" for a in adjectives for n in nouns], 55)
subgenres = [s for subs in taxonomy.values() for s in subs]
series_of = {"Aria Chronicles": "High Fantasy", "Detective Meera": "Detective Fiction", "Star Drifters": "Space Opera",
             "Island Quest": "Survival Stories", "Old Kingdom Saga": "Medieval Tales", "Young Explorers": "Children's Fantasy"}

books = []
for i, t in enumerate(titles):
    sg = subgenres[i % len(subgenres)]            # 55 books spread over 10 sub-genres
    books.append(t)
    link(t, "is-a", sg)
    link(t, "written-by", random.choice(authors))
    if random.random() < 0.20: link(t, "has-property", "award-winning")
    if random.random() < 0.20: link(t, "has-property", "translated")

# ---- six series of three books, each series inside one sub-genre ----
for series, sg in series_of.items():
    members = [b for b in books if (b, sg) in G.edges][:3]
    for b in members:
        link(b, "part-of-series", series)

# ---- property inheritance through is-a links ----
def isa_ancestors(node):
    out, stack = [], [node]
    while stack:
        n = stack.pop()
        for _, parent, d in G.out_edges(n, data=True):
            if d["label"] == "is-a":
                out.append(parent); stack.append(parent)
    return out

def own_props(node):
    return {b for _, b, d in G.out_edges(node, data=True) if d["label"] == "has-property"}

def all_props(book):
    props = set(own_props(book))
    for anc in isa_ancestors(book):
        props |= own_props(anc)
    return props

def books_under(genre):
    return [b for b in books if genre in isa_ancestors(b)]

print("Nodes:", G.number_of_nodes(), "| Edges:", G.number_of_edges(), "| Books:", len(books))
from collections import Counter
print("Edge labels:", dict(Counter(d["label"] for _, _, d in G.edges(data=True))))
print("Books per genre:", {g: len(books_under(g)) for g in taxonomy})

b = books[1]
print(f"\nInheritance demo for '{b}':")
print("  is-a chain      :", " -> ".join([b] + isa_ancestors(b)))
print("  own properties  :", sorted(own_props(b)) or "none")
print("  all (inherited) :", sorted(all_props(b)))

print("\nQuery 1: Which fantasy books are suitable for children?")
for t in books_under("Fantasy"):
    if "suitable-for-children" in all_props(t):
        print("  -", t)

print("\nQuery 2: Award-winning children's books (any genre)")
for t in books:
    p = all_props(t)
    if "suitable-for-children" in p and "award-winning" in p:
        print("  -", t, "|", [a for _, a, d in G.out_edges(t, data=True) if d["label"] == "is-a"][0])

print("\nQuery 3: Translated mystery books")
for t in books_under("Mystery"):
    if "translated" in all_props(t):
        print("  -", t)

print("\nQuery 4: Books in the series 'Detective Meera'")
for a, s, d in G.edges(data=True):
    if s == "Detective Meera" and d["label"] == "part-of-series":
        print("  -", a)
