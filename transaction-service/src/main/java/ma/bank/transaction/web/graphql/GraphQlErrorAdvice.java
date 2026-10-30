package ma.bank.transaction.web.graphql;

import graphql.GraphQLError;
import graphql.GraphqlErrorBuilder;
import ma.bank.transaction.exception.*;
import org.springframework.graphql.data.method.annotation.GraphQlExceptionHandler;
import org.springframework.graphql.execution.ErrorType;
import org.springframework.web.bind.annotation.ControllerAdvice;

@ControllerAdvice
public class GraphQlErrorAdvice {

    @GraphQlExceptionHandler
    public GraphQLError businessRule(BusinessRuleException ex) {
        return error(ErrorType.BAD_REQUEST, ex);
    }

    @GraphQlExceptionHandler
    public GraphQLError accountNotFound(AccountNotFoundException ex) {
        return error(ErrorType.NOT_FOUND, ex);
    }

    @GraphQlExceptionHandler
    public GraphQLError transactionNotFound(TransactionNotFoundException ex) {
        return error(ErrorType.NOT_FOUND, ex);
    }

    @GraphQlExceptionHandler
    public GraphQLError unavailable(AccountServiceUnavailableException ex) {
        return error(ErrorType.INTERNAL_ERROR, ex);
    }

    private GraphQLError error(ErrorType type, RuntimeException ex) {
        return GraphqlErrorBuilder.newError().errorType(type).message(ex.getMessage()).build();
    }
}
