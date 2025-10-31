import pytest
from unittest.mock import AsyncMock, patch

from src.scrapers.tjsp import TJSPScraper


@pytest.mark.asyncio
async def test_tjsp_scraper_format_process_number():
    """Testa formatação de número de processo."""
    scraper = TJSPScraper()
    
    formatted = scraper._format_process_number("12345678920241234567")
    assert formatted == "1234567-89.2024.1.23.4567"


@pytest.mark.asyncio
async def test_tjsp_scraper_clean_text():
    """Testa limpeza de texto."""
    scraper = TJSPScraper()
    
    cleaned = scraper.clean_text("  Texto   com   espaços  \n  extras  ")
    assert cleaned == "Texto com espaços extras"