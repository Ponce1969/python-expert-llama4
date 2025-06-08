# Makefile para gestión de entorno y CLI Llama-Groq CEO Python

REQ_FILE=requirements.txt
DEPS=\
    groq \
    python-dotenv \
    sqlalchemy \
    rich \
    "typer[all]" \
    markdown \
    weasyprint

DEV_DEPS=\
    mypy \
    ruff \
    pytest \
    pytest-cov \
    pre-commit

# 🔁 Sincroniza entorno local y Docker
install:
	uv pip install $(DEPS)

install-dev: install
	uv pip install $(DEV_DEPS)

freeze:
	uv pip freeze > $(REQ_FILE)

sync: install freeze
	@echo "✅ Dependencias sincronizadas entre UV y Docker."

init-dev: install-dev
	pre-commit install
	@echo "✅ Entorno de desarrollo configurado."

# 🐳 Contenedor
up:
	docker-compose up --build

down:
	docker-compose down

cli:
	docker-compose run --rm app python app.py

# 📆 Exports
export-md:
	python app.py export --md

export-pdf:
	python app.py export --pdf

export-all:
	python app.py export --md --pdf

export-md-docker:
	docker-compose run --rm app python app.py export --md

export-pdf-docker:
	docker-compose run --rm app python app.py export --pdf

export-all-docker:
	docker-compose run --rm app python app.py export --md --pdf

# 🗃️ Base de datos
reset-db:
	rm -f chat.db

# 🔧 Herramientas de desarrollo
lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy app.py groq_client.py chat_db.py

test:
	pytest

test-cov:
	pytest --cov=. --cov-report=term --cov-report=html

quality: lint type-check test
	echo "✅ Todas las verificaciones de calidad completadas."

ci: quality
	@echo "✅ CI verificación completada."

# 📚 Documentación
docs:
	mkdir -p docs
	python -c "import app; help(app)" > docs/app_help.txt
	python -c "import groq_client; help(groq_client)" > docs/groq_client_help.txt
	python -c "import chat_db; help(chat_db)" > docs/chat_db_help.txt
	@echo "✅ Documentación generada en el directorio docs/"
