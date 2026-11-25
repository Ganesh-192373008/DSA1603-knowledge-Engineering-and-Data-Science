# Q16: Multi-armed bandits for coupon selection (epsilon-greedy and UCB1)
import numpy as np
import matplotlib.pyplot as plt

TRUE_P = np.array([0.05, 0.12, 0.08, 0.20, 0.15])     # hidden redemption probabilities
K, T = len(TRUE_P), 10000

def pull(arm, rng):                                    # environment: reward 1 if redeemed
    return 1 if rng.random() < TRUE_P[arm] else 0

def epsilon_greedy(rng, eps=0.1):
    n, q, rewards = np.zeros(K), np.zeros(K), []
    for t in range(T):
        arm = rng.integers(K) if rng.random() < eps else int(np.argmax(q))
        r = pull(arm, rng)
        n[arm] += 1
        q[arm] += (r - q[arm]) / n[arm]                # incremental mean
        rewards.append(r)
    return np.array(rewards), n, q

def ucb1(rng, c=2.0):
    n, q, rewards = np.zeros(K), np.zeros(K), []
    for t in range(T):
        if t < K:
            arm = t                                    # play each coupon once first
        else:
            arm = int(np.argmax(q + np.sqrt(c * np.log(t + 1) / n)))
        r = pull(arm, rng)
        n[arm] += 1
        q[arm] += (r - q[arm]) / n[arm]
        rewards.append(r)
    return np.array(rewards), n, q

best = TRUE_P.max()
print("True probabilities:", TRUE_P, "| best coupon = #%d (p=%.2f)" % (TRUE_P.argmax() + 1, best))
print("Random policy would expect %.0f redemptions in %d steps; always-best would expect %.0f\n" % (TRUE_P.mean() * T, T, best * T))

for name, fn in [("epsilon-greedy (eps=0.1)", epsilon_greedy), ("UCB1", ucb1)]:
    rewards, n, q = fn(np.random.default_rng(42))
    regret = best * T - rewards.sum()
    print(f"{name}")
    print("  total redemptions :", int(rewards.sum()), f"({rewards.mean() * 100:.2f}% rate)")
    print("  pulls per coupon  :", n.astype(int))
    print("  estimated p       :", q.round(3))
    print("  most-used coupon  : #%d" % (n.argmax() + 1), "| approx. regret:", round(regret, 1), "\n")

# average cumulative regret over 30 independent runs
plt.figure(figsize=(8, 4.5))
for name, fn in [("epsilon-greedy (0.1)", epsilon_greedy), ("UCB1", ucb1)]:
    curves = []
    for seed in range(30):
        r, _, _ = fn(np.random.default_rng(seed))
        curves.append(np.cumsum(best - r))
    plt.plot(np.mean(curves, axis=0), label=name)
plt.xlabel("Step"); plt.ylabel("Cumulative regret (avg of 30 runs)"); plt.title("Bandit agents: regret")
plt.legend(); plt.grid(alpha=0.3)
plt.savefig("q16.png", dpi=110, bbox_inches="tight"); plt.show()
