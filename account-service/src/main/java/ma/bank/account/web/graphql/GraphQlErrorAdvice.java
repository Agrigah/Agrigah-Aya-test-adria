package ma.bank.account.web.graphql;

import graphql.GraphQLError;
import graphql.GraphqlErrorBuilder;
import ma.bank.account.exception.AccountNotFoundException;
import ma.bank.account.exception.InvalidAccountOperationException;
import org.springframework.graphql.data.method.annotation.GraphQlExceptionHandler;
import org.springframework.graphql.execution.ErrorType;
import org.springframework.web.bind.annotation.ControllerAdvice;

@ControllerAdvice
public class GraphQlErrorAdvice {

    @GraphQlExceptionHandler
    public GraphQLError notFound(AccountNotFoundException ex) {
        return GraphqlErrorBuilder.newError().errorType(ErrorType.NOT_FOUND).message(ex.getMessage()).build();
    }

    @GraphQlExceptionHandler
    public GraphQLError invalid(InvalidAccountOperationException ex) {
        return GraphqlErrorBuilder.newError().errorType(ErrorType.BAD_REQUEST).message(ex.getMessage()).build();
    }
}
