import pytest
from uuid import uuid4

from src.models.process import Court, Process, ProcessStatus
from src.repositories.process_repository import ProcessRepository
from src.repositories.court_repository import CourtRepository


@pytest.mark.asyncio
async def test_create_court(test_db):
    """Testa criação de tribunal."""
    repo = CourtRepository(test_db)
    
    court = Court(
        name="Tribunal de Justiça de São Paulo",
        acronym="TJSP",
        court_type="TJ",
        state="SP",
        base_url="https://esaj.tjsp.jus.br",
        search_url="https://esaj.tjsp.jus.br/cpopg/search.do"
    )
    
    created = await repo.create(court)
    assert created.id is not None
    assert created.acronym == "TJSP"


@pytest.mark.asyncio
async def test_get_court_by_acronym(test_db):
    """Testa busca de tribunal por sigla."""
    repo = CourtRepository(test_db)
    
    court = Court(
        name="Superior Tribunal de Justiça",
        acronym="STJ",
        court_type="STJ",
        base_url="https://www.stj.jus.br"
    )
    
    await repo.create(court)
    
    found = await repo.get_by_acronym("STJ")
    assert found is not None
    assert found.name == "Superior Tribunal de Justiça"


@pytest.mark.asyncio
async def test_create_process(test_db):
    """Testa criação de processo."""
    court_repo = CourtRepository(test_db)
    process_repo = ProcessRepository(test_db)
    
    # Cria tribunal primeiro
    court = Court(
        name="TJSP",
        acronym="TJSP",
        court_type="TJ",
        state="SP",
        base_url="https://esaj.tjsp.jus.br"
    )
    created_court = await court_repo.create(court)
    
    # Cria processo
    process = Process(
        process_number="12345678920241234567",
        court_id=created_court.id,
        subject="Ação de cobrança",
        status=ProcessStatus.ATIVO
    )
    
    created_process = await process_repo.create(process)
    assert created_process.id is not None
    assert created_process.process_number == "12345678920241234567"


@pytest.mark.asyncio
async def test_get_process_by_number(test_db):
    """Testa busca de processo por número."""
    court_repo = CourtRepository(test_db)
    process_repo = ProcessRepository(test_db)
    
    # Setup
    court = await court_repo.create(
        Court(
            name="TJRJ",
            acronym="TJRJ",
            court_type="TJ",
            state="RJ",
            base_url="https://www.tjrj.jus.br"
        )
    )
    
    process_number = "98765432120241234567"
    await process_repo.create(
        Process(
            process_number=process_number,
            court_id=court.id,
            subject="Ação de indenização"
        )
    )
    
    # Busca
    found = await process_repo.get_by_process_number(process_number)
    assert found is not None
    assert found.subject == "Ação de indenização"


@pytest.mark.asyncio
async def test_search_processes(test_db):
    """Testa busca de processos por texto."""
    court_repo = CourtRepository(test_db)
    process_repo = ProcessRepository(test_db)
    
    court = await court_repo.create(
        Court(
            name="TJSP",
            acronym="TJSP",
            court_type="TJ",
            state="SP",
            base_url="https://esaj.tjsp.jus.br"
        )
    )
    
    # Cria vários processos
    await process_repo.create(
        Process(
            process_number="11111111120241234567",
            court_id=court.id,
            subject="Ação trabalhista"
        )
    )
    
    await process_repo.create(
        Process(
            process_number="22222222220241234567",
            court_id=court.id,
            subject="Ação de cobrança"
        )
    )
    
    # Busca
    results = await process_repo.search(query="trabalhista", limit=10)
    assert len(results) == 1
    assert results[0].subject == "Ação trabalhista"