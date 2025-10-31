from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from uuid import UUID

from src.models.process import Process, Movement, Document, ProcessStatus
from .base import BaseRepository


class ProcessRepository(BaseRepository[Process]):
    """Repository para processos judiciais."""
    
    def __init__(self, db):
        super().__init__(Process, db)
    
    async def get_by_process_number(self, process_number: str) -> Optional[Process]:
        """Busca processo pelo número."""
        result = await self.db.execute(
            select(Process)
            .where(Process.process_number == process_number)
            .options(
                selectinload(Process.court),
                selectinload(Process.movements),
                selectinload(Process.documents)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_details(self, id: UUID) -> Optional[Process]:
        """Busca processo com todas as relações."""
        result = await self.db.execute(
            select(Process)
            .where(Process.id == id)
            .options(
                selectinload(Process.court),
                selectinload(Process.movements),
                selectinload(Process.documents)
            )
        )
        return result.scalar_one_or_none()
    
    async def search(
        self,
        query: str,
        court_id: Optional[UUID] = None,
        status: Optional[ProcessStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Process]:
        """Busca processos por texto."""
        stmt = select(Process).options(selectinload(Process.court))
        
        # Filtro de texto (busca em múltiplos campos)
        if query:
            stmt = stmt.where(
                or_(
                    Process.process_number.ilike(f"%{query}%"),
                    Process.subject.ilike(f"%{query}%"),
                    Process.judge.ilike(f"%{query}%")
                )
            )
        
        if court_id:
            stmt = stmt.where(Process.court_id == court_id)
        
        if status:
            stmt = stmt.where(Process.status == status)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_processes_to_scrape(
        self,
        court_id: UUID,
        hours_since_last_scrape: int = 24,
        limit: int = 100
    ) -> List[Process]:
        """Busca processos que precisam ser atualizados."""
        cutoff_time = datetime.utcnow()
        
        stmt = (
            select(Process)
            .where(Process.court_id == court_id)
            .where(
                or_(
                    Process.last_scraped_at.is_(None),
                    Process.last_scraped_at < cutoff_time
                )
            )
            .order_by(Process.last_scraped_at.asc().nullsfirst())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def update_scraping_status(
        self,
        process_id: UUID,
        success: bool,
        raw_html: Optional[str] = None
    ) -> None:
        """Atualiza status de scraping do processo."""
        data = {
            "last_scraped_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if success:
            data["scraping_errors"] = 0
            if raw_html:
                data["raw_html"] = raw_html
        else:
            # Incrementa contador de erros
            process = await self.get_by_id(process_id)
            if process:
                data["scraping_errors"] = process.scraping_errors + 1
        
        await self.update_by_id(process_id, data)
    
    async def add_movement(self, movement: Movement) -> Movement:
        """Adiciona movimentação ao processo."""
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(movement)
        return movement
    
    async def add_document(self, document: Document) -> Document:
        """Adiciona documento ao processo."""
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document