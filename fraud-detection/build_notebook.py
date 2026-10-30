import nbformat as nbf
nb = nbf.v4.new_notebook()
md = lambda s: nb.cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: nb.cells.append(nbf.v4.new_code_cell(s))

md("# Partie H — Détection de fraude bancaire (classification binaire)\n"
   "Pipeline scikit-learn : imputation → encodage → normalisation → modèle. "
   "Le prétraitement est ajusté **uniquement sur le train**. Le **test** ne sert ni à entraîner, ni à choisir le modèle, ni à choisir le seuil.")

code('''import os, subprocess, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (precision_score, recall_score, f1_score, confusion_matrix,
                             average_precision_score, classification_report,
                             precision_recall_curve, ConfusionMatrixDisplay)
RANDOM_STATE = 42''')

md("## 1. Chargement des données")
code('''CSV = "bank_transactions.csv"
if not os.path.exists(CSV):
    print("⚠️ bank_transactions.csv introuvable -> génération d'un jeu SYNTHÉTIQUE pour tester le notebook.")
    subprocess.run([sys.executable, "generate_sample_data.py"], check=True)
df = pd.read_csv(CSV)
print(df.shape)
df.head()''')

md("## 2. Proportion de fraudes et valeurs manquantes")
code('''print("Proportion de fraudes :", round(df["is_fraud"].mean() * 100, 2), "%")
print(df["is_fraud"].value_counts())
print()
missing = df.isna().sum().to_frame("manquantes")
missing["%"] = (missing["manquantes"] / len(df) * 100).round(2)
missing''')

md("## 3. Séparation entraînement / test stratifiée\nLa stratification conserve la même proportion de fraudes dans les deux ensembles (classes déséquilibrées).")
code('''ID_COLS = ["transaction_id", "account_id"]          # 4. identifiants exclus des variables explicatives
TARGET = "is_fraud"
X = df.drop(columns=ID_COLS + [TARGET])
y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
print("Fraude train :", round(y_train.mean()*100, 2), "% | test :", round(y_test.mean()*100, 2), "%")''')

md("## 5. Pipeline de prétraitement (imputation, encodage, normalisation)")
code('''numeric = ["amount", "hour", "transactions_last_24h", "average_amount_last_7d"]
categorical = ["country", "merchant_category"]

preprocess = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                      ("scaler", StandardScaler())]), numeric),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
])

def make_model(clf):
    return Pipeline([("prep", preprocess), ("clf", clf)])

candidates = {
    "LogisticRegression": make_model(LogisticRegression(class_weight="balanced", max_iter=1000)),
    "RandomForest": make_model(RandomForestClassifier(n_estimators=200, min_samples_leaf=5,
                                                      class_weight="balanced_subsample",
                                                      n_jobs=-1, random_state=RANDOM_STATE)),
}''')

md("## 6. Choix du modèle (validation croisée stratifiée sur le TRAIN uniquement)")
code('''cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_scores = {}
for name, model in candidates.items():
    s = cross_val_score(model, X_train, y_train, cv=cv, scoring="average_precision")
    cv_scores[name] = s.mean()
    print(f"{name:20s} average precision (CV) = {s.mean():.3f} ± {s.std():.3f}")
best_name = max(cv_scores, key=cv_scores.get)
print("\\nModèle retenu :", best_name)''')

md("### Choix du seuil de décision\nLe seuil est choisi sur des **prédictions hors-échantillon (out-of-fold) du train**, jamais sur le test. "
   "Critère : maximiser le F1 de la classe fraude.")
code('''oof_proba = cross_val_predict(candidates[best_name], X_train, y_train, cv=cv, method="predict_proba")[:, 1]
prec, rec, thr = precision_recall_curve(y_train, oof_proba)
f1 = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-12, None)
THRESHOLD = float(thr[np.argmax(f1)])
print(f"Seuil retenu (max F1 sur validation croisée du train) : {THRESHOLD:.3f}")

# Effet d'une variation du seuil (sur les prédictions out-of-fold du train)
rows = []
for t in [0.9, 0.7, 0.5, 0.3, 0.2, 0.1]:
    pred = (oof_proba >= t).astype(int)
    rows.append({"seuil": t, "précision": precision_score(y_train, pred, zero_division=0),
                 "rappel": recall_score(y_train, pred), "nb alertes": int(pred.sum())})
pd.DataFrame(rows).round(3)''')

md("## 7. Entraînement final et évaluation sur le test (une seule fois)")
code('''model = candidates[best_name].fit(X_train, y_train)      # prétraitement ajusté sur le train uniquement
proba = model.predict_proba(X_test)[:, 1]
pred = (proba >= THRESHOLD).astype(int)

print(f"Précision (classe fraude) : {precision_score(y_test, pred, zero_division=0):.3f}")
print(f"Rappel    (classe fraude) : {recall_score(y_test, pred):.3f}")
print(f"F1-score  (classe fraude) : {f1_score(y_test, pred):.3f}")
print(f"Average precision         : {average_precision_score(y_test, proba):.3f}")
print(f"(référence : un modèle aléatoire aurait AP ≈ {y_test.mean():.3f})\\n")
print(classification_report(y_test, pred, target_names=["légitime", "fraude"], zero_division=0))
cm = confusion_matrix(y_test, pred)
print("Matrice de confusion [[TN FP],[FN TP]] :\\n", cm)''')

code('''fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ConfusionMatrixDisplay(cm, display_labels=["légitime", "fraude"]).plot(ax=ax[0], colorbar=False)
ax[0].set_title(f"Matrice de confusion (seuil={THRESHOLD:.2f})")
p, r, _ = precision_recall_curve(y_test, proba)
ax[1].plot(r, p); ax[1].set_xlabel("Rappel"); ax[1].set_ylabel("Précision")
ax[1].set_title(f"Courbe précision-rappel (AP={average_precision_score(y_test, proba):.3f})")
plt.tight_layout(); plt.savefig("results.png", dpi=130); plt.show()''')

md("""## Questions d'analyse

**1. Pourquoi l'accuracy seule est-elle insuffisante ?**
Les classes sont très déséquilibrées : avec ~2 % de fraudes, un modèle qui répond toujours « légitime » obtient ~98 % d'accuracy tout en ne détectant **aucune** fraude. L'accuracy est dominée par la classe majoritaire ; il faut regarder la précision, le rappel, le F1 et l'average precision de la classe fraude.

**2. Quel compromis entre faux positifs et fraudes non détectées ?**
Un faux positif (transaction légitime bloquée) dégrade l'expérience client et charge les équipes d'analyse ; une fraude non détectée (faux négatif) coûte directement de l'argent et nuit à la confiance/réputation. Améliorer le rappel (moins de fraudes manquées) se fait au prix de la précision (plus de fausses alertes), et inversement. Le bon équilibre dépend du **coût relatif** des deux erreurs et de la capacité de traitement des alertes.

**3. Effet possible d'une diminution du seuil de décision ?**
Plus de transactions sont classées « fraude » : le **rappel augmente** (moins de fraudes manquées) mais la **précision diminue** et le nombre d'alertes (faux positifs) augmente (voir le tableau des seuils ci-dessus).

**4. Pourquoi privilégier une validation temporelle sur des données bancaires réelles ?**
En production, le modèle prédit le **futur** à partir du passé. Un découpage aléatoire mélange des transactions de périodes différentes : fuite d'information (les mêmes comptes/schémas apparaissent dans train et test, des variables historiques calculées avec des données postérieures), et surestimation des performances. La fraude évolue (dérive de concept) : une validation temporelle (entraîner sur le passé, tester sur la période suivante) reproduit les conditions réelles et mesure la robustesse à cette dérive.""")

nbf.write(nb, "fraud_detection.ipynb")
