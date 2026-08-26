/**
 * کلاینت API برای AI Agent Manager
 * این ماژول ارتباط بین UI و API مرکزی را برقرار می‌کند
 */

const API = {
    // آدرس پایه API (از طریق پروکسی Flask)
    baseUrl: '',
    
    // کلید API (از localStorage خوانده می‌شود)
    get apiKey() {
        return localStorage.getItem('ai_agent_api_key') || '';
    },
    
    set apiKey(value) {
        localStorage.setItem('ai_agent_api_key', value);
    },

    /**
     * فراخوانی API
     * @param {string} endpoint - مسیر API
     * @param {string} method - متد HTTP
     * @param {object} data - داده‌های ارسالی
     * @returns {Promise<object>} - پاسخ API
     */
    async call(endpoint, method = 'GET', data = null) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        const options = {
            method,
            headers,
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        // استفاده از پروکسی Flask برای جلوگیری از مشکل CORS
        const proxyUrl = `/api/proxy${endpoint}`;
        const response = await fetch(proxyUrl, options);
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `خطای HTTP ${response.status}`);
        }

        return response.json();
    },

    /**
     * بررسی سلامت API
     * @returns {Promise<object>}
     */
    async health() {
        return this.call('/health');
    },

    /**
     * اجرای ایجنت
     * @param {string} request - درخواست کاربر
     * @param {string} agent - نام ایجنت
     * @returns {Promise<object>}
     */
    async execute(request, agent = 'developer') {
        return this.call('/execute', 'POST', { request, agent });
    },

    /**
     * ممیزی سایت
     * @param {string} url - آدرس سایت
     * @param {string} mode - حالت ممیزی (pre_contract/post_contract)
     * @returns {Promise<object>}
     */
    async audit(url, mode = 'pre_contract') {
        const executionId = `exec-${Date.now()}`;
        return this.call('/execute/website-audit', 'POST', {
            request_id: executionId,
            url,
            mode,
            language: 'fa',
        });
    },

    /**
     * مسیریابی درخواست
     * @param {string} request - درخواست کاربر
     * @returns {Promise<object>}
     */
    async route(request) {
        return this.call('/route', 'POST', { request });
    },

    /**
     * ایجاد پروژه جدید
     * @param {object} project - اطلاعات پروژه
     * @returns {Promise<object>}
     */
    async createProject(project) {
        return this.call('/project/create', 'POST', project);
    },

    /**
     * شروع نشست
     * @param {string} sessionId - شناسه نشست
     * @param {string} request - درخواست اولیه
     * @returns {Promise<object>}
     */
    async startSession(sessionId, request) {
        return this.call('/session/start', 'POST', { session_id: sessionId, request });
    },

    /**
     * پاسخ به نشست
     * @param {string} sessionId - شناسه نشست
     * @param {string} answer - پاسخ کاربر
     * @returns {Promise<object>}
     */
    async answerSession(sessionId, answer) {
        return this.call('/session/answer', 'POST', { session_id: sessionId, answer });
    },

    /**
     * دریافت وضعیت اجرا
     * @param {string} executionId - شناسه اجرا
     * @returns {Promise<object>}
     */
    async getExecution(executionId) {
        return this.call(`/executions/${executionId}`);
    },
};

// توابع کمکی برای نمایش پیام
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// تابع کپی متن
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('متن کپی شد', 'success');
    });
}
