from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
import time
import random
import logging
from data.embrapa_scraper import parse_table_producao, parse_table_processamento_viniferas, parse_table_processamento_americanas_hibridas, parse_table_processamento_uvas_mesa, parse_table_processamento_sem_classificacao, parse_table_comercializacao, parse_table_importacao

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="API Produção Vinhos EMBRAPA")

BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"


async def _fetch_embrapa_data(params: dict, ano: int, operation_description: str) -> requests.Response:
    """
    Função auxiliar para buscar dados da Embrapa com lógica de retry.
    operation_description é usado para logging e mensagens de erro.
    Retorna o objeto Response em caso de sucesso, ou levanta HTTPException.
    """
    max_retries = 5
    base_delay = 5  # segundos
    max_delay = 60  # segundos
    resp = None # Inicializa resp como None

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para {operation_description}, ano {ano}...")
            # Timeout de conexão: 10s, Timeout de leitura: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()  # Levanta HTTPError para códigos de status 4xx/5xx
            
            logger.info(f"Sucesso ao buscar dados para {operation_description}, ano {ano} na tentativa {attempt + 1}.")
            return resp # Retorna a resposta em caso de sucesso
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para {operation_description}, ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa ({operation_description}) após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para {operation_description}, ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa ({operation_description}) após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            status_code_val = resp.status_code if resp else "N/A"
            logger.error(f"Erro HTTP {status_code_val} na tentativa {attempt + 1} para {operation_description}, ano {ano}: {e}")
            # Para erros HTTP específicos, pode ser que não valha a pena tentar novamente (ex: 404 Not Found)
            if attempt == max_retries - 1 or (resp and resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429): # 429 Too Many Requests (Muitas Requisições) pode ser retentado
                raise HTTPException(status_code=resp.status_code if resp else 500, detail=f"Não foi possível obter dados no site Embrapa ({operation_description}, HTTP {status_code_val}): {e}")
        except requests.RequestException as e: # Captura outras exceções de requests (ex: InvalidURL)
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para {operation_description}, ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa ({operation_description}) após {max_retries} tentativas: {e}")
        
        # Lógica de backoff exponencial com jitter
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa para {operation_description}, ano {ano}...")
        time.sleep(delay)
    
    # Este ponto só deve ser alcançado se algo inesperado ocorrer e o loop terminar sem retornar ou levantar exceção.
    # As exceções dentro do loop devem cobrir o caso de falha na última tentativa.
    raise HTTPException(status_code=500, detail=f"Falha crítica ao obter dados da Embrapa para {operation_description}, ano {ano} após {max_retries} tentativas.")


@app.get("/producao", response_class=JSONResponse, summary="Produção anual de vinhos/derivados RS")
async def producao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano da produção (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_02",
        "ano": ano
    }
    operation_description = f"produção (opção: {params['opcao']})"

    resp = await _fetch_embrapa_data(params, ano, operation_description)

    try:
        data = parse_table_producao(resp.text)
    except ValueError as e: # Captura o ValueError específico de parse_table_producao
        logger.error(f"Erro ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    # O site traz os números no formato brasileiro; podem ser convertidos para int aqui, se desejado.

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_litros": data["total_geral_litros"]
    }


@app.get("/processamento/viniferas", response_class=JSONResponse, summary="Processamento anual de uvas viníferas RS")
async def processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await get_processamento_data("subopt_01", ano, "viníferas", parse_table_processamento_viniferas)


@app.get("/processamento/americanas-hibridas", response_class=JSONResponse, summary="Processamento anual de uvas americanas e híbridas RS")
async def processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await get_processamento_data("subopt_02", ano, "americanas e híbridas", parse_table_processamento_americanas_hibridas)


@app.get("/processamento/uvas-mesa", response_class=JSONResponse, summary="Processamento anual de uvas de mesa RS")
async def processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await get_processamento_data("subopt_03", ano, "uvas de mesa", parse_table_processamento_uvas_mesa)


@app.get("/processamento/sem-classificacao", response_class=JSONResponse, summary="Processamento anual de uvas sem classificação RS")
async def processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    return await get_processamento_data("subopt_04", ano, "sem classificação", parse_table_processamento_sem_classificacao)


@app.get("/comercializacao", response_class=JSONResponse, summary="Comercialização anual de vinhos e derivados RS")
async def comercializacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano da comercialização (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_04",
        "ano": ano
    }
    operation_description = f"comercialização (opção: {params['opcao']})"
    
    resp = await _fetch_embrapa_data(params, ano, operation_description)

    try:
        data = parse_table_comercializacao(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_litros": data["total_geral_litros"]
    }


# --- Função auxiliar para endpoints de Processamento ---

async def get_processamento_data(subopcao: str, ano: int, tipo_processamento: str, parser_func):
    """
    Função auxiliar para buscar e processar dados de processamento de uvas.
    tipo_processamento é usado para logs e mensagens de erro.
    parser_func é a função específica de parsing para cada tipo de processamento.
    """
    params = {
        "opcao": "opt_03",  # Todos os processamentos usam opt_03
        "subopcao": subopcao,
        "ano": ano
    }
    operation_description = f"processamento {tipo_processamento} (opção: {params['opcao']}, subopção: {params['subopcao']})"

    resp = await _fetch_embrapa_data(params, ano, operation_description)
    
    if resp is None: # Verificação adicional, embora _fetch_embrapa_data deva levantar exceção
        raise HTTPException(status_code=500, detail=f"Resposta não obtida da Embrapa para {operation_description}, ano {ano}.")

    try:
        data = parser_func(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela de {tipo_processamento} não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML ({tipo_processamento}): {e}")

    return {
        "ano": ano,
        "tipo_processamento": tipo_processamento,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"]
    }

# --- Início dos endpoints de Comércio Exterior (Importação/Exportação) ---

async def get_comex_data(opcao_param: str, subopcao: str, ano: int, tipo_operacao: str):
    """
    Função auxiliar para buscar e processar dados de Comércio Exterior (Importação/Exportação).
    tipo_operacao é "importação" ou "exportação" para logs e mensagens de erro.
    """
    params = {
        "opcao": opcao_param,
        "subopcao": subopcao,
        "ano": ano
    }
    operation_description = f"{tipo_operacao} {subopcao} (opção: {params['opcao']}, subopção: {params['subopcao']})"

    resp = await _fetch_embrapa_data(params, ano, operation_description)
    
    if resp is None: # Verificação adicional, embora _fetch_embrapa_data deva levantar exceção
        raise HTTPException(status_code=500, detail=f"Resposta não obtida da Embrapa para {operation_description}, ano {ano}.")

    try:
        # parse_table_importacao é genérica o suficiente para importação e exportação, conforme estrutura atual
        data = parse_table_importacao(resp.text) 
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela de {tipo_operacao} não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML ({tipo_operacao}): {e}")

    # Define o mapeamento de nome do produto baseado na subopção
    product_mapping = {
        "subopt_01": "vinho-mesa", # Padronizado
        "subopt_02": "espumante",
        "subopt_03": "uvas-frescas", # Padronizado
        "subopt_04": "uvas-passas", # Usado por importacao. Para exportacao, subopt_04 é suco-uva.
        "subopt_05": "suco-uva"     # Usado por importacao
    }
    
    # Ajuste específico para exportação de suco de uva, que usa subopt_04
    if tipo_operacao == "exportação" and subopcao == "subopt_04":
        tipo_produto_nome = "suco-uva"
    else:
        tipo_produto_nome = product_mapping.get(subopcao, subopcao) # Fallback para subopcao se não estiver no mapa

    return {
        "ano": ano,
        "tipo_produto": tipo_produto_nome,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"],
        "total_geral_valor_us": data["total_geral_valor_us"]
    }

# --- Endpoints de Importação ---
@app.get("/importacao/vinho-mesa", response_class=JSONResponse, summary="Importação anual de vinhos de mesa")
async def importacao_vinho_mesa(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_05", "subopt_01", ano, "importação")

@app.get("/importacao/espumante", response_class=JSONResponse, summary="Importação anual de espumantes")
async def importacao_espumante(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_05", "subopt_02", ano, "importação")

@app.get("/importacao/uvas-frescas", response_class=JSONResponse, summary="Importação anual de uvas frescas")
async def importacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_05", "subopt_03", ano, "importação")

@app.get("/importacao/uvas-passas", response_class=JSONResponse, summary="Importação anual de uvas passas")
async def importacao_uvas_passas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_05", "subopt_04", ano, "importação")

@app.get("/importacao/suco-uva", response_class=JSONResponse, summary="Importação anual de suco de uva")
async def importacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da importação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_05", "subopt_05", ano, "importação")


# --- Endpoints de Exportação ---
@app.get("/exportacao/vinho-mesa", response_class=JSONResponse, summary="Exportação anual de vinhos de mesa")
async def exportacao_vinho_mesa(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_06", "subopt_01", ano, "exportação")

@app.get("/exportacao/espumante", response_class=JSONResponse, summary="Exportação anual de espumantes")
async def exportacao_espumante(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_06", "subopt_02", ano, "exportação")

@app.get("/exportacao/uvas-frescas", response_class=JSONResponse, summary="Exportação anual de uvas frescas")
async def exportacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    return await get_comex_data("opt_06", "subopt_03", ano, "exportação")

@app.get("/exportacao/suco-uva", response_class=JSONResponse, summary="Exportação anual de suco de uva")
async def exportacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2024, description="Ano da exportação (entre 1970 e 2024)")
):
    # Exportação usa subopt_04 para suco de uva
    return await get_comex_data("opt_06", "subopt_04", ano, "exportação")

# --- Fim dos endpoints de Comércio Exterior (Importação/Exportação) ---


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
