from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from src.config.database import get_db
from src.repositories.court_repository import CourtRepository
from src.schemas.process import CourtCreate, CourtResponse

router = APIRouter(prefix="/courts", tags=["courts"])


def get_court_repo(db = Depends(get_db)) -> CourtRepository:
    """Dependency para obter CourtRepository."""
    return CourtRepository(db)


@router.post(
    "/",
    response_model=CourtResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tribunal"
)
async def create_court(
    data: CourtCreate,
    repo: CourtRepository = Depends(get_court_repo)
):
    """Cadastra novo tribunal no sistema."""
    from src.models.process import Court
    
    court = Court(**data.model_dump())
    created = await repo.create(court)
    return CourtResponse.model_validate(created)


@router.get(
    "/",
    response_model=List[CourtResponse],
    summary="Listar tribunais"
)
async def list_courts(
    active_only: bool = True,
    repo: CourtRepository = Depends(get_court_repo)
):
    """Lista todos os tribunais cadastrados."""
    if active_only:
        courts = await repo.get_active_courts()
    else:
        courts = await repo.get_all()
    
    return [CourtResponse.model_validate(c) for c in courts]


@router.get(
    "/{court_id}",
    response_model=CourtResponse,
    summary="Buscar tribunal por ID"
)
async def get_court(
    court_id: UUID,
    repo: CourtRepository = Depends(get_court_repo)
):
    """Busca tribunal pelo ID."""
    court = await repo.get_by_id(court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Tribunal não encontrado")
    return CourtResponse.model_validate(court)


@router.get(
    "/acronym/{acronym}",
    response_model=CourtResponse,
    summary="Buscar tribunal por sigla"
)
async def get_court_by_acronym(
    acronym: str,
    repo: CourtRepository = Depends(get_court_repo)
):
    """Busca tribunal pela sigla (ex: TJSP, STJ)."""
    court = await repo.get_by_acronym(acronym.upper())
    if not court:
        raise HTTPException(status_code=404, detail="Tribunal não encontrado")
    return CourtResponse.model_validate(court)