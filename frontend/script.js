// Configuração da API
// Como o frontend agora é servido pelo mesmo servidor, usamos URL relativa
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
    resultContent.innerHTML = formatarDados(data);
    
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

function formatarDados(data) {
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
        html += '<table class="data-table">';
        
        // Cabeçalho da tabela
        const firstItem = data.dados[0];
        html += '<thead><tr>';
        Object.keys(firstItem).forEach(key => {
            html += `<th>${formatarChave(key)}</th>`;
        });
        html += '</tr></thead>';
        
        // Dados da tabela
        html += '<tbody>';
        data.dados.forEach(item => {
            html += '<tr>';
            Object.values(item).forEach(value => {
                html += `<td>${formatarValor(value)}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
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

function formatarChave(key) {
    const mapeamento = {
        'produto': 'Produto',
        'quantidade': 'Quantidade',
        'unidade': 'Unidade',
        'valor': 'Valor',
        'pais': 'País',
        'cultivar': 'Cultivar',
        'tipo': 'Tipo',
        'ano': 'Ano',
        'categoria': 'Categoria',
        'subcategoria': 'Subcategoria'
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
