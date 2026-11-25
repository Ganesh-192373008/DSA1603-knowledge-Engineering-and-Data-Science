# Q7: Travel-mode survey - data structures and bar chart (percentages)
import matplotlib.pyplot as plt

survey = {"Walk": 8, "Bicycle": 12, "Bus": 30, "Metro": 18,
          "Two-wheeler": 20, "Car": 9, "Auto-rickshaw": 3}
modes = list(survey.keys())
households = list(survey.values())
total = sum(households)
percent = [h / total * 100 for h in households]

print("Total households surveyed:", total)
print(f"{'Mode':<15}{'Households':>11}{'Percent':>10}")
for m, h, p in zip(modes, households, percent):
    print(f"{m:<15}{h:>11}{p:>9.1f}%")

plt.figure(figsize=(9, 5))
bars = plt.bar(modes, percent, color="steelblue")
for b, p in zip(bars, percent):
    plt.text(b.get_x() + b.get_width() / 2, p + 0.5, f"{p:.0f}%", ha="center")
plt.xlabel("Travel mode")
plt.ylabel("Households (%)")
plt.title("Main Mode of Daily Travel (100 households)")
plt.xticks(rotation=20)
plt.savefig("q07.png", dpi=110, bbox_inches="tight")
plt.show()
