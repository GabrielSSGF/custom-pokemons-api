"""
Router: /pokemons
-----------------
Rotas que consomem a PokéAPI externa via AiohttpWrapper.
"""

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/pokemons", tags=["pokemons"])


@router.get(
    "",
    summary="Listar Pokémons da API externa",
    description=(
        "Busca uma lista de Pokémons diretamente na PokéAPI. "
        "Não utiliza cache nem banco de dados."
    ),
)
async def list_pokemons(request: Request):
    """
    TODO (alunos):
        1. Acesse ``request.app.state.http_client`` (instância de AiohttpWrapper).
        2. Faça um GET em ``/pokemon`` (com parâmetros ``limit`` e ``offset`` opcionais via query string).
        3. Retorne a resposta da API externa.

    Dica:
        data = await request.app.state.http_client.get("/pokemon", params={"limit": 20})
        return data
    """
    raise NotImplementedError("Implemente list_pokemons()")


@router.get(
    "/{name}",
    summary="Buscar Pokémon por nome na API externa com cache",
    description=(
        "Tenta encontrar o Pokémon no cache Redis primeiro. "
        "Se não existir, busca na PokéAPI e armazena no cache."
    ),
)
async def get_pokemon(name: str, request: Request):
    """
    TODO (alunos):
        1. Monte a chave de cache, ex.: ``f"pokemon:{name}"``.
        2. Verifique ``request.app.state.cache`` — se existir, retorne o valor cacheado.
        3. Caso contrário, chame a PokéAPI via ``request.app.state.http_client.get(f"/pokemon/{name}")``.
        4. Salve o resultado no cache com um TTL razoável.
        5. Retorne os dados.
        6. Trate o caso de Pokémon não encontrado (HTTP 404).
    """
    raise NotImplementedError("Implemente get_pokemon()")
