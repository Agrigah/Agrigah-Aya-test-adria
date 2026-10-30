package ma.bank.transaction.service;

import ma.bank.transaction.client.AccountDto;
import ma.bank.transaction.client.AccountGateway;
import ma.bank.transaction.config.BankTransactionProperties;
import ma.bank.transaction.domain.Transaction;
import ma.bank.transaction.domain.TransactionType;
import ma.bank.transaction.exception.BusinessRuleException;
import ma.bank.transaction.exception.TransactionNotFoundException;
import ma.bank.transaction.messaging.TransactionCreatedEvent;
import ma.bank.transaction.repository.TransactionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.UUID;

/** Couche service unique : appelée par REST, GraphQL et MCP. Contient toutes les règles métier. */
@Service
public class TransactionService {

    private static final Logger log = LoggerFactory.getLogger(TransactionService.class);

    private final TransactionRepository repository;
    private final AccountGateway accounts;
    private final BankTransactionProperties properties;
    private final ApplicationEventPublisher events;

    public TransactionService(TransactionRepository repository, AccountGateway accounts,
                              BankTransactionProperties properties, ApplicationEventPublisher events) {
        this.repository = repository;
        this.accounts = accounts;
        this.properties = properties;
        this.events = events;
    }

    @Transactional
    public Transaction create(CreateTransactionCommand cmd) {
        BigDecimal amount = validateAmount(cmd.amount());
        AccountDto account = accounts.getAccount(cmd.accountId());      // consultation du solde (Feign)
        checkAccountUsable(account, cmd.currency());
        if (cmd.type() == TransactionType.DEBIT) {
            checkSufficientFunds(account, amount);
        }
        Transaction tx = persist(cmd.accountId(), amount, cmd.currency(), cmd.merchantCategory(),
                cmd.country(), cmd.type());
        BigDecimal delta = cmd.type() == TransactionType.DEBIT ? amount.negate() : amount;
        accounts.adjustBalance(cmd.accountId(), delta.doubleValue());   // mise à jour du solde (Feign)
        return tx;
    }

    /** Virement : débit du compte source puis crédit du compte destination, avec compensation. */
    @Transactional
    public TransferResult transfer(TransferCommand cmd) {
        BigDecimal amount = validateAmount(cmd.amount());
        if (cmd.fromAccountId().equals(cmd.toAccountId())) {
            throw new BusinessRuleException("Source and destination accounts must be different");
        }
        AccountDto from = accounts.getAccount(cmd.fromAccountId());
        AccountDto to = accounts.getAccount(cmd.toAccountId());
        checkAccountUsable(from, cmd.currency());
        checkAccountUsable(to, cmd.currency());
        checkSufficientFunds(from, amount);

        Transaction debit = persist(from.id(), amount, cmd.currency(), "TRANSFER", null, TransactionType.DEBIT);
        Transaction credit = persist(to.id(), amount, cmd.currency(), "TRANSFER", null, TransactionType.CREDIT);

        accounts.adjustBalance(from.id(), amount.negate().doubleValue());
        try {
            accounts.adjustBalance(to.id(), amount.doubleValue());
        } catch (RuntimeException e) {
            // compensation : on rend l'argent au compte source avant de faire échouer le virement
            try {
                accounts.adjustBalance(from.id(), amount.doubleValue());
            } catch (RuntimeException ce) {
                log.error("COMPENSATION FAILED for transfer from {} amount {} : manual action required",
                        from.id(), amount, ce);
            }
            throw e;
        }
        return new TransferResult(debit, credit);
    }

    @Transactional(readOnly = true)
    public Transaction get(UUID id) {
        return repository.findById(id).orElseThrow(() -> new TransactionNotFoundException(id));
    }

    @Transactional(readOnly = true)
    public List<Transaction> list(UUID accountId) {
        return accountId == null
                ? repository.findAll(Sort.by(Sort.Direction.DESC, "createdAt"))
                : repository.findByAccountIdOrderByCreatedAtDesc(accountId);
    }

    // ------------------------------------------------------------------ règles métier

    private BigDecimal validateAmount(BigDecimal amount) {
        if (amount == null || amount.signum() <= 0) {
            throw new BusinessRuleException("Amount must be strictly positive");
        }
        BigDecimal scaled = amount.setScale(2, RoundingMode.HALF_UP);
        if (scaled.compareTo(properties.getMaxAmount()) > 0) {
            throw new BusinessRuleException("Amount exceeds the maximum allowed: " + properties.getMaxAmount());
        }
        return scaled;
    }

    private void checkAccountUsable(AccountDto account, String currency) {
        if (!"ACTIVE".equals(account.status())) {
            throw new BusinessRuleException("Account " + account.id() + " is not active");
        }
        if (!account.currency().equalsIgnoreCase(currency)) {
            throw new BusinessRuleException("Transaction currency " + currency
                    + " does not match account currency " + account.currency());
        }
    }

    private void checkSufficientFunds(AccountDto account, BigDecimal amount) {
        if (BigDecimal.valueOf(account.balance()).compareTo(amount) < 0) {
            throw new BusinessRuleException("Insufficient balance: " + account.balance());
        }
    }

    private Transaction persist(UUID accountId, BigDecimal amount, String currency, String merchantCategory,
                                String country, TransactionType type) {
        Instant now = Instant.now().truncatedTo(ChronoUnit.MILLIS);
        Transaction tx = repository.save(new Transaction(accountId, amount, currency.toUpperCase(),
                merchantCategory, country, type, now));
        // publié sur Kafka seulement APRÈS commit (@TransactionalEventListener AFTER_COMMIT)
        events.publishEvent(new TransactionCreatedEvent(UUID.randomUUID(), TransactionCreatedEvent.TYPE,
                tx.getId(), accountId, amount, tx.getCurrency(), now));
        return tx;
    }
}
