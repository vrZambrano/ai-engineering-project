from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, List, Callable, Tuple

# Tipagem para a função de processamento de linha
RowProcessor = Callable[[List[Tag], Dict[str, Any]], None]

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
