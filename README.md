# API de Dados Vitivinícolas EMBRAPA

Esta é uma API FastAPI completa que fornece acesso aos dados vitivinícolas do Rio Grande do Sul através de web scraping do site da [Embrapa Vitibrasil](http://vitibrasil.cnpuv.embrapa.br/index.php). A API oferece dados sobre produção, comercialização, processamento de uvas e comércio exterior de vinhos e derivados.

O processo para captura dos dados envolve web scrapping do site da Embrapa utilizando parsing com BeautifulSoup. Já a aplicação com o portal foi disponibilizado utilizando o [serviço serverless Render](https://render.com/).

## Links

Site: https://ai-engineering-project.onrender.com/static/index.html

Projeto: https://github.com/vrZambrano/ai-engineering-project

Arquitetura: [ai-engineering-project/docs/deployment_architecture.drawio](https://github.com/vrZambrano/ai-engineering-project/blob/main/docs/arquitetura.drawio)



## 🍇 Funcionalidades

A API oferece **15 endpoints** organizados em **5 categorias principais**:

### **1. Produção de Vinhos**
- **`/producao`** - Dados de produção anual de vinhos e derivados (em litros)

### **2. Comercialização**
- **`/comercializacao`** - Dados de comercialização anual de vinhos e derivados (em litros)

### **3. Processamento de Uvas**
- **`/processamento/viniferas`** - Processamento de uvas viníferas (em kg)
- **`/processamento/americanas-hibridas`** - Processamento de uvas americanas e híbridas (em kg)
- **`/processamento/uvas-mesa`** - Processamento de uvas de mesa (em kg)
- **`/processamento/sem-classificacao`** - Processamento de uvas sem classificação (em kg)

### **4. Importação**
- **`/importacao/vinho-mesa`** - Importação de vinhos de mesa
- **`/importacao/espumante`** - Importação de espumantes
- **`/importacao/uvas-frescas`** - Importação de uvas frescas
- **`/importacao/uvas-passas`** - Importação de uvas passas
- **`/importacao/suco-uva`** - Importação de suco de uva

### **5. Exportação**
- **`/exportacao/vinho-mesa`** - Exportação de vinhos de mesa
- **`/exportacao/espumante`** - Exportação de espumantes
- **`/exportacao/uvas-frescas`** - Exportação de uvas frescas
- **`/exportacao/suco-uva`** - Exportação de suco de uva

## 🏗️ Arquitetura

```
ai-engineering-project/
├── src/
│   ├── main.py                    # API FastAPI com configuração CORS e frontend
│   ├── data/
│   │   └── embrapa_scraper.py     # Módulo de parsing HTML especializado
│   └── api/
│       ├── endpoints.py           # Definição de todos os endpoints
│       └── models.py              # Modelos Pydantic para validação
├── frontend/                      # Interface web para consumir a API
│   ├── index.html                 # Página principal do frontend
│   ├── script.js                  # Lógica JavaScript
│   ├── styles.css                 # Estilos CSS
│   └── README.md                  # Documentação do frontend
├── tests/                         # Testes unitários
├── docs/                          # Documentação adicional
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

### Características Técnicas

- **Arquitetura Modular**: Separação clara entre lógica de API, parsing de dados e frontend
- **Frontend Integrado**: Interface web servida estaticamente pela própria API
- **Retry com Backoff Exponencial**: Mecanismo robusto de tentativas com jitter
- **Logging Estruturado**: Rastreamento completo de operações e erros
- **Tratamento de Erros Específicos**: Códigos HTTP apropriados para diferentes falhas
- **Parsing HTML Especializado**: Funções dedicadas para cada tipo de tabela
- **CORS Configurado**: Permite acesso de qualquer origem
- **Validação com Pydantic**: Modelos de dados tipados e validados

## 📋 Requisitos

- Python 3.9+
- FastAPI
- Uvicorn
- Gunicorn
- Requests
- BeautifulSoup4
- Pydantic

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
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app -b 0.0.0.0:8888 --reload
```

### Produção
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app -b 0.0.0.0:8888
```

### Acessando a Aplicação

Após iniciar o servidor, você pode acessar:

- **Frontend Web**: `http://localhost:8888/` (interface gráfica para usar a API)
- **Swagger UI**: `http://localhost:8888/docs` ou `http://localhost:8888/swagger`
- **ReDoc**: `http://localhost:8888/redoc`

## 🌐 Frontend Web

O projeto inclui um **frontend web completo** que permite consultar todos os endpoints da API através de uma interface gráfica intuitiva.

### Funcionalidades do Frontend:
- **Interface responsiva** com design moderno
- **Seleção dinâmica** de categorias e subcategorias
- **Validação de anos** conforme o período disponível
- **Exibição organizada** dos dados em tabelas e cards
- **Tratamento de erros** com mensagens informativas
- **Integração completa** com todos os 15 endpoints da API

### Como usar o Frontend:
1. Acesse `http://localhost:8888/`
2. Selecione uma categoria (Produção, Comercialização, etc.)
3. Escolha uma subcategoria quando aplicável
4. Digite o ano desejado
5. Clique em "Consultar" para ver os resultados

## 📚 Documentação dos Endpoints

### Períodos de Dados Disponíveis:
- **Produção, Comercialização e Processamento**: 1970-2023
- **Importação e Exportação**: 1970-2024

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
    }
  ],
  "total_geral_litros": "308352487"
}
```

### 2. Comercialização

#### `GET /comercializacao`

Dados de comercialização anual de vinhos e derivados no Rio Grande do Sul.

**Parâmetros:**
- `ano` (obrigatório): Ano da comercialização (1970-2023)

**Estrutura de resposta similar ao endpoint de produção.**

### 3. Processamento de Uvas

#### `GET /processamento/viniferas`

Dados de processamento anual de uvas viníferas por cultivar.

**Parâmetros:**
- `ano` (obrigatório): Ano do processamento (1970-2023)

**Exemplo de Requisição:**
```bash
curl "http://localhost:8888/processamento/viniferas?ano=2020"
```

**Exemplo de Resposta:**
```json
{
  "ano": 2020,
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
    }
  ],
  "total_geral_kg": "68580245"
}
```

#### Outros endpoints de processamento:
- **`GET /processamento/americanas-hibridas`** - Uvas americanas e híbridas
- **`GET /processamento/uvas-mesa`** - Uvas de mesa
- **`GET /processamento/sem-classificacao`** - Uvas sem classificação

### 4. Importação

Todos os endpoints de importação seguem o padrão `GET /importacao/{produto}` com período 1970-2024:

- **`/importacao/vinho-mesa`** - Importação de vinhos de mesa
- **`/importacao/espumante`** - Importação de espumantes
- **`/importacao/uvas-frescas`** - Importação de uvas frescas
- **`/importacao/uvas-passas`** - Importação de uvas passas
- **`/importacao/suco-uva`** - Importação de suco de uva

**Exemplo de Resposta:**
```json
{
  "ano": 2022,
  "tipo": "importação",
  "produto": "vinho-mesa",
  "dados": [
    {
      "pais": "Argentina",
      "quantidade": "1234567",
      "valor_usd": "2345678"
    }
  ],
  "total_quantidade": "5678901",
  "total_valor_usd": "6789012"
}
```

### 5. Exportação

Todos os endpoints de exportação seguem o padrão `GET /exportacao/{produto}` com período 1970-2024:

- **`/exportacao/vinho-mesa`** - Exportação de vinhos de mesa
- **`/exportacao/espumante`** - Exportação de espumantes
- **`/exportacao/uvas-frescas`** - Exportação de uvas frescas
- **`/exportacao/suco-uva`** - Exportação de suco de uva

**Estrutura de resposta similar aos endpoints de importação.**

## ⚠️ Códigos de Erro

Todos os endpoints podem retornar os seguintes códigos de erro:

- **400 Bad Request**: Parâmetro `ano` ausente ou fora do intervalo permitido
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

- `fetch_and_parse_producao()`: Tabelas de produção com estrutura hierárquica
- `fetch_and_parse_comercializacao()`: Tabelas de comercialização
- `fetch_and_parse_processamento()`: Tabelas de processamento por cultivar
- `fetch_and_parse_comex()`: Tabelas de comércio exterior (importação/exportação)

### Logging

O sistema registra:
- Tentativas de acesso ao site da Embrapa
- Sucessos e falhas de requisições
- Erros de parsing e processamento
- Tempos de retry e backoff

### Frontend Integrado

- **Servido estaticamente** pela própria API FastAPI
- **Rota raiz** (`/`) redireciona automaticamente para o frontend
- **CORS configurado** para permitir requisições do frontend
- **Design responsivo** compatível com desktop e mobile

## 🔍 Exemplos de Uso

### Via Frontend Web
```
1. Acesse http://localhost:8888/
2. Use a interface gráfica para consultar qualquer endpoint
3. Acesse http://localhost:8888/docs para utilizar o Swagger
```

### Via API REST

#### Comparar Produção vs Comercialização
```bash
# Produção de vinhos em 2022
curl "http://localhost:8888/producao?ano=2022"

# Comercialização de vinhos em 2022
curl "http://localhost:8888/comercializacao?ano=2022"
```

#### Análise de Comércio Exterior
```bash
# Importação de vinhos de mesa em 2023
curl "http://localhost:8888/importacao/vinho-mesa?ano=2023"

# Exportação de vinhos de mesa em 2023
curl "http://localhost:8888/exportacao/vinho-mesa?ano=2023"
```

#### Análise por Tipo de Uva
```bash
# Diferentes tipos de processamento em 2022
curl "http://localhost:8888/processamento/viniferas?ano=2022"
curl "http://localhost:8888/processamento/americanas-hibridas?ano=2022"
curl "http://localhost:8888/processamento/uvas-mesa?ano=2022"
```

#### Análise Temporal
```bash
# Evolução da produção ao longo dos anos
curl "http://localhost:8888/producao?ano=2020"
curl "http://localhost:8888/producao?ano=2021"
curl "http://localhost:8888/producao?ano=2022"
```

## 📝 Observações Importantes

1. **Dependência Externa**: O scraping depende da estrutura HTML do site da Embrapa. Mudanças no site podem afetar o funcionamento.

2. **Formato de Números**: Os valores são retornados como strings no formato brasileiro (ex: "195.031.611"). A conversão para números pode ser feita pelo cliente.

3. **Diferença de Unidades**: 
   - **Produção e Comercialização**: medidas em **litros**
   - **Processamento**: medido em **quilogramas**
   - **Importação e Exportação**: quantidade em **kg** e valor em **USD**

4. **Períodos de Dados**: 
   - **Produção, Comercialização e Processamento**: 1970-2023
   - **Importação e Exportação**: 1970-2024

5. **Rate Limiting**: O sistema implementa delays automáticos para não sobrecarregar o servidor da Embrapa.

6. **Frontend Integrado**: A aplicação serve tanto a API quanto uma interface web completa no mesmo servidor.

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados e serialização
- **Uvicorn/Gunicorn**: Servidor ASGI para produção
- **Requests**: Cliente HTTP para web scraping
- **BeautifulSoup4**: Parser HTML para extração de dados

### Frontend
- **HTML5**: Estrutura da interface
- **CSS3**: Estilização responsiva com gradientes e animações
- **JavaScript ES6+**: Lógica da aplicação e requisições à API
- **Fetch API**: Comunicação com a API REST

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
