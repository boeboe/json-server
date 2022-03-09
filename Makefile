# General release info
DOCKER_ACCOUNT := boeboe
APP_NAME       := json-server
APP_VERSION    := 1.0.1

ENV_FILE := $(shell pwd)/.env
DOMAIN   := tetrate.io
SERVER   := server
CLIENT   := client
CERT_DIR := $(shell pwd)/certs

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build: ## Build container
	docker build --no-cache -t $(DOCKER_ACCOUNT)/$(APP_NAME) .

run: ## Run container
	docker run -it --rm -p 8080:8080 \
		--env-file=${ENV_FILE} \
		--volume=${CERT_DIR}:/certs \
		--name=$(APP_NAME) $(DOCKER_ACCOUNT)/$(APP_NAME)

shell: ## Login with bash in running container
	docker exec -it $(APP_NAME) /bin/bash

stop: ## Stop and remove a running container
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

publish: ## Tag and publish container
	docker tag $(DOCKER_ACCOUNT)/$(APP_NAME) $(DOCKER_ACCOUNT)/$(APP_NAME):${APP_VERSION}
	docker tag $(DOCKER_ACCOUNT)/$(APP_NAME) $(DOCKER_ACCOUNT)/$(APP_NAME):latest
	docker push $(DOCKER_ACCOUNT)/$(APP_NAME):${APP_VERSION}
	docker push $(DOCKER_ACCOUNT)/$(APP_NAME):latest

release: build publish ## Make a full release

certificates: ## Generate certificates
	openssl req -x509 -sha512 -nodes -days 7300 -newkey rsa:4096 -subj '/O=Tetrate/CN=${DOMAIN}' \
		-keyout ${CERT_DIR}/${DOMAIN}.key -out ${CERT_DIR}/${DOMAIN}.crt

	openssl req -out ${CERT_DIR}/${SERVER}.${DOMAIN}.csr -newkey rsa:4096 -sha512 -nodes \
		-keyout ${CERT_DIR}/${SERVER}.${DOMAIN}.key -subj "/CN=${SERVER}.${DOMAIN}/O=server organization"
	openssl x509 -req -sha512 -days 3650 -CA ${CERT_DIR}/${DOMAIN}.crt -CAkey ${CERT_DIR}/${DOMAIN}.key \
		-set_serial 0 -in ${CERT_DIR}/${SERVER}.${DOMAIN}.csr -out ${CERT_DIR}/${SERVER}.${DOMAIN}.crt

	openssl req -out ${CERT_DIR}/${CLIENT}.${DOMAIN}.csr -newkey rsa:4096 -sha512 -nodes \
		-keyout ${CERT_DIR}/${CLIENT}.${DOMAIN}.key -subj "/CN=${CLIENT}.${DOMAIN}/O=client organization"
	openssl x509 -req -sha512 -days 3650 -CA ${CERT_DIR}/${DOMAIN}.crt -CAkey ${CERT_DIR}/${DOMAIN}.key \
		-set_serial 1 -in ${CERT_DIR}/${CLIENT}.${DOMAIN}.csr -out ${CERT_DIR}/${CLIENT}.${DOMAIN}.crt

curl_none: ## Curl to HTTP Server
	curl --resolve server.${DOMAIN}:8080:127.0.0.1 \
		http://server.${DOMAIN}:8080 -v

curl_tls: ## Curl to HTTPS Server with TLS
	curl --resolve server.${DOMAIN}:8080:127.0.0.1 \
			 --cacert ${CERT_DIR}/${DOMAIN}.crt \
			 https://server.${DOMAIN}:8080 -v

curl_mtls: ## Curl to HTTPS Server with Mutual TLS
	curl --resolve server.${DOMAIN}:8080:127.0.0.1 \
			 --cacert ${CERT_DIR}/${DOMAIN}.crt \
			 --cert ${CERT_DIR}/client.${DOMAIN}.crt \
			 --key ${CERT_DIR}/client.${DOMAIN}.key \
			 https://server.${DOMAIN}:8080 -v
