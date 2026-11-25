# Q3: Bookstore sales - data structures and pie chart
import matplotlib.pyplot as plt

sales = {"Fiction": 14, "Mystery": 9, "Science": 6, "History": 5,
         "Biography": 7, "Self-help": 11, "Comics": 8}
genres = list(sales.keys())
counts = list(sales.values())
total = sum(counts)
print("Genres:", genres)
print("Counts:", counts)
print("Total books sold:", total)
print("\nPercentage distribution")
for g, c in sales.items():
    print(f"  {g:<10} {c:>3}  {c / total * 100:6.2f}%")

plt.figure(figsize=(7, 7))
plt.pie(counts, labels=genres, autopct="%1.1f%%", startangle=90)
plt.title("Books Sold per Genre (60 books, one week)")
plt.axis("equal")
plt.savefig("q03.png", dpi=110, bbox_inches="tight")
plt.show()
