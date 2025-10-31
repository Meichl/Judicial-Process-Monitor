from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from src.config.settings import settings
from src.config.database import init_db
from src.api.v1.endpoints import processes, courts, scraping

# Configuração de logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicializa aplicação
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging e métricas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições."""
    start_time = time.time()
    
    # Processa request
    response = await call_next(request)
    
    # Calcula tempo de processamento
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "type": type(exc).__name__
        }
    )


# Eventos de startup/shutdown
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação."""
    logger.info("Iniciando aplicação...")
    
    # Inicializa banco de dados
    try:
        await init_db()
        logger.info("Banco de dados inicializado")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação."""
    logger.info("Desligando aplicação...")


# Rotas
@app.get("/", tags=["health"])
async def root():
    """Endpoint raiz."""
    return {
        "application": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check da aplicação."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Registra routers
app.include_router(processes.router, prefix=settings.API_V1_PREFIX)
app.include_router(courts.router, prefix=settings.API_V1_PREFIX)
app.include_router(scraping.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )