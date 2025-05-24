from bs4 import BeautifulSoup
from typing import Dict, Any

def parse_table_producao(html):
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

def parse_table_processamento_viniferas(html: str) -> Dict[str, Any]:
    """
    Função auxiliar para extrair dados da tabela de processamento de uvas viníferas.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError("Tabela de dados não encontrada.")

    # Pega cabeçalhos das colunas
    headers = [th.get_text(strip=True) for th in data_table.find_all("th")]
    if headers != ["Cultivar", "Quantidade (Kg)"]:
        raise ValueError("Formato da tabela não corresponde ao esperado para processamento de viníferas.")

    # Pega os dados da tabela
    items = []
    current_item = None
    for tr in data_table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            cultivar_cell = tds[0]
            quantidade_cell = tds[1]
            
            cultivar = cultivar_cell.get_text(strip=True)
            quantidade = quantidade_cell.get_text(strip=True)

            if 'tb_item' in cultivar_cell.get("class", []):
                # This is a main item (e.g., "TINTAS", "BRANCAS E ROSADAS")
                current_item = {
                    "categoria": cultivar,
                    "quantidade_kg": quantidade,
                    "cultivares": []
                }
                items.append(current_item)
            elif 'tb_subitem' in cultivar_cell.get("class", []) and current_item:
                # This is a subitem (specific cultivar)
                current_item["cultivares"].append({
                    "cultivar": cultivar,
                    "quantidade_kg": quantidade
                })

    # Pega total no <tfoot>
    total_kg = None
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot:
        tds = tfoot.find_all("td")
        if len(tds) == 2:
            total_kg = tds[1].get_text(strip=True)
    
    return {
        "headers": headers,
        "itens": items,
        "total_geral_kg": total_kg
    }

def parse_table_processamento_sem_classificacao(html: str) -> Dict[str, Any]:
    """
    Função auxiliar para extrair dados da tabela de processamento de uvas sem classificação.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError("Tabela de dados não encontrada.")

    # Pega cabeçalhos das colunas
    headers = [th.get_text(strip=True) for th in data_table.find_all("th")]
    if headers != ["Sem definição", "Quantidade (Kg)"]:
        raise ValueError("Formato da tabela não corresponde ao esperado para processamento sem classificação.")

    # Pega os dados da tabela - estrutura mais simples, apenas um item
    items = []
    for tr in data_table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            item_cell = tds[0]
            quantidade_cell = tds[1]
            
            item = item_cell.get_text(strip=True)
            quantidade = quantidade_cell.get_text(strip=True)

            if 'tb_item' in item_cell.get("class", []):
                # Para sem classificação, é apenas um item simples
                items.append({
                    "item": item,
                    "quantidade_kg": quantidade
                })

    # Pega total no <tfoot>
    total_kg = None
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot:
        tds = tfoot.find_all("td")
        if len(tds) == 2:
            total_kg = tds[1].get_text(strip=True)
    
    return {
        "headers": headers,
        "itens": items,
        "total_geral_kg": total_kg
    }

def parse_table_processamento_uvas_mesa(html: str) -> Dict[str, Any]:
    """
    Função auxiliar para extrair dados da tabela de processamento de uvas de mesa.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError("Tabela de dados não encontrada.")

    # Pega cabeçalhos das colunas
    headers = [th.get_text(strip=True) for th in data_table.find_all("th")]
    if headers != ["Cultivar", "Quantidade (Kg)"]:
        raise ValueError("Formato da tabela não corresponde ao esperado para processamento de uvas de mesa.")

    # Pega os dados da tabela
    items = []
    current_item = None
    for tr in data_table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            cultivar_cell = tds[0]
            quantidade_cell = tds[1]
            
            cultivar = cultivar_cell.get_text(strip=True)
            quantidade = quantidade_cell.get_text(strip=True)

            if 'tb_item' in cultivar_cell.get("class", []):
                # This is a main item (e.g., "TINTAS", "BRANCAS")
                current_item = {
                    "categoria": cultivar,
                    "quantidade_kg": quantidade,
                    "cultivares": []
                }
                items.append(current_item)
            elif 'tb_subitem' in cultivar_cell.get("class", []) and current_item:
                # This is a subitem (specific cultivar)
                current_item["cultivares"].append({
                    "cultivar": cultivar,
                    "quantidade_kg": quantidade
                })

    # Pega total no <tfoot>
    total_kg = None
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot:
        tds = tfoot.find_all("td")
        if len(tds) == 2:
            total_kg = tds[1].get_text(strip=True)
    
    return {
        "headers": headers,
        "itens": items,
        "total_geral_kg": total_kg
    }

def parse_table_processamento_americanas_hibridas(html: str) -> Dict[str, Any]:
    """
    Função auxiliar para extrair dados da tabela de processamento de uvas americanas e híbridas.
    """
    soup = BeautifulSoup(html, "html.parser")
    data_table = soup.find("table", class_="tb_base tb_dados")
    if not data_table:
        raise ValueError("Tabela de dados não encontrada.")

    # Pega cabeçalhos das colunas
    headers = [th.get_text(strip=True) for th in data_table.find_all("th")]
    if headers != ["Cultivar", "Quantidade (Kg)"]:
        raise ValueError("Formato da tabela não corresponde ao esperado para processamento de americanas e híbridas.")

    # Pega os dados da tabela
    items = []
    current_item = None
    for tr in data_table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            cultivar_cell = tds[0]
            quantidade_cell = tds[1]
            
            cultivar = cultivar_cell.get_text(strip=True)
            quantidade = quantidade_cell.get_text(strip=True)

            if 'tb_item' in cultivar_cell.get("class", []):
                # This is a main item (e.g., "TINTAS", "BRANCAS E ROSADAS")
                current_item = {
                    "categoria": cultivar,
                    "quantidade_kg": quantidade,
                    "cultivares": []
                }
                items.append(current_item)
            elif 'tb_subitem' in cultivar_cell.get("class", []) and current_item:
                # This is a subitem (specific cultivar)
                current_item["cultivares"].append({
                    "cultivar": cultivar,
                    "quantidade_kg": quantidade
                })

    # Pega total no <tfoot>
    total_kg = None
    tfoot = data_table.find("tfoot", class_="tb_total")
    if tfoot:
        tds = tfoot.find_all("td")
        if len(tds) == 2:
            total_kg = tds[1].get_text(strip=True)
    
    return {
        "headers": headers,
        "itens": items,
        "total_geral_kg": total_kg
    }
