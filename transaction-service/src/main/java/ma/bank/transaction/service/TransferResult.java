package ma.bank.transaction.service;

import ma.bank.transaction.domain.Transaction;

public record TransferResult(Transaction debit, Transaction credit) { }
