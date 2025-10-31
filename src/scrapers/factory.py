from typing import Dict, Type
from .base import BaseScraper
from .tjsp import TJSPScraper


class ScraperFactory:
    """Factory para criar scrapers específicos de cada tribunal."""
    
    _scrapers: Dict[str, Type[BaseScraper]] = {
        "TJSP": TJSPScraper,
        # Adicionar outros tribunais aqui
        # "TJRJ": TJRJScraper,
        # "STJ": STJScraper,
    }
    
    @classmethod
    def create(cls, court_acronym: str) -> BaseScraper:
        """
        Cria scraper para o tribunal especificado.
        
        Args:
            court_acronym: Sigla do tribunal (ex: TJSP, TJRJ)
            
        Returns:
            Instância do scraper
            
        Raises:
            ValueError: Se tribunal não tiver scraper implementado
        """
        scraper_class = cls._scrapers.get(court_acronym.upper())
        
        if not scraper_class:
            raise ValueError(f"Scraper não implementado para tribunal: {court_acronym}")
        
        return scraper_class()
    
    @classmethod
    def get_available_courts(cls) -> List[str]:
        """Retorna lista de tribunais com scraper disponível."""
        return list(cls._scrapers.keys())