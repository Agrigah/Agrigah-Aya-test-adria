"""Génère docs/RAPPORT.pdf. Usage: python3 docs/build_report.py
Pour ajouter une capture manquante : la déposer dans docs/screenshots/ avec le nom indiqué dans le cadre
gris du PDF, puis relancer le script."""
import os
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether, Preformatted)

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS, IMG = os.path.join(HERE, "screenshots"), os.path.join(HERE, "img")
OUT = os.path.join(HERE, "RAPPORT.pdf")
NAVY = colors.HexColor("#0b3d6b")
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, fontSize=16, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=NAVY, fontSize=12, spaceBefore=8, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=10, leading=14, spaceAfter=5)
CAP = ParagraphStyle("CAP", parent=P, fontSize=8.5, textColor=colors.HexColor("#555555"), alignment=1)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=7.6, leading=9.6, backColor=colors.HexColor("#f4f6f8"), borderPadding=4)
W = A4[0] - 4*cm
story = []

def p(t): story.append(Paragraph(t, P))
def b(items):
    for t in items: story.append(Paragraph("• " + t, ParagraphStyle("b", parent=P, leftIndent=12, firstLineIndent=-8, spaceAfter=2)))
    story.append(Spacer(1, 4))
def code(t): story.append(Preformatted(t.strip("\n"), CODE)); story.append(Spacer(1, 6))
def fig(path, caption, maxh=11*cm, folder=SHOTS):
    f = os.path.join(folder, path)
    if os.path.exists(f):
        w, h = PILImage.open(f).size
        sc = min(W / w, maxh / h)
        story.append(KeepTogether([Image(f, w*sc, h*sc), Paragraph(caption, CAP), Spacer(1, 8)]))
    else:
        print('capture absente (ignorée):', path)

# ---- Couverture
story += [Spacer(1, 5*cm), Paragraph("Épreuve technique de sélection — ADRIA PFE 27", ParagraphStyle("T", parent=H1, fontSize=22, leading=28, alignment=1)),
          Paragraph("Architecture micro-services, IA et développement full-stack", ParagraphStyle("S", parent=P, fontSize=13, alignment=1)),
          Spacer(1, 1.2*cm), Paragraph("<b>Candidate :</b> Agrigah Aya", ParagraphStyle("c", parent=P, alignment=1, fontSize=12)),
          Paragraph("<b>Dépôt :</b> github.com/Agrigah/Agrigah-Aya-test-adria", ParagraphStyle("c", parent=P, alignment=1)),
          Paragraph("<b>Date :</b> 30 octobre 2026", ParagraphStyle("c", parent=P, alignment=1)), PageBreak()]

# ---- A
story.append(Paragraph("Partie A — Préparation", H1))
b(["Dépôt GitHub (privé pendant l'épreuve, rendu public à la fin) ; projet Maven multi-modules : <font face='Courier'>discovery-service, config-service, account-service, transaction-service, notification-consumer, chatbot-agent, gateway-service</font>.",
   "Commits réguliers toutes les 15 minutes : script <font face='Courier'>autocommit.sh</font> (add + commit + push, puis pause de 900 s).",
   "Google Sheet rempli séparément (hors rapport)."])
fig("github_commits.png", "Historique des commits GitHub (intervalles de 15 min)")
fig("arborescence_modules.png", "Arborescence des modules du projet Maven")

# ---- B
story.append(Paragraph("Partie B — Conception et architecture", H1))
p("Le diagramme de classes reprend le modèle minimal demandé (Account, Transaction) auquel s'ajoutent le type de transaction (DEBIT/CREDIT, nécessaire aux virements), l'événement Kafka et les classes de communication (Feign + Resilience4J).")
fig("diagramme_classes.png", "Figure B1 — Diagramme de classes", folder=IMG)
fig("schema_architecture.png", "Figure B2 — Schéma d'architecture", folder=IMG)
p("<b>Séparation des couches</b> (dans chaque micro-service métier) : <font face='Courier'>domain/ → repository/ → service/ ← web/rest, web/graphql, mcp/</font>. Les contrôleurs REST, GraphQL et les outils MCP appellent la <b>même couche service</b>.")

# ---- C
story.append(PageBreak()); story.append(Paragraph("Partie C — Micro-services fonctionnels", H1))
p("<b>account-service (8081)</b> et <b>transaction-service (8082)</b> exposent chacun trois connecteurs : REST (Swagger), GraphQL (GraphiQL) et MCP (SSE).")
story.append(Paragraph("Règles métier implémentées (transaction-service)", H2))
b(["Montant strictement positif et inférieur ou égal au plafond (<font face='Courier'>bank.transaction.max-amount=1000</font>, lu depuis le config-service).",
   "Le compte doit exister et être <b>ACTIVE</b>.", "La devise de la transaction doit être celle du compte.",
   "Consultation du solde avant chaque transaction (solde suffisant pour un débit), puis mise à jour du solde après enregistrement.",
   "Virement d'un compte vers un autre : deux écritures liées (DEBIT sur la source, CREDIT sur la destination, catégorie TRANSFER)."])
story.append(Paragraph("OpenFeign + Resilience4J", H2))
p("<font face='Courier'>AccountClient</font> (Feign) est appelé via <font face='Courier'>AccountGateway</font> : <b>Retry</b> sur les lectures (erreurs réseau/5xx), <b>CircuitBreaker</b> (seuil 50 %, fenêtre de 10 appels, 10 s ouvert) et <b>fallback</b> renvoyant 503. Pas de retry sur l'ajustement du solde (opération non idempotente). Les erreurs métier 4xx n'ouvrent pas le circuit.")
story.append(Paragraph("Tests effectués", H2))
fig("ui_comptes.png", "C1 — Liste des comptes (REST account-service via la gateway) : statuts ACTIVE/BLOCKED, création de compte, blocage/activation")
fig("ui_transaction.png", "C2 — Enregistrement d'une transaction : « Transaction enregistrée » (règles : montant > 0 et ≤ plafond, compte actif, même devise, solde suffisant)", maxh=8*cm)
fig("rest_transactions_json.png", "C3 — Réponse JSON REST de GET /api/transactions (id, accountId, amount, currency, merchantCategory, country, type, createdAt)", maxh=12*cm)
fig("ui_virement.png", "C4 — Formulaire de virement entre comptes (CUST-007 → CUST-006, 100 MAD)", maxh=7*cm)
fig("ui_historique_virements.png", "C5 — Historique : le virement produit deux écritures TRANSFER (DEBIT sur la source, CREDIT sur la destination) ; les soldes des comptes sont mis à jour")
fig("swagger_graphql.png", "C6 — Swagger / GraphiQL (REST et GraphQL)")
fig("erreur_plafond_422.png", "C7 — Rejet d'un montant supérieur au plafond (422)")
fig("resilience_503.png", "C8 — account-service arrêté : fallback 503 puis circuit breaker OPEN (/actuator/health)")

# ---- D
story.append(Paragraph("Partie D — Services techniques", H1))
b(["<b>Spring Cloud Gateway</b> (8080) : point d'entrée unique, routage <font face='Courier'>lb://</font> via Eureka.",
   "<b>Eureka</b> (8761) : découverte de services.",
   "<b>Config Service</b> (8888) : partage <font face='Courier'>bank.transaction.max-amount=1000</font>."])
fig("eureka.png", "Dashboard Eureka avec les services enregistrés")
fig("config_service.png", "http://localhost:8888/transaction-service/default (paramètre max-amount=1000)")

# ---- E
story.append(Paragraph("Partie E — Chatbot agentique", H1))
p("Le module <font face='Courier'>chatbot-agent</font> (8084) utilise un <b>ChatClient Spring AI</b> relié à un LLM compatible OpenAI et à un <b>client MCP</b> connecté aux serveurs MCP d'account-service et de transaction-service ; les outils découverts (consulter/créer/bloquer un compte, enregistrer une transaction, virement) sont fournis au modèle. Une mémoire de conversation (20 messages) est activée. Le prompt système interdit d'inventer des identifiants ou des soldes.")
fig("ui_assistant_ia.png", "E1 — Onglet « Assistant IA » de l'interface Angular (appelle POST /api/chat vers le chatbot-agent)", maxh=7*cm)
fig("chat_solde.png", "E2 — Conversation : « Quel est le solde de CUST-001 ? »")
fig("chat_virement.png", "E3 — Conversation : demande de virement via les outils MCP")

# ---- F
story.append(Paragraph("Partie F — Communication asynchrone avec Kafka", H1))
b(["Après la persistance réussie d'une transaction (publication <b>après commit</b>), événement <font face='Courier'>TransactionCreated</font> publié dans <font face='Courier'>bank.transactions.created</font>.",
   "Clé du message : <font face='Courier'>accountId</font> (ordre garanti par compte).",
   "<font face='Courier'>notification-consumer</font> (8083) consomme le topic et journalise <font face='Courier'>[EVENT RECEIVED]</font> sans modifier les données bancaires."])
code('''{ "eventId":"UUID", "eventType":"TransactionCreated", "transactionId":"UUID",
  "accountId":"UUID", "amount":250.00, "currency":"EUR", "occurredAt":"2026-01-15T10:30:00Z" }''')
fig("kafka_producer_log.png", "Log du producer (transaction-service)")
fig("kafka_consumer_log.png", "Log [EVENT RECEIVED] du notification-consumer")

# ---- G
story.append(Paragraph("Partie G — Client web Angular", H1))
p("Application Angular <font face='Courier'>bank-ui</font> (port 4200) avec quatre onglets : <b>Comptes</b> (liste, création, blocage/activation, historique filtrable), <b>Transaction</b>, <b>Virement</b> et <b>Assistant IA</b>. Les captures C1, C2, C4, C5 et E1 ci-dessus illustrent chaque écran.")

# ---- H
story.append(PageBreak()); story.append(Paragraph("Partie H — Détection de fraude (Python)", H1))
p("Notebook : <font face='Courier'>fraud-detection/fraud_detection.ipynb</font>. Pipeline scikit-learn : imputation (médiane / valeur la plus fréquente), encodage one-hot des catégories, normalisation des numériques ; identifiants exclus ; séparation 80/20 stratifiée ; prétraitement ajusté <b>uniquement sur le train</b> ; modèle choisi par validation croisée stratifiée sur le train ; seuil choisi sur des prédictions hors-échantillon du train (le test sert une seule fois, à l'évaluation).")
p("<b>Important :</b> les résultats ci-dessous ont été obtenus sur le <b>jeu synthétique</b> généré par <font face='Courier'>generate_sample_data.py</font> (20 000 lignes), le fichier officiel <font face='Courier'>bank_transactions.csv</font> n'étant pas disponible lors de la rédaction. Les chiffres sont donc indicatifs et doivent être régénérés avec le vrai fichier.")
t = Table([["Indicateur (classe fraude, test)", "Valeur"], ["Proportion de fraudes", "3,11 %"], ["Modèle retenu (AP en CV)", "Régression logistique (0,258)"],
           ["Seuil de décision", "0,856"], ["Précision", "0,257"], ["Rappel", "0,282"], ["F1-score", "0,269"], ["Average precision", "0,262 (aléatoire ≈ 0,031)"],
           ["Matrice de confusion [[TN FP],[FN TP]]", "[[3775, 101], [89, 35]]"]], colWidths=[9*cm, 7*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 9)]))
story += [t, Spacer(1, 8)]
fig("fraud_results.png", "H1 — Matrice de confusion et courbe précision-rappel (jeu synthétique)", maxh=7*cm, folder=IMG)
story.append(Paragraph("Questions d'analyse", H2))
p("<b>1. Pourquoi l'accuracy seule est-elle insuffisante ?</b> Avec ~3 % de fraudes, prédire « légitime » partout donne ~97 % d'accuracy sans détecter aucune fraude. Il faut regarder précision, rappel, F1 et average precision de la classe fraude.")
p("<b>2. Compromis faux positifs / fraudes non détectées ?</b> Un faux positif bloque ou alerte un client honnête (coût d'image et de traitement) ; une fraude non détectée est une perte financière directe. On cherche l'équilibre selon les coûts respectifs.")
p("<b>3. Effet d'une diminution du seuil ?</b> Le rappel augmente (plus de fraudes détectées) mais la précision baisse (plus de fausses alertes, donc plus de charge pour les analystes).")
p("<b>4. Pourquoi une validation temporelle ?</b> Les fraudes évoluent dans le temps : un découpage aléatoire laisse fuiter le futur dans l'entraînement et surestime les performances. Entraîner sur le passé et tester sur le futur reproduit les conditions réelles.")

# ---- I
story.append(Paragraph("Partie I — DevOps", H1))
b(["<b>Dockerfile unique</b> pour tous les modules (<font face='Courier'>--build-arg MODULE=...</font>), build multi-étapes (Maven puis JRE 21), utilisateur non-root.",
   "<b>docker-compose.yml</b> : Kafka, Eureka, Config, account, transaction, consumer, chatbot, gateway ; <font face='Courier'>healthcheck</font> + <font face='Courier'>depends_on: service_healthy</font>.",
   "<b>GitHub Actions</b> (<font face='Courier'>.github/workflows/ci-cd.yml</font>) : compilation, tests (<font face='Courier'>mvn verify</font>), construction d'images (matrice par module), publication sur GHCR, déploiement schématique via SSH + docker compose."])
story.append(Paragraph("Réponses courtes", H2))
p("<b>Secrets vs configuration.</b> La configuration (ports, URLs, plafond, topics) n'est pas sensible : versionnée, propre à chaque environnement (config-service). Les secrets (clé du LLM, mots de passe, token de registre, clé SSH) ne sont jamais committés ni dans l'image : injectés à l'exécution (<font face='Courier'>.env</font> ignoré par git, GitHub Actions secrets, Docker/Kubernetes secrets ou Vault) et renouvelables sans reconstruire l'image.")
p("<b>Démarrage, disponibilité, vitalité.</b> Actuator expose <font face='Courier'>/actuator/health/liveness</font> (process vivant, sinon redémarrage) et <font face='Courier'>/actuator/health/readiness</font> (prêt à recevoir du trafic, dépendances OK) ; une <i>startup probe</i> laisse le temps au démarrage. Dans Compose : <font face='Courier'>healthcheck</font> et <font face='Courier'>service_healthy</font>.")
p("<b>Logs, métriques, traces.</b> Logs structurés sur la sortie standard avec identifiant de corrélation, centralisés (ELK/Loki) ; métriques Micrometer/Actuator exposées à Prometheus et visualisées dans Grafana ; traces distribuées via OpenTelemetry/Micrometer Tracing vers Zipkin ou Jaeger.")
p("<b>Stratégie de rollback.</b> Images immuables taguées par SHA de commit : revenir en arrière = redéployer le tag précédent (<font face='Courier'>TAG=&lt;sha précédent&gt; docker compose up -d</font>). Pour réduire le risque : déploiement progressif (blue/green ou canary) et retour automatique si readiness échoue. Les migrations de base doivent rester rétro-compatibles.")
fig("docker_compose_ps.png", "I1 — docker compose ps : Kafka démarré et « healthy » (port 29092 exposé pour les services lancés en local)", maxh=3*cm)
fig("docker_desktop.png", "I2 — Docker Desktop : projet agrigah-aya-test-adria-pfe-27 en cours d'exécution", maxh=2*cm)
fig("github_actions.png", "Exécution du workflow GitHub Actions")

story.append(Paragraph("Limites connues", H2))
b(["Keycloak (authentification/autorisations) cité dans l'architecture cible mais <b>non implémenté</b>.",
   "Cohérence solde/transaction assurée par compensation ; un pattern Saga/Outbox serait l'évolution naturelle.",
   "H2 en mémoire pour la simplicité ; PostgreSQL recommandé en production."])

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(2*cm, 1.2*cm, "Agrigah Aya — Épreuve technique ADRIA PFE 27"); c.drawRightString(A4[0]-2*cm, 1.2*cm, f"Page {d.page}"); c.restoreState()
SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=2*cm, title="Rapport — Épreuve ADRIA PFE 27", author="Agrigah Aya").build(story, onFirstPage=footer, onLaterPages=footer)
print("OK", OUT)
