"""
Router: /pokemons/custom
------------------------
Rotas que operam sobre Pokémons customizados armazenados no Postgres,
com cache em Redis.
"""

from fastapi import APIRouter, Request, HTTPException

from app.models.pokemon import PokemonCreation, PokemonUpdate

router = APIRouter(prefix="/pokemons/custom", tags=["custom-pokemons"])


@router.post(
    "",
    status_code=201,
    summary="Criar Pokémon customizado",
    description="Persiste um novo Pokémon no banco de dados Postgres.",
)
async def create_custom_pokemon(body: PokemonCreation, request: Request):
    """
    TODO (alunos):
        1. Acesse ``request.app.state.db`` (instância de DBManager).
        2. Execute um INSERT na tabela ``custom_pokemons`` com os dados de ``body``.
        3. Retorne o registro criado (incluindo o ``id`` gerado).
        4. Trate o caso de conflito de nome (UNIQUE constraint → HTTP 409).

    Dica de query:
        row = await db.fetchrow(
            \"\"\"
            INSERT INTO custom_pokemons (name, type, hp, attack, defense)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            \"\"\",
            body.name, body.type, body.hp, body.attack, body.defense,
        )
        return dict(row)
    """
    raise NotImplementedError("Implemente create_custom_pokemon()")


@router.get(
    "",
    summary="Listar Pokémons customizados",
    description="Retorna todos os Pokémons armazenados no banco de dados.",
)
async def list_custom_pokemons(request: Request):
    """
    TODO (alunos):
        1. Acesse ``request.app.state.db``.
        2. Execute um SELECT em ``custom_pokemons``.
        3. Retorne a lista de registros.

    Dica de query:
        rows = await db.fetch("SELECT * FROM custom_pokemons ORDER BY id")
        return [dict(r) for r in rows]
    """
    raise NotImplementedError("Implemente list_custom_pokemons()")


@router.get(
    "/{name}",
    summary="Buscar Pokémon customizado por nome com cache",
    description=(
        "Tenta encontrar o Pokémon no cache Redis. "
        "Se não existir, busca no Postgres e armazena no cache."
    ),
)
async def get_custom_pokemon(name: str, request: Request):
    """
    TODO (alunos):
        1. Verifique o cache Redis (``request.app.state.cache``) pela chave ``f"custom:{name}"``.
        2. Se existir, retorne o valor cacheado.
        3. Caso contrário, busque no Postgres via ``request.app.state.db``.
        4. Se não encontrado no Postgres → HTTP 404.
        5. Salve o resultado no cache e retorne.
    """
    raise NotImplementedError("Implemente get_custom_pokemon()")


@router.patch(
    "/{name}",
    summary="Atualizar Pokémon customizado",
    description=(
        "Atualiza campos de um Pokémon existente no Postgres "
        "e invalida/atualiza a entrada no cache Redis."
    ),
)
async def update_custom_pokemon(name: str, body: PokemonUpdate, request: Request):
    """
    TODO (alunos):
        1. Verifique se o Pokémon existe no Postgres → HTTP 404 se não.
        2. Monte a query de UPDATE apenas com os campos presentes em ``body``
           (use ``body.model_dump(exclude_none=True)`` para pegar só os enviados).
        3. Execute o UPDATE e retorne o registro atualizado.
        4. Atualize (ou delete) a entrada no cache Redis para a chave ``f"custom:{name}"``.

    Dica de query dinâmica:
        fields = body.model_dump(exclude_none=True)
        set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(fields))
        values = list(fields.values())
        row = await db.fetchrow(
            f"UPDATE custom_pokemons SET {set_clause}, updated_at = NOW() "
            f"WHERE name = $1 RETURNING *",
            name, *values,
        )
    """
    raise NotImplementedError("Implemente update_custom_pokemon()")
