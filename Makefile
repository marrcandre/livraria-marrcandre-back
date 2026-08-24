.DEFAULT_GOAL := help

.PHONY: help \
	dev dev-django sync lock upgrade tree \
	add add-dev remove \
	createsuperuser makemigrations migrate graph-models migrations \
	shell shellp check-django test loaddata dumpdata cria-api \
	lint lint-fix format format-check quality \
	python python-install python-pin \
	collectstatic deploy-check

# ==============================================================================
# Help
# ==============================================================================

help:
	@echo "Livraria - comandos disponíveis:"
	@echo ""
	@echo "Ambiente e dependências:"
	@echo "  make sync                  Sincroniza o ambiente com uv.lock"
	@echo "  make lock                  Atualiza o uv.lock"
	@echo "  make upgrade               Atualiza todas as dependências"
	@echo "  make tree                  Mostra a árvore de dependências"
	@echo "  make add package=PACOTE    Adiciona uma dependência"
	@echo "  make add-dev package=PACOTE Adiciona dependência de desenvolvimento"
	@echo "  make remove package=PACOTE Remove uma dependência"
	@echo ""
	@echo "Django:"
	@echo "  make dev                   Inicia o servidor de desenvolvimento (uvicorn)"
	@echo "  make dev-django            Inicia o servidor de desenvolvimento (base)"
	@echo "  make check-django          Verifica o projeto Django"
	@echo "  make createsuperuser       Cria um superusuário"
	@echo "  make makemigrations        Cria novas migrations"
	@echo "  make migrate               Executa as migrations"
	@echo "  make migrations            Cria, aplica e gera o diagrama das migrations"
	@echo "  make graph-models          Gera o diagrama dos modelos"
	@echo "  make shell                 Abre o Django Shell"
	@echo "  make shellp                Abre o Django Shell Plus"
	@echo "  make test                  Executa os testes"
	@echo "  make loaddata              Carrega os dados de core.json"
	@echo "  make dumpdata              Exporta os dados para JSON"
	@echo "  make cria-api              Executa o script de criação da API"
	@echo "  make collectstatic         Coleta os arquivos estáticos"
	@echo ""
	@echo "Qualidade de código:"
	@echo "  make lint                  Verifica o código com Ruff"
	@echo "  make lint-fix              Corrige problemas automaticamente"
	@echo "  make format                Formata o código"
	@echo "  make format-check          Verifica a formatação"
	@echo "  make quality               Executa lint e verificação de formatação"
	@echo ""
	@echo "Python:"
	@echo "  make python                Lista versões do Python disponíveis"
	@echo "  make python-install version=VERSÃO"
	@echo "                             Instala uma versão do Python"
	@echo "  make python-pin version=VERSÃO"
	@echo "                             Define a versão do Python para o projeto"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy-check          Executa verificações para deploy"
	@echo ""
	@echo "Exemplos:"
	@echo "  make add package=django-filter"
	@echo "  make add-dev package=pytest"
	@echo "  make python-pin version=3.14"


# ==============================================================================
# Ambiente e dependências
# ==============================================================================

sync:
	uv sync --all-groups

lock:
	uv lock

upgrade:
	uv lock --upgrade
	uv sync --all-groups

tree:
	uv tree

add:
	uv add $(package)

add-dev:
	uv add --dev $(package)

remove:
	uv remove $(package)


# ==============================================================================
# Django
# ==============================================================================

dev-django:
	uv run python manage.py runserver 127.0.0.1:8000

dev:
	uv run uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --reload

check-django:
	uv run python manage.py check

createsuperuser:
	uv run python manage.py createsuperuser

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

graph-models:
	uv run python manage.py graph_models -S -g -o core.png core

migrations: makemigrations migrate graph-models

shell:
	uv run python manage.py shell

shellp:
	uv run python manage.py shell_plus

test:
	uv run python manage.py test

loaddata:
	uv run python manage.py loaddata core.json

dumpdata:
	uv run python manage.py dumpdata --indent 2

cria-api:
	uv run python ./scripts/cria_api.py

collectstatic:
	uv run python manage.py collectstatic --noinput


# ==============================================================================
# Ruff
# ==============================================================================

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

quality: lint format-check


# ==============================================================================
# Python
# ==============================================================================

python:
	uv python list

python-install:
	uv python install $(version)

python-pin:
	uv python pin $(version)


# ==============================================================================
# Deploy
# ==============================================================================

deploy-check:
	uv sync --locked
	uv run python manage.py check --deploy
