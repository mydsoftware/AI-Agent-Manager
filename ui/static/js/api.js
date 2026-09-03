/**
 * کلاینت API برای AI Agent Manager
 * این ماژول ارتباط بین UI و API مرکزی را برقرار می‌کند
 */

const API = {
    baseUrl: '',
    get apiKey() { return localStorage.getItem('ai_agent_api_key') || ''; },
    set apiKey(value) { localStorage.setItem('ai_agent_api_key', value); },

    async call(endpoint, method = 'GET', data = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.apiKey) headers['X-API-Key'] = this.apiKey;
        const options = { method, headers };
        if (data && method !== 'GET') options.body = JSON.stringify(data);
        const response = await fetch(`/api/proxy${endpoint}`, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `خطای HTTP ${response.status}`);
        }
        return response.json();
    },

    async health() { return this.call('/health'); },
    async execute(request, agent = 'developer') { return this.call('/execute', 'POST', { request, agent }); },
    async audit(url, mode = 'pre_contract') {
        return this.call('/execute/website-audit', 'POST', {
            request_id: `exec-${Date.now()}`, url, mode, language: 'fa'
        });
    },
    async route(request) { return this.call('/route', 'POST', { request }); },
    async createProject(project) { return this.call('/project/create', 'POST', project); },
    async getProject(projectId) { return this.call(`/project/${encodeURIComponent(projectId)}`); },
    async runProject(projectId, request = '', agent = 'developer') {
        return this.call(`/project/${encodeURIComponent(projectId)}/run`, 'POST', { request, agent });
    },
    async updateProjectStatus(projectId, status) {
        return this.call(`/project/${encodeURIComponent(projectId)}/status`, 'POST', { status });
    },
    async startSession(sessionId, request) { return this.call('/session/start', 'POST', { session_id: sessionId, request }); },
    async answerSession(sessionId, answer) { return this.call('/session/answer', 'POST', { session_id: sessionId, answer }); },
    async getExecution(executionId) { return this.call(`/executions/${encodeURIComponent(executionId)}`); },
};

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => showNotification('متن کپی شد', 'success'));
}
