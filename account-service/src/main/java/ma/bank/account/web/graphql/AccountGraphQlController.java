package ma.bank.account.web.graphql;

import ma.bank.account.domain.Account;
import ma.bank.account.domain.AccountStatus;
import ma.bank.account.service.AccountService;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

import java.util.List;
import java.util.UUID;

@Controller
public class AccountGraphQlController {

    private final AccountService service;

    public AccountGraphQlController(AccountService service) {
        this.service = service;
    }

    @QueryMapping
    public List<Account> accounts() {
        return service.list();
    }

    @QueryMapping
    public Account accountById(@Argument UUID id) {
        return service.get(id);
    }

    @MutationMapping
    public Account createAccount(@Argument String customerReference, @Argument String currency,
                                 @Argument Double initialBalance) {
        return service.create(customerReference, currency, initialBalance);
    }

    @MutationMapping
    public Account blockAccount(@Argument UUID id) {
        return service.changeStatus(id, AccountStatus.BLOCKED);
    }

    @MutationMapping
    public Account activateAccount(@Argument UUID id) {
        return service.changeStatus(id, AccountStatus.ACTIVE);
    }
}
