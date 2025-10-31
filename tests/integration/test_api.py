import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Testa endpoint de health check."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_court(client: AsyncClient):
    """Testa criação de tribunal via API."""
    court_data = {
        "name": "Tribunal de Justiça de São Paulo",
        "acronym": "TJSP",
        "court_type": "TJ",
        "state": "SP",
        "base_url": "https://esaj.tjsp.jus.br",
        "search_url": "https://esaj.tjsp.jus.br/cpopg/search.do"
    }
    
    response = await client.post("/api/v1/courts/", json=court_data)
    assert response.status_code == 201
    data = response.json()
    assert data["acronym"] == "TJSP"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_courts(client: AsyncClient):
    """Testa listagem de tribunais."""
    response = await client.get("/api/v1/courts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# tests/fixtures/sample_data.py
"""Dados de exemplo para testes."""

SAMPLE_PROCESS_DATA = {
    "process_number": "12345678920241234567",
    "subject": "Ação de Cobrança",
    "class_type": "Procedimento Comum Cível",
    "area": "Cível",
    "plaintiffs": [
        {"type": "Autor", "name": "João da Silva"}
    ],
    "defendants": [
        {"type": "Réu", "name": "Maria de Souza"}
    ],
    "lawyers": [
        {"name": "Dr. José Advogado", "type": "advogado"}
    ],
    "judge": "Juiz Federal João Santos",
    "case_value": "R$ 50.000,00"
}

SAMPLE_MOVEMENT_DATA = {
    "movement_type": "Juntada de Petição",
    "description": "Petição inicial protocolada eletronicamente",
    "complementary_info": "Petição de 10 páginas"
}

SAMPLE_COURT_DATA = {
    "name": "Tribunal de Justiça de São Paulo",
    "acronym": "TJSP",
    "court_type": "TJ",
    "state": "SP",
    "base_url": "https://esaj.tjsp.jus.br",
    "search_url": "https://esaj.tjsp.jus.br/cpopg/search.do"
}