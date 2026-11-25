# Q15: Preprocessing for k-NN: scaling, binning, one-hot encoding (fit on training data only)
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, cross_val_score, RepeatedStratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder, KBinsDiscretizer

# ---------- Task 1: scale the vector three ways ----------
x = np.array([150, 250, 450, 700, 900], dtype=float)
minmax = (x - x.min()) / (x.max() - x.min())
zscore = (x - x.mean()) / x.std()                      # population std, same as StandardScaler
j = int(np.floor(np.log10(np.abs(x).max()))) + 1       # smallest j with max|x| / 10^j < 1
decimal = x / 10 ** j
print("Task 1: scaling of", x)
print("  min-max  :", minmax.round(4))
print("  z-score  :", zscore.round(4), f"(mean={x.mean():.0f}, std={x.std():.4f})")
print(f"  decimal  : {decimal.round(4)}   (j = {j}, divide by 10^{j})")

# ---------- Task 2: equal-depth binning ----------
h = np.array([5, 9, 12, 18, 20, 22, 27, 30, 36], dtype=float)
bins = h.reshape(3, 3)                                  # 9 sorted values -> 3 bins of equal depth (3)
print("\nTask 2: equal-depth bins of", h.astype(int))
by_mean = np.repeat(bins.mean(axis=1), 3)
by_bound = np.concatenate([[b[0] if v - b[0] <= b[-1] - v else b[-1] for v in b] for b in bins])
for i, b in enumerate(bins, 1):
    print(f"  Bin {i}: {b.astype(int)}  mean={b.mean():.2f}")
print("  Smoothing by bin means      :", by_mean.round(2))
print("  Smoothing by bin boundaries :", by_bound.astype(int))
kb = KBinsDiscretizer(n_bins=3, encode="ordinal", strategy="quantile")
labels = kb.fit_transform(h.reshape(-1, 1)).ravel().astype(int)
print("  KBinsDiscretizer edges      :", kb.bin_edges_[0].round(2))
print("  KBinsDiscretizer bin labels :", labels)
kb_mean = np.array([h[labels == b].mean() for b in labels])
print("  Same grouping as manual bins:", np.array_equal(labels, np.repeat([0, 1, 2], 3)),
      "| same smoothed values:", np.allclose(kb_mean, by_mean))

# ---------- Task 3: 600 synthetic learners, split, effect of scaling on k-NN ----------
rng = np.random.default_rng(42)
n = 600
learners = pd.DataFrame({"age": rng.integers(18, 60, n),
                         "study_minutes": rng.normal(3000, 1200, n).clip(300, 7000).round(),
                         "country": rng.choice(["India", "USA", "UK"], n, p=[0.5, 0.3, 0.2]),
                         "plan": rng.choice(["free", "basic", "premium"], n, p=[0.4, 0.4, 0.2])})
# completion depends on BOTH numeric features (younger learners and heavier studiers finish more often)
logit = 2.0 * ((learners.study_minutes - 3000) / 1200 + (38 - learners.age) / 12
               + learners.plan.map({"free": -0.4, "basic": 0.0, "premium": 0.5}))
learners["completed"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
X, y = learners.drop(columns="completed"), learners["completed"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
print(f"\nTask 3: {n} learners -> train {len(X_tr)}, test {len(X_te)}; completion rate {y.mean():.2f}")

class DecimalScaler(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.j_ = np.floor(np.log10(np.abs(np.asarray(X)).max(axis=0))) + 1   # learnt from training data only
        return self
    def transform(self, X):
        return np.asarray(X) / 10 ** self.j_

num, cat = ["age", "study_minutes"], ["country", "plan"]
def model(scaler):
    ct = ColumnTransformer([("num", scaler, num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    return Pipeline([("prep", ct), ("knn", KNeighborsClassifier(n_neighbors=5))])

options = {"No scaling": "passthrough", "Min-max": MinMaxScaler(), "Z-score": StandardScaler(), "Decimal scaling": DecimalScaler()}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=4, random_state=0)
print(f"\n{'Preprocessing':<18}{'Test accuracy':>15}{'20-fold CV mean':>17}{'CV std':>9}")
for name, sc in options.items():
    pipe = model(sc).fit(X_tr, y_tr)                  # scaler/encoder fitted on TRAIN rows only
    cvs = cross_val_score(model(sc), X, y, cv=cv)     # inside each fold, fitted on that fold's train part
    print(f"{name:<18}{pipe.score(X_te, y_te):>15.4f}{cvs.mean():>17.4f}{cvs.std():>9.4f}")

mm = MinMaxScaler().fit(X_tr[num])
print("\nMin-max parameters learnt from the training set only:",
      "min =", mm.data_min_, "max =", mm.data_max_)
print("Test-set range after applying those training-set parameters (min per column, max per column):")
print(mm.transform(X_te[num]).min(axis=0).round(3), mm.transform(X_te[num]).max(axis=0).round(3))
