# src/models/process.py
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from src.config.database import Base


class ProcessStatus(str, enum.Enum):
    """Status do processo judicial."""
    ATIVO = "ativo"
    ARQUIVADO = "arquivado"
    SUSPENSO = "suspenso"
    BAIXADO = "baixado"
    TRANSITADO_JULGADO = "transitado_julgado"


class Court(Base):
    """Modelo para Tribunais."""
    __tablename__ = "courts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    acronym = Column(String(10), nullable=False, unique=True)
    court_type = Column(String(50), nullable=False)  # TJ, TRF, TST, STJ, STF
    state = Column(String(2), nullable=True)
    base_url = Column(String(500), nullable=False)
    search_url = Column(String(500), nullable=True)
    
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    processes = relationship("Process", back_populates="court")
    
    __table_args__ = (
        Index("idx_court_acronym", "acronym"),
        Index("idx_court_type", "court_type"),
    )


class Process(Base):
    """Modelo para Processos Judiciais."""
    __tablename__ = "processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_number = Column(String(25), nullable=False, unique=True, index=True)
    
    court_id = Column(UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False)
    
    # Informações básicas
    subject = Column(String(500), nullable=True)
    class_type = Column(String(100), nullable=True)
    area = Column(String(50), nullable=True)
    distribution_date = Column(DateTime, nullable=True)
    
    # Partes processuais (JSON para flexibilidade)
    plaintiffs = Column(JSON, nullable=True)
    defendants = Column(JSON, nullable=True)
    lawyers = Column(JSON, nullable=True)
    
    # Status e localização
    status = Column(Enum(ProcessStatus), default=ProcessStatus.ATIVO)
    current_location = Column(String(200), nullable=True)
    judge = Column(String(200), nullable=True)
    
    # Valores
    case_value = Column(String(50), nullable=True)
    
    # Metadados de scraping
    last_scraped_at = Column(DateTime, nullable=True)
    scraping_errors = Column(Integer, default=0)
    raw_html = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    court = relationship("Court", back_populates="processes")
    movements = relationship("Movement", back_populates="process", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="process", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_process_number", "process_number"),
        Index("idx_process_status", "status"),
        Index("idx_process_court", "court_id"),
        Index("idx_process_distribution_date", "distribution_date"),
    )


class Movement(Base):
    """Modelo para Movimentações Processuais."""
    __tablename__ = "movements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    movement_date = Column(DateTime, nullable=False)
    movement_type = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Informações complementares
    complementary_info = Column(Text, nullable=True)
    responsible = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    process = relationship("Process", back_populates="movements")
    
    __table_args__ = (
        Index("idx_movement_process", "process_id"),
        Index("idx_movement_date", "movement_date"),
    )


class Document(Base):
    """Modelo para Documentos do Processo."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    document_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    filing_date = Column(DateTime, nullable=True)
    
    # Armazenamento
    file_url = Column(String(1000), nullable=True)
    file_hash = Column(String(64), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Metadados
    is_public = Column(Integer, default=1)
    downloaded = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    process = relationship("Process", back_populates="documents")
    
    __table_args__ = (
        Index("idx_document_process", "process_id"),
        Index("idx_document_type", "document_type"),
    )