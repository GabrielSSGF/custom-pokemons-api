"""
Models
------
Pydantic schemas used as request/response bodies.

TODO (alunos): ajuste os campos de acordo com o que a sua tabela ``custom_pokemons``
               armazena. Adicione validações (Field, validator) conforme necessário.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class PokemonCreation(BaseModel):
    """
    Payload para criar um Pokémon customizado no banco de dados.

    TODO: adicione / remova campos conforme o schema da sua tabela.
    """

    name: str = Field(..., min_length=1, max_length=100, examples=["mypokemon"])
    type: str = Field(..., min_length=1, max_length=50, examples=["fire"])
    hp: int = Field(default=0, ge=0, examples=[45])
    attack: int = Field(default=0, ge=0, examples=[49])
    defense: int = Field(default=0, ge=0, examples=[49])


class PokemonUpdate(BaseModel):
    """
    Payload para atualizar parcialmente um Pokémon customizado.

    Todos os campos são opcionais — apenas os enviados serão atualizados.

    TODO: adicione / remova campos conforme o schema da sua tabela.
    """

    type: str | None = Field(default=None, min_length=1, max_length=50, examples=["water"])
    hp: int | None = Field(default=None, ge=0, examples=[60])
    attack: int | None = Field(default=None, ge=0, examples=[55])
    defense: int | None = Field(default=None, ge=0, examples=[50])


# ---------------------------------------------------------------------------
# Response bodies
# ---------------------------------------------------------------------------

class PokemonResponse(BaseModel):
    """Generic response for a custom Pokémon record."""

    id: int
    name: str
    type: str
    hp: int
    attack: int
    defense: int
