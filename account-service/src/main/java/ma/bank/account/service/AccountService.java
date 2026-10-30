package ma.bank.account.service;

import ma.bank.account.domain.Account;
import ma.bank.account.domain.AccountStatus;
import ma.bank.account.exception.AccountNotFoundException;
import ma.bank.account.exception.InvalidAccountOperationException;
import ma.bank.account.repository.AccountRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/** Couche service unique : appelée par REST, GraphQL et MCP. */
@Service
public class AccountService {

    private final AccountRepository repository;

    public AccountService(AccountRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public Account create(String customerReference, String currency, Double initialBalance) {
        if (currency == null || currency.length() != 3) {
            throw new InvalidAccountOperationException("Currency must be a 3-letter ISO code");
        }
        double balance = initialBalance == null ? 0.0 : initialBalance;
        if (balance < 0) {
            throw new InvalidAccountOperationException("Initial balance cannot be negative");
        }
        Account account = new Account();
        account.setCustomerReference(customerReference);
        account.setCurrency(currency.toUpperCase());
        account.setBalance(balance);
        return repository.save(account);
    }

    @Transactional(readOnly = true)
    public Account get(UUID id) {
        return repository.findById(id).orElseThrow(() -> new AccountNotFoundException(id));
    }

    @Transactional(readOnly = true)
    public List<Account> list() {
        return repository.findAll();
    }

    @Transactional
    public Account changeStatus(UUID id, AccountStatus status) {
        Account account = get(id);
        account.setStatus(status);
        return repository.save(account);
    }

    /** Ajoute (delta > 0) ou retire (delta < 0) un montant au solde. */
    @Transactional
    public Account adjustBalance(UUID id, double delta) {
        Account account = get(id);
        if (account.getStatus() != AccountStatus.ACTIVE) {
            throw new InvalidAccountOperationException("Account is blocked");
        }
        double newBalance = Math.round((account.getBalance() + delta) * 100.0) / 100.0;
        if (newBalance < 0) {
            throw new InvalidAccountOperationException("Insufficient balance");
        }
        account.setBalance(newBalance);
        return repository.save(account);
    }
}
