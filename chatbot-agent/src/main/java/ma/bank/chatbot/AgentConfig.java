package ma.bank.chatbot;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AgentConfig {

    private static final String SYSTEM_PROMPT = """
            You are a banking assistant for a bank. You can consult accounts, create accounts, block or
            activate accounts, record transactions and make transfers between accounts, ONLY by using the
            provided tools (they are connected to the account-service and transaction-service MCP servers).
            Rules:
            - Never invent account ids, balances or transactions: call a tool to get them.
            - If the user refers to an account by customer reference (e.g. CUST-001), list the accounts
              first to find its UUID.
            - Before a transfer or a transaction, make sure the user gave the amount, the currency and the
              account(s). If something is missing, ask one short question.
            - If a tool returns an error (limit exceeded, blocked account, wrong currency, insufficient
              balance), explain it clearly to the user in plain language.
            - Answer in the language of the user, concisely.
            """;

    @Bean
    public ChatMemory chatMemory() {
        return MessageWindowChatMemory.builder().maxMessages(20).build();
    }

    @Bean
    public ChatClient bankChatClient(ChatClient.Builder builder, ToolCallbackProvider mcpTools,
                                     ChatMemory chatMemory) {
        return builder
                .defaultSystem(SYSTEM_PROMPT)
                .defaultToolCallbacks(mcpTools)   // outils découverts sur les serveurs MCP des micro-services
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
    }
}
