# Rapport — Épreuve technique ADRIA PFE 27
**Candidat : Agrigah Aya** — Repository : `agrigah-aya-test-adria-pfe-27`

> Pour chaque section : coller la capture d'écran indiquée, puis exporter ce document en **PDF**.

## Partie A — Préparation
- Repo GitHub privé, projet Maven multi-modules, commits toutes les 15 min (`autocommit.sh`).
- 📸 Capture : liste des commits GitHub (historique) + arborescence des modules.

## Partie B — Conception
Voir `docs/architecture.md` : diagramme de classes, schéma d'architecture, séquence.
- 📸 Capture : rendu des diagrammes (coller le code sur https://mermaid.live).

## Partie C — Micro-services fonctionnels
- account-service : REST (Swagger `http://localhost:8081/swagger-ui.html`), GraphQL (`/account-graphiql`), MCP (`/sse`).
- transaction-service : REST, GraphQL (`/transaction-graphiql`), MCP ; règles : montant > 0 et ≤ plafond, compte ACTIVE, devise identique, consultation du solde puis mise à jour, virement.
- Communication OpenFeign (`AccountClient`) + Resilience4J (`AccountGateway`) : Retry (lectures, erreurs réseau/5xx) + CircuitBreaker (seuil 50 %, fenêtre 10 appels, 10 s ouvert) + fallback `503`. Pas de retry sur l'écriture du solde (non idempotente). Les erreurs métier 4xx n'ouvrent pas le circuit.
- Les contrôleurs REST/GraphQL/MCP appellent la **même** couche `service`.
- 📸 Captures : Swagger (création de transaction OK), erreur plafond (422), compte BLOCKED (422), devise différente (422), GraphiQL, virement, panne d'account-service → 503, puis `/actuator/health` montrant le circuit breaker OPEN.

## Partie D — Services techniques
- Gateway (8080), Eureka (8761), Config (8888, `bank.transaction.max-amount=1000`).
- 📸 Captures : dashboard Eureka, `http://localhost:8888/transaction-service/default`.

## Partie E — Chatbot agentique
- `chatbot-agent` : Spring AI `ChatClient` + client MCP connecté aux serveurs MCP des deux micro-services ; mémoire de conversation ; testé avec un client REST (`POST /api/chat`) et l'interface Angular.
- 📸 Captures : conversation « solde de CUST-001 », « vire 100 EUR de CUST-001 vers CUST-002 », refus à 5000 EUR.

## Partie F — Kafka
- Publication sur `bank.transactions.created` **après commit**, clé = `accountId`, consumer qui journalise.
- 📸 Captures : log du producer, log `[EVENT RECEIVED]` du consumer.

## Partie G — Client web
- Angular (`bank-ui`) : comptes, transactions, virement, chat.
- 📸 Captures : chaque onglet.

## Partie H — Fraude (Python)
- Notebook `fraud-detection/fraud_detection.ipynb` exécuté sur `bank_transactions.csv`.
- 📸 Captures : proportion de fraudes / valeurs manquantes, métriques, matrice de confusion, courbe PR.
- Réponses aux 4 questions d'analyse : à la fin du notebook.

## Partie I — DevOps
- `Dockerfile` (unique, `--build-arg MODULE=`), `docker-compose.yml`, `.github/workflows/ci-cd.yml`.
- Réponses courtes : `docs/DEVOPS.md`.
- 📸 Captures : `docker compose ps` (tous healthy), exécution du workflow GitHub Actions.

## Limites connues / améliorations
- Keycloak (sécurité) non implémenté car hors des parties demandées.
- Mise à jour du solde + enregistrement : cohérence éventuelle assurée par compensation ; un pattern Saga / Outbox serait l'évolution naturelle.
- H2 en mémoire pour la simplicité ; PostgreSQL en production.
