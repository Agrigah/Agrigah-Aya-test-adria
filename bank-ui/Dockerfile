FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build -- --configuration production \
    && mkdir /out \
    && if [ -d dist/bank-ui/browser ]; then cp -r dist/bank-ui/browser/. /out/; else cp -r dist/bank-ui/. /out/; fi

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /out /usr/share/nginx/html
EXPOSE 80
