# Livraria API (Django + DRF + uv)

API REST de uma livraria desenvolvida com Django e Django REST Framework (DRF), gerenciada com [uv](https://docs.astral.sh/uv/) e padronizada com o linter/formatador [Ruff](https://docs.astral.sh/ruff/).

## Tecnologias Utilizadas

- [Python 3.14](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/): Gerenciador de pacotes e ambientes virtuais ultrarrápido para Python.
- [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/): Framework web e toolkit para construção de Web APIs.
- [Ruff](https://docs.astral.sh/ruff/): Linter e formatador de código Python de alta performance.
- [SQLite](https://www.sqlite.org/): Banco de dados relacional para desenvolvimento local.
- [PostgreSQL](https://www.postgresql.org/): Banco de dados relacional para produção.
- [drf-spectacular](https://drf-spectacular.readthedocs.io/): Geração de esquemas OpenAPI 3 e documentação Swagger / Redoc.
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/): Autenticação via JWT.
- [Cloudinary](https://cloudinary.com/): Armazenamento de arquivos de mídia em nuvem.
- [WhiteNoise](http://whitenoise.evans.io/): Servidor de arquivos estáticos.
- [Gunicorn](https://gunicorn.org/) / [Uvicorn](https://www.uvicorn.org/): Servidores WSGI / ASGI.
- [Django-Extensions](https://django-extensions.readthedocs.io/): Ferramentas adicionais como `shell_plus` e `graph_models`.
- [Django-Filter](https://django-filter.readthedocs.io/): Filtragem de dados em APIs REST.

---

## Instalação e Configuração

### 1. Pré-requisitos

Certifique-se de ter o `uv` instalado em seu sistema:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clonar o repositório e instalar dependências

```bash
git clone https://github.com/marrcandre/livraria-marrcandre-back.git
cd livraria-marrcandre-back

# Sincroniza o ambiente virtual (.venv) e instala todas as dependências
make sync
# ou diretamente via uv:
uv sync --all-groups
```

### 3. Configurar variáveis de ambiente

Crie o arquivo `.env` a partir do modelo `.env.example`:

```bash
cp .env.example .env
```

### 4. Executar as migrações e carregar dados iniciais

```bash
make migrate
make loaddata  # Carrega os dados de exemplo do core.json
```

### 5. Iniciar o servidor de desenvolvimento

```bash
make dev
```

A API estará disponível em: `http://127.0.0.1:8000/api/`

---

## Documentação da API

- **Swagger UI**: `http://127.0.0.1:8000/api/doc/`
- **Redoc**: `http://127.0.0.1:8000/api/redoc/`
- **Schema OpenAPI**: `http://127.0.0.1:8000/api/schema/`

---

## Comandos Úteis (Makefile)

O projeto possui um `Makefile` com atalhos para os comandos mais comuns:

### Ambiente e Dependências
- `make sync`: Sincroniza o ambiente com `uv.lock`.
- `make lock`: Atualiza o arquivo `uv.lock`.
- `make upgrade`: Atualiza todas as dependências.
- `make tree`: Exibe a árvore de dependências.
- `make add package=PACOTE`: Adiciona uma dependência de produção.
- `make add-dev package=PACOTE`: Adiciona uma dependência de desenvolvimento.
- `make remove package=PACOTE`: Remove uma dependência.

### Django
- `make dev`: Inicia o servidor com Uvicorn (`http://0.0.0.0:8000`).
- `make dev-django`: Inicia com o `runserver` padrão do Django.
- `make makemigrations`: Cria novas migrations.
- `make migrate`: Aplica as migrations pendentes.
- `make migrations`: Cria migrations, aplica e gera o diagrama de modelos (`core.png`).
- `make createsuperuser`: Cria um superusuário.
- `make shell` / `make shellp`: Abre o Django Shell / Shell Plus.
- `make graph-models`: Gera o diagrama dos modelos (`core.png`).
- `make check-django`: Valida a configuração do Django.
- `make test`: Executa a suíte de testes.
- `make loaddata`: Carrega dados de `core.json`.
- `make dumpdata`: Exporta os dados para JSON.

### Qualidade de Código (Ruff)
- `make lint`: Verifica o código com o Ruff.
- `make lint-fix`: Aplica correções automáticas de lint.
- `make format`: Formata o código com o Ruff.
- `make format-check`: Verifica a formatação sem modificar os arquivos.
- `make quality`: Executa lint e verificação de formatação.

### Deploy
- `make deploy-check`: Executa verificações de pré-deploy do Django com `--locked`.

---

## Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT).
