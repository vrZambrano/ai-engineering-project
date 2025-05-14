from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

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
    for tr in data_table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            produto = tds[0].get_text(strip=True)
            quantidade = tds[1].get_text(strip=True)
            items.append({
                "produto": produto,
                "quantidade_litros": quantidade
            })

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
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar Embrapa: {e}")
    
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Não foi possível obter dados no site Embrapa.")

    try:
        data = parse_table(resp.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML: {e}")

    # O site traz os números no formato brasileiro, pode converter para int se quiser aqui

    return {
        "ano": ano,
        "dados": data["itens"],
        "total_geral_litros": data["total_geral_litros"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
