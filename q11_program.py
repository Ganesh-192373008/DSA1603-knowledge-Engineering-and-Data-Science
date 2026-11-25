# Q11: Cleaning merged admission records
import numpy as np, pandas as pd

data = {
 "student_id": [101, 102, 103, 104, 105, 106, 107, 108, 101],
 "name":       ["Arun", "bala", " Chitra", "Deepa ", "Eswar", "Farah", "Gopal", "Hema", "ARUN"],
 "state":      [" tamil nadu", "Tamil Nadu", "KERALA", "kerala ", "Karnataka", "karnataka", " Tamil Nadu ", "ANDHRA PRADESH", "TAMIL NADU"],
 "age":        [19, 20, 18, 21, 210, 19, 22, 20, 19],
 "marks":      [78, 65, np.nan, 82, 74, np.nan, 91, 69, 78],
 "family_income": [240000, 180000, 320000, np.nan, 150000, 9800000, 410000, np.nan, 240000],
}
df = pd.DataFrame(data)
print("RAW TABLE"); print(df.to_string()); print()

def profile(d, title):
    print(f"--- Profile: {title} ---")
    print("Shape:", d.shape)
    print("Missing values per column:"); print(d.isna().sum().to_string())
    print("Duplicate rows:", d.duplicated().sum()); print()

profile(df, "before cleaning")
print("Distinct state spellings before:", sorted(df["state"].unique()), "\n")

# 1. Standardise text columns: trim spaces and use consistent capitalisation
for c in ["name", "state"]:
    df[c] = df[c].str.strip().str.title()
print("Distinct state spellings after :", sorted(df["state"].unique()))
profile(df, "after text standardisation (duplicates now visible)")

# 2. Remove duplicate students
df = df.drop_duplicates().reset_index(drop=True)

# 3. Impossible ages (< 15 or > 60) -> missing
bad_age = (df["age"] < 15) | (df["age"] > 60)
print("Impossible ages replaced by NaN:", df.loc[bad_age, ["student_id", "age"]].values.tolist())
df.loc[bad_age, "age"] = np.nan

print(); profile(df, "after cleaning")
print("CLEAN TABLE"); print(df.to_string())
