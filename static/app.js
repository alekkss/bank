// app.js - Логика frontend приложения

// ============ КОНФИГУРАЦИЯ ============
const API_URL = '/api';

// ============ ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ============
let selectedClientId = null;
let currentFilter = 'all';

// ============ MARKDOWN PARSER ============
function parseMarkdown(text) {
    // Экранируем HTML теги для безопасности
    text = text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');
    
    // Заголовки
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Горизонтальная линия
    text = text.replace(/^---$/gim, '<hr>');
    
    // Списки ПЕРЕД обработкой курсива и жирного текста
    let lines = text.split('\n');
    let inList = false;
    let result = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        
        // Проверяем маркированный список
        if (line.match(/^\s*[\*\-]\s+(.+)$/)) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            result.push('<li>' + line.replace(/^\s*[\*\-]\s+/, '') + '</li>');
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
    }
    
    if (inList) {
        result.push('</ul>');
    }
    
    text = result.join('\n');
    
    // Жирный текст (ПОСЛЕ обработки списков)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Курсив (ПОСЛЕ обработки списков)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Параграфы
    text = text.replace(/\n\n+/g, '</p><p>');
    
    // Обрабатываем переносы строк
    text = text.replace(/\n/g, '<br>');
    
    // Оборачиваем в параграф если не начинается с тега
    if (!text.match(/^<[h|u|o]/)) {
        text = '<p>' + text + '</p>';
    }
    
    return text;
}

// ============ ИНИЦИАЛИЗАЦИЯ ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AI CRM System загружена');
    
    // Загружаем данные
    loadStats();
    loadClients();
    
    // Настраиваем обработчики событий
    setupEventListeners();
    
    // Устанавливаем текущую дату в форме транзакции
    document.getElementById('transactionDate').valueAsDate = new Date();
});

// ============ ОБРАБОТЧИКИ СОБЫТИЙ ============
function setupEventListeners() {
    // Отправка вопроса по Ctrl+Enter
    document.getElementById('aiQuestion').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            askAI();
        }
    });
    
    // Закрытие модальных окон по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

// ============ ЗАГРУЗКА СТАТИСТИКИ ============
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        
        // Обновляем счетчики
        document.getElementById('totalClients').textContent = data.clients.total;
        document.getElementById('activeClients').textContent = data.clients.active;
        document.getElementById('totalIncome').textContent = 
            formatMoney(data.transactions.income);
        document.getElementById('totalExpense').textContent = 
            formatMoney(data.transactions.expense);
            
    } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
        showNotification('Ошибка загрузки статистики', 'error');
    }
}

// ============ РАБОТА С КЛИЕНТАМИ ============
async function loadClients(status = null) {
    try {
        const url = status ? `${API_URL}/clients?status=${status}` : `${API_URL}/clients`;
        const response = await fetch(url);
        const data = await response.json();
        
        const clientsList = document.getElementById('clientsList');
        
        if (data.clients.length === 0) {
            clientsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">👥</div>
                    <p>Нет клиентов${status ? ` со статусом "${status}"` : ''}</p>
                    <button class="btn btn-secondary" onclick="showAddClientModal()">
                        Добавить клиента
                    </button>
                </div>
            `;
            return;
        }
        
        clientsList.innerHTML = data.clients.map(client => {
            // Преобразуем ID в строку для безопасности
            const clientIdStr = String(client.id);
            const isSelected = selectedClientId === clientIdStr;
            
            return `
                <div class="client-card ${isSelected ? 'selected' : ''}" 
                     onclick="selectClient('${escapeHtml(clientIdStr)}')">
                    <div class="client-name">${escapeHtml(client.name)}</div>
                    <div class="client-info">📧 ${escapeHtml(client.email || 'Не указан')}</div>
                    <div class="client-info">📱 ${escapeHtml(client.phone || 'Не указан')}</div>
                    <span class="client-status ${client.status}">
                        ${getStatusLabel(client.status)}
                    </span>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('❌ Ошибка загрузки клиентов:', error);
        showNotification('Ошибка загрузки клиентов', 'error');
    }
}

function filterClients(status) {
    currentFilter = status;
    
    // Обновляем активную кнопку фильтра
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-status="${status}"]`).classList.add('active');
    
    // Загружаем клиентов с фильтром
    loadClients(status === 'all' ? null : status);
}

async function selectClient(clientId) {
    // Сохраняем ID как строку
    selectedClientId = String(clientId);
    
    console.log('Выбран клиент:', selectedClientId);
    
    // Обновляем визуальное выделение
    await loadClients(currentFilter === 'all' ? null : currentFilter);
    
    // Загружаем детали клиента
    await loadClientDetails(selectedClientId);
    
    // Очищаем чат и загружаем предложенные вопросы
    clearChat();
    loadSuggestedQuestions(selectedClientId);
}

async function loadClientDetails(clientId) {
    try {
        console.log('Загрузка деталей клиента:', clientId);
        
        const response = await fetch(`${API_URL}/clients/${encodeURIComponent(clientId)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log('Получены данные клиента:', data);
        
        const detailsHtml = `
            <h3 style="margin-bottom: 16px; color: var(--text-primary);">
                💼 ${escapeHtml(data.client.name)}
            </h3>
            
            <div class="financial-summary">
                <div class="summary-item">
                    <div class="summary-label">Доходы</div>
                    <div class="summary-value income">
                        ${formatMoney(data.summary.total_income)}
                    </div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Расходы</div>
                    <div class="summary-value expense">
                        ${formatMoney(data.summary.total_expense)}
                    </div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Баланс</div>
                    <div class="summary-value balance">
                        ${formatMoney(data.summary.balance)}
                    </div>
                </div>
            </div>
            
            <h4 style="margin: 20px 0 12px; color: var(--text-primary);">
                📝 Последние транзакции
            </h4>
            
            <div class="transactions-list">
                ${data.transactions.length > 0 ? 
                    data.transactions.slice(0, 10).map(tx => {
                        // Определяем направление транзакции
                        const isIncome = tx.direction === 'income' || tx.direction === 'Credit';
                        const directionClass = isIncome ? 'income' : 'expense';
                        const sign = isIncome ? '+' : '-';
                        
                        return `
                            <div class="transaction-item">
                                <div class="transaction-info">
                                    <div class="transaction-category">
                                        ${escapeHtml(tx.category || 'Без категории')}
                                    </div>
                                    ${tx.description ? `
                                        <div class="transaction-description">
                                            ${escapeHtml(tx.description)}
                                        </div>
                                    ` : ''}
                                    <div class="transaction-date">
                                        ${formatDate(tx.transaction_date)}
                                    </div>
                                </div>
                                <div class="transaction-amount ${directionClass}">
                                    ${sign}${formatMoney(Math.abs(tx.amount))}
                                </div>
                            </div>
                        `;
                    }).join('') 
                    : '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">Нет транзакций</p>'
                }
            </div>
            
            <button class="btn btn-primary" 
                    style="width: 100%; margin-top: 16px;" 
                    onclick="showAddTransactionModal('${escapeHtml(String(clientId))}')">
                <span>+</span> Добавить транзакцию
            </button>
        `;
        
        const detailsContainer = document.getElementById('clientDetails');
        detailsContainer.innerHTML = detailsHtml;
        detailsContainer.style.display = 'block';
        
    } catch (error) {
        console.error('❌ Ошибка загрузки деталей клиента:', error);
        showNotification('Ошибка загрузки данных клиента: ' + error.message, 'error');
        
        // Показываем сообщение об ошибке в интерфейсе
        const detailsContainer = document.getElementById('clientDetails');
        detailsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--danger-color);">
                <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
                <p>Ошибка загрузки данных клиента</p>
                <p style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">
                    ${error.message}
                </p>
            </div>
        `;
        detailsContainer.style.display = 'block';
    }
}

async function addClient(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('clientName').value,
        email: document.getElementById('clientEmail').value || null,
        phone: document.getElementById('clientPhone').value || null,
        status: document.getElementById('clientStatus').value
    };
    
    try {
        const response = await fetch(`${API_URL}/clients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            closeModal('addClientModal');
            document.getElementById('addClientForm').reset();
            await loadClients(currentFilter === 'all' ? null : currentFilter);
            await loadStats();
            showNotification('✅ Клиент успешно добавлен', 'success');
            
            // Автоматически выбираем нового клиента
            selectClient(result.id);
        } else {
            const error = await response.json();
            showNotification(`Ошибка: ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Ошибка добавления клиента:', error);
        showNotification('Ошибка при добавлении клиента', 'error');
    }
}

// ============ РАБОТА С ТРАНЗАКЦИЯМИ ============
function showAddTransactionModal(clientId) {
    document.getElementById('transactionClientId').value = clientId;
    openModal('addTransactionModal');
}

async function addTransaction(event) {
    event.preventDefault();
    
    const direction = document.querySelector('input[name="direction"]:checked').value;
    
    const data = {
        client_id: parseInt(document.getElementById('transactionClientId').value),
        amount: parseFloat(document.getElementById('transactionAmount').value),
        category: document.getElementById('transactionCategory').value,
        direction: direction,
        description: document.getElementById('transactionDescription').value || null,
        transaction_date: document.getElementById('transactionDate').value || null
    };
    
    try {
        const response = await fetch(`${API_URL}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeModal('addTransactionModal');
            document.getElementById('addTransactionForm').reset();
            
            // Обновляем данные
            await loadClientDetails(data.client_id);
            await loadStats();
            showNotification('✅ Транзакция добавлена', 'success');
        } else {
            const error = await response.json();
            showNotification(`Ошибка: ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Ошибка добавления транзакции:', error);
        showNotification('Ошибка при добавлении транзакции', 'error');
    }
}

// ============ РАБОТА С AI ============
async function askAI() {
    const questionInput = document.getElementById('aiQuestion');
    const question = questionInput.value.trim();
    
    if (!question) {
        showNotification('Введите вопрос', 'warning');
        return;
    }
    
    const askBtn = document.getElementById('askBtn');
    const originalHtml = askBtn.innerHTML;
    askBtn.innerHTML = '<span class="loading"></span> Думаю...';
    askBtn.disabled = true;
    
    const chatContainer = document.getElementById('aiChat');
    
    // Добавляем вопрос пользователя
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = question;
    chatContainer.appendChild(userMessage);
    
    // Скрываем предложенные вопросы
    document.getElementById('suggestedQuestions').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/ai/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                client_id: selectedClientId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Добавляем ответ AI с поддержкой Markdown
            const aiMessage = document.createElement('div');
            aiMessage.className = 'message assistant';
            aiMessage.innerHTML = parseMarkdown(data.answer);  // Парсим Markdown
            chatContainer.appendChild(aiMessage);
        } else {
            // Показываем ошибку
            const errorMessage = document.createElement('div');
            errorMessage.className = 'message assistant';
            errorMessage.textContent = `❌ Ошибка: ${data.error}`;
            chatContainer.appendChild(errorMessage);
            showNotification('Ошибка AI', 'error');
        }
        
        // Прокручиваем вниз
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Очищаем поле ввода
        questionInput.value = '';
        
    } catch (error) {
        console.error('❌ Ошибка AI:', error);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message assistant';
        errorMessage.textContent = '❌ Ошибка подключения к AI сервису';
        chatContainer.appendChild(errorMessage);
        showNotification('Ошибка подключения', 'error');
    } finally {
        askBtn.innerHTML = originalHtml;
        askBtn.disabled = false;
    }
}

async function loadSuggestedQuestions(clientId) {
    try {
        const url = clientId 
            ? `${API_URL}/ai/suggestions?client_id=${clientId}` 
            : `${API_URL}/ai/suggestions`;
            
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.suggestions && data.suggestions.length > 0) {
            const suggestionsContainer = document.getElementById('suggestedQuestions');
            const suggestionsList = document.getElementById('suggestionsList');
            
            suggestionsList.innerHTML = data.suggestions.map(suggestion => `
                <button class="suggestion-btn" onclick="useSuggestion('${escapeHtml(suggestion).replace(/'/g, "\\'")}')">
                    ${escapeHtml(suggestion)}
                </button>
            `).join('');
            
            suggestionsContainer.style.display = 'block';
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки предложений:', error);
    }
}

function useSuggestion(suggestion) {
    document.getElementById('aiQuestion').value = suggestion;
    document.getElementById('aiQuestion').focus();
}

function clearChat() {
    const chatContainer = document.getElementById('aiChat');
    chatContainer.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">🤖</div>
            <p>${selectedClientId ? 'Задайте вопрос об этом клиенте' : 'Выберите клиента и задайте вопрос'}</p>
            <p class="empty-hint">или задайте общий вопрос о системе</p>
        </div>
    `;
}

// ============ МОДАЛЬНЫЕ ОКНА ============
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

function showAddClientModal() {
    openModal('addClientModal');
}

// ============ УТИЛИТЫ ============
function formatMoney(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(date);
}

function getStatusLabel(status) {
    const labels = {
        'active': 'Активен',
        'inactive': 'Неактивен',
        'vip': 'VIP',
        'blocked': 'Заблокирован'
    };
    return labels[status] || status;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

function showNotification(message, type = 'info') {
    // Простая реализация уведомлений через console
    // Можно заменить на toast-библиотеку
    const emoji = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    console.log(`${emoji[type]} ${message}`);
    
    // Для production можно добавить toast-уведомления
    // Например, используя библиотеку Toastify или создать кастомные
}

// ============ ЭКСПОРТ ДЛЯ ГЛОБАЛЬНОГО ИСПОЛЬЗОВАНИЯ ============
window.loadStats = loadStats;
window.loadClients = loadClients;
window.filterClients = filterClients;
window.selectClient = selectClient;
window.addClient = addClient;
window.showAddClientModal = showAddClientModal;
window.showAddTransactionModal = showAddTransactionModal;
window.addTransaction = addTransaction;
window.askAI = askAI;
window.useSuggestion = useSuggestion;
window.clearChat = clearChat;
window.openModal = openModal;
window.closeModal = closeModal;
