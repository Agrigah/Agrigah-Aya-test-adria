# Partie B — Conception et architecture (Mermaid)

## Diagramme de classes
```mermaid
classDiagram
    direction LR
    class Account {
        +UUID id
        +String customerReference
        +AccountStatus status
        +String currency
        +double balance
    }
    class AccountStatus {
        <<enumeration>>
        ACTIVE
        BLOCKED
    }
    class Transaction {
        +UUID id
        +UUID accountId
        +BigDecimal amount
        +String currency
        +String merchantCategory
        +String country
        +Instant createdAt
        +TransactionType type
    }
    class TransactionType {
        <<enumeration>>
        DEBIT
        CREDIT
    }
    class TransactionCreatedEvent {
        +UUID eventId
        +String eventType
        +UUID transactionId
        +UUID accountId
        +BigDecimal amount
        +String currency
        +Instant occurredAt
    }
    class AccountService {
        +create()
        +get()
        +list()
        +changeStatus()
        +adjustBalance()
    }
    class TransactionService {
        +create()
        +transfer()
        +get()
        +list()
    }
    class AccountGateway {
        +getAccount() Retry + CircuitBreaker
        +adjustBalance() CircuitBreaker
    }
    class AccountClient {
        <<Feign>>
    }
    Account --> AccountStatus
    Transaction --> TransactionType
    Account "1" <.. "0..*" Transaction : accountId (référence logique)
    TransactionService --> AccountGateway
    AccountGateway --> AccountClient
    AccountClient ..> AccountService : HTTP (via Eureka)
    TransactionService ..> TransactionCreatedEvent : publie après commit
```

## Schéma d'architecture
```mermaid
flowchart LR
    subgraph Clients
        UI[Angular :4200]
        REST[Client REST / Telegram / Discord]
    end
    GW[Spring Cloud Gateway :8080]
    EU[(Eureka Discovery :8761)]
    CFG[Config Service :8888<br/>bank.transaction.max-amount=1000]
    subgraph Services metier
        ACC[account-service :8081<br/>REST + GraphQL + MCP]
        TX[transaction-service :8082<br/>REST + GraphQL + MCP]
    end
    BOT[chatbot-agent :8084<br/>Spring AI + client MCP]
    LLM[[LLM OpenAI-compatible]]
    K[(Kafka<br/>bank.transactions.created)]
    NC[notification-consumer :8083<br/>journalise l'evenement]

    UI --> GW
    REST --> GW
    GW --> ACC
    GW --> TX
    GW --> BOT
    TX -- "OpenFeign + Resilience4J" --> ACC
    BOT -- "MCP SSE (tools)" --> ACC
    BOT -- "MCP SSE (tools)" --> TX
    BOT --> LLM
    TX -- "cle = accountId" --> K
    K --> NC
    ACC -.-> EU
    TX -.-> EU
    GW -.-> EU
    BOT -.-> EU
    CFG -.-> EU
    ACC -.-> CFG
    TX -.-> CFG
    GW -.-> CFG
```

## Séparation des couches (par micro-service métier)
```mermaid
flowchart TB
    R[web/rest] --> S[service]
    G[web/graphql] --> S
    M[mcp tools] --> S
    S --> RP[repository]
    RP --> D[domain]
    S --> D
```

## Séquence : création d'une transaction
```mermaid
sequenceDiagram
    participant C as Client
    participant GW as Gateway
    participant T as transaction-service
    participant A as account-service
    participant K as Kafka
    participant N as notification-consumer
    C->>GW: POST /api/transactions
    GW->>T: route (lb://TRANSACTION-SERVICE)
    T->>T: montant > 0 et <= max-amount (config)
    T->>A: GET /api/accounts/{id} (Feign + Retry + CircuitBreaker)
    A-->>T: compte (statut, devise, solde)
    T->>T: compte ACTIVE, devise identique, solde suffisant
    T->>T: sauvegarde Transaction
    T->>A: POST /balance-adjustments (Feign + CircuitBreaker)
    A-->>T: nouveau solde
    T->>T: commit
    T-)K: TransactionCreated (cle = accountId)
    K-)N: consomme et journalise
    T-->>C: 201 Created
```
