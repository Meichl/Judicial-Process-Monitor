# src/services/process_service.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import asyncio

from src.repositories.process_repository import ProcessRepository
from src.repositories.court_repository import CourtRepository
from src.models.process import Process, Movement, Document
from src.schemas.process import (
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    ProcessDetailResponse,
    PaginationParams
)
from src.scrapers.factory import ScraperFactory


class ProcessService:
    """Service para gerenciar processos judiciais."""
    
    def __init__(
        self,
        process_repo: ProcessRepository,
        court_repo: CourtRepository
    ):
        self.process_repo = process_repo
        self.court_repo = court_repo
    
    async def create_process(self, data: ProcessCreate) -> ProcessResponse:
        """Cria novo processo."""
        # Valida se tribunal existe
        court = await self.court_repo.get_by_id(data.court_id)
        if not court:
            raise ValueError(f"Tribunal não encontrado: {data.court_id}")
        
        # Verifica se processo já existe
        existing = await self.process_repo.get_by_process_number(data.process_number)
        if existing:
            raise ValueError(f"Processo já cadastrado: {data.process_number}")
        
        # Cria processo
        process = Process(**data.model_dump())
        created = await self.process_repo.create(process)
        
        return ProcessResponse.model_validate(created)
    
    async def get_process(self, process_id: UUID) -> Optional[ProcessDetailResponse]:
        """Busca processo com detalhes completos."""
        process = await self.process_repo.get_with_details(process_id)
        if not process:
            return None
        
        return ProcessDetailResponse.model_validate(process)
    
    async def get_process_by_number(
        self,
        process_number: str
    ) -> Optional[ProcessDetailResponse]:
        """Busca processo pelo número."""
        process = await self.process_repo.get_by_process_number(process_number)
        if not process:
            return None
        
        return ProcessDetailResponse.model_validate(process)
    
    async def update_process(
        self,
        process_id: UUID,
        data: ProcessUpdate
    ) -> Optional[ProcessResponse]:
        """Atualiza dados do processo."""
        # Remove campos None
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        
        if not update_data:
            return None
        
        updated = await self.process_repo.update_by_id(process_id, update_data)
        if not updated:
            return None
        
        return ProcessResponse.model_validate(updated)
    
    async def delete_process(self, process_id: UUID) -> bool:
        """Deleta processo."""
        return await self.process_repo.delete_by_id(process_id)
    
    async def search_processes(
        self,
        query: str = "",
        court_id: Optional[UUID] = None,
        status: Optional[str] = None,
        pagination: PaginationParams = PaginationParams()
    ) -> Dict[str, Any]:
        """Busca processos com filtros."""
        processes = await self.process_repo.search(
            query=query,
            court_id=court_id,
            status=status,
            skip=pagination.offset,
            limit=pagination.limit
        )
        
        total = await self.process_repo.count({
            "court_id": court_id,
            "status": status
        } if court_id or status else None)
        
        return {
            "items": [ProcessResponse.model_validate(p) for p in processes],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": (total + pagination.page_size - 1) // pagination.page_size
        }
