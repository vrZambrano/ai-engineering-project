from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, List, Callable, Tuple
import requests
import time
import random
import logging
from fastapi import HTTPException

# Tipagem para a função de processamento de linha
RowProcessor = Callable[[List[Tag], Dict[str, Any]], None]

# Configuração específica para o scraper
BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
logger = logging.getLogger(__name__)

def _parse_generic_table(
    html: str,
    table_description: str,
    expected_headers: List[str] = None,
    row_processor: RowProcessor = None,
    total_processor: Callable[[Tag], Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Função genérica para extrair dados de tabelas HTML da Embrapa.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError(f"Tabela de dados ({table_description}) não encontrada.")

    # Pega cabeçalhos das colunas
    headers_html = data_table.find("thead")
    if not headers_html: # Algumas tabelas podem ter TH diretamente, sem thead
        headers_html = data_table
        
    headers = [th.get_text(strip=True) for th in headers_html.find_all("th", recursive=False)] # recursive=False para pegar só os TH diretos
    if not headers: # Tenta pegar TH de forma mais ampla se não encontrou no nível direto
         headers = [th.get_text(strip=True) for th in data_table.find_all("th")]


    if expected_headers and headers != expected_headers:
        raise ValueError(
            f"Formato do cabeçalho da tabela ({table_description}) não corresponde ao esperado. "
            f"Esperado: {expected_headers}, Obtido: {headers}"
        )

    # Pega os dados da tabela
    items_data = {"items": [], "current_item_ref": None} # Usar um dict para passar current_item por referência
    
    tbody = data_table.find("tbody")
    if not tbody:
        raise ValueError(f"Corpo da tabela ({table_description}) (tbody) não encontrado.")
        
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if row_processor:
            row_processor(tds, items_data) # Passa a referência para items_data

    # Pega totais no <tfoot>
    processed_totals = {}
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot and total_processor:
        processed_totals = total_processor(tfoot)
    
    return {
        "headers": headers,
        "itens": items_data["items"],
        **processed_totals # Adiciona os totais processados ao resultado
    }

# --- Processadores de Linha Específicos ---

def _process_row_producao_comercio(tds: List[Tag], items_data: Dict[str, Any]):
    """Processa uma linha para tabelas de produção ou comercialização."""
    if len(tds) == 2:
        produto_cell = tds[0]
        quantidade_cell = tds[1]
        
        produto = produto_cell.get_text(strip=True)
        quantidade = quantidade_cell.get_text(strip=True)

        if 'tb_item' in produto_cell.get("class", []):
            # Este é um item principal
            items_data["current_item_ref"] = {
                "produto": produto,
                "quantidade_litros": quantidade, # Assumindo litros para generalização
                "subitems": []
            }
            items_data["items"].append(items_data["current_item_ref"])
        elif 'tb_subitem' in produto_cell.get("class", []) and items_data["current_item_ref"]:
            # Este é um subitem, adiciona ao item principal atual
            items_data["current_item_ref"]["subitems"].append({
                "produto": produto,
                "quantidade_litros": quantidade # Assumindo litros
            })

def _process_row_importacao(tds: List[Tag], items_data: Dict[str, Any]):
    """Processa uma linha para tabelas de importação/exportação."""
    if len(tds) == 3: # País, Quantidade, Valor
        pais = tds[0].get_text(strip=True)
        quantidade_kg = tds[1].get_text(strip=True)
        valor_us = tds[2].get_text(strip=True)
        
        # Tratar casos onde a quantidade/valor pode ser '-' ou vazia
        quantidade_kg = "0" if quantidade_kg == '-' or not quantidade_kg.strip() else quantidade_kg
        valor_us = "0" if valor_us == '-' or not valor_us.strip() else valor_us

        items_data["items"].append({
            "pais": pais,
            "quantidade_kg": quantidade_kg,
            "valor_usd": valor_us # Mantendo 'valor_usd' para consistência com o original
        })
    elif len(tds) == 1 and 'tb_item' in tds[0].get("class", []):
        # Lida com casos como "Não consta na tabela" ou "Outros"
        # Por enquanto, ignora ou pode ser tratado como um item especial se necessário.
        pass

# --- Processadores de Total Específicos ---

def _process_total_producao_comercio(tfoot: Tag) -> Dict[str, Any]:
    """Processa o rodapé (total) para tabelas de produção ou comercialização."""
    tds_foot = tfoot.find_all("td")
    total_val = None
    if len(tds_foot) == 2:
        total_val = tds_foot[1].get_text(strip=True)
    return {"total_geral_litros": total_val} # Assumindo litros

def _process_total_importacao(tfoot: Tag) -> Dict[str, Any]:
    """Processa o rodapé (total) para tabelas de importação/exportação."""
    tds_foot = tfoot.find_all("td")
    total_kg_val = None
    total_valor_us_val = None
    if len(tds_foot) == 3: # Espera-se "Total", "Total Quantidade", "Total Valor"
        total_kg_val = tds_foot[1].get_text(strip=True)
        total_valor_us_val = tds_foot[2].get_text(strip=True)
        
        total_kg_val = "0" if total_kg_val == '-' or not total_kg_val.strip() else total_kg_val
        total_valor_us_val = "0" if total_valor_us_val == '-' or not total_valor_us_val.strip() else total_valor_us_val
    return {
        "total_geral_kg": total_kg_val,
        "total_geral_valor_us": total_valor_us_val
    }

# --- Processadores para Tabelas de Processamento ---

def _process_row_processamento_categoria_cultivar(tds: List[Tag], items_data: Dict[str, Any]):
    """Processa uma linha para tabelas de processamento com categorias e cultivares."""
    if len(tds) == 2:
        cultivar_cell = tds[0]
        quantidade_cell = tds[1]
        
        cultivar_nome = cultivar_cell.get_text(strip=True)
        quantidade = quantidade_cell.get_text(strip=True)

        if 'tb_item' in cultivar_cell.get("class", []):
            # Este é um item principal de categoria (ex: "TINTAS")
            items_data["current_item_ref"] = {
                "categoria": cultivar_nome,
                "quantidade_kg": quantidade, # Quantidade da categoria (geralmente 0 ou total da categoria)
                "cultivares": []
            }
            items_data["items"].append(items_data["current_item_ref"])
        elif 'tb_subitem' in cultivar_cell.get("class", []) and items_data["current_item_ref"]:
            # Este é um subitem (cultivar específico)
            items_data["current_item_ref"]["cultivares"].append({
                "cultivar": cultivar_nome,
                "quantidade_kg": quantidade
            })

def _process_row_processamento_sem_classificacao(tds: List[Tag], items_data: Dict[str, Any]):
    """Processa uma linha para tabela de processamento sem classificação."""
    if len(tds) == 2:
        item_cell = tds[0]
        quantidade_cell = tds[1]
        
        item_nome = item_cell.get_text(strip=True)
        quantidade = quantidade_cell.get_text(strip=True)

        if 'tb_item' in item_cell.get("class", []):
            # Para sem classificação, é apenas um item simples
            items_data["items"].append({
                "item": item_nome,
                "quantidade_kg": quantidade
            })

def _process_total_kg(tfoot: Tag) -> Dict[str, Any]:
    """Processa o rodapé (total) para tabelas que totalizam em Kg."""
    tds_foot = tfoot.find_all("td")
    total_kg_val = None
    if len(tds_foot) == 2: # Espera-se "Total", "Total Quantidade (Kg)"
        total_kg_val = tds_foot[1].get_text(strip=True)
        total_kg_val = "0" if total_kg_val == '-' or not total_kg_val.strip() else total_kg_val
    return {"total_geral_kg": total_kg_val}

# --- Função de Fetch de Dados ---

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

# --- Funções de Parsing Refatoradas ---

def parse_table_producao(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de produção.
    """
    return _parse_generic_table(
        html=html,
        table_description="Produção",
        # expected_headers=["Produto", "Quantidade (L)"], # Cabeçalhos podem variar (ex: "Produtos")
        row_processor=_process_row_producao_comercio,
        total_processor=_process_total_producao_comercio
    )


def parse_table_processamento_viniferas(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de processamento de uvas viníferas.
    """
    return _parse_generic_table(
        html=html,
        table_description="Processamento Viníferas",
        expected_headers=["Cultivar", "Quantidade (Kg)"],
        row_processor=_process_row_processamento_categoria_cultivar,
        total_processor=_process_total_kg
    )

def parse_table_importacao(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de importação (opcao=opt_05).
    Também usada para exportação.
    """
    return _parse_generic_table(
        html=html,
        table_description="Importação/Exportação",
        expected_headers=["Países", "Quantidade (Kg)", "Valor (US$)"],
        row_processor=_process_row_importacao,
        total_processor=_process_total_importacao
    )

def parse_table_comercializacao(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de comercialização.
    """
    # A estrutura é idêntica à de produção
    result = _parse_generic_table(
        html=html,
        table_description="Comercialização",
        # expected_headers=["Produto", "Quantidade (L)"], # Cabeçalhos podem variar
        row_processor=_process_row_producao_comercio,
        total_processor=_process_total_producao_comercio 
    )
    # A chave do total é 'total_geral_litros', já tratada por _process_total_producao_comercio
    return result


def parse_table_processamento_sem_classificacao(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de processamento de uvas sem classificação.
    """
    return _parse_generic_table(
        html=html,
        table_description="Processamento Sem Classificação",
        expected_headers=["Sem definição", "Quantidade (Kg)"],
        row_processor=_process_row_processamento_sem_classificacao,
        total_processor=_process_total_kg
    )

def parse_table_processamento_uvas_mesa(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de processamento de uvas de mesa.
    """
    return _parse_generic_table(
        html=html,
        table_description="Processamento Uvas de Mesa",
        expected_headers=["Cultivar", "Quantidade (Kg)"],
        row_processor=_process_row_processamento_categoria_cultivar,
        total_processor=_process_total_kg
    )

def parse_table_processamento_americanas_hibridas(html: str) -> Dict[str, Any]:
    """
    Função para extrair dados da tabela de processamento de uvas americanas e híbridas.
    """
    return _parse_generic_table(
        html=html,
        table_description="Processamento Americanas e Híbridas",
        expected_headers=["Cultivar", "Quantidade (Kg)"],
        row_processor=_process_row_processamento_categoria_cultivar,
        total_processor=_process_total_kg
    )


# --- Funções de Alto Nível que Combinam Fetch e Parse ---

async def fetch_and_parse_producao(ano: int) -> Dict[str, Any]:
    """
    Busca e processa dados de produção para um ano específico.
    """
    params = {
        "opcao": "opt_02",
        "ano": ano
    }
    operation_description = f"produção (opção: {params['opcao']})"
    
    resp = await _fetch_embrapa_data(params, ano, operation_description)
    
    try:
        data = parse_table_producao(resp.text)
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


async def fetch_and_parse_comercializacao(ano: int) -> Dict[str, Any]:
    """
    Busca e processa dados de comercialização para um ano específico.
    """
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


async def fetch_and_parse_processamento(subopcao: str, ano: int, tipo_processamento: str) -> Dict[str, Any]:
    """
    Busca e processa dados de processamento de uvas para um ano específico.
    """
    params = {
        "opcao": "opt_03",
        "subopcao": subopcao,
        "ano": ano
    }
    operation_description = f"processamento {tipo_processamento} (opção: {params['opcao']}, subopção: {params['subopcao']})"
    
    resp = await _fetch_embrapa_data(params, ano, operation_description)
    
    # Mapear subopção para função de parsing
    parser_map = {
        "subopt_01": parse_table_processamento_viniferas,
        "subopt_02": parse_table_processamento_americanas_hibridas,
        "subopt_03": parse_table_processamento_uvas_mesa,
        "subopt_04": parse_table_processamento_sem_classificacao
    }
    
    parser_func = parser_map.get(subopcao)
    if not parser_func:
        raise HTTPException(status_code=400, detail=f"Subopção de processamento inválida: {subopcao}")
    
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


async def fetch_and_parse_comex(opcao_param: str, subopcao: str, ano: int, tipo_operacao: str) -> Dict[str, Any]:
    """
    Busca e processa dados de Comércio Exterior (Importação/Exportação) para um ano específico.
    """
    params = {
        "opcao": opcao_param,
        "subopcao": subopcao,
        "ano": ano
    }
    operation_description = f"{tipo_operacao} {subopcao} (opção: {params['opcao']}, subopção: {params['subopcao']})"
    
    resp = await _fetch_embrapa_data(params, ano, operation_description)
    
    try:
        data = parse_table_importacao(resp.text)
    except ValueError as e:
        logger.error(f"Erro ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML (tabela de {tipo_operacao} não encontrada ou formato inesperado): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar HTML para {operation_description}, ano {ano}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar HTML ({tipo_operacao}): {e}")
    
    # Define o mapeamento de nome do produto baseado na subopção
    product_mapping = {
        "subopt_01": "vinho-mesa",
        "subopt_02": "espumante",
        "subopt_03": "uvas-frescas",
        "subopt_04": "uvas-passas",  # Usado por importacao. Para exportacao, subopt_04 é suco-uva.
        "subopt_05": "suco-uva"     # Usado por importacao
    }
    
    # Ajuste específico para exportação de suco de uva, que usa subopt_04
    if tipo_operacao == "exportação" and subopcao == "subopt_04":
        tipo_produto_nome = "suco-uva"
    else:
        tipo_produto_nome = product_mapping.get(subopcao, subopcao)
    
    return {
        "ano": ano,
        "tipo_produto": tipo_produto_nome,
        "dados": data["itens"],
        "total_geral_kg": data["total_geral_kg"],
        "total_geral_valor_us": data["total_geral_valor_us"]
    }
