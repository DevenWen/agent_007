import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function AgentsPage() {
    const [agents, setAgents] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedAgent, setSelectedAgent] = useState(null)
    const [isCreating, setIsCreating] = useState(false)
    const [newAgent, setNewAgent] = useState({ name: '', description: '', prompt: '' })
    const [createError, setCreateError] = useState(null)

    useEffect(() => {
        loadAgents()
    }, [])

    const loadAgents = async () => {
        try {
            const data = await api.listAgents()
            setAgents(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadAgentDetail = async (id) => {
        try {
            const data = await api.getAgent(id)
            setSelectedAgent(data)
        } catch (err) {
            console.error(err)
        }
    }

    const handleCreateAgent = async (e) => {
        e.preventDefault()
        setCreateError(null)
        try {
            await api.createAgent(newAgent)
            setNewAgent({ name: '', description: '', prompt: '' })
            setIsCreating(false)
            loadAgents()
        } catch (err) {
            setCreateError(err.message)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">Agents</h2>
                <button
                    onClick={() => setIsCreating(!isCreating)}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
                >
                    {isCreating ? 'Cancel' : '+ Create Agent'}
                </button>
            </div>

            {/* Create Form */}
            {isCreating && (
                <form onSubmit={handleCreateAgent} className="bg-slate-800 rounded-xl p-4 border border-slate-700 space-y-4">
                    {createError && <div className="p-2 bg-red-500/20 text-red-400 text-sm rounded">{createError}</div>}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Name *</label>
                            <input
                                type="text"
                                value={newAgent.name}
                                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Description</label>
                            <input
                                type="text"
                                value={newAgent.description}
                                onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Prompt *</label>
                        <textarea
                            value={newAgent.prompt}
                            onChange={(e) => setNewAgent({ ...newAgent, prompt: e.target.value })}
                            className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white h-24"
                            required
                        />
                    </div>
                    <button type="submit" className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
                        Create
                    </button>
                </form>
            )}

            <div className="flex gap-6">
                {/* Agent List */}
                <div className="flex-1 grid gap-4 md:grid-cols-2">
                    {agents.length === 0 ? (
                        <div className="text-center py-12 text-slate-400 col-span-2">
                            No agents configured.
                        </div>
                    ) : (
                        agents.map(agent => (
                            <div
                                key={agent.id}
                                onClick={() => loadAgentDetail(agent.id)}
                                className={`bg-slate-800 rounded-xl p-5 border cursor-pointer transition ${selectedAgent?.id === agent.id
                                    ? 'border-indigo-500'
                                    : 'border-slate-700 hover:border-slate-600'
                                    }`}
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg">
                                        🧠
                                    </div>
                                    <h3 className="font-semibold">{agent.name}</h3>
                                </div>
                                <p className="text-sm text-slate-400 line-clamp-2">{agent.description || 'No description'}</p>
                            </div>
                        ))
                    )}
                </div>

                {/* Detail Panel */}
                {selectedAgent && (
                    <div className="w-96 bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="font-semibold">{selectedAgent.name}</h3>
                            <button onClick={() => setSelectedAgent(null)} className="text-slate-400 hover:text-white">✕</button>
                        </div>

                        {selectedAgent.description && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Description</h4>
                                <p className="text-sm">{selectedAgent.description}</p>
                            </div>
                        )}

                        {/* Skill Badge */}
                        {selectedAgent.skill_name && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Skill</h4>
                                <span className="px-3 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full text-sm font-medium">
                                    🎯 {selectedAgent.skill_name}
                                </span>
                            </div>
                        )}

                        {/* Max Iterations */}
                        <div className="flex items-center gap-4">
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-1">Max Iterations</h4>
                                <span className="text-lg font-semibold text-indigo-400">{selectedAgent.max_iterations || 10}</span>
                            </div>
                        </div>

                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">System Prompt</h4>
                            <pre className="bg-slate-900 rounded p-3 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto scroll-area">
                                {selectedAgent.prompt}
                            </pre>
                        </div>

                        {/* Default Params */}
                        {selectedAgent.default_params && Object.keys(selectedAgent.default_params).length > 0 && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Default Params</h4>
                                <pre className="bg-slate-900 rounded p-3 text-xs whitespace-pre-wrap max-h-32 overflow-y-auto scroll-area">
                                    {JSON.stringify(selectedAgent.default_params, null, 2)}
                                </pre>
                            </div>
                        )}

                        {/* Tool Names (from Skill + Agent) */}
                        {selectedAgent.tool_names && selectedAgent.tool_names.length > 0 && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">
                                    Agent Tools ({selectedAgent.tool_names.length})
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAgent.tool_names.map(name => (
                                        <span key={name} className="px-2 py-1 bg-emerald-900/50 text-emerald-300 rounded text-xs">
                                            ⚡ {name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(selectedAgent.tools?.length > 0 || selectedAgent.tool_ids?.length > 0) && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">
                                    Configured Tools ({selectedAgent.tools?.length || selectedAgent.tool_ids?.length})
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAgent.tools ? (
                                        selectedAgent.tools.map(tool => (
                                            <span key={tool.id} className="px-2 py-1 bg-slate-700 rounded text-xs" title={tool.description}>
                                                🔧 {tool.name}
                                            </span>
                                        ))
                                    ) : (
                                        selectedAgent.tool_ids.map(id => (
                                            <span key={id} className="px-2 py-1 bg-slate-700 rounded text-xs">
                                                🔧 {id.replace('tool-', '')}
                                            </span>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
