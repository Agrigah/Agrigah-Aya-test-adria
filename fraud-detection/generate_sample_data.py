"""Génère un jeu de données SYNTHÉTIQUE au même format que bank_transactions.csv.
À utiliser uniquement pour tester le notebook si le fichier officiel de l'épreuve n'est pas encore là."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
n = 20000
countries = ["MA", "FR", "ES", "US", "NG", "RU", "AE"]
cats = ["GROCERY", "TRAVEL", "ELECTRONICS", "RESTAURANT", "FUEL", "GAMBLING", "ATM"]

avg7 = rng.gamma(4, 40, n)
amount = rng.gamma(2, avg7 / 2)
hour = rng.integers(0, 24, n)
tx24 = rng.poisson(2, n)
country = rng.choice(countries, n, p=[.45, .2, .1, .1, .05, .05, .05])
cat = rng.choice(cats, n, p=[.25, .1, .1, .25, .15, .05, .1])

score = (-6.2 + 2.6 * (amount / (avg7 + 1) > 3) + 1.8 * ((hour <= 4) | (hour >= 23))
         + 0.6 * np.clip(tx24 - 3, 0, 8) + 2.2 * np.isin(country, ["NG", "RU"])
         + 2.0 * np.isin(cat, ["ELECTRONICS", "GAMBLING"]) + 0.003 * amount)
is_fraud = (rng.random(n) < 1 / (1 + np.exp(-score))).astype(int)

df = pd.DataFrame({
    "transaction_id": np.arange(1, n + 1), "account_id": rng.integers(1000, 3000, n),
    "amount": amount.round(2), "hour": hour, "country": country, "merchant_category": cat,
    "transactions_last_24h": tx24, "average_amount_last_7d": avg7.round(2), "is_fraud": is_fraud})
for col, p in [("amount", .01), ("country", .02), ("average_amount_last_7d", .02), ("merchant_category", .01)]:
    df.loc[rng.random(n) < p, col] = np.nan
df.to_csv("bank_transactions.csv", index=False)
print("bank_transactions.csv généré :", df.shape, "| taux de fraude :", df.is_fraud.mean().round(4))
