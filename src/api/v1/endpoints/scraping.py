from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from uuid import UUID

from src.config.database import get_db
from src.repositories.process_repository import ProcessRepository
from src.repositories.court_repository import CourtRepository
from src.services.scraping_service import ScrapingService
from src.schemas.process import ScrapingJobRequest, ScrapingJobResponse

router = APIRouter(prefix="/scraping", tags=["scraping"])


def get_scraping_service(db = Depends(get_db)) -> ScrapingService:
    """Dependency para obter ScrapingService."""
    return ScrapingService(
        process_repo=ProcessRepository(db),
        court_repo=CourtRepository(db)
    )


@router.post(
    "/process/{process_number}",
    summary="Fazer scraping de processo"
)
async def scrape_process(
    process_number: str,
    court_id: UUID,
    force_update: bool = False,
    service: ScrapingService = Depends(get_scraping_service)
):
    """
    Faz scraping de um processo específico.
    
    - **process_number**: Número do processo (CNJ)
    - **court_id**: ID do tribunal
    - **force_update**: Força atualização mesmo se recente
    """
    result = await service.scrape_process(
        process_number=process_number,
        court_id=court_id,
        force_update=force_update
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post(
    "/batch",
    summary="Fazer scraping em lote"
)
async def scrape_batch(
    request: ScrapingJobRequest,
    background_tasks: BackgroundTasks,
    service: ScrapingService = Depends(get_scraping_service)
):
    """
    Inicia job de scraping para múltiplos processos em background.
    
    - **process_numbers**: Lista de números de processo
    - **court_id**: ID do tribunal
    - **priority**: Prioridade do job (1-10)
    - **force_update**: Força atualização
    """
    # Adiciona task em background
    background_tasks.add_task(
        service.scrape_multiple_processes,
        process_numbers=request.process_numbers,
        court_id=request.court_id,
        max_concurrent=5
    )
    
    return {
        "message": f"Job iniciado para {len(request.process_numbers)} processos",
        "total_processes": len(request.process_numbers)
    }