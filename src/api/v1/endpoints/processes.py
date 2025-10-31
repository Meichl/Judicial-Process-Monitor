from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from uuid import UUID

from src.config.database import get_db
from src.repositories.process_repository import ProcessRepository
from src.repositories.court_repository import CourtRepository
from src.services.process_service import ProcessService
from src.schemas.process import (
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    ProcessDetailResponse,
    PaginationParams
)

router = APIRouter(prefix="/processes", tags=["processes"])


def get_process_service(db = Depends(get_db)) -> ProcessService:
    """Dependency para obter ProcessService."""
    return ProcessService(
        process_repo=ProcessRepository(db),
        court_repo=CourtRepository(db)
    )


@router.post(
    "/",
    response_model=ProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar processo"
)
async def create_process(
    data: ProcessCreate,
    service: ProcessService = Depends(get_process_service)
):
    """Cria um novo processo judicial no sistema."""
    try:
        return await service.create_process(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{process_id}",
    response_model=ProcessDetailResponse,
    summary="Buscar processo por ID"
)
async def get_process(
    process_id: UUID,
    service: ProcessService = Depends(get_process_service)
):
    """Busca processo pelo ID com todos os detalhes."""
    process = await service.get_process(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process


@router.get(
    "/number/{process_number}",
    response_model=ProcessDetailResponse,
    summary="Buscar processo por número"
)
async def get_process_by_number(
    process_number: str,
    service: ProcessService = Depends(get_process_service)
):
    """Busca processo pelo número CNJ."""
    process = await service.get_process_by_number(process_number)
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process


@router.get(
    "/",
    summary="Buscar processos"
)
async def search_processes(
    query: str = Query(default="", description="Termo de busca"),
    court_id: Optional[UUID] = Query(default=None, description="ID do tribunal"),
    status: Optional[str] = Query(default=None, description="Status do processo"),
    page: int = Query(default=1, ge=1, description="Página"),
    page_size: int = Query(default=50, ge=1, le=100, description="Itens por página"),
    service: ProcessService = Depends(get_process_service)
):
    """
    Busca processos com filtros e paginação.
    
    - **query**: Busca em número, assunto e juiz
    - **court_id**: Filtra por tribunal
    - **status**: Filtra por status
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    return await service.search_processes(
        query=query,
        court_id=court_id,
        status=status,
        pagination=pagination
    )


@router.put(
    "/{process_id}",
    response_model=ProcessResponse,
    summary="Atualizar processo"
)
async def update_process(
    process_id: UUID,
    data: ProcessUpdate,
    service: ProcessService = Depends(get_process_service)
):
    """Atualiza dados do processo."""
    updated = await service.update_process(process_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return updated


@router.delete(
    "/{process_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar processo"
)
async def delete_process(
    process_id: UUID,
    service: ProcessService = Depends(get_process_service)
):
    """Deleta processo do sistema."""
    deleted = await service.delete_process(process_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Processo não encontrado")