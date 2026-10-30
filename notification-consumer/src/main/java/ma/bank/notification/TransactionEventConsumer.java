package ma.bank.notification;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/** Consomme bank.transactions.created et journalise l'événement. Ne modifie AUCUNE donnée bancaire. */
@Component
public class TransactionEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(TransactionEventConsumer.class);
    private final ObjectMapper objectMapper;

    public TransactionEventConsumer(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @KafkaListener(topics = "bank.transactions.created", groupId = "notification-consumer")
    public void onMessage(ConsumerRecord<String, String> record) {
        try {
            JsonNode e = objectMapper.readTree(record.value());
            log.info("[EVENT RECEIVED] type={} eventId={} transactionId={} accountId={} amount={} {} occurredAt={} "
                            + "(key={}, partition={}, offset={})",
                    e.path("eventType").asText(), e.path("eventId").asText(), e.path("transactionId").asText(),
                    e.path("accountId").asText(), e.path("amount").asText(), e.path("currency").asText(),
                    e.path("occurredAt").asText(), record.key(), record.partition(), record.offset());
        } catch (Exception ex) {
            log.warn("Unreadable event (offset {}): {}", record.offset(), record.value());
        }
    }
}
