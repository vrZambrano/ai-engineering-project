from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="API Produção Vinhos EMPRAPA")

BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"

def parse_table(html):
    """
    Função auxiliar para extrair dados da tabela de produção.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError("Tabela de dados não encontrada.")

    # Pega cabeçalhos das colunas
    headers = [th.get_text(strip=True) for th in data_table.find_all("th")]

    # Pega os dados da tabela
    items = []
    current_item = None
    for tr in data_table.find("tbody").find_all("tr"): # Iterate only through tbody rows
        tds = tr.find_all("td")
        if len(tds) == 2:
            produto_cell = tds[0]
            quantidade_cell = tds[1]
            
            produto = produto_cell.get_text(strip=True)
            quantidade = quantidade_cell.get_text(strip=True)

            if 'tb_item' in produto_cell.get("class", []):
                # This is a main item
                current_item = {
                    "produto": produto,
                    "quantidade_litros": quantidade,
                    "subitems": []
                }
                items.append(current_item)
            elif 'tb_subitem' in produto_cell.get("class", []) and current_item:
                # This is a subitem, add it to the current main item
                current_item["subitems"].append({
                    "produto": produto,
                    "quantidade_litros": quantidade
                })
            # If it's neither tb_item nor tb_subitem with a current_item, it's ignored as per the new logic

    # Pega total no <tfoot>
    total_l = None
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot:
        tds = tfoot.find_all("td")
        if len(tds) == 2:
            total_l = tds[1].get_text(strip=True)
    
    return {
        "headers": headers,
        "itens": items,
        "total_geral_litros": total_l
    }

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
        data = parse_table(resp.text)
    except ValueError as e: # Captura o ValueError específico de parse_table
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
