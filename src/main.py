from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
import time
import random
import logging
from data.embrapa_scraper import parse_table_producao, parse_table_processamento_viniferas, parse_table_processamento_americanas_hibridas, parse_table_processamento_uvas_mesa, parse_table_processamento_sem_classificacao

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="API Produção Vinhos EMPRAPA")

BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"


@app.get("/producao", response_class=JSONResponse, summary="Produção anual de vinhos/derivados RS")
async def producao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano da produção (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_02",
        "ano": ano
    }

    max_retries = 5
    base_delay = 5  # seconds
    max_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para o ano {ano}...")
            # Connection timeout: 10s, Read timeout: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()  # Levanta HTTPError para códigos de status 4xx/5xx
            
            logger.info(f"Sucesso ao buscar dados para o ano {ano} na tentativa {attempt + 1}.")
            break  # Sai do loop se a requisição for bem-sucedida
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {resp.status_code} na tentativa {attempt + 1} para o ano {ano}: {e}")
            # Para erros HTTP específicos, pode ser que não valha a pena tentar novamente (ex: 404 Not Found)
            # Aqui estamos tratando todos os HTTPError como potencialmente recuperáveis, mas pode ser ajustado.
            if attempt == max_retries - 1 or (resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429): # 429 Too Many Requests pode ser retentado
                raise HTTPException(status_code=resp.status_code, detail=f"Não foi possível obter dados no site Embrapa (HTTP {resp.status_code}): {e}")
        except requests.RequestException as e:
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa após {max_retries} tentativas: {e}")
        
        # Lógica de backoff exponencial com jitter
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa...")
        time.sleep(delay)
    else: # Executado se o loop terminar sem um 'break' (ou seja, todas as tentativas falharam)
        # Este else é redundante se as exceções dentro do loop sempre levantam HTTPException no último attempt.
        # Mantido para clareza caso a lógica de exceção mude.
        raise HTTPException(status_code=500, detail=f"Falha ao obter dados da Embrapa para o ano {ano} após {max_retries} tentativas.")


    try:
        data = parse_table_producao(resp.text)
    except ValueError as e: # Captura o ValueError específico de parse_table_producao
        logger.error(f"Erro ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    # O site traz os números no formato brasileiro, pode converter para int se quiser aqui

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_litros": data["total_geral_litros"]
    }


@app.get("/processamento/viniferas", response_class=JSONResponse, summary="Processamento anual de uvas viníferas RS")
async def processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_03",
        "subopcao": "subopt_01",
        "ano": ano
    }

    max_retries = 5
    base_delay = 5  # seconds
    max_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para o ano {ano}...")
            # Connection timeout: 10s, Read timeout: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()
            
            logger.info(f"Sucesso ao buscar dados para o ano {ano} na tentativa {attempt + 1}.")
            break
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {resp.status_code} na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1 or (resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429):
                raise HTTPException(status_code=resp.status_code, detail=f"Não foi possível obter dados no site Embrapa (HTTP {resp.status_code}): {e}")
        except requests.RequestException as e:
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa após {max_retries} tentativas: {e}")
        
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa...")
        time.sleep(delay)
    else:
        raise HTTPException(status_code=500, detail=f"Falha ao obter dados da Embrapa para o ano {ano} após {max_retries} tentativas.")

    try:
        data = parse_table_processamento_viniferas(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"]
    }


@app.get("/processamento/americanas_hibridas", response_class=JSONResponse, summary="Processamento anual de uvas americanas e híbridas RS")
async def processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_03",
        "subopcao": "subopt_02",
        "ano": ano
    }

    max_retries = 5
    base_delay = 5  # seconds
    max_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para o ano {ano}...")
            # Connection timeout: 10s, Read timeout: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()
            
            logger.info(f"Sucesso ao buscar dados para o ano {ano} na tentativa {attempt + 1}.")
            break
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {resp.status_code} na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1 or (resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429):
                raise HTTPException(status_code=resp.status_code, detail=f"Não foi possível obter dados no site Embrapa (HTTP {resp.status_code}): {e}")
        except requests.RequestException as e:
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa após {max_retries} tentativas: {e}")
        
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa...")
        time.sleep(delay)
    else:
        raise HTTPException(status_code=500, detail=f"Falha ao obter dados da Embrapa para o ano {ano} após {max_retries} tentativas.")

    try:
        data = parse_table_processamento_americanas_hibridas(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"]
    }


@app.get("/processamento/uvas_mesa", response_class=JSONResponse, summary="Processamento anual de uvas de mesa RS")
async def processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_03",
        "subopcao": "subopt_03",
        "ano": ano
    }

    max_retries = 5
    base_delay = 5  # seconds
    max_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para o ano {ano}...")
            # Connection timeout: 10s, Read timeout: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()
            
            logger.info(f"Sucesso ao buscar dados para o ano {ano} na tentativa {attempt + 1}.")
            break
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {resp.status_code} na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1 or (resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429):
                raise HTTPException(status_code=resp.status_code, detail=f"Não foi possível obter dados no site Embrapa (HTTP {resp.status_code}): {e}")
        except requests.RequestException as e:
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa após {max_retries} tentativas: {e}")
        
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa...")
        time.sleep(delay)
    else:
        raise HTTPException(status_code=500, detail=f"Falha ao obter dados da Embrapa para o ano {ano} após {max_retries} tentativas.")

    try:
        data = parse_table_processamento_uvas_mesa(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"]
    }


@app.get("/processamento/sem_classificacao", response_class=JSONResponse, summary="Processamento anual de uvas sem classificação RS")
async def processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano do processamento (entre 1970 e 2023)")
):
    params = {
        "opcao": "opt_03",
        "subopcao": "subopt_04",
        "ano": ano
    }

    max_retries = 5
    base_delay = 5  # seconds
    max_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} para o ano {ano}...")
            # Connection timeout: 10s, Read timeout: 30s
            resp = requests.get(BASE_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()
            
            logger.info(f"Sucesso ao buscar dados para o ano {ano} na tentativa {attempt + 1}.")
            break
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail=f"Erro de Timeout ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail=f"Erro de Conexão ao acessar Embrapa após {max_retries} tentativas: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {resp.status_code} na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1 or (resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429):
                raise HTTPException(status_code=resp.status_code, detail=f"Não foi possível obter dados no site Embrapa (HTTP {resp.status_code}): {e}")
        except requests.RequestException as e:
            logger.error(f"Erro genérico de requisição na tentativa {attempt + 1} para o ano {ano}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa após {max_retries} tentativas: {e}")
        
        delay = min(base_delay * (2 ** attempt) + random.uniform(1, 3), max_delay)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima tentativa...")
        time.sleep(delay)
    else:
        raise HTTPException(status_code=500, detail=f"Falha ao obter dados da Embrapa para o ano {ano} após {max_retries} tentativas.")

    try:
        data = parse_table_processamento_sem_classificacao(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para o ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML: {e}")

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
