package ma.bank.transaction.messaging;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/** Format de l'événement publié sur bank.transactions.created. */
public record TransactionCreatedEvent(UUID eventId, String eventType, UUID transactionId, UUID accountId,
                                      BigDecimal amount, String currency, Instant occurredAt) {
    public static final String TYPE = "TransactionCreated";
}
