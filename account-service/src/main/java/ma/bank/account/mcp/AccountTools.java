package ma.bank.account.mcp;

import ma.bank.account.domain.Account;
import ma.bank.account.domain.AccountStatus;
import ma.bank.account.service.AccountService;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.UUID;

/** Outils MCP exposés par account-service : même couche service que REST et GraphQL. */
@Component
public class AccountTools {

    private final AccountService service;

    public AccountTools(AccountService service) {
        this.service = service;
    }

    @Tool(description = "List all bank accounts with id, customer reference, status, currency and balance")
    public List<Account> listAccounts() {
        return service.list();
    }

    @Tool(description = "Get one bank account (status, currency, balance) by its UUID")
    public Account getAccount(@ToolParam(description = "UUID of the account") String accountId) {
        return service.get(UUID.fromString(accountId));
    }

    @Tool(description = "Create a new bank account for a customer")
    public Account createAccount(@ToolParam(description = "Customer reference, e.g. CUST-010") String customerReference,
                                 @ToolParam(description = "3-letter ISO currency, e.g. EUR") String currency,
                                 @ToolParam(description = "Initial balance, 0 if unknown") double initialBalance) {
        return service.create(customerReference, currency, initialBalance);
    }

    @Tool(description = "Block a bank account")
    public Account blockAccount(@ToolParam(description = "UUID of the account") String accountId) {
        return service.changeStatus(UUID.fromString(accountId), AccountStatus.BLOCKED);
    }

    @Tool(description = "Activate (unblock) a bank account")
    public Account activateAccount(@ToolParam(description = "UUID of the account") String accountId) {
        return service.changeStatus(UUID.fromString(accountId), AccountStatus.ACTIVE);
    }
}
