import asyncio
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.repositories.process_repository import ProcessRepository
from src.repositories.court_repository import CourtRepository
from src.models.process import Process, Movement, Document
from src.scrapers.factory import ScraperFactory


class ScrapingService:
    """Service para orquestrar scraping de processos."""
    
    def __init__(
        self,
        process_repo: ProcessRepository,
        court_repo: CourtRepository
    ):
        self.process_repo = process_repo
        self.court_repo = court_repo
    
    async def scrape_process(
        self,
        process_number: str,
        court_id: UUID,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Faz scraping de um processo específico.
        
        Args:
            process_number: Número do processo
            court_id: ID do tribunal
            force_update: Force atualização mesmo se recente
            
        Returns:
            Resultado do scraping
        """
        # Busca tribunal
        court = await self.court_repo.get_by_id(court_id)
        if not court:
            return {
                "success": False,
                "error": f"Tribunal não encontrado: {court_id}"
            }
        
        # Verifica se processo existe
        process = await self.process_repo.get_by_process_number(process_number)
        
        # Se não forçar update e processo foi atualizado recentemente, pula
        if not force_update and process and process.last_scraped_at:
            hours_since_update = (datetime.utcnow() - process.last_scraped_at).total_seconds() / 3600
            if hours_since_update < 1:  # Menos de 1 hora
                return {
                    "success": True,
                    "cached": True,
                    "message": "Processo atualizado recentemente"
                }
        
        try:
            # Cria scraper para o tribunal
            scraper = ScraperFactory.create(court.acronym)
            
            async with scraper:
                # Faz scraping dos dados
                process_data = await scraper.search_process(process_number)
                movements_data = await scraper.get_movements(process_number)
                documents_data = await scraper.get_documents(process_number)
            
            # Atualiza ou cria processo
            if process:
                await self._update_process(process, process_data, movements_data, documents_data)
            else:
                await self._create_process(
                    court_id,
                    process_number,
                    process_data,
                    movements_data,
                    documents_data
                )
            
            return {
                "success": True,
                "cached": False,
                "movements_count": len(movements_data),
                "documents_count": len(documents_data)
            }
            
        except Exception as e:
            # Registra erro
            if process:
                await self.process_repo.update_scraping_status(
                    process.id,
                    success=False
                )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_process(
        self,
        court_id: UUID,
        process_number: str,
        process_data: Dict[str, Any],
        movements_data: List[Dict[str, Any]],
        documents_data: List[Dict[str, Any]]
    ) -> Process:
        """Cria novo processo com movimentações e documentos."""
        # Cria processo
        process = Process(
            court_id=court_id,
            process_number=process_number,
            subject=process_data.get("subject"),
            class_type=process_data.get("class_type"),
            area=process_data.get("area"),
            distribution_date=process_data.get("distribution_date"),
            plaintiffs=process_data.get("plaintiffs"),
            defendants=process_data.get("defendants"),
            lawyers=process_data.get("lawyers"),
            judge=process_data.get("judge"),
            case_value=process_data.get("case_value"),
            raw_html=process_data.get("raw_html"),
            last_scraped_at=datetime.utcnow()
        )
        
        created_process = await self.process_repo.create(process)
        
        # Adiciona movimentações
        for mov_data in movements_data:
            movement = Movement(
                process_id=created_process.id,
                **mov_data
            )
            await self.process_repo.add_movement(movement)
        
        # Adiciona documentos
        for doc_data in documents_data:
            document = Document(
                process_id=created_process.id,
                **doc_data
            )
            await self.process_repo.add_document(document)
        
        return created_process
    
    async def _update_process(
        self,
        process: Process,
        process_data: Dict[str, Any],
        movements_data: List[Dict[str, Any]],
        documents_data: List[Dict[str, Any]]
    ) -> None:
        """Atualiza processo existente."""
        # Atualiza dados básicos
        update_data = {
            "subject": process_data.get("subject"),
            "class_type": process_data.get("class_type"),
            "area": process_data.get("area"),
            "judge": process_data.get("judge"),
            "case_value": process_data.get("case_value"),
            "plaintiffs": process_data.get("plaintiffs"),
            "defendants": process_data.get("defendants"),
            "lawyers": process_data.get("lawyers"),
            "raw_html": process_data.get("raw_html"),
            "last_scraped_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.process_repo.update_by_id(process.id, update_data)
        
        # Adiciona novas movimentações (compara com existentes)
        existing_movements = {
            (m.movement_date, m.description) for m in process.movements
        }
        
        for mov_data in movements_data:
            key = (mov_data["movement_date"], mov_data["description"])
            if key not in existing_movements:
                movement = Movement(
                    process_id=process.id,
                    **mov_data
                )
                await self.process_repo.add_movement(movement)
        
        # Adiciona novos documentos
        existing_docs = {d.title for d in process.documents}
        
        for doc_data in documents_data:
            if doc_data["title"] not in existing_docs:
                document = Document(
                    process_id=process.id,
                    **doc_data
                )
                await self.process_repo.add_document(document)
    
    async def scrape_multiple_processes(
        self,
        process_numbers: List[str],
        court_id: UUID,
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Faz scraping de múltiplos processos em paralelo.
        
        Args:
            process_numbers: Lista de números de processo
            court_id: ID do tribunal
            max_concurrent: Máximo de requisições concorrentes
            
        Returns:
            Resumo dos resultados
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_limit(process_num: str):
            async with semaphore:
                return await self.scrape_process(process_num, court_id)
        
        results = await asyncio.gather(
            *[scrape_with_limit(pn) for pn in process_numbers],
            return_exceptions=True
        )
        
        # Processa resultados
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        error_count = len(results) - success_count
        
        return {
            "total": len(process_numbers),
            "success": success_count,
            "errors": error_count,
            "results": results
        }