from pydantic import BaseModel, Field
from typing import List, Optional


class SubItem(BaseModel):
    """Modelo para subitens de produção/comercialização."""
    produto: str = Field(..., description="Nome do produto")
    quantidade_litros: str = Field(..., description="Quantidade em litros")


class ItemProducaoComercio(BaseModel):
    """Modelo para itens de produção ou comercialização."""
    produto: str = Field(..., description="Nome do produto")
    quantidade_litros: str = Field(..., description="Quantidade em litros")
    subitems: List[SubItem] = Field(default=[], description="Lista de subitens do produto")


class ProducaoResponse(BaseModel):
    """Modelo de resposta para endpoints de produção."""
    ano: int = Field(..., description="Ano da produção")
    dados: List[ItemProducaoComercio] = Field(..., description="Lista de dados de produção")
    total_geral_litros: Optional[str] = Field(None, description="Total geral em litros")


class ComercializacaoResponse(BaseModel):
    """Modelo de resposta para endpoints de comercialização."""
    ano: int = Field(..., description="Ano da comercialização")
    dados: List[ItemProducaoComercio] = Field(..., description="Lista de dados de comercialização")
    total_geral_litros: Optional[str] = Field(None, description="Total geral em litros")


class Cultivar(BaseModel):
    """Modelo para cultivares em processamento."""
    cultivar: str = Field(..., description="Nome da cultivar")
    quantidade_kg: str = Field(..., description="Quantidade em quilogramas")


class CategoriaProcessamento(BaseModel):
    """Modelo para categorias de processamento com cultivares."""
    categoria: str = Field(..., description="Nome da categoria")
    quantidade_kg: str = Field(..., description="Quantidade total em quilogramas")
    cultivares: List[Cultivar] = Field(default=[], description="Lista de cultivares da categoria")


class ItemProcessamentoSemClassificacao(BaseModel):
    """Modelo para itens de processamento sem classificação."""
    item: str = Field(..., description="Nome do item")
    quantidade_kg: str = Field(..., description="Quantidade em quilogramas")


class ProcessamentoResponse(BaseModel):
    """Modelo de resposta para endpoints de processamento."""
    ano: int = Field(..., description="Ano do processamento")
    tipo_processamento: str = Field(..., description="Tipo de processamento (viníferas, americanas-híbridas, etc.)")
    dados: List[CategoriaProcessamento] = Field(..., description="Lista de dados de processamento")
    total_geral_kg: Optional[str] = Field(None, description="Total geral em quilogramas")


class ProcessamentoSemClassificacaoResponse(BaseModel):
    """Modelo de resposta para processamento sem classificação."""
    ano: int = Field(..., description="Ano do processamento")
    tipo_processamento: str = Field(..., description="Tipo de processamento")
    dados: List[ItemProcessamentoSemClassificacao] = Field(..., description="Lista de itens sem classificação")
    total_geral_kg: Optional[str] = Field(None, description="Total geral em quilogramas")


class PaisImportacaoExportacao(BaseModel):
    """Modelo para países em importação/exportação."""
    pais: str = Field(..., description="Nome do país")
    quantidade_kg: str = Field(..., description="Quantidade em quilogramas")
    valor_usd: str = Field(..., description="Valor em dólares americanos")


class ImportacaoExportacaoResponse(BaseModel):
    """Modelo de resposta para endpoints de importação/exportação."""
    ano: int = Field(..., description="Ano da importação/exportação")
    tipo_produto: str = Field(..., description="Tipo de produto (vinho de mesa, espumante, etc.)")
    dados: List[PaisImportacaoExportacao] = Field(..., description="Lista de dados por país")
    total_geral_kg: Optional[str] = Field(None, description="Total geral em quilogramas")
    total_geral_valor_us: Optional[str] = Field(None, description="Total geral em dólares americanos")
