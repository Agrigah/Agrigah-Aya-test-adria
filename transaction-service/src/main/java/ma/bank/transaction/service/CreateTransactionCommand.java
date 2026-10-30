package ma.bank.transaction.service;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import ma.bank.transaction.domain.TransactionType;

import java.math.BigDecimal;
import java.util.UUID;

/** Commande partagée par REST, GraphQL et MCP. */
public record CreateTransactionCommand(@NotNull UUID accountId,
                                       @NotNull BigDecimal amount,
                                       @NotBlank String currency,
                                       String merchantCategory,
                                       String country,
                                       TransactionType type) {
    public CreateTransactionCommand {
        if (type == null) type = TransactionType.DEBIT;
    }
}
