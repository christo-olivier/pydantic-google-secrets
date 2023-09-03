.PHONY: build-app
.PHONY: run-app-env-file
.PHONY: run-app-env-var
.PHONY: run-app-adc

build-app:
	@echo "Building docker container..."
	docker build -t pydantic-google-secrets:latest .


run-app-env-file:
	@echo "Running docker container with env-file..."
	docker run -it --rm --env-file .env pydantic-google-secrets:latest

run-app-env-var:
	@echo "Running docker container with env-file..."
	docker run -it --rm --env my_secret_value="ENV Secret" pydantic-google-secrets:latest

run-app-adc:
	@echo "Running docker container with Google Cloud application default credentials..."
	docker run \
	-v "${HOME}/.config/gcloud/application_default_credentials.json:/gcp/config/application_default_credentials.json:ro" \
	-e GOOGLE_CLOUD_PROJECT=$$(gcloud config get-value project) \
	-e GOOGLE_APPLICATION_CREDENTIALS=/gcp/config/application_default_credentials.json \
	-it --rm pydantic-google-secrets:latest