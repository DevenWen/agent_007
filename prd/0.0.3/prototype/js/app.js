// App Logic for v0.0.3

// State
let currentView = 'tickets';
let selectedAgent = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    showView('tickets');
});

// View Navigation
function showView(view) {
    currentView = view;
    // Update Nav
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('bg-slate-700', 'text-white'));
    document.getElementById(`nav-${view}`).classList.add('bg-slate-700', 'text-white');

    // Update Title
    const titles = { tickets: 'Tickets', agents: 'Agents', skills: 'Skills' };
    document.getElementById('page-title').textContent = titles[view];

    // Toggle Buttons
    document.getElementById('create-agent-btn').classList.toggle('hidden', view !== 'agents');

    renderContent(view);
}

function renderContent(view) {
    const content = document.getElementById('content');
    content.innerHTML = '';

    if (view === 'tickets') renderTickets(content);
    else if (view === 'agents') renderAgents(content);
    else if (view === 'skills') renderSkills(content);
}

// ==================== Renderers ====================

function renderTickets(container) {
    container.innerHTML = `
        <div class="grid gap-4">
            ${mockData.tickets.map(t => `
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 hover:border-primary/50 cursor-pointer" onclick="showTicketDetail('${t.id}')">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-slate-500 font-mono text-xs">#${t.id.slice(0, 8)}</span>
                                <span class="px-2 py-0.5 rounded text-xs ${t.status === 'running' ? 'bg-blue-900 text-blue-200' : 'bg-green-900 text-green-200'}">${t.status}</span>
                            </div>
                            <h3 class="font-medium">${t.context.goal}</h3>
                            <div class="text-sm text-slate-400 mt-1">🧠 ${t.agentName}</div>
                        </div>
                        <div class="text-right text-xs text-slate-500">
                            Updates: ${t.steps.length}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderAgents(container) {
    container.innerHTML = `
        <div class="grid gap-4 md:grid-cols-2">
            ${mockData.agents.map(a => `
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center">🧠</div>
                            <div>
                                <h3 class="font-semibold">${a.name}</h3>
                                <div class="text-xs text-slate-400">Skill: ${a.skillName}</div>
                            </div>
                        </div>
                    </div>
                    <p class="text-sm text-slate-400 mb-3">${a.description}</p>
                    <div class="flex flex-wrap gap-2 text-xs">
                        ${a.toolNames.map(t => `<span class="px-2 py-1 bg-slate-700 rounded">🔧 ${t}</span>`).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderSkills(container) {
    container.innerHTML = `
        <div class="grid gap-4">
            ${mockData.skills.map(s => `
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                    <div class="flex justify-between">
                        <h3 class="font-bold text-lg text-primary">${s.name}</h3>
                        <span class="text-xs text-slate-500">${s.tools.length} Tools</span>
                    </div>
                    <p class="text-sm text-slate-300 mt-2">${s.description}</p>
                    <div class="mt-4 bg-slate-900 p-3 rounded text-xs font-mono text-slate-400 truncate">
                        ${s.content}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// ==================== Modals & Interactions ====================

function openCreateModal() {
    // Ticket Creation Modal
    const modalHtml = `
        <div class="fixed inset-0 modal-backdrop flex items-center justify-center z-50" id="create-modal">
            <div class="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-lg p-6 shadow-2xl">
                <h2 class="text-lg font-bold mb-4">Create Ticket</h2>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Select Agent</label>
                        <select class="w-full bg-slate-900 border border-slate-600 rounded p-2" onchange="onAgentSelect(this.value)">
                            <option value="">-- Choose --</option>
                            ${mockData.agents.map(a => `<option value="${a.id}">${a.name}</option>`).join('')}
                        </select>
                    </div>
                    
                    <div id="dynamic-form" class="hidden">
                        <div class="border-t border-slate-700 pt-4">
                            <h3 class="text-sm font-semibold mb-2">Parameters</h3>
                            <div id="form-fields" class="space-y-3"></div>
                        </div>
                    </div>

                    <div class="flex justify-end gap-2 mt-6">
                        <button onclick="document.getElementById('create-modal').remove()" class="px-4 py-2 bg-slate-700 rounded">Cancel</button>
                        <button onclick="submitTicket()" class="px-4 py-2 bg-primary rounded">Create</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('modal-container').innerHTML = modalHtml;
}

function onAgentSelect(agentId) {
    const agent = mockData.agents.find(a => a.id === agentId);
    selectedAgent = agent;
    const formContainer = document.getElementById('dynamic-form');
    const fieldsContainer = document.getElementById('form-fields');

    if (!agent) {
        formContainer.classList.add('hidden');
        return;
    }

    formContainer.classList.remove('hidden');
    fieldsContainer.innerHTML = '';

    // Render Schema Fields
    if (agent.paramsSchema && agent.paramsSchema.properties) {
        Object.entries(agent.paramsSchema.properties).forEach(([key, prop]) => {
            const defaultVal = agent.defaultParams?.[key] || '';
            const html = `
                <div>
                    <label class="block text-xs text-slate-400 mb-1">${key}</label>
                    <input type="${prop.type === 'integer' ? 'number' : 'text'}" 
                           class="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm"
                           placeholder="${prop.description || ''}"
                           value="${defaultVal}"
                           id="field-${key}">
                </div>
            `;
            fieldsContainer.innerHTML += html;
        });
    } else {
        fieldsContainer.innerHTML = '<div class="text-sm text-slate-500 italic">No parameters required.</div>';
    }
}

function showTicketDetail(id) {
    const t = mockData.tickets.find(x => x.id === id);
    if (!t) return;

    document.getElementById('detail-title').textContent = `Ticket #${t.id.slice(0, 8)}`;
    document.getElementById('detail-content').innerHTML = `
        <div class="space-y-4">
            <div class="bg-slate-700/50 p-3 rounded-lg">
                <div class="text-xs text-slate-400">Context</div>
                <pre class="text-xs mt-1">${JSON.stringify(t.context, null, 2)}</pre>
            </div>
             <div class="bg-slate-700/50 p-3 rounded-lg">
                <div class="text-xs text-slate-400">Params</div>
                <pre class="text-xs mt-1">${JSON.stringify(t.params, null, 2)}</pre>
            </div>
            <div>
                <h4 class="font-semibold mb-2">Steps</h4>
                <div class="space-y-2">
                    ${t.steps.map(s => `
                        <div class="flex items-center gap-2 text-sm">
                            <span class="w-2 h-2 rounded-full ${s.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'}"></span>
                            <span>${s.title}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    const panel = document.getElementById('detail-panel');
    panel.classList.remove('translate-x-full');
}

function closeDetail() {
    document.getElementById('detail-panel').classList.add('translate-x-full');
}
