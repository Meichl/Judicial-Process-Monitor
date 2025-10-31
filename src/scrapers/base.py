from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime
import re

from src.config.settings import settings


class BaseScraper(ABC):
    """Scraper base abstrato para todos os tribunais."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
    
    async def __aenter__(self):
        """Context manager para gerenciar sessão HTTP."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha sessão HTTP."""
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=settings.RETRY_DELAY, max=60)
    )
    async def fetch(self, url: str, method: str = "GET", **kwargs) -> str:
        """Faz requisição HTTP com retry automático."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.text()
    
    @staticmethod
    def parse_html(html: str) -> BeautifulSoup:
        """Parse HTML usando BeautifulSoup."""
        return BeautifulSoup(html, "lxml")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove espaços extras e quebras de linha."""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def parse_date(date_str: str, formats: List[str]) -> Optional[datetime]:
        """Tenta parsear data em múltiplos formatos."""
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    @abstractmethod
    async def search_process(self, process_number: str) -> Dict[str, Any]:
        """
        Busca processo pelo número.
        
        Args:
            process_number: Número do processo
            
        Returns:
            Dicionário com dados do processo
        """
        pass
    
    @abstractmethod
    async def get_movements(self, process_number: str) -> List[Dict[str, Any]]:
        """
        Busca movimentações do processo.
        
        Args:
            process_number: Número do processo
            
        Returns:
            Lista de movimentações
        """
        pass
    
    @abstractmethod
    async def get_documents(self, process_number: str) -> List[Dict[str, Any]]:
        """
        Busca documentos do processo.
        
        Args:
            process_number: Número do processo
            
        Returns:
            Lista de documentos
        """
        pass