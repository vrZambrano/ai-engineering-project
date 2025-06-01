// Configuração da API
// Como o frontend agora é servido pelo mesmo servidor, usamos URL relativa
// Atualizado: Cabeçalhos das tabelas de Produção/Comercialização alterados
const API_BASE_URL = '';

// Mapeamento das subcategorias
const subcategorias = {
    processamento: [
        { value: 'viniferas', label: 'Uvas Viníferas' },
        { value: 'americanas-hibridas', label: 'Uvas Americanas e Híbridas' },
        { value: 'uvas-mesa', label: 'Uvas de Mesa' },
        { value: 'sem-classificacao', label: 'Sem Classificação' }
    ],
    importacao: [
        { value: 'vinho-mesa', label: 'Vinho de Mesa' },
        { value: 'espumante', label: 'Espumante' },
        { value: 'uvas-frescas', label: 'Uvas Frescas' },
        { value: 'uvas-passas', label: 'Uvas Passas' },
        { value: 'suco-uva', label: 'Suco de Uva' }
    ],
    exportacao: [
        { value: 'vinho-mesa', label: 'Vinho de Mesa' },
        { value: 'espumante', label: 'Espumante' },
        { value: 'uvas-frescas', label: 'Uvas Frescas' },
        { value: 'suco-uva', label: 'Suco de Uva' }
    ]
};

// Elementos do DOM
const categoriaSelect = document.getElementById('categoria');
const subcategoriaGroup = document.getElementById('subcategoriaGroup');
const subcategoriaSelect = document.getElementById('subcategoria');
const anoInput = document.getElementById('ano');
const consultaForm = document.getElementById('consultaForm');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const resultHeader = document.getElementById('resultHeader');
const resultContent = document.getElementById('resultContent');
const errorMessage = document.getElementById('errorMessage');
const consultarBtn = document.getElementById('consultarBtn');

// Event Listeners
categoriaSelect.addEventListener('change', handleCategoriaChange);
consultaForm.addEventListener('submit', handleFormSubmit);

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Define o ano atual como padrão
    const currentYear = new Date().getFullYear();
    anoInput.value = Math.min(currentYear, 2024);
});

function handleCategoriaChange() {
    const categoria = categoriaSelect.value;
    
    // Limpa resultados anteriores
    hideAllSections();
    
    // Mostra/esconde subcategorias baseado na categoria
    if (categoria && subcategorias[categoria]) {
        subcategoriaGroup.style.display = 'block';
        populateSubcategorias(categoria);
        
        // Ajusta o range do ano baseado na categoria
        if (categoria === 'importacao' || categoria === 'exportacao') {
            anoInput.max = 2024;
        } else {
            anoInput.max = 2023;
        }
    } else {
        subcategoriaGroup.style.display = 'none';
        subcategoriaSelect.innerHTML = '<option value="">Selecione uma subcategoria</option>';
        
        // Para produção e comercialização
        if (categoria === 'producao' || categoria === 'comercializacao') {
            anoInput.max = 2023;
        }
    }
}

function populateSubcategorias(categoria) {
    subcategoriaSelect.innerHTML = '<option value="">Selecione uma subcategoria</option>';
    
    subcategorias[categoria].forEach(sub => {
        const option = document.createElement('option');
        option.value = sub.value;
        option.textContent = sub.label;
        subcategoriaSelect.appendChild(option);
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const categoria = categoriaSelect.value;
    const subcategoria = subcategoriaSelect.value;
    const ano = anoInput.value;
    
    if (!categoria || !ano) {
        showError('Por favor, preencha todos os campos obrigatórios.');
        return;
    }
    
    // Verifica se subcategoria é necessária
    if (subcategorias[categoria] && !subcategoria) {
        showError('Por favor, selecione uma subcategoria.');
        return;
    }
    
    // Constrói a URL do endpoint
    let endpoint = `/${categoria}`;
    if (subcategoria) {
        endpoint += `/${subcategoria}`;
    }
    
    await consultarAPI(endpoint, ano);
}

async function consultarAPI(endpoint, ano) {
    showLoading();
    
    try {
        const url = `${API_BASE_URL}${endpoint}?ano=${ano}`;
        console.log('Fazendo requisição para:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Armazena os dados para download
        currentData = data;
        currentEndpoint = endpoint;
        currentYear = ano;
        
        showResults(data, endpoint, ano);
        
    } catch (error) {
        console.error('Erro na requisição:', error);
        showError(`Erro ao consultar a API: ${error.message}`);
    }
}

function showLoading() {
    hideAllSections();
    loading.style.display = 'block';
    consultarBtn.disabled = true;
}

function hideAllSections() {
    loading.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    if (downloadButtons) {
        downloadButtons.style.display = 'none';
    }
    consultarBtn.disabled = false;
}

function showError(message) {
    hideAllSections();
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
}

function showResults(data, endpoint, ano) {
    hideAllSections();
    
    // Monta o cabeçalho do resultado
    const endpointParts = endpoint.split('/').filter(part => part);
    const categoria = endpointParts[0];
    const subcategoria = endpointParts[1];
    
    let titulo = formatarTitulo(categoria, subcategoria);
    resultHeader.innerHTML = `
        <h3>${titulo} - Ano ${ano}</h3>
        <p>Dados obtidos da EMBRAPA</p>
    `;
    
    // Monta o conteúdo do resultado
    resultContent.innerHTML = formatarDados(data, categoria);
    
    // Mostra os botões de download
    if (downloadButtons) {
        downloadButtons.style.display = 'flex';
    }
    
    resultsSection.style.display = 'block';
}

function formatarTitulo(categoria, subcategoria) {
    const titulos = {
        producao: 'Produção de Vinhos e Derivados',
        comercializacao: 'Comercialização de Vinhos e Derivados',
        processamento: {
            'viniferas': 'Processamento de Uvas Viníferas',
            'americanas-hibridas': 'Processamento de Uvas Americanas e Híbridas',
            'uvas-mesa': 'Processamento de Uvas de Mesa',
            'sem-classificacao': 'Processamento de Uvas sem Classificação'
        },
        importacao: {
            'vinho-mesa': 'Importação de Vinhos de Mesa',
            'espumante': 'Importação de Espumantes',
            'uvas-frescas': 'Importação de Uvas Frescas',
            'uvas-passas': 'Importação de Uvas Passas',
            'suco-uva': 'Importação de Suco de Uva'
        },
        exportacao: {
            'vinho-mesa': 'Exportação de Vinhos de Mesa',
            'espumante': 'Exportação de Espumantes',
            'uvas-frescas': 'Exportação de Uvas Frescas',
            'suco-uva': 'Exportação de Suco de Uva'
        }
    };
    
    if (subcategoria && titulos[categoria][subcategoria]) {
        return titulos[categoria][subcategoria];
    }
    
    return titulos[categoria] || 'Dados EMBRAPA';
}

function formatarDados(data, categoria) {
    if (!data || typeof data !== 'object') {
        return '<p>Nenhum dado encontrado.</p>';
    }
    
    let html = '';
    
    // Informações gerais
    if (data.ano) {
        html += `<div class="data-item"><strong>Ano:</strong> <span class="data-value">${data.ano}</span></div>`;
    }
    
    if (data.categoria) {
        html += `<div class="data-item"><strong>Categoria:</strong> <span class="data-value">${data.categoria}</span></div>`;
    }
    
    if (data.subcategoria) {
        html += `<div class="data-item"><strong>Subcategoria:</strong> <span class="data-value">${data.subcategoria}</span></div>`;
    }
    
    // Dados específicos
    if (data.dados && Array.isArray(data.dados) && data.dados.length > 0) {
        html += '<h4>Dados Detalhados:</h4>';
        
        // Verifica se é Produção, Comercialização ou Processamento (que têm subitens para expandir)
        const isProducaoOuComercializacao = categoria === 'producao' || categoria === 'comercializacao';
        const isProcessamento = categoria === 'processamento';
        
        if (isProducaoOuComercializacao && data.dados.some(item => item.subitems && Array.isArray(item.subitems))) {
            html += formatarTabelaExpandida(data.dados, 'producao');
        } else if (isProcessamento && data.dados.some(item => item.cultivares && Array.isArray(item.cultivares))) {
            html += formatarTabelaExpandida(data.dados, 'processamento');
        } else {
            html += formatarTabelaSimples(data.dados);
        }
    } else {
        // Se não há array de dados, mostra os campos diretamente
        html += '<div class="data-grid">';
        Object.entries(data).forEach(([key, value]) => {
            if (key !== 'ano' && key !== 'categoria' && key !== 'subcategoria') {
                html += `
                    <div class="data-item">
                        <strong>${formatarChave(key)}:</strong>
                        <span class="data-value">${formatarValor(value)}</span>
                    </div>
                `;
            }
        });
        html += '</div>';
    }
    
    return html;
}

// Função para formatar tabela expandida (Produção/Comercialização/Processamento)
function formatarTabelaExpandida(dados, tipo) {
    let html = '<table class="data-table">';
    
    if (tipo === 'processamento') {
        // Cabeçalho para Processamento
        html += '<thead><tr>';
        html += '<th>Produto Principal</th>';
        html += '<th>Quantidade Total (Kg)</th>';
        html += '<th>Cultivar</th>';
        html += '<th>Quantidade Cultivar (Kg)</th>';
        html += '</tr></thead>';
        
        // Dados expandidos para Processamento
        html += '<tbody>';
        dados.forEach(item => {
            if (item.cultivares && Array.isArray(item.cultivares) && item.cultivares.length > 0) {
                // Para cada cultivar, cria uma linha
                item.cultivares.forEach((cultivar, index) => {
                    html += '<tr>';
                    
                    // Produto principal e quantidade total (só na primeira linha do grupo)
                    if (index === 0) {
                        html += `<td rowspan="${item.cultivares.length}">${item.categoria || item.produto || '-'}</td>`;
                        html += `<td rowspan="${item.cultivares.length}">${formatarNumero(item.quantidade_kg)}</td>`;
                    }
                    
                    // Dados do cultivar
                    html += `<td>${cultivar.cultivar || '-'}</td>`;
                    html += `<td>${formatarNumero(cultivar.quantidade_kg)}</td>`;
                    
                    html += '</tr>';
                });
            } else {
                // Se não tem cultivares, mostra só o item principal
                html += '<tr>';
                html += `<td>${item.categoria || item.produto || '-'}</td>`;
                html += `<td>${formatarNumero(item.quantidade_kg)}</td>`;
                html += '<td>-</td>';
                html += '<td>-</td>';
                html += '</tr>';
            }
        });
    } else {
        // Cabeçalho para Produção/Comercialização
        html += '<thead><tr>';
        html += '<th>Tipo Produto</th>';
        html += '<th>Total Quantidade (Litros)</th>';
        html += '<th>Produto</th>';
        html += '<th>Quantidade (Litros)</th>';
        html += '</tr></thead>';
        
        // Dados expandidos para Produção/Comercialização
        html += '<tbody>';
        dados.forEach(item => {
            if (item.subitems && Array.isArray(item.subitems) && item.subitems.length > 0) {
                // Para cada subitem, cria uma linha
                item.subitems.forEach((subitem, index) => {
                    html += '<tr>';
                    
                    // Produto principal e quantidade total (só na primeira linha do grupo)
                    if (index === 0) {
                        html += `<td rowspan="${item.subitems.length}">${item.produto || '-'}</td>`;
                        html += `<td rowspan="${item.subitems.length}">${formatarNumero(item.quantidade_litros)}</td>`;
                    }
                    
                    // Dados do subitem
                    html += `<td>${subitem.produto || subitem.cultivar || subitem.tipo || '-'}</td>`;
                    html += `<td>${formatarNumero(subitem.quantidade_litros || subitem.quantidade)}</td>`;
                    
                    html += '</tr>';
                });
            } else {
                // Se não tem subitems, mostra só o item principal
                html += '<tr>';
                html += `<td>${item.produto || '-'}</td>`;
                html += `<td>${formatarNumero(item.quantidade_litros)}</td>`;
                html += '<td>-</td>';
                html += '<td>-</td>';
                html += '</tr>';
            }
        });
    }
    
    html += '</tbody></table>';
    return html;
}

// Função para formatar tabela simples (outros endpoints)
function formatarTabelaSimples(dados) {
    let html = '<table class="data-table">';
    
    // Cabeçalho da tabela
    const firstItem = dados[0];
    html += '<thead><tr>';
    Object.keys(firstItem).forEach(key => {
        html += `<th>${formatarChave(key)}</th>`;
    });
    html += '</tr></thead>';
    
    // Dados da tabela
    html += '<tbody>';
    dados.forEach(item => {
        html += '<tr>';
        Object.values(item).forEach(value => {
            html += `<td>${formatarValor(value)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    return html;
}

function formatarChave(key) {
    const mapeamento = {
        'produto': 'Produto',
        'quantidade': 'Quantidade',
        'quantidade_litros': 'Quantidade (Litros)',
        'quantidade_kg': 'Quantidade (Kg)',
        'cultivares': 'Cultivares',
        'unidade': 'Unidade',
        'valor': 'Valor',
        'pais': 'País',
        'cultivar': 'Cultivar',
        'valor_usd': 'Valor (US$)',
        'tipo': 'Tipo',
        'ano': 'Ano',
        'categoria': 'Categoria',
        'subcategoria': 'Subcategoria',
        'subitems': 'Subitems'
    };
    
    return mapeamento[key] || key.charAt(0).toUpperCase() + key.slice(1);
}

function formatarValor(value) {
    if (value === null || value === undefined) {
        return '-';
    }
    
    if (typeof value === 'number') {
        return value.toLocaleString('pt-BR');
    }
    
    // Se for um array de objetos (como subitens)
    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '-';
        }
        
        // Se são objetos, cria uma lista formatada
        if (typeof value[0] === 'object') {
            return value.map(item => {
                if (item.cultivar && item.quantidade) {
                    return `${item.cultivar}: ${formatarNumero(item.quantidade)}`;
                } else if (item.tipo && item.quantidade) {
                    return `${item.tipo}: ${formatarNumero(item.quantidade)}`;
                } else if (item.produto && item.quantidade_litros) {
                    return `${item.produto}: ${formatarNumero(item.quantidade_litros)}`;
                } else if (item.cultivar && item.quantidade_kg) {
                    return `${item.cultivar}: ${formatarNumero(item.quantidade_kg)} kg`;
                } else {
                    // Fallback para outros tipos de objeto
                    return Object.entries(item)
                        .map(([k, v]) => `${k}: ${v}`)
                        .join(', ');
                }
            }).join('\n');
        }
        
        // Se são valores simples
        return value.join(', ');
    }
    
    // Se for um objeto simples
    if (typeof value === 'object') {
        return Object.entries(value)
            .map(([k, v]) => `${k}: ${v}`)
            .join(', ');
    }
    
    return value;
}

// Função auxiliar para formatação de números
function formatarNumero(num) {
    if (typeof num === 'number') {
        return num.toLocaleString('pt-BR');
    }
    return num;
}

// Função para testar a conexão com a API
async function testarConexao() {
    try {
        const response = await fetch(`${API_BASE_URL}/docs`);
        if (response.ok) {
            console.log('✅ Conexão com a API estabelecida');
        } else {
            console.warn('⚠️ API respondeu mas com status:', response.status);
        }
    } catch (error) {
        console.error('❌ Erro ao conectar com a API:', error.message);
        console.log('💡 Certifique-se de que a API está rodando em http://localhost:8888');
    }
}

// Testa a conexão quando a página carrega
document.addEventListener('DOMContentLoaded', testarConexao);

// Variáveis globais para download
let currentData = null;
let currentEndpoint = null;
let currentYear = null;

// Elementos de download
const downloadButtons = document.getElementById('downloadButtons');
const downloadJsonBtn = document.getElementById('downloadJson');
const downloadCsvBtn = document.getElementById('downloadCsv');

// Event listeners para download
if (downloadJsonBtn && downloadCsvBtn) {
    downloadJsonBtn.addEventListener('click', downloadJson);
    downloadCsvBtn.addEventListener('click', downloadCsv);
}

// Função para download em JSON
function downloadJson() {
    if (!currentData) {
        alert('Nenhum dado disponível para download.');
        return;
    }
    
    const jsonString = JSON.stringify(currentData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const filename = generateFilename('json');
    downloadFile(url, filename);
}

// Função para download em CSV
function downloadCsv() {
    if (!currentData) {
        alert('Nenhum dado disponível para download.');
        return;
    }
    
    const csvString = convertToCSV(currentData);
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const filename = generateFilename('csv');
    downloadFile(url, filename);
}

// Função para converter dados para CSV
function convertToCSV(data) {
    if (!data.dados || !Array.isArray(data.dados) || data.dados.length === 0) {
        return 'Nenhum dado disponível';
    }

    const processedRows = [];
    const endpointParts = currentEndpoint.split('/').filter(part => part);
    const categoria = endpointParts[0];

    data.dados.forEach(item => {
        if (categoria === 'producao' || categoria === 'comercializacao') {
            // Para produção e comercialização, expandir subitems conforme especificado
            if (item.subitems && Array.isArray(item.subitems) && item.subitems.length > 0) {
                item.subitems.forEach(subitem => {
                    const row = {
                        total_produto: item.produto || '',
                        produto: subitem.produto || '',
                        quantidade_litros: subitem.quantidade_litros || ''
                    };
                    processedRows.push(row);
                });
            } else {
                // Se não tem subitems, criar linha apenas com dados principais
                const row = {
                    total_produto: item.produto || '',
                    produto: '',
                    quantidade_litros: ''
                };
                processedRows.push(row);
            }
        } else if (categoria === 'processamento') {
            // Para processamento, expandir cultivares
            if (item.cultivares && Array.isArray(item.cultivares) && item.cultivares.length > 0) {
                item.cultivares.forEach(cultivar => {
                    const row = {
                        categoria: item.categoria || item.produto || '',
                        cultivar: cultivar.cultivar || '',
                        quantidade_kg: cultivar.quantidade_kg || ''
                    };
                    processedRows.push(row);
                });
            } else {
                // Se não tem cultivares, criar linha apenas com dados principais
                const row = {
                    categoria: item.categoria || item.produto || '',
                    cultivar: '',
                    quantidade_kg: ''
                };
                processedRows.push(row);
            }
        } else {
            // Para outras categorias (importação/exportação), usar estrutura simples
            const row = {};
            Object.keys(item).forEach(key => {
                if (Array.isArray(item[key])) {
                    row[key] = item[key].join('; ');
                } else if (typeof item[key] === 'object' && item[key] !== null) {
                    row[key] = JSON.stringify(item[key]);
                } else {
                    row[key] = item[key] || '';
                }
            });
            processedRows.push(row);
        }
    });

    if (processedRows.length === 0) {
        return 'Nenhum dado para exibir em CSV após processamento.';
    }

    // Definir ordem das colunas baseada na categoria
    let headers = [];
    if (categoria === 'producao' || categoria === 'comercializacao') {
        headers = ['total_produto', 'produto', 'quantidade_litros'];
    } else if (categoria === 'processamento') {
        headers = ['categoria', 'cultivar', 'quantidade_kg'];
    } else {
        // Para outras categorias, usar todas as chaves encontradas
        headers = [...new Set(processedRows.flatMap(Object.keys))];
    }

    // Criar cabeçalho CSV
    const headerRow = headers.map(header => `"${String(header).replace(/"/g, '""')}"`).join(',');
    
    // Criar linhas de dados
    const dataRows = processedRows.map(row => {
        return headers.map(header => {
            const value = row[header] !== undefined && row[header] !== null ? row[header] : '';
            return `"${String(value).replace(/"/g, '""')}"`;
        }).join(',');
    });

    return [headerRow, ...dataRows].join('\n');
}

// Função para gerar nome do arquivo
function generateFilename(extension) {
    const endpointParts = currentEndpoint.split('/').filter(part => part);
    const categoria = endpointParts[0];
    const subcategoria = endpointParts[1];
    
    let filename = `embrapa_${categoria}`;
    if (subcategoria) {
        filename += `_${subcategoria}`;
    }
    filename += `_${currentYear}.${extension}`;
    
    return filename;
}

// Função auxiliar para fazer download do arquivo
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Limpar URL do objeto
    URL.revokeObjectURL(url);
}
