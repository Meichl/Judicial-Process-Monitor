import re
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


def parse_currency(value: str) -> Optional[Decimal]:
    """
    Parse valor monetário brasileiro.
    
    Exemplo: "R$ 1.234,56" -> Decimal("1234.56")
    """
    if not value:
        return None
    
    # Remove símbolos e espaços
    clean = re.sub(r'[R$\s]', '', value)
    
    # Substitui vírgula por ponto
    clean = clean.replace('.', '').replace(',', '.')
    
    try:
        return Decimal(clean)
    except:
        return None


def parse_date_flexible(date_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """
    Tenta parsear data em múltiplos formatos.
    
    Args:
        date_str: String com data
        formats: Lista de formatos para tentar
    """
    if not date_str:
        return None
    
    if formats is None:
        formats = [
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y às %H:%M",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y",
            "%d.%m.%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None