# Q12: Movie recommender - user-based and item-based collaborative filtering (cosine similarity)
import numpy as np, pandas as pd

rng = np.random.default_rng(1)
n_users, n_movies, n_ratings = 943, 1682, 100000

# ---- synthetic catalogue and ratings (MovieLens-100K sized) ----
genre_names = ["Action", "Comedy", "Drama", "Thriller", "Romance", "Sci-Fi", "Animation", "Documentary"]
movies = pd.DataFrame({"movieId": np.arange(n_movies),
                       "title": [f"Movie {i + 1:04d}" for i in range(n_movies)],
                       "genre": rng.choice(genre_names, n_movies),
                       "year": rng.integers(1960, 2021, n_movies)})
g_idx = movies["genre"].map({g: i for i, g in enumerate(genre_names)}).values
user_pref = rng.normal(0, 0.9, (n_users, len(genre_names)))      # each user likes some genres more
user_bias, movie_q = rng.normal(0, 0.3, n_users), rng.normal(0, 0.4, n_movies)
u_w = rng.pareto(2.0, n_users) + 1; u_w /= u_w.sum()               # some users rate far more than others
m_w = rng.pareto(1.2, n_movies) + 1; m_w /= m_w.sum()              # some movies are far more popular
pairs = np.unique(rng.choice(n_users, 160000, p=u_w) * n_movies + rng.choice(n_movies, 160000, p=m_w))
pairs = rng.permutation(pairs)[:n_ratings]
uid, mid = pairs // n_movies, pairs % n_movies
raw = 3.2 + user_pref[uid, g_idx[mid]] + user_bias[uid] + movie_q[mid] + rng.normal(0, 0.5, len(uid))
ratings = pd.DataFrame({"userId": uid, "movieId": mid, "rating": np.clip(np.rint(raw), 1, 5).astype(int)})
print("Ratings:", ratings.shape[0], "| users:", ratings.userId.nunique(), "| movies:", ratings.movieId.nunique())
print(ratings.head(3).to_string(index=False))

# ---- 1. user-movie matrix and sparsity ----
R_full = np.zeros((n_users, n_movies)); R_full[uid, mid] = ratings.rating
sparsity = 1 - ratings.shape[0] / (n_users * n_movies)
print(f"\nUser-movie matrix: {n_users} x {n_movies} = {n_users * n_movies:,} cells, {ratings.shape[0]:,} filled")
print(f"Sparsity = {sparsity * 100:.2f}%")

# ---- train/test split (80/20 of the ratings) ----
test_mask = rng.random(len(ratings)) < 0.2
train, test = ratings[~test_mask], ratings[test_mask]
R = np.zeros((n_users, n_movies)); R[train.userId, train.movieId] = train.rating
M = R > 0
user_mean = np.where(M.sum(1) > 0, R.sum(1) / np.maximum(M.sum(1), 1), 3.0)
Rc = (R - user_mean[:, None]) * M                                   # mean-centred ratings

def cosine(A):                                                       # cosine similarity between rows of A
    norm = np.linalg.norm(A, axis=1, keepdims=True); norm[norm == 0] = 1
    A = A / norm
    S = A @ A.T; np.fill_diagonal(S, 0); return S

S_user = cosine(Rc)            # user-user
S_item = cosine(Rc.T)          # item-item (adjusted cosine)

def predict_user(u, i, k=30):
    v = np.where(M[:, i])[0]
    if len(v) == 0: return user_mean[u]
    s = S_user[u, v]; top = np.argsort(-s)[:k]; v, s = v[top], s[top]
    return user_mean[u] + (s @ Rc[v, i]) / max(np.abs(s).sum(), 1e-9)

def predict_item(u, i, k=30):
    j = np.where(M[u])[0]
    if len(j) == 0: return user_mean[u]
    s = S_item[i, j]; top = np.argsort(-s)[:k]; j, s = j[top], s[top]
    return user_mean[u] + (s @ Rc[u, j]) / max(np.abs(s).sum(), 1e-9)

sample = test.sample(4000, random_state=0)
y = sample.rating.values
res = {"User mean baseline": np.array([user_mean[u] for u in sample.userId]),
       "User-based CF": np.array([predict_user(u, i) for u, i in zip(sample.userId, sample.movieId)]),
       "Item-based CF": np.array([predict_item(u, i) for u, i in zip(sample.userId, sample.movieId)])}
print(f"\nEvaluation on {len(sample)} held-out ratings (k = 30 neighbours)")
print(f"{'Method':<22}{'RMSE':>8}{'MAE':>8}")
for name, p in res.items():
    p = np.clip(p, 1, 5)
    print(f"{name:<22}{np.sqrt(np.mean((p - y) ** 2)):>8.4f}{np.mean(np.abs(p - y)):>8.4f}")

# ---- 'Because you watched ...' list for one user (item-based) ----
u = 5
liked = np.argmax(np.where(M[u], R[u], 0))
m = movies.loc[liked]
print(f"\nBecause you watched '{m.title}' ({m.genre}, {m.year}), user {u} may like:")
cand = np.argsort(-S_item[liked])
shown = 0
for c in cand:
    if not M[u, c]:
        r = movies.loc[c]
        print(f"  {r.title}  ({r.genre}, {r.year})  similarity={S_item[liked, c]:.3f}")
        shown += 1
    if shown == 5: break
