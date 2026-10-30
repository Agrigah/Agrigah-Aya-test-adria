package ma.bank.transaction.config;

import ma.bank.transaction.mcp.TransactionTools;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class McpServerConfig {

    @Bean
    public ToolCallbackProvider transactionToolCallbacks(TransactionTools tools) {
        return MethodToolCallbackProvider.builder().toolObjects(tools).build();
    }
}
