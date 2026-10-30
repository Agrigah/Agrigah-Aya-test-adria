package ma.bank.account.web.rest;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import ma.bank.account.domain.Account;
import ma.bank.account.domain.AccountStatus;
import ma.bank.account.service.AccountService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/accounts")
public class AccountController {

    public record CreateAccountRequest(@NotBlank String customerReference,
                                       @NotBlank @Size(min = 3, max = 3) String currency,
                                       @PositiveOrZero Double initialBalance) { }
    public record StatusRequest(@NotNull AccountStatus status) { }
    public record BalanceAdjustmentRequest(@NotNull Double delta) { }

    private final AccountService service;

    public AccountController(AccountService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Account create(@Valid @RequestBody CreateAccountRequest r) {
        return service.create(r.customerReference(), r.currency(), r.initialBalance());
    }

    @GetMapping
    public List<Account> list() {
        return service.list();
    }

    @GetMapping("/{id}")
    public Account get(@PathVariable UUID id) {
        return service.get(id);
    }

    @PatchMapping("/{id}/status")
    public Account changeStatus(@PathVariable UUID id, @Valid @RequestBody StatusRequest r) {
        return service.changeStatus(id, r.status());
    }

    /** Utilisé par transaction-service (OpenFeign) pour mettre à jour le solde. */
    @PostMapping("/{id}/balance-adjustments")
    public Account adjustBalance(@PathVariable UUID id, @Valid @RequestBody BalanceAdjustmentRequest r) {
        return service.adjustBalance(id, r.delta());
    }
}
