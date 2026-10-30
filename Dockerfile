# Un seul Dockerfile pour TOUS les micro-services :
#   docker build --build-arg MODULE=account-service -t account-service .
FROM maven:3.9-eclipse-temurin-21 AS build
ARG MODULE
WORKDIR /app
COPY . .
RUN mvn -B -q -pl ${MODULE} -am package -DskipTests

FROM eclipse-temurin:21-jre
ARG MODULE
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 1001 appuser
WORKDIR /app
COPY --from=build /app/${MODULE}/target/*.jar app.jar
USER appuser
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
