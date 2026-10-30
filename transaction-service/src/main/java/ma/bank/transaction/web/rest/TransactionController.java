package ma.bank.transaction.web.rest;

import jakarta.validation.Valid;
import ma.bank.transaction.domain.Transaction;
import ma.bank.transaction.service.CreateTransactionCommand;
import ma.bank.transaction.service.TransactionService;
import ma.bank.transaction.service.TransferCommand;
import ma.bank.transaction.service.TransferResult;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api")
public class TransactionController {

    private final TransactionService service;

    public TransactionController(TransactionService service) {
        this.service = service;
    }

    @PostMapping("/transactions")
    @ResponseStatus(HttpStatus.CREATED)
    public Transaction create(@Valid @RequestBody CreateTransactionCommand cmd) {
        return service.create(cmd);
    }

    @GetMapping("/transactions/{id}")
    public Transaction get(@PathVariable UUID id) {
        return service.get(id);
    }

    @GetMapping("/transactions")
    public List<Transaction> list(@RequestParam(required = false) UUID accountId) {
        return service.list(accountId);
    }

    @PostMapping("/transfers")
    @ResponseStatus(HttpStatus.CREATED)
    public TransferResult transfer(@Valid @RequestBody TransferCommand cmd) {
        return service.transfer(cmd);
    }
}
