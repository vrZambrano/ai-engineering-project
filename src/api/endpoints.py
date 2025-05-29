from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from api.models import (
    ProducaoResponse, 
    ComercializacaoResponse, 
    ProcessamentoResponse, 
    ProcessamentoSemClassificacaoResponse,
    ImportacaoExportacaoResponse
)
from data.embrapa_scraper import (
    fetch_and_parse_producao,
    fetch_and_parse_comercializacao,
    fetch_and_parse_processamento,
    fetch_and_parse_comex
)

router = APIRouter()


@router.get("/producao", response_model=ProducaoResponse, response_class=JSONResponse, summary="Produção anual de vinhos/derivados RS")
async def producao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano da produção (entre 1970 e 2023)")
):
    return await fetch_and_parse_producao(ano)


@router.get("/comercializacao", response_model=ComercializacaoResponse, response_class=JSONResponse, summary="Comercialização anual de vinhos e derivados RS")
async def comercializacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano da comercialização (entre 1970 e 2023)")
):
    return await fetch_and_parse_comercializacao(ano)


@router.get("/processamento/viniferas", response_model=ProcessamentoResponse, response_class=JSONResponse, summary="Processamento anual de uvas viníferas RS")
async def processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await fetch_and_parse_processamento("subopt_01", ano, "viníferas")


@router.get("/processamento/americanas-hibridas", response_model=ProcessamentoResponse, response_class=JSONResponse, summary="Processamento anual de uvas americanas e híbridas RS")
async def processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await fetch_and_parse_processamento("subopt_02", ano, "americanas-híbridas")


@router.get("/processamento/uvas-mesa", response_model=ProcessamentoResponse, response_class=JSONResponse, summary="Processamento anual de uvas de mesa RS")
async def processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await fetch_and_parse_processamento("subopt_03", ano, "uvas-mesa")


@router.get("/processamento/sem-classificacao", response_model=ProcessamentoSemClassificacaoResponse, response_class=JSONResponse, summary="Processamento anual de uvas sem classificação RS")
async def processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await fetch_and_parse_processamento("subopt_04", ano, "sem-classificação")


# --- Endpoints de Importação ---
@router.get("/importacao/vinho-mesa", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Importação anual de vinhos de mesa")
async def importacao_vinho_mesa(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_05", "subopt_01", ano, "importação")


@router.get("/importacao/espumante", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Importação anual de espumantes")
async def importacao_espumante(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_05", "subopt_02", ano, "importação")


@router.get("/importacao/uvas-frescas", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Importação anual de uvas frescas")
async def importacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_05", "subopt_03", ano, "importação")


@router.get("/importacao/uvas-passas", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Importação anual de uvas passas")
async def importacao_uvas_passas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_05", "subopt_04", ano, "importação")


@router.get("/importacao/suco-uva", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Importação anual de suco de uva")
async def importacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_05", "subopt_05", ano, "importação")


# --- Endpoints de Exportação ---
@router.get("/exportacao/vinho-mesa", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Exportação anual de vinhos de mesa")
async def exportacao_vinho_mesa(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_06", "subopt_01", ano, "exportação")


@router.get("/exportacao/espumante", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Exportação anual de espumantes")
async def exportacao_espumante(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_06", "subopt_02", ano, "exportação")


@router.get("/exportacao/uvas-frescas", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Exportação anual de uvas frescas")
async def exportacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await fetch_and_parse_comex("opt_06", "subopt_03", ano, "exportação")


@router.get("/exportacao/suco-uva", response_model=ImportacaoExportacaoResponse, response_class=JSONResponse, summary="Exportação anual de suco de uva")
async def exportacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    # Exportação usa subopt_04 para suco de uva
    return await fetch_and_parse_comex("opt_06", "subopt_04", ano, "exportação")
