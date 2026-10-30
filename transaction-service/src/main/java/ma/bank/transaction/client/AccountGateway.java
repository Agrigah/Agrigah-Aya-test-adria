package ma.bank.transaction.client;

import feign.FeignException;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import ma.bank.transaction.exception.AccountNotFoundException;
import ma.bank.transaction.exception.AccountServiceUnavailableException;
import ma.bank.transaction.exception.BusinessRuleException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.UUID;

/**
 * Façade résiliente autour du client Feign.
 * - Lecture : Retry (erreurs réseau/5xx uniquement) puis CircuitBreaker, avec fallback.
 * - Écriture (mise à jour du solde) : CircuitBreaker seulement, JAMAIS de retry (non idempotent).
 * Les erreurs métier 4xx n'ouvrent pas le circuit (voir application.yml).
 */
@Component
public class AccountGateway {

    private static final Logger log = LoggerFactory.getLogger(AccountGateway.class);
    private final AccountClient client;

    public AccountGateway(AccountClient client) {
        this.client = client;
    }

    @Retry(name = "accountService", fallbackMethod = "getAccountFallback")
    @CircuitBreaker(name = "accountService")
    public AccountDto getAccount(UUID id) {
        return client.getAccount(id);
    }

    public AccountDto getAccountFallback(UUID id, Throwable t) {
        throw translate(id, t);
    }

    @CircuitBreaker(name = "accountService", fallbackMethod = "adjustBalanceFallback")
    public AccountDto adjustBalance(UUID id, double delta) {
        return client.adjustBalance(id, new AccountClient.BalanceAdjustment(delta));
    }

    public AccountDto adjustBalanceFallback(UUID id, double delta, Throwable t) {
        throw translate(id, t);
    }

    private RuntimeException translate(UUID id, Throwable t) {
        if (t instanceof BusinessRuleException || t instanceof AccountNotFoundException) {
            return (RuntimeException) t;
        }
        if (t instanceof FeignException.NotFound) {
            return new AccountNotFoundException(id);
        }
        if (t instanceof FeignException.Conflict || t instanceof FeignException.BadRequest) {
            return new BusinessRuleException("Account service rejected the operation: " + t.getMessage());
        }
        log.warn("account-service unavailable for account {} : {}", id, t.toString());
        return new AccountServiceUnavailableException(
                "Account service is temporarily unavailable, please retry later", t);
    }
}
