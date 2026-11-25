# Q8: Unsupervised learning - customer segmentation of music listeners
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, dendrogram
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)

# ---- 1. Synthetic data: 8,000 users, no labels used anywhere below ----
rng = np.random.default_rng(42)
# (hours/week, genres played, skip rate, playlists created, offline ratio) for 4 hidden listener types
types = [(4, 4, 0.40, 1, 0.10, 2800), (18, 12, 0.15, 8, 0.30, 1800),
         (10, 6, 0.25, 3, 0.70, 1900), (8, 20, 0.50, 5, 0.15, 1500)]
rows = []
for h, g, s, p, o, n in types:
    rows.append(np.column_stack([rng.normal(h, 2.0, n), rng.normal(g, 2.0, n),
                                 np.clip(rng.normal(s, 0.07, n), 0, 1), rng.poisson(p, n),
                                 np.clip(rng.normal(o, 0.08, n), 0, 1)]))
cols = ["weekly_hours", "n_genres", "skip_rate", "playlists_created", "offline_ratio"]
df = pd.DataFrame(np.vstack(rows), columns=cols).clip(lower=0).sample(frac=1, random_state=1).reset_index(drop=True)
print("Data shape:", df.shape)
print(df.describe().round(2).loc[["mean", "std", "min", "max"]])

# ---- 2. Standardise ----
X = StandardScaler().fit_transform(df)
print("\nAfter StandardScaler: mean ~", X.mean(axis=0).round(3), " std ~", X.std(axis=0).round(3))

# ---- 3. K-Means: elbow + silhouette ----
ks = range(2, 9)
inertia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inertia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_))
    print(f"k={k}  inertia={km.inertia_:10.1f}  silhouette={sil[-1]:.4f}")
best_k = list(ks)[int(np.argmax(sil))]
print("Best k by silhouette:", best_k)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(list(ks), inertia, "o-"); ax[0].set_title("Elbow method"); ax[0].set_xlabel("k"); ax[0].set_ylabel("Inertia (WCSS)")
ax[1].plot(list(ks), sil, "o-", color="darkorange"); ax[1].set_title("Silhouette score"); ax[1].set_xlabel("k"); ax[1].set_ylabel("Silhouette")
plt.tight_layout(); plt.savefig("q08_elbow.png", dpi=110); plt.show()

km = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(X)
df["kmeans"] = km.labels_

# ---- 4. Agglomerative (Ward) clustering + dendrogram ----
agg = AgglomerativeClustering(n_clusters=best_k, linkage="ward").fit(X)
df["agglo"] = agg.labels_
Z = linkage(X, method="ward")
plt.figure(figsize=(10, 5))
dendrogram(Z, truncate_mode="lastp", p=30, show_leaf_counts=True, leaf_rotation=90)
plt.title("Dendrogram (Ward linkage, last 30 merged clusters, 8,000 users)")
plt.xlabel("Cluster (number of users)"); plt.ylabel("Distance")
plt.tight_layout(); plt.savefig("q08_dendrogram.png", dpi=110); plt.show()

# ---- 5. Compare the two clusterings ----
print(f"\n{'Method':<15}{'Silhouette (higher better)':>28}{'Davies-Bouldin (lower better)':>32}")
for name, lab in [("K-Means", df["kmeans"]), ("Agglomerative", df["agglo"])]:
    print(f"{name:<15}{silhouette_score(X, lab):>28.4f}{davies_bouldin_score(X, lab):>32.4f}")
print("Adjusted Rand Index between the two clusterings:", round(adjusted_rand_score(df["kmeans"], df["agglo"]), 4))

print("\nK-Means cluster profile (original units):")
print(df.groupby("kmeans")[cols].mean().round(2).assign(users=df["kmeans"].value_counts().sort_index()))

pc = PCA(n_components=2).fit_transform(X)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
for a, lab, t in [(ax[0], df["kmeans"], "K-Means"), (ax[1], df["agglo"], "Agglomerative")]:
    a.scatter(pc[:, 0], pc[:, 1], c=lab, s=4, cmap="tab10"); a.set_title(t + f" (k={best_k}) on PCA axes")
    a.set_xlabel("PC1"); a.set_ylabel("PC2")
plt.tight_layout(); plt.savefig("q08_clusters.png", dpi=110); plt.show()
