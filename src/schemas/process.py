# src/schemas/process.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import re


class CourtBase(BaseModel):
    name: str
    acronym: str
    court_type: str
    state: Optional[str] = None
    base_url: str
    search_url: Optional[str] = None


class CourtCreate(CourtBase):
    pass


class CourtResponse(CourtBase):
    id: UUID
    active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProcessBase(BaseModel):
    process_number: str = Field(..., description="Número do processo (CNJ)")
    subject: Optional[str] = None
    class_type: Optional[str] = None
    area: Optional[str] = None
    distribution_date: Optional[datetime] = None
    plaintiffs: Optional[List[Dict[str, Any]]] = None
    defendants: Optional[List[Dict[str, Any]]] = None
    lawyers: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = "ativo"
    current_location: Optional[str] = None
    judge: Optional[str] = None
    case_value: Optional[str] = None
    
    @validator("process_number")
    def validate_process_number(cls, v):
        """Valida número do processo no padrão CNJ."""
        # Remove caracteres não numéricos
        clean_number = re.sub(r'\D', '', v)
        
        # Padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
        if len(clean_number) != 20:
            raise ValueError("Número do processo deve ter 20 dígitos")
        
        return clean_number


class ProcessCreate(ProcessBase):
    court_id: UUID


class ProcessUpdate(BaseModel):
    subject: Optional[str] = None
    class_type: Optional[str] = None
    area: Optional[str] = None
    status: Optional[str] = None
    current_location: Optional[str] = None
    judge: Optional[str] = None
    case_value: Optional[str] = None
    plaintiffs: Optional[List[Dict[str, Any]]] = None
    defendants: Optional[List[Dict[str, Any]]] = None
    lawyers: Optional[List[Dict[str, Any]]] = None


class ProcessResponse(ProcessBase):
    id: UUID
    court_id: UUID
    last_scraped_at: Optional[datetime] = None
    scraping_errors: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MovementBase(BaseModel):
    movement_date: datetime
    movement_type: str
    description: str
    complementary_info: Optional[str] = None
    responsible: Optional[str] = None


class MovementCreate(MovementBase):
    process_id: UUID


class MovementResponse(MovementBase):
    id: UUID
    process_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    document_type: str
    title: str
    filing_date: Optional[datetime] = None
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    is_public: bool = True


class DocumentCreate(DocumentBase):
    process_id: UUID


class DocumentResponse(DocumentBase):
    id: UUID
    process_id: UUID
    downloaded: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProcessDetailResponse(ProcessResponse):
    """Response completo com movimentações e documentos."""
    court: CourtResponse
    movements: List[MovementResponse] = []
    documents: List[DocumentResponse] = []


class ScrapingJobRequest(BaseModel):
    """Request para iniciar job de scraping."""
    process_numbers: List[str]
    court_id: UUID
    priority: int = Field(default=5, ge=1, le=10)
    force_update: bool = False


class ScrapingJobResponse(BaseModel):
    """Response de job de scraping."""
    job_id: str
    status: str
    total_processes: int
    created_at: datetime


# src/schemas/pagination.py
class PaginationParams(BaseModel):
    """Parâmetros de paginação."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel):
    """Response paginado genérico."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[Any], total: int, pagination: PaginationParams):
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages
        )