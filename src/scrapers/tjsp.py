from typing import Dict, List, Any
import re
from datetime import datetime

from .base import BaseScraper


class TJSPScraper(BaseScraper):
    """Scraper para Tribunal de Justiça de São Paulo."""
    
    BASE_URL = "https://esaj.tjsp.jus.br"
    SEARCH_URL = f"{BASE_URL}/cpopg/search.do"
    
    def __init__(self):
        super().__init__()
        self.court_acronym = "TJSP"
    
    def _format_process_number(self, process_number: str) -> str:
        """Formata número do processo para o padrão do TJSP."""
        clean = re.sub(r'\D', '', process_number)
        if len(clean) == 20:
            # Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
            return f"{clean[0:7]}-{clean[7:9]}.{clean[9:13]}.{clean[13]}.{clean[14:16]}.{clean[16:20]}"
        return clean
    
    async def search_process(self, process_number: str) -> Dict[str, Any]:
        """Busca informações básicas do processo no TJSP."""
        formatted_number = self._format_process_number(process_number)
        
        params = {
            "conversationId": "",
            "dadosConsulta.localPesquisa.cdLocal": "-1",
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
            "numeroDigitoAnoUnificado": formatted_number.split('-')[0],
            "foroNumeroUnificado": formatted_number.split('.')[-1],
            "dadosConsulta.valorConsultaNuUnificado": formatted_number,
            "dadosConsulta.valorConsulta": ""
        }
        
        html = await self.fetch(self.SEARCH_URL, method="GET", params=params)
        soup = self.parse_html(html)
        
        # Extrai dados básicos
        data = {
            "process_number": process_number,
            "raw_html": html,
            "scraped_at": datetime.utcnow()
        }
        
        # Assunto
        subject_elem = soup.find("span", {"id": "labelAssuntoProcesso"})
        if subject_elem:
            data["subject"] = self.clean_text(subject_elem.text)
        
        # Classe
        class_elem = soup.find("span", {"id": "classeProcesso"})
        if class_elem:
            data["class_type"] = self.clean_text(class_elem.text)
        
        # Área
        area_elem = soup.find("div", {"id": "areaProcesso"})
        if area_elem:
            data["area"] = self.clean_text(area_elem.find("span").text)
        
        # Distribuição
        dist_elem = soup.find("div", {"id": "dataHoraDistribuicaoProcesso"})
        if dist_elem:
            date_text = self.clean_text(dist_elem.text)
            data["distribution_date"] = self.parse_date(
                date_text,
                ["%d/%m/%Y às %H:%M", "%d/%m/%Y"]
            )
        
        # Juiz
        judge_elem = soup.find("span", {"id": "juizProcesso"})
        if judge_elem:
            data["judge"] = self.clean_text(judge_elem.text)
        
        # Valor da causa
        value_elem = soup.find("div", {"id": "valorAcaoProcesso"})
        if value_elem:
            data["case_value"] = self.clean_text(value_elem.find("span").text)
        
        # Partes
        data["plaintiffs"] = self._extract_parties(soup, "Autor")
        data["defendants"] = self._extract_parties(soup, "Réu")
        data["lawyers"] = self._extract_lawyers(soup)
        
        return data
    
    def _extract_parties(self, soup: BeautifulSoup, party_type: str) -> List[Dict[str, str]]:
        """Extrai partes processuais (autor/réu)."""
        parties = []
        party_table = soup.find("table", {"id": "tablePartesPrincipais"})
        
        if party_table:
            rows = party_table.find_all("tr")
            for row in rows:
                type_cell = row.find("td", {"class": "tipoParteProcesso"})
                if type_cell and party_type.lower() in type_cell.text.lower():
                    name_cell = row.find("td", {"class": "nomeParteProcesso"})
                    if name_cell:
                        parties.append({
                            "type": party_type,
                            "name": self.clean_text(name_cell.text)
                        })
        
        return parties
    
    def _extract_lawyers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extrai advogados."""
        lawyers = []
        lawyer_spans = soup.find_all("span", {"class": "mensagemExibindo"})
        
        for span in lawyer_spans:
            if "Advogad" in span.text:
                lawyer_text = self.clean_text(span.text)
                lawyers.append({
                    "name": lawyer_text,
                    "type": "advogado"
                })
        
        return lawyers
    
    async def get_movements(self, process_number: str) -> List[Dict[str, Any]]:
        """Busca movimentações do processo."""
        formatted_number = self._format_process_number(process_number)
        
        # Faz a mesma busca que search_process
        html = await self.fetch(
            self.SEARCH_URL,
            method="GET",
            params={
                "dadosConsulta.valorConsultaNuUnificado": formatted_number,
                "cbPesquisa": "NUMPROC"
            }
        )
        
        soup = self.parse_html(html)
        movements = []
        
        # Tabela de movimentações
        mov_table = soup.find("tbody", {"id": "tabelaTodasMovimentacoes"})
        if mov_table:
            rows = mov_table.find_all("tr", {"class": "containerMovimentacao"})
            
            for row in rows:
                date_cell = row.find("td", {"class": "dataMovimentacao"})
                desc_cell = row.find("td", {"class": "descricaoMovimentacao"})
                
                if date_cell and desc_cell:
                    movement_date = self.parse_date(
                        self.clean_text(date_cell.text),
                        ["%d/%m/%Y"]
                    )
                    
                    # Extrai tipo e descrição
                    mov_title = desc_cell.find("span", {"class": "tipoMovimentacao"})
                    mov_type = self.clean_text(mov_title.text) if mov_title else "Sem tipo"
                    
                    # Remove o título da descrição
                    if mov_title:
                        mov_title.extract()
                    
                    description = self.clean_text(desc_cell.text)
                    
                    movements.append({
                        "movement_date": movement_date,
                        "movement_type": mov_type,
                        "description": description
                    })
        
        return movements
    
    async def get_documents(self, process_number: str) -> List[Dict[str, Any]]:
        """Busca documentos do processo."""
        # TJSP geralmente requer autenticação para documentos
        # Aqui retornamos lista vazia, mas pode ser implementado com credenciais
        return []