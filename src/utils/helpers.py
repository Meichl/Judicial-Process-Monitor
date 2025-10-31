import re
import unicodedata


def slugify(text: str) -> str:
    """
    Converte texto em slug URL-friendly.
    
    Exemplo: "Ação de Cobrança" -> "acao-de-cobranca"
    """
    text = remove_accents(text.lower())
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def remove_accents(text: str) -> str:
    """Remove acentos de texto."""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto adicionando sufixo."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_process_parts(process_number: str) -> dict:
    """
    Extrai partes do número de processo CNJ.
    
    NNNNNNN-DD.AAAA.J.TR.OOOO
    """
    clean = re.sub(r'\D', '', process_number)
    
    if len(clean) != 20:
        return {}
    
    return {
        "sequential": clean[0:7],
        "verification_digit": clean[7:9],
        "year": clean[9:13],
        "justice_segment": clean[13],
        "court": clean[14:16],
        "origin": clean[16:20]
    }
