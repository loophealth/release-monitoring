
# Makefile for Alembic database migrations

.PHONY: migrate-schema

# Migrate schema with a custom message
migrate-schema:
	@read -p "Enter migration message: " msg; \
	if [ -z "$$msg" ]; then \
		echo "Migration message cannot be empty"; \
		exit 1; \
	fi; \
	alembic revision --autogenerate -m "$$msg"

apply-migrations:
	alembic upgrade head
