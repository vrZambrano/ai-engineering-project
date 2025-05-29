from pydantic import BaseModel, Field
from typing import List, Optional


class SubItem(BaseModel):
    """Modelo para subitens de produção/comercialização."""
    produto: str
    quantidade_litros: str


class ItemProducaoComercio(BaseModel):
    """Modelo para itens de produção ou comercialização."""
    produto: str
    quantidade_litros: str
    subitems: List[SubItem] = []


class ProducaoResponse(BaseModel):
    """Modelo de resposta para endpoints de produção."""
    ano: int
    dados: List[ItemProducaoComercio]
    total_geral_litros: Optional[str] = None


class ComercializacaoResponse(BaseModel):
    """Modelo de resposta para endpoints de comercialização."""
    ano: int
    dados: List[ItemProducaoComercio]
    total_geral_litros: Optional[str] = None


class Cultivar(BaseModel):
    """Modelo para cultivares em processamento."""
    cultivar: str
    quantidade_kg: str


class CategoriaProcessamento(BaseModel):
    """Modelo para categorias de processamento com cultivares."""
    categoria: str
    quantidade_kg: str
    cultivares: List[Cultivar] = []


class ItemProcessamentoSemClassificacao(BaseModel):
    """Modelo para itens de processamento sem classificação."""
    item: str
    quantidade_kg: str


class ProcessamentoResponse(BaseModel):
    """Modelo de resposta para endpoints de processamento."""
    ano: int
    tipo_processamento: str
    dados: List[CategoriaProcessamento]
    total_geral_kg: Optional[str] = None


class ProcessamentoSemClassificacaoResponse(BaseModel):
    """Modelo de resposta para processamento sem classificação."""
    ano: int
    tipo_processamento: str
    dados: List[ItemProcessamentoSemClassificacao]
    total_geral_kg: Optional[str] = None


class PaisImportacaoExportacao(BaseModel):
    """Modelo para países em importação/exportação."""
    pais: str
    quantidade_kg: str
    valor_usd: str


class ImportacaoExportacaoResponse(BaseModel):
    """Modelo de resposta para endpoints de importação/exportação."""
    ano: int
    tipo_produto: str
    dados: List[PaisImportacaoExportacao]
    total_geral_kg: Optional[str] = None
    total_geral_valor_us: Optional[str] = None
