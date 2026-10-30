package ma.bank.transaction.mcp;

import ma.bank.transaction.domain.Transaction;
import ma.bank.transaction.domain.TransactionType;
import ma.bank.transaction.service.CreateTransactionCommand;
import ma.bank.transaction.service.TransactionService;
import ma.bank.transaction.service.TransferCommand;
import ma.bank.transaction.service.TransferResult;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

/** Outils MCP exposés par transaction-service : même couche service que REST et GraphQL. */
@Component
public class TransactionTools {

    private final TransactionService service;

    public TransactionTools(TransactionService service) {
        this.service = service;
    }

    @Tool(description = "Record a bank transaction on an account. A DEBIT withdraws money, a CREDIT adds money. "
            + "The amount must be > 0 and <= the configured maximum, and the currency must match the account.")
    public Transaction createTransaction(
            @ToolParam(description = "UUID of the account") String accountId,
            @ToolParam(description = "Amount, strictly positive") double amount,
            @ToolParam(description = "3-letter ISO currency, same as the account") String currency,
            @ToolParam(description = "Merchant category, e.g. GROCERY, TRAVEL, ELECTRONICS", required = false) String merchantCategory,
            @ToolParam(description = "2-letter country code, e.g. MA, FR", required = false) String country,
            @ToolParam(description = "DEBIT or CREDIT, defaults to DEBIT", required = false) String type) {
        TransactionType t = type == null || type.isBlank() ? TransactionType.DEBIT
                : TransactionType.valueOf(type.toUpperCase());
        return service.create(new CreateTransactionCommand(UUID.fromString(accountId),
                BigDecimal.valueOf(amount), currency, merchantCategory, country, t));
    }

    @Tool(description = "Transfer money from one account to another account (same currency on both accounts)")
    public TransferResult transferFunds(
            @ToolParam(description = "UUID of the source account") String fromAccountId,
            @ToolParam(description = "UUID of the destination account") String toAccountId,
            @ToolParam(description = "Amount, strictly positive") double amount,
            @ToolParam(description = "3-letter ISO currency") String currency) {
        return service.transfer(new TransferCommand(UUID.fromString(fromAccountId),
                UUID.fromString(toAccountId), BigDecimal.valueOf(amount), currency));
    }

    @Tool(description = "List the transactions of an account, most recent first; omit accountId for all transactions")
    public List<Transaction> listTransactions(
            @ToolParam(description = "UUID of the account", required = false) String accountId) {
        return service.list(accountId == null || accountId.isBlank() ? null : UUID.fromString(accountId));
    }

    @Tool(description = "Get one transaction by its UUID")
    public Transaction getTransaction(@ToolParam(description = "UUID of the transaction") String transactionId) {
        return service.get(UUID.fromString(transactionId));
    }
}
