# stage 1: build the react app to plain static files
FROM node:22-alpine AS build

WORKDIR /app

# package files first, so npm ci is cached when only code changes
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm ci

COPY src/frontend/ .
RUN npm run build


# stage 2: nginx with the built app inside
FROM nginx:alpine

RUN apk add --no-cache openssl

# self-signed TLS certificate (browser will warn, it is ok for local use)
RUN mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/transcendence.key \
    -out /etc/nginx/ssl/transcendence.crt \
    -subj "/C=PL/ST=Mazowieckie/L=Warsaw/O=42/OU=Transcendence/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# only the result of the build, no node and no sources
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 443
