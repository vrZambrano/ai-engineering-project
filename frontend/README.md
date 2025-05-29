# Frontend - API Produção Vinhos EMBRAPA

Este é um frontend simples para consumir a API de dados da EMBRAPA sobre produção de vinhos no Rio Grande do Sul.

## 📋 Funcionalidades

O frontend permite consultar os seguintes endpoints da API:

### 🍇 Produção
- **Endpoint**: `/producao`
- **Descrição**: Produção anual de vinhos e derivados no RS
- **Período**: 1970-2023

### 🏪 Comercialização
- **Endpoint**: `/comercializacao`
- **Descrição**: Comercialização anual de vinhos e derivados no RS
- **Período**: 1970-2023

### ⚙️ Processamento
- **Endpoint**: `/processamento/{tipo}`
- **Tipos disponíveis**:
  - `viniferas` - Uvas Viníferas
  - `americanas-hibridas` - Uvas Americanas e Híbridas
  - `uvas-mesa` - Uvas de Mesa
  - `sem-classificacao` - Sem Classificação
- **Período**: 1970-2023

### 📥 Importação
- **Endpoint**: `/importacao/{produto}`
- **Produtos disponíveis**:
  - `vinho-mesa` - Vinho de Mesa
  - `espumante` - Espumante
  - `uvas-frescas` - Uvas Frescas
  - `uvas-passas` - Uvas Passas
  - `suco-uva` - Suco de Uva
- **Período**: 1970-2024

### 📤 Exportação
- **Endpoint**: `/exportacao/{produto}`
- **Produtos disponíveis**:
  - `vinho-mesa` - Vinho de Mesa
  - `espumante` - Espumante
  - `uvas-frescas` - Uvas Frescas
  - `suco-uva` - Suco de Uva
- **Período**: 1970-2024

## 🚀 Como usar

### Pré-requisitos

1. **API Backend rodando**: Certifique-se de que a API FastAPI está rodando em `http://localhost:8888`

   ```bash
   cd ai-engineering-project/src
   python main.py
   ```

### Executando o Frontend

1. **Abrir o arquivo HTML**: Simplesmente abra o arquivo `index.html` em um navegador web moderno

   ```bash
   # No diretório do frontend
   open index.html
   # ou
   firefox index.html
   # ou
   google-chrome index.html
   ```

2. **Usando um servidor local** (recomendado para evitar problemas de CORS):

   ```bash
   # Python 3
   python -m http.server 3000
   
   # Node.js (se tiver o http-server instalado)
   npx http-server -p 3000
   
   # Depois acesse: http://localhost:3000
   ```

## 🎯 Como usar a interface

1. **Selecione uma categoria**: Escolha entre Produção, Comercialização, Processamento, Importação ou Exportação

2. **Selecione uma subcategoria** (se aplicável): Para Processamento, Importação e Exportação, você precisará escolher uma subcategoria específica

3. **Digite o ano**: Insira um ano válido dentro do período permitido para a categoria selecionada

4. **Clique em "Consultar"**: O sistema fará a requisição para a API e exibirá os resultados

## 🛠️ Tecnologias utilizadas

- **HTML5**: Estrutura da página
- **CSS3**: Estilização com gradientes, animações e design responsivo
- **JavaScript (ES6+)**: Lógica da aplicação, requisições à API e manipulação do DOM
- **Fetch API**: Para fazer requisições HTTP à API

## 📱 Design Responsivo

O frontend foi desenvolvido com design responsivo, funcionando bem em:
- 💻 Desktop
- 📱 Tablets
- 📱 Smartphones

## 🎨 Características do Design

- **Interface moderna**: Design limpo com gradientes e efeitos visuais
- **Feedback visual**: Loading spinner durante requisições
- **Tratamento de erros**: Mensagens de erro claras e informativas
- **Formatação de dados**: Dados numéricos formatados para o padrão brasileiro
- **Tabelas responsivas**: Exibição organizada dos dados retornados pela API

## 🔧 Configuração

A configuração da URL da API pode ser alterada no arquivo `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8888';
```

## 📊 Estrutura dos Dados

O frontend está preparado para exibir diferentes tipos de resposta da API:

- **Dados tabulares**: Exibidos em tabelas organizadas
- **Dados simples**: Exibidos em cards informativos
- **Metadados**: Ano, categoria e subcategoria destacados

## 🐛 Solução de Problemas

### API não está respondendo
- Verifique se a API está rodando em `http://localhost:8888`
- Abra o console do navegador (F12) para ver mensagens de erro
- Teste a API diretamente acessando `http://localhost:8888/docs`

### Problemas de CORS
- Use um servidor local para servir os arquivos HTML
- Certifique-se de que a API tem CORS configurado corretamente

### Dados não aparecem
- Verifique se o ano inserido está dentro do período válido
- Confirme se a categoria e subcategoria foram selecionadas corretamente
- Verifique o console do navegador para erros de JavaScript

## 📝 Estrutura de Arquivos

```
frontend/
├── index.html      # Página principal
├── styles.css      # Estilos CSS
├── script.js       # Lógica JavaScript
└── README.md       # Este arquivo
