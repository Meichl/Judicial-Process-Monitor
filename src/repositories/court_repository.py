from typing import Optional
from sqlalchemy import select
from src.models.process import Court
from .base import BaseRepository


class CourtRepository(BaseRepository[Court]):
    """Repository para tribunais."""
    
    def __init__(self, db):
        super().__init__(Court, db)
    
    async def get_by_acronym(self, acronym: str) -> Optional[Court]:
        """Busca tribunal pela sigla."""
        result = await self.db.execute(
            select(Court).where(Court.acronym == acronym)
        )
        return result.scalar_one_or_none()
    
    async def get_active_courts(self) -> list[Court]:
        """Retorna tribunais ativos."""
        result = await self.db.execute(
            select(Court).where(Court.active == 1)
        )
        return result.scalars().all()