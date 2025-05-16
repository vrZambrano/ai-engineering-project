# API de Produção de Vinhos EMPRAPA

Esta é uma API FastAPI que fornece dados sobre a produção anual de vinhos e derivados no Rio Grande do Sul, obtidos através de web scraping do site da Embrapa Vitibrasil.

## Funcionalidades

- Expõe um endpoint `/producao` que aceita um ano como parâmetro.
- Realiza scraping dos dados de produção do site da Embrapa para o ano especificado.
- Analisa a tabela HTML de dados, lidando com uma estrutura hierárquica de produtos e subprodutos.
- Retorna os dados em formato JSON, incluindo os itens de produção e o total geral em litros.
- Implementa um mecanismo de retentativas com backoff exponencial e jitter para lidar com falhas de rede ou instabilidade do site da Embrapa.
- Registra informações e erros durante o processo.

## Requisitos

- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- BeautifulSoup4

Você pode instalar as dependências com:
```bash
pip install fastapi uvicorn requests beautifulsoup4
```

## Como Executar

1. Certifique-se de que todas as dependências estão instaladas.
2. Execute o servidor Uvicorn a partir do diretório do projeto:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8888 --reload
   ```

   - `main`: refere-se ao arquivo `main.py`.
   - `app`: é a instância FastAPI criada em `main.py`.
   - `--host 0.0.0.0`: torna o servidor acessível na rede local.
   - `--port 8888`: especifica a porta em que o servidor será executado.
   - `--reload`: ativa o recarregamento automático do servidor quando o código é alterado (útil para desenvolvimento).

## Endpoint da API

### `GET /producao`

Recupera os dados de produção de vinhos e derivados para um ano específico.

**Parâmetros da Query:**

- `ano` (obrigatório, inteiro): O ano da produção desejada. Deve estar entre 1970 e 2023 (inclusive).

**Exemplo de Requisição:**

```
GET http://localhost:8888/producao?ano=2022
```

**Exemplo de Resposta Bem-Sucedida (200 OK):**

```json
{
  "ano": 2022,
  "dados": [
    {
      "produto": "VINHO DE MESA",
      "quantidade_litros": "195031611",
      "subitems": [
        {
          "produto": "Tinto",
          "quantidade_litros": "162844214"
        },
        {
          "produto": "Branco",
          "quantidade_litros": "30198430"
        },
        {
          "produto": "Rosado",
          "quantidade_litros": "1988968"
        }
      ]
    },
    {
      "produto": "VINHO FINO DE MESA (VINIFERA)",
      "quantidade_litros": "47511796",
      "subitems": [
        {
          "produto": "Tinto",
          "quantidade_litros": "24417918"
        },
        // ... mais subitens
      ]
    }
    // ... mais itens principais
  ],
  "total_geral_litros": "308352487" // Exemplo, o valor real será o do ano consultado
}
```

**Respostas de Erro:**

- `400 Bad Request`: Se o parâmetro `ano` estiver ausente ou fora do intervalo permitido.
- `422 Unprocessable Entity`: Se o parâmetro `ano` não for um inteiro válido.
- `500 Internal Server Error`: Se ocorrer um erro inesperado durante o processamento ou parsing.
- `502 Bad Gateway`: Se houver um erro genérico ao acessar o site da Embrapa após múltiplas tentativas.
- `503 Service Unavailable`: Se houver um erro de conexão ao acessar o site da Embrapa após múltiplas tentativas.
- `504 Gateway Timeout`: Se ocorrer um timeout ao acessar o site da Embrapa após múltiplas tentativas.
- Outros códigos HTTP (ex: 404, 500) podem ser retornados diretamente do site da Embrapa se a tentativa de scraping falhar com esses códigos.

## Estrutura do Código (`main.py`)

- **`FastAPI app`**: Instância principal da aplicação FastAPI.
- **`BASE_URL`**: URL base do site Vitibrasil da Embrapa.
- **`parse_table(html: str) -> dict`**: Função auxiliar que recebe o conteúdo HTML de uma página e extrai os dados da tabela de produção.
  - Utiliza `BeautifulSoup` para analisar o HTML.
  - Identifica itens principais (`tb_item`) e subitens (`tb_subitem`) para construir uma estrutura de dados aninhada.
  - Retorna um dicionário contendo os cabeçalhos da tabela, os itens de produção e o total geral.
- **`producao(ano: int) -> JSONResponse`**: Função do endpoint assíncrono que lida com as requisições GET para `/producao`.
  - Constrói os parâmetros para a requisição ao site da Embrapa.
  - Implementa um loop de retentativas com backoff exponencial para buscar os dados.
  - Chama `parse_table` para processar o HTML obtido.
  - Retorna os dados formatados como `JSONResponse` ou levanta `HTTPException` em caso de erros.
- **`if __name__ == "__main__":`**: Bloco para executar o servidor Uvicorn diretamente ao rodar o script.

## Observações

- O scraping depende da estrutura HTML do site da Embrapa. Mudanças no site podem quebrar o parser.
- Os valores de quantidade são retornados como strings, pois o site os formata com pontos (ex: "195.031.611"). A conversão para números inteiros pode ser feita pelo cliente da API, se necessário.
