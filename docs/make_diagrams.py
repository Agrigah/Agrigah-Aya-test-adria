"""Génère docs/img/architecture.png et docs/img/classes.png (matplotlib, sans dépendance externe)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def box(ax, x, y, w, h, text, fc="#e8f0fa", ec="#0b3d6b", fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1", fc=fc, ec=ec, lw=1.3))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal")

def arrow(ax, p, q, label="", style="->", color="#333", ls="-", off=(0, 0.08)):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=style, color=color, lw=1.2, ls=ls))
    if label:
        ax.text((p[0]+q[0])/2 + off[0], (p[1]+q[1])/2 + off[1], label, fontsize=6.5, ha="center", color=color)

# ---------- Architecture ----------
fig, ax = plt.subplots(figsize=(11, 6.2)); ax.set_xlim(0, 11); ax.set_ylim(0, 6.2); ax.axis("off")
box(ax, 0.2, 4.9, 1.9, 0.9, "Angular\n:4200", "#fff3d6", "#b7791f", bold=True)
box(ax, 0.2, 3.7, 1.9, 0.9, "Client REST /\nTelegram / Discord", "#fff3d6", "#b7791f")
box(ax, 3.0, 4.2, 1.9, 1.0, "Spring Cloud\nGateway :8080", "#d9f2e3", "#2f855a", bold=True)
box(ax, 3.0, 0.3, 1.9, 0.8, "Eureka :8761", "#eee", "#555")
box(ax, 5.2, 0.3, 2.3, 0.8, "Config Service :8888\nmax-amount=1000", "#eee", "#555")
box(ax, 5.9, 4.6, 2.4, 1.0, "account-service :8081\nREST+GraphQL+MCP", "#e8f0fa", "#0b3d6b", bold=True)
box(ax, 5.9, 2.6, 2.4, 1.0, "transaction-service\n:8082 REST+GraphQL+MCP", "#e8f0fa", "#0b3d6b", bold=True)
box(ax, 3.0, 2.4, 1.9, 1.0, "chatbot-agent :8084\nSpring AI + MCP", "#f3e8fa", "#6b46c1", bold=True)
box(ax, 0.2, 2.4, 1.9, 1.0, "LLM\n(OpenAI-compatible)", "#f3e8fa", "#6b46c1")
box(ax, 9.0, 2.6, 1.8, 1.0, "Kafka\nbank.transactions\n.created", "#fde8e8", "#c53030", bold=True)
box(ax, 9.0, 0.9, 1.8, 0.9, "notification-\nconsumer :8083", "#fde8e8", "#c53030")
arrow(ax, (2.1, 5.3), (3.0, 4.9)); arrow(ax, (2.1, 4.2), (3.0, 4.5))
arrow(ax, (4.9, 4.9), (6.0, 5.1)); arrow(ax, (4.9, 4.4), (6.0, 3.3))
arrow(ax, (3.95, 4.2), (3.95, 3.4), "/api/chat", off=(0.45, 0))
arrow(ax, (3.0, 2.9), (2.1, 2.9))
arrow(ax, (4.9, 3.0), (6.0, 4.7), "MCP (SSE)", color="#6b46c1", off=(-0.5, 0.0))
arrow(ax, (4.9, 2.8), (6.0, 2.9), "MCP (SSE)", color="#6b46c1", off=(0, -0.25))
arrow(ax, (7.05, 3.6), (7.05, 4.6), "OpenFeign + Resilience4J", color="#2f855a", off=(1.15, 0))
arrow(ax, (8.3, 3.1), (9.0, 3.1), "clé=accountId", color="#c53030", off=(0, 0.2))
arrow(ax, (9.9, 2.6), (9.9, 1.8), color="#c53030")
for p in [(7.0, 4.6), (7.0, 2.6), (4.0, 4.2)]:
    pass
ax.text(5.5, 1.35, "Enregistrement Eureka + configuration centralisée (tous les services)", fontsize=7, style="italic", ha="center", color="#555")
ax.set_title("Schéma d'architecture — plateforme bancaire micro-services", fontsize=11, weight="bold")
plt.savefig("img/architecture.png", dpi=170, bbox_inches="tight"); plt.close()

# ---------- Classes ----------
fig, ax = plt.subplots(figsize=(11, 6)); ax.set_xlim(0, 11); ax.set_ylim(-0.4, 6); ax.axis("off")
def cls(x, y, w, title, lines, fc="#e8f0fa"):
    h = 0.45 + 0.27*len(lines)
    ax.add_patch(FancyBboxPatch((x, y-h), w, h, boxstyle="square,pad=0", fc=fc, ec="#0b3d6b", lw=1.3))
    ax.plot([x, x+w], [y-0.35, y-0.35], color="#0b3d6b", lw=1)
    ax.text(x+w/2, y-0.18, title, ha="center", va="center", fontsize=8.5, weight="bold")
    for i, l in enumerate(lines):
        ax.text(x+0.1, y-0.55-0.27*i, l, fontsize=7.2, va="center", family="monospace")
    return (x, y-h, w, h)
cls(0.2, 5.8, 3.0, "Account", ["+ id : UUID", "+ customerReference : String", "+ status : AccountStatus", "+ currency : String", "+ balance : double"])
cls(0.2, 3.6, 3.0, "«enum» AccountStatus", ["ACTIVE", "BLOCKED"], "#fff3d6")
cls(4.2, 5.8, 3.1, "Transaction", ["+ id : UUID", "+ accountId : UUID", "+ amount : BigDecimal", "+ currency : String", "+ merchantCategory : String", "+ country : String", "+ createdAt : Instant", "+ type : TransactionType"])
cls(4.2, 3.0, 3.1, "«enum» TransactionType", ["DEBIT", "CREDIT"], "#fff3d6")
cls(8.0, 5.8, 2.9, "TransactionCreatedEvent", ["+ eventId : UUID", "+ eventType : String", "+ transactionId : UUID", "+ accountId : UUID", "+ amount : BigDecimal", "+ currency : String", "+ occurredAt : Instant"], "#fde8e8")
cls(0.2, 2.2, 3.0, "AccountService", ["+ create()", "+ get() / list()", "+ changeStatus()", "+ adjustBalance()"], "#d9f2e3")
cls(4.2, 1.6, 3.1, "TransactionService", ["+ create()", "+ transfer()", "+ get() / list()"], "#d9f2e3")
cls(8.0, 2.6, 2.9, "AccountGateway", ["Retry + CircuitBreaker", "+ getAccount()", "+ adjustBalance()"], "#d9f2e3")
cls(8.0, 0.9, 2.9, "AccountClient «Feign»", ["GET /api/accounts/{id}", "POST balance-adjustments"], "#f3e8fa")
ax.annotate("", xy=(1.7, 3.62), xytext=(1.7, 4.0), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.annotate("", xy=(5.75, 3.02), xytext=(5.75, 3.19), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.annotate("", xy=(4.2, 4.6), xytext=(3.2, 4.6), arrowprops=dict(arrowstyle="->", lw=1.1, ls="--"))
ax.text(3.7, 4.68, "accountId", fontsize=6.5, ha="center")
ax.annotate("", xy=(8.0, 4.3), xytext=(7.3, 4.3), arrowprops=dict(arrowstyle="->", lw=1.1, ls="--"))
ax.text(7.65, 4.38, "événement", fontsize=6.5, ha="center")
ax.annotate("", xy=(8.0, 1.9), xytext=(7.3, 1.1), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.annotate("", xy=(9.45, 0.95), xytext=(9.45, 1.34), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.set_title("Diagramme de classes (modèle minimal + couches service/client)", fontsize=11, weight="bold")
plt.savefig("img/classes.png", dpi=170, bbox_inches="tight"); plt.close()
print("ok")
