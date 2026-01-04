const API_BASE = '/api'

async function request(path, options = {}) {
    const url = `${API_BASE}${path}`
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }))
        throw new Error(error.message || `HTTP ${response.status}`)
    }

    if (response.status === 204) {
        return null
    }

    return response.json()
}

export const api = {
    // Tickets
    listTickets: (params = {}) => {
        const query = new URLSearchParams(params).toString()
        return request(`/tickets${query ? `?${query}` : ''}`)
    },
    getTicket: (id) => request(`/tickets/${id}`),
    createTicket: (data) => request('/tickets', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    resumeTicket: (id) => request(`/tickets/${id}/resume`, { method: 'PATCH' }),
    resetTicket: (id) => request(`/tickets/${id}/reset`, { method: 'PATCH' }),
    deleteTicket: (id) => request(`/tickets/${id}`, { method: 'DELETE' }),

    // Agents
    listAgents: () => request('/agents'),
    getAgent: (id) => request(`/agents/${id}`),
    createAgent: (data) => request('/agents', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    updateAgent: (id, data) => request(`/agents/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    deleteAgent: (id) => request(`/agents/${id}`, { method: 'DELETE' }),

    // Sessions
    listSessions: (params = {}) => {
        const query = new URLSearchParams(params).toString()
        return request(`/sessions${query ? `?${query}` : ''}`)
    },
    getSession: (id) => request(`/sessions/${id}`),
    addMessage: (sessionId, content) => request(`/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
    }),

    // Tools
    listTools: () => request('/tools'),
    getTool: (id) => request(`/tools/${id}`),
}
