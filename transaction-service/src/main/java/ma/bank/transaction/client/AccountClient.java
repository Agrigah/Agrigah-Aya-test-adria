package ma.bank.transaction.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.UUID;

/** Client OpenFeign vers account-service (résolu via Eureka). */
@FeignClient(name = "account-service")
public interface AccountClient {

    record BalanceAdjustment(double delta) { }

    @GetMapping("/api/accounts/{id}")
    AccountDto getAccount(@PathVariable("id") UUID id);

    @PostMapping("/api/accounts/{id}/balance-adjustments")
    AccountDto adjustBalance(@PathVariable("id") UUID id, @RequestBody BalanceAdjustment body);
}
