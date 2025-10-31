from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from uuid import UUID

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Repository base com operações CRUD genéricas."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Busca registro por ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Busca todos os registros com paginação."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Conta registros."""
        query = select(func.count(self.model.id))
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create(self, obj: ModelType) -> ModelType:
        """Cria novo registro."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def update_by_id(self, id: UUID, data: Dict[str, Any]) -> Optional[ModelType]:
        """Atualiza registro por ID."""
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
        return await self.get_by_id(id)
    
    async def delete_by_id(self, id: UUID) -> bool:
        """Deleta registro por ID."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0