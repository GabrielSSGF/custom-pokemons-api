"""
tests/test_custom_pokemons.py
-----------------------------
Testes unitários para as rotas /pokemons/custom.

Cobre criação, listagem, busca com cache e atualização.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


# Simula um asyncpg.Record como um dict simples
def make_record(**kwargs) -> MagicMock:
    record = MagicMock()
    record.__iter__ = lambda self: iter(kwargs.items())
    record.keys = lambda: kwargs.keys()
    record.__getitem__ = lambda self, key: kwargs[key]
    # dict(record) → usado pelos handlers
    record._data = kwargs
    return record


CUSTOM_POKEMON = {
    "id": 1,
    "name": "charminha",
    "type": "fire",
    "hp": 45,
    "attack": 60,
    "defense": 40,
}

CREATE_BODY = {
    "name": "charminha",
    "type": "fire",
    "hp": 45,
    "attack": 60,
    "defense": 40,
}


class TestCreateCustomPokemon:
    """POST /pokemons/custom"""

    async def test_returns_201_on_success(self, client, mock_db):
        """Deve retornar 201 com o Pokémon criado."""
        mock_db.fetchrow = AsyncMock(return_value=CUSTOM_POKEMON)

        response = await client.post("/pokemons/custom", json=CREATE_BODY)

        assert response.status_code == 201

    async def test_persists_to_database(self, client, mock_db):
        """Deve chamar o banco de dados para persistir o Pokémon."""
        mock_db.fetchrow = AsyncMock(return_value=CUSTOM_POKEMON)

        await client.post("/pokemons/custom", json=CREATE_BODY)

        mock_db.fetchrow.assert_called_once()

    async def test_returns_409_on_duplicate_name(self, client, mock_db):
        """Deve retornar 409 quando o nome já existir (violação de UNIQUE)."""
        import asyncpg

        mock_db.fetchrow = AsyncMock(
            side_effect=asyncpg.UniqueViolationError("duplicate key")
        )

        response = await client.post("/pokemons/custom", json=CREATE_BODY)

        assert response.status_code == 409

    async def test_returns_422_for_invalid_body(self, client):
        """Deve retornar 422 se o body não satisfizer as validações do modelo."""
        response = await client.post("/pokemons/custom", json={"name": ""})

        assert response.status_code == 422


class TestListCustomPokemons:
    """GET /pokemons/custom"""

    async def test_returns_200_with_list(self, client, mock_db):
        """Deve retornar 200 com a lista de Pokémons."""
        mock_db.fetch = AsyncMock(return_value=[CUSTOM_POKEMON])

        response = await client.get("/pokemons/custom")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_returns_empty_list_when_no_pokemons(self, client, mock_db):
        """Deve retornar lista vazia quando não houver Pokémons."""
        mock_db.fetch = AsyncMock(return_value=[])

        response = await client.get("/pokemons/custom")

        assert response.status_code == 200
        assert response.json() == []

    async def test_does_not_use_cache(self, client, mock_db, mock_cache):
        """A listagem completa não deve usar o cache."""
        mock_db.fetch = AsyncMock(return_value=[CUSTOM_POKEMON])

        await client.get("/pokemons/custom")

        mock_cache.get.assert_not_called()


class TestGetCustomPokemon:
    """GET /pokemons/custom/{name}"""

    async def test_returns_cached_when_available(self, client, mock_cache, mock_db):
        """Se estiver em cache, deve retornar sem bater no banco."""
        mock_cache.get = AsyncMock(return_value=CUSTOM_POKEMON)

        response = await client.get("/pokemons/custom/charminha")

        assert response.status_code == 200
        mock_db.fetchrow.assert_not_called()

    async def test_fetches_from_db_when_not_cached(self, client, mock_cache, mock_db):
        """Se não estiver em cache, deve buscar no banco."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_db.fetchrow = AsyncMock(return_value=CUSTOM_POKEMON)

        response = await client.get("/pokemons/custom/charminha")

        assert response.status_code == 200
        mock_db.fetchrow.assert_called_once()

    async def test_stores_in_cache_after_db_fetch(self, client, mock_cache, mock_db):
        """Após buscar no banco, deve salvar no cache."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_db.fetchrow = AsyncMock(return_value=CUSTOM_POKEMON)

        await client.get("/pokemons/custom/charminha")

        mock_cache.set.assert_called_once()

    async def test_returns_404_when_not_found(self, client, mock_cache, mock_db):
        """Deve retornar 404 quando o Pokémon não existir no banco."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_db.fetchrow = AsyncMock(return_value=None)

        response = await client.get("/pokemons/custom/fantasma")

        assert response.status_code == 404


class TestUpdateCustomPokemon:
    """PATCH /pokemons/custom/{name}"""

    async def test_returns_200_on_success(self, client, mock_db, mock_cache):
        """Deve retornar 200 com o Pokémon atualizado."""
        updated = {**CUSTOM_POKEMON, "hp": 99}
        mock_db.fetchrow = AsyncMock(return_value=updated)

        response = await client.patch(
            "/pokemons/custom/charminha", json={"hp": 99}
        )

        assert response.status_code == 200
        assert response.json()["hp"] == 99

    async def test_updates_cache_after_db_update(self, client, mock_db, mock_cache):
        """Após atualizar no banco, deve invalidar ou atualizar o cache."""
        updated = {**CUSTOM_POKEMON, "hp": 99}
        mock_db.fetchrow = AsyncMock(return_value=updated)

        await client.patch("/pokemons/custom/charminha", json={"hp": 99})

        # Deve ter chamado set ou delete no cache
        assert mock_cache.set.called or mock_cache.delete.called

    async def test_returns_404_when_not_found(self, client, mock_db):
        """Deve retornar 404 quando o Pokémon a ser atualizado não existir."""
        mock_db.fetchrow = AsyncMock(return_value=None)

        response = await client.patch(
            "/pokemons/custom/fantasma", json={"hp": 10}
        )

        assert response.status_code == 404

    async def test_accepts_partial_update(self, client, mock_db, mock_cache):
        """Deve aceitar atualização com apenas um campo."""
        updated = {**CUSTOM_POKEMON, "type": "water"}
        mock_db.fetchrow = AsyncMock(return_value=updated)

        response = await client.patch(
            "/pokemons/custom/charminha", json={"type": "water"}
        )

        assert response.status_code == 200
