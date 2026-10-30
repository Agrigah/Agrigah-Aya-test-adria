package ma.bank.transaction.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import java.math.BigDecimal;

/** bank.transaction.max-amount : fourni par le config-service (valeur 1000). */
@ConfigurationProperties(prefix = "bank.transaction")
public class BankTransactionProperties {
    private BigDecimal maxAmount = new BigDecimal("1000");

    public BigDecimal getMaxAmount() { return maxAmount; }
    public void setMaxAmount(BigDecimal maxAmount) { this.maxAmount = maxAmount; }
}
