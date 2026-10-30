package ma.bank.account.config;

import ma.bank.account.domain.AccountStatus;
import ma.bank.account.repository.AccountRepository;
import ma.bank.account.service.AccountService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Données de démonstration pour les tests (H2 en mémoire). */
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seed(AccountRepository repository, AccountService service) {
        return args -> {
            if (repository.count() > 0) return;
            service.create("CUST-001", "EUR", 5000.0);
            service.create("CUST-002", "EUR", 2000.0);
            service.create("CUST-003", "MAD", 30000.0);
            var blocked = service.create("CUST-004", "EUR", 100.0);
            service.changeStatus(blocked.getId(), AccountStatus.BLOCKED);
        };
    }
}
