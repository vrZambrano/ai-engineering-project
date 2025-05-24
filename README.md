# API de Dados Vitivinícolas EMBRAPA

Esta é uma API FastAPI completa que fornece acesso aos dados vitivinícolas do Rio Grande do Sul através de web scraping do site da Embrapa Vitibrasil. A API oferece dados sobre produção de vinhos e processamento de diferentes tipos de uvas.

## 🍇 Funcionalidades

A API oferece 5 endpoints principais organizados em duas categorias:

### **Produção de Vinhos**
- **`/producao`** - Dados de produção anual de vinhos e derivados (em litros)

### **Processamento de Uvas**
- **`/processamento/viniferas`** - Processamento de uvas viníferas (em kg)
- **`/processamento/americanas_hibridas`** - Processamento de uvas americanas e híbridas (em kg)
- **`/processamento/uvas_mesa`** - Processamento de uvas de mesa (em kg)
- **`/processamento/sem_classificacao`** - Processamento de uvas sem classificação (em kg)

## 🏗️ Arquitetura

```
ai-engineering-project/
├── src/
│   ├── main.py                    # API FastAPI com todos os endpoints
│   ├── data/
│   │   └── embrapa_scraper.py     # Módulo de parsing HTML especializado
│   └── api/                       # Estrutura para expansões futuras
├── tests/                         # Testes unitários
├── docs/                          # Documentação adicional
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

### Características Técnicas

- **Arquitetura Modular**: Separação clara entre lógica de API e parsing de dados
- **Retry com Backoff Exponencial**: Mecanismo robusto de tentativas com jitter
- **Logging Estruturado**: Rastreamento completo de operações e erros
- **Tratamento de Erros Específicos**: Códigos HTTP apropriados para diferentes falhas
- **Parsing HTML Especializado**: Funções dedicadas para cada tipo de tabela

## 📋 Requisitos

- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- BeautifulSoup4

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd ai-engineering-project

# Instale as dependências
pip install -r requirements.txt
```

## 🚀 Como Executar

### Desenvolvimento
```bash
# A partir do diretório raiz do projeto
uvicorn src.main:app --host 0.0.0.0 --port 8888 --reload
```

### Produção
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8888
```

### Execução Direta
```bash
# Execute o arquivo main.py diretamente
cd src
python main.py
```

A API estará disponível em: `http://localhost:8888`

## 📚 Documentação dos Endpoints

### 1. Produção de Vinhos

#### `GET /producao`

Recupera dados de produção anual de vinhos e derivados no Rio Grande do Sul.

**Parâmetros:**
- `ano` (obrigatório): Ano da produção (1970-2023)

**Exemplo de Requisição:**
```bash
curl "http://localhost:8888/producao?ano=2022"
```

**Exemplo de Resposta:**
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
        {
          "produto": "Branco",
          "quantidade_litros": "23093878"
        }
      ]
    }
  ],
  "total_geral_litros": "308352487"
}
```

### 2. Processamento de Uvas Viníferas

#### `GET /processamento/viniferas`

Dados de processamento anual de uvas viníferas por cultivar.

**Parâmetros:**
- `ano` (obrigatório): Ano do processamento (1970-2023)

**Exemplo de Requisição:**
```bash
curl "http://localhost:8888/processamento/viniferas?ano=2022"
```

**Exemplo de Resposta:**
```json
{
  "ano": 2022,
  "dados": [
    {
      "categoria": "TINTAS",
      "quantidade_kg": "45123456",
      "cultivares": [
        {
          "cultivar": "Cabernet Sauvignon",
          "quantidade_kg": "12345678"
        },
        {
          "cultivar": "Merlot",
          "quantidade_kg": "9876543"
        }
      ]
    },
    {
      "categoria": "BRANCAS E ROSADAS",
      "quantidade_kg": "23456789",
      "cultivares": [
        {
          "cultivar": "Chardonnay",
          "quantidade_kg": "8765432"
        }
      ]
    }
  ],
  "total_geral_kg": "68580245"
}
```

### 3. Processamento de Uvas Americanas e Híbridas

#### `GET /processamento/americanas_hibridas`

Dados de processamento anual de uvas americanas e híbridas.

**Parâmetros:**
- `ano` (obrigatório): Ano do processamento (1970-2023)

**Estrutura de resposta similar ao endpoint de viníferas, mas com cultivares americanas e híbridas.**

### 4. Processamento de Uvas de Mesa

#### `GET /processamento/uvas_mesa`

Dados de processamento anual de uvas de mesa por cultivar.

**Parâmetros:**
- `ano` (obrigatório): Ano do processamento (1970-2023)

**Estrutura de resposta similar, organizada por categorias de uvas de mesa.**

### 5. Processamento de Uvas Sem Classificação

#### `GET /processamento/sem_classificacao`

Dados de processamento anual de uvas sem classificação específica.

**Parâmetros:**
- `ano` (obrigatório): Ano do processamento (1970-2023)

**Exemplo de Resposta:**
```json
{
  "ano": 2022,
  "dados": [
    {
      "item": "SEM CLASSIFICAÇÃO",
      "quantidade_kg": "1234567"
    }
  ],
  "total_geral_kg": "1234567"
}
```

## ⚠️ Códigos de Erro

Todos os endpoints podem retornar os seguintes códigos de erro:

- **400 Bad Request**: Parâmetro `ano` ausente ou fora do intervalo (1970-2023)
- **422 Unprocessable Entity**: Parâmetro `ano` não é um inteiro válido
- **500 Internal Server Error**: Erro no processamento ou parsing dos dados
- **502 Bad Gateway**: Erro genérico ao acessar o site da Embrapa
- **503 Service Unavailable**: Erro de conexão com o site da Embrapa
- **504 Gateway Timeout**: Timeout ao acessar o site da Embrapa

## 🔧 Detalhes Técnicos

### Mecanismo de Retry

- **Máximo de tentativas**: 5
- **Backoff exponencial**: Delay inicial de 5s, máximo de 60s
- **Jitter**: Variação aleatória de 1-3s para evitar thundering herd
- **Timeouts**: Conexão 10s, leitura 30s

### Parsing de Dados

O módulo `embrapa_scraper.py` contém funções especializadas para cada tipo de tabela:

- `parse_table_producao()`: Tabelas de produção com estrutura hierárquica
- `parse_table_processamento_viniferas()`: Tabelas de processamento por cultivar
- `parse_table_processamento_americanas_hibridas()`: Uvas americanas e híbridas
- `parse_table_processamento_uvas_mesa()`: Uvas de mesa
- `parse_table_processamento_sem_classificacao()`: Dados sem classificação

### Logging

O sistema registra:
- Tentativas de acesso ao site da Embrapa
- Sucessos e falhas de requisições
- Erros de parsing e processamento
- Tempos de retry e backoff

## 📊 Documentação Interativa

Após iniciar a API, acesse:

- **Swagger UI**: `http://localhost:8888/docs`
- **ReDoc**: `http://localhost:8888/redoc`

## 🔍 Exemplos de Uso

### Comparar Produção vs Processamento
```bash
# Produção de vinhos em 2022 (litros)
curl "http://localhost:8888/producao?ano=2022"

# Processamento de uvas viníferas em 2022 (kg)
curl "http://localhost:8888/processamento/viniferas?ano=2022"
```

### Análise Temporal
```bash
# Dados de diferentes anos
curl "http://localhost:8888/producao?ano=2020"
curl "http://localhost:8888/producao?ano=2021"
curl "http://localhost:8888/producao?ano=2022"
```

### Análise por Tipo de Uva
```bash
# Diferentes tipos de processamento
curl "http://localhost:8888/processamento/viniferas?ano=2022"
curl "http://localhost:8888/processamento/americanas_hibridas?ano=2022"
curl "http://localhost:8888/processamento/uvas_mesa?ano=2022"
```

## 📝 Observações Importantes

1. **Dependência Externa**: O scraping depende da estrutura HTML do site da Embrapa. Mudanças no site podem afetar o funcionamento.

2. **Formato de Números**: Os valores são retornados como strings no formato brasileiro (ex: "195.031.611"). A conversão para números pode ser feita pelo cliente.

3. **Diferença de Unidades**: 
   - Produção: medida em **litros**
   - Processamento: medido em **quilogramas**

4. **Período de Dados**: Disponível para anos entre 1970 e 2023 (conforme disponibilidade no site da Embrapa).

5. **Rate Limiting**: O sistema implementa delays automáticos para não sobrecarregar o servidor da Embrapa.

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
