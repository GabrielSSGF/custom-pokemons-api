# 🎮 Pokémon API — Projeto de Casa

API assíncrona construída com **FastAPI**, **asyncpg** (Postgres), **Redis** e **aiohttp**.  
Parte do código já está pronta (infraestrutura, modelos, esqueleto das rotas).  
**Você deve implementar os handlers das rotas e a criação das tabelas.**

---

## 📁 Estrutura do Projeto

```
pokemon_api/
├── app/
│   ├── core/
│   │   ├── config.py          # Configurações via variáveis de ambiente
│   │   ├── db.py              # DBManager — asyncpg
│   │   ├── cache.py           # CacheManager — Redis async
│   │   └── http_client.py     # AiohttpWrapper — requisições externas
│   ├── models/
│   │   └── pokemon.py         # PokemonCreation, PokemonUpdate, PokemonResponse
│   ├── routers/
│   │   ├── pokemons.py        # Rotas /pokemons (PokéAPI externa)
│   │   └── custom_pokemons.py # Rotas /pokemons/custom (Postgres + Redis)
│   └── main.py                # App FastAPI + lifespan (startup/shutdown)
├── tests/
│   ├── conftest.py            # Fixtures e mocks compartilhados
│   ├── test_pokemons.py       # Testes das rotas externas
│   └── test_custom_pokemons.py# Testes das rotas customizadas
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

---

## 🚀 Como Iniciar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) instalados.
- [Poetry](https://python-poetry.org/docs/#installation) (para desenvolvimento local sem Docker).

---

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` se quiser mudar usuário/senha do banco. Os valores padrão já funcionam com o `docker-compose.yml`.

---

### 2. Subir todos os serviços

```bash
docker compose up --build
```

Isso irá subir:

| Serviço    | Porta local | Descrição                        |
|------------|-------------|----------------------------------|
| `app`      | `8000`      | FastAPI (reload automático)      |
| `postgres` | `5432`      | Banco de dados PostgreSQL 16     |
| `redis`    | `6379`      | Cache Redis 7                    |

A API estará disponível em: **http://localhost:8000**  
Documentação interativa: **http://localhost:8000/docs**

---

### 3. Verificar saúde da API

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

### 4. Parar os serviços

```bash
docker compose down
```

Para remover também os volumes (apaga dados do Postgres):

```bash
docker compose down -v
```

---

## 🛠️ Desenvolvimento Local (sem Docker)

```bash
# Instalar dependências
poetry install

# Ativar o ambiente virtual
poetry shell

# Subir apenas o Postgres e o Redis via Docker
docker compose up postgres redis -d

# Rodar a API localmente
uvicorn app.main:app --reload
```

---

## 🧪 Rodando os Testes

Os testes **não precisam de Docker** — usam mocks no lugar do banco e do Redis.

```bash
# Com Poetry
poetry run pytest -v

# Dentro do container
docker compose exec app pytest -v
```

---

## 📋 Rotas da API

### Rotas Externas (PokéAPI)

#### `GET /pokemons`

Busca uma lista de Pokémons diretamente na [PokéAPI](https://pokeapi.co/).

- **Não usa cache nem banco de dados.**
- Deve delegar a requisição ao `AiohttpWrapper`.
- Pode aceitar query params opcionais como `limit` e `offset`.

**Resposta esperada:** lista de Pokémons no formato retornado pela PokéAPI.

---

#### `GET /pokemons/{name}`

Busca um Pokémon pelo nome na PokéAPI, **com cache Redis**.

- Verifica primeiro no Redis pela chave `pokemon:{name}`.
- Se encontrar no cache → retorna imediatamente (sem chamar a PokéAPI).
- Se não encontrar → faz GET na PokéAPI, salva no cache com TTL, retorna o resultado.
- Se a PokéAPI retornar 404 → retorne HTTP **404**.

---

### Rotas Customizadas (Postgres + Redis)

#### `POST /pokemons/custom`

Cria um Pokémon customizado e persiste no Postgres.

- **Body:** `PokemonCreation` (name, type, hp, attack, defense).
- Retorna o registro criado com o `id` gerado.
- Se o nome já existir → HTTP **409 Conflict**.
- **Status de sucesso:** `201 Created`.

---

#### `GET /pokemons/custom`

Lista todos os Pokémons customizados do banco de dados.

- **Não usa cache** — sempre consulta o Postgres.
- Retorna lista vazia `[]` quando não houver registros.

---

#### `GET /pokemons/custom/{name}`

Busca um Pokémon customizado pelo nome, **com cache Redis**.

- Verifica primeiro no Redis pela chave `custom:{name}`.
- Se encontrar → retorna sem bater no banco.
- Se não encontrar no cache → busca no Postgres, salva no cache, retorna.
- Se não existir no banco → HTTP **404**.

---

#### `PATCH /pokemons/custom/{name}`

Atualiza parcialmente um Pokémon customizado no Postgres **e invalida/atualiza o cache**.

- **Body:** `PokemonUpdate` (todos os campos opcionais: type, hp, attack, defense).
- Atualiza apenas os campos enviados no body.
- Após atualizar no banco → deve atualizar ou deletar a entrada em `custom:{name}` no Redis.
- Se o Pokémon não existir → HTTP **404**.

---

## 🗄️ Schema do Banco de Dados

Você deve implementar o método `create_tables()` em `app/core/db.py`.  
Abaixo está um exemplo de schema para a tabela de Pokémons customizados:

```sql
CREATE TABLE IF NOT EXISTS custom_pokemons (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) UNIQUE NOT NULL,
    type       VARCHAR(50)  NOT NULL,
    hp         INTEGER      NOT NULL DEFAULT 0,
    attack     INTEGER      NOT NULL DEFAULT 0,
    defense    INTEGER      NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

Você pode executar esse SQL diretamente no Postgres:

```bash
docker compose exec postgres psql -U pokemon -d pokemon_db
```

Ou chamar `await db.create_tables()` no lifespan do `main.py` após implementar o método.

---

## 🏗️ Classes Prontas (não precisam ser modificadas)

### `AiohttpWrapper` (`app/core/http_client.py`)

| Método | Descrição |
|--------|-----------|
| `await client.get(url, **kwargs)` | GET assíncrono, retorna JSON |
| `await client.post(url, params, **kwargs)` | POST assíncrono com body JSON |
| `await client.patch(url, params, **kwargs)` | PATCH assíncrono com body JSON |

O cliente já está disponível em `request.app.state.http_client`.

### `DBManager` (`app/core/db.py`)

| Método | Descrição |
|--------|-----------|
| `await db.fetch(query, *args)` | Retorna lista de registros |
| `await db.fetchrow(query, *args)` | Retorna um registro ou `None` |
| `await db.execute(query, *args)` | Executa DML (INSERT/UPDATE/DELETE) |
| `await db.fetchval(query, *args)` | Retorna um único valor |

O manager já está disponível em `request.app.state.db`.

### `CacheManager` (`app/core/cache.py`)

| Método | Descrição |
|--------|-----------|
| `await cache.get(key)` | Retorna valor ou `None` |
| `await cache.set(key, value, ttl?)` | Salva valor com TTL |
| `await cache.delete(key)` | Remove chave |
| `await cache.exists(key)` | Verifica existência |

O manager já está disponível em `request.app.state.cache`.

---

## 💡 Dicas

- Use `body.model_dump(exclude_none=True)` no PATCH para pegar apenas os campos enviados.
- Trate `asyncpg.UniqueViolationError` para retornar HTTP 409 no POST.
- Use `raise HTTPException(status_code=404, detail="Pokemon not found")` para 404s.
- O TTL padrão do cache está configurado em `.env` na variável `REDIS_TTL` (segundos).
- A documentação interativa da API fica em `/docs` (Swagger) e `/redoc`.
