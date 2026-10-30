package ma.bank.account.repository;

import ma.bank.account.domain.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface AccountRepository extends JpaRepository<Account, UUID> { }
