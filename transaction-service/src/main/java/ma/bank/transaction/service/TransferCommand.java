package ma.bank.transaction.service;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;
import java.util.UUID;

public record TransferCommand(@NotNull UUID fromAccountId, @NotNull UUID toAccountId,
                              @NotNull BigDecimal amount, @NotBlank String currency) { }
