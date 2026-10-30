package ma.bank.transaction.web.graphql;

import ma.bank.transaction.domain.Transaction;
import ma.bank.transaction.service.CreateTransactionCommand;
import ma.bank.transaction.service.TransactionService;
import ma.bank.transaction.service.TransferCommand;
import ma.bank.transaction.service.TransferResult;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Controller
public class TransactionGraphQlController {

    private final TransactionService service;

    public TransactionGraphQlController(TransactionService service) {
        this.service = service;
    }

    @QueryMapping
    public List<Transaction> transactions(@Argument UUID accountId) {
        return service.list(accountId);
    }

    @QueryMapping
    public Transaction transactionById(@Argument UUID id) {
        return service.get(id);
    }

    @MutationMapping
    public Transaction createTransaction(@Argument("input") CreateTransactionCommand input) {
        return service.create(input);
    }

    @MutationMapping
    public TransferResult transfer(@Argument UUID fromAccountId, @Argument UUID toAccountId,
                                   @Argument BigDecimal amount, @Argument String currency) {
        return service.transfer(new TransferCommand(fromAccountId, toAccountId, amount, currency));
    }
}
